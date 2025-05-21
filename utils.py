import pandas as pd
import streamlit as st
from PIL import Image
import os
import numpy as np
from matplotlib import pyplot as plt

# 데이터 캐싱 및 로드 기능 향상
@st.cache_data(ttl=3600, show_spinner=True)  # 1시간 TTL 설정
def load_data():
    """
    MLB 타자 데이터를 로드하고 캐싱합니다.
    
    Returns:
        pandas.DataFrame: 타자 데이터
    """
    try:
        data = pd.read_csv('./mlb_batter_stats_2000_2023.csv')
        data = data.reset_index(drop=True)
        return data
    except Exception as e:
        st.error(f"타자 데이터를 불러오는 중 오류가 발생했습니다: {e}")
        # 데이터 로드 실패 시 간단한 예시 데이터를 반환
        return _create_sample_batter_data()

@st.cache_data(ttl=3600, show_spinner=True)  # 1시간 TTL 설정
def load_pitcher_data():
    """
    MLB 투수 데이터를 로드하고 캐싱합니다.
    
    Returns:
        pandas.DataFrame: 투수 데이터
    """
    try:
        data = pd.read_csv('./mlb_pitcher_stats_2000_2023.csv')
        data = data.reset_index(drop=True)
        return data
    except Exception as e:
        st.error(f"투수 데이터를 불러오는 중 오류가 발생했습니다: {e}")
        # 데이터 로드 실패 시 간단한 예시 데이터를 반환
        return _create_sample_pitcher_data()

def load_logo_image(image_path):
    """
    이미지 파일을 로드합니다.
    
    Args:
        image_path (str): 이미지 경로
        
    Returns:
        PIL.Image: 로드된 이미지 객체, 또는 None (로드 실패 시)
    """
    try:
        return Image.open(image_path)
    except Exception as e:
        st.error(f"이미지를 불러오는 중 오류가 발생했습니다: {e}")
        return None

# 샘플 데이터 생성 함수들 (로드 실패 시 사용)
def _create_sample_batter_data():
    """데이터 로드 실패 시 사용할 타자 샘플 데이터를 생성합니다."""
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

def _create_sample_pitcher_data():
    """데이터 로드 실패 시 사용할 투수 샘플 데이터를 생성합니다."""
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
                'InningsPitched': round(np.random.uniform(150, 220), 1),
                'Walks': int(np.random.uniform(30, 80)),
                'HitsAllowed': int(np.random.uniform(120, 200))
            })
    return pd.DataFrame(data)

# 추가 유틸리티 함수
def set_chart_style():
    """차트 시각화를 위한 기본 스타일 설정"""
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams.update({
        'font.size': 12,
        'axes.titlesize': 16,
        'axes.labelsize': 14,
        'xtick.labelsize': 12,
        'ytick.labelsize': 12,
        'legend.fontsize': 12,
        'figure.figsize': (10, 6),
    })

def get_player_image_url(player_id):
    """선수의 프로필 이미지 URL을 생성합니다."""
    return f"https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_426,q_auto:best/v1/people/{player_id}/headshot/67/current"
