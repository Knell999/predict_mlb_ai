"""Agent 노드 함수 단위 테스트 (LLM 모킹)"""

import pytest
from unittest.mock import MagicMock, patch


class MockLLMResponse:
    """LLM 응답 모킹"""
    def __init__(self, content="Mock LLM response"):
        self.content = content


@pytest.mark.agent
class TestReportNodes:
    """리포트 Agent 노드 테스트"""

    def test_plan_sections_node(self):
        from agents.report.nodes import plan_sections_node
        state = {"report_type": "full", "player_name": "Mike Trout"}
        result = plan_sections_node(state)
        assert "report_title" in result
        assert "Mike Trout" in result["report_title"]

    def test_assemble_report_node(self):
        from agents.report.nodes import assemble_report_node
        state = {
            "report_title": "Test Report",
            "section_profile": "## Profile\nTest profile",
            "section_metrics": "## Metrics\nTest metrics",
            "section_trends": "## Trends\nTest trends",
            "section_predictions": "",
            "section_comparisons": "## Comparisons\nTest comparisons",
        }
        result = assemble_report_node(state)
        assert "full_report" in result
        report = result["full_report"]
        assert "Test Report" in report
        assert "Profile" in report
        assert "Metrics" in report

    def test_assemble_report_with_predictions(self):
        from agents.report.nodes import assemble_report_node
        state = {
            "report_title": "Test",
            "section_profile": "profile",
            "section_metrics": "metrics",
            "section_trends": "trends",
            "section_predictions": "predictions section here",
            "section_comparisons": "comparisons",
        }
        result = assemble_report_node(state)
        assert "predictions section here" in result["full_report"]

    @patch("agents.report.nodes.create_llm")
    def test_gen_profile_node_no_llm(self, mock_create_llm):
        from agents.report.nodes import gen_profile_node
        mock_create_llm.return_value = None
        state = {
            "lang": "ko",
            "player_data": {"seasons": 10, "season_range": [2015, 2024]},
            "player_name": "Mike Trout",
        }
        result = gen_profile_node(state)
        assert "section_profile" in result

    @patch("agents.report.nodes.create_llm")
    def test_gen_profile_node_with_llm(self, mock_create_llm):
        from agents.report.nodes import gen_profile_node
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MockLLMResponse("## 선수 프로파일\nMike Trout은 뛰어난 선수입니다.")
        mock_create_llm.return_value = mock_llm
        state = {
            "lang": "ko",
            "player_data": {"seasons": 10, "season_range": [2015, 2024]},
            "player_name": "Mike Trout",
        }
        result = gen_profile_node(state)
        assert "section_profile" in result
        assert "Mike Trout" in result["section_profile"]


@pytest.mark.agent
class TestUpdateNodes:
    """업데이트 Agent 노드 테스트"""

    def test_select_source_auto_first_try(self):
        from agents.update.nodes import select_source_node
        state = {"method": "auto", "failed_methods": []}
        result = select_source_node(state)
        assert result["selected_method"] == "pybaseball"

    def test_select_source_auto_pybaseball_failed(self):
        from agents.update.nodes import select_source_node
        state = {"method": "auto", "failed_methods": ["pybaseball"]}
        result = select_source_node(state)
        assert result["selected_method"] == "mlb-api"

    def test_select_source_all_failed(self):
        from agents.update.nodes import select_source_node
        state = {"method": "auto", "failed_methods": ["pybaseball", "mlb-api"]}
        result = select_source_node(state)
        assert result["selected_method"] == "none"
        assert "error" in result

    def test_select_source_user_specified(self):
        from agents.update.nodes import select_source_node
        state = {"method": "mlb-api", "failed_methods": []}
        result = select_source_node(state)
        assert result["selected_method"] == "mlb-api"

    def test_report_failure_node(self):
        from agents.update.nodes import report_failure_node
        state = {"failed_methods": ["pybaseball", "mlb-api"], "retry_count": 2, "error": "테스트 에러"}
        result = report_failure_node(state)
        assert "status_report" in result
        assert "실패" in result["status_report"]

    def test_generate_report_node_success(self):
        from agents.update.nodes import generate_report_node
        state = {
            "update_steps": [
                {"step": "backup", "status": "completed"},
                {"step": "update", "status": "completed"},
            ],
            "quality_report": {"stats": {}},
            "update_success": True,
            "selected_method": "pybaseball",
            "start_year": 2024,
            "end_year": 2025,
        }
        result = generate_report_node(state)
        assert "status_report" in result
        assert "성공" in result["status_report"]


@pytest.mark.agent
class TestQualityNodes:
    """품질 Agent 노드 테스트"""

    @patch("agents.tools.quality_tools.check_file_existence")
    def test_validate_files_node(self, mock_check):
        from agents.quality.nodes import validate_files_node
        mock_check.invoke.return_value = {"batter_exists": True, "pitcher_exists": True}
        state = {}
        result = validate_files_node(state)
        assert "file_check" in result

    def test_assemble_report_node_no_anomalies(self):
        from agents.quality.nodes import assemble_report_node
        state = {
            "file_check": {"batter_exists": True, "pitcher_exists": True},
            "schema_validation": {"batter_valid": True, "pitcher_valid": True},
            "range_violations": {},
            "anomalies": [],
            "anomaly_interpretations": [],
            "lang": "ko",
        }
        result = assemble_report_node(state)
        assert "report_markdown" in result
        assert "quality_score" in result
        assert result["quality_score"] > 0


@pytest.mark.agent
class TestConversationalNodes:
    """대화형 Agent 노드 테스트"""

    @patch("agents.conversational.nodes.create_llm")
    def test_general_node_no_llm(self, mock_create_llm):
        from agents.conversational.nodes import general_node
        from langchain_core.messages import HumanMessage
        mock_create_llm.return_value = None
        state = {
            "messages": [HumanMessage(content="안녕하세요")],
            "lang": "ko",
        }
        result = general_node(state)
        assert "messages" in result

    @patch("agents.conversational.nodes.create_llm")
    def test_router_node_no_llm(self, mock_create_llm):
        from agents.conversational.nodes import router_node
        from langchain_core.messages import HumanMessage
        mock_create_llm.return_value = None
        state = {
            "messages": [HumanMessage(content="Mike Trout 분석해줘")],
            "lang": "ko",
        }
        result = router_node(state)
        assert "current_intent" in result
        assert result["current_intent"] == "general"
