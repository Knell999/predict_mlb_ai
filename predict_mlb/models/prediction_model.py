"""
예측 모델 모듈: 선수 기록 예측을 위한 클래스와 함수를 제공합니다.
"""
import pandas as pd
import numpy as np
from prophet import Prophet
from typing import Dict, List, Any, Optional, Tuple
import streamlit as st

class PredictionModel:
    """예측 모델 클래스"""
    def __init__(self, min_seasons: int = 2):
        """
        PredictionModel 클래스 초기화
        
        Args:
            min_seasons: 예측에 필요한 최소 시즌 수
        """
        self.model = None
        self.min_seasons = min_seasons
        
    def prepare_data(self, player_data: pd.DataFrame, metric: str) -> pd.DataFrame:
        """
        Prophet 모델에 맞게 데이터를 준비합니다.
        
        Args:
            player_data: 선수 데이터
            metric: 예측할 지표
            
        Returns:
            pd.DataFrame: Prophet 모델용 데이터프레임
        """
        # Prophet은 'ds'와 'y' 컬럼을 필요로 함
        prophet_data = player_data[['Season', metric]].rename(columns={
            'Season': 'ds',
            metric: 'y'
        })
        # ds 컬럼을 datetime 형식으로 변환 (Prophet 요구사항)
        prophet_data['ds'] = pd.to_datetime(prophet_data['ds'], format='%Y')
        return prophet_data
    
    def train_model(self, data: pd.DataFrame, yearly_seasonality: bool = False) -> Prophet:
        """
        Prophet 모델을 훈련합니다.
        
        Args:
            data: 훈련 데이터
            yearly_seasonality: 연간 계절성 사용 여부
            
        Returns:
            Prophet: 훈련된 Prophet 모델
        """
        model = Prophet(yearly_seasonality=yearly_seasonality)
        model.fit(data)
        self.model = model
        return model
        
    def predict(self, player_data: pd.DataFrame, metric: str, periods: int = 5) -> Dict[str, Any]:
        """
        선수의 특정 지표에 대한 예측을 수행합니다.
        
        Args:
            player_data: 선수 데이터
            metric: 예측할 지표
            periods: 예측할 미래 기간 (연도 수)
            
        Returns:
            Dict[str, Any]: 예측 결과 및 관련 정보
        """
        # 최소 시즌 수 확인
        if len(player_data) < self.min_seasons:
            return {"error": f"예측에 필요한 데이터가 부족합니다. 최소 {self.min_seasons}개 시즌이 필요합니다."}
        
        # 데이터 준비
        prophet_data = self.prepare_data(player_data, metric)
        
        # 모델 훈련
        model = self.train_model(prophet_data)
        
        # 미래 예측을 위한 데이터프레임 생성
        future = model.make_future_dataframe(periods=periods, freq='Y')
        
        # 예측 수행
        forecast = model.predict(future)
        
        # 예측 결과 포맷팅
        result = {
            'seasons': [],
            'actual': [],
            'predicted': [],
            'lower': [],
            'upper': []
        }
        
        # 실제 데이터
        for i, row in prophet_data.iterrows():
            season = row['ds'].year
            result['seasons'].append(season)
            result['actual'].append(row['y'])
            
            # 해당 시즌의 예측값 찾기
            forecast_row = forecast[forecast['ds'] == row['ds']]
            if not forecast_row.empty:
                result['predicted'].append(forecast_row['yhat'].values[0])
                result['lower'].append(forecast_row['yhat_lower'].values[0])
                result['upper'].append(forecast_row['yhat_upper'].values[0])
            else:
                result['predicted'].append(None)
                result['lower'].append(None)
                result['upper'].append(None)
        
        # 미래 예측값
        last_season = prophet_data['ds'].dt.year.max()
        for i in range(1, periods + 1):
            future_season = last_season + i
            result['seasons'].append(future_season)
            result['actual'].append(None)  # 미래 데이터는 실제값 없음
            
            # 예측값 찾기
            forecast_row = forecast[forecast['ds'].dt.year == future_season]
            if not forecast_row.empty:
                result['predicted'].append(forecast_row['yhat'].values[0])
                result['lower'].append(forecast_row['yhat_lower'].values[0])
                result['upper'].append(forecast_row['yhat_upper'].values[0])
            else:
                result['predicted'].append(None)
                result['lower'].append(None)
                result['upper'].append(None)
        
        # 추가 정보
        result['metric'] = metric
        result['player_name'] = player_data['PlayerName'].iloc[0]
        result['model'] = model
        result['forecast'] = forecast
        
        return result

    @st.cache_data(ttl=3600)
    def predict_multiple_metrics(self, player_data: pd.DataFrame, metrics: List[str], periods: int = 5) -> Dict[str, Dict[str, Any]]:
        """
        여러 지표에 대한 예측을 수행합니다.
        
        Args:
            player_data: 선수 데이터
            metrics: 예측할 지표 리스트
            periods: 예측할 미래 기간 (연도 수)
            
        Returns:
            Dict[str, Dict[str, Any]]: 각 지표별 예측 결과
        """
        results = {}
        for metric in metrics:
            results[metric] = self.predict(player_data, metric, periods)
        return results
