import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from streamlit_option_menu import option_menu
from utils import load_data, load_pitcher_data, get_plotly_layout_config, get_plotly_config, display_player_image
from i18n import get_text
from player_analysis_ai import PlayerAnalysisAI, is_ai_analysis_available, get_ai_analysis_status

df = load_data()
df_pitchers = load_pitcher_data()

# 리그 평균 계산 함수
def calculate_league_averages(df, metrics):
    """
    시즌별 리그 평균을 계산하는 함수입니다.

    Args:
        df: 분석할 데이터프레임
        metrics: 계산할 지표들의 리스트

    Returns:
        시즌별로 그룹화된 리그 평균 데이터프레임
    """
    league_averages = df.groupby('Season')[metrics].mean().reset_index()
    return league_averages

# 타자와 투수의 리그 평균 계산
batting_metrics = ['BattingAverage', 'OnBasePercentage', 'SluggingPercentage', 'OPS', 'Hits', 'RBIs', 'HomeRuns', 'StolenBases', 'Walks', 'StrikeOuts']
pitching_metrics = ['EarnedRunAverage', 'Whip', 'Wins', 'Losses', 'StrikeOuts', 'InningsPitched', 'Walks', 'HitsAllowed']

batting_league_avg = calculate_league_averages(df, batting_metrics)
pitching_league_avg = calculate_league_averages(df_pitchers, pitching_metrics)

