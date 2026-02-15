"""
데이터 업데이트 통합 테스트

PyBaseball 및 MLB API를 통한 데이터 수집 기능을 테스트합니다.
기존 test_data_update.py를 pytest 형식으로 마이그레이션했습니다.
"""

import pytest
import os
import pandas as pd
from config import BATTER_STATS_FILE, PITCHER_STATS_FILE


class TestExistingData:
    """기존 데이터 파일 검증"""

    def test_batter_data_file_exists(self):
        """타자 데이터 파일이 존재하는지 확인"""
        assert os.path.exists(BATTER_STATS_FILE), \
            f"타자 데이터 파일이 없습니다: {BATTER_STATS_FILE}"

    def test_pitcher_data_file_exists(self):
        """투수 데이터 파일이 존재하는지 확인"""
        assert os.path.exists(PITCHER_STATS_FILE), \
            f"투수 데이터 파일이 없습니다: {PITCHER_STATS_FILE}"

    def test_batter_data_not_empty(self):
        """타자 데이터가 비어있지 않은지 확인"""
        df = pd.read_csv(BATTER_STATS_FILE)
        assert len(df) > 0, "타자 데이터가 비어있습니다"

    def test_pitcher_data_not_empty(self):
        """투수 데이터가 비어있지 않은지 확인"""
        df = pd.read_csv(PITCHER_STATS_FILE)
        assert len(df) > 0, "투수 데이터가 비어있습니다"

    def test_batter_data_has_required_columns(self):
        """타자 데이터에 필수 컬럼이 있는지 확인"""
        df = pd.read_csv(BATTER_STATS_FILE)
        required_columns = [
            'Season', 'PlayerID', 'PlayerName',
            'BattingAverage', 'HomeRuns', 'RBIs'
        ]
        for col in required_columns:
            assert col in df.columns, f"필수 컬럼 {col}이 없습니다"

    def test_pitcher_data_has_required_columns(self):
        """투수 데이터에 필수 컬럼이 있는지 확인"""
        df = pd.read_csv(PITCHER_STATS_FILE)
        required_columns = [
            'Season', 'PlayerID', 'PlayerName',
            'EarnedRunAverage', 'Wins', 'StrikeOuts'
        ]
        for col in required_columns:
            assert col in df.columns, f"필수 컬럼 {col}이 없습니다"

    def test_batter_data_season_range(self):
        """타자 데이터의 시즌 범위 확인"""
        df = pd.read_csv(BATTER_STATS_FILE)
        min_season = df['Season'].min()
        max_season = df['Season'].max()

        assert min_season >= 2000, f"최소 시즌이 2000보다 작습니다: {min_season}"
        assert max_season <= 2030, f"최대 시즌이 2030보다 큽니다: {max_season}"
        assert min_season <= max_season, "시즌 범위가 잘못되었습니다"

    def test_pitcher_data_season_range(self):
        """투수 데이터의 시즌 범위 확인"""
        df = pd.read_csv(PITCHER_STATS_FILE)
        min_season = df['Season'].min()
        max_season = df['Season'].max()

        assert min_season >= 2000, f"최소 시즌이 2000보다 작습니다: {min_season}"
        assert max_season <= 2030, f"최대 시즌이 2030보다 큽니다: {max_season}"


@pytest.mark.integration
@pytest.mark.slow
class TestPyBaseball:
    """PyBaseball 데이터 수집 테스트"""

    def test_pybaseball_import(self):
        """PyBaseball 라이브러리를 import할 수 있는지 확인"""
        try:
            from pybaseball_processor import PyBaseballDataProcessor
            assert PyBaseballDataProcessor is not None
        except ImportError as e:
            pytest.fail(f"PyBaseball import 실패: {e}")

    @pytest.mark.skip(reason="실제 API 호출로 인해 느림, 필요시 수동 실행")
    def test_collect_batting_data(self):
        """타자 데이터 수집 테스트 (실제 API 호출)"""
        from pybaseball_processor import PyBaseballDataProcessor
        processor = PyBaseballDataProcessor()

        # 최근 1년만 테스트 (빠른 실행)
        batting_data = processor.collect_batting_data(2024, 2024)

        assert isinstance(batting_data, pd.DataFrame)
        if not batting_data.empty:
            assert 'PlayerName' in batting_data.columns
            assert len(batting_data) > 0

    @pytest.mark.skip(reason="실제 API 호출로 인해 느림, 필요시 수동 실행")
    def test_collect_pitching_data(self):
        """투수 데이터 수집 테스트 (실제 API 호출)"""
        from pybaseball_processor import PyBaseballDataProcessor
        processor = PyBaseballDataProcessor()

        # 최근 1년만 테스트
        pitching_data = processor.collect_pitching_data(2024, 2024)

        assert isinstance(pitching_data, pd.DataFrame)
        if not pitching_data.empty:
            assert 'PlayerName' in pitching_data.columns
            assert len(pitching_data) > 0


@pytest.mark.integration
@pytest.mark.slow
class TestMLBAPI:
    """MLB API 테스트"""

    def test_data_processor_import(self):
        """MLB Data Processor를 import할 수 있는지 확인"""
        try:
            from data_processor import MLBDataProcessor
            assert MLBDataProcessor is not None
        except ImportError as e:
            pytest.fail(f"MLBDataProcessor import 실패: {e}")

    @pytest.mark.skip(reason="실제 API 호출로 인해 느림, 필요시 수동 실행")
    def test_get_teams(self):
        """팀 목록 조회 테스트 (실제 API 호출)"""
        from data_processor import MLBDataProcessor
        processor = MLBDataProcessor()

        teams = processor.get_teams(2024)

        assert isinstance(teams, list)
        if len(teams) > 0:
            assert 'id' in teams[0]
            assert 'name' in teams[0]

    @pytest.mark.skip(reason="실제 API 호출로 인해 느림, 필요시 수동 실행")
    def test_get_roster(self):
        """로스터 조회 테스트 (실제 API 호출)"""
        from data_processor import MLBDataProcessor
        processor = MLBDataProcessor()

        # 양키스 팀 ID (147)
        roster = processor.get_roster(147, 2024)

        assert isinstance(roster, list)
        if len(roster) > 0:
            assert 'person' in roster[0]


class TestUpdateScripts:
    """업데이트 스크립트 import 테스트"""

    def test_update_data_import(self):
        """update_data.py를 import할 수 있는지 확인"""
        try:
            import update_data
            assert update_data is not None
        except ImportError as e:
            pytest.fail(f"update_data.py import 실패: {e}")

    def test_auto_update_import(self):
        """auto_update.py를 import할 수 있는지 확인"""
        try:
            import auto_update
            assert auto_update is not None
        except ImportError as e:
            pytest.fail(f"auto_update.py import 실패: {e}")


class TestDataProcessor:
    """데이터 처리 모듈 테스트"""

    def test_pybaseball_processor_initialization(self):
        """PyBaseball Processor 초기화 테스트"""
        from pybaseball_processor import PyBaseballDataProcessor
        processor = PyBaseballDataProcessor()
        assert processor is not None

    def test_mlb_data_processor_initialization(self):
        """MLB Data Processor 초기화 테스트"""
        from data_processor import MLBDataProcessor
        processor = MLBDataProcessor()
        assert processor is not None
        assert hasattr(processor, 'base_url')
