"""
데이터 검증 모듈: 데이터 유효성 검사 기능을 제공합니다.
"""
from typing import List, Dict, Any, Optional
import pandas as pd

class DataValidator:
    """데이터 검증 클래스"""
    
    @staticmethod
    def validate_player_data(data: pd.DataFrame) -> bool:
        """
        선수 데이터 검증
        
        Args:
            data: 검증할 데이터프레임
            
        Returns:
            bool: 검증 성공 시 True, 실패 시 False
        """
        required_columns = ['PlayerID', 'PlayerName', 'Season']
        return all(col in data.columns for col in required_columns)
        
    @staticmethod
    def validate_metrics(data: pd.DataFrame, metrics: List[str]) -> bool:
        """
        메트릭 데이터 검증
        
        Args:
            data: 검증할 데이터프레임
            metrics: 검증할 메트릭 목록
            
        Returns:
            bool: 검증 성공 시 True, 실패 시 False
        """
        return all(metric in data.columns for metric in metrics)
        
    @staticmethod
    def check_data_completeness(data: pd.DataFrame, min_seasons: int = 2) -> bool:
        """
        데이터 완성도 검사
        
        Args:
            data: 검증할 데이터프레임
            min_seasons: 필요한 최소 시즌 수
            
        Returns:
            bool: 검증 성공 시 True, 실패 시 False
        """
        if 'Season' not in data.columns:
            return False
            
        return len(data['Season'].unique()) >= min_seasons
    
    @staticmethod
    def validate_numeric_range(data: pd.DataFrame, column: str, min_val: float, max_val: float) -> bool:
        """
        숫자 데이터 범위 검증
        
        Args:
            data: 검증할 데이터프레임
            column: 검증할 컬럼
            min_val: 최소값
            max_val: 최대값
            
        Returns:
            bool: 검증 성공 시 True, 실패 시 False
        """
        if column not in data.columns:
            return False
            
        col_data = data[column].dropna()
        if len(col_data) == 0:
            return False
            
        return col_data.min() >= min_val and col_data.max() <= max_val
    
    @staticmethod
    def validate_recent_data(data: pd.DataFrame, required_years: List[int]) -> bool:
        """
        최근 데이터 존재 여부 검증
        
        Args:
            data: 검증할 데이터프레임
            required_years: 필요한 연도 목록
            
        Returns:
            bool: 검증 성공 시 True, 실패 시 False
        """
        if 'Season' not in data.columns:
            return False
            
        seasons = data['Season'].unique()
        return all(year in seasons for year in required_years)
    
    @staticmethod
    def get_data_quality_score(data: pd.DataFrame, metrics: List[str]) -> Dict[str, Any]:
        """
        데이터 품질 점수 계산
        
        Args:
            data: 평가할 데이터프레임
            metrics: 평가할 메트릭 목록
            
        Returns:
            Dict[str, Any]: 데이터 품질 점수 및 관련 정보
        """
        result = {
            'completeness': 0.0,
            'validity': 0.0,
            'consistency': 0.0,
            'overall_score': 0.0,
            'issues': []
        }
        
        # 완전성 검사 (Null 값 비율)
        null_ratios = {}
        for metric in metrics:
            if metric in data.columns:
                null_ratio = data[metric].isnull().mean()
                null_ratios[metric] = null_ratio
                
        avg_null_ratio = sum(null_ratios.values()) / max(len(null_ratios), 1)
        result['completeness'] = 1.0 - avg_null_ratio
        
        # 유효성 검사 (이상값 비율)
        outlier_ratios = {}
        for metric in metrics:
            if metric in data.columns:
                # 간단한 IQR 기반 이상값 탐지
                q1 = data[metric].quantile(0.25)
                q3 = data[metric].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                outlier_ratio = data[(data[metric] < lower_bound) | (data[metric] > upper_bound)].shape[0] / data.shape[0]
                outlier_ratios[metric] = outlier_ratio
                
        avg_outlier_ratio = sum(outlier_ratios.values()) / max(len(outlier_ratios), 1)
        result['validity'] = 1.0 - avg_outlier_ratio
        
        # 일관성 검사 (연도별 변동성)
        if 'Season' in data.columns:
            consistency_scores = {}
            for metric in metrics:
                if metric in data.columns:
                    # 시즌별 표준편차 계산
                    grouped = data.groupby('Season')[metric].std()
                    if not grouped.empty:
                        avg_std = grouped.mean()
                        overall_std = data[metric].std()
                        
                        # 표준편차 비율 (작을수록 일관성 높음)
                        if overall_std > 0:
                            consistency_scores[metric] = 1.0 - (avg_std / overall_std)
                        else:
                            consistency_scores[metric] = 1.0
            
            if consistency_scores:
                result['consistency'] = sum(consistency_scores.values()) / len(consistency_scores)
        
        # 전체 점수 계산
        result['overall_score'] = (result['completeness'] + result['validity'] + result['consistency']) / 3.0
        
        # 이슈 목록 생성
        if result['completeness'] < 0.9:
            result['issues'].append("Missing data issues")
            
        if result['validity'] < 0.9:
            result['issues'].append("Data validity issues (outliers)")
            
        if result['consistency'] < 0.7:
            result['issues'].append("Data consistency issues (high variability)")
            
        return result
