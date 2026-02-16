"""리포트 Agent 노드 함수들"""

import json
import logging
from typing import Dict, Any

from langchain_core.messages import HumanMessage, SystemMessage
from agents.base import create_llm
from config import AGENT_LLM_TEMPERATURE, AGENT_LLM_MAX_TOKENS

logger = logging.getLogger(__name__)


def _get_llm_and_language(lang: str):
    """LLM 인스턴스와 언어 문자열을 반환합니다."""
    llm = create_llm(temperature=AGENT_LLM_TEMPERATURE, max_tokens=AGENT_LLM_MAX_TOKENS)
    lang_map = {"ko": "한국어", "en": "English", "ja": "日本語"}
    return llm, lang_map.get(lang, "한국어")


def load_all_data_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """리포트에 필요한 모든 데이터를 로드합니다."""
    from agents.tools.data_tools import get_player_stats, get_league_averages

    player_name = state["player_name"]
    player_type = state["player_type"]

    stats = get_player_stats.invoke({"player_name": player_name, "player_type": player_type})
    if "error" in stats:
        return {"error": stats["error"]}

    from config import BATTING_METRICS, PITCHING_METRICS
    metrics = BATTING_METRICS if player_type == "batter" else PITCHING_METRICS
    league = get_league_averages.invoke({"player_type": player_type, "metrics": metrics})

    return {
        "player_data": stats,
        "league_averages": league,
    }


def plan_sections_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """리포트 섹션을 계획합니다."""
    report_type = state.get("report_type", "full")
    player_name = state.get("player_name", "")
    return {"report_title": f"{player_name} 분석 보고서"}


def gen_profile_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """선수 프로파일 섹션을 생성합니다."""
    lang = state.get("lang", "ko")
    llm, language = _get_llm_and_language(lang)
    player_data = state.get("player_data", {})

    if llm is None:
        return {"section_profile": f"## 선수 프로파일\n시즌 수: {player_data.get('seasons', '?')}"}

    response = llm.invoke([
        SystemMessage(content=f"You are an MLB analyst writing a report section in {language}. Use markdown."),
        HumanMessage(content=f"""선수 프로파일 섹션을 작성해주세요.

선수: {state.get('player_name', '')}
시즌 수: {player_data.get('seasons', '')}
시즌 범위: {player_data.get('season_range', '')}

3-5문장으로 선수의 커리어 개요를 작성해주세요."""),
    ])
    return {"section_profile": response.content}


def gen_metrics_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """핵심 지표 분석 섹션을 생성합니다."""
    from agents.tools.stats_tools import calculate_career_averages

    lang = state.get("lang", "ko")
    player_name = state.get("player_name", "")
    player_type = state.get("player_type", "batter")

    from config import BATTING_METRICS, PITCHING_METRICS
    metrics = BATTING_METRICS if player_type == "batter" else PITCHING_METRICS

    career_avg = calculate_career_averages.invoke({
        "player_name": player_name, "player_type": player_type, "metrics": metrics
    })

    llm, language = _get_llm_and_language(lang)
    if llm is None:
        return {"section_metrics": f"## 핵심 지표\n{json.dumps(career_avg, ensure_ascii=False)}"}

    response = llm.invoke([
        SystemMessage(content=f"You are an MLB analyst. Write in {language}. Use markdown."),
        HumanMessage(content=f"""핵심 지표 분석 섹션을 작성해주세요.

{player_name}의 커리어 평균:
{json.dumps(career_avg, ensure_ascii=False)}

주요 지표별 의미와 분석을 간결하게 작성해주세요."""),
    ])
    return {"section_metrics": response.content}


