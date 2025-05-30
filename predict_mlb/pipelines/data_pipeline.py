"""
데이터 파이프라인 모듈: 데이터 처리 파이프라인을 정의합니다.
"""
from typing import Dict, List, Any, Optional, Callable
import pandas as pd

class DataValidator:
    """데이터 검증 클래스"""
    
    @staticmethod
    def validate(data: pd.DataFrame, conditions: List[Callable[[pd.DataFrame], bool]]) -> bool:
        """
        데이터가 모든 조건을 만족하는지 검증합니다.
        
        Args:
            data: 검증할 데이터프레임
            conditions: 검증 조건 목록 (각 조건은 DataFrame을 인자로 받고 bool을 반환하는 함수)
            
        Returns:
            bool: 모든 조건을 만족하면 True, 아니면 False
        """
        for condition in conditions:
            if not condition(data):
                return False
        return True


class DataProcessor:
    """데이터 처리 클래스"""
    
    def __init__(self, processors: List[Callable[[pd.DataFrame], pd.DataFrame]] = None):
        """
        DataProcessor 클래스 초기화
        
        Args:
            processors: 데이터 처리 함수 목록
        """
        self.processors = processors or []
        
    def add_processor(self, processor: Callable[[pd.DataFrame], pd.DataFrame]) -> None:
        """
        데이터 처리기를 추가합니다.
        
        Args:
            processor: 데이터 처리 함수
        """
        self.processors.append(processor)
        
    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        데이터를 처리합니다.
        
        Args:
            data: 처리할 데이터프레임
            
        Returns:
            pd.DataFrame: 처리된 데이터프레임
        """
        result = data.copy()
        for processor in self.processors:
            result = processor(result)
        return result


class DataPipeline:
    """데이터 처리 파이프라인"""
    
    def __init__(self):
        """DataPipeline 클래스 초기화"""
        self.validators = []
        self.processors = []
        
    def add_validator(self, validator: Callable[[pd.DataFrame], bool]) -> None:
        """
        데이터 검증기를 추가합니다.
        
        Args:
            validator: 데이터 검증 함수
        """
        self.validators.append(validator)
        
    def add_processor(self, processor: Callable[[pd.DataFrame], pd.DataFrame]) -> None:
        """
        데이터 처리기를 추가합니다.
        
        Args:
            processor: 데이터 처리 함수
        """
        self.processors.append(processor)
        
    def execute(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        파이프라인을 실행합니다.
        
        Args:
            data: 처리할 데이터프레임
            
        Returns:
            pd.DataFrame: 처리된 데이터프레임
            
        Raises:
            ValueError: 데이터 검증 실패 시
        """
        # 검증 단계
        for validator in self.validators:
            if not validator(data):
                raise ValueError("Data validation failed")
        
        # 처리 단계
        result = data.copy()
        for processor in self.processors:
            result = processor(result)
            
        return result


# 일반적인 검증 함수들
def validate_required_columns(data: pd.DataFrame, required_columns: List[str]) -> bool:
    """
    필수 컬럼이 존재하는지 검증합니다.
    
    Args:
        data: 검증할 데이터프레임
        required_columns: 필수 컬럼 목록
        
    Returns:
        bool: 모든 필수 컬럼이 존재하면 True, 아니면 False
    """
    return all(col in data.columns for col in required_columns)

def validate_no_null_values(data: pd.DataFrame, columns: List[str]) -> bool:
    """
    지정된 컬럼에 null 값이 없는지 검증합니다.
    
    Args:
        data: 검증할 데이터프레임
        columns: 검증할 컬럼 목록
        
    Returns:
        bool: null 값이 없으면 True, 있으면 False
    """
    for col in columns:
        if col in data.columns and data[col].isnull().any():
            return False
    return True

def validate_data_range(data: pd.DataFrame, column: str, min_value: float, max_value: float) -> bool:
    """
    지정된 컬럼의 값이 범위 내에 있는지 검증합니다.
    
    Args:
        data: 검증할 데이터프레임
        column: 검증할 컬럼
        min_value: 최소값
        max_value: 최대값
        
    Returns:
        bool: 모든 값이 범위 내에 있으면 True, 아니면 False
    """
    if column not in data.columns:
        return False
    return data[column].between(min_value, max_value).all()

# 일반적인 처리 함수들
def fill_na_values(data: pd.DataFrame, columns: List[str], fill_value: Any = 0) -> pd.DataFrame:
    """
    지정된 컬럼의 null 값을 채웁니다.
    
    Args:
        data: 처리할 데이터프레임
        columns: 처리할 컬럼 목록
        fill_value: 채울 값
        
    Returns:
        pd.DataFrame: 처리된 데이터프레임
    """
    result = data.copy()
    for col in columns:
        if col in result.columns:
            result[col] = result[col].fillna(fill_value)
    return result

def add_derived_column(data: pd.DataFrame, new_column: str, 
                       formula: Callable[[pd.DataFrame], pd.Series]) -> pd.DataFrame:
    """
    새로운 파생 컬럼을 추가합니다.
    
    Args:
        data: 처리할 데이터프레임
        new_column: 새 컬럼 이름
        formula: 컬럼 값을 계산하는 함수
        
    Returns:
        pd.DataFrame: 처리된 데이터프레임
    """
    result = data.copy()
    result[new_column] = formula(result)
    return result

def normalize_column(data: pd.DataFrame, column: str, new_column: Optional[str] = None) -> pd.DataFrame:
    """
    지정된 컬럼을 정규화합니다.
    
    Args:
        data: 처리할 데이터프레임
        column: 정규화할 컬럼
        new_column: 정규화된 값을 저장할 새 컬럼 (None이면 기존 컬럼 덮어쓰기)
        
    Returns:
        pd.DataFrame: 처리된 데이터프레임
    """
    result = data.copy()
    if column in result.columns:
        min_val = result[column].min()
        max_val = result[column].max()
        
        if max_val > min_val:  # 분모가 0이 되지 않도록
            normalized = (result[column] - min_val) / (max_val - min_val)
            
            if new_column:
                result[new_column] = normalized
            else:
                result[column] = normalized
                
    return result
