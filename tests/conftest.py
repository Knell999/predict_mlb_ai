"""
pytest 설정 및 공유 fixtures

이 파일은 모든 테스트에서 사용할 수 있는 공통 fixtures를 정의합니다.
"""

import pytest
import pandas as pd
from pathlib import Path


@pytest.fixture
def sample_batter_data():
    """타자 테스트 데이터 샘플"""
    return pd.DataFrame({
        'Season': [2023, 2023, 2024],
        'PlayerID': ['660271', '592450', '543807'],
        'PlayerName': ['Shohei Ohtani', 'Aaron Judge', 'Mookie Betts'],
        'Team': ['LAA', 'NYY', 'LAD'],
        'GamesPlayed': [135, 157, 142],
        'AtBats': [497, 550, 520],
        'Runs': [95, 133, 115],
        'Hits': [151, 177, 163],
        'HomeRuns': [44, 62, 35],
        'RBIs': [95, 131, 107],
        'StolenBases': [20, 16, 12],
        'Walks': [72, 111, 82],
        'StrikeOuts': [103, 175, 88],
        'BattingAverage': [0.304, 0.322, 0.314],
        'OnBasePercentage': [0.412, 0.425, 0.408],
        'SluggingPercentage': [0.654, 0.686, 0.579],
        'OPS': [1.066, 1.111, 0.987],
    })


@pytest.fixture
def sample_pitcher_data():
    """투수 테스트 데이터 샘플"""
    return pd.DataFrame({
        'Season': [2023, 2023, 2024],
        'PlayerID': ['665155', '543037', '592789'],
        'PlayerName': ['Gerrit Cole', 'Justin Verlander', 'Spencer Strider'],
        'Team': ['NYY', 'HOU', 'ATL'],
        'Wins': [15, 13, 20],
        'Losses': [4, 8, 5],
        'EarnedRunAverage': [2.63, 3.22, 2.20],
        'Whip': [1.02, 1.13, 0.99],
        'StrikeOuts': [222, 183, 281],
        'InningsPitched': [209.0, 162.1, 186.2],
        'Walks': [50, 32, 38],
        'HitsAllowed': [163, 152, 127],
    })


@pytest.fixture
def temp_data_dir(tmp_path):
    """임시 데이터 디렉토리 생성"""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir


@pytest.fixture
def sample_csv_files(temp_data_dir, sample_batter_data, sample_pitcher_data):
    """테스트용 CSV 파일 생성"""
    batter_file = temp_data_dir / "mlb_batter_stats_2000_2023.csv"
    pitcher_file = temp_data_dir / "mlb_pitcher_stats_2000_2023.csv"

    sample_batter_data.to_csv(batter_file, index=False)
    sample_pitcher_data.to_csv(pitcher_file, index=False)

    return {
        'batter_file': str(batter_file),
        'pitcher_file': str(pitcher_file),
    }


@pytest.fixture
def mock_env(monkeypatch):
    """환경변수 모킹"""
    monkeypatch.setenv("GOOGLE_AI_API_KEY", "test_api_key_123")
    return monkeypatch


@pytest.fixture(scope="session")
def test_languages():
    """테스트용 언어 목록"""
    return ["ko", "en", "ja"]


@pytest.fixture
def sample_player_stats():
    """선수 통계 샘플 (단일 선수)"""
    return {
        'Season': 2023,
        'PlayerName': 'Test Player',
        'BattingAverage': 0.300,
        'HomeRuns': 30,
        'RBIs': 100,
        'OPS': 0.900,
    }
