"""
에러 처리 모듈: 예외 처리 및 오류 관리 기능을 제공합니다.
"""
import logging
from typing import Any, Callable, Optional, TypeVar, Dict
import traceback
import streamlit as st

T = TypeVar('T')

class ErrorHandler:
    """에러 처리 클래스"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        ErrorHandler 클래스 초기화
        
        Args:
            logger: 로깅에 사용할 Logger 객체
        """
        self.logger = logger or logging.getLogger(__name__)
        
    def handle_data_error(self, error: Exception, fallback_action: Optional[Callable[[], T]] = None) -> Optional[T]:
        """
        데이터 관련 에러 처리
        
        Args:
            error: 발생한 예외
            fallback_action: 오류 발생 시 실행할 대체 함수
            
        Returns:
            Optional[T]: fallback_action이 제공된 경우 그 결과, 아니면 None
        """
        self.logger.error(f"Data error: {error}")
        self.logger.debug(traceback.format_exc())
        
        if fallback_action:
            try:
                return fallback_action()
            except Exception as fallback_error:
                self.logger.error(f"Fallback action error: {fallback_error}")
                
        return None
        
    def handle_prediction_error(self, error: Exception, player_name: str) -> Dict[str, Any]:
        """
        예측 관련 에러 처리
        
        Args:
            error: 발생한 예외
            player_name: 예측 대상 선수 이름
            
        Returns:
            Dict[str, Any]: 오류 정보
        """
        self.logger.error(f"Prediction error for {player_name}: {error}")
        self.logger.debug(traceback.format_exc())
        
        return {
            "error": f"예측을 수행할 수 없습니다: {error}",
            "player_name": player_name
        }
        
    def handle_ui_error(self, error: Exception, error_message: str = None) -> None:
        """
        UI 관련 에러 처리 (Streamlit 화면에 표시)
        
        Args:
            error: 발생한 예외
            error_message: 사용자에게 표시할 오류 메시지
        """
        self.logger.error(f"UI error: {error}")
        self.logger.debug(traceback.format_exc())
        
        # 오류 메시지가 없으면 예외 내용 사용
        message = error_message or f"오류가 발생했습니다: {error}"
        st.error(message)
        
    def handle_generic_error(self, error: Exception, context: str = "") -> None:
        """
        일반적인 에러 처리
        
        Args:
            error: 발생한 예외
            context: 오류가 발생한 컨텍스트 정보
        """
        self.logger.error(f"Error in {context}: {error}")
        self.logger.debug(traceback.format_exc())


def safe_execute(func: Callable[..., T], *args, **kwargs) -> Optional[T]:
    """
    함수를 안전하게 실행하는 데코레이터
    
    Args:
        func: 실행할 함수
        *args: 함수에 전달할 위치 인자
        **kwargs: 함수에 전달할 키워드 인자
        
    Returns:
        Optional[T]: 함수 실행 결과 또는 오류 발생 시 None
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error executing {func.__name__}: {e}")
        logger.debug(traceback.format_exc())
        return None
