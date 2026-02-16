"""대화형 분석 Agent 통합 테스트"""

import pytest
from unittest.mock import patch, MagicMock


class MockLLMResponse:
    def __init__(self, content):
        self.content = content


@pytest.mark.agent
class TestConversationalAgentGraph:
    """대화형 Agent 그래프 통합 테스트"""

    def test_graph_compiles(self):
        from agents.conversational import create_conversational_agent
        agent = create_conversational_agent()
        nodes = list(agent.get_graph().nodes.keys())
        assert "__start__" in nodes
        assert "router" in nodes
        assert "synthesize" in nodes
        assert "__end__" in nodes

    def test_graph_has_all_intent_nodes(self):
        from agents.conversational import create_conversational_agent
        agent = create_conversational_agent()
        nodes = list(agent.get_graph().nodes.keys())
        for intent_node in ["profile", "compare", "trend", "predict", "root_cause", "general"]:
            assert intent_node in nodes, f"Missing node: {intent_node}"

    @patch("agents.conversational.nodes.create_llm")
    def test_general_conversation_flow(self, mock_create_llm, sample_batter_data):
        """LLM 없이 일반 대화 플로우 테스트"""
        from agents.conversational import create_conversational_agent
        from langchain_core.messages import HumanMessage

        mock_create_llm.return_value = None

        agent = create_conversational_agent()
        result = agent.invoke({
            "messages": [HumanMessage(content="야구에 대해 알려줘")],
            "current_intent": "",
            "player_name": None,
            "player_names": None,
            "player_type": "batter",
            "player_data": None,
            "league_averages": None,
            "lang": "ko",
            "error": None,
        })
        assert "messages" in result
        assert len(result["messages"]) > 0


@pytest.mark.agent
class TestConversationalAgentIntents:
    """의도(intent) 라우팅 테스트"""

    @patch("agents.conversational.nodes.create_llm")
    def test_router_returns_valid_intent(self, mock_create_llm):
        from agents.conversational.nodes import router_node
        from langchain_core.messages import HumanMessage

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MockLLMResponse('{"intent": "profile", "player_name": "Trout"}')
        mock_create_llm.return_value = mock_llm

        state = {
            "messages": [HumanMessage(content="Mike Trout 분석해줘")],
            "lang": "ko",
        }
        result = router_node(state)
        assert result["current_intent"] in ["profile", "compare", "trend", "predict", "root_cause", "general"]
