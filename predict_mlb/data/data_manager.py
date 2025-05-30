"""
데이터 관리 모듈: 데이터 로드, 필터링, 계산 등의 기능을 제공합니다.
"""
import pandas as pd
import numpy as np
import os
import streamlit as st
from typing import List, Dict, Any, Tuple, Optional

class DataManager:
    """통합 데이터 관리 클래스"""
    def __init__(self, batter_file: str, pitcher_file: str):
        """
        DataManager 클래스 초기화
        
        Args:
            batter_file: 타자 데이터 파일 경로
            pitcher_file: 투수 데이터 파일 경로
        """
        self.batter_file = batter_file
        self.pitcher_file = pitcher_file
        self.batter_data = None
        self.pitcher_data = None
        
    @st.cache_data(ttl=3600, show_spinner=True)
    def load_all_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        모든 데이터를 로드하고 전처리합니다.
        
        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: 타자 데이터와 투수 데이터
        """
        self.batter_data = self._load_batter_data()
        self.pitcher_data = self._load_pitcher_data()
        return self.batter_data, self.pitcher_data
    
    def _load_batter_data(self) -> pd.DataFrame:
        """
        타자 데이터를 로드합니다.
        
        Returns:
            pd.DataFrame: 전처리된 타자 데이터
        """
        try:
            df = pd.read_csv(self.batter_file)
            # 데이터 클리닝 및 전처리
            df = df.rename(columns=lambda x: x.strip())  # 컬럼명 공백 제거
            numeric_cols = df.select_dtypes(include=np.number).columns
            df[numeric_cols] = df[numeric_cols].fillna(0)  # 숫자형 컬럼 NaN 0으로 채우기
            return df
        except FileNotFoundError:
            st.error(f"타자 데이터 파일을 찾을 수 없습니다: {self.batter_file}")
            st.info("샘플 데이터를 대신 사용합니다.")
            return self._create_sample_batter_data()
        except Exception as e:
            st.error(f"타자 데이터 로드 중 오류 발생: {e}")
            st.info("샘플 데이터를 대신 사용합니다.")
            return self._create_sample_batter_data()
    
    def _load_pitcher_data(self) -> pd.DataFrame:
        """
        투수 데이터를 로드합니다.
        
        Returns:
            pd.DataFrame: 전처리된 투수 데이터
        """
        try:
            df = pd.read_csv(self.pitcher_file)
            # 데이터 클리닝 및 전처리
            df = df.rename(columns=lambda x: x.strip())  # 컬럼명 공백 제거
            numeric_cols = df.select_dtypes(include=np.number).columns
            df[numeric_cols] = df[numeric_cols].fillna(0)  # 숫자형 컬럼 NaN 0으로 채우기
            return df
        except FileNotFoundError:
            st.error(f"투수 데이터 파일을 찾을 수 없습니다: {self.pitcher_file}")
            st.info("샘플 데이터를 대신 사용합니다.")
            return self._create_sample_pitcher_data()
        except Exception as e:
            st.error(f"투수 데이터 로드 중 오류 발생: {e}")
            st.info("샘플 데이터를 대신 사용합니다.")
            return self._create_sample_pitcher_data()
    
    def get_player_data(self, player_name: str, player_type: str = 'batter') -> pd.DataFrame:
        """
        특정 선수의 데이터를 조회합니다.
        
        Args:
            player_name: 선수 이름
            player_type: 선수 유형 ('batter' 또는 'pitcher')
            
        Returns:
            pd.DataFrame: 해당 선수의 데이터
        """
        if not self.batter_data or not self.pitcher_data:
            self.load_all_data()
            
        if player_type.lower() == 'batter':
            return self.batter_data[self.batter_data['PlayerName'] == player_name]
        else:
            return self.pitcher_data[self.pitcher_data['PlayerName'] == player_name]
    
    def calculate_league_averages(self, metrics: List[str], player_type: str = 'batter') -> pd.DataFrame:
        """
        리그 평균을 계산합니다.
        
        Args:
            metrics: 계산할 지표 리스트
            player_type: 선수 유형 ('batter' 또는 'pitcher')
            
        Returns:
            pd.DataFrame: 시즌별 리그 평균 데이터프레임
        """
        if not self.batter_data or not self.pitcher_data:
            self.load_all_data()
            
        if player_type.lower() == 'batter':
            return self.batter_data.groupby('Season')[metrics].mean().reset_index()
        else:
            return self.pitcher_data.groupby('Season')[metrics].mean().reset_index()
    
    def calculate_moving_average(self, df: pd.DataFrame, metrics: List[str], window: int) -> pd.DataFrame:
        """
        이동평균을 계산합니다.
        
        Args:
            df: 데이터프레임
            metrics: 계산할 지표 리스트
            window: 이동평균 윈도우 크기
            
        Returns:
            pd.DataFrame: 이동평균이 계산된 데이터프레임
        """
        moving_avg = df.copy()
        for metric in metrics:
            moving_avg[metric] = moving_avg[metric].rolling(window=window, min_periods=1).mean()
        return moving_avg
    
    def get_all_players(self, player_type: str = 'batter') -> List[str]:
        """
        모든 선수 이름 목록을 반환합니다.
        
        Args:
            player_type: 선수 유형 ('batter' 또는 'pitcher')
            
        Returns:
            List[str]: 선수 이름 목록
        """
        if not self.batter_data or not self.pitcher_data:
            self.load_all_data()
            
        if player_type.lower() == 'batter':
            return sorted(self.batter_data['PlayerName'].unique())
        else:
            return sorted(self.pitcher_data['PlayerName'].unique())
    
    def get_all_seasons(self) -> List[int]:
        """
        모든 시즌 목록을 반환합니다.
        
        Returns:
            List[int]: 시즌 목록
        """
        if not self.batter_data:
            self.load_all_data()
            
        return sorted(self.batter_data['Season'].unique())
    
    def _create_sample_batter_data(self) -> pd.DataFrame:
        """
        데이터 로드 실패 시 사용할 타자 샘플 데이터를 생성합니다.
        
        Returns:
            pd.DataFrame: 샘플 타자 데이터
        """
        seasons = list(range(2000, 2024))
        player_names = ["Mike Trout", "Aaron Judge", "Shohei Ohtani"]
        player_ids = ["1234567", "7654321", "9876543"]
        
        data = []
        for player_name, player_id in zip(player_names, player_ids):
            for season in seasons:
                data.append({
                    'PlayerID': player_id,
                    'PlayerName': player_name,
                    'Season': season,
                    'BattingAverage': round(np.random.uniform(0.250, 0.350), 3),
                    'OnBasePercentage': round(np.random.uniform(0.330, 0.450), 3),
                    'SluggingPercentage': round(np.random.uniform(0.400, 0.650), 3),
                    'OPS': round(np.random.uniform(0.750, 1.050), 3),
                    'Hits': int(np.random.uniform(120, 220)),
                    'RBIs': int(np.random.uniform(70, 130)),
                    'HomeRuns': int(np.random.uniform(15, 45)),
                    'StolenBases': int(np.random.uniform(0, 30)),
                    'Walks': int(np.random.uniform(40, 100)),
                    'StrikeOuts': int(np.random.uniform(80, 200))
                })
        return pd.DataFrame(data)
    
    def _create_sample_pitcher_data(self) -> pd.DataFrame:
        """
        데이터 로드 실패 시 사용할 투수 샘플 데이터를 생성합니다.
        
        Returns:
            pd.DataFrame: 샘플 투수 데이터
        """
        seasons = list(range(2000, 2024))
        player_names = ["Clayton Kershaw", "Jacob deGrom", "Gerrit Cole"]
        player_ids = ["1234568", "7654322", "9876544"]
        
        data = []
        for player_name, player_id in zip(player_names, player_ids):
            for season in seasons:
                data.append({
                    'PlayerID': player_id,
                    'PlayerName': player_name,
                    'Season': season,
                    'EarnedRunAverage': round(np.random.uniform(2.0, 4.5), 2),
                    'Whip': round(np.random.uniform(0.9, 1.3), 2),
                    'Wins': int(np.random.uniform(10, 20)),
                    'Losses': int(np.random.uniform(5, 15)),
                    'StrikeOuts': int(np.random.uniform(150, 300)),
                    'Walks': int(np.random.uniform(30, 90)),
                    'HitsAllowed': int(np.random.uniform(120, 200)),
                    'InningsPitched': round(np.random.uniform(150, 220), 1)
                })
        return pd.DataFrame(data)
