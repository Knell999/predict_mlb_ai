# filepath: /Users/hyunjong/Desktop/KHJ/personal/predict_mlb/home.py
import streamlit as st
from PIL import Image
from i18n import get_text
from config import MLB_PLAYERS_IMAGE_PATH


def run_home(lang="ko"):
    """애플리케이션의 홈 페이지를 구성하고 주요 기능 및 사용법을 안내합니다."""
    st.title("⚾️ " + get_text("app_title", lang) + " ⚾️")

    # 이미지 폭 조절
    st.image(MLB_PLAYERS_IMAGE_PATH, use_container_width=True)

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
                f"""
                - **{get_text("search_feature_desc_1", lang)}**
                - **{get_text("search_feature_desc_2", lang)}**
                - **{get_text("search_feature_desc_3", lang)}**
                """
            )

        with col2:
            st.subheader(get_text("prediction_feature", lang))
            st.markdown(
                f"""
                - **{get_text("prediction_feature_desc_1", lang)}**
                - **{get_text("prediction_feature_desc_2", lang)}**
                - **{get_text("prediction_feature_desc_3", lang)}**
                """
            )

        with col3:
            st.subheader(get_text("visualization_feature", lang))
            st.markdown(
                f"""
                - **{get_text("visualization_feature_desc_1", lang)}**
                - **{get_text("visualization_feature_desc_2", lang)}**
                - **{get_text("visualization_feature_desc_3", lang)}**
                """
            )
            
if __name__ == "__main__":
    run_home()
