"""
utils.py 모듈 테스트

유틸리티 함수들이 올바르게 작동하는지 검증합니다.
"""

import pytest
import pandas as pd
from utils import (
    calculate_league_averages,
    get_player_image_url,
    get_plotly_layout_config,
    get_plotly_config,
    create_color_palette,
    get_chart_theme_options,
    get_theme_colors,
)


class TestCalculateLeagueAverages:
    """리그 평균 계산 테스트"""

    def test_calculate_league_averages_returns_dataframe(self, sample_batter_data):
        """데이터프레임을 반환하는지 확인"""
        metrics = ['BattingAverage', 'HomeRuns']
        result = calculate_league_averages(sample_batter_data, metrics)
        assert isinstance(result, pd.DataFrame)

    def test_calculate_league_averages_has_season_column(self, sample_batter_data):
        """Season 컬럼이 포함되는지 확인"""
        metrics = ['BattingAverage']
        result = calculate_league_averages(sample_batter_data, metrics)
        assert 'Season' in result.columns

    def test_calculate_league_averages_has_metric_columns(self, sample_batter_data):
        """요청한 메트릭 컬럼들이 포함되는지 확인"""
        metrics = ['BattingAverage', 'HomeRuns', 'RBIs']
        result = calculate_league_averages(sample_batter_data, metrics)

        for metric in metrics:
            assert metric in result.columns

    def test_calculate_league_averages_correct_calculation(self):
        """평균 계산이 정확한지 확인"""
        # 간단한 테스트 데이터
        df = pd.DataFrame({
            'Season': [2023, 2023, 2023],
            'BattingAverage': [0.300, 0.250, 0.350],
        })
        result = calculate_league_averages(df, ['BattingAverage'])

        # 2023 시즌 평균 = (0.300 + 0.250 + 0.350) / 3 = 0.300
        assert len(result) == 1
        assert result['Season'].iloc[0] == 2023
        assert abs(result['BattingAverage'].iloc[0] - 0.300) < 0.001

    def test_calculate_league_averages_multiple_seasons(self):
        """여러 시즌의 평균을 올바르게 계산하는지 확인"""
        df = pd.DataFrame({
            'Season': [2022, 2022, 2023, 2023],
            'HomeRuns': [30, 40, 35, 45],
        })
        result = calculate_league_averages(df, ['HomeRuns'])

        assert len(result) == 2
        assert 2022 in result['Season'].values
        assert 2023 in result['Season'].values


class TestPlayerImageUrl:
    """선수 이미지 URL 테스트"""

    def test_get_player_image_url_returns_string(self):
        """문자열 URL을 반환하는지 확인"""
        url = get_player_image_url("660271")
        assert isinstance(url, str)

    def test_get_player_image_url_contains_player_id(self):
        """URL에 선수 ID가 포함되는지 확인"""
        player_id = "592450"
        url = get_player_image_url(player_id)
        assert player_id in url

    def test_get_player_image_url_is_valid_url(self):
        """유효한 URL 형식인지 확인"""
        url = get_player_image_url("543807")
        assert url.startswith("http")
        assert "mlbstatic.com" in url


class TestPlotlyConfig:
    """Plotly 설정 테스트"""

    def test_get_plotly_layout_config_returns_dict(self):
        """딕셔너리를 반환하는지 확인"""
        config = get_plotly_layout_config()
        assert isinstance(config, dict)

    def test_get_plotly_layout_config_with_title(self):
        """제목이 설정되는지 확인"""
        title = "Test Chart"
        config = get_plotly_layout_config(title=title)
        assert 'title' in config
        assert config['title']['text'] == title

    def test_get_plotly_layout_config_with_axis_titles(self):
        """축 제목이 설정되는지 확인"""
        config = get_plotly_layout_config(
            xaxis_title="X Axis",
            yaxis_title="Y Axis"
        )
        assert 'xaxis' in config
        assert 'yaxis' in config

    def test_get_plotly_layout_config_with_height(self):
        """높이가 설정되는지 확인"""
        height = 600
        config = get_plotly_layout_config(height=height)
        assert 'height' in config
        assert config['height'] == height

    def test_get_plotly_config_returns_dict(self):
        """Plotly config가 딕셔너리를 반환하는지 확인"""
        config = get_plotly_config()
        assert isinstance(config, dict)

    def test_get_plotly_config_has_display_mode_bar(self):
        """displayModeBar 설정이 있는지 확인"""
        config = get_plotly_config()
        assert 'displayModeBar' in config


