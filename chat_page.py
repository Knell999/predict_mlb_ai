"""
AI 야구 분석 채팅 페이지
LangGraph 기반 대화형 Agent를 통해 선수 분석, 비교, 예측을 수행합니다.
"""

import streamlit as st
from i18n import get_text
from agents.base import is_llm_available


def _invoke_conversational_agent(user_message: str, lang: str) -> str:
    """대화형 Agent를 호출하고 응답을 반환합니다."""
    from langchain_core.messages import HumanMessage, AIMessage

    # 그래프 초기화 (세션에 캐시)
    if "agent_graph" not in st.session_state or st.session_state.agent_graph is None:
        from agents.conversational.graph import create_conversational_agent
        st.session_state.agent_graph = create_conversational_agent()

    agent = st.session_state.agent_graph

    # 이전 대화 이력 구성
    from config import CHAT_MAX_HISTORY
    history_messages = []
    for msg in st.session_state.chat_messages[-(CHAT_MAX_HISTORY * 2):]:
        if msg["role"] == "user":
            history_messages.append(HumanMessage(content=msg["content"]))
        else:
            history_messages.append(AIMessage(content=msg["content"]))

    # 현재 메시지 추가
    history_messages.append(HumanMessage(content=user_message))

    # Agent 호출
    result = agent.invoke({
        "messages": history_messages,
        "current_intent": "",
        "player_name": None,
        "player_names": None,
        "player_type": "batter",
        "lang": lang,
        "error": None,
    })

    # 마지막 AI 메시지 추출
    response_messages = result.get("messages", [])
    for msg in reversed(response_messages):
        if hasattr(msg, 'content') and isinstance(msg, AIMessage):
            return msg.content

    return get_text("agent_error", lang)


def run_chat(lang="ko"):
    """AI 야구 분석 채팅 페이지"""
    st.title("🤖 " + get_text("chat_title", lang))

    # 세션 상태 초기화
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "agent_graph" not in st.session_state:
        st.session_state.agent_graph = None

    # AI 가용성 체크
    if not is_llm_available():
        st.warning(get_text("ai_not_available", lang))
        with st.expander("🔧 " + get_text("ai_setup_guide", lang)):
            st.markdown("""
1. `.env` 파일에 API 키를 설정하세요:
```
GOOGLE_AI_API_KEY=your_api_key_here
```
2. [Google AI Studio](https://aistudio.google.com/apikey)에서 API 키를 발급받을 수 있습니다.
3. 앱을 재시작하세요.
            """)
        return

    # 사이드바: 빠른 질문 & 대화 초기화
    with st.sidebar:
        st.subheader("💡 " + get_text("quick_actions", lang))

        quick_questions = {
            "ko": [
                "Shohei Ohtani 분석해줘",
                "Mike Trout과 Aaron Judge 비교해줘",
                "Clayton Kershaw의 ERA 트렌드 분석해줘",
                "Mookie Betts의 향후 성적을 예측해줘",
            ],
            "en": [
                "Analyze Shohei Ohtani",
                "Compare Mike Trout and Aaron Judge",
                "Analyze Clayton Kershaw's ERA trend",
                "Predict Mookie Betts' future performance",
            ],
            "ja": [
                "大谷翔平を分析して",
                "Mike TroutとAaron Judgeを比較して",
                "Clayton KershawのERAトレンドを分析して",
                "Mookie Bettsの将来の成績を予測して",
            ],
        }

        for q in quick_questions.get(lang, quick_questions["ko"]):
            if st.button(q, key=f"quick_{q}", use_container_width=True):
                st.session_state.chat_messages.append({"role": "user", "content": q})
                st.rerun()

        st.markdown("---")
        if st.button("🗑️ " + get_text("clear_chat", lang), use_container_width=True):
            st.session_state.chat_messages = []
            st.session_state.agent_graph = None
            st.rerun()

    # 환영 메시지
    if not st.session_state.chat_messages:
        with st.chat_message("assistant"):
            st.markdown(get_text("chat_welcome", lang))

    # 대화 이력 표시
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 마지막 메시지가 user이고 아직 응답이 없으면 Agent 호출
    if (st.session_state.chat_messages
            and st.session_state.chat_messages[-1]["role"] == "user"):
        last_user_msg = st.session_state.chat_messages[-1]["content"]
        # 이미 응답이 있는지 확인
        needs_response = True
        if len(st.session_state.chat_messages) >= 2:
            if st.session_state.chat_messages[-1]["role"] != "user":
                needs_response = False

        if needs_response:
            with st.chat_message("assistant"):
                with st.spinner(get_text("agent_thinking", lang)):
                    try:
                        response = _invoke_conversational_agent(last_user_msg, lang)
                        st.markdown(response)
                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": response,
                        })
                    except Exception as e:
                        error_msg = f"{get_text('agent_error', lang)}: {str(e)}"
                        st.error(error_msg)
                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": error_msg,
                        })

    # 채팅 입력
    if prompt := st.chat_input(get_text("chat_placeholder", lang)):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        st.rerun()
