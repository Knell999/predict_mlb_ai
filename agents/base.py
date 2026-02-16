"""
Agent 공통 기반 모듈
LLM 팩토리, 가용성 체크 등 모든 Agent가 공유하는 유틸리티를 제공합니다.
"""

import os
import logging
from typing import Optional

from config import AI_MODEL_NAME, AI_TEMPERATURE, AI_MAX_TOKENS

logger = logging.getLogger(__name__)

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

try:
    from langgraph.graph import StateGraph
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False


def create_llm(
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> Optional["ChatGoogleGenerativeAI"]:
    """LLM 인스턴스를 생성합니다.

    Args:
        temperature: 생성 온도 (None이면 config 기본값 사용)
        max_tokens: 최대 토큰 수 (None이면 config 기본값 사용)

    Returns:
        ChatGoogleGenerativeAI 인스턴스 또는 사용 불가 시 None
    """
    if not LANGCHAIN_AVAILABLE:
        logger.warning("LangChain 라이브러리가 설치되지 않았습니다.")
        return None

    api_key = os.getenv("GOOGLE_AI_API_KEY")
    if not api_key:
        logger.warning("GOOGLE_AI_API_KEY 환경변수가 설정되지 않았습니다.")
        return None

    try:
        return ChatGoogleGenerativeAI(
            model=AI_MODEL_NAME,
            google_api_key=api_key,
            temperature=temperature if temperature is not None else AI_TEMPERATURE,
            max_tokens=max_tokens if max_tokens is not None else AI_MAX_TOKENS,
        )
    except Exception as e:
        logger.error(f"LLM 인스턴스 생성 실패: {e}")
        return None


def is_llm_available() -> bool:
    """LLM 사용 가능 여부를 확인합니다."""
    return LANGCHAIN_AVAILABLE and bool(os.getenv("GOOGLE_AI_API_KEY"))


def is_langgraph_available() -> bool:
    """LangGraph 사용 가능 여부를 확인합니다."""
    return LANGGRAPH_AVAILABLE and is_llm_available()
