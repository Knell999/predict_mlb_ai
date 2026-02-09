import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from streamlit_option_menu import option_menu
from utils import load_data, load_pitcher_data, get_plotly_config, apply_theme_to_figure
from i18n import get_text


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


# 이동평균 계산 함수
def calculate_moving_average(df, metrics, window):
    """
    특정 윈도우 크기의 이동평균을 계산하는 함수입니다.

    Args:
        df: 분석할 데이터프레임
        metrics: 계산할 지표들의 리스트
        window: 이동평균 윈도우 크기

    Returns:
        이동평균이 계산된 데이터프레임
    """
    moving_avg = df.copy()
    for metric in metrics:
        moving_avg[metric] = moving_avg[metric].rolling(window=window, min_periods=1).mean()
    return moving_avg


def create_animated_trend_chart(league_avg, metric, title, theme="plotly_white"):
    """
    애니메이션이 포함된 트렌드 차트를 생성합니다.

    Args:
        league_avg: 리그 평균 데이터
        metric: 표시할 지표
        title: 차트 제목
        theme: 차트 테마

    Returns:
        Plotly Figure 객체
    """
    # 애니메이션 프레임 생성
    frames = []
    for i in range(len(league_avg)):
        frame_data = league_avg.iloc[:i+1]
        frames.append(go.Frame(
            data=[go.Scatter(
                x=frame_data['Season'],
                y=frame_data[metric],
                mode='lines+markers',
                line=dict(color='#636EFA', width=3),
                marker=dict(size=8),
                name=metric
            )],
            name=str(league_avg.iloc[i]['Season'])
        ))

    # 초기 Figure 생성
    fig = go.Figure(
        data=[go.Scatter(
            x=league_avg['Season'][:1],
            y=league_avg[metric][:1],
            mode='lines+markers',
            line=dict(color='#636EFA', width=3),
            marker=dict(size=8),
            name=metric
        )],
        frames=frames
    )

    # 애니메이션 버튼 추가
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title="시즌",
        yaxis_title=metric,
        height=500,
        updatemenus=[
            {
                'type': 'buttons',
                'showactive': False,
                'buttons': [
                    {
                        'label': '▶️ 재생',
                        'method': 'animate',
                        'args': [None, {
                            'frame': {'duration': 500, 'redraw': True},
                            'fromcurrent': True,
                            'transition': {'duration': 300}
                        }]
                    },
                    {
                        'label': '⏸️ 정지',
                        'method': 'animate',
                        'args': [[None], {
                            'frame': {'duration': 0, 'redraw': False},
                            'mode': 'immediate',
                            'transition': {'duration': 0}
                        }]
                    }
                ],
                'x': 0.1,
                'xanchor': 'left',
                'y': 1.15,
                'yanchor': 'top'
            }
        ],
        sliders=[{
            'active': 0,
            'steps': [
                {
                    'args': [[f.name], {
                        'frame': {'duration': 0, 'redraw': True},
                        'mode': 'immediate',
                        'transition': {'duration': 0}
                    }],
                    'label': str(season),
                    'method': 'animate'
                }
                for f, season in zip(frames, league_avg['Season'])
            ],
            'x': 0.1,
            'len': 0.9,
            'xanchor': 'left',
            'y': 0,
            'yanchor': 'top'
        }]
    )

    # Y축 범위 고정
    fig.update_yaxes(range=[league_avg[metric].min() * 0.95, league_avg[metric].max() * 1.05])

    # 테마 적용
    fig = apply_theme_to_figure(fig, theme)

    return fig


def create_multi_line_chart(league_avg, metrics, title, theme="plotly_white"):
    """
    여러 지표를 한 차트에 표시하는 인터랙티브 차트를 생성합니다.
    """
    fig = go.Figure()

    colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3']

    for idx, metric in enumerate(metrics):
        fig.add_trace(go.Scatter(
            x=league_avg['Season'],
            y=league_avg[metric],
            mode='lines+markers',
            name=metric,
            line=dict(color=colors[idx % len(colors)], width=3),
            marker=dict(size=6),
            hovertemplate=f'<b>{metric}</b><br>시즌: %{{x}}<br>값: %{{y:.3f}}<extra></extra>'
        ))

    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title="시즌",
        yaxis_title="값",
        height=600,
        hovermode='x unified',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255, 255, 255, 0.8)"
        )
    )

    # 테마 적용
    fig = apply_theme_to_figure(fig, theme)

    return fig


