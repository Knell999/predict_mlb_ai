import pandas as pd
import streamlit as st
from PIL import Image
import os
import numpy as np
from matplotlib import pyplot as plt
from config import BATTER_STATS_FILE, PITCHER_STATS_FILE, FONT_PATH, MLB_LOGO_PATH

# 데이터 캐싱 및 로드 기능 향상
@st.cache_data(ttl=3600, show_spinner=True)  # 1시간 TTL 설정
def load_data():
    """타자 데이터를 로드합니다. 파일 경로를 config에서 가져옵니다."""
    try:
        df = pd.read_csv(BATTER_STATS_FILE)
        # 데이터 클리닝 또는 전처리 (예시)
        df = df.rename(columns=lambda x: x.strip()) # 컬럼명 공백 제거
        numeric_cols = df.select_dtypes(include=np.number).columns
        df[numeric_cols] = df[numeric_cols].fillna(0) # 숫자형 컬럼 NaN 0으로 채우기
        return df
    except FileNotFoundError:
        st.error(f"타자 데이터 파일을 찾을 수 없습니다: {BATTER_STATS_FILE}")
        st.info("샘플 데이터를 대신 사용합니다.")
        return _create_sample_batter_data()
    except Exception as e:
        st.error(f"타자 데이터 로드 중 오류 발생: {e}")
        st.info("샘플 데이터를 대신 사용합니다.")
        return _create_sample_batter_data()

@st.cache_data(ttl=3600, show_spinner=True)  # 1시간 TTL 설정
def load_pitcher_data():
    """투수 데이터를 로드합니다. 파일 경로를 config에서 가져옵니다."""
    try:
        df = pd.read_csv(PITCHER_STATS_FILE)
        # 데이터 클리닝 또는 전처리 (예시)
        df = df.rename(columns=lambda x: x.strip()) # 컬럼명 공백 제거
        numeric_cols = df.select_dtypes(include=np.number).columns
        df[numeric_cols] = df[numeric_cols].fillna(0) # 숫자형 컬럼 NaN 0으로 채우기
        return df
    except FileNotFoundError:
        st.error(f"투수 데이터 파일을 찾을 수 없습니다: {PITCHER_STATS_FILE}")
        st.info("샘플 데이터를 대신 사용합니다.")
        return _create_sample_pitcher_data()
    except Exception as e:
        st.error(f"투수 데이터 로드 중 오류 발생: {e}")
        st.info("샘플 데이터를 대신 사용합니다.")
        return _create_sample_pitcher_data()

def load_logo_image(image_path=MLB_LOGO_PATH): # 기본값을 config에서 가져오도록 수정
    """로고 이미지를 로드합니다."""
    try:
        if not os.path.exists(image_path):
            st.error(f"로고 파일을 찾을 수 없습니다: {image_path}")
            return None
        return Image.open(image_path)
    except Exception as e:
        st.error(f"로고 이미지 로드 중 오류 발생: {e}")
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
    """차트 스타일을 설정합니다. 폰트 경로를 config에서 가져옵니다."""
    plt.rcParams['font.family'] = 'sans-serif' # 기본 폰트 설정
    if os.path.exists(FONT_PATH):
        plt.rcParams['font.sans-serif'] = [fm.FontProperties(fname=FONT_PATH).get_name(), 'Malgun Gothic', 'AppleGothic', 'sans-serif']
    else:
        # 사용 가능한 시스템 폰트로 대체 (예: 'Malgun Gothic' for Windows, 'AppleGothic' for macOS)
        # 이 부분은 운영체제에 따라 적절한 폰트 리스트를 제공해야 합니다.
        # 여기서는 간단히 경고만 출력하고 기본 sans-serif를 사용합니다.
        st.warning(f"지정된 폰트 파일을 찾을 수 없습니다: {FONT_PATH}. 기본 시스템 폰트를 사용합니다.")
        plt.rcParams['font.sans-serif'] = ['Malgun Gothic', 'AppleGothic', 'sans-serif']
        
    plt.rcParams['axes.unicode_minus'] = False # 마이너스 부호 깨짐 방지
    # Seaborn 스타일 설정 (선택 사항)
    sns.set_style("whitegrid")
    sns.set_context("talk") # talk, paper, notebook, poster
    # Matplotlib 추가 설정
    plt.rcParams['figure.figsize'] = (10, 6)
    plt.rcParams['axes.titlesize'] = 16
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['xtick.labelsize'] = 12
    plt.rcParams['ytick.labelsize'] = 12
    plt.rcParams['legend.fontsize'] = 12

# matplotlib.font_manager 임포트 추가
import matplotlib.font_manager as fm
import seaborn as sns # seaborn 임포트 추가

def get_player_image_url(player_id):
    """선수의 프로필 이미지 URL을 생성합니다."""
    return f"https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_426,q_auto:best/v1/people/{player_id}/headshot/67/current"
