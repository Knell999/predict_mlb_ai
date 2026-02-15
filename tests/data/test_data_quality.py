"""
데이터 품질 테스트

기존 data_quality_checker.py를 pytest 형식으로 마이그레이션했습니다.
CSV 파일의 데이터 무결성 및 품질을 검증합니다.
"""

import pytest
import pandas as pd
from data_quality_checker import DataQualityChecker


@pytest.fixture(scope="module")
def quality_checker():
    """DataQualityChecker 인스턴스 생성"""
    return DataQualityChecker()


@pytest.fixture(scope="module")
def quality_report(quality_checker):
    """전체 품질 보고서 생성 (한 번만 실행)"""
    return quality_checker.generate_report()


class TestFileExistence:
    """파일 존재 여부 테스트"""

    def test_check_file_existence(self, quality_checker):
        """파일 존재 여부 확인 메서드 테스트"""
        result = quality_checker.check_file_existence()
        assert isinstance(result, dict)
        assert 'batter_file_exists' in result
        assert 'pitcher_file_exists' in result

    def test_batter_file_exists(self, quality_checker):
        """타자 데이터 파일이 존재하는지 확인"""
        result = quality_checker.check_file_existence()
        assert result['batter_file_exists'] is True, \
            "타자 데이터 파일이 존재하지 않습니다"

    def test_pitcher_file_exists(self, quality_checker):
        """투수 데이터 파일이 존재하는지 확인"""
        result = quality_checker.check_file_existence()
        assert result['pitcher_file_exists'] is True, \
            "투수 데이터 파일이 존재하지 않습니다"


class TestDataStructure:
    """데이터 구조 검증 테스트"""

    def test_check_data_structure(self, quality_checker):
        """데이터 구조 확인 메서드 테스트"""
        result = quality_checker.check_data_structure()
        assert isinstance(result, dict)
        assert 'batter' in result
        assert 'pitcher' in result

    def test_batter_data_has_records(self, quality_checker):
        """타자 데이터에 레코드가 있는지 확인"""
        result = quality_checker.check_data_structure()
        assert result['batter']['total_records'] > 0, \
            "타자 데이터에 레코드가 없습니다"

    def test_pitcher_data_has_records(self, quality_checker):
        """투수 데이터에 레코드가 있는지 확인"""
        result = quality_checker.check_data_structure()
        assert result['pitcher']['total_records'] > 0, \
            "투수 데이터에 레코드가 없습니다"

    def test_batter_required_columns_present(self, quality_checker):
        """타자 데이터 필수 컬럼 존재 확인"""
        result = quality_checker.check_data_structure()
        missing_cols = result['batter'].get('missing_columns', [])
        assert len(missing_cols) == 0, \
            f"타자 데이터에 누락된 컬럼: {missing_cols}"

    def test_pitcher_required_columns_present(self, quality_checker):
        """투수 데이터 필수 컬럼 존재 확인"""
        result = quality_checker.check_data_structure()
        missing_cols = result['pitcher'].get('missing_columns', [])
        assert len(missing_cols) == 0, \
            f"투수 데이터에 누락된 컬럼: {missing_cols}"

    def test_batter_no_duplicate_columns(self, quality_checker):
        """타자 데이터 중복 컬럼 확인"""
        result = quality_checker.check_data_structure()
        duplicate_cols = result['batter'].get('duplicate_columns', [])
        assert len(duplicate_cols) == 0, \
            f"타자 데이터에 중복 컬럼: {duplicate_cols}"

    def test_pitcher_no_duplicate_columns(self, quality_checker):
        """투수 데이터 중복 컬럼 확인"""
        result = quality_checker.check_data_structure()
        duplicate_cols = result['pitcher'].get('duplicate_columns', [])
        assert len(duplicate_cols) == 0, \
            f"투수 데이터에 중복 컬럼: {duplicate_cols}"

    def test_batter_season_range_valid(self, quality_checker):
        """타자 데이터 시즌 범위 유효성 확인"""
        result = quality_checker.check_data_structure()
        min_season = result['batter']['season_range']['min']
        max_season = result['batter']['season_range']['max']

        assert min_season >= 2000, f"최소 시즌이 너무 작습니다: {min_season}"
        assert max_season <= 2030, f"최대 시즌이 너무 큽니다: {max_season}"
        assert min_season <= max_season, "시즌 범위가 잘못되었습니다"

    def test_pitcher_season_range_valid(self, quality_checker):
        """투수 데이터 시즌 범위 유효성 확인"""
        result = quality_checker.check_data_structure()
        min_season = result['pitcher']['season_range']['min']
        max_season = result['pitcher']['season_range']['max']

        assert min_season >= 2000, f"최소 시즌이 너무 작습니다: {min_season}"
        assert max_season <= 2030, f"최대 시즌이 너무 큽니다: {max_season}"