def create_comparison_area_chart(league_avg, moving_avg_5, metric, title, theme="plotly_white"):
    """
    리그 평균과 이동평균을 비교하는 영역 차트를 생성합니다.
    """
    fig = go.Figure()

    # 리그 평균 라인
    fig.add_trace(go.Scatter(
        x=league_avg['Season'],
        y=league_avg[metric],
        mode='lines',
        name='리그 평균',
        line=dict(color='rgba(99, 110, 250, 0.8)', width=2),
        fill='tozeroy',
        fillcolor='rgba(99, 110, 250, 0.2)',
        hovertemplate='<b>리그 평균</b><br>시즌: %{x}<br>값: %{y:.3f}<extra></extra>'
    ))

    # 5년 이동평균 라인
    fig.add_trace(go.Scatter(
        x=moving_avg_5['Season'],
        y=moving_avg_5[metric],
        mode='lines',
        name='5년 이동평균',
        line=dict(color='rgba(239, 85, 59, 0.8)', width=3, dash='dash'),
        hovertemplate='<b>5년 이동평균</b><br>시즌: %{x}<br>값: %{y:.3f}<extra></extra>'
    ))

    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title="시즌",
        yaxis_title=metric,
        height=500,
        hovermode='x unified'
    )

    # 테마 적용
    fig = apply_theme_to_figure(fig, theme)

    return fig


# 타자와 투수의 리그 평균 계산
batting_metrics = ['BattingAverage', 'OnBasePercentage', 'SluggingPercentage', 'OPS', 'Hits', 'RBIs', 'HomeRuns', 'StolenBases']
pitching_metrics = ['EarnedRunAverage', 'Whip', 'Wins', 'StrikeOuts', 'InningsPitched']

df_batters = load_data()
df_pitchers = load_pitcher_data()

batting_league_avg = calculate_league_averages(df_batters, batting_metrics)
pitching_league_avg = calculate_league_averages(df_pitchers, pitching_metrics)

batting_moving_avg_5 = calculate_moving_average(batting_league_avg, batting_metrics, 5)
pitching_moving_avg_5 = calculate_moving_average(pitching_league_avg, pitching_metrics, 5)


