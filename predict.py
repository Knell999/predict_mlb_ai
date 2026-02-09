import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from prophet import Prophet
from utils import load_data, load_pitcher_data
from matplotlib import rc
from streamlit_option_menu import option_menu
from i18n import get_text

path = 'font/H2GTRM.TTF'
fontprop = fm.FontProperties(fname=path, size=12)
rc('font', family=fontprop.get_name())


@st.cache_resource
def get_prophet_forecast(data, metric, periods=5):
    """
    Prophet 모델을 학습하고 예측을 수행합니다.
    Streamlit 캐싱을 통해 반복 학습을 방지합니다.
    """
    df_metric = data[['Season', metric]].copy()
    df_metric.columns = ['ds', 'y']
    
    model = Prophet()
    model.fit(df_metric)
    
    future = model.make_future_dataframe(periods=periods, freq='Y')
    forecast = model.predict(future)
    return forecast

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
        metrics = {
            'BattingAverage': (0, 0.4),
            'OnBasePercentage': (0, 0.7),
            'SluggingPercentage': (0, 0.8),
            'OPS': (0, 1.4)
        }
    else:
        df = load_pitcher_data()
        player_names = [""] + sorted(df['PlayerName'].unique())
        metrics = {
            'EarnedRunAverage': (0, 5),
            'Wins': (0, 35),
            'Losses': (0, 30),
            'StrikeOuts': (0, 400),
            'Whip': (0, 4),
            'InningsPitched': (0, 400)
        }

    st.header(get_text("player_option", lang))
    player = st.selectbox(get_text("select_player", lang), player_names, index=0)

    player_data = df[df['PlayerName'] == player]

    if not player_data.empty:
        tab1, tab2 = st.tabs([get_text("player_info", lang), get_text("prediction_tab", lang)])

        with tab1:
            st.subheader(f"{player} {get_text('player_info', lang)}")

            player_id = player_data.iloc[0]['PlayerID']
            profile_url = f"https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_426,q_auto:best/v1/people/{player_id}/headshot/67/current"

            col1, col2 = st.columns([1, 2])

            with col1:
                try:
                    profile_caption = {
                        'ko': f"{player}의 프로필 사진",
                        'en': f"{player}'s Profile Picture",
                        'ja': f"{player}のプロフィール写真"
                    }
                    st.image(profile_url, caption=profile_caption.get(lang, profile_caption['ko']), width=200)
                except:
                    error_msg = {
                        'ko': "프로필 사진을 불러올 수 없습니다.",
                        'en': "Unable to load profile picture.",
                        'ja': "プロフィール写真を読み込めません。"
                    }
                    st.warning(error_msg.get(lang, error_msg['ko']))

            with col2:
                show_data = player_data.drop(['PlayerID', 'PlayerName'], axis=1)
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
                }))

        with tab2:
            st.subheader(get_text("prediction_tab", lang))

            seasons_required = [2022, 2023]
            available_seasons = player_data['Season'].unique()

            if all(season in available_seasons for season in seasons_required):
                player_data['Season'] = pd.to_datetime(player_data['Season'], format='%Y')

                forecasts = {}

                for metric, (min_val, max_val) in metrics.items():
                    if metric not in player_data.columns:
                        continue
                    
                    # 시각화를 위해 데이터 준비
                    player_metric_data = player_data[['Season', metric]].copy()
                    player_metric_data.columns = ['ds', 'y']
                    
                    # 캐싱된 함수를 사용하여 예측 수행
                    forecast = get_prophet_forecast(player_data, metric)
                    
                    # 예측 결과 저장
                    forecasts[metric] = forecast
                    
                    # 예측 결과 시각화
                    predict_title = {
                        'ko': f"{metric} 예측",
                        'en': f"{metric} Prediction",
                        'ja': f"{metric} 予測"
                    }
                    st.subheader(predict_title.get(lang, predict_title['ko']))
                    
                    fig, ax = plt.subplots(figsize=(10, 6))
                    
                    # 라벨 텍스트 정의
                    label_text = {
                        'ko': {'actual': '실제 기록', 'predict': '예측', 'interval': '95% 신뢰 구간'},
                        'en': {'actual': 'Actual Records', 'predict': 'Prediction', 'interval': '95% Confidence Interval'},
                        'ja': {'actual': '実績', 'predict': '予測', 'interval': '95% 信頼区間'}
                    }
                    
                    # 현재 언어에 맞는 라벨 선택
                    current_labels = label_text.get(lang, label_text['ko'])
                    
                    # 실제 데이터 플롯
                    ax.plot(player_metric_data['ds'].dt.year, player_metric_data['y'], 'ko-', label=current_labels['actual'])
                    
                    # 예측 데이터 플롯
                    future_forecast = forecast[forecast['ds'] > player_metric_data['ds'].max()]
                    ax.plot(future_forecast['ds'].dt.year, future_forecast['yhat'], 'b-', label=current_labels['predict'])
                    ax.fill_between(future_forecast['ds'].dt.year, future_forecast['yhat_lower'], future_forecast['yhat_upper'], alpha=0.2, label=current_labels['interval'])

                    title_text = {
                        'ko': f"{player}의 향후 5년 {metric} 예측 그래프",
                        'en': f"{player}'s 5-Year {metric} Prediction Graph",
                        'ja': f"{player}の今後5年間の{metric}予測グラフ"
                    }
                    xlabel_text = {
                        'ko': "시즌",
                        'en': "Season",
                        'ja': "シーズン"
                    }
                    
                    ax.set_title(title_text.get(lang, title_text['ko']), fontproperties=fontprop)
                    ax.set_xlabel(xlabel_text.get(lang, xlabel_text['ko']), fontproperties=fontprop)
                    ax.set_ylabel(metric, fontproperties=fontprop)
                    ax.legend(prop=fontprop)
                    plt.xticks(rotation=45)
                    
                    # Y축 범위 설정 (지표에 따라 적절한 범위 설정)
                    ax.set_ylim(min_val, max_val)
                    
                    st.pyplot(fig)
                    
                    # 예측 결과 표 형태로 보여주기
                    result_title = {
                        'ko': f"{metric} 예측 결과",
                        'en': f"{metric} Prediction Results",
                        'ja': f"{metric} 予測結果"
                    }
                    
                    column_names = {
                        'ko': ['Season', '예측값', '하한값', '상한값'],
                        'en': ['Season', 'Prediction', 'Lower Bound', 'Upper Bound'],
                        'ja': ['シーズン', '予測値', '下限値', '上限値']
                    }
                    
                    st.subheader(result_title.get(lang, result_title['ko']))
                    future_result = future_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
                    future_result.columns = column_names.get(lang, column_names['ko'])
                    future_result['Season'] = future_result['Season'].dt.year
                    
                    # 자릿수 형식 지정
                    if metric in ['BattingAverage', 'OnBasePercentage', 'SluggingPercentage', 'OPS', 'Whip']:
                        st.dataframe(future_result.style.format({
                            '예측값': "{:.3f}",
                            '하한값': "{:.3f}",
                            '상한값': "{:.3f}"
                        }))
                    else:
                        st.dataframe(future_result.style.format({
                            '예측값': "{:.1f}",
                            '하한값': "{:.1f}",
                            '상한값': "{:.1f}"
                        }))
            else:
                warning_msg = {
                    'ko': f"{player}의 최근 2개년(2022, 2023) 시즌 데이터가 없어 예측이 불가능합니다.",
                    'en': f"{player} does not have recent data (2022, 2023) required for prediction.",
                    'ja': f"{player}は予測に必要な最近のデータ（2022年、2023年）がありません。"
                }
                st.warning(warning_msg.get(lang, warning_msg['ko']))
    else:
        no_data_msg = {
            'ko': "선수 데이터가 존재하지 않습니다.",
            'en': "No player data exists.",
            'ja': "選手データが存在しません。"
        }
        st.warning(no_data_msg.get(lang, no_data_msg['ko']))

if __name__ == "__main__":
    run_predict()
