"""Agent 도구(Tools) 단위 테스트"""

import pytest
import pandas as pd


@pytest.mark.agent
class TestDataTools:
    """data_tools.py 도구 테스트"""

    def test_get_player_stats_batter(self, sample_batter_data, monkeypatch):
        from agents.tools.data_tools import get_player_stats

        monkeypatch.setattr("utils.load_data", lambda: sample_batter_data)
        result = get_player_stats.invoke({"player_name": "Shohei Ohtani", "player_type": "batter"})
        assert "error" not in result
        assert result["player_name"] == "Shohei Ohtani"
        assert result["seasons"] >= 1

    def test_get_player_stats_pitcher(self, sample_pitcher_data, monkeypatch):
        from agents.tools.data_tools import get_player_stats

        monkeypatch.setattr("utils.load_pitcher_data", lambda: sample_pitcher_data)
        result = get_player_stats.invoke({"player_name": "Gerrit Cole", "player_type": "pitcher"})
        assert "error" not in result
        assert result["player_name"] == "Gerrit Cole"

    def test_get_player_stats_not_found(self, sample_batter_data, monkeypatch):
        from agents.tools.data_tools import get_player_stats

        monkeypatch.setattr("utils.load_data", lambda: sample_batter_data)
        result = get_player_stats.invoke({"player_name": "Unknown Player", "player_type": "batter"})
        assert "error" in result

    def test_search_players(self, sample_batter_data, monkeypatch):
        from agents.tools.data_tools import search_players

        monkeypatch.setattr("utils.load_data", lambda: sample_batter_data)
        result = search_players.invoke({"query": "Ohtani", "player_type": "batter"})
        assert len(result) >= 1
        assert "Shohei Ohtani" in result

    def test_search_players_no_match(self, sample_batter_data, monkeypatch):
        from agents.tools.data_tools import search_players

        monkeypatch.setattr("utils.load_data", lambda: sample_batter_data)
        result = search_players.invoke({"query": "ZZZZZ", "player_type": "batter"})
        assert len(result) == 0

    def test_get_league_averages(self, sample_batter_data, monkeypatch):
        from agents.tools.data_tools import get_league_averages

        monkeypatch.setattr("utils.load_data", lambda: sample_batter_data)
        monkeypatch.setattr("utils.calculate_league_averages", lambda df, metrics: df.groupby("Season")[metrics].mean().reset_index())
        result = get_league_averages.invoke({
            "player_type": "batter",
            "metrics": ["BattingAverage", "OPS"],
        })
        assert isinstance(result, dict)
        assert "data" in result

    def test_get_player_season_stats(self, sample_batter_data, monkeypatch):
        from agents.tools.data_tools import get_player_season_stats

        monkeypatch.setattr("utils.load_data", lambda: sample_batter_data)
        result = get_player_season_stats.invoke({
            "player_name": "Aaron Judge",
            "season": 2023,
            "player_type": "batter",
        })
        assert "error" not in result
        assert result["Season"] == 2023


@pytest.mark.agent
class TestStatsTools:
    """stats_tools.py 도구 테스트"""

    def test_calculate_career_averages(self, sample_batter_data, monkeypatch):
        from agents.tools.stats_tools import calculate_career_averages

        monkeypatch.setattr("utils.load_data", lambda: sample_batter_data)
        result = calculate_career_averages.invoke({
            "player_name": "Shohei Ohtani",
            "player_type": "batter",
            "metrics": ["BattingAverage", "HomeRuns", "OPS"],
        })
        assert isinstance(result, dict)
        assert "BattingAverage" in result

    def test_compare_to_league(self, sample_batter_data, monkeypatch):
        from agents.tools.stats_tools import compare_to_league

        monkeypatch.setattr("utils.load_data", lambda: sample_batter_data)
        result = compare_to_league.invoke({
            "player_name": "Aaron Judge",
            "player_type": "batter",
            "season": 2023,
            "metrics": ["BattingAverage", "HomeRuns"],
        })
        assert isinstance(result, dict)
        assert "BattingAverage" in result
        assert "player" in result["BattingAverage"]

    def test_detect_trend(self, monkeypatch):
        """트렌드 감지는 최소 2시즌 데이터가 필요"""
        from agents.tools.stats_tools import detect_trend

        multi_season = pd.DataFrame({
            "Season": [2021, 2022, 2023, 2024],
            "PlayerName": ["Test"] * 4,
            "BattingAverage": [0.280, 0.290, 0.300, 0.310],
            "OPS": [0.800, 0.850, 0.900, 0.950],
        })
        monkeypatch.setattr("utils.load_data", lambda: multi_season)
        result = detect_trend.invoke({
            "player_name": "Test",
            "player_type": "batter",
            "metric": "BattingAverage",
        })
        assert "error" not in result
        assert result["direction"] in ["improving", "declining", "stable"]
        assert "slope" in result


