import streamlit as st
import pandas as pd
from utils import load_data

# 데이터 로드
df = load_data()


def run_search():
    # 데이터프레임을 사용하여 선수 데이터 구성
    players_data = df.groupby(['PlayerName', 'Season']).agg({
        'GamesPlayed': 'sum',
        'BattingAverage': 'mean',
        'AtBats': 'sum',
        'Runs': 'sum',
        'Hits': 'sum',
        'HomeRuns': 'sum',
        'RBIs': 'sum',
        'StolenBases': 'sum',
        'OnBasePercentage': 'mean',
        'SluggingPercentage': 'mean',
        'Walks': 'sum',
        'StrikeOuts': 'sum',
        'OPS': 'mean'
    }).reset_index()

    # 선수 이름 리스트
    player_names = players_data['PlayerName'].unique()

    # 제목
    st.title("MLB 선수 기록 조회 및 예측 서비스")

    # 시즌 선택
    season = st.selectbox("시즌을 선택하세요:", options=sorted(df['Season'].unique()))

    # 검색창
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""

    search_query = st.text_input(
        "선수 이름을 입력하세요(영문):", st.session_state.search_query, key="search")

    # 선택한 시즌의 모든 선수 데이터 프레임 표시
    season_data = players_data[players_data['Season']
                               == season].reset_index(drop=True)
    season_data_styled = season_data.style.format({"Season": "{:.0f}",
                                                   'BattingAverage': '{:.3f}',
                                                   'OnBasePercentage': '{:.3f}',
                                                   'SluggingPercentage': '{:.3f}',
                                                   'OPS': '{:.3f}'})
    st.subheader(f"{season} 시즌 전체 선수 기록")
    st.dataframe(season_data_styled, height=600)

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
    if st.session_state.search_query:
        filtered_data = players_data[(players_data['PlayerName'] == st.session_state.search_query) & (
            players_data['Season'] == season)].reset_index(drop=True)
        if not filtered_data.empty:
            filtered_data_styled = filtered_data.style.format({"Season": "{:.0f}",
                                                               'BattingAverage': '{:.3f}',
                                                               'OnBasePercentage': '{:.3f}',
                                                               'SluggingPercentage': '{:.3f}'})  # 천 단위 구분기호 제거
            st.subheader(f"{st.session_state.search_query}의 {season} 시즌 기록")
            # 데이터 프레임 전체를 인덱스 숨김 상태로 표시
            st.dataframe(filtered_data_styled, height=400)
        else:
            st.write(f"{season} 시즌에 대한 해당 선수의 기록을 찾을 수 없습니다.")
    elif search_query:
        st.write("해당 선수의 기록을 찾을 수 없습니다.")


if __name__ == "__main__":
    run_search()
