"""예측 Agent 상태 정의"""

from typing import TypedDict, Optional, List, Dict, Any


class PredictionState(TypedDict):
    """지능형 예측 Agent의 상태"""
    # 입력
    player_name: str
    player_type: str  # "batter"|"pitcher"
    metrics: List[str]
    prediction_years: int
    # 데이터 평가
    player_data: Optional[Dict[str, Any]]
    data_seasons: int
    data_adequate: bool
    data_assessment: str
    # 맥락 분석
    player_age_curve: Optional[str]
    similar_players_context: Optional[str]
    # 예측 결과
    forecasts: Dict[str, Dict[str, Any]]
    # 해석
    interpretation: str
    confidence_assessment: str
    # 메타데이터
    lang: str
    error: Optional[str]
