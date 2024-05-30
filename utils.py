# utils.py

import pandas as pd
import streamlit as st


@st.cache_data
def load_data():
    data = pd.read_csv('./mlb_batter_stats_2000_2023.csv')
    return data
