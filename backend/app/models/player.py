"""
선수 관련 데이터 모델

MLB 선수 정보 및 통계 데이터 모델
"""

from typing import Optional, List, Dict, Any, Union, Generic, TypeVar, Annotated
from datetime import datetime
from pydantic import BaseModel, Field, validator, Discriminator
from enum import Enum

# Generic 타입 변수
T = TypeVar('T')


class PlayerType(str, Enum):
    """선수 타입"""
    BATTER = "batter"
    PITCHER = "pitcher"


class PlayerBase(BaseModel):
    """선수 기본 정보"""
    player_id: str = Field(..., description="선수 고유 ID")
    player_name: str = Field(..., description="선수명")
    team: Optional[str] = Field(None, description="소속 팀")


class BatterStats(BaseModel):
    """타자 통계"""
    season: int = Field(..., description="시즌")
    games: Optional[float] = Field(None, description="경기 수")
    at_bats: Optional[float] = Field(None, description="타석")
    runs: Optional[float] = Field(None, description="득점")
    hits: Optional[float] = Field(None, description="안타")
    home_runs: Optional[float] = Field(None, description="홈런")
    rbi: Optional[float] = Field(None, description="타점")
    stolen_bases: Optional[float] = Field(None, description="도루")
    walks: Optional[float] = Field(None, description="볼넷")
    strikeouts: Optional[float] = Field(None, description="삼진")
    batting_average: Optional[float] = Field(None, description="타율")
    on_base_percentage: Optional[float] = Field(None, description="출루율")
    slugging_percentage: Optional[float] = Field(None, description="장타율")
    ops: Optional[float] = Field(None, description="OPS")

    @validator('batting_average', 'on_base_percentage', 'slugging_percentage', 'ops')
    def validate_percentages(cls, v):
        """퍼센티지 값 검증"""
        if v is not None and (v < 0 or v > 2.0):  # 현실적인 범위
            raise ValueError("Invalid percentage value")
        return v


class PitcherStats(BaseModel):
    """투수 통계"""
    season: int = Field(..., description="시즌")
    games: Optional[float] = Field(None, description="경기 수")
    wins: Optional[float] = Field(None, description="승수")
    losses: Optional[float] = Field(None, description="패수")
    era: Optional[float] = Field(None, description="평균자책점")
    innings_pitched: Optional[float] = Field(None, description="이닝")
    strikeouts: Optional[float] = Field(None, description="삼진")
    walks: Optional[float] = Field(None, description="볼넷")
    hits_allowed: Optional[float] = Field(None, description="피안타")
    home_runs_allowed: Optional[float] = Field(None, description="피홈런")
    saves: Optional[float] = Field(None, description="세이브")
    whip: Optional[float] = Field(None, description="WHIP")

    @validator('era', 'whip')
    def validate_era_whip(cls, v):
        """ERA, WHIP 검증"""
        if v is not None and v < 0:
            raise ValueError("ERA and WHIP cannot be negative")
        return v


class BatterRecord(PlayerBase):
    """타자 전체 기록"""
    season: int = Field(..., description="시즌")
    player_type: PlayerType = PlayerType.BATTER
    stats: BatterStats = Field(..., description="최신 시즌 통계")


class PitcherRecord(PlayerBase):
    """투수 전체 기록"""
    season: int = Field(..., description="시즌")
    player_type: PlayerType = PlayerType.PITCHER
    stats: PitcherStats = Field(..., description="최신 시즌 통계")


# Union type for player records with discriminator
PlayerRecord = Annotated[
    Union[BatterRecord, PitcherRecord], 
    Discriminator('player_type')
]


class PlayerSearchQuery(BaseModel):
    """선수 검색 쿼리"""
    query: Optional[str] = Field(None, description="검색어 (선수명)")
    player_type: Optional[PlayerType] = Field(None, description="선수 타입")
    team: Optional[str] = Field(None, description="팀")
    season: Optional[int] = Field(None, description="시즌")
    limit: int = Field(default=50, ge=1, le=100, description="결과 수 제한")
    offset: int = Field(default=0, ge=0, description="결과 오프셋")


class PlayerSearchResponse(BaseModel):
    """선수 검색 응답"""
    total: int = Field(..., description="전체 결과 수")
    limit: int = Field(..., description="요청 제한 수")
    offset: int = Field(..., description="오프셋")
    results: List[PlayerRecord] = Field(..., description="검색 결과")


class PlayerStatsQuery(BaseModel):
    """선수 통계 조회 쿼리"""
    player_id: str = Field(..., description="선수 ID")
    season_start: Optional[int] = Field(None, description="시작 시즌")
    season_end: Optional[int] = Field(None, description="종료 시즌")
    include_career: bool = Field(default=True, description="통산 기록 포함 여부")


class StatsSummary(BaseModel):
    """통계 요약"""
    total_players: int = Field(..., description="총 선수 수")
    total_seasons: int = Field(..., description="총 시즌 수")
    latest_season: int = Field(..., description="최신 시즌")
    earliest_season: int = Field(..., description="최초 시즌")
    batter_count: int = Field(..., description="타자 수")
    pitcher_count: int = Field(..., description="투수 수")


class APIResponse(BaseModel, Generic[T]):
    """공통 API 응답"""
    success: bool = Field(default=True, description="성공 여부")
    message: Optional[str] = Field(None, description="메시지")
    data: Optional[T] = Field(None, description="응답 데이터")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }