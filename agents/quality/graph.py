"""품질 Agent 그래프 정의"""

from langgraph.graph import StateGraph, END

from agents.quality.state import QualityState
from agents.quality.nodes import (
    validate_files_node,
    validate_schema_node,
    check_ranges_node,
    detect_anomalies_node,
    interpret_anomalies_node,
    assemble_report_node,
)


def _check_anomalies(state: dict) -> str:
    """이상치 존재 여부에 따라 분기합니다."""
    anomalies = state.get("anomalies", [])
    return "interpret" if anomalies else "assemble"


def create_quality_agent():
    """데이터 품질 검증 Agent 그래프를 생성하고 컴파일합니다."""
    graph = StateGraph(QualityState)

    graph.add_node("validate_files", validate_files_node)
    graph.add_node("validate_schema", validate_schema_node)
    graph.add_node("check_ranges", check_ranges_node)
    graph.add_node("detect_anomalies", detect_anomalies_node)
    graph.add_node("interpret_anomalies", interpret_anomalies_node)
    graph.add_node("assemble_report", assemble_report_node)

    graph.set_entry_point("validate_files")
    graph.add_edge("validate_files", "validate_schema")
    graph.add_edge("validate_schema", "check_ranges")
    graph.add_edge("check_ranges", "detect_anomalies")

    graph.add_conditional_edges(
        "detect_anomalies",
        _check_anomalies,
        {
            "interpret": "interpret_anomalies",
            "assemble": "assemble_report",
        },
    )

    graph.add_edge("interpret_anomalies", "assemble_report")
    graph.add_edge("assemble_report", END)

    return graph.compile()
