"""대화형 Agent 그래프 정의"""

from langgraph.graph import StateGraph, END

from agents.conversational.state import ConversationalState
from agents.conversational.nodes import (
    router_node,
    profile_node,
    compare_node,
    trend_node,
    predict_node,
    root_cause_node,
    general_node,
    synthesize_node,
)
from config import AGENT_RECURSION_LIMIT


def _route_by_intent(state: dict) -> str:
    """current_intent에 따라 적절한 노드로 라우팅합니다."""
    intent = state.get("current_intent", "general")
    valid_intents = {"profile", "compare", "trend", "predict", "root_cause", "general"}
    return intent if intent in valid_intents else "general"


def create_conversational_agent():
    """대화형 분석 Agent 그래프를 생성하고 컴파일합니다.

    Returns:
        컴파일된 StateGraph
    """
    graph = StateGraph(ConversationalState)

    # 노드 추가
    graph.add_node("router", router_node)
    graph.add_node("profile", profile_node)
    graph.add_node("compare", compare_node)
    graph.add_node("trend", trend_node)
    graph.add_node("predict", predict_node)
    graph.add_node("root_cause", root_cause_node)
    graph.add_node("general", general_node)
    graph.add_node("synthesize", synthesize_node)

    # 엣지 정의
    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router",
        _route_by_intent,
        {
            "profile": "profile",
            "compare": "compare",
            "trend": "trend",
            "predict": "predict",
            "root_cause": "root_cause",
            "general": "general",
        },
    )

    # 모든 분석 노드 → synthesize → END
    for node in ["profile", "compare", "trend", "predict", "root_cause", "general"]:
        graph.add_edge(node, "synthesize")
    graph.add_edge("synthesize", END)

    return graph.compile()
