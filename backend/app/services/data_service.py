"""
데이터 서비스

MLB 선수 데이터 로드, 처리 및 조회 서비스
"""

import pandas as pd
from typing import List, Optional, Dict, Any, Union
from pathlib import Path
import logging
from functools import lru_cache

from app.core.config import settings
from app.models.player import (
    PlayerBase, BatterRecord, PitcherRecord, BatterStats, PitcherStats,
    PlayerType, PlayerSearchQuery, PlayerSearchResponse, StatsSummary
)

logger = logging.getLogger(__name__)


class DataService:
    """MLB 데이터 서비스"""
    
    def __init__(self):
        self._batter_df: Optional[pd.DataFrame] = None
        self._pitcher_df: Optional[pd.DataFrame] = None
        self._loaded = False
    
    def _load_data(self) -> None:
        """데이터 로드 (한 번만 실행)"""
        if self._loaded:
            return
        
        try:
            logger.info("MLB 데이터 로드 시작...")
            
            # 타자 데이터 로드
            if settings.batter_stats_file.exists():
                self._batter_df = pd.read_csv(settings.batter_stats_file)
                logger.info(f"타자 데이터 로드 완료: {len(self._batter_df)} 레코드")
            else:
                logger.warning(f"타자 데이터 파일 없음: {settings.batter_stats_file}")
                self._batter_df = pd.DataFrame()
            
            # 투수 데이터 로드
            if settings.pitcher_stats_file.exists():
                self._pitcher_df = pd.read_csv(settings.pitcher_stats_file)
                logger.info(f"투수 데이터 로드 완료: {len(self._pitcher_df)} 레코드")
            else:
                logger.warning(f"투수 데이터 파일 없음: {settings.pitcher_stats_file}")
                self._pitcher_df = pd.DataFrame()
            
            self._loaded = True
            logger.info("MLB 데이터 로드 완료")
            
        except Exception as e:
            logger.error(f"데이터 로드 실패: {e}")
            self._batter_df = pd.DataFrame()
            self._pitcher_df = pd.DataFrame()
            self._loaded = True
    
    @property
    def batter_df(self) -> pd.DataFrame:
        """타자 데이터프레임"""
        self._load_data()
        return self._batter_df.copy() if self._batter_df is not None else pd.DataFrame()
    
    @property
    def pitcher_df(self) -> pd.DataFrame:
        """투수 데이터프레임"""
        self._load_data()
        return self._pitcher_df.copy() if self._pitcher_df is not None else pd.DataFrame()
    
    def get_stats_summary(self) -> StatsSummary:
        """통계 요약 정보"""
        batter_df = self.batter_df
        pitcher_df = self.pitcher_df
        
        # 타자 통계
        batter_seasons = set(batter_df['Season'].unique()) if not batter_df.empty else set()
        batter_players = set(batter_df['PlayerID'].unique()) if not batter_df.empty else set()
        
        # 투수 통계
        pitcher_seasons = set(pitcher_df['Season'].unique()) if not pitcher_df.empty else set()
        pitcher_players = set(pitcher_df['PlayerID'].unique()) if not pitcher_df.empty else set()
        
        # 전체 통계
        all_seasons = batter_seasons.union(pitcher_seasons)
        
        return StatsSummary(
            total_players=len(batter_players.union(pitcher_players)),
            total_seasons=len(all_seasons),
            latest_season=max(all_seasons) if all_seasons else 0,
            earliest_season=min(all_seasons) if all_seasons else 0,
            batter_count=len(batter_players),
            pitcher_count=len(pitcher_players)
        )
    
    def search_players(self, query: PlayerSearchQuery) -> PlayerSearchResponse:
        """선수 검색"""
        try:
            results = []
            
            if query.player_type == PlayerType.BATTER or query.player_type is None:
                batter_results = self._search_in_dataframe(
                    self.batter_df, query, PlayerType.BATTER
                )
                results.extend(batter_results)
            
            if query.player_type == PlayerType.PITCHER or query.player_type is None:
                pitcher_results = self._search_in_dataframe(
                    self.pitcher_df, query, PlayerType.PITCHER
                )
                results.extend(pitcher_results)
            
            # 중복 제거 (같은 선수가 타자와 투수 둘 다인 경우)
            seen = set()
            unique_results = []
            for player in results:
                if player.player_id not in seen:
                    unique_results.append(player)
                    seen.add(player.player_id)
            
            # 정렬 및 페이지네이션
            unique_results.sort(key=lambda x: x.player_name)
            total = len(unique_results)
            paginated_results = unique_results[query.offset:query.offset + query.limit]
            
            return PlayerSearchResponse(
                total=total,
                limit=query.limit,
                offset=query.offset,
                results=paginated_results
            )
            
        except Exception as e:
            logger.error(f"선수 검색 중 오류: {e}")
            return PlayerSearchResponse(
                total=0,
                limit=query.limit,
                offset=query.offset,
                results=[]
            )
    
    def _search_in_dataframe(
        self, 
        df: pd.DataFrame, 
        query: PlayerSearchQuery, 
        player_type: PlayerType
    ) -> List[Union[BatterRecord, PitcherRecord]]:
        """데이터프레임에서 선수 검색"""
        if df.empty:
            return []
        
        # 기본 필터링
        filtered_df = df.copy()
        
        # 이름 검색
        if query.query:
            filtered_df = filtered_df[
                filtered_df['PlayerName'].str.contains(
                    query.query, case=False, na=False
                )
            ]
        
        # 팀 필터
        if query.team:
            filtered_df = filtered_df[
                filtered_df['Team'].str.contains(
                    query.team, case=False, na=False
                )
            ]
        
        # 시즌 필터
        if query.season:
            filtered_df = filtered_df[filtered_df['Season'] == query.season]
        
        # 선수별로 그룹화하여 고유 선수 목록 생성
        if filtered_df.empty:
            return []
        
        player_groups = filtered_df.groupby(['PlayerID', 'PlayerName'])
        results = []
        
        for (player_id, player_name), group in player_groups:
            # 가장 최근 시즌 데이터 사용
            latest_record = group.loc[group['Season'].idxmax()]
            
            if player_type == PlayerType.BATTER:
                # 타자 통계 생성
                stats = BatterStats(
                    season=int(latest_record['Season']),
                    games=float(latest_record['GamesPlayed']) if pd.notna(latest_record['GamesPlayed']) else None,
                    at_bats=float(latest_record['AtBats']) if pd.notna(latest_record['AtBats']) else None,
                    runs=float(latest_record['Runs']) if pd.notna(latest_record['Runs']) else None,
                    hits=float(latest_record['Hits']) if pd.notna(latest_record['Hits']) else None,
                    home_runs=float(latest_record['HomeRuns']) if pd.notna(latest_record['HomeRuns']) else None,
                    rbi=float(latest_record['RBIs']) if pd.notna(latest_record['RBIs']) else None,
                    stolen_bases=float(latest_record['StolenBases']) if pd.notna(latest_record['StolenBases']) else None,
                    walks=float(latest_record['Walks']) if pd.notna(latest_record['Walks']) else None,
                    strikeouts=float(latest_record['StrikeOuts']) if pd.notna(latest_record['StrikeOuts']) else None,
                    batting_average=float(latest_record['BattingAverage']) if pd.notna(latest_record['BattingAverage']) else None,
                    on_base_percentage=float(latest_record['OnBasePercentage']) if pd.notna(latest_record['OnBasePercentage']) else None,
                    slugging_percentage=float(latest_record['SluggingPercentage']) if pd.notna(latest_record['SluggingPercentage']) else None,
                    ops=float(latest_record['OPS']) if pd.notna(latest_record['OPS']) else None
                )
                
                results.append(BatterRecord(
                    player_id=str(player_id),
                    player_name=player_name,
                    team=latest_record['Team'] if pd.notna(latest_record['Team']) else "Unknown",
                    season=int(latest_record['Season']),
                    player_type=PlayerType.BATTER,
                    stats=stats
                ))
            else:
                # 투수 통계 생성
                stats = PitcherStats(
                    season=int(latest_record['Season']),
                    games=float(latest_record['GamesPlayed']) if pd.notna(latest_record['GamesPlayed']) else None,
                    wins=float(latest_record['Wins']) if pd.notna(latest_record['Wins']) else None,
                    losses=float(latest_record['Losses']) if pd.notna(latest_record['Losses']) else None,
                    era=float(latest_record['EarnedRunAverage']) if pd.notna(latest_record['EarnedRunAverage']) else None,
                    innings_pitched=float(latest_record['InningsPitched']) if pd.notna(latest_record['InningsPitched']) else None,
                    strikeouts=float(latest_record['StrikeOuts']) if pd.notna(latest_record['StrikeOuts']) else None,
                    walks=float(latest_record['Walks']) if pd.notna(latest_record['Walks']) else None,
                    hits_allowed=float(latest_record['HitsAllowed']) if pd.notna(latest_record['HitsAllowed']) else None,
                    home_runs_allowed=float(latest_record['HomeRunsAllowed']) if pd.notna(latest_record['HomeRunsAllowed']) else None,
                    saves=float(latest_record['Saves']) if pd.notna(latest_record['Saves']) else None,
                    whip=float(latest_record['Whip']) if pd.notna(latest_record['Whip']) else None
                )
                
                results.append(PitcherRecord(
                    player_id=str(player_id),
                    player_name=player_name,
                    team=latest_record['Team'] if pd.notna(latest_record['Team']) else "Unknown",
                    season=int(latest_record['Season']),
                    player_type=PlayerType.PITCHER,
                    stats=stats
                ))
        
        return results
    
    def get_player_stats(
        self, 
        player_id: str, 
        player_type: PlayerType,
        season_start: Optional[int] = None,
        season_end: Optional[int] = None
    ) -> Union[BatterRecord, PitcherRecord, None]:
        """선수 상세 통계 조회"""
        try:
            if player_type == PlayerType.BATTER:
                return self._get_batter_stats(player_id, season_start, season_end)
            else:
                return self._get_pitcher_stats(player_id, season_start, season_end)
        except Exception as e:
            logger.error(f"선수 통계 조회 중 오류: {e}")
            return None
    
    def _get_batter_stats(
        self, 
        player_id: str, 
        season_start: Optional[int], 
        season_end: Optional[int]
    ) -> Optional[BatterRecord]:
        """타자 통계 조회"""
        df = self.batter_df
        if df.empty:
            return None
        
        player_data = df[df['PlayerID'] == player_id].copy()
        if player_data.empty:
            return None
        
        # 시즌 필터링
        if season_start:
            player_data = player_data[player_data['Season'] >= season_start]
        if season_end:
            player_data = player_data[player_data['Season'] <= season_end]
        
        if player_data.empty:
            return None
        
        # 기본 정보
        first_record = player_data.iloc[0]
        player_name = first_record['PlayerName']
        latest_team = player_data.loc[player_data['Season'].idxmax(), 'Team']
        
        # 시즌별 통계
        stats_list = []
        for _, row in player_data.iterrows():
            stats = BatterStats(
                season=int(row['Season']),
                games_played=self._safe_float(row.get('GamesPlayed')),
                at_bats=self._safe_float(row.get('AtBats')),
                runs=self._safe_float(row.get('Runs')),
                hits=self._safe_float(row.get('Hits')),
                home_runs=self._safe_float(row.get('HomeRuns')),
                rbis=self._safe_float(row.get('RBIs')),
                stolen_bases=self._safe_float(row.get('StolenBases')),
                walks=self._safe_float(row.get('Walks')),
                strike_outs=self._safe_float(row.get('StrikeOuts')),
                batting_average=self._safe_float(row.get('BattingAverage')),
                on_base_percentage=self._safe_float(row.get('OnBasePercentage')),
                slugging_percentage=self._safe_float(row.get('SluggingPercentage')),
                ops=self._safe_float(row.get('OPS'))
            )
            stats_list.append(stats)
        
        # 통산 기록 계산 (필요시)
        career_stats = self._calculate_career_batter_stats(player_data)
        
        return BatterRecord(
            player_id=player_id,
            player_name=player_name,
            team=latest_team if pd.notna(latest_team) else None,
            stats=stats_list,
            career_stats=career_stats
        )
    
    def _get_pitcher_stats(
        self, 
        player_id: str, 
        season_start: Optional[int], 
        season_end: Optional[int]
    ) -> Optional[PitcherRecord]:
        """투수 통계 조회"""
        df = self.pitcher_df
        if df.empty:
            return None
        
        player_data = df[df['PlayerID'] == player_id].copy()
        if player_data.empty:
            return None
        
        # 시즌 필터링
        if season_start:
            player_data = player_data[player_data['Season'] >= season_start]
        if season_end:
            player_data = player_data[player_data['Season'] <= season_end]
        
        if player_data.empty:
            return None
        
        # 기본 정보
        first_record = player_data.iloc[0]
        player_name = first_record['PlayerName']
        latest_team = player_data.loc[player_data['Season'].idxmax(), 'Team']
        
        # 시즌별 통계
        stats_list = []
        for _, row in player_data.iterrows():
            stats = PitcherStats(
                season=int(row['Season']),
                games_played=self._safe_float(row.get('GamesPlayed')),
                wins=self._safe_float(row.get('Wins')),
                losses=self._safe_float(row.get('Losses')),
                earned_run_average=self._safe_float(row.get('EarnedRunAverage')),
                innings_pitched=self._safe_float(row.get('InningsPitched')),
                strike_outs=self._safe_float(row.get('StrikeOuts')),
                walks=self._safe_float(row.get('Walks')),
                hits_allowed=self._safe_float(row.get('HitsAllowed')),
                home_runs_allowed=self._safe_float(row.get('HomeRunsAllowed')),
                saves=self._safe_float(row.get('Saves')),
                whip=self._safe_float(row.get('Whip')),
                qualifying_innings=self._safe_bool(row.get('QualifyingInnings'))
            )
            stats_list.append(stats)
        
        # 통산 기록 계산
        career_stats = self._calculate_career_pitcher_stats(player_data)
        
        return PitcherRecord(
            player_id=player_id,
            player_name=player_name,
            team=latest_team if pd.notna(latest_team) else None,
            stats=stats_list,
            career_stats=career_stats
        )
    
    def _safe_float(self, value: Any) -> Optional[float]:
        """안전한 float 변환"""
        if pd.isna(value):
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _safe_bool(self, value: Any) -> Optional[bool]:
        """안전한 bool 변환"""
        if pd.isna(value):
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes')
        try:
            return bool(value)
        except (ValueError, TypeError):
            return None
    
    def _calculate_career_batter_stats(self, df: pd.DataFrame) -> Optional[BatterStats]:
        """타자 통산 기록 계산"""
        if df.empty:
            return None
        
        # 합계 계산
        total_games = df['GamesPlayed'].sum() if 'GamesPlayed' in df.columns else None
        total_at_bats = df['AtBats'].sum() if 'AtBats' in df.columns else None
        total_runs = df['Runs'].sum() if 'Runs' in df.columns else None
        total_hits = df['Hits'].sum() if 'Hits' in df.columns else None
        total_home_runs = df['HomeRuns'].sum() if 'HomeRuns' in df.columns else None
        total_rbis = df['RBIs'].sum() if 'RBIs' in df.columns else None
        total_stolen_bases = df['StolenBases'].sum() if 'StolenBases' in df.columns else None
        total_walks = df['Walks'].sum() if 'Walks' in df.columns else None
        total_strike_outs = df['StrikeOuts'].sum() if 'StrikeOuts' in df.columns else None
        
        # 평균 계산
        avg_batting_average = df['BattingAverage'].mean() if 'BattingAverage' in df.columns else None
        avg_on_base_percentage = df['OnBasePercentage'].mean() if 'OnBasePercentage' in df.columns else None
        avg_slugging_percentage = df['SluggingPercentage'].mean() if 'SluggingPercentage' in df.columns else None
        avg_ops = df['OPS'].mean() if 'OPS' in df.columns else None
        
        return BatterStats(
            season=0,  # 통산은 시즌 0으로 표시
            games_played=self._safe_float(total_games),
            at_bats=self._safe_float(total_at_bats),
            runs=self._safe_float(total_runs),
            hits=self._safe_float(total_hits),
            home_runs=self._safe_float(total_home_runs),
            rbis=self._safe_float(total_rbis),
            stolen_bases=self._safe_float(total_stolen_bases),
            walks=self._safe_float(total_walks),
            strike_outs=self._safe_float(total_strike_outs),
            batting_average=self._safe_float(avg_batting_average),
            on_base_percentage=self._safe_float(avg_on_base_percentage),
            slugging_percentage=self._safe_float(avg_slugging_percentage),
            ops=self._safe_float(avg_ops)
        )
    
    def _calculate_career_pitcher_stats(self, df: pd.DataFrame) -> Optional[PitcherStats]:
        """투수 통산 기록 계산"""
        if df.empty:
            return None
        
        # 합계 계산
        total_games = df['GamesPlayed'].sum() if 'GamesPlayed' in df.columns else None
        total_wins = df['Wins'].sum() if 'Wins' in df.columns else None
        total_losses = df['Losses'].sum() if 'Losses' in df.columns else None
        total_innings = df['InningsPitched'].sum() if 'InningsPitched' in df.columns else None
        total_strike_outs = df['StrikeOuts'].sum() if 'StrikeOuts' in df.columns else None
        total_walks = df['Walks'].sum() if 'Walks' in df.columns else None
        total_hits_allowed = df['HitsAllowed'].sum() if 'HitsAllowed' in df.columns else None
        total_hrs_allowed = df['HomeRunsAllowed'].sum() if 'HomeRunsAllowed' in df.columns else None
        total_saves = df['Saves'].sum() if 'Saves' in df.columns else None
        
        # 평균 계산
        avg_era = df['EarnedRunAverage'].mean() if 'EarnedRunAverage' in df.columns else None
        avg_whip = df['Whip'].mean() if 'Whip' in df.columns else None
        
        return PitcherStats(
            season=0,  # 통산은 시즌 0으로 표시
            games_played=self._safe_float(total_games),
            wins=self._safe_float(total_wins),
            losses=self._safe_float(total_losses),
            earned_run_average=self._safe_float(avg_era),
            innings_pitched=self._safe_float(total_innings),
            strike_outs=self._safe_float(total_strike_outs),
            walks=self._safe_float(total_walks),
            hits_allowed=self._safe_float(total_hits_allowed),
            home_runs_allowed=self._safe_float(total_hrs_allowed),
            saves=self._safe_float(total_saves),
            whip=self._safe_float(avg_whip),
            qualifying_innings=None  # 통산에서는 의미 없음
        )


# 전역 데이터 서비스 인스턴스
data_service = DataService()


def get_data_service() -> DataService:
    """데이터 서비스 의존성 주입"""
    return data_service