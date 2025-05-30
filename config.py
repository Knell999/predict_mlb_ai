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

# Prediction settings (example)
# DEFAULT_PREDICTION_YEARS = 2

# Add other configurations as needed