def create_interactive_charts(player_data, league_avg, metrics, player_name, player_type):
    """
    Plotly를 사용하여 인터랙티브 차트를 생성합니다.

    Args:
        player_data: 선수 데이터
        league_avg: 리그 평균 데이터
        metrics: 표시할 지표 리스트
        player_name: 선수 이름
        player_type: '타자' 또는 '투수'
    """
    # 지표를 2개씩 묶어서 서브플롯 생성
    num_rows = (len(metrics) + 1) // 2

    fig = make_subplots(
        rows=num_rows,
        cols=2,
        subplot_titles=[f"{metric}" for metric in metrics],
        vertical_spacing=0.12,
        horizontal_spacing=0.15
    )

    colors = px.colors.qualitative.Plotly

    for idx, metric in enumerate(metrics):
        row = idx // 2 + 1
        col = idx % 2 + 1

        # 선수 데이터 라인
        fig.add_trace(
            go.Scatter(
                x=player_data['Season'],
                y=player_data[metric],
                mode='lines+markers',
                name=f'{player_name}',
                line=dict(color=colors[0], width=3),
                marker=dict(size=8),
                hovertemplate=f'<b>{player_name}</b><br>시즌: %{{x}}<br>{metric}: %{{y}}<extra></extra>',
                legendgroup='player',
                showlegend=(idx == 0)
            ),
            row=row, col=col
        )

        # 리그 평균 라인
        league_data_filtered = league_avg[league_avg['Season'].isin(player_data['Season'])]
        fig.add_trace(
            go.Scatter(
                x=league_data_filtered['Season'],
                y=league_data_filtered[metric],
                mode='lines+markers',
                name='리그 평균',
                line=dict(color=colors[1], width=2, dash='dash'),
                marker=dict(size=6),
                hovertemplate=f'<b>리그 평균</b><br>시즌: %{{x}}<br>{metric}: %{{y}}<extra></extra>',
                legendgroup='league',
                showlegend=(idx == 0)
            ),
            row=row, col=col
        )

        # 축 레이블 업데이트
        fig.update_xaxes(title_text="시즌", row=row, col=col, showgrid=True, gridcolor='lightgray')
        fig.update_yaxes(title_text=metric, row=row, col=col, showgrid=True, gridcolor='lightgray')

    # 레이아웃 업데이트
    fig.update_layout(
        title={
            'text': f"{player_name}의 시즌별 성적 변화 ({player_type})",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        height=400 * num_rows,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='closest',
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    return fig

def create_comparison_bar_chart(player_data, league_data, metrics, player_name, season):
    """
    선수와 리그 평균을 비교하는 막대 차트를 생성합니다.
    """
    player_values = player_data[metrics].values.flatten()
    league_values = league_data[metrics].mean().values.flatten()

    fig = go.Figure(data=[
        go.Bar(
            name=player_name,
            x=metrics,
            y=player_values,
            marker_color='steelblue',
            hovertemplate='<b>%{x}</b><br>값: %{y}<extra></extra>'
        ),
        go.Bar(
            name='리그 평균',
            x=metrics,
            y=league_values,
            marker_color='lightcoral',
            hovertemplate='<b>%{x}</b><br>값: %{y}<extra></extra>'
        )
    ])

    fig.update_layout(
        title={
            'text': f'{player_name} vs 리그 평균 ({season})',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title='지표',
        yaxis_title='값',
        barmode='group',
        height=500,
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    return fig

def run_search(lang="ko"):
    """MLB 선수 기록을 조회하고 시각화하는 함수입니다."""
    st.title(get_text("search_title", lang))

    menu_options = {
        'ko': ['타자(선수기준)', '타자(시즌기준)', '투수(선수기준)', '투수(시즌기준)'],
        'en': ['Batters (By Player)', 'Batters (By Season)', 'Pitchers (By Player)', 'Pitchers (By Season)'],
        'ja': ['打者(選手基準)', '打者(シーズン基準)', '投手(選手基準)', '投手(シーズン基準)']
    }

    selected_lang_options = menu_options.get(lang, menu_options['ko'])

    selected = option_menu(
        None,
        selected_lang_options,
        icons=['person-fill', 'calendar-date', 'person', 'calendar'],
        menu_icon='cast',
        default_index=0,
        orientation='horizontal',
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "blue", "font-size": "20px"},
            "nav-link": {"font-size": "15px", "text-align": "center", "margin": "0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#4CAF50"},
        }
    )

    def view_player_stats(data, league_avg, player_type, metrics, season=None):
        if season:
            data = data[data['Season'] == season]
            league_avg = league_avg[league_avg['Season'] == season]

        player_names = [""] + sorted(data['PlayerName'].unique())
        player = st.selectbox(get_text('select_player', lang), player_names, index=0)

        if player:
            with st.spinner('선수 데이터를 불러오는 중...'):
                player_data = data[data['PlayerName'] == player].sort_values(by='Season')
                player_data_styled = player_data.style.format(precision=3)

                if player_type == '투수':
                    player_data_styled = player_data.style.format({
                        "EarnedRunAverage": "{:.2f}",
                        "Whip": "{:.2f}",
                        "InningsPitched": "{:.1f}"
                    })

            if not player_data.empty:
                player_id = player_data.iloc[0]['PlayerID']

                col1, col2 = st.columns([1, 2])

                with col1:
                    display_player_image(player_id, player, width=200)

                with col2:
                    st.markdown(f"### {player}")
                    if season:
                        st.markdown(f"**{season} 시즌**")

                    # 주요 통계 요약
                    if player_type == '타자':
                        st.metric("통산 시즌", len(player_data))
                        avg_ops = player_data['OPS'].mean()
                        st.metric("평균 OPS", f"{avg_ops:.3f}")
                    else:
                        st.metric("통산 시즌", len(player_data))
                        avg_era = player_data['EarnedRunAverage'].mean()
                        st.metric("평균 ERA", f"{avg_era:.2f}")

                st.dataframe(player_data_styled, height=min(400, 50 + 35 * len(player_data)), use_container_width=True)

                st.subheader("📊 선수 기록 인터랙티브 시각화")

                with st.spinner('차트를 생성하는 중...'):
                    if player_type == '타자':
                        metrics_to_display = batting_metrics
                    else:
                        metrics_to_display = pitching_metrics

                    # Plotly 인터랙티브 차트 생성
                    fig = create_interactive_charts(
                        player_data,
                        league_avg,
                        metrics_to_display,
                        player,
                        player_type
                    )

                    st.plotly_chart(fig, use_container_width=True, config=get_plotly_config())

                    # 차트 다운로드 안내
                    st.info("💡 차트 위에 마우스를 올리면 확대/축소, 다운로드 등의 기능을 사용할 수 있습니다.")

                # AI 분석 기능
                st.markdown("---")

                if is_ai_analysis_available():
                    st.subheader("🤖 AI 기반 선수 분석 보고서")

                    if st.button(f"✨ {player} AI 분석 보고서 생성", key=f"ai_analysis_{player}", use_container_width=True):
                        with st.spinner("🤖 AI가 선수 기록을 분석 중입니다... (30초 소요)"):
                            try:
                                # 프로그레스 바
                                progress_bar = st.progress(0)
                                progress_bar.progress(20)

                                ai_analyzer = PlayerAnalysisAI()
                                progress_bar.progress(40)

                                # 언어 매핑
                                lang_mapping = {"ko": "한국어", "en": "영어", "ja": "일본어"}
                                analysis_lang = lang_mapping.get(lang, "한국어")

                                progress_bar.progress(60)

                                # AI 분석 실행
                                analysis_report = ai_analyzer.generate_player_analysis(
                                    player_name=player,
                                    player_data=player_data,
                                    league_averages=league_avg,
                                    player_type=player_type,
                                    language=analysis_lang
                                )

                                progress_bar.progress(100)

                                # 분석 결과 표시
                                st.success("✅ AI 분석이 완료되었습니다!")
                                st.markdown("### 📊 AI 분석 보고서")
                                st.markdown(analysis_report)

                                # 보고서 다운로드 옵션
                                col1, col2 = st.columns([1, 4])
                                with col1:
                                    st.download_button(
                                        label="📥 다운로드",
                                        data=analysis_report,
                                        file_name=f"{player}_analysis_report.md",
                                        mime="text/markdown",
                                        use_container_width=True
                                    )

                            except Exception as e:
                                st.error(f"❌ AI 분석 중 오류가 발생했습니다: {str(e)}")
                else:
                    # AI 기능 사용 불가 시 상태 표시
                    with st.expander("💡 AI 분석 기능 안내"):
                        ai_status = get_ai_analysis_status()
                        if not ai_status["langchain_available"]:
                            st.warning("AI 분석 기능을 사용하려면 LangChain을 설치하세요:")
                            st.code("pip install langchain langchain-google-genai")
                        elif not ai_status["api_key_configured"]:
                            st.warning("AI 분석 기능을 사용하려면 환경변수를 설정하세요:")
                            st.code("export GOOGLE_AI_API_KEY='your_api_key_here'")
            else:
                st.warning(f"❌ 해당 선수의 기록을 찾을 수 없습니다.")

    def view_player_stats_by_season(data, league_avg, player_type, metrics, season):
        player_names = [""] + sorted(data['PlayerName'].unique())
        player = st.selectbox('선수를 선택하세요:', player_names, index=0)

        if player and season:
            with st.spinner('선수 데이터를 불러오는 중...'):
                player_data = data[(data['PlayerName'] == player) & (data['Season'] == season)]
                league_data = league_avg[league_avg['Season'] == season]

            if not player_data.empty:
                player_id = player_data.iloc[0]['PlayerID']

                col1, col2 = st.columns([1, 2])

                with col1:
                    display_player_image(player_id, player, width=200)

                with col2:
                    st.markdown(f"### {player}")
                    st.markdown(f"**{season} 시즌**")

                player_data_styled = player_data.style.format(precision=3)
                if player_type == '투수':
                    player_data_styled = player_data.style.format({
                        "EarnedRunAverage": "{:.2f}",
                        "Whip": "{:.2f}",
                        "InningsPitched": "{:.1f}"
                    })

                st.dataframe(player_data_styled, height=min(400, 50 + 35 * len(player_data)), use_container_width=True)

                st.subheader("📊 선수와 리그 평균 비교")

                with st.spinner('비교 차트를 생성하는 중...'):
                    fig = create_comparison_bar_chart(player_data, league_data, metrics, player, season)
                    st.plotly_chart(fig, use_container_width=True, config=get_plotly_config())

                    st.info("💡 차트 위에 마우스를 올리면 확대/축소, 다운로드 등의 기능을 사용할 수 있습니다.")
            else:
                st.warning(f"❌ 해당 시즌에 대한 선수의 기록을 찾을 수 없습니다.")

    def view_bat_stats(season=None):
        view_player_stats(df, batting_league_avg, "타자", batting_metrics, season)

    def view_pit_stats(season=None):
        view_player_stats(df_pitchers, pitching_league_avg, "투수", pitching_metrics, season)

    def view_bat_stats_by_season(season):
        view_player_stats_by_season(df, batting_league_avg, "타자", batting_metrics, season)

    def view_pit_stats_by_season(season):
        view_player_stats_by_season(df_pitchers, pitching_league_avg, "투수", pitching_metrics, season)

    # 메뉴 선택에 따른 처리 (다국어 지원)
    if selected == selected_lang_options[0]:  # 타자(선수기준)
        view_bat_stats()
    elif selected == selected_lang_options[1]:  # 타자(시즌기준)
        season = st.selectbox("시즌을 선택하세요:", options=sorted(df['Season'].unique(), reverse=True))
        view_bat_stats_by_season(season)
    elif selected == selected_lang_options[2]:  # 투수(선수기준)
        view_pit_stats()
    elif selected == selected_lang_options[3]:  # 투수(시즌기준)
        season = st.selectbox("시즌을 선택하세요:", options=sorted(df_pitchers['Season'].unique(), reverse=True))
        view_pit_stats_by_season(season)

if __name__ == "__main__":
    run_search()
