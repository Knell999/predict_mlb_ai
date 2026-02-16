"""업데이트 Agent 그래프 정의"""

from langgraph.graph import StateGraph, END

from agents.update.state import UpdateState
from agents.update.nodes import (
    select_source_node,
    create_backup_node,
    execute_update_node,
    validate_data_node,
    recover_node,
    generate_report_node,
    report_failure_node,
)
from config import UPDATE_MAX_RETRIES


def _check_update_success(state: dict) -> str:
    """업데이트 성공 여부에 따라 분기합니다."""
    if state.get("update_success", False):
        return "validate"
    return "recover"


def _check_can_retry(state: dict) -> str:
    """재시도 가능 여부에 따라 분기합니다."""
    retry_count = state.get("retry_count", 0)
    if retry_count < UPDATE_MAX_RETRIES:
        return "retry"
    return "fail"


def create_update_agent():
    """데이터 업데이트 오케스트레이션 Agent 그래프를 생성하고 컴파일합니다."""
    graph = StateGraph(UpdateState)

    graph.add_node("select_source", select_source_node)
    graph.add_node("create_backup", create_backup_node)
    graph.add_node("execute_update", execute_update_node)
    graph.add_node("validate_data", validate_data_node)
    graph.add_node("recover", recover_node)
    graph.add_node("generate_report", generate_report_node)
    graph.add_node("report_failure", report_failure_node)

    graph.set_entry_point("select_source")
    graph.add_edge("select_source", "create_backup")
    graph.add_edge("create_backup", "execute_update")

    graph.add_conditional_edges(
        "execute_update",
        _check_update_success,
        {
            "validate": "validate_data",
            "recover": "recover",
        },
    )

    graph.add_edge("validate_data", "generate_report")
    graph.add_edge("generate_report", END)

    graph.add_conditional_edges(
        "recover",
        _check_can_retry,
        {
            "retry": "select_source",
            "fail": "report_failure",
        },
    )

    graph.add_edge("report_failure", END)

    return graph.compile()
