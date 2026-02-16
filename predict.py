import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from prophet import Prophet
from utils import load_data, load_pitcher_data, get_plotly_config, display_player_image
from streamlit_option_menu import option_menu
from i18n import get_text, get_metric_names_dict
from config import PREDICT_BATTER_METRICS, PREDICT_PITCHER_METRICS


@st.cache_data(ttl=3600)
def get_prophet_forecast(data, metric, periods=5):
    """
    Prophet 모델을 학습하고 예측을 수행합니다.
    Streamlit 캐싱을 통해 반복 학습을 방지합니다.
    """
    try:
        df_metric = data[['Season', metric]].copy()
        df_metric.columns = ['ds', 'y']

        model = Prophet(
            yearly_seasonality=False,
            weekly_seasonality=False,
            daily_seasonality=False
        )
        model.fit(df_metric)

        future = model.make_future_dataframe(periods=periods, freq='Y')
        forecast = model.predict(future)
        return forecast
    except Exception as e:
        return None


def create_prediction_plot(player_data, forecast, metric, player_name, lang="ko"):
    """
    Plotly를 사용하여 예측 차트를 생성합니다.

    Args:
        player_data: 선수 실제 데이터
        forecast: Prophet 예측 결과
        metric: 예측한 지표명
        player_name: 선수 이름
        lang: 언어 코드
    """
    # 실제 데이터와 예측 데이터 분리
    actual_years = player_data['ds'].dt.year
    future_forecast = forecast[forecast['ds'] > player_data['ds'].max()]
    future_years = future_forecast['ds'].dt.year

    # Figure 생성
    fig = go.Figure()

    # 실제 데이터 라인
    fig.add_trace(go.Scatter(
        x=actual_years,
        y=player_data['y'],
        mode='lines+markers',
        name='실제 기록',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=10, symbol='circle'),
        hovertemplate='<b>시즌:</b> %{x}<br><b>실제값:</b> %{y:.2f}<extra></extra>'
    ))

    # 예측 데이터 라인
    fig.add_trace(go.Scatter(
        x=future_years,
        y=future_forecast['yhat'],
        mode='lines+markers',
        name='예측',
        line=dict(color='#ff7f0e', width=3, dash='dash'),
        marker=dict(size=10, symbol='diamond'),
        hovertemplate='<b>시즌:</b> %{x}<br><b>예측값:</b> %{y:.2f}<extra></extra>'
    ))

    # 신뢰 구간 (95%)
    fig.add_trace(go.Scatter(
        x=list(future_years) + list(future_years[::-1]),
        y=list(future_forecast['yhat_upper']) + list(future_forecast['yhat_lower'][::-1]),
        fill='toself',
        fillcolor='rgba(255, 127, 14, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='95% 신뢰 구간',
        hoverinfo='skip',
        showlegend=True
    ))

    # 레이아웃 업데이트
    fig.update_layout(
        title={
            'text': f"{player_name}의 {metric} 5년 예측",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title="시즌",
        yaxis_title=metric,
        height=500,
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    fig.update_xaxes(showgrid=True, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridcolor='lightgray')

    return fig


def run_predict(lang="ko"):
    """선수별 기록을 입력받아 미래 시즌의 성적을 예측하고 시각화합니다."""
    st.title(get_text('predict_title', lang))

    # 다국어 메뉴 옵션 정의
    menu_options = {
        'ko': ['타자', '투수'],
        'en': ['Batters', 'Pitchers'],
        'ja': ['打者', '投手']
    }

    selected_lang_options = menu_options.get(lang, menu_options['ko'])

    selected = option_menu(
        None,
        selected_lang_options,
        icons=['person', 'ball'],
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

    # 언어에 따른 메뉴 옵션 매핑
    batter_options = {'ko': '타자', 'en': 'Batters', 'ja': '打者'}
    batter_option = batter_options.get(lang, '타자')

    if selected == batter_option:
        df = load_data()
        player_names = [""] + sorted(df['PlayerName'].unique())
        metrics = get_metric_names_dict(list(PREDICT_BATTER_METRICS.keys()), lang)
    else:
        df = load_pitcher_data()
        player_names = [""] + sorted(df['PlayerName'].unique())
        metrics = get_metric_names_dict(list(PREDICT_PITCHER_METRICS.keys()), lang)

    st.header(get_text("player_option", lang))

    # 검색 기능 추가
    search_query = st.text_input("🔍 선수 이름 검색", "")
    if search_query:
        filtered_names = [""] + [name for name in sorted(df['PlayerName'].unique()) if search_query.lower() in name.lower()]
        player = st.selectbox(get_text("select_player", lang), filtered_names, index=0)
    else:
        player = st.selectbox(get_text("select_player", lang), player_names, index=0)

    player_data = df[df['PlayerName'] == player]

    if not player_data.empty and len(player_data) > 0:
        tab1, tab2 = st.tabs([get_text("player_info", lang), get_text("prediction_tab", lang)])

        with tab1:
            st.subheader(f"📊 {player} {get_text('player_info', lang)}")

            player_id = player_data.iloc[0]['PlayerID']

            col1, col2 = st.columns([1, 2])

            with col1:
                display_player_image(player_id, player, width=200)

                # 주요 통계
                st.metric("통산 시즌", len(player_data))
                if selected == batter_option:
                    avg_ops = player_data['OPS'].mean()
                    st.metric("평균 OPS", f"{avg_ops:.3f}")
                else:
                    avg_era = player_data['EarnedRunAverage'].mean()
                    st.metric("평균 ERA", f"{avg_era:.2f}")

            with col2:
                show_data = player_data.drop(['PlayerID', 'PlayerName'], axis=1).sort_values('Season', ascending=False)
                st.dataframe(show_data.style.format({
                    "Season": "{:.0f}",
                    "BattingAverage": "{:.3f}",
                    "OnBasePercentage": "{:.3f}",
                    "SluggingPercentage": "{:.3f}",
                    "OPS": "{:.3f}",
                    "EarnedRunAverage": "{:.2f}",
                    "Wins": "{:.0f}",
                    "Losses": "{:.0f}",
                    "Strikeouts": "{:.0f}",
                    "Whip": "{:.2f}",
                    "InningsPitched": "{:.1f}"
                }), height=400, use_container_width=True)

        with tab2:
            st.subheader("🔮 " + get_text("prediction_tab", lang))

            # 최소 3시즌 데이터 필요
            if len(player_data) < 3:
                st.warning(f"⚠️ {player}의 데이터가 부족합니다. 예측을 위해서는 최소 3시즌 이상의 데이터가 필요합니다.")
                return

            # 선택 가능한 지표
            selected_metrics = st.multiselect(
                "예측할 지표를 선택하세요",
                options=list(metrics.keys()),
                format_func=lambda x: metrics[x],
                default=list(metrics.keys())[:2]
            )

            if not selected_metrics:
                st.info("💡 예측할 지표를 하나 이상 선택해주세요.")
                return

            # 예측 기간 선택
            prediction_years = st.slider("예측 기간 (년)", 1, 10, 5)

            if st.button("🚀 예측 시작", type="primary", use_container_width=True):
                player_data_copy = player_data.copy()
                player_data_copy['Season'] = pd.to_datetime(player_data_copy['Season'], format='%Y')

                progress_bar = st.progress(0)
                status_text = st.empty()

                for idx, metric in enumerate(selected_metrics):
                    if metric not in player_data_copy.columns:
                        continue

                    status_text.text(f"📊 {metrics[metric]} 예측 중... ({idx + 1}/{len(selected_metrics)})")
                    progress_bar.progress((idx + 1) / len(selected_metrics))

                    with st.spinner(f'{metrics[metric]} 모델 학습 및 예측 중...'):
                        # 데이터 준비
                        player_metric_data = player_data_copy[['Season', metric]].copy()
                        player_metric_data.columns = ['ds', 'y']

                        # 예측 수행
                        forecast = get_prophet_forecast(player_data_copy, metric, periods=prediction_years)

                        if forecast is None:
                            st.error(f"{metrics[metric]} 예측에 실패했습니다.")
                            continue

                        # 예측 차트 생성
                        st.subheader(f"📈 {metrics[metric]} 예측 결과")

                        fig = create_prediction_plot(
                            player_metric_data,
                            forecast,
                            metrics[metric],
                            player,
                            lang
                        )

                        st.plotly_chart(fig, use_container_width=True, config=get_plotly_config())

                        # 예측 결과 테이블
                        future_forecast = forecast[forecast['ds'] > player_metric_data['ds'].max()]

                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown("**📊 예측 통계**")
                            avg_pred = future_forecast['yhat'].mean()
                            st.metric("평균 예측값", f"{avg_pred:.2f}")

                        with col2:
                            trend = "상승 📈" if future_forecast['yhat'].iloc[-1] > player_metric_data['y'].iloc[-1] else "하락 📉"
                            st.markdown("**📊 추세**")
                            st.metric("예측 트렌드", trend)

                        # 상세 예측 테이블
                        with st.expander("📋 상세 예측 데이터 보기"):
                            result_df = future_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
                            result_df.columns = ['시즌', '예측값', '하한값', '상한값']
                            result_df['시즌'] = result_df['시즌'].dt.year

                            if metric in ['BattingAverage', 'OnBasePercentage', 'SluggingPercentage', 'OPS', 'Whip', 'EarnedRunAverage']:
                                st.dataframe(result_df.style.format({
                                    '예측값': "{:.3f}",
                                    '하한값': "{:.3f}",
                                    '상한값': "{:.3f}"
                                }), use_container_width=True)
                            else:
                                st.dataframe(result_df.style.format({
                                    '예측값': "{:.1f}",
                                    '하한값': "{:.1f}",
                                    '상한값': "{:.1f}"
                                }), use_container_width=True)

                        st.markdown("---")

                progress_bar.progress(1.0)
                status_text.text("✅ 모든 예측이 완료되었습니다!")
                st.success("🎉 예측이 성공적으로 완료되었습니다!")

                st.info("💡 차트 위에 마우스를 올리면 확대/축소, 다운로드 등의 기능을 사용할 수 있습니다.")

                # AI 예측 해석 버튼
                from agents.base import is_llm_available
                if is_llm_available():
                    st.markdown("---")
                    if st.button("🤖 " + get_text("ai_prediction_explain", lang), use_container_width=True):
                        with st.spinner(get_text("agent_thinking", lang)):
                            try:
                                from agents.prediction.graph import create_prediction_agent
                                agent = create_prediction_agent()
                                result = agent.invoke({
                                    "player_name": player,
                                    "player_type": "batter" if selected == batter_option else "pitcher",
                                    "metrics": selected_metrics,
                                    "prediction_years": prediction_years,
                                    "player_data": None, "data_seasons": 0,
                                    "data_adequate": False, "data_assessment": "",
                                    "player_age_curve": None, "similar_players_context": None,
                                    "forecasts": {}, "interpretation": "",
                                    "confidence_assessment": "", "lang": lang, "error": None,
                                })
                                st.markdown(f"**{get_text('prediction_confidence', lang)}**: {result.get('confidence_assessment', '')}")
                                st.markdown(result.get("interpretation", ""))
                            except Exception as e:
                                st.error(f"{get_text('agent_error', lang)}: {str(e)}")

    else:
        no_data_msg = {
            'ko': "선수 데이터가 존재하지 않습니다.",
            'en': "No player data exists.",
            'ja': "選手データが存在しません。"
        }
        st.warning(no_data_msg.get(lang, no_data_msg['ko']))


if __name__ == "__main__":
    run_predict()
