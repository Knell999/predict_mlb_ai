"""유사 선수 Agent 노드 함수들"""

import json
import logging
from typing import Dict, Any

from langchain_core.messages import HumanMessage, SystemMessage
from agents.base import create_llm
from config import (
    AGENT_LLM_TEMPERATURE, AGENT_LLM_MAX_TOKENS,
    SIMILARITY_DEFAULT_BATTER_METRICS, SIMILARITY_DEFAULT_PITCHER_METRICS,
    SIMILARITY_DEFAULT_TOP_N,
)

logger = logging.getLogger(__name__)


def parse_criteria_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """자연어 쿼리에서 검색 조건을 파싱합니다."""
    query = state.get("query", "")
    lang = state.get("lang", "ko")

    llm = create_llm(temperature=0.0, max_tokens=500)
    if llm is None:
        # LLM 없이 기본 파싱 (선수 이름 직접 사용)
        return {
            "target_player": query.strip(),
            "player_type": state.get("player_type", "batter"),
            "similarity_metrics": SIMILARITY_DEFAULT_BATTER_METRICS,
            "top_n": state.get("top_n", SIMILARITY_DEFAULT_TOP_N),
        }

    response = llm.invoke([
        SystemMessage(content="""Parse the user query to extract player similarity search criteria.
Return ONLY a JSON object:
{
  "target_player": "<player name or null>",
  "player_type": "batter" or "pitcher",
  "season": <year or null>,
  "metrics": ["metric1", "metric2"] or null,
  "top_n": <number, default 10>
}

Available metrics for batters: BattingAverage, OnBasePercentage, SluggingPercentage, OPS, HomeRuns, RBIs, Hits, StolenBases, Walks, StrikeOuts
Available metrics for pitchers: EarnedRunAverage, Whip, StrikeOuts, InningsPitched, Wins, Losses, Walks, HitsAllowed"""),
        HumanMessage(content=query),
    ])

    try:
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        parsed = json.loads(raw)

        player_type = parsed.get("player_type", state.get("player_type", "batter"))
        default_metrics = (
            SIMILARITY_DEFAULT_BATTER_METRICS if player_type == "batter"
            else SIMILARITY_DEFAULT_PITCHER_METRICS
        )

        return {
            "target_player": parsed.get("target_player"),
            "player_type": player_type,
            "season_filter": parsed.get("season"),
            "similarity_metrics": parsed.get("metrics") or default_metrics,
            "top_n": parsed.get("top_n", state.get("top_n", SIMILARITY_DEFAULT_TOP_N)),
        }
    except Exception as e:
        logger.error(f"조건 파싱 오류: {e}")
        return {
            "target_player": query.strip(),
            "player_type": state.get("player_type", "batter"),
            "similarity_metrics": SIMILARITY_DEFAULT_BATTER_METRICS,
            "top_n": SIMILARITY_DEFAULT_TOP_N,
        }


def compute_from_player_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """특정 선수 기준으로 유사 선수를 계산합니다."""
    from agents.tools.similarity_tools import find_similar_players

    result = find_similar_players.invoke({
        "player_name": state["target_player"],
        "player_type": state["player_type"],
        "metrics": state["similarity_metrics"],
        "season": state.get("season_filter"),
        "top_n": state["top_n"],
    })

    if result and isinstance(result[0], dict) and "error" in result[0]:
        return {"error": result[0]["error"], "candidates": []}

    return {"candidates": result}


def compute_from_criteria_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """통계 조건으로 선수를 검색합니다."""
    from agents.tools.similarity_tools import find_players_by_criteria

    target_metrics = state.get("target_metrics", {})
    if not target_metrics:
        return {"error": "검색 조건이 지정되지 않았습니다", "candidates": []}

    criteria = {k: {"min": v * 0.9, "max": v * 1.1} for k, v in target_metrics.items()}

    result = find_players_by_criteria.invoke({
        "player_type": state["player_type"],
        "criteria": criteria,
        "season": state.get("season_filter"),
        "top_n": state["top_n"],
    })

    return {"candidates": result}


def rank_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """결과를 유사도 순으로 정렬합니다 (이미 정렬되어 있으므로 통과)."""
    return {}


def explain_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """유사 선수 결과를 자연어로 설명합니다."""
    lang = state.get("lang", "ko")
    candidates = state.get("candidates", [])
    target_player = state.get("target_player", "")

    if not candidates:
        return {"explanation": "유사한 선수를 찾지 못했습니다."}

    llm = create_llm(temperature=AGENT_LLM_TEMPERATURE, max_tokens=AGENT_LLM_MAX_TOKENS)
    if llm is None:
        top3 = candidates[:3]
        names = [c.get("player_name", "") for c in top3]
        return {"explanation": f"{target_player}과(와) 가장 유사한 선수: {', '.join(names)}"}

    lang_map = {"ko": "한국어", "en": "English", "ja": "日本語"}
    language = lang_map.get(lang, "한국어")

    response = llm.invoke([
        SystemMessage(content=f"You are an MLB analyst. Respond in {language} with markdown formatting."),
        HumanMessage(content=f"""기준 선수: {target_player}
비교 지표: {state.get('similarity_metrics', [])}

유사 선수 결과 (상위 {min(5, len(candidates))}명):
{json.dumps(candidates[:5], ensure_ascii=False, default=str)}

각 유사 선수에 대해:
1. 왜 유사한지 (어떤 지표가 비슷한지)
2. 차이점은 무엇인지
간결하게 설명해주세요."""),
    ])

    return {"explanation": response.content}
