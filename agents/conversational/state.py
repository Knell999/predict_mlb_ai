"""대화형 Agent 상태 정의"""

from typing import TypedDict, Annotated, Optional, List, Dict, Any
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage


class ConversationalState(TypedDict):
    """대화형 분석 Agent의 상태"""
    # 대화 이력 (add_messages reducer로 자동 누적)
    messages: Annotated[list[BaseMessage], add_messages]
    # 라우팅 의도
    current_intent: str  # "profile"|"compare"|"trend"|"predict"|"root_cause"|"general"
    # 데이터 컨텍스트
    player_name: Optional[str]
    player_names: Optional[List[str]]
    player_type: str  # "batter"|"pitcher"
    # 메타데이터
    lang: str
    error: Optional[str]
