import streamlit as st


def run_search():
    # 선수 데이터 (추후 API로 만든 데이터프레임 형태로 구현필요)
    players_data = {
        "Mike Trout": {"타율": 0.304, "홈런": 45, "타점": 104},
        "Aaron Judge": {"타율": 0.287, "홈런": 52, "타점": 119},
        "Mookie Betts": {"타율": 0.319, "홈런": 32, "타점": 80},
        "Bryce Harper": {"타율": 0.276, "홈런": 35, "타점": 114},
        "Freddie Freeman": {"타율": 0.310, "홈런": 31, "타점": 102},
        "Fernando Tatis Jr.": {"타율": 0.285, "홈런": 42, "타점": 97},
    }

    # 선수 이름 리스트
    player_names = list(players_data.keys())

    # 제목
    st.title("MLB 선수 기록 조회 및 예측 서비스")

    # 검색창
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""

    search_query = st.text_input(
        "선수 이름을 입력하세요(영문):", st.session_state.search_query, key="search")

    # 검색어와 유사한 이름 찾기
    if search_query:
        suggestions = [
            name for name in player_names if search_query.lower() in name.lower()]
        if suggestions:
            st.subheader("비슷한 선수 이름:")
            for suggestion in suggestions:
                if st.button(suggestion):
                    st.session_state.search_query = suggestion
                    st.experimental_rerun()

    # 검색 결과 처리
    if st.session_state.search_query and st.session_state.search_query in players_data:
        st.subheader(f"{st.session_state.search_query}의 기록")
        player_stats = players_data[st.session_state.search_query]
        for stat, value in player_stats.items():
            st.write(f"{stat}: {value}")
    elif search_query:
        st.write("해당 선수의 기록을 찾을 수 없습니다.")
