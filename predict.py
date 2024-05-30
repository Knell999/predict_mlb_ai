import streamlit as st
import pandas as pd
from prophet import Prophet
from utils import load_data
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

def run_predict():
    st.title('기록 예측')
    st.write('여기에서 기록을 예측할 수 있습니다.')

    path = 'font/H2GTRM.TTF'
    fontprop = fm.FontProperties(fname=path, size=12)

    df = load_data()
    df = df.reset_index(drop=True) #인덱스 삭제?

    # 선수 이름 선택
    player_names = df['PlayerName'].unique()
    player = st.selectbox('선수를 선택하세요:', player_names)

    # 데이터 필터링
    player_data = df[df['PlayerName'] == player]

    if not player_data.empty:
        st.write("선수 데이터:")
        st.dataframe(player_data.head())  # 필터링된 선수 데이터 확인

        # Season을 datetime 형식으로 변환
        player_data['Season'] = pd.to_datetime(player_data['Season'], format='%Y')
        player_data = player_data[['Season', 'BattingAverage']]
        player_data.columns = ['ds', 'y']

        model = Prophet()
        model.fit(player_data)

        # 미래 데이터프레임 생성
        future = model.make_future_dataframe(periods=5, freq='Y')
        forecast = model.predict(future)

        # 예측 결과 연도만 추출하여 데이터프레임 생성
        forecast['Season'] = forecast['ds'].dt.year

        st.subheader(f"{player}의 향후 5년간 예측된 기록")
        # 데이터프레임 출력 시 천 단위 구분 기호 제거
        st.dataframe(forecast[['Season', 'yhat', 'yhat_lower', 'yhat_upper']].tail(5).style.format(
            {"Season": "{:.0f}", "yhat": "{:.3f}", "yhat_lower": "{:.3f}", "yhat_upper": "{:.3f}"}))

        # 그래프 시각화
        fig, ax = plt.subplots()
        ax.plot(forecast['ds'], forecast['yhat'], '-o', label='예측값')
        ax.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], alpha=0.2, label='95% 신뢰 구간')

        ax.set_title(f"{player}의 향후 5년 타율 예측그래프", fontproperties=fontprop)
        ax.set_xlabel("Season", fontproperties=fontprop)
        ax.set_ylabel("AVG", fontproperties=fontprop)
        ax.legend(prop=fontprop)

        st.pyplot(fig)

    else:
        st.write("선수 데이터가 존재하지 않습니다.")
