"""대화형 Agent 노드 함수들"""

import json
import logging
from typing import Dict, Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from agents.base import create_llm
from config import AGENT_ROUTER_TEMPERATURE, AGENT_LLM_TEMPERATURE, AGENT_LLM_MAX_TOKENS

logger = logging.getLogger(__name__)

ROUTER_SYSTEM_PROMPT = """You are a routing assistant for an MLB baseball analysis system.
Classify the user's intent into exactly ONE of these categories:

- "profile": User wants to know about a specific player's stats, career, performance
- "compare": User wants to compare two or more players
- "trend": User wants to analyze trends in a player's or league's performance over time
- "predict": User wants predictions or forecasts for a player's future performance
- "root_cause": User wants to understand WHY a player's performance changed (decline/improvement)
- "general": General baseball conversation, greetings, or questions not fitting above categories

Respond with ONLY a JSON object: {"intent": "<category>", "player_name": "<name or null>", "player_names": ["<name1>", "<name2>"] or null, "player_type": "batter" or "pitcher"}

Examples:
- "Mike Trout에 대해 알려줘" -> {"intent": "profile", "player_name": "Mike Trout", "player_names": null, "player_type": "batter"}
- "Trout과 Ohtani 비교해줘" -> {"intent": "compare", "player_name": null, "player_names": ["Mike Trout", "Shohei Ohtani"], "player_type": "batter"}
- "Clayton Kershaw의 ERA가 왜 올랐어?" -> {"intent": "root_cause", "player_name": "Clayton Kershaw", "player_names": null, "player_type": "pitcher"}
- "향후 3년 예측해줘" -> {"intent": "predict", "player_name": null, "player_names": null, "player_type": "batter"}
- "안녕" -> {"intent": "general", "player_name": null, "player_names": null, "player_type": "batter"}
"""


def router_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """사용자 메시지의 의도를 분류합니다."""
    llm = create_llm(temperature=AGENT_ROUTER_TEMPERATURE, max_tokens=500)
    if llm is None:
        return {"current_intent": "general", "error": "LLM을 사용할 수 없습니다"}

    messages = state.get("messages", [])
    if not messages:
        return {"current_intent": "general"}

    last_message = messages[-1]
    user_text = last_message.content if hasattr(last_message, 'content') else str(last_message)

    try:
        response = llm.invoke([
            SystemMessage(content=ROUTER_SYSTEM_PROMPT),
            HumanMessage(content=user_text),
        ])
        raw = response.content.strip()
        # JSON 파싱 (마크다운 코드블록 제거)
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        parsed = json.loads(raw)

        return {
            "current_intent": parsed.get("intent", "general"),
            "player_name": parsed.get("player_name"),
            "player_names": parsed.get("player_names"),
            "player_type": parsed.get("player_type", "batter"),
        }
    except Exception as e:
        logger.error(f"라우터 파싱 오류: {e}")
        return {"current_intent": "general"}


def _get_analysis_system_prompt(lang: str) -> str:
    """분석 시스템 프롬프트를 생성합니다."""
    lang_map = {"ko": "한국어", "en": "English", "ja": "日本語"}
    language = lang_map.get(lang, "한국어")
    return f"""You are an expert MLB baseball data analyst. You have access to tools that can query player statistics, calculate career averages, compare players to league averages, detect trends, run Prophet forecasts, and find similar players.

Use these tools to gather data, then provide insightful analysis in {language}.
Always base your analysis on actual data from the tools. Use markdown formatting for readability.
When mentioning statistics, be specific with numbers and seasons."""


def profile_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """선수 프로파일 분석을 수행합니다."""
    from agents.tools.data_tools import get_player_stats
    from agents.tools.stats_tools import calculate_career_averages, detect_trend

    lang = state.get("lang", "ko")
    player_name = state.get("player_name", "")
    player_type = state.get("player_type", "batter")

    if not player_name:
        return {"messages": [AIMessage(content="분석할 선수 이름을 알려주세요.")]}

    # 데이터 수집
    stats = get_player_stats.invoke({"player_name": player_name, "player_type": player_type})
    if "error" in stats:
        suggestions = stats.get("suggestions", [])
        msg = f"'{player_name}'을(를) 찾을 수 없습니다."
        if suggestions:
            msg += f" 혹시 이 선수를 찾으시나요? {', '.join(suggestions)}"
        return {"messages": [AIMessage(content=msg)]}

    from config import BATTING_METRICS, PITCHING_METRICS
    metrics = BATTING_METRICS if player_type == "batter" else PITCHING_METRICS
    career_avg = calculate_career_averages.invoke({
        "player_name": player_name, "player_type": player_type, "metrics": metrics
    })

    # 주요 지표 트렌드
    key_metric = "OPS" if player_type == "batter" else "EarnedRunAverage"
    trend = detect_trend.invoke({
        "player_name": player_name, "player_type": player_type, "metric": key_metric
    })

    # LLM으로 종합 분석
    llm = create_llm(temperature=AGENT_LLM_TEMPERATURE, max_tokens=AGENT_LLM_MAX_TOKENS)
    if llm is None:
        return {"messages": [AIMessage(content=f"**{player_name}** 커리어 평균: {json.dumps(career_avg, ensure_ascii=False)}")]}

    analysis_prompt = f"""다음 데이터를 바탕으로 {player_name}의 종합 분석을 작성해주세요.

커리어 통계: {json.dumps(career_avg, ensure_ascii=False)}
트렌드 분석 ({key_metric}): {json.dumps(trend, ensure_ascii=False)}
시즌 수: {stats['seasons']}
시즌 범위: {stats['season_range']}

다음을 포함해주세요:
1. 선수 개요 및 주요 성과
2. 핵심 지표 분석
3. 트렌드 분석
4. 종합 평가"""

    response = llm.invoke([
        SystemMessage(content=_get_analysis_system_prompt(lang)),
        HumanMessage(content=analysis_prompt),
    ])
    return {"messages": [AIMessage(content=response.content)]}


