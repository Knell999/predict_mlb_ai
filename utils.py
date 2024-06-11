import pandas as pd
import streamlit as st
from PIL import Image

@st.cache_data
def load_data():
    data = pd.read_csv('./mlb_batter_stats_2000_2023.csv')
    data = data.reset_index(drop=True)
    return data

@st.cache_data
def load_pitcher_data():
    data = pd.read_csv('./mlb_pitcher_stats_2000_2023.csv')
    data = data.reset_index(drop=True)
    return data

def load_logo_image(image_path):
    try:
        return Image.open(image_path)
    except Exception as e:
        st.error(f"이미지를 불러오는 중 오류가 발생했습니다: {e}")
        return None
