"""
AI 분석 관련 데이터 모델

AI 기반 선수 분석 및 예측 모델
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

from .player import PlayerType


class AnalysisLanguage(str, Enum):
    """분석 언어"""
    KOREAN = "한국어"
    ENGLISH = "영어" 
    JAPANESE = "일본어"


class AnalysisRequest(BaseModel):
    """AI 분석 요청"""
    player_id: str = Field(..., description="선수 ID")
    player_type: PlayerType = Field(..., description="선수 타입")
    language: AnalysisLanguage = Field(default=AnalysisLanguage.KOREAN, description="분석 언어")
    season_start: Optional[int] = Field(None, description="분석 시작 시즌")
    season_end: Optional[int] = Field(None, description="분석 종료 시즌")
    include_league_comparison: bool = Field(default=True, description="리그 평균 비교 포함")


class AnalysisResponse(BaseModel):
    """AI 분석 응답"""
    player_id: str = Field(..., description="선수 ID")
    player_name: str = Field(..., description="선수명")
    player_type: PlayerType = Field(..., description="선수 타입")
    language: AnalysisLanguage = Field(..., description="분석 언어")
    analysis_content: str = Field(..., description="AI 분석 내용 (마크다운)")
    generated_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    seasons_analyzed: List[int] = Field(..., description="분석된 시즌 목록")


class ComparisonAnalysisRequest(BaseModel):
    """선수 비교 분석 요청"""
    player1_id: str = Field(..., description="첫 번째 선수 ID")
    player2_id: str = Field(..., description="두 번째 선수 ID")
    player_type: PlayerType = Field(..., description="선수 타입")
    language: AnalysisLanguage = Field(default=AnalysisLanguage.KOREAN, description="분석 언어")
    season_start: Optional[int] = Field(None, description="비교 시작 시즌")
    season_end: Optional[int] = Field(None, description="비교 종료 시즌")


class ComparisonAnalysisResponse(BaseModel):
    """선수 비교 분석 응답"""
    player1_id: str = Field(..., description="첫 번째 선수 ID")
    player1_name: str = Field(..., description="첫 번째 선수명")
    player2_id: str = Field(..., description="두 번째 선수 ID")
    player2_name: str = Field(..., description="두 번째 선수명")
    player_type: PlayerType = Field(..., description="선수 타입")
    language: AnalysisLanguage = Field(..., description="분석 언어")
    comparison_content: str = Field(..., description="비교 분석 내용 (마크다운)")
    generated_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    seasons_compared: List[int] = Field(..., description="비교된 시즌 목록")


class PredictionRequest(BaseModel):
    """예측 분석 요청"""
    player_id: str = Field(..., description="선수 ID")
    player_type: PlayerType = Field(..., description="선수 타입")
    metric: str = Field(..., description="예측할 지표")
    forecast_periods: int = Field(default=1, ge=1, le=5, description="예측 기간 (시즌)")
    include_intervals: bool = Field(default=True, description="신뢰구간 포함")


class PredictionPoint(BaseModel):
    """예측 데이터 포인트"""
    season: int = Field(..., description="시즌")
    predicted_value: float = Field(..., description="예측값")
    lower_bound: Optional[float] = Field(None, description="하한값")
    upper_bound: Optional[float] = Field(None, description="상한값")


class PredictionResponse(BaseModel):
    """예측 분석 응답"""
    player_id: str = Field(..., description="선수 ID")
    player_name: str = Field(..., description="선수명")
    player_type: PlayerType = Field(..., description="선수 타입")
    metric: str = Field(..., description="예측된 지표")
    historical_data: List[Dict[str, Any]] = Field(..., description="과거 데이터")
    predictions: List[PredictionPoint] = Field(..., description="예측 데이터")
    model_performance: Dict[str, float] = Field(..., description="모델 성능 지표")
    generated_at: datetime = Field(default_factory=datetime.now, description="생성 시간")


class TrendAnalysisRequest(BaseModel):
    """트렌드 분석 요청"""
    metric: str = Field(..., description="분석할 지표")
    player_type: PlayerType = Field(..., description="선수 타입")
    season_start: Optional[int] = Field(None, description="시작 시즌")
    season_end: Optional[int] = Field(None, description="종료 시즌")
    team: Optional[str] = Field(None, description="특정 팀 (전체 리그는 None)")


class TrendDataPoint(BaseModel):
    """트렌드 데이터 포인트"""
    season: int = Field(..., description="시즌")
    value: float = Field(..., description="값")
    player_count: int = Field(..., description="해당 시즌 선수 수")


class TrendAnalysisResponse(BaseModel):
    """트렌드 분석 응답"""
    metric: str = Field(..., description="분석된 지표")
    player_type: PlayerType = Field(..., description="선수 타입")
    team: Optional[str] = Field(None, description="팀 (전체 리그는 None)")
    trend_data: List[TrendDataPoint] = Field(..., description="트렌드 데이터")
    trend_direction: str = Field(..., description="트렌드 방향 (증가/감소/안정)")
    correlation_coefficient: Optional[float] = Field(None, description="상관계수")
    generated_at: datetime = Field(default_factory=datetime.now, description="생성 시간")