def gen_trends_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """트렌드 분석 섹션을 생성합니다."""
    from agents.tools.stats_tools import detect_trend

    lang = state.get("lang", "ko")
    player_name = state.get("player_name", "")
    player_type = state.get("player_type", "batter")

    key_metrics = ["OPS", "BattingAverage", "HomeRuns"] if player_type == "batter" else ["EarnedRunAverage", "Whip", "StrikeOuts"]

    trends = {}
    for metric in key_metrics:
        result = detect_trend.invoke({
            "player_name": player_name, "player_type": player_type, "metric": metric
        })
        if "error" not in result:
            trends[metric] = result

    llm, language = _get_llm_and_language(lang)
    if llm is None:
        return {"section_trends": f"## 트렌드\n{json.dumps(trends, ensure_ascii=False)}"}

    response = llm.invoke([
        SystemMessage(content=f"You are an MLB analyst. Write in {language}. Use markdown."),
        HumanMessage(content=f"""트렌드 분석 섹션을 작성해주세요.

{player_name}의 지표별 트렌드:
{json.dumps(trends, ensure_ascii=False)}

각 지표의 방향, 피크, 최근 추세를 분석해주세요."""),
    ])
    return {"section_trends": response.content}


def gen_predictions_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """예측 섹션을 생성합니다."""
    if not state.get("include_predictions", False):
        return {"section_predictions": ""}

    from agents.tools.prediction_tools import run_prophet_forecast

    lang = state.get("lang", "ko")
    player_name = state.get("player_name", "")
    player_type = state.get("player_type", "batter")

    key_metric = "OPS" if player_type == "batter" else "EarnedRunAverage"
    forecast = run_prophet_forecast.invoke({
        "player_name": player_name, "player_type": player_type,
        "metric": key_metric, "periods": 3,
    })

    llm, language = _get_llm_and_language(lang)
    if llm is None:
        return {"section_predictions": f"## 예측\n{json.dumps(forecast, ensure_ascii=False)}"}

    response = llm.invoke([
        SystemMessage(content=f"You are an MLB analyst. Write in {language}. Use markdown."),
        HumanMessage(content=f"""예측 섹션을 작성해주세요.

{player_name}의 {key_metric} 예측:
{json.dumps(forecast, ensure_ascii=False)}

예측값의 의미와 주의사항을 간결하게 작성해주세요."""),
    ])
    return {"section_predictions": response.content}


def gen_comparisons_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """리그 비교 섹션을 생성합니다."""
    from agents.tools.stats_tools import compare_to_league

    lang = state.get("lang", "ko")
    player_name = state.get("player_name", "")
    player_type = state.get("player_type", "batter")
    player_data = state.get("player_data", {})

    latest_season = player_data.get("season_range", [2000, 2024])[1] if player_data else 2024

    from config import BATTING_METRICS, PITCHING_METRICS
    metrics = BATTING_METRICS[:5] if player_type == "batter" else PITCHING_METRICS[:4]

    comparison = compare_to_league.invoke({
        "player_name": player_name, "player_type": player_type,
        "season": latest_season, "metrics": metrics,
    })

    llm, language = _get_llm_and_language(lang)
    if llm is None:
        return {"section_comparisons": f"## 리그 비교\n{json.dumps(comparison, ensure_ascii=False)}"}

    response = llm.invoke([
        SystemMessage(content=f"You are an MLB analyst. Write in {language}. Use markdown."),
        HumanMessage(content=f"""{latest_season} 시즌 리그 비교 섹션을 작성해주세요.

{player_name}의 리그 비교:
{json.dumps(comparison, ensure_ascii=False)}

리그 평균 대비 강점과 약점을 분석해주세요."""),
    ])
    return {"section_comparisons": response.content}


def assemble_report_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """모든 섹션을 결합하여 최종 리포트를 조립합니다."""
    title = state.get("report_title", "분석 보고서")

    sections = [
        f"# {title}\n",
        state.get("section_profile", ""),
        state.get("section_metrics", ""),
        state.get("section_trends", ""),
    ]

    if state.get("section_predictions"):
        sections.append(state["section_predictions"])

    sections.append(state.get("section_comparisons", ""))
    sections.append("\n---\n*이 보고서는 AI에 의해 자동 생성되었습니다.*")

    return {"full_report": "\n\n".join(s for s in sections if s)}
