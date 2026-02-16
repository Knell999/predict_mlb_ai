"""품질 Agent 통합 테스트"""

import pytest
from unittest.mock import patch


@pytest.mark.agent
class TestQualityAgentGraph:
    """품질 Agent 그래프 통합 테스트"""

    def test_graph_compiles(self):
        from agents.quality import create_quality_agent
        agent = create_quality_agent()
        nodes = list(agent.get_graph().nodes.keys())
        assert "__start__" in nodes
        assert "validate_files" in nodes
        assert "detect_anomalies" in nodes
        assert "assemble_report" in nodes
        assert "__end__" in nodes

    def test_graph_has_anomaly_conditional(self):
        from agents.quality import create_quality_agent
        agent = create_quality_agent()
        nodes = list(agent.get_graph().nodes.keys())
        assert "interpret_anomalies" in nodes

    @patch("agents.tools.quality_tools.check_file_existence")
    @patch("agents.tools.quality_tools.check_data_structure")
    @patch("agents.tools.quality_tools.check_data_quality")
    @patch("agents.tools.quality_tools.detect_statistical_anomalies")
    def test_quality_check_no_anomalies_flow(self, mock_anomaly, mock_quality, mock_structure, mock_files):
        """이상치 없는 경우의 정상 플로우"""
        from agents.quality import create_quality_agent

        mock_files.invoke.return_value = {"batter_exists": True, "pitcher_exists": True}
        mock_structure.invoke.return_value = {"batter_valid": True, "pitcher_valid": True}
        mock_quality.invoke.return_value = {
            "batter": {"null_count": 0, "duplicate_count": 0},
            "pitcher": {"null_count": 0, "duplicate_count": 0},
        }
        mock_anomaly.invoke.return_value = []

        agent = create_quality_agent()
        result = agent.invoke({
            "file_check": {},
            "schema_validation": {},
            "range_violations": {},
            "anomalies": [],
            "anomaly_interpretations": [],
            "quality_score": 0.0,
            "report_markdown": "",
            "recommendations": [],
            "trigger": "manual",
            "lang": "ko",
            "error": None,
        })
        assert "report_markdown" in result
        assert result.get("quality_score", 0) > 0


@pytest.mark.agent
class TestSimilarityAgentGraph:
    """유사선수 Agent 그래프 통합 테스트"""

    def test_graph_compiles(self):
        from agents.similarity import create_similarity_agent
        agent = create_similarity_agent()
        nodes = list(agent.get_graph().nodes.keys())
        assert "__start__" in nodes
        assert "parse_criteria" in nodes
        assert "rank" in nodes
        assert "explain" in nodes
        assert "__end__" in nodes

    def test_graph_has_conditional_paths(self):
        from agents.similarity import create_similarity_agent
        agent = create_similarity_agent()
        nodes = list(agent.get_graph().nodes.keys())
        assert "from_player" in nodes
        assert "from_criteria" in nodes
