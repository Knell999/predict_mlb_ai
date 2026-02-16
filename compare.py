import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import load_data, load_pitcher_data, get_plotly_config, apply_theme_to_figure, display_player_image
from i18n import get_text, get_metric_names_dict
from config import BATTER_METRIC_NAMES, PITCHER_METRIC_NAMES


def create_radar_chart(players_data, player_names, metrics, theme="plotly_white"):
    """
    레이더 차트로 여러 선수의 능력치를 비교합니다.

    Args:
        players_data: 선수들의 데이터 (리스트)
        player_names: 선수 이름 리스트
        metrics: 비교할 지표 리스트
        theme: 차트 테마

    Returns:
        Plotly Figure 객체
    """
    fig = go.Figure()

    colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A']

    for idx, (player_data, player_name) in enumerate(zip(players_data, player_names)):
        # 데이터 정규화 (0-1 범위)
        values = []
        for metric in metrics:
            val = player_data[metric].mean()
            values.append(val)

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=metrics,
            fill='toself',
            name=player_name,
            line=dict(color=colors[idx % len(colors)], width=2),
            opacity=0.7
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                showticklabels=True
            )
        ),
        title={
            'text': "선수 능력치 레이더 차트",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        height=600,
        showlegend=True
    )

    fig = apply_theme_to_figure(fig, theme)

    return fig


