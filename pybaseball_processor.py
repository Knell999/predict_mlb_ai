"""
PyBaseball을 활용한 MLB 데이터 수집 스크립트
더 간단하고 안정적인 데이터 수집 방법
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging
import os
from config import DATA_DIR, BATTER_STATS_FILE, PITCHER_STATS_FILE

# pybaseball이 설치되어 있지 않은 경우를 대비한 import
try:
    from pybaseball import batting_stats, pitching_stats
    PYBASEBALL_AVAILABLE = True
except ImportError:
    PYBASEBALL_AVAILABLE = False
    print("pybaseball이 설치되지 않았습니다. 설치하려면 'pip install pybaseball'을 실행하세요.")

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PyBaseballDataProcessor:
    """PyBaseball을 활용한 데이터 수집 클래스"""
    
    def __init__(self):
        if not PYBASEBALL_AVAILABLE:
            raise ImportError("pybaseball 라이브러리가 필요합니다. 'pip install pybaseball'로 설치하세요.")
    
    def collect_batting_data(self, start_year: int = 2024, end_year: int = None) -> pd.DataFrame:
        """타자 데이터 수집"""
        if end_year is None:
            end_year = datetime.now().year
        
        logger.info(f"타자 데이터 수집: {start_year}-{end_year}")
        
        all_data = []
        for year in range(start_year, end_year + 1):
            try:
                logger.info(f"  {year}년 타자 데이터 수집 중...")
                yearly_data = batting_stats(year, qual=50)  # 최소 50타석 이상
                
                if not yearly_data.empty:
                    # 컬럼명 매핑 (존재하는 컬럼만)
                    column_mapping = {
                        'IDfg': 'PlayerID',
                        'Name': 'PlayerName',
                        'AVG': 'BattingAverage',
                        'OBP': 'OnBasePercentage',
                        'SLG': 'SluggingPercentage',
                        'OPS': 'OPS',
                        'H': 'Hits',
                        'RBI': 'RBIs',
                        'HR': 'HomeRuns',
                        'SB': 'StolenBases',
                        'BB': 'Walks',
                        'SO': 'StrikeOuts'
                    }
                    safe_mapping = {k: v for k, v in column_mapping.items() if k in yearly_data.columns}
                    yearly_data = yearly_data.rename(columns=safe_mapping)
                    
                    # 시즌 컬럼 추가
                    yearly_data['Season'] = year
                    
                    # 필요한 컬럼만 선택
                    columns_to_keep = [
                        'PlayerID', 'PlayerName', 'Season', 'Team',
                        'BattingAverage', 'OnBasePercentage', 'SluggingPercentage', 
                        'OPS', 'Hits', 'RBIs', 'HomeRuns', 'StolenBases', 
                        'Walks', 'StrikeOuts'
                    ]
                    
                    # 존재하는 컬럼만 선택
                    available_columns = [col for col in columns_to_keep if col in yearly_data.columns]
                    yearly_data = yearly_data[available_columns]
                    
                    all_data.append(yearly_data)
                    logger.info(f"    {len(yearly_data)}명의 선수 데이터 수집 완료")
                
            except Exception as e:
                logger.error(f"  {year}년 타자 데이터 수집 실패: {e}")
                continue
        
        if all_data:
            result = pd.concat(all_data, ignore_index=True)
            logger.info(f"타자 데이터 수집 완료: 총 {len(result)}개 레코드")
            return result
        else:
            logger.warning("수집된 타자 데이터가 없습니다.")
            return pd.DataFrame()
    
    def collect_pitching_data(self, start_year: int = 2024, end_year: int = None) -> pd.DataFrame:
        """투수 데이터 수집"""
        if end_year is None:
            end_year = datetime.now().year
        
        logger.info(f"투수 데이터 수집: {start_year}-{end_year}")
        
        all_data = []
        for year in range(start_year, end_year + 1):
            try:
                logger.info(f"  {year}년 투수 데이터 수집 중...")
                yearly_data = pitching_stats(year, qual=20)  # 최소 20이닝 이상
                
                if not yearly_data.empty:
                    # 컬럼명 매핑 (존재하는 컬럼만)
                    column_mapping = {
                        'IDfg': 'PlayerID',
                        'Name': 'PlayerName',
                        'ERA': 'EarnedRunAverage',
                        'WHIP': 'Whip',
                        'W': 'Wins',
                        'L': 'Losses',
                        'SO': 'StrikeOuts',
                        'IP': 'InningsPitched',
                        'BB': 'Walks',
                        'H': 'HitsAllowed'
                    }
                    safe_mapping = {k: v for k, v in column_mapping.items() if k in yearly_data.columns}
                    yearly_data = yearly_data.rename(columns=safe_mapping)
                    
                    # 시즌 컬럼 추가
                    yearly_data['Season'] = year
                    
                    # 필요한 컬럼만 선택
                    columns_to_keep = [
                        'PlayerID', 'PlayerName', 'Season', 'Team',
                        'EarnedRunAverage', 'Whip', 'Wins', 'Losses', 
                        'StrikeOuts', 'InningsPitched', 'Walks', 'HitsAllowed'
                    ]
                    
                    # 존재하는 컬럼만 선택
                    available_columns = [col for col in columns_to_keep if col in yearly_data.columns]
                    yearly_data = yearly_data[available_columns]
                    
                    all_data.append(yearly_data)
                    logger.info(f"    {len(yearly_data)}명의 선수 데이터 수집 완료")
                
            except Exception as e:
                logger.error(f"  {year}년 투수 데이터 수집 실패: {e}")
                continue
        
        if all_data:
            result = pd.concat(all_data, ignore_index=True)
            logger.info(f"투수 데이터 수집 완료: 총 {len(result)}개 레코드")
            return result
        else:
            logger.warning("수집된 투수 데이터가 없습니다.")
            return pd.DataFrame()
    
    def merge_with_existing_data(self, new_data: pd.DataFrame, existing_file: str) -> pd.DataFrame:
        """새 데이터를 기존 데이터와 병합"""
        try:
            if os.path.exists(existing_file):
                existing_data = pd.read_csv(existing_file)
                logger.info(f"기존 데이터: {len(existing_data)}개 레코드")
                
                # 중복 제거를 위해 PlayerID, Season 기준으로 병합
                combined_data = pd.concat([existing_data, new_data], ignore_index=True)
                
                # PlayerID와 Season으로 중복 제거 (새 데이터 우선)
                combined_data = combined_data.drop_duplicates(
                    subset=['PlayerID', 'Season'], 
                    keep='last'
                ).sort_values(['PlayerName', 'Season'])
                
                logger.info(f"병합 후: {len(combined_data)}개 레코드")
                return combined_data
            else:
                logger.info("기존 파일이 없습니다. 새 파일을 생성합니다.")
                return new_data
        except Exception as e:
            logger.error(f"데이터 병합 실패: {e}")
            return new_data
    
    def update_data(self, start_year: int = 2024, end_year: int = None):
        """데이터 업데이트 실행"""
        logger.info(f"PyBaseball을 사용한 데이터 업데이트 시작")
        
        # 타자 데이터 수집 및 업데이트
        logger.info("=== 타자 데이터 업데이트 ===")
        new_batting_data = self.collect_batting_data(start_year, end_year)
        if not new_batting_data.empty:
            updated_batting_data = self.merge_with_existing_data(
                new_batting_data, BATTER_STATS_FILE
            )
            updated_batting_data.to_csv(BATTER_STATS_FILE, index=False)
            logger.info(f"타자 데이터 저장 완료: {BATTER_STATS_FILE}")
        
        # 투수 데이터 수집 및 업데이트
        logger.info("=== 투수 데이터 업데이트 ===")
        new_pitching_data = self.collect_pitching_data(start_year, end_year)
        if not new_pitching_data.empty:
            updated_pitching_data = self.merge_with_existing_data(
                new_pitching_data, PITCHER_STATS_FILE
            )
            updated_pitching_data.to_csv(PITCHER_STATS_FILE, index=False)
            logger.info(f"투수 데이터 저장 완료: {PITCHER_STATS_FILE}")
        
        logger.info("데이터 업데이트 완료!")

def main():
    """PyBaseball 데이터 업데이트 실행"""
    if not PYBASEBALL_AVAILABLE:
        print("pybaseball 라이브러리를 먼저 설치해주세요:")
        print("pip install pybaseball")
        return
    
    processor = PyBaseballDataProcessor()
    
    # 2024년부터 현재까지 데이터 업데이트
    current_year = datetime.now().year
    processor.update_data(start_year=2024, end_year=current_year)

if __name__ == "__main__":
    main()
