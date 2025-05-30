"""
애플리케이션 설정 관리 모듈
"""
import os
from dataclasses import dataclass
from typing import Dict, List, Optional
import json

@dataclass
class AppConfig:
    """애플리케이션 설정"""
    data_paths: Dict[str, str]
    supported_languages: List[str]
    default_language: str
    cache_ttl: int
    max_prediction_periods: int
    base_dir: str
    font_path: str
    logo_path: str
    log_dir: str
    
    @classmethod
    def from_file(cls, config_path: str) -> 'AppConfig':
        """설정 파일에서 로드"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                
            return cls(
                data_paths=config_data.get('data_paths', {}),
                supported_languages=config_data.get('supported_languages', ['ko', 'en', 'ja']),
                default_language=config_data.get('default_language', 'ko'),
                cache_ttl=config_data.get('cache_ttl', 3600),
                max_prediction_periods=config_data.get('max_prediction_periods', 5),
                base_dir=config_data.get('base_dir', os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                font_path=config_data.get('font_path', ''),
                logo_path=config_data.get('logo_path', ''),
                log_dir=config_data.get('log_dir', '')
            )
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # 파일이 없거나 JSON 형식이 아닌 경우 기본값 사용
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            return cls(
                data_paths={
                    'batter': os.path.join(base_dir, 'data', 'raw', 'mlb_batter_stats_2000_2023.csv'),
                    'pitcher': os.path.join(base_dir, 'data', 'raw', 'mlb_pitcher_stats_2000_2023.csv')
                },
                supported_languages=['ko', 'en', 'ja'],
                default_language='ko',
                cache_ttl=3600,
                max_prediction_periods=5,
                base_dir=base_dir,
                font_path=os.path.join(base_dir, 'font', 'H2GTRM.TTF'),
                logo_path=os.path.join(base_dir, 'mlb_logo.png'),
                log_dir=os.path.join(base_dir, 'logs')
            )
            
    def save_to_file(self, config_path: str) -> None:
        """설정을 파일로 저장"""
        config_data = {
            'data_paths': self.data_paths,
            'supported_languages': self.supported_languages,
            'default_language': self.default_language,
            'cache_ttl': self.cache_ttl,
            'max_prediction_periods': self.max_prediction_periods,
            'base_dir': self.base_dir,
            'font_path': self.font_path,
            'logo_path': self.logo_path,
            'log_dir': self.log_dir
        }
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"설정 저장 중 오류 발생: {e}")


# 메트릭 설정 - 타자
BATTING_METRICS = {
    'BattingAverage': {'min': 0, 'max': 0.4, 'format': '.3f', 'description': '타율'},
    'OnBasePercentage': {'min': 0, 'max': 0.7, 'format': '.3f', 'description': '출루율'},
    'SluggingPercentage': {'min': 0, 'max': 0.8, 'format': '.3f', 'description': '장타율'},
    'OPS': {'min': 0, 'max': 1.4, 'format': '.3f', 'description': 'OPS(출루율+장타율)'},
    'HomeRuns': {'min': 0, 'max': 80, 'format': '.0f', 'description': '홈런'},
    'Hits': {'min': 0, 'max': 250, 'format': '.0f', 'description': '안타'},
    'RBIs': {'min': 0, 'max': 200, 'format': '.0f', 'description': '타점'},
    'StolenBases': {'min': 0, 'max': 100, 'format': '.0f', 'description': '도루'},
    'Walks': {'min': 0, 'max': 150, 'format': '.0f', 'description': '볼넷'},
    'StrikeOuts': {'min': 0, 'max': 250, 'format': '.0f', 'description': '삼진'}
}

# 메트릭 설정 - 투수
PITCHING_METRICS = {
    'EarnedRunAverage': {'min': 0, 'max': 5, 'format': '.2f', 'description': '평균자책점'},
    'Whip': {'min': 0, 'max': 4, 'format': '.2f', 'description': 'WHIP'},
    'Wins': {'min': 0, 'max': 35, 'format': '.0f', 'description': '승리'},
    'Losses': {'min': 0, 'max': 30, 'format': '.0f', 'description': '패배'},
    'StrikeOuts': {'min': 0, 'max': 400, 'format': '.0f', 'description': '삼진'},
    'InningsPitched': {'min': 0, 'max': 300, 'format': '.1f', 'description': '이닝'},
    'Walks': {'min': 0, 'max': 150, 'format': '.0f', 'description': '볼넷'},
    'HitsAllowed': {'min': 0, 'max': 300, 'format': '.0f', 'description': '피안타'}
}

# 기본 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
BATTER_STATS_FILE = os.path.join(DATA_DIR, "mlb_batter_stats_2000_2023.csv")
PITCHER_STATS_FILE = os.path.join(DATA_DIR, "mlb_pitcher_stats_2000_2023.csv")
FONT_PATH = os.path.join(BASE_DIR, "..", "font", "H2GTRM.TTF")
MLB_LOGO_PATH = os.path.join(BASE_DIR, "..", "mlb_logo.png")
MLB_PLAYERS_IMAGE_PATH = os.path.join(BASE_DIR, "..", "mlb_players.jpg")
LOG_DIR = os.path.join(BASE_DIR, "..", "logs")
