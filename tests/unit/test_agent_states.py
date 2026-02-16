"""Agent State TypedDict 검증 테스트"""

import pytest


@pytest.mark.agent
class TestConversationalState:
    def test_state_has_required_fields(self):
        from agents.conversational.state import ConversationalState
        annotations = ConversationalState.__annotations__
        assert "messages" in annotations
        assert "current_intent" in annotations
        assert "player_name" in annotations
        assert "lang" in annotations

    def test_state_instantiation(self):
        from agents.conversational.state import ConversationalState
        state = ConversationalState(
            messages=[],
            current_intent="general",
            player_name=None,
            player_names=None,
            player_type="batter",
            player_data=None,
            league_averages=None,
            lang="ko",
            error=None,
        )
        assert state["current_intent"] == "general"
        assert state["lang"] == "ko"


@pytest.mark.agent
class TestPredictionState:
    def test_state_has_required_fields(self):
        from agents.prediction.state import PredictionState
        annotations = PredictionState.__annotations__
        assert "player_name" in annotations
        assert "forecasts" in annotations
        assert "data_adequate" in annotations
        assert "confidence_assessment" in annotations

    def test_state_instantiation(self):
        from agents.prediction.state import PredictionState
        state = PredictionState(
            player_name="Test",
            player_type="batter",
            metrics=["OPS"],
            prediction_years=3,
            data_adequate=False,
            data_assessment="",
            player_age_curve=None,
            similar_players_context=None,
            forecasts={},
            interpretation="",
            confidence_assessment="",
            lang="ko",
            error=None,
        )
        assert state["player_name"] == "Test"


@pytest.mark.agent
class TestSimilarityState:
    def test_state_has_required_fields(self):
        from agents.similarity.state import SimilarityState
        annotations = SimilarityState.__annotations__
        assert "query" in annotations
        assert "target_player" in annotations
        assert "candidates" in annotations
        assert "explanation" in annotations


@pytest.mark.agent
class TestQualityState:
    def test_state_has_required_fields(self):
        from agents.quality.state import QualityState
        annotations = QualityState.__annotations__
        assert "file_check" in annotations
        assert "anomalies" in annotations
        assert "quality_score" in annotations
        assert "report_markdown" in annotations


@pytest.mark.agent
class TestUpdateState:
    def test_state_has_required_fields(self):
        from agents.update.state import UpdateState
        annotations = UpdateState.__annotations__
        assert "start_year" in annotations
        assert "end_year" in annotations
        assert "update_success" in annotations
        assert "retry_count" in annotations
        assert "failed_methods" in annotations


@pytest.mark.agent
class TestReportState:
    def test_state_has_required_fields(self):
        from agents.report.state import ReportState
        annotations = ReportState.__annotations__
        assert "player_name" in annotations
        assert "section_profile" in annotations
        assert "section_metrics" in annotations
        assert "full_report" in annotations
        assert "include_predictions" in annotations
