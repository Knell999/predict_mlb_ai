
import streamlit as st
import pandas as pd
from utils import load_data, load_pitcher_data
from i18n import get_text

def run_compare(lang):
    st.header(get_text("compare_players", lang))

    # 데이터 선택 (타자/투수)
    data_type = st.radio(
        get_text("select_data_type", lang),
        [get_text("batter", lang), get_text("pitcher", lang)],
        horizontal=True
    )

    if data_type == get_text("batter", lang):
        df = load_data()
        stats_options = ['BattingAverage', 'HomeRuns', 'RBIs', 'OPS', 'Hits', 'StolenBases']
    else:
        df = load_pitcher_data()
        stats_options = ['EarnedRunAverage', 'Wins', 'StrikeOuts', 'Whip', 'InningsPitched']

    if df is None or df.empty:
        st.warning(get_text("no_data_available", lang))
        return

    # 선수 선택
    player_names = sorted(df['PlayerName'].unique())
    
    col1, col2 = st.columns(2)
    with col1:
        player1 = st.selectbox(get_text("select_player_1", lang), player_names, index=0)
    with col2:
        player2 = st.selectbox(get_text("select_player_2", lang), player_names, index=1)

    # 비교할 스탯 선택
    selected_stats = st.multiselect(
        get_text("select_stats_to_compare", lang),
        options=stats_options,
        default=stats_options[:3]
    )

    if not selected_stats:
        st.info(get_text("select_stats_prompt", lang))
        return

    if player1 == player2:
        st.warning(get_text("select_different_players", lang))
        return

    # 데이터 비교
    player1_data = df[df['PlayerName'] == player1]
    player2_data = df[df['PlayerName'] == player2]

    st.subheader(f"{player1} vs {player2}")

    # 커리어 통산 스탯 비교
    st.write(f"**{get_text('career_summary', lang)}**")

    # 스탯 유형 정의
    cumulative_stats = ['HomeRuns', 'RBIs', 'Hits', 'StolenBases', 'Wins', 'StrikeOuts', 'InningsPitched', 'Walks', 'Losses', 'HitsAllowed']
    rate_stats = ['BattingAverage', 'OnBasePercentage', 'SluggingPercentage', 'OPS', 'EarnedRunAverage', 'Whip']

    # 커리어 스탯 계산 함수
    def calculate_career_stats(player_data, stats_to_calc):
        career_stats = {}
        for stat in stats_to_calc:
            if stat in cumulative_stats:
                career_stats[stat] = player_data[stat].sum()
            elif stat in rate_stats:
                career_stats[stat] = player_data[stat].mean()
        return pd.Series(career_stats)

    career_stats1 = calculate_career_stats(player1_data, selected_stats).rename(player1)
    career_stats2 = calculate_career_stats(player2_data, selected_stats).rename(player2)

    comparison_df = pd.concat([career_stats1, career_stats2], axis=1)
    st.dataframe(comparison_df.style.format("{:.3f}"))

    # 시즌별 스탯 비교 차트
    st.write(f"**{get_text('season_by_season', lang)}**")
    
    for stat in selected_stats:
        st.write(f"**{stat}**")
        chart_data = pd.DataFrame({
            'Season': player1_data['Season'],
            player1: player1_data[stat].values,
            player2: player2_data.set_index('Season').reindex(player1_data['Season'])[stat].values
        }).set_index('Season')
        
        st.line_chart(chart_data, color=["#0000FF", "#FF0000"])  # Player1: Blue, Player2: Red
