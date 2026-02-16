"""유사 선수 Agent 상태 정의"""

from typing import TypedDict, Optional, List, Dict, Any


class SimilarityState(TypedDict):
    """유사 선수 발견 Agent의 상태"""
    # 입력
    query: str
    # 파싱된 조건
    target_player: Optional[str]
    target_metrics: Optional[Dict[str, float]]
    player_type: str  # "batter"|"pitcher"
    season_filter: Optional[int]
    top_n: int
    similarity_metrics: List[str]
    # 결과
    candidates: List[Dict[str, Any]]
    # 설명
    explanation: str
    # 메타데이터
    lang: str
    error: Optional[str]