class TestColorPalette:
    """색상 팔레트 테스트"""

    def test_create_color_palette_returns_list(self):
        """리스트를 반환하는지 확인"""
        palette = create_color_palette()
        assert isinstance(palette, list)

    def test_create_color_palette_correct_length(self):
        """요청한 색상 개수만큼 반환하는지 확인"""
        n_colors = 5
        palette = create_color_palette(n_colors)
        assert len(palette) == n_colors

    def test_create_color_palette_returns_hex_colors(self):
        """HEX 색상 코드를 반환하는지 확인"""
        palette = create_color_palette(3)
        for color in palette:
            assert isinstance(color, str)
            # HEX 색상은 #으로 시작하고 6자리 또는 8자리
            assert color.startswith('#')

    def test_create_color_palette_different_colors(self):
        """서로 다른 색상을 반환하는지 확인"""
        palette = create_color_palette(5)
        # 모든 색상이 unique해야 함
        assert len(set(palette)) == len(palette)


class TestChartTheme:
    """차트 테마 테스트"""

    def test_get_chart_theme_options_returns_dict(self):
        """테마 옵션 딕셔너리를 반환하는지 확인"""
        options = get_chart_theme_options()
        assert isinstance(options, dict)

    def test_get_chart_theme_options_not_empty(self):
        """테마 옵션이 비어있지 않은지 확인"""
        options = get_chart_theme_options()
        assert len(options) > 0

    def test_get_chart_theme_options_contains_strings(self):
        """모든 테마 값이 문자열인지 확인"""
        options = get_chart_theme_options()
        assert all(isinstance(value, str) for value in options.values())

    def test_get_theme_colors_returns_dict(self):
        """테마 색상이 딕셔너리를 반환하는지 확인"""
        colors = get_theme_colors()
        assert isinstance(colors, dict)

    def test_get_theme_colors_has_required_keys(self):
        """필수 색상 키들이 포함되는지 확인"""
        colors = get_theme_colors()
        required_keys = ['plot_bgcolor', 'paper_bgcolor', 'font_color', 'grid_color', 'line_colors']
        for key in required_keys:
            assert key in colors, f"{key} 색상이 없습니다"

    def test_get_theme_colors_different_themes(self):
        """다른 테마는 다른 색상을 반환하는지 확인"""
        colors_white = get_theme_colors("plotly_white")
        colors_dark = get_theme_colors("plotly_dark")

        # 적어도 하나의 색상은 달라야 함
        assert colors_white != colors_dark


class TestDataLoading:
    """데이터 로딩 테스트 (샘플 데이터 사용)"""

    def test_sample_data_creation(self, sample_batter_data, sample_pitcher_data):
        """샘플 데이터가 올바르게 생성되는지 확인"""
        # 타자 데이터
        assert isinstance(sample_batter_data, pd.DataFrame)
        assert len(sample_batter_data) > 0
        assert 'PlayerName' in sample_batter_data.columns
        assert 'BattingAverage' in sample_batter_data.columns

        # 투수 데이터
        assert isinstance(sample_pitcher_data, pd.DataFrame)
        assert len(sample_pitcher_data) > 0
        assert 'PlayerName' in sample_pitcher_data.columns
        assert 'EarnedRunAverage' in sample_pitcher_data.columns

    def test_sample_data_has_valid_values(self, sample_batter_data):
        """샘플 데이터의 값이 유효한지 확인"""
        # 타율은 0과 1 사이
        assert all(0 <= ba <= 1 for ba in sample_batter_data['BattingAverage'])

        # 홈런은 음수가 아님
        assert all(hr >= 0 for hr in sample_batter_data['HomeRuns'])

    def test_sample_pitcher_data_has_valid_values(self, sample_pitcher_data):
        """샘플 투수 데이터의 값이 유효한지 확인"""
        # ERA는 양수
        assert all(era >= 0 for era in sample_pitcher_data['EarnedRunAverage'])

        # WHIP는 양수
        assert all(whip >= 0 for whip in sample_pitcher_data['Whip'])


@pytest.mark.parametrize("n_colors", [1, 5, 10])
class TestColorPaletteParametrized:
    """색상 팔레트 파라미터화 테스트"""

    def test_create_color_palette_with_various_sizes(self, n_colors):
        """다양한 크기의 색상 팔레트 생성 (Plotly 기본 팔레트는 10개까지)"""
        palette = create_color_palette(n_colors)
        assert len(palette) == min(n_colors, 10)  # Plotly 기본 팔레트는 10개
        assert all(isinstance(color, str) for color in palette)
