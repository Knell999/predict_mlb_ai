import time
import streamlit as st
import pandas as pd
import logging
from datetime import datetime
import os

__all__ = ['MetricTracker', 'timing_decorator', 'init_metrics']

# 로그 설정
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{log_dir}/app_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('mlb_stats_app')

class MetricTracker:
    """애플리케이션 메트릭을 추적하는 클래스"""
    
    def __init__(self):
        self.metrics = {
            "page_views": {},
            "player_searches": {},
            "season_selections": {},
            "response_times": [],
            "errors": []
        }
        
    def log_page_view(self, page_name):
        """페이지 뷰 로깅"""
        if page_name in self.metrics["page_views"]:
            self.metrics["page_views"][page_name] += 1
        else:
            self.metrics["page_views"][page_name] = 1
        logger.info(f"Page view: {page_name}")
        
    def log_player_search(self, player_name):
        """선수 검색 로깅"""
        if player_name and player_name != "":  # 빈 문자열 필터링
            if player_name in self.metrics["player_searches"]:
                self.metrics["player_searches"][player_name] += 1
            else:
                self.metrics["player_searches"][player_name] = 1
            logger.info(f"Player searched: {player_name}")
            
    def log_season_selection(self, season):
        """시즌 선택 로깅"""
        if season:
            season_str = str(season)
            if season_str in self.metrics["season_selections"]:
                self.metrics["season_selections"][season_str] += 1
            else:
                self.metrics["season_selections"][season_str] = 1
            logger.info(f"Season selected: {season}")
            
    def log_response_time(self, operation, time_ms):
        """응답 시간 로깅"""
        self.metrics["response_times"].append({
            "operation": operation,
            "time_ms": time_ms,
            "timestamp": datetime.now().isoformat()
        })
        logger.info(f"Response time for {operation}: {time_ms:.2f} ms")
        
    def log_error(self, error_type, error_message, detail=None):
        """오류 로깅"""
        error_data = {
            "type": error_type,
            "message": error_message,
            "timestamp": datetime.now().isoformat()
        }
        if detail:
            error_data["detail"] = detail
            
        self.metrics["errors"].append(error_data)
        logger.error(f"Error ({error_type}): {error_message} - {detail if detail else ''}")
    
    def get_summary(self):
        """메트릭 요약 조회"""
        return {
            "total_page_views": sum(self.metrics["page_views"].values()),
            "popular_pages": sorted(self.metrics["page_views"].items(), key=lambda x: x[1], reverse=True)[:5],
            "top_players": sorted(self.metrics["player_searches"].items(), key=lambda x: x[1], reverse=True)[:10],
            "popular_seasons": sorted(self.metrics["season_selections"].items(), key=lambda x: x[1], reverse=True)[:5],
            "avg_response_time": sum([r["time_ms"] for r in self.metrics["response_times"]]) / max(len(self.metrics["response_times"]), 1),
            "error_count": len(self.metrics["errors"])
        }
        
    def reset_metrics(self):
        """메트릭 초기화"""
        self.__init__()


# 성능 측정 데코레이터
def timing_decorator(func):
    """함수 실행 시간을 측정하는 데코레이터"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # milliseconds
        
        # 글로벌 메트릭 트래커가 초기화되어 있다면 응답 시간 로깅
        if 'metric_tracker' in st.session_state:
            st.session_state.metric_tracker.log_response_time(func.__name__, execution_time)
        
        return result
    return wrapper


# 세션 상태에서 메트릭 트래커 초기화
def init_metrics():
    """세션 상태에 메트릭 트래커 초기화"""
    if 'metric_tracker' not in st.session_state:
        st.session_state.metric_tracker = MetricTracker()
    
    return st.session_state.metric_tracker
