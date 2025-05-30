"""
트렌드 분석 모듈: 리그 추세와 트렌드를 분석하는 클래스와 함수를 제공합니다.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import streamlit as st

class TrendAnalyzer:
    """트렌드 분석 클래스"""
    def __init__(self, data_manager):
        """
        TrendAnalyzer 클래스 초기화
        
        Args:
            data_manager: 데이터 관리자 인스턴스
        """
        self.data_manager = data_manager
        
    def analyze_league_trends(self, metrics: List[str], player_type: str = 'batter', window_sizes: List[int] = [5, 10, 20]) -> Dict[str, Any]:
        """
        리그 평균 지표의 트렌드를 분석합니다.
        
        Args:
            metrics: 분석할 지표 리스트
            player_type: 선수 유형 ('batter' 또는 'pitcher')
            window_sizes: 이동평균 윈도우 크기 리스트
            
        Returns:
            Dict[str, Any]: 트렌드 분석 결과
        """
        # 리그 평균 계산
        league_avg = self.data_manager.calculate_league_averages(metrics, player_type)
        
        # 각 윈도우 크기별 이동평균 계산
        moving_avgs = {}
        for window in window_sizes:
            moving_avgs[window] = self.data_manager.calculate_moving_average(league_avg, metrics, window)
            
        # 결과 정리
        result = {
            'league_avg': league_avg,
            'moving_avgs': moving_avgs,
            'metrics': metrics,
            'player_type': player_type
        }
        
        return result
    
    def analyze_player_trends(self, player_name: str, metrics: List[str], player_type: str = 'batter') -> Dict[str, Any]:
        """
        특정 선수의 지표 트렌드를 분석합니다.
        
        Args:
            player_name: 선수 이름
            metrics: 분석할 지표 리스트
            player_type: 선수 유형 ('batter' 또는 'pitcher')
            
        Returns:
            Dict[str, Any]: 트렌드 분석 결과
        """
        # 선수 데이터 조회
        player_data = self.data_manager.get_player_data(player_name, player_type)
        
        # 리그 평균 계산
        league_avg = self.data_manager.calculate_league_averages(metrics, player_type)
        
        # 분석 결과 정리
        result = {
            'player_data': player_data,
            'league_avg': league_avg,
            'metrics': metrics,
            'player_name': player_name,
            'player_type': player_type
        }
        
        return result
    
    def get_trend_insights(self, metrics: List[str], player_type: str = 'batter', years: int = 5) -> List[Dict[str, Any]]:
        """
        리그 트렌드에 대한 인사이트를 생성합니다.
        
        Args:
            metrics: 분석할 지표 리스트
            player_type: 선수 유형 ('batter' 또는 'pitcher')
            years: 분석할 최근 연도 수
            
        Returns:
            List[Dict[str, Any]]: 트렌드 인사이트 목록
        """
        # 리그 평균 계산
        league_avg = self.data_manager.calculate_league_averages(metrics, player_type)
        
        # 최근 연도만 필터링
        max_year = league_avg['Season'].max()
        recent_data = league_avg[league_avg['Season'] >= max_year - years + 1]
        
        insights = []
        
        for metric in metrics:
            # 지표 변화율 계산
            first_value = recent_data.iloc[0][metric]
            last_value = recent_data.iloc[-1][metric]
            change_pct = (last_value - first_value) / first_value * 100 if first_value != 0 else 0
            
            # 변화 방향 결정
            trend = "증가" if change_pct > 0 else "감소"
            
            # 연간 평균 변화율
            annual_change_pct = change_pct / years
            
            # 인사이트 생성
            insight = {
                'metric': metric,
                'first_year': recent_data.iloc[0]['Season'],
                'last_year': recent_data.iloc[-1]['Season'],
                'first_value': first_value,
                'last_value': last_value,
                'change_pct': change_pct,
                'annual_change_pct': annual_change_pct,
                'trend': trend
            }
            
            insights.append(insight)
            
        return insights
