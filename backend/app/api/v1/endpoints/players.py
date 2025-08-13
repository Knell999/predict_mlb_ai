"""
선수 관련 API 엔드포인트

선수 검색, 조회, 통계 관련 API
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from app.models.player import (
    PlayerSearchQuery, PlayerSearchResponse, PlayerType, 
    BatterRecord, PitcherRecord, PlayerStatsQuery, StatsSummary,
    APIResponse
)
from app.services.data_service import DataService, get_data_service

router = APIRouter(prefix="/players", tags=["players"])


@router.get("/summary", response_model=StatsSummary)
async def get_stats_summary(
    data_service: DataService = Depends(get_data_service)
) -> StatsSummary:
    """통계 요약 정보 조회"""
    try:
        return data_service.get_stats_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 요약 조회 실패: {str(e)}")


@router.get("/search", response_model=PlayerSearchResponse)
async def search_players(
    query: Optional[str] = Query(None, description="검색어 (선수명)"),
    player_type: Optional[PlayerType] = Query(None, description="선수 타입"),
    team: Optional[str] = Query(None, description="팀"),
    season: Optional[int] = Query(None, description="시즌"),
    limit: int = Query(50, ge=1, le=100, description="결과 수 제한"),
    offset: int = Query(0, ge=0, description="결과 오프셋"),
    data_service: DataService = Depends(get_data_service)
) -> PlayerSearchResponse:
    """선수 검색"""
    try:
        search_query = PlayerSearchQuery(
            query=query,
            player_type=player_type,
            team=team,
            season=season,
            limit=limit,
            offset=offset
        )
        return data_service.search_players(search_query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"선수 검색 실패: {str(e)}")


@router.get("/{player_id}/stats")
async def get_player_stats(
    player_id: str,
    player_type: PlayerType = Query(..., description="선수 타입"),
    season_start: Optional[int] = Query(None, description="시작 시즌"),
    season_end: Optional[int] = Query(None, description="종료 시즌"),
    data_service: DataService = Depends(get_data_service)
):
    """선수 상세 통계 조회"""
    try:
        stats = data_service.get_player_stats(
            player_id=player_id,
            player_type=player_type,
            season_start=season_start,
            season_end=season_end
        )
        
        if stats is None:
            raise HTTPException(
                status_code=404, 
                detail=f"선수 ID {player_id}의 {player_type.value} 통계를 찾을 수 없습니다"
            )
        
        return APIResponse(
            success=True,
            message="선수 통계 조회 성공",
            data=stats
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"선수 통계 조회 실패: {str(e)}")


@router.get("/batters", response_model=List[str])
async def get_batter_list(
    season: Optional[int] = Query(None, description="시즌"),
    team: Optional[str] = Query(None, description="팀"),
    limit: int = Query(100, ge=1, le=500, description="결과 수 제한"),
    data_service: DataService = Depends(get_data_service)
) -> List[str]:
    """타자 목록 조회 (선수명 리스트)"""
    try:
        search_query = PlayerSearchQuery(
            player_type=PlayerType.BATTER,
            season=season,
            team=team,
            limit=limit,
            offset=0
        )
        
        result = data_service.search_players(search_query)
        return [player.player_name for player in result.results]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"타자 목록 조회 실패: {str(e)}")


@router.get("/pitchers", response_model=List[str])
async def get_pitcher_list(
    season: Optional[int] = Query(None, description="시즌"),
    team: Optional[str] = Query(None, description="팀"),
    limit: int = Query(100, ge=1, le=500, description="결과 수 제한"),
    data_service: DataService = Depends(get_data_service)
) -> List[str]:
    """투수 목록 조회 (선수명 리스트)"""
    try:
        search_query = PlayerSearchQuery(
            player_type=PlayerType.PITCHER,
            season=season,
            team=team,
            limit=limit,
            offset=0
        )
        
        result = data_service.search_players(search_query)
        return [player.player_name for player in result.results]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"투수 목록 조회 실패: {str(e)}")


@router.get("/teams", response_model=List[str])
async def get_team_list(
    player_type: Optional[PlayerType] = Query(None, description="선수 타입"),
    season: Optional[int] = Query(None, description="시즌"),
    data_service: DataService = Depends(get_data_service)
) -> List[str]:
    """팀 목록 조회"""
    try:
        # 데이터프레임에서 팀 목록 추출
        teams = set()
        
        if player_type == PlayerType.BATTER or player_type is None:
            batter_df = data_service.batter_df
            if not batter_df.empty:
                if season:
                    batter_df = batter_df[batter_df['Season'] == season]
                teams.update(batter_df['Team'].dropna().unique())
        
        if player_type == PlayerType.PITCHER or player_type is None:
            pitcher_df = data_service.pitcher_df
            if not pitcher_df.empty:
                if season:
                    pitcher_df = pitcher_df[pitcher_df['Season'] == season]
                teams.update(pitcher_df['Team'].dropna().unique())
        
        return sorted(list(teams))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"팀 목록 조회 실패: {str(e)}")


@router.get("/seasons", response_model=List[int])
async def get_season_list(
    player_type: Optional[PlayerType] = Query(None, description="선수 타입"),
    data_service: DataService = Depends(get_data_service)
) -> List[int]:
    """시즌 목록 조회"""
    try:
        seasons = set()
        
        if player_type == PlayerType.BATTER or player_type is None:
            batter_df = data_service.batter_df
            if not batter_df.empty:
                seasons.update(batter_df['Season'].unique())
        
        if player_type == PlayerType.PITCHER or player_type is None:
            pitcher_df = data_service.pitcher_df
            if not pitcher_df.empty:
                seasons.update(pitcher_df['Season'].unique())
        
        return sorted(list(seasons), reverse=True)  # 최신 시즌부터
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"시즌 목록 조회 실패: {str(e)}")