def compare_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """선수 비교 분석을 수행합니다."""
    from agents.tools.data_tools import get_player_stats
    from agents.tools.stats_tools import calculate_career_averages

    lang = state.get("lang", "ko")
    player_names = state.get("player_names", [])
    player_type = state.get("player_type", "batter")

    if not player_names or len(player_names) < 2:
        return {"messages": [AIMessage(content="비교할 선수 2명 이상의 이름을 알려주세요.")]}

    from config import BATTING_METRICS, PITCHING_METRICS
    metrics = BATTING_METRICS if player_type == "batter" else PITCHING_METRICS

    players_data = {}
    for name in player_names[:5]:
        stats = get_player_stats.invoke({"player_name": name, "player_type": player_type})
        if "error" not in stats:
            avg = calculate_career_averages.invoke({
                "player_name": name, "player_type": player_type, "metrics": metrics
            })
            players_data[name] = {"stats": stats, "career_avg": avg}

    if len(players_data) < 2:
        return {"messages": [AIMessage(content="비교할 수 있는 선수 데이터가 부족합니다.")]}

    llm = create_llm(temperature=AGENT_LLM_TEMPERATURE, max_tokens=AGENT_LLM_MAX_TOKENS)
    if llm is None:
        return {"messages": [AIMessage(content=f"비교 데이터: {json.dumps(players_data, ensure_ascii=False, default=str)}")]}

    compare_prompt = f"""다음 선수들의 데이터를 비교 분석해주세요.

{json.dumps(players_data, ensure_ascii=False, default=str)}

다음을 포함해주세요:
1. 각 선수 개요
2. 핵심 지표 비교
3. 강점/약점 비교
4. 종합 평가"""

    response = llm.invoke([
        SystemMessage(content=_get_analysis_system_prompt(lang)),
        HumanMessage(content=compare_prompt),
    ])
    return {"messages": [AIMessage(content=response.content)]}


def trend_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """트렌드 분석을 수행합니다."""
    from agents.tools.stats_tools import detect_trend

    lang = state.get("lang", "ko")
    player_name = state.get("player_name", "")
    player_type = state.get("player_type", "batter")

    if not player_name:
        return {"messages": [AIMessage(content="트렌드를 분석할 선수 이름을 알려주세요.")]}

    from config import BATTING_METRICS, PITCHING_METRICS
    metrics = BATTING_METRICS[:5] if player_type == "batter" else PITCHING_METRICS[:4]

    trends = {}
    for metric in metrics:
        result = detect_trend.invoke({
            "player_name": player_name, "player_type": player_type, "metric": metric
        })
        if "error" not in result:
            trends[metric] = result

    if not trends:
        return {"messages": [AIMessage(content=f"{player_name}의 트렌드 데이터를 찾을 수 없습니다.")]}

    llm = create_llm(temperature=AGENT_LLM_TEMPERATURE, max_tokens=AGENT_LLM_MAX_TOKENS)
    if llm is None:
        return {"messages": [AIMessage(content=f"트렌드 데이터: {json.dumps(trends, ensure_ascii=False)}")]}

    response = llm.invoke([
        SystemMessage(content=_get_analysis_system_prompt(lang)),
        HumanMessage(content=f"""{player_name}의 지표별 트렌드를 분석해주세요.

트렌드 데이터: {json.dumps(trends, ensure_ascii=False)}

각 지표의 방향, 피크 시즌, 최근 추세를 중심으로 분석해주세요."""),
    ])
    return {"messages": [AIMessage(content=response.content)]}