def create_comparison_bar_chart(players_data, player_names, metrics, theme="plotly_white"):
    """
    막대 차트로 선수들의 평균 스탯을 비교합니다.
    """
    fig = go.Figure()

    colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A']

    for idx, (player_data, player_name) in enumerate(zip(players_data, player_names)):
        values = [player_data[metric].mean() for metric in metrics]

        fig.add_trace(go.Bar(
            name=player_name,
            x=metrics,
            y=values,
            marker_color=colors[idx % len(colors)],
            hovertemplate=f'<b>{player_name}</b><br>%{{x}}: %{{y:.2f}}<extra></extra>'
        ))

    fig.update_layout(
        title={
            'text': "선수 스탯 비교",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title="지표",
        yaxis_title="평균값",
        barmode='group',
        height=500,
        hovermode='x unified'
    )

    fig = apply_theme_to_figure(fig, theme)

    return fig


def create_season_comparison_chart(players_data, player_names, metric, theme="plotly_white"):
    """
    시즌별 특정 지표의 변화를 선수별로 비교합니다.
    """
    fig = go.Figure()

    colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A']

    for idx, (player_data, player_name) in enumerate(zip(players_data, player_names)):
        fig.add_trace(go.Scatter(
            x=player_data['Season'],
            y=player_data[metric],
            mode='lines+markers',
            name=player_name,
            line=dict(color=colors[idx % len(colors)], width=3),
            marker=dict(size=8),
            hovertemplate=f'<b>{player_name}</b><br>시즌: %{{x}}<br>{metric}: %{{y:.2f}}<extra></extra>'
        ))

    fig.update_layout(
        title={
            'text': f"시즌별 {metric} 비교",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title="시즌",
        yaxis_title=metric,
        height=500,
        hovermode='x unified'
    )

    fig = apply_theme_to_figure(fig, theme)

    return fig


def run_compare(lang):
    st.header(get_text("compare_players", lang))

    # 차트 테마 가져오기
    theme = st.session_state.get('chart_theme', 'plotly_white')

    # 데이터 선택 (타자/투수)
    data_type = st.radio(
        get_text("select_data_type", lang),
        [get_text("batter", lang), get_text("pitcher", lang)],
        horizontal=True
    )

    if data_type == get_text("batter", lang):
        df = load_data()
        stats_options = get_metric_names_dict(list(BATTER_METRIC_NAMES.keys()), lang)
        player_type_key = "batter"
    else:
        df = load_pitcher_data()
        stats_options = get_metric_names_dict(list(PITCHER_METRIC_NAMES.keys()), lang)
        player_type_key = "pitcher"

    if df is None or df.empty:
        st.warning(get_text("no_data_available", lang))
        return

    # 비교 모드 선택
    comparison_mode = st.radio(
        "비교 모드",
        ["2명 비교", "다중 선수 비교 (최대 5명)"],
        horizontal=True
    )

    # 선수 선택
    player_names = sorted(df['PlayerName'].unique())

    if comparison_mode == "2명 비교":
        col1, col2 = st.columns(2)
        with col1:
            player1 = st.selectbox(get_text("select_player_1", lang), player_names, index=0)
        with col2:
            player2 = st.selectbox(get_text("select_player_2", lang), player_names, index=min(1, len(player_names)-1))

        selected_players = [player1, player2]

        if player1 == player2:
            st.warning(get_text("select_different_players", lang))
            return
    else:
        selected_players = st.multiselect(
            "비교할 선수 선택 (2-5명)",
            player_names,
            default=player_names[:2] if len(player_names) >= 2 else player_names,
            max_selections=5
        )

        if len(selected_players) < 2:
            st.warning("비교를 위해 최소 2명의 선수를 선택해주세요.")
            return

    # 비교할 스탯 선택
    selected_stats = st.multiselect(
        get_text("select_stats_to_compare", lang),
        options=list(stats_options.keys()),
        default=list(stats_options.keys())[:4],
        format_func=lambda x: stats_options[x]
    )

    if not selected_stats:
        st.info(get_text("select_stats_prompt", lang))
        return

    # 선수 데이터 로드
    players_data = []
    for player in selected_players:
        player_data = df[df['PlayerName'] == player]
        if not player_data.empty:
            players_data.append(player_data)

    if len(players_data) < 2:
        st.warning("선택한 선수들의 데이터가 부족합니다.")
        return

    # 선수 프로필 표시
    st.subheader("📊 선수 프로필")
    cols = st.columns(len(selected_players))
    for idx, (col, player, player_data) in enumerate(zip(cols, selected_players, players_data)):
        with col:
            if player_data.empty:
                continue
            player_id = player_data.iloc[0]['PlayerID']
            display_player_image(player_id, player, width=150)
            st.markdown(f"**{player}**")
            st.metric("통산 시즌", len(player_data))

    # 탭으로 구분
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 " + get_text("tab_stat_compare", lang),
        "🕸️ " + get_text("tab_radar_chart", lang),
        "📈 " + get_text("tab_season_trend", lang),
        "📋 " + get_text("tab_detail_data", lang),
        "🔍 " + get_text("similar_players_title", lang),
    ])

    with tab1:
        st.subheader("통계 비교 (평균)")

        with st.spinner('막대 차트 생성 중...'):
            fig = create_comparison_bar_chart(players_data, selected_players, selected_stats, theme)
            st.plotly_chart(fig, use_container_width=True, config=get_plotly_config())

        # 통계 테이블
        summary_data = []
        for player, player_data in zip(selected_players, players_data):
            row = {'선수': player}
            for stat in selected_stats:
                row[stats_options[stat]] = round(player_data[stat].mean(), 2)
            summary_data.append(row)

        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)

    with tab2:
        st.subheader("능력치 레이더 차트")
        st.info("💡 각 지표는 선수의 커리어 평균값으로 표시됩니다.")

        with st.spinner('레이더 차트 생성 중...'):
            fig = create_radar_chart(players_data, selected_players, selected_stats, theme)
            st.plotly_chart(fig, use_container_width=True, config=get_plotly_config())

    with tab3:
        st.subheader("시즌별 추이 비교")

        # 비교할 지표 선택
        trend_metric = st.selectbox(
            "추이를 볼 지표 선택",
            selected_stats,
            format_func=lambda x: stats_options[x]
        )

        with st.spinner('시즌별 차트 생성 중...'):
            fig = create_season_comparison_chart(players_data, selected_players, trend_metric, theme)
            st.plotly_chart(fig, use_container_width=True, config=get_plotly_config())

    with tab4:
        st.subheader("상세 데이터")

        for player, player_data in zip(selected_players, players_data):
            with st.expander(f"📋 {player} 상세 기록"):
                display_data = player_data[['Season'] + selected_stats].sort_values('Season', ascending=False)
                st.dataframe(display_data, use_container_width=True, height=300)

    with tab5:
        st.subheader("🔍 " + get_text("similar_players_title", lang))
        if selected_players:
            ref_player = st.selectbox(
                get_text("similarity_search", lang),
                selected_players,
                key="sim_ref_player",
            )
            if st.button("🔍 " + get_text("similarity_search", lang), key="sim_search_btn", use_container_width=True):
                from agents.base import is_llm_available
                with st.spinner(get_text("agent_thinking", lang)):
                    try:
                        from agents.similarity.graph import create_similarity_agent
                        agent = create_similarity_agent()
                        result = agent.invoke({
                            "query": ref_player,
                            "target_player": ref_player,
                            "target_metrics": None,
                            "player_type": player_type_key,
                            "season_filter": None,
                            "top_n": 10,
                            "similarity_metrics": list(selected_stats),
                            "candidates": [],
                            "explanation": "",
                            "lang": lang,
                            "error": None,
                        })
                        candidates = result.get("candidates", [])
                        if candidates:
                            import pandas as pd
                            sim_df = pd.DataFrame(candidates)
                            st.dataframe(sim_df, use_container_width=True)
                        if result.get("explanation"):
                            st.markdown(result["explanation"])
                        elif not candidates:
                            st.info(get_text("no_data_available", lang))
                    except Exception as e:
                        st.error(f"{get_text('agent_error', lang)}: {str(e)}")

    # 차트 사용 안내
    st.markdown("---")
    st.info("💡 " + get_text("chart_usage_tip", lang))


if __name__ == "__main__":
    run_compare("ko")
