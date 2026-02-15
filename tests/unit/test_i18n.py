"""
i18n.py 모듈 테스트

다국어 지원 기능이 올바르게 작동하는지 검증합니다.
"""

import pytest
from i18n import get_text, get_languages, get_metric_name, get_metric_names_dict


class TestGetLanguages:
    """언어 목록 조회 테스트"""

    def test_get_languages_returns_list(self):
        """언어 목록이 리스트로 반환되는지 확인"""
        languages = get_languages()
        assert isinstance(languages, list)

    def test_get_languages_contains_korean(self):
        """한국어가 포함되어 있는지 확인"""
        languages = get_languages()
        assert "ko" in languages

    def test_get_languages_contains_english(self):
        """영어가 포함되어 있는지 확인"""
        languages = get_languages()
        assert "en" in languages

    def test_get_languages_contains_japanese(self):
        """일본어가 포함되어 있는지 확인"""
        languages = get_languages()
        assert "ja" in languages

    def test_get_languages_has_three_languages(self):
        """정확히 3개 언어를 지원하는지 확인"""
        languages = get_languages()
        assert len(languages) == 3


class TestGetText:
    """텍스트 조회 테스트"""

    def test_get_text_returns_string(self):
        """get_text가 문자열을 반환하는지 확인"""
        text = get_text("app_title", "ko")
        assert isinstance(text, str)

    def test_get_text_korean(self):
        """한국어 텍스트 조회"""
        text = get_text("app_title", "ko")
        assert len(text) > 0
        # 한국어 텍스트는 한글을 포함해야 함
        assert any('\uac00' <= c <= '\ud7a3' for c in text)

    def test_get_text_english(self):
        """영어 텍스트 조회"""
        text = get_text("app_title", "en")
        assert len(text) > 0
        assert isinstance(text, str)

    def test_get_text_japanese(self):
        """일본어 텍스트 조회"""
        text = get_text("app_title", "ja")
        assert len(text) > 0
        assert isinstance(text, str)

    def test_get_text_default_language(self):
        """기본 언어(한국어)로 조회"""
        text_default = get_text("app_title")
        text_korean = get_text("app_title", "ko")
        assert text_default == text_korean

    def test_get_text_different_languages_return_different_values(self):
        """언어별로 다른 텍스트를 반환하는지 확인"""
        text_ko = get_text("app_title", "ko")
        text_en = get_text("app_title", "en")
        text_ja = get_text("app_title", "ja")

        # 최소한 하나는 달라야 함
        assert text_ko != text_en or text_en != text_ja or text_ko != text_ja

    def test_get_text_invalid_key_returns_key(self):
        """존재하지 않는 키는 키 자체를 반환하는지 확인"""
        invalid_key = "this_key_does_not_exist_12345"
        result = get_text(invalid_key, "ko")
        assert result == invalid_key


class TestGetMetricName:
    """메트릭 이름 조회 테스트"""

    def test_get_metric_name_batting_average_korean(self):
        """타율 메트릭 한국어 이름 조회"""
        name = get_metric_name("BattingAverage", "ko")
        assert isinstance(name, str)
        assert len(name) > 0

    def test_get_metric_name_era_korean(self):
        """평균자책점 메트릭 한국어 이름 조회"""
        name = get_metric_name("EarnedRunAverage", "ko")
        assert isinstance(name, str)
        assert len(name) > 0

    def test_get_metric_name_returns_string(self):
        """메트릭 이름이 문자열로 반환되는지 확인"""
        name = get_metric_name("HomeRuns", "en")
        assert isinstance(name, str)

    def test_get_metric_name_different_languages(self):
        """언어별로 다른 메트릭 이름 반환 확인"""
        name_ko = get_metric_name("HomeRuns", "ko")
        name_en = get_metric_name("HomeRuns", "en")
        name_ja = get_metric_name("HomeRuns", "ja")

        # 각 언어별로 결과가 있어야 함
        assert len(name_ko) > 0
        assert len(name_en) > 0
        assert len(name_ja) > 0

    def test_get_metric_name_default_language(self):
        """기본 언어로 메트릭 이름 조회"""
        name_default = get_metric_name("OPS")
        name_korean = get_metric_name("OPS", "ko")
        assert name_default == name_korean


class TestGetMetricNamesDict:
    """메트릭 이름 딕셔너리 조회 테스트"""

    def test_get_metric_names_dict_returns_dict(self):
        """딕셔너리를 반환하는지 확인"""
        metrics = ["BattingAverage", "HomeRuns", "RBIs"]
        result = get_metric_names_dict(metrics, "ko")
        assert isinstance(result, dict)

    def test_get_metric_names_dict_correct_keys(self):
        """요청한 메트릭 키들이 모두 포함되는지 확인"""
        metrics = ["BattingAverage", "HomeRuns", "RBIs"]
        result = get_metric_names_dict(metrics, "ko")

        for metric in metrics:
            assert metric in result

    def test_get_metric_names_dict_values_are_strings(self):
        """모든 값이 문자열인지 확인"""
        metrics = ["BattingAverage", "OPS", "EarnedRunAverage"]
        result = get_metric_names_dict(metrics, "en")

        for value in result.values():
            assert isinstance(value, str)
            assert len(value) > 0

    def test_get_metric_names_dict_empty_list(self):
        """빈 리스트를 전달하면 빈 딕셔너리 반환"""
        result = get_metric_names_dict([], "ko")
        assert isinstance(result, dict)
        assert len(result) == 0

    def test_get_metric_names_dict_different_languages(self):
        """언어별로 다른 메트릭 이름 딕셔너리 반환"""
        metrics = ["BattingAverage", "HomeRuns"]
        result_ko = get_metric_names_dict(metrics, "ko")
        result_en = get_metric_names_dict(metrics, "en")
        result_ja = get_metric_names_dict(metrics, "ja")

        # 모두 같은 키를 가져야 함
        assert set(result_ko.keys()) == set(metrics)
        assert set(result_en.keys()) == set(metrics)
        assert set(result_ja.keys()) == set(metrics)

    def test_get_metric_names_dict_default_language(self):
        """기본 언어로 메트릭 딕셔너리 조회"""
        metrics = ["OPS", "Wins"]
        result_default = get_metric_names_dict(metrics)
        result_korean = get_metric_names_dict(metrics, "ko")
        assert result_default == result_korean


@pytest.mark.parametrize("lang", ["ko", "en", "ja"])
class TestMultiLanguageSupport:
    """다국어 지원 통합 테스트"""

    def test_common_keys_available_in_all_languages(self, lang):
        """주요 키들이 모든 언어에서 사용 가능한지 확인"""
        common_keys = [
            "app_title",
            "search_player",
            "predict_performance",
            "trend_analysis",
        ]

        for key in common_keys:
            text = get_text(key, lang)
            assert isinstance(text, str)
            assert len(text) > 0

    def test_metric_names_available_in_all_languages(self, lang):
        """주요 메트릭 이름이 모든 언어에서 사용 가능한지 확인"""
        metrics = [
            "BattingAverage",
            "HomeRuns",
            "EarnedRunAverage",
            "Wins",
        ]

        for metric in metrics:
            name = get_metric_name(metric, lang)
            assert isinstance(name, str)
            assert len(name) > 0
