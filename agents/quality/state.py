"""품질 Agent 상태 정의"""

from typing import TypedDict, Optional, List, Dict, Any


class QualityState(TypedDict):
    """데이터 품질 검증 Agent의 상태"""
    # 검증 결과
    file_check: Dict[str, bool]
    schema_validation: Dict[str, Any]
    range_violations: Dict[str, Any]
    duplicate_check: Dict[str, int]
    anomalies: List[Dict[str, Any]]
    # LLM 해석
    anomaly_interpretations: List[Dict[str, Any]]
    # 보고서
    quality_score: float
    report_markdown: str
    recommendations: List[str]
    # 메타데이터
    trigger: str  # "manual"|"post_update"|"scheduled"
    lang: str
    error: Optional[str]
