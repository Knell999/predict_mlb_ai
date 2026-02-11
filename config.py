"""
Configuration file for the MLB Player Stats and Prediction App.
Contains paths, constants, and other settings.
"""

import os

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data files
DATA_DIR = os.path.join(BASE_DIR, "data")
BATTER_STATS_FILE = os.path.join(DATA_DIR, "mlb_batter_stats_2000_2023.csv")
PITCHER_STATS_FILE = os.path.join(DATA_DIR, "mlb_pitcher_stats_2000_2023.csv")

# Font files
FONT_DIR = os.path.join(BASE_DIR, "font")
FONT_PATH = os.path.join(FONT_DIR, "H2GTRM.TTF")

# Image files
MLB_LOGO_PATH = os.path.join(BASE_DIR, "mlb_logo.png")
MLB_PLAYERS_IMAGE_PATH = os.path.join(BASE_DIR, "mlb_players.jpg")

# Log directory
LOG_DIR = os.path.join(BASE_DIR, "logs")

# === Data collection settings ===
DATA_START_YEAR = 2000
DATA_END_YEAR = 2025
MLB_SEASON_START_MONTH = 3
MLB_SEASON_END_MONTH = 10

# === API settings ===
MLB_API_BASE_URL = "https://statsapi.mlb.com/api/v1"
MLB_IMAGE_CDN_URL = "https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_426,q_auto:best/v1/people/{player_id}/headshot/67/current"
API_RATE_LIMIT_DELAY = 0.2

# === AI analysis settings ===
AI_MODEL_NAME = "gemini-2.5-pro"
AI_TEMPERATURE = 0.3
AI_MAX_TOKENS = 20000

# === Chart settings ===
DEFAULT_CHART_THEME = "plotly_white"
DEFAULT_CHART_HEIGHT = 500

# === Language settings ===
DEFAULT_LANGUAGE = "ko"

# === Caching settings ===
CACHE_TTL_SECONDS = 3600

# === Metric definitions ===
BATTING_METRICS = [
    'BattingAverage', 'OnBasePercentage', 'SluggingPercentage', 'OPS',
    'Hits', 'RBIs', 'HomeRuns', 'StolenBases', 'Walks', 'StrikeOuts'
]

PITCHING_METRICS = [
    'EarnedRunAverage', 'Whip', 'Wins', 'Losses',
    'StrikeOuts', 'InningsPitched', 'Walks', 'HitsAllowed'
]

BATTING_TREND_METRICS = [
    'BattingAverage', 'OnBasePercentage', 'SluggingPercentage', 'OPS',
    'Hits', 'RBIs', 'HomeRuns', 'StolenBases'
]

PITCHING_TREND_METRICS = [
    'EarnedRunAverage', 'Whip', 'Wins', 'StrikeOuts', 'InningsPitched'
]

BATTER_METRIC_NAMES = {
    'BattingAverage': '타율',
    'OnBasePercentage': '출루율',
    'SluggingPercentage': '장타율',
    'OPS': 'OPS',
    'Hits': '안타',
    'RBIs': '타점',
    'HomeRuns': '홈런',
    'StolenBases': '도루',
    'Walks': '볼넷',
    'StrikeOuts': '삼진',
}

PITCHER_METRIC_NAMES = {
    'EarnedRunAverage': '평균자책점',
    'Whip': 'WHIP',
    'Wins': '승수',
    'Losses': '패수',
    'StrikeOuts': '탈삼진',
    'InningsPitched': '이닝',
    'Walks': '볼넷',
    'HitsAllowed': '피안타',
}

PREDICT_BATTER_METRICS = {
    'BattingAverage': '타율',
    'OnBasePercentage': '출루율',
    'SluggingPercentage': '장타율',
    'OPS': 'OPS',
}

PREDICT_PITCHER_METRICS = {
    'EarnedRunAverage': '평균자책점',
    'Wins': '승수',
    'Losses': '패수',
    'StrikeOuts': '탈삼진',
    'Whip': 'WHIP',
    'InningsPitched': '이닝',
}
