"""
config.py 모듈 테스트

설정 파일의 상수와 경로가 올바르게 정의되어 있는지 검증합니다.
"""

import pytest
import os
from pathlib import Path
import config


class TestPaths:
    """경로 상수 테스트"""

    def test_base_dir_exists(self):
        """BASE_DIR이 존재하는 디렉토리인지 확인"""
        assert os.path.isdir(config.BASE_DIR)

    def test_data_dir_path(self):
        """DATA_DIR 경로가 올바른지 확인"""
        assert config.DATA_DIR.endswith("data")
        assert os.path.isdir(config.DATA_DIR)

    def test_batter_stats_file_path(self):
        """타자 통계 파일 경로 확인"""
        assert config.BATTER_STATS_FILE.endswith(".csv")
        assert "batter" in config.BATTER_STATS_FILE.lower()

    def test_pitcher_stats_file_path(self):
        """투수 통계 파일 경로 확인"""
        assert config.PITCHER_STATS_FILE.endswith(".csv")
        assert "pitcher" in config.PITCHER_STATS_FILE.lower()

    def test_font_path(self):
        """폰트 파일 경로 확인"""
        assert config.FONT_PATH.endswith(".TTF")
        assert "font" in config.FONT_PATH.lower()


class TestDataSettings:
    """데이터 수집 설정 테스트"""

    def test_data_year_range(self):
        """데이터 수집 연도 범위가 유효한지 확인"""
        assert config.DATA_START_YEAR >= 2000
        assert config.DATA_END_YEAR >= config.DATA_START_YEAR
        assert config.DATA_END_YEAR <= 2030

    def test_season_months(self):
        """시즌 기간이 유효한지 확인"""
        assert 1 <= config.MLB_SEASON_START_MONTH <= 12
        assert 1 <= config.MLB_SEASON_END_MONTH <= 12
        assert config.MLB_SEASON_START_MONTH < config.MLB_SEASON_END_MONTH


class TestAPISettings:
    """API 설정 테스트"""

    def test_mlb_api_base_url(self):
        """MLB API URL이 유효한지 확인"""
        assert config.MLB_API_BASE_URL.startswith("https://")
        assert "mlb.com" in config.MLB_API_BASE_URL

    def test_api_rate_limit_delay(self):
        """API 요청 딜레이가 양수인지 확인"""
        assert config.API_RATE_LIMIT_DELAY > 0
        assert isinstance(config.API_RATE_LIMIT_DELAY, (int, float))


class TestAISettings:
    """AI 분석 설정 테스트"""

    def test_ai_model_name(self):
        """AI 모델명이 문자열인지 확인"""
        assert isinstance(config.AI_MODEL_NAME, str)
        assert len(config.AI_MODEL_NAME) > 0

    def test_ai_temperature(self):
        """AI 온도 설정이 유효 범위인지 확인"""
        assert 0 <= config.AI_TEMPERATURE <= 2.0

    def test_ai_max_tokens(self):
        """AI 최대 토큰이 양수인지 확인"""
        assert config.AI_MAX_TOKENS > 0
        assert isinstance(config.AI_MAX_TOKENS, int)


class TestMetrics:
    """메트릭 정의 테스트"""

    def test_batting_metrics_not_empty(self):
        """타자 메트릭 리스트가 비어있지 않은지 확인"""
        assert len(config.BATTING_METRICS) > 0
        assert isinstance(config.BATTING_METRICS, list)

    def test_pitching_metrics_not_empty(self):
        """투수 메트릭 리스트가 비어있지 않은지 확인"""
        assert len(config.PITCHING_METRICS) > 0
        assert isinstance(config.PITCHING_METRICS, list)

    def test_batting_metrics_are_strings(self):
        """타자 메트릭이 모두 문자열인지 확인"""
        assert all(isinstance(m, str) for m in config.BATTING_METRICS)

    def test_pitching_metrics_are_strings(self):
        """투수 메트릭이 모두 문자열인지 확인"""
        assert all(isinstance(m, str) for m in config.PITCHING_METRICS)

    def test_batter_metric_names_dict(self):
        """타자 메트릭 이름 딕셔너리 검증"""
        assert isinstance(config.BATTER_METRIC_NAMES, dict)
        assert len(config.BATTER_METRIC_NAMES) > 0
        # 모든 BATTING_METRICS가 BATTER_METRIC_NAMES에 포함되어야 함
        for metric in config.BATTING_METRICS:
            assert metric in config.BATTER_METRIC_NAMES, \
                f"{metric}이 BATTER_METRIC_NAMES에 없습니다"

    def test_pitcher_metric_names_dict(self):
        """투수 메트릭 이름 딕셔너리 검증"""
        assert isinstance(config.PITCHER_METRIC_NAMES, dict)
        assert len(config.PITCHER_METRIC_NAMES) > 0
        # 모든 PITCHING_METRICS가 PITCHER_METRIC_NAMES에 포함되어야 함
        for metric in config.PITCHING_METRICS:
            assert metric in config.PITCHER_METRIC_NAMES, \
                f"{metric}이 PITCHER_METRIC_NAMES에 없습니다"

    def test_predict_batter_metrics(self):
        """예측용 타자 메트릭 검증"""
        assert isinstance(config.PREDICT_BATTER_METRICS, dict)
        assert len(config.PREDICT_BATTER_METRICS) > 0
        # 모든 키가 BATTING_METRICS에 포함되어야 함
        for metric in config.PREDICT_BATTER_METRICS.keys():
            assert metric in config.BATTING_METRICS

    def test_predict_pitcher_metrics(self):
        """예측용 투수 메트릭 검증"""
        assert isinstance(config.PREDICT_PITCHER_METRICS, dict)
        assert len(config.PREDICT_PITCHER_METRICS) > 0
        # 모든 키가 PITCHING_METRICS에 포함되어야 함
        for metric in config.PREDICT_PITCHER_METRICS.keys():
            assert metric in config.PITCHING_METRICS


class TestOtherSettings:
    """기타 설정 테스트"""

    def test_default_language(self):
        """기본 언어 설정 확인"""
        assert config.DEFAULT_LANGUAGE in ["ko", "en", "ja"]

    def test_cache_ttl(self):
        """캐시 TTL이 양수인지 확인"""
        assert config.CACHE_TTL_SECONDS > 0
        assert isinstance(config.CACHE_TTL_SECONDS, int)

    def test_chart_settings(self):
        """차트 설정 확인"""
        assert isinstance(config.DEFAULT_CHART_THEME, str)
        assert config.DEFAULT_CHART_HEIGHT > 0
        assert isinstance(config.DEFAULT_CHART_HEIGHT, int)
