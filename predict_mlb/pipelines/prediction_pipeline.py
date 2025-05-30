"""
예측 파이프라인 모듈: 예측 처리 파이프라인을 정의합니다.
"""
from typing import Dict, List, Any, Optional, Callable, Protocol
import pandas as pd

class PredictionStep(Protocol):
    """예측 단계 프로토콜"""
    def execute(self, data: pd.DataFrame, metric: str) -> Any:
        """
        예측 단계를 실행합니다.
        
        Args:
            data: 처리할 데이터
            metric: 예측할 지표
            
        Returns:
            Any: 처리 결과
        """
        ...

class DataPreparationStep:
    """데이터 준비 단계"""
    
    def __init__(self, min_seasons: int = 2):
        """
        DataPreparationStep 클래스 초기화
        
        Args:
            min_seasons: 필요한 최소 시즌 수
        """
        self.min_seasons = min_seasons
        
    def execute(self, data: pd.DataFrame, metric: str) -> pd.DataFrame:
        """
        데이터 준비 단계를 실행합니다.
        
        Args:
            data: 처리할 데이터
            metric: 예측할 지표
            
        Returns:
            pd.DataFrame: 준비된 데이터
            
        Raises:
            ValueError: 데이터가 부족한 경우
        """
        if len(data) < self.min_seasons:
            raise ValueError(f"예측에 필요한 데이터가 부족합니다. 최소 {self.min_seasons}개 시즌이 필요합니다.")
            
        # 필요한 컬럼만 선택
        prepared_data = data[['Season', metric]].copy()
        
        # null 값 확인 및 처리
        if prepared_data[metric].isnull().any():
            prepared_data[metric] = prepared_data[metric].fillna(prepared_data[metric].mean())
            
        return prepared_data

class ModelTrainingStep:
    """모델 훈련 단계"""
    
    def __init__(self, model_factory: Callable[[], Any]):
        """
        ModelTrainingStep 클래스 초기화
        
        Args:
            model_factory: 모델 객체를 생성하는 팩토리 함수
        """
        self.model_factory = model_factory
        
    def execute(self, data: pd.DataFrame, metric: str) -> Any:
        """
        모델 훈련 단계를 실행합니다.
        
        Args:
            data: 훈련 데이터
            metric: 예측할 지표
            
        Returns:
            Any: 훈련된 모델
        """
        # Prophet 모델용 데이터프레임 변환
        prophet_data = data.rename(columns={
            'Season': 'ds',
            metric: 'y'
        })
        
        # ds 컬럼을 datetime 형식으로 변환
        prophet_data['ds'] = pd.to_datetime(prophet_data['ds'], format='%Y')
        
        # 모델 생성 및 훈련
        model = self.model_factory()
        model.fit(prophet_data)
        
        return {
            'model': model,
            'training_data': prophet_data
        }

class PredictionExecutionStep:
    """예측 실행 단계"""
    
    def __init__(self, periods: int = 5):
        """
        PredictionExecutionStep 클래스 초기화
        
        Args:
            periods: 예측할 미래 기간 (연도 수)
        """
        self.periods = periods
        
    def execute(self, model_data: Dict[str, Any], metric: str) -> Dict[str, Any]:
        """
        예측 실행 단계를 실행합니다.
        
        Args:
            model_data: 모델 및 훈련 데이터
            metric: 예측할 지표
            
        Returns:
            Dict[str, Any]: 예측 결과
        """
        model = model_data['model']
        training_data = model_data['training_data']
        
        # 미래 예측을 위한 데이터프레임 생성
        future = model.make_future_dataframe(periods=self.periods, freq='Y')
        
        # 예측 수행
        forecast = model.predict(future)
        
        # 예측 결과 포맷팅
        result = self._format_forecast(training_data, forecast, metric)
        
        return result
    
    def _format_forecast(self, training_data: pd.DataFrame, forecast: pd.DataFrame, 
                         metric: str) -> Dict[str, Any]:
        """
        예측 결과를 포맷팅합니다.
        
        Args:
            training_data: 훈련 데이터
            forecast: 예측 결과
            metric: 예측한 지표
            
        Returns:
            Dict[str, Any]: 포맷팅된 예측 결과
        """
        result = {
            'seasons': [],
            'actual': [],
            'predicted': [],
            'lower': [],
            'upper': []
        }
        
        # 실제 데이터
        for i, row in training_data.iterrows():
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
        last_season = training_data['ds'].dt.year.max()
        for i in range(1, self.periods + 1):
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
        result['forecast'] = forecast
        
        return result

class PredictionPipeline:
    """예측 파이프라인"""
    
    def __init__(self):
        """PredictionPipeline 클래스 초기화"""
        self.steps = []
        
    def add_step(self, step: PredictionStep) -> None:
        """
        파이프라인에 단계를 추가합니다.
        
        Args:
            step: 추가할 예측 단계
        """
        self.steps.append(step)
        
    def execute(self, player_data: pd.DataFrame, metrics: List[str]) -> Dict[str, Any]:
        """
        예측 파이프라인을 실행합니다.
        
        Args:
            player_data: 선수 데이터
            metrics: 예측할 지표 리스트
            
        Returns:
            Dict[str, Any]: 각 지표별 예측 결과
        """
        results = {}
        
        for metric in metrics:
            try:
                # 파이프라인 단계 실행
                current_data = player_data
                for step in self.steps:
                    current_data = step.execute(current_data, metric)
                
                # 결과 저장
                results[metric] = current_data
                results[metric]['player_name'] = player_data['PlayerName'].iloc[0]
                
            except Exception as e:
                # 오류 발생 시 오류 정보 저장
                results[metric] = {
                    'error': str(e),
                    'player_name': player_data['PlayerName'].iloc[0]
                }
                
        return results