def run_trend(lang="ko"):
    """리그 트렌드 분석 페이지를 실행합니다."""
    st.title(get_text("trend_title", lang))

    # 차트 테마 가져오기
    theme = st.session_state.get('chart_theme', 'plotly_white')

    # 메뉴 옵션
    menu_options = {
        'ko': ['타자 트렌드', '투수 트렌드'],
        'en': ['Batting Trends', 'Pitching Trends'],
        'ja': ['打者トレンド', '投手トレンド']
    }

    selected_lang_options = menu_options.get(lang, menu_options['ko'])

    selected = option_menu(
        None,
        selected_lang_options,
        icons=['graph-up', 'graph-down'],
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

    if selected == selected_lang_options[0]:  # 타자
        st.subheader("⚾ 타자 트렌드 분석")

        # 분석 모드 선택
        analysis_mode = st.radio(
            "분석 모드 선택",
            ["📊 단일 지표 애니메이션", "📈 다중 지표 비교", "🔄 이동평균 비교"],
            horizontal=True
        )

        if analysis_mode == "📊 단일 지표 애니메이션":
            st.info("💡 재생 버튼을 눌러 시즌별 변화를 애니메이션으로 확인하세요!")

            selected_metric = st.selectbox(
                "분석할 지표 선택",
                batting_metrics,
                format_func=lambda x: {
                    'BattingAverage': '타율',
                    'OnBasePercentage': '출루율',
                    'SluggingPercentage': '장타율',
                    'OPS': 'OPS',
                    'Hits': '안타',
                    'RBIs': '타점',
                    'HomeRuns': '홈런',
                    'StolenBases': '도루'
                }.get(x, x)
            )

            with st.spinner('애니메이션 차트 생성 중...'):
                fig = create_animated_trend_chart(
                    batting_league_avg,
                    selected_metric,
                    f"MLB 리그 {selected_metric} 변화 추이",
                    theme
                )

                st.plotly_chart(fig, use_container_width=True, config=get_plotly_config())

        elif analysis_mode == "📈 다중 지표 비교":
            selected_metrics = st.multiselect(
                "비교할 지표 선택 (최대 6개)",
                batting_metrics,
                default=['BattingAverage', 'OPS'],
                max_selections=6,
                format_func=lambda x: {
                    'BattingAverage': '타율',
                    'OnBasePercentage': '출루율',
                    'SluggingPercentage': '장타율',
                    'OPS': 'OPS',
                    'Hits': '안타',
                    'RBIs': '타점',
                    'HomeRuns': '홈런',
                    'StolenBases': '도루'
                }.get(x, x)
            )

            if selected_metrics:
                with st.spinner('다중 지표 차트 생성 중...'):
                    # 지표 정규화
                    normalized_data = batting_league_avg.copy()
                    for metric in selected_metrics:
                        normalized_data[metric] = (batting_league_avg[metric] - batting_league_avg[metric].min()) / (batting_league_avg[metric].max() - batting_league_avg[metric].min())

                    fig = create_multi_line_chart(
                        normalized_data,
                        selected_metrics,
                        "MLB 타자 지표 비교 (정규화)",
                        theme
                    )

                    st.plotly_chart(fig, use_container_width=True, config=get_plotly_config())

                    st.info("💡 정규화된 값(0-1)으로 표시되어 서로 다른 단위의 지표를 비교할 수 있습니다.")
            else:
                st.warning("비교할 지표를 하나 이상 선택해주세요.")

        else:  # 이동평균 비교
            selected_metric = st.selectbox(
                "분석할 지표 선택",
                batting_metrics,
                format_func=lambda x: {
                    'BattingAverage': '타율',
                    'OnBasePercentage': '출루율',
                    'SluggingPercentage': '장타율',
                    'OPS': 'OPS',
                    'Hits': '안타',
                    'RBIs': '타점',
                    'HomeRuns': '홈런',
                    'StolenBases': '도루'
                }.get(x, x)
            )

            with st.spinner('이동평균 차트 생성 중...'):
                fig = create_comparison_area_chart(
                    batting_league_avg,
                    batting_moving_avg_5,
                    selected_metric,
                    f"MLB {selected_metric} - 리그 평균 vs 이동평균",
                    theme
                )

                st.plotly_chart(fig, use_container_width=True, config=get_plotly_config())

                st.info("💡 이동평균은 단기 변동을 제거하고 장기 트렌드를 파악하는 데 유용합니다.")

    else:  # 투수
        st.subheader("⚾ 투수 트렌드 분석")

        # 분석 모드 선택
        analysis_mode = st.radio(
            "분석 모드 선택",
            ["📊 단일 지표 애니메이션", "📈 다중 지표 비교", "🔄 이동평균 비교"],
            horizontal=True
        )

        if analysis_mode == "📊 단일 지표 애니메이션":
            st.info("💡 재생 버튼을 눌러 시즌별 변화를 애니메이션으로 확인하세요!")

            selected_metric = st.selectbox(
                "분석할 지표 선택",
                pitching_metrics,
                format_func=lambda x: {
                    'EarnedRunAverage': '평균자책점',
                    'Whip': 'WHIP',
                    'Wins': '승수',
                    'StrikeOuts': '탈삼진',
                    'InningsPitched': '이닝'
                }.get(x, x)
            )

            with st.spinner('애니메이션 차트 생성 중...'):
                fig = create_animated_trend_chart(
                    pitching_league_avg,
                    selected_metric,
                    f"MLB 리그 {selected_metric} 변화 추이",
                    theme
                )

                st.plotly_chart(fig, use_container_width=True, config=get_plotly_config())

        elif analysis_mode == "📈 다중 지표 비교":
            selected_metrics = st.multiselect(
                "비교할 지표 선택 (최대 6개)",
                pitching_metrics,
                default=['EarnedRunAverage', 'Whip'],
                max_selections=6,
                format_func=lambda x: {
                    'EarnedRunAverage': '평균자책점',
                    'Whip': 'WHIP',
                    'Wins': '승수',
                    'StrikeOuts': '탈삼진',
                    'InningsPitched': '이닝'
                }.get(x, x)
            )

            if selected_metrics:
                with st.spinner('다중 지표 차트 생성 중...'):
                    # 지표 정규화
                    normalized_data = pitching_league_avg.copy()
                    for metric in selected_metrics:
                        normalized_data[metric] = (pitching_league_avg[metric] - pitching_league_avg[metric].min()) / (pitching_league_avg[metric].max() - pitching_league_avg[metric].min())

                    fig = create_multi_line_chart(
                        normalized_data,
                        selected_metrics,
                        "MLB 투수 지표 비교 (정규화)",
                        theme
                    )

                    st.plotly_chart(fig, use_container_width=True, config=get_plotly_config())

                    st.info("💡 정규화된 값(0-1)으로 표시되어 서로 다른 단위의 지표를 비교할 수 있습니다.")
            else:
                st.warning("비교할 지표를 하나 이상 선택해주세요.")

        else:  # 이동평균 비교
            selected_metric = st.selectbox(
                "분석할 지표 선택",
                pitching_metrics,
                format_func=lambda x: {
                    'EarnedRunAverage': '평균자책점',
                    'Whip': 'WHIP',
                    'Wins': '승수',
                    'StrikeOuts': '탈삼진',
                    'InningsPitched': '이닝'
                }.get(x, x)
            )

            with st.spinner('이동평균 차트 생성 중...'):
                fig = create_comparison_area_chart(
                    pitching_league_avg,
                    pitching_moving_avg_5,
                    selected_metric,
                    f"MLB {selected_metric} - 리그 평균 vs 이동평균",
                    theme
                )

                st.plotly_chart(fig, use_container_width=True, config=get_plotly_config())

                st.info("💡 이동평균은 단기 변동을 제거하고 장기 트렌드를 파악하는 데 유용합니다.")

    # 차트 사용 안내
    st.markdown("---")
    st.info("💡 **차트 사용법**: 차트 위에 마우스를 올리면 확대/축소, 다운로드 등의 기능을 사용할 수 있습니다.")


if __name__ == "__main__":
    run_trend()
