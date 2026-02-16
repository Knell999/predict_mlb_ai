"""리포트 Agent 상태 정의"""

from typing import TypedDict, Optional, List, Dict, Any


class ReportState(TypedDict):
    """자동 리포트 생성 Agent의 상태"""
    # 입력
    player_name: str
    player_type: str  # "batter"|"pitcher"
    report_type: str  # "full"|"season_summary"|"comparison"
    include_predictions: bool
    comparison_player: Optional[str]
    # 데이터
    player_data: Optional[Dict[str, Any]]
    league_averages: Optional[Dict[str, Any]]
    prediction_data: Optional[Dict[str, Any]]
    # 섹션
    section_profile: str
    section_metrics: str
    section_trends: str
    section_predictions: str
    section_comparisons: str
    # 조립
    full_report: str
    report_title: str
    # 메타데이터
    lang: str
    error: Optional[str]
