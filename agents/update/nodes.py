"""업데이트 Agent 노드 함수들"""

import logging
from typing import Dict, Any
from datetime import datetime

from config import UPDATE_MAX_RETRIES

logger = logging.getLogger(__name__)


def select_source_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """최적의 데이터 소스를 선택합니다."""
    method = state.get("method", "auto")
    failed = state.get("failed_methods", [])

    if method != "auto":
        if method not in failed:
            return {
                "selected_method": method,
                "source_rationale": f"사용자 지정 방법: {method}",
            }

    # auto: pybaseball 우선, 실패 시 mlb-api
    if "pybaseball" not in failed:
        return {
            "selected_method": "pybaseball",
            "source_rationale": "PyBaseball 우선 (더 빠르고 안정적)",
        }
    elif "mlb-api" not in failed:
        return {
            "selected_method": "mlb-api",
            "source_rationale": "PyBaseball 실패로 MLB API로 전환",
        }
    else:
        return {
            "selected_method": "none",
            "source_rationale": "모든 소스가 실패했습니다",
            "error": "사용 가능한 데이터 소스가 없습니다",
        }


def create_backup_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """데이터 백업을 생성합니다."""
    from agents.tools.update_tools import create_data_backup

    if not state.get("backup_requested", False):
        return {"update_steps": state.get("update_steps", []) + [
            {"step": "backup", "status": "skipped", "timestamp": str(datetime.now())}
        ]}

    result = create_data_backup.invoke({})
    return {"update_steps": state.get("update_steps", []) + [
        {"step": "backup", "status": "completed", "result": result, "timestamp": str(datetime.now())}
    ]}


def execute_update_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """선택된 방법으로 데이터를 업데이트합니다."""
    from agents.tools.update_tools import run_pybaseball_update, run_mlb_api_update

    method = state.get("selected_method", "pybaseball")
    start_year = state["start_year"]
    end_year = state["end_year"]

    if method == "pybaseball":
        result = run_pybaseball_update.invoke({"start_year": start_year, "end_year": end_year})
    elif method == "mlb-api":
        result = run_mlb_api_update.invoke({"start_year": start_year, "end_year": end_year})
    else:
        return {
            "update_success": False,
            "error": "유효하지 않은 업데이트 방법",
            "update_steps": state.get("update_steps", []) + [
                {"step": "update", "status": "failed", "method": method, "timestamp": str(datetime.now())}
            ],
        }

    success = result.get("success", False)
    steps = state.get("update_steps", []) + [
        {"step": "update", "status": "completed" if success else "failed",
         "method": method, "result": result, "timestamp": str(datetime.now())}
    ]

    if not success:
        failed = state.get("failed_methods", []) + [method]
        return {
            "update_success": False,
            "failed_methods": failed,
            "retry_count": state.get("retry_count", 0) + 1,
            "update_steps": steps,
        }

    return {
        "update_success": True,
        "update_steps": steps,
    }


def validate_data_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """업데이트된 데이터를 검증합니다."""
    from agents.tools.quality_tools import check_data_quality
    from agents.tools.update_tools import get_current_data_stats

    quality = check_data_quality.invoke({})
    stats = get_current_data_stats.invoke({})

    return {
        "quality_report": {"quality": quality, "stats": stats},
        "post_update_valid": True,
        "update_steps": state.get("update_steps", []) + [
            {"step": "validate", "status": "completed", "timestamp": str(datetime.now())}
        ],
    }


def recover_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """업데이트 실패 시 복구를 시도합니다."""
    retry_count = state.get("retry_count", 0)

    if retry_count >= UPDATE_MAX_RETRIES:
        return {
            "error": f"최대 재시도 횟수({UPDATE_MAX_RETRIES})를 초과했습니다",
            "update_steps": state.get("update_steps", []) + [
                {"step": "recover", "status": "max_retries_exceeded", "timestamp": str(datetime.now())}
            ],
        }

    return {
        "update_steps": state.get("update_steps", []) + [
            {"step": "recover", "status": "retrying", "retry_count": retry_count, "timestamp": str(datetime.now())}
        ],
    }


def generate_report_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """업데이트 결과 보고서를 생성합니다."""
    steps = state.get("update_steps", [])
    quality = state.get("quality_report", {})
    success = state.get("update_success", False)
    method = state.get("selected_method", "unknown")

    report_lines = [
        "# 데이터 업데이트 보고서\n",
        f"**상태**: {'✅ 성공' if success else '❌ 실패'}",
        f"**소스**: {method}",
        f"**범위**: {state.get('start_year', '?')} ~ {state.get('end_year', '?')}",
        "",
        "## 실행 단계",
    ]

    for step in steps:
        emoji = "✅" if step.get("status") == "completed" else "⏭️" if step.get("status") == "skipped" else "❌"
        report_lines.append(f"- {emoji} {step.get('step', '?')}: {step.get('status', '?')}")

    if quality:
        stats = quality.get("stats", {})
        report_lines.append("\n## 현재 데이터 상태")
        for dtype, info in stats.items():
            if isinstance(info, dict) and "records" in info:
                report_lines.append(f"- {dtype}: {info['records']}건 ({info.get('season_range', [])})")

    return {"status_report": "\n".join(report_lines)}


def report_failure_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """실패 보고서를 생성합니다."""
    failed = state.get("failed_methods", [])
    return {
        "status_report": (
            f"# 데이터 업데이트 실패\n\n"
            f"시도한 방법: {', '.join(failed)}\n"
            f"재시도 횟수: {state.get('retry_count', 0)}\n"
            f"오류: {state.get('error', '알 수 없는 오류')}"
        ),
    }
