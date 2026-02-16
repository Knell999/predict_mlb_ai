"""리포트 Agent 그래프 정의"""

from langgraph.graph import StateGraph, END

from agents.report.state import ReportState
from agents.report.nodes import (
    load_all_data_node,
    plan_sections_node,
    gen_profile_node,
    gen_metrics_node,
    gen_trends_node,
    gen_predictions_node,
    gen_comparisons_node,
    assemble_report_node,
)


def _check_include_predictions(state: dict) -> str:
    """예측 포함 여부에 따라 분기합니다."""
    return "gen_predictions" if state.get("include_predictions", False) else "gen_comparisons"


def create_report_agent():
    """리포트 생성 Agent 그래프를 생성하고 컴파일합니다."""
    graph = StateGraph(ReportState)

    graph.add_node("load_all_data", load_all_data_node)
    graph.add_node("plan_sections", plan_sections_node)
    graph.add_node("gen_profile", gen_profile_node)
    graph.add_node("gen_metrics", gen_metrics_node)
    graph.add_node("gen_trends", gen_trends_node)
    graph.add_node("gen_predictions", gen_predictions_node)
    graph.add_node("gen_comparisons", gen_comparisons_node)
    graph.add_node("assemble_report", assemble_report_node)

    graph.set_entry_point("load_all_data")
    graph.add_edge("load_all_data", "plan_sections")
    graph.add_edge("plan_sections", "gen_profile")
    graph.add_edge("gen_profile", "gen_metrics")
    graph.add_edge("gen_metrics", "gen_trends")

    graph.add_conditional_edges(
        "gen_trends",
        _check_include_predictions,
        {
            "gen_predictions": "gen_predictions",
            "gen_comparisons": "gen_comparisons",
        },
    )

    graph.add_edge("gen_predictions", "gen_comparisons")
    graph.add_edge("gen_comparisons", "assemble_report")
    graph.add_edge("assemble_report", END)

    return graph.compile()
