# filepath: /Users/hyunjong/Desktop/KHJ/personal/predict_mlb/home.py
import streamlit as st
from PIL import Image
from i18n import get_text


def run_home(lang="ko"):
    """애플리케이션의 홈 페이지를 구성하고 주요 기능 및 사용법을 안내합니다."""
    st.title("⚾️ " + get_text("app_title", lang) + " ⚾️")

    # 이미지 폭 조절
    st.image("mlb_players.jpg", use_container_width=True)

    st.markdown(
        f"""
        {get_text("welcome_message", lang)}

        {get_text("app_intro", lang)}

        {get_text("app_description", lang)}
        """
    )

    # 주요 기능 강조
    st.markdown("---")
    st.header(get_text("main_features", lang))

    with st.container():
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader(get_text("search_feature", lang))
            st.markdown(
                """
                - **실시간 검색**: 최신 MLB 선수 기록을 실시간으로 검색하고 조회할 수 있습니다.
                - **상세 정보**: 타자와 투수의 다양한 지표를 상세하게 확인할 수 있습니다.
                - **커스텀 필터**: 원하는 조건에 맞게 검색 결과를 필터링하고 정렬할 수 있습니다.
                """
            )

        with col2:
            st.subheader(get_text("prediction_feature", lang))
            st.markdown(
                """
                - **알고리즘 기반 예측**: 최신 머신 러닝 알고리즘을 활용하여 타자와 투수의 다양한 기록을 예측합니다.
                - **맞춤형 예측**: 사용자가 선택한 조건에 따라 맞춤형 예측을 제공하여, 전략적 판단에 도움을 줍니다.
                - **트렌드 분석**: 선수들의 최근 경기 흐름을 분석하여 향후 성과를 예측합니다.
                """
            )

        with col3:
            st.subheader(get_text("visualization_feature", lang))
            st.markdown(
                """
                - **그래프 및 차트**: 데이터를 시각화하여 이해하기 쉽게 제공하며, 다양한 시각적 도구를 통해 직관적인 분석이 가능합니다.
                - **트렌드 분석**: 타자와 투수의 리그 평균 지표 변화 추이를 시각화하여, 경기의 흐름을 한눈에 파악할 수 있습니다.
                - **인터랙티브 대시보드**: 사용자가 원하는 대로 대시보드를 커스터마이징하여, 필요한 정보만을 빠르게 조회할 수 있습니다.
                """
            )
            
if __name__ == "__main__":
    run_home()
