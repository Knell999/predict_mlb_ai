import streamlit as st
import pandas as pd
from prophet import Prophet
from utils import load_data, load_pitcher_data
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib import rc
from streamlit_option_menu import option_menu

path = 'font/H2GTRM.TTF'
fontprop = fm.FontProperties(fname=path, size=12)
rc('font', family=fontprop.get_name())

def run_predict():
    st.title('MLB 선수 기록 예측')

    selected = option_menu(
        None,
        ['타자', '투수'],
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

    if selected == '타자':
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

    st.header("선수 및 옵션 선택")
    player = st.selectbox('선수를 선택하세요:', player_names, index=0)

    player_data = df[df['PlayerName'] == player]

    if not player_data.empty:
        tab1, tab2 = st.tabs(["선수 정보", "기록 예측"])

        with tab1:
            st.subheader(f"{player} 선수 정보")

            player_id = player_data.iloc[0]['PlayerID']
            profile_url = f"https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_426,q_auto:best/v1/people/{player_id}/headshot/67/current"

            col1, col2 = st.columns([1, 2])

            with col1:
                try:
                    st.image(profile_url, caption=f"{player}의 프로필 사진", width=200)
                except:
                    st.warning("프로필 사진을 불러올 수 없습니다.")

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
            st.subheader("기록 예측")

            seasons_required = [2022, 2023]
            available_seasons = player_data['Season'].unique()

            if all(season in available_seasons for season in seasons_required):
                player_data['Season'] = pd.to_datetime(player_data['Season'], format='%Y')

                forecasts = {}

                for metric, (min_val, max_val) in metrics.items():
                    if metric not in player_data.columns:
                        continue

                    player_metric_data = player_data[['Season', metric]]
                    player_metric_data.columns = ['ds', 'y']

                    model = Prophet()
                    model.fit(player_metric_data)
                    future = model.make_future_dataframe(periods=5, freq='Y')
                    forecast = model.predict(future)

                    # 예측 값을 지정된 범위로 제한
                    forecast['yhat'] = forecast['yhat'].clip(lower=min_val, upper=max_val)
                    forecast['yhat_lower'] = forecast['yhat_lower'].clip(lower=min_val, upper=max_val)
                    forecast['yhat_upper'] = forecast['yhat_upper'].clip(lower=min_val, upper=max_val)

                    forecasts[metric] = forecast

                    st.subheader(f"{player}의 향후 5년간 예측된 {metric}")

                    fig, ax = plt.subplots(figsize=(12, 6))
                    ax.plot(player_metric_data['ds'], player_metric_data['y'], 'bo-', label='실제값')
                    future_forecast = forecast[forecast['ds'] > player_metric_data['ds'].max()]
                    ax.plot(future_forecast['ds'], future_forecast['yhat'], 'ro-', label='예측값')
                    ax.fill_between(future_forecast['ds'], future_forecast['yhat_lower'], future_forecast['yhat_upper'], alpha=0.2, label='95% 신뢰 구간')

                    ax.set_title(f"{player}의 향후 5년 {metric} 예측 그래프", fontproperties=fontprop)
                    ax.set_xlabel("Season", fontproperties=fontprop)
                    ax.set_ylabel(metric, fontproperties=fontprop)
                    ax.legend(prop=fontprop)
                    plt.xticks(rotation=45)

                    st.pyplot(fig)
            else:
                st.warning(f"{player}의 최근 2개년(2022, 2023) 시즌 데이터가 없어 예측이 불가능합니다.")
    else:
        st.warning("선수 데이터가 존재하지 않습니다.")

if __name__ == "__main__":
    run_predict()