@pytest.mark.agent
class TestSimilarityTools:
    """similarity_tools.py 도구 테스트"""

    def test_find_similar_players(self, sample_batter_data, monkeypatch):
        from agents.tools.similarity_tools import find_similar_players

        monkeypatch.setattr("utils.load_data", lambda: sample_batter_data)
        result = find_similar_players.invoke({
            "player_name": "Shohei Ohtani",
            "player_type": "batter",
            "metrics": ["BattingAverage", "OPS"],
            "season": 2023,
            "top_n": 3,
        })
        assert isinstance(result, list)

    def test_find_players_by_criteria(self, sample_batter_data, monkeypatch):
        from agents.tools.similarity_tools import find_players_by_criteria

        monkeypatch.setattr("utils.load_data", lambda: sample_batter_data)
        result = find_players_by_criteria.invoke({
            "player_type": "batter",
            "criteria": {"BattingAverage": {"min": 0.300}},
            "season": 2023,
            "top_n": 5,
        })
        assert isinstance(result, list)


@pytest.mark.agent
class TestPredictionTools:
    """prediction_tools.py 도구 테스트"""

    def test_assess_prediction_data_adequacy(self, monkeypatch):
        from agents.tools.prediction_tools import assess_prediction_data_adequacy

        multi_season = pd.DataFrame({
            "Season": [2020, 2021, 2022, 2023, 2024],
            "PlayerName": ["Test"] * 5,
            "OPS": [0.800, 0.850, 0.900, 0.880, 0.920],
        })
        monkeypatch.setattr("utils.load_data", lambda: multi_season)
        result = assess_prediction_data_adequacy.invoke({
            "player_name": "Test",
            "player_type": "batter",
        })
        assert isinstance(result, dict)
        assert "adequate" in result
        assert "total_seasons" in result


@pytest.mark.agent
class TestQualityTools:
    """quality_tools.py 도구 테스트"""

    def test_check_file_existence(self, sample_csv_files, monkeypatch):
        from agents.tools.quality_tools import check_file_existence
        from unittest.mock import MagicMock

        mock_checker = MagicMock()
        mock_checker.check_file_existence.return_value = {
            "batter_exists": True,
            "pitcher_exists": True,
        }
        monkeypatch.setattr(
            "data_quality_checker.DataQualityChecker",
            lambda: mock_checker,
        )
        result = check_file_existence.invoke({})
        assert isinstance(result, dict)
        assert result.get("batter_exists", False) is True

    def test_check_data_quality(self, sample_csv_files, monkeypatch):
        from agents.tools.quality_tools import check_data_quality
        from unittest.mock import MagicMock

        mock_checker = MagicMock()
        mock_checker.check_data_quality.return_value = {
            "batter": {"null_count": 0, "duplicate_count": 0},
            "pitcher": {"null_count": 0, "duplicate_count": 0},
        }
        monkeypatch.setattr(
            "data_quality_checker.DataQualityChecker",
            lambda: mock_checker,
        )
        result = check_data_quality.invoke({})
        assert isinstance(result, dict)
