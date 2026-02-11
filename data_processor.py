"""
MLB 데이터 수집 및 처리를 위한 모듈
공식 MLB Stats API를 활용하여 최신 데이터를 수집하고 기존 데이터와 통합
"""

import pandas as pd
import requests
import json
import time
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional
import os
from config import DATA_DIR, BATTER_STATS_FILE, PITCHER_STATS_FILE, MLB_API_BASE_URL, API_RATE_LIMIT_DELAY

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _safe_float(value, default=0.0):
    """안전한 float 변환. 실패 시 기본값 반환."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def _safe_int(value, default=0):
    """안전한 int 변환. 실패 시 기본값 반환."""
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default

class MLBDataProcessor:
    """MLB 데이터 수집 및 처리 클래스"""

    def __init__(self):
        self.base_url = MLB_API_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MLB-Stats-App/1.0'
        })
    
    def get_seasons_list(self, start_year: int = 2024, end_year: int = None) -> List[int]:
        """수집할 시즌 목록 반환"""
        if end_year is None:
            end_year = datetime.now().year
        return list(range(start_year, end_year + 1))
    
    def get_teams(self, season: int) -> List[Dict]:
        """특정 시즌의 팀 목록 조회"""
        try:
            url = f"{self.base_url}/teams"
            params = {
                'season': season,
                'sportId': 1  # MLB
            }
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('teams', [])
        except Exception as e:
            logger.error(f"팀 목록 조회 실패 (시즌: {season}): {e}")
            return []
    
    def get_roster(self, team_id: int, season: int) -> List[Dict]:
        """특정 팀의 로스터 조회"""
        try:
            url = f"{self.base_url}/teams/{team_id}/roster"
            params = {
                'season': season,
                'rosterType': 'active'
            }
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('roster', [])
        except Exception as e:
            logger.error(f"로스터 조회 실패 (팀: {team_id}, 시즌: {season}): {e}")
            return []
    
    def get_player_stats(self, player_id: int, season: int, stat_group: str = 'hitting') -> Dict:
        """선수의 특정 시즌 스탯 조회"""
        try:
            url = f"{self.base_url}/people/{player_id}/stats"
            params = {
                'stats': 'season',
                'season': season,
                'group': stat_group  # 'hitting' 또는 'pitching'
            }
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get('stats') and len(data['stats']) > 0:
                return data['stats'][0].get('splits', [])
            return []
        except Exception as e:
            logger.error(f"선수 스탯 조회 실패 (선수: {player_id}, 시즌: {season}): {e}")
            return []
    
    def collect_batting_stats(self, seasons: List[int]) -> pd.DataFrame:
        """타자 스탯 수집"""
        all_batting_data = []
        
        for season in seasons:
            logger.info(f"타자 데이터 수집 중: {season}년")
            teams = self.get_teams(season)
            
            for team in teams:
                team_id = team['id']
                roster = self.get_roster(team_id, season)
                
                for player in roster:
                    player_info = player['person']
                    player_id = player_info['id']
                    position = player.get('position', {})
                    
                    # 타자인지 확인 (포지션 확인)
                    if position.get('abbreviation') not in ['P']:  # 투수가 아닌 경우
                        stats = self.get_player_stats(player_id, season, 'hitting')
                        
                        for stat_split in stats:
                            if stat_split.get('team', {}).get('id') == team_id:
                                batting_stats = stat_split.get('stat', {})
                                
                                # 필요한 스탯만 추출
                                row = {
                                    'PlayerID': player_id,
                                    'PlayerName': player_info['fullName'],
                                    'Season': season,
                                    'Team': team['name'],
                                    'BattingAverage': _safe_float(batting_stats.get('avg', 0)),
                                    'OnBasePercentage': _safe_float(batting_stats.get('obp', 0)),
                                    'SluggingPercentage': _safe_float(batting_stats.get('slg', 0)),
                                    'OPS': _safe_float(batting_stats.get('ops', 0)),
                                    'Hits': _safe_int(batting_stats.get('hits', 0)),
                                    'RBIs': _safe_int(batting_stats.get('rbi', 0)),
                                    'HomeRuns': _safe_int(batting_stats.get('homeRuns', 0)),
                                    'StolenBases': _safe_int(batting_stats.get('stolenBases', 0)),
                                    'Walks': _safe_int(batting_stats.get('baseOnBalls', 0)),
                                    'StrikeOuts': _safe_int(batting_stats.get('strikeOuts', 0))
                                }
                                all_batting_data.append(row)
                
                # API 호출 제한을 위한 지연
                time.sleep(API_RATE_LIMIT_DELAY)
        
        return pd.DataFrame(all_batting_data)
    
    def collect_pitching_stats(self, seasons: List[int]) -> pd.DataFrame:
        """투수 스탯 수집"""
        all_pitching_data = []
        
        for season in seasons:
            logger.info(f"투수 데이터 수집 중: {season}년")
            teams = self.get_teams(season)
            
            for team in teams:
                team_id = team['id']
                roster = self.get_roster(team_id, season)
                
                for player in roster:
                    player_info = player['person']
                    player_id = player_info['id']
                    position = player.get('position', {})
                    
                    # 투수인지 확인
                    if position.get('abbreviation') == 'P':
                        stats = self.get_player_stats(player_id, season, 'pitching')
                        
                        for stat_split in stats:
                            if stat_split.get('team', {}).get('id') == team_id:
                                pitching_stats = stat_split.get('stat', {})
                                
                                # 필요한 스탯만 추출
                                row = {
                                    'PlayerID': player_id,
                                    'PlayerName': player_info['fullName'],
                                    'Season': season,
                                    'Team': team['name'],
                                    'EarnedRunAverage': _safe_float(pitching_stats.get('era', 0)),
                                    'Whip': _safe_float(pitching_stats.get('whip', 0)),
                                    'Wins': _safe_int(pitching_stats.get('wins', 0)),
                                    'Losses': _safe_int(pitching_stats.get('losses', 0)),
                                    'StrikeOuts': _safe_int(pitching_stats.get('strikeOuts', 0)),
                                    'InningsPitched': _safe_float(pitching_stats.get('inningsPitched', 0)),
                                    'Walks': _safe_int(pitching_stats.get('baseOnBalls', 0)),
                                    'HitsAllowed': _safe_int(pitching_stats.get('hits', 0))
                                }
                                all_pitching_data.append(row)
                
                # API 호출 제한을 위한 지연
                time.sleep(API_RATE_LIMIT_DELAY)
        
        return pd.DataFrame(all_pitching_data)
    
    def merge_with_existing_data(self, new_data: pd.DataFrame, existing_file: str) -> pd.DataFrame:
        """새 데이터를 기존 데이터와 병합"""
        try:
            if os.path.exists(existing_file):
                existing_data = pd.read_csv(existing_file)
                
                # 중복 제거를 위해 PlayerID, Season 기준으로 병합
                combined_data = pd.concat([existing_data, new_data], ignore_index=True)
                combined_data = combined_data.drop_duplicates(
                    subset=['PlayerID', 'Season'], 
                    keep='last'
                ).sort_values(['PlayerName', 'Season'])
                
                return combined_data
            else:
                return new_data
        except Exception as e:
            logger.error(f"데이터 병합 실패: {e}")
            return new_data
    
    def update_data(self, start_year: int = 2024, end_year: int = None):
        """데이터 업데이트 실행"""
        seasons = self.get_seasons_list(start_year, end_year)
        logger.info(f"데이터 업데이트 시작: {seasons}")
        
        # 타자 데이터 수집 및 업데이트
        logger.info("타자 데이터 수집 시작...")
        new_batting_data = self.collect_batting_stats(seasons)
        if not new_batting_data.empty:
            updated_batting_data = self.merge_with_existing_data(
                new_batting_data, BATTER_STATS_FILE
            )
            updated_batting_data.to_csv(BATTER_STATS_FILE, index=False)
            logger.info(f"타자 데이터 업데이트 완료: {len(new_batting_data)}개 레코드 추가")
        
        # 투수 데이터 수집 및 업데이트
        logger.info("투수 데이터 수집 시작...")
        new_pitching_data = self.collect_pitching_stats(seasons)
        if not new_pitching_data.empty:
            updated_pitching_data = self.merge_with_existing_data(
                new_pitching_data, PITCHER_STATS_FILE
            )
            updated_pitching_data.to_csv(PITCHER_STATS_FILE, index=False)
            logger.info(f"투수 데이터 업데이트 완료: {len(new_pitching_data)}개 레코드 추가")
        
        logger.info("데이터 업데이트 완료!")

def main():
    """데이터 업데이트 실행"""
    processor = MLBDataProcessor()
    
    # 2024년부터 현재까지 데이터 업데이트
    current_year = datetime.now().year
    processor.update_data(start_year=2024, end_year=current_year)

if __name__ == "__main__":
    main()