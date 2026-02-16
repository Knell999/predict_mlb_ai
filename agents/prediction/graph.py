"""예측 Agent 그래프 정의"""

from langgraph.graph import StateGraph, END

from agents.prediction.state import PredictionState
from agents.prediction.nodes import (
    load_data_node,
    evaluate_data_node,
    context_analysis_node,
    run_forecasts_node,
    interpret_node,
    assess_confidence_node,
    insufficient_response_node,
)


def _check_data_adequacy(state: dict) -> str:
    """데이터 충분성에 따라 분기합니다."""
    return "context_analysis" if state.get("data_adequate", False) else "insufficient"


def create_prediction_agent():
    """지능형 예측 Agent 그래프를 생성하고 컴파일합니다."""
    graph = StateGraph(PredictionState)

    # 노드 추가
    graph.add_node("load_data", load_data_node)
    graph.add_node("evaluate_data", evaluate_data_node)
    graph.add_node("context_analysis", context_analysis_node)
    graph.add_node("run_forecasts", run_forecasts_node)
    graph.add_node("interpret", interpret_node)
    graph.add_node("assess_confidence", assess_confidence_node)
    graph.add_node("insufficient", insufficient_response_node)

    # 엣지
    graph.set_entry_point("load_data")
    graph.add_edge("load_data", "evaluate_data")

    graph.add_conditional_edges(
        "evaluate_data",
        _check_data_adequacy,
        {
            "context_analysis": "context_analysis",
            "insufficient": "insufficient",
        },
    )

    graph.add_edge("context_analysis", "run_forecasts")
    graph.add_edge("run_forecasts", "interpret")
    graph.add_edge("interpret", "assess_confidence")
    graph.add_edge("assess_confidence", END)
    graph.add_edge("insufficient", END)

    return graph.compile()