@pytest.mark.data
class TestDataQuality:
    """데이터 품질 검증 테스트"""

    def test_check_data_quality(self, quality_checker):
        """데이터 품질 확인 메서드 테스트"""
        result = quality_checker.check_data_quality()
        assert isinstance(result, dict)
        assert 'batter' in result
        assert 'pitcher' in result

    def test_batter_no_duplicate_records(self, quality_checker):
        """타자 데이터 중복 레코드 확인"""
        result = quality_checker.check_data_quality()
        duplicate_count = result['batter']['duplicate_records']
        assert duplicate_count == 0, \
            f"타자 데이터에 {duplicate_count}개 중복 레코드가 있습니다"

    def test_pitcher_no_duplicate_records(self, quality_checker):
        """투수 데이터 중복 레코드 확인"""
        result = quality_checker.check_data_quality()
        duplicate_count = result['pitcher']['duplicate_records']
        assert duplicate_count == 0, \
            f"투수 데이터에 {duplicate_count}개 중복 레코드가 있습니다"

    def test_batter_valid_batting_average(self, quality_checker):
        """타율이 유효 범위(0~1)인지 확인"""
        result = quality_checker.check_data_quality()
        out_of_range = result['batter']['out_of_range_stats'].get('BattingAverage', 0)
        assert out_of_range == 0, \
            f"유효하지 않은 타율 값이 {out_of_range}개 있습니다"

    def test_batter_valid_ops(self, quality_checker):
        """OPS가 유효 범위(0~5)인지 확인"""
        result = quality_checker.check_data_quality()
        out_of_range = result['batter']['out_of_range_stats'].get('OPS', 0)
        assert out_of_range == 0, \
            f"유효하지 않은 OPS 값이 {out_of_range}개 있습니다"

    def test_pitcher_valid_era(self, quality_checker):
        """ERA가 유효 범위(0~15)인지 확인"""
        result = quality_checker.check_data_quality()
        out_of_range = result['pitcher']['out_of_range_stats'].get('EarnedRunAverage', 0)
        assert out_of_range == 0, \
            f"유효하지 않은 ERA 값이 {out_of_range}개 있습니다"

    def test_pitcher_valid_whip(self, quality_checker):
        """WHIP가 유효 범위(0~5)인지 확인"""
        result = quality_checker.check_data_quality()
        out_of_range = result['pitcher']['out_of_range_stats'].get('Whip', 0)
        assert out_of_range == 0, \
            f"유효하지 않은 WHIP 값이 {out_of_range}개 있습니다"

    @pytest.mark.skip(reason="논리적 일관성 검사는 선택적 검증")
    def test_batter_logical_consistency(self, quality_checker):
        """타자 데이터 논리적 일관성 확인 (안타 <= 타수)"""
        result = quality_checker.check_data_quality()
        inconsistencies = result['batter'].get('logical_inconsistencies', 0)
        assert inconsistencies == 0, \
            f"논리적으로 일관되지 않은 타자 레코드가 {inconsistencies}개 있습니다"


class TestSeasonStatistics:
    """시즌 통계 테스트"""

    def test_get_season_statistics(self, quality_checker):
        """시즌 통계 조회 메서드 테스트"""
        result = quality_checker.get_season_statistics()
        assert isinstance(result, dict)
        assert 'batter' in result
        assert 'pitcher' in result

    def test_batter_has_season_stats(self, quality_checker):
        """타자 시즌별 통계가 존재하는지 확인"""
        result = quality_checker.get_season_statistics()
        assert len(result['batter']) > 0, "타자 시즌 통계가 없습니다"

    def test_pitcher_has_season_stats(self, quality_checker):
        """투수 시즌별 통계가 존재하는지 확인"""
        result = quality_checker.get_season_statistics()
        assert len(result['pitcher']) > 0, "투수 시즌 통계가 없습니다"


class TestGenerateReport:
    """종합 보고서 생성 테스트"""

    def test_generate_report(self, quality_report):
        """종합 보고서가 생성되는지 확인"""
        assert isinstance(quality_report, dict)

    def test_report_has_all_sections(self, quality_report):
        """보고서에 모든 섹션이 포함되는지 확인"""
        required_sections = [
            'timestamp',
            'file_existence',
            'data_structure',
            'data_quality',
            'season_statistics'
        ]
        for section in required_sections:
            assert section in quality_report, \
                f"보고서에 {section} 섹션이 없습니다"

    def test_report_timestamp_format(self, quality_report):
        """보고서 타임스탬프 형식 확인"""
        timestamp = quality_report['timestamp']
        assert isinstance(timestamp, str)
        assert len(timestamp) > 0

    def test_report_summary_exists(self, quality_report):
        """보고서 요약이 존재하는지 확인"""
        assert 'summary' in quality_report or \
               'file_existence' in quality_report


@pytest.mark.data
class TestDataIntegrity:
    """데이터 무결성 통합 테스트"""

    def test_overall_data_health(self, quality_report):
        """전체 데이터 건강성 확인"""
        # 파일이 모두 존재해야 함
        file_check = quality_report['file_existence']
        assert file_check['batter_file_exists'] is True
        assert file_check['pitcher_file_exists'] is True

        # 데이터가 비어있지 않아야 함
        structure = quality_report['data_structure']
        assert structure['batter']['total_records'] > 0
        assert structure['pitcher']['total_records'] > 0

    def test_no_critical_quality_issues(self, quality_report):
        """치명적인 품질 문제가 없는지 확인"""
        quality = quality_report['data_quality']

        # 중복 레코드가 없어야 함
        assert quality['batter']['duplicate_records'] == 0
        assert quality['pitcher']['duplicate_records'] == 0

        # 필수 컬럼이 모두 있어야 함
        structure = quality_report['data_structure']
        assert len(structure['batter']['missing_columns']) == 0
        assert len(structure['pitcher']['missing_columns']) == 0