def predict_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """예측 분석을 수행합니다."""
    from agents.tools.prediction_tools import run_prophet_forecast, assess_prediction_data_adequacy

    lang = state.get("lang", "ko")
    player_name = state.get("player_name", "")
    player_type = state.get("player_type", "batter")

    if not player_name:
        return {"messages": [AIMessage(content="예측할 선수 이름을 알려주세요.")]}

    adequacy = assess_prediction_data_adequacy.invoke({
        "player_name": player_name, "player_type": player_type
    })
    if not adequacy.get("adequate", False):
        return {"messages": [AIMessage(
            content=f"{player_name}의 데이터가 예측에 충분하지 않습니다. ({adequacy.get('total_seasons', 0)}시즌, 최소 3시즌 필요)"
        )]}

    key_metrics = ["OPS", "BattingAverage"] if player_type == "batter" else ["EarnedRunAverage", "Whip"]
    forecasts = {}
    for metric in key_metrics:
        result = run_prophet_forecast.invoke({
            "player_name": player_name, "player_type": player_type,
            "metric": metric, "periods": 3,
        })
        if "error" not in result:
            forecasts[metric] = result

    if not forecasts:
        return {"messages": [AIMessage(content="예측을 수행할 수 없습니다.")]}

    llm = create_llm(temperature=AGENT_LLM_TEMPERATURE, max_tokens=AGENT_LLM_MAX_TOKENS)
    if llm is None:
        return {"messages": [AIMessage(content=f"예측 결과: {json.dumps(forecasts, ensure_ascii=False)}")]}

    response = llm.invoke([
        SystemMessage(content=_get_analysis_system_prompt(lang)),
        HumanMessage(content=f"""{player_name}의 예측 결과를 해석해주세요.

데이터 충분성: {json.dumps(adequacy, ensure_ascii=False)}
예측 결과: {json.dumps(forecasts, ensure_ascii=False)}

예측값의 의미, 신뢰도, 주의사항을 포함해주세요."""),
    ])
    return {"messages": [AIMessage(content=response.content)]}


def root_cause_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """성과 변화 원인을 분석합니다."""
    from agents.tools.data_tools import get_player_stats
    from agents.tools.stats_tools import detect_trend, compare_to_league

    lang = state.get("lang", "ko")
    player_name = state.get("player_name", "")
    player_type = state.get("player_type", "batter")

    if not player_name:
        return {"messages": [AIMessage(content="분석할 선수 이름을 알려주세요.")]}

    stats = get_player_stats.invoke({"player_name": player_name, "player_type": player_type})
    if "error" in stats:
        return {"messages": [AIMessage(content=stats["error"])]}

    from config import BATTING_METRICS, PITCHING_METRICS
    metrics = BATTING_METRICS if player_type == "batter" else PITCHING_METRICS

    trends = {}
    for metric in metrics[:6]:
        result = detect_trend.invoke({
            "player_name": player_name, "player_type": player_type, "metric": metric
        })
        if "error" not in result:
            trends[metric] = result

    # 최근 시즌 vs 리그 평균
    latest_season = stats["season_range"][1]
    league_comp = compare_to_league.invoke({
        "player_name": player_name, "player_type": player_type,
        "season": latest_season, "metrics": metrics[:6],
    })

    llm = create_llm(temperature=AGENT_LLM_TEMPERATURE, max_tokens=AGENT_LLM_MAX_TOKENS)
    if llm is None:
        return {"messages": [AIMessage(content=f"분석 데이터: 트렌드={json.dumps(trends, ensure_ascii=False)}")]}

    response = llm.invoke([
        SystemMessage(content=_get_analysis_system_prompt(lang)),
        HumanMessage(content=f"""{player_name}의 성과 변화 원인을 분석해주세요.

커리어 시즌 범위: {stats['season_range']}
지표별 트렌드: {json.dumps(trends, ensure_ascii=False)}
최근 시즌({latest_season}) 리그 비교: {json.dumps(league_comp, ensure_ascii=False)}

다음을 분석해주세요:
1. 어떤 지표가 가장 크게 변화했는가?
2. 변화의 시기와 패턴
3. 가능한 원인 (나이, 부상 가능성, 기술 변화 등)
4. 향후 전망"""),
    ])
    return {"messages": [AIMessage(content=response.content)]}


def general_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """일반 대화를 처리합니다."""
    lang = state.get("lang", "ko")
    messages = state.get("messages", [])

    llm = create_llm(temperature=AGENT_LLM_TEMPERATURE, max_tokens=2000)
    if llm is None:
        return {"messages": [AIMessage(content="안녕하세요! MLB 선수에 대해 무엇이든 물어보세요.")]}

    lang_map = {"ko": "한국어", "en": "English", "ja": "日本語"}
    language = lang_map.get(lang, "한국어")

    system = f"""You are a friendly MLB baseball expert chatbot.
Respond in {language}. You can discuss baseball history, rules, players, and statistics.
If the user asks about specific player data, suggest they ask about a specific player for detailed analysis.
Keep responses concise and engaging."""

    chat_messages = [SystemMessage(content=system)] + list(messages[-10:])
    response = llm.invoke(chat_messages)
    return {"messages": [AIMessage(content=response.content)]}


def synthesize_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """분석 결과를 그대로 전달합니다 (이미 각 노드에서 메시지가 생성됨)."""
    return {}
