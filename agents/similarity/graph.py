"""유사 선수 Agent 그래프 정의"""

from langgraph.graph import StateGraph, END

from agents.similarity.state import SimilarityState
from agents.similarity.nodes import (
    parse_criteria_node,
    compute_from_player_node,
    compute_from_criteria_node,
    rank_node,
    explain_node,
)


def _route_by_target(state: dict) -> str:
    """target_player 존재 여부에 따라 분기합니다."""
    return "from_player" if state.get("target_player") else "from_criteria"


def create_similarity_agent():
    """유사 선수 발견 Agent 그래프를 생성하고 컴파일합니다."""
    graph = StateGraph(SimilarityState)

    graph.add_node("parse_criteria", parse_criteria_node)
    graph.add_node("from_player", compute_from_player_node)
    graph.add_node("from_criteria", compute_from_criteria_node)
    graph.add_node("rank", rank_node)
    graph.add_node("explain", explain_node)

    graph.set_entry_point("parse_criteria")

    graph.add_conditional_edges(
        "parse_criteria",
        _route_by_target,
        {
            "from_player": "from_player",
            "from_criteria": "from_criteria",
        },
    )

    graph.add_edge("from_player", "rank")
    graph.add_edge("from_criteria", "rank")
    graph.add_edge("rank", "explain")
    graph.add_edge("explain", END)

    return graph.compile()
