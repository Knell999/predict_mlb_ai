"""
차트 컴포넌트 모듈: 시각화를 위한 차트와 그래프를 제공합니다.
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.font_manager as fm
from matplotlib import ticker
from typing import Dict, List, Any, Tuple, Optional
import streamlit as st

class ChartComponents:
    """차트 컴포넌트 클래스"""
    
    def __init__(self, font_path: Optional[str] = None):
        """
        ChartComponents 클래스 초기화
        
        Args:
            font_path: 사용할 폰트 경로
        """
        self.font_path = font_path
        if font_path:
            self.fontprop = fm.FontProperties(fname=font_path, size=12)
        else:
            self.fontprop = None
        
        # 차트 스타일 설정
        self.set_chart_style()
            
    def set_chart_style(self):
        """
        Matplotlib 및 Seaborn 차트 스타일을 설정합니다.
        """
        # Seaborn 스타일 설정
        sns.set_style("whitegrid")
        
        # Matplotlib 설정
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['axes.grid'] = True
        plt.rcParams['axes.grid.which'] = 'both'
        plt.rcParams['axes.axisbelow'] = True
        plt.rcParams['grid.linestyle'] = '--'
        plt.rcParams['grid.linewidth'] = 0.5
        plt.rcParams['grid.alpha'] = 0.7
        
        # 한글 폰트 설정 (폰트가 제공된 경우)
        if self.fontprop:
            plt.rcParams['font.family'] = self.fontprop.get_name()
            
    @staticmethod
    def create_prediction_chart(prediction_result: Dict[str, Any], metric: str, lang: str = "ko") -> plt.Figure:
        """
        예측 차트를 생성합니다.
        
        Args:
            prediction_result: 예측 결과 데이터
            metric: 차트에 표시할 지표
            lang: 언어 코드
            
        Returns:
            plt.Figure: Matplotlib 그림 객체
        """
        # 언어별 레이블 설정
        labels = {
            'ko': {
                'title': f"{prediction_result['player_name']}의 {metric} 예측",
                'actual': '실제',
                'predicted': '예측',
                'season': '시즌'
            },
            'en': {
                'title': f"{prediction_result['player_name']}'s {metric} Prediction",
                'actual': 'Actual',
                'predicted': 'Predicted',
                'season': 'Season'
            },
            'ja': {
                'title': f"{prediction_result['player_name']}の{metric}予測",
                'actual': '実際',
                'predicted': '予測',
                'season': 'シーズン'
            }
        }
        
        # 기본 언어가 없으면 한국어 사용
        curr_labels = labels.get(lang, labels['ko'])
        
        # 그림 및 축 생성
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 예측 결과에서 데이터 추출
        seasons = prediction_result['seasons']
        actual = prediction_result['actual']
        predicted = prediction_result['predicted']
        lower = prediction_result['lower']
        upper = prediction_result['upper']
        
        # 실제 데이터와 예측 데이터의 경계 찾기
        last_actual_idx = next((i for i, val in enumerate(actual) if val is None), len(actual)) - 1
        
        # 실제 데이터 플롯
        ax.plot(seasons[:last_actual_idx+1], actual[:last_actual_idx+1], 
                marker='o', linestyle='-', color='blue', label=curr_labels['actual'])
        
        # 예측 데이터 플롯
        ax.plot(seasons, predicted, marker='s', linestyle='--', color='red', label=curr_labels['predicted'])
        
        # 신뢰 구간 플롯
        ax.fill_between(seasons, lower, upper, color='red', alpha=0.2)
        
        # 축 설정
        ax.set_xlabel(curr_labels['season'])
        ax.set_ylabel(metric)
        ax.set_title(curr_labels['title'])
        
        # 범례 추가
        ax.legend()
        
        # 그리드 설정
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # x축 틱 조정
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        
        return fig
    
    @staticmethod
    def create_trend_chart(trend_result: Dict[str, Any], metric: str, lang: str = "ko") -> plt.Figure:
        """
        트렌드 차트를 생성합니다.
        
        Args:
            trend_result: 트렌드 분석 결과
            metric: 차트에 표시할 지표
            lang: 언어 코드
            
        Returns:
            plt.Figure: Matplotlib 그림 객체
        """
        # 언어별 레이블 설정
        labels = {
            'ko': {
                'title': f"리그 평균 {metric} 추이",
                'league_avg': '리그 평균',
                'moving_avg_5': '5년 이동평균',
                'moving_avg_10': '10년 이동평균',
                'moving_avg_20': '20년 이동평균',
                'season': '시즌'
            },
            'en': {
                'title': f"League Average {metric} Trend",
                'league_avg': 'League Average',
                'moving_avg_5': '5-Year Moving Average',
                'moving_avg_10': '10-Year Moving Average',
                'moving_avg_20': '20-Year Moving Average',
                'season': 'Season'
            },
            'ja': {
                'title': f"リーグ平均 {metric} 推移",
                'league_avg': 'リーグ平均',
                'moving_avg_5': '5年移動平均',
                'moving_avg_10': '10年移動平均',
                'moving_avg_20': '20年移動平均',
                'season': 'シーズン'
            }
        }
        
        # 기본 언어가 없으면 한국어 사용
        curr_labels = labels.get(lang, labels['ko'])
        
        # 그림 및 축 생성
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 리그 평균 데이터
        league_avg = trend_result['league_avg']
        moving_avgs = trend_result['moving_avgs']
        
        # 리그 평균 플롯
        ax.plot(league_avg['Season'], league_avg[metric], 
                marker='o', linestyle='-', color='blue', label=curr_labels['league_avg'])
        
        # 이동평균 플롯
        colors = ['red', 'green', 'purple']
        for i, (window, df) in enumerate(moving_avgs.items()):
            label_key = f'moving_avg_{window}'
            ax.plot(df['Season'], df[metric], 
                    marker='', linestyle='--', color=colors[i % len(colors)], 
                    label=curr_labels.get(label_key, f'{window}년 이동평균'))
        
        # 축 설정
        ax.set_xlabel(curr_labels['season'])
        ax.set_ylabel(metric)
        ax.set_title(curr_labels['title'])
        
        # 범례 추가
        ax.legend()
        
        # 그리드 설정
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # x축 틱 조정
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        
        return fig
    
    @staticmethod
    def create_player_comparison_chart(player_data: pd.DataFrame, league_avg: pd.DataFrame, 
                                      metric: str, lang: str = "ko") -> plt.Figure:
        """
        선수와 리그 평균을 비교하는 차트를 생성합니다.
        
        Args:
            player_data: 선수 데이터
            league_avg: 리그 평균 데이터
            metric: 차트에 표시할 지표
            lang: 언어 코드
            
        Returns:
            plt.Figure: Matplotlib 그림 객체
        """
        # 언어별 레이블 설정
        labels = {
            'ko': {
                'title': f"{player_data['PlayerName'].iloc[0]}의 {metric} vs 리그 평균",
                'player': '선수',
                'league_avg': '리그 평균',
                'season': '시즌'
            },
            'en': {
                'title': f"{player_data['PlayerName'].iloc[0]}'s {metric} vs League Average",
                'player': 'Player',
                'league_avg': 'League Average',
                'season': 'Season'
            },
            'ja': {
                'title': f"{player_data['PlayerName'].iloc[0]}の{metric} vs リーグ平均",
                'player': '選手',
                'league_avg': 'リーグ平均',
                'season': 'シーズン'
            }
        }
        
        # 기본 언어가 없으면 한국어 사용
        curr_labels = labels.get(lang, labels['ko'])
        
        # 그림 및 축 생성
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 선수 데이터 정렬
        player_data = player_data.sort_values(by='Season')
        
        # 선수 데이터 플롯
        ax.plot(player_data['Season'], player_data[metric], 
                marker='o', linestyle='-', color='blue', label=curr_labels['player'])
        
        # 리그 평균 데이터 플롯
        common_seasons = set(player_data['Season']).intersection(set(league_avg['Season']))
        filtered_league_avg = league_avg[league_avg['Season'].isin(common_seasons)]
        filtered_league_avg = filtered_league_avg.sort_values(by='Season')
        
        ax.plot(filtered_league_avg['Season'], filtered_league_avg[metric], 
                marker='s', linestyle='--', color='red', label=curr_labels['league_avg'])
        
        # 축 설정
        ax.set_xlabel(curr_labels['season'])
        ax.set_ylabel(metric)
        ax.set_title(curr_labels['title'])
        
        # 범례 추가
        ax.legend()
        
        # 그리드 설정
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # x축 틱 조정
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        
        return fig
    
    @staticmethod
    def create_histogram(data: pd.DataFrame, metric: str, player_value: Optional[float] = None, 
                         bins: int = 20, lang: str = "ko") -> plt.Figure:
        """
        데이터 분포를 보여주는 히스토그램을 생성합니다.
        
        Args:
            data: 히스토그램에 표시할 데이터
            metric: 차트에 표시할 지표
            player_value: 히스토그램에 표시할 특정 선수의 값
            bins: 히스토그램 빈(구간) 수
            lang: 언어 코드
            
        Returns:
            plt.Figure: Matplotlib 그림 객체
        """
        # 언어별 레이블 설정
        labels = {
            'ko': {
                'title': f"{metric} 분포",
                'player_value': '선수 값',
                'frequency': '빈도'
            },
            'en': {
                'title': f"{metric} Distribution",
                'player_value': 'Player Value',
                'frequency': 'Frequency'
            },
            'ja': {
                'title': f"{metric} 分布",
                'player_value': '選手の値',
                'frequency': '頻度'
            }
        }
        
        # 기본 언어가 없으면 한국어 사용
        curr_labels = labels.get(lang, labels['ko'])
        
        # 그림 및 축 생성
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 히스토그램 플롯
        sns.histplot(data[metric].dropna(), bins=bins, kde=True, ax=ax)
        
        # 선수 값이 제공된 경우 수직선 추가
        if player_value is not None:
            ax.axvline(x=player_value, color='red', linestyle='--', 
                       label=f"{curr_labels['player_value']}: {player_value:.3f}")
            ax.legend()
        
        # 축 설정
        ax.set_xlabel(metric)
        ax.set_ylabel(curr_labels['frequency'])
        ax.set_title(curr_labels['title'])
        
        # 그리드 설정
        ax.grid(True, linestyle='--', alpha=0.7)
        
        return fig
