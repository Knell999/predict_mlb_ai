import pandas as pd
import streamlit as st
from PIL import Image
import os
import numpy as np
from matplotlib import pyplot as plt
from config import (
    BATTER_STATS_FILE, PITCHER_STATS_FILE, FONT_PATH, MLB_LOGO_PATH,
    DATA_START_YEAR, DATA_END_YEAR, MLB_IMAGE_CDN_URL, CACHE_TTL_SECONDS,
)

def _load_csv_file(file_path, data_name, fallback_fn):
    """CSV 파일을 로드하고 전처리합니다. 실패 시 fallback 함수를 호출합니다."""
    try:
        df = pd.read_csv(file_path)
        df = df.rename(columns=lambda x: x.strip())
        numeric_cols = df.select_dtypes(include=np.number).columns
        df[numeric_cols] = df[numeric_cols].fillna(0)
        return df
    except FileNotFoundError:
        st.error(f"{data_name} 데이터 파일을 찾을 수 없습니다: {file_path}")
        st.info("샘플 데이터를 대신 사용합니다.")
        return fallback_fn()
    except Exception as e:
        st.error(f"{data_name} 데이터 로드 중 오류 발생: {e}")
        st.info("샘플 데이터를 대신 사용합니다.")
        return fallback_fn()

@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=True)
def load_data():
    """타자 데이터를 로드합니다."""
    return _load_csv_file(BATTER_STATS_FILE, "타자", _create_sample_batter_data)

@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=True)
def load_pitcher_data():
    """투수 데이터를 로드합니다."""
    return _load_csv_file(PITCHER_STATS_FILE, "투수", _create_sample_pitcher_data)

def calculate_league_averages(df, metrics):
    """시즌별 리그 평균을 계산합니다."""
    return df.groupby('Season')[metrics].mean().reset_index()

def load_logo_image(image_path=MLB_LOGO_PATH):
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
    seasons = list(range(DATA_START_YEAR, DATA_END_YEAR))
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
    seasons = list(range(DATA_START_YEAR, DATA_END_YEAR))
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
    return MLB_IMAGE_CDN_URL.format(player_id=player_id)

def get_placeholder_image():
    """
    선수 이미지 로딩 실패 시 사용할 placeholder 이미지를 반환합니다.
    간단한 회색 이미지를 numpy 배열로 생성합니다.
    """
    import numpy as np
    from PIL import Image

    # 200x200 회색 이미지 생성
    placeholder = np.ones((200, 200, 3), dtype=np.uint8) * 200

    # 중앙에 "No Image" 텍스트를 표시하고 싶지만, PIL로 간단하게 처리
    return Image.fromarray(placeholder)

def display_player_image(player_id, player_name, width=200):
    """
    선수 이미지를 표시합니다. 로딩 실패 시 placeholder를 표시합니다.

    Args:
        player_id: 선수 ID
        player_name: 선수 이름
        width: 이미지 너비
    """
    try:
        image_url = get_player_image_url(player_id)
        st.image(image_url, caption=f"{player_name}", width=width)
    except Exception as e:
        placeholder = get_placeholder_image()
        st.image(placeholder, caption=f"{player_name} (이미지 없음)", width=width)

# Plotly 차트 공통 설정
def get_plotly_layout_config(title="", xaxis_title="", yaxis_title="", height=500):
    """
    Plotly 차트의 공통 레이아웃 설정을 반환합니다.

    Args:
        title: 차트 제목
        xaxis_title: X축 제목
        yaxis_title: Y축 제목
        height: 차트 높이

    Returns:
        dict: Plotly layout 설정
    """
    return {
        'title': {
            'text': title,
            'font': {'size': 18, 'family': 'Arial, sans-serif'},
            'x': 0.5,
            'xanchor': 'center'
        },
        'xaxis': {
            'title': xaxis_title,
            'showgrid': True,
            'gridcolor': 'lightgray'
        },
        'yaxis': {
            'title': yaxis_title,
            'showgrid': True,
            'gridcolor': 'lightgray'
        },
        'height': height,
        'hovermode': 'closest',
        'plot_bgcolor': 'white',
        'paper_bgcolor': 'white',
        'font': {'family': 'Arial, sans-serif'}
    }

def get_plotly_config():
    """
    Plotly 차트의 상호작용 설정을 반환합니다.
    다운로드, 확대/축소 등의 기능을 포함합니다.
    """
    return {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToAdd': ['downloadSvg'],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'mlb_chart',
            'height': 800,
            'width': 1200,
            'scale': 2
        }
    }

def create_color_palette(n_colors=10):
    """
    시각화를 위한 색상 팔레트를 생성합니다.

    Args:
        n_colors: 생성할 색상 수

    Returns:
        list: 색상 코드 리스트
    """
    import plotly.express as px
    return px.colors.qualitative.Plotly[:n_colors]

# 차트 테마 관련 함수
def get_chart_theme_options():
    """
    사용 가능한 차트 테마 옵션을 반환합니다.
    """
    return {
        "라이트 모드 🌞": "plotly_white",
        "다크 모드 🌙": "plotly_dark",
        "색약자 친화 🎨": "colorblind_friendly",
        "비비드 컬러 🌈": "vivid"
    }

def get_theme_colors(theme="plotly_white"):
    """
    테마에 따른 색상 설정을 반환합니다.

    Args:
        theme: 테마 이름

    Returns:
        dict: 색상 설정
    """
    if theme == "plotly_dark":
        return {
            'plot_bgcolor': '#1e1e1e',
            'paper_bgcolor': '#1e1e1e',
            'font_color': 'white',
            'grid_color': '#444444',
            'line_colors': ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A']
        }
    elif theme == "colorblind_friendly":
        return {
            'plot_bgcolor': 'white',
            'paper_bgcolor': 'white',
            'font_color': 'black',
            'grid_color': 'lightgray',
            'line_colors': ['#0173B2', '#DE8F05', '#029E73', '#CC78BC', '#ECE133']
        }
    elif theme == "vivid":
        return {
            'plot_bgcolor': 'white',
            'paper_bgcolor': 'white',
            'font_color': 'black',
            'grid_color': 'lightgray',
            'line_colors': ['#E74C3C', '#3498DB', '#2ECC71', '#F39C12', '#9B59B6']
        }
    else:  # plotly_white (default)
        return {
            'plot_bgcolor': 'white',
            'paper_bgcolor': 'white',
            'font_color': 'black',
            'grid_color': 'lightgray',
            'line_colors': ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A']
        }

def apply_theme_to_figure(fig, theme="plotly_white"):
    """
    Plotly Figure에 테마를 적용합니다.

    Args:
        fig: Plotly Figure 객체
        theme: 테마 이름

    Returns:
        fig: 테마가 적용된 Figure 객체
    """
    colors = get_theme_colors(theme)

    fig.update_layout(
        plot_bgcolor=colors['plot_bgcolor'],
        paper_bgcolor=colors['paper_bgcolor'],
        font=dict(color=colors['font_color'])
    )

    fig.update_xaxes(gridcolor=colors['grid_color'])
    fig.update_yaxes(gridcolor=colors['grid_color'])

    return fig
