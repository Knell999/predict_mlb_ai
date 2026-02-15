"""
데이터 처리 모듈 통합 테스트

데이터 처리 모듈(data_processor, pybaseball_processor)의 기능을 테스트합니다.
"""

import pytest


class TestMLBDataProcessor:
    """MLB Data Processor 테스트"""

    def test_import_mlb_data_processor(self):
        """MLBDataProcessor를 import할 수 있는지 확인"""
        from data_processor import MLBDataProcessor
        assert MLBDataProcessor is not None

    def test_mlb_data_processor_initialization(self):
        """MLBDataProcessor 초기화 테스트"""
        from data_processor import MLBDataProcessor
        processor = MLBDataProcessor()
        assert processor is not None

    def test_mlb_data_processor_has_base_url(self):
        """MLBDataProcessor가 base_url을 가지고 있는지 확인"""
        from data_processor import MLBDataProcessor
        processor = MLBDataProcessor()
        assert hasattr(processor, 'base_url')
        assert 'mlb.com' in processor.base_url


class TestPyBaseballProcessor:
    """PyBaseball Processor 테스트"""

    def test_import_pybaseball_processor(self):
        """PyBaseballDataProcessor를 import할 수 있는지 확인"""
        from pybaseball_processor import PyBaseballDataProcessor
        assert PyBaseballDataProcessor is not None

    def test_pybaseball_processor_initialization(self):
        """PyBaseballDataProcessor 초기화 테스트"""
        from pybaseball_processor import PyBaseballDataProcessor
        processor = PyBaseballDataProcessor()
        assert processor is not None

    def test_pybaseball_has_collect_methods(self):
        """PyBaseballDataProcessor가 수집 메서드를 가지고 있는지 확인"""
        from pybaseball_processor import PyBaseballDataProcessor
        processor = PyBaseballDataProcessor()
        assert hasattr(processor, 'collect_batting_data')
        assert hasattr(processor, 'collect_pitching_data')
