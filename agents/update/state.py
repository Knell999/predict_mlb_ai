"""업데이트 Agent 상태 정의"""

from typing import TypedDict, Optional, List, Dict, Any


class UpdateState(TypedDict):
    """데이터 업데이트 오케스트레이션 Agent의 상태"""
    # 입력
    start_year: int
    end_year: int
    method: str  # "auto"|"pybaseball"|"mlb-api"
    backup_requested: bool
    # 소스 선택
    selected_method: str
    source_rationale: str
    # 실행 추적
    update_steps: List[Dict[str, Any]]
    batter_records_added: int
    pitcher_records_added: int
    update_success: bool
    # 복구
    retry_count: int
    failed_methods: List[str]
    # 검증
    quality_report: Optional[Dict[str, Any]]
    post_update_valid: bool
    # 보고
    status_report: str
    # 메타데이터
    lang: str
    error: Optional[str]
