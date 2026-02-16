"""예측 Agent 통합 테스트"""

import pytest
from unittest.mock import patch


@pytest.mark.agent
class TestPredictionAgentGraph:
    """예측 Agent 그래프 통합 테스트"""

    def test_graph_compiles(self):
        from agents.prediction import create_prediction_agent
        agent = create_prediction_agent()
        nodes = list(agent.get_graph().nodes.keys())
        assert "__start__" in nodes
        assert "load_data" in nodes
        assert "evaluate_data" in nodes
        assert "__end__" in nodes

    def test_graph_has_conditional_path(self):
        from agents.prediction import create_prediction_agent
        agent = create_prediction_agent()
        nodes = list(agent.get_graph().nodes.keys())
        assert "context_analysis" in nodes
        assert "run_forecasts" in nodes
        assert "insufficient" in nodes

    @patch("agents.tools.prediction_tools.assess_prediction_data_adequacy")
    @patch("agents.tools.data_tools.get_player_stats")
    def test_insufficient_data_path(self, mock_stats, mock_assess):
        """데이터 부족 시 insufficient 경로 테스트"""
        from agents.prediction import create_prediction_agent

        mock_stats.invoke.return_value = {"player_name": "Test", "seasons": 1, "stats": {}}
        mock_assess.invoke.return_value = {"adequate": False, "total_seasons": 1, "reason": "시즌 수 부족"}

        agent = create_prediction_agent()
        result = agent.invoke({
            "player_name": "Test",
            "player_type": "batter",
            "metrics": ["OPS"],
            "prediction_years": 3,
            "data_adequate": False,
            "data_assessment": "",
            "player_age_curve": None,
            "similar_players_context": None,
            "forecasts": {},
            "interpretation": "",
            "confidence_assessment": "",
            "lang": "ko",
            "error": None,
        })
        assert result.get("data_adequate") is False
