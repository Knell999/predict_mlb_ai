"""예측 Agent 노드 함수들"""

import json
import logging
from typing import Dict, Any

from langchain_core.messages import HumanMessage, SystemMessage
from agents.base import create_llm
from config import AGENT_LLM_TEMPERATURE, AGENT_LLM_MAX_TOKENS

logger = logging.getLogger(__name__)


def load_data_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """선수 데이터를 로드합니다."""
    from agents.tools.data_tools import get_player_stats

    player_name = state["player_name"]
    player_type = state["player_type"]
    result = get_player_stats.invoke({"player_name": player_name, "player_type": player_type})

    if "error" in result:
        return {"error": result["error"], "data_adequate": False, "data_seasons": 0}

    return {
        "player_data": result,
        "data_seasons": result["seasons"],
    }


def evaluate_data_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """데이터 충분성을 평가합니다."""
    from agents.tools.prediction_tools import assess_prediction_data_adequacy

    player_name = state["player_name"]
    player_type = state["player_type"]

    adequacy = assess_prediction_data_adequacy.invoke({
        "player_name": player_name, "player_type": player_type
    })

    assessment = (
        f"시즌 수: {adequacy.get('total_seasons', 0)}, "
        f"범위: {adequacy.get('season_range', [])}, "
        f"신뢰도: {adequacy.get('confidence_level', 'unknown')}, "
        f"최근 데이터: {'있음' if adequacy.get('has_recent_data') else '없음'}"
    )

    return {
        "data_adequate": adequacy.get("adequate", False),
        "data_assessment": assessment,
    }


def context_analysis_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """선수의 맥락적 요인을 분석합니다 (나이 곡선, 유사 선수)."""
    from agents.tools.stats_tools import detect_trend
    from agents.tools.similarity_tools import find_similar_players

    player_name = state["player_name"]
    player_type = state["player_type"]
    lang = state.get("lang", "ko")

    # 주요 지표 트렌드
    key_metric = "OPS" if player_type == "batter" else "EarnedRunAverage"
    trend = detect_trend.invoke({
        "player_name": player_name, "player_type": player_type, "metric": key_metric
    })

    # 유사 선수
    from config import SIMILARITY_DEFAULT_BATTER_METRICS, SIMILARITY_DEFAULT_PITCHER_METRICS
    sim_metrics = SIMILARITY_DEFAULT_BATTER_METRICS if player_type == "batter" else SIMILARITY_DEFAULT_PITCHER_METRICS
    similar = find_similar_players.invoke({
        "player_name": player_name, "player_type": player_type,
        "metrics": sim_metrics, "top_n": 5,
    })

    llm = create_llm(temperature=AGENT_LLM_TEMPERATURE, max_tokens=3000)
    if llm is None:
        return {
            "player_age_curve": json.dumps(trend, ensure_ascii=False),
            "similar_players_context": json.dumps(similar[:3], ensure_ascii=False, default=str),
        }

    lang_map = {"ko": "한국어", "en": "English", "ja": "日本語"}
    language = lang_map.get(lang, "한국어")

    response = llm.invoke([
        SystemMessage(content=f"You are an MLB analyst. Respond in {language}."),
        HumanMessage(content=f"""{player_name}의 맥락 분석:

트렌드: {json.dumps(trend, ensure_ascii=False)}
유사 선수: {json.dumps(similar[:3], ensure_ascii=False, default=str)}

1. 나이/커리어 곡선 관점에서 현재 위치 (상승기/피크/하강기)
2. 유사 선수들의 커리어 경로를 참고한 전망
간결하게 3-4문장으로 작성해주세요."""),
    ])

    return {
        "player_age_curve": response.content,
        "similar_players_context": json.dumps(similar[:3], ensure_ascii=False, default=str),
    }


def run_forecasts_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Prophet 예측을 실행합니다."""
    from agents.tools.prediction_tools import run_prophet_forecast

    player_name = state["player_name"]
    player_type = state["player_type"]
    metrics = state["metrics"]
    periods = state.get("prediction_years", 5)

    forecasts = {}
    for metric in metrics:
        result = run_prophet_forecast.invoke({
            "player_name": player_name, "player_type": player_type,
            "metric": metric, "periods": periods,
        })
        if "error" not in result:
            forecasts[metric] = result

    return {"forecasts": forecasts}


def interpret_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """예측 결과를 자연어로 해석합니다."""
    lang = state.get("lang", "ko")
    llm = create_llm(temperature=AGENT_LLM_TEMPERATURE, max_tokens=AGENT_LLM_MAX_TOKENS)

    if llm is None:
        return {"interpretation": json.dumps(state.get("forecasts", {}), ensure_ascii=False)}

    lang_map = {"ko": "한국어", "en": "English", "ja": "日本語"}
    language = lang_map.get(lang, "한국어")

    response = llm.invoke([
        SystemMessage(content=f"You are an MLB data analyst. Respond in {language} with markdown formatting."),
        HumanMessage(content=f"""{state['player_name']}의 예측 결과를 해석해주세요.

데이터 평가: {state.get('data_assessment', '')}
맥락 분석: {state.get('player_age_curve', '')}
예측 결과: {json.dumps(state.get('forecasts', {}), ensure_ascii=False)}

다음을 포함해주세요:
1. 각 지표별 예측 요약
2. 예측의 의미와 시사점
3. 주의사항 및 한계"""),
    ])

    return {"interpretation": response.content}


def assess_confidence_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """예측 신뢰도를 평가합니다."""
    data_seasons = state.get("data_seasons", 0)
    forecasts = state.get("forecasts", {})

    if data_seasons >= 8:
        level = "높음"
    elif data_seasons >= 5:
        level = "보통"
    else:
        level = "낮음"

    # 예측 범위 폭으로 불확실성 판단
    wide_intervals = 0
    for metric, forecast in forecasts.items():
        predictions = forecast.get("predictions", [])
        for p in predictions:
            interval = p.get("upper_bound", 0) - p.get("lower_bound", 0)
            if interval > abs(p.get("predicted", 1)) * 0.5:
                wide_intervals += 1

    if wide_intervals > len(forecasts):
        level = "낮음"

    assessment = f"신뢰도: {level} (데이터 {data_seasons}시즌 기반)"
    return {"confidence_assessment": assessment}


def insufficient_response_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """데이터 부족 시 응답을 생성합니다."""
    player_name = state.get("player_name", "")
    data_seasons = state.get("data_seasons", 0)

    return {
        "interpretation": (
            f"**{player_name}**의 데이터가 예측에 충분하지 않습니다.\n\n"
            f"- 보유 시즌 수: {data_seasons}\n"
            f"- 최소 필요 시즌: 3\n\n"
            f"더 많은 시즌 데이터가 축적된 후 예측을 시도해주세요."
        ),
        "confidence_assessment": "예측 불가",
    }
