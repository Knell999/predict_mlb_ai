"""
홈 페이지 모듈: 애플리케이션의 홈 페이지를 구성합니다.
"""
import streamlit as st
from PIL import Image
import os
from typing import Optional

from ..i18n import get_text

def run_home(lang: str = "ko", image_path: Optional[str] = None) -> None:
    """
    애플리케이션의 홈 페이지를 구성하고 주요 기능 및 사용법을 안내합니다.
    
    Args:
        lang: 언어 코드
        image_path: 홈 이미지 경로
    """
    st.title("⚾️ " + get_text("app_title", lang) + " ⚾️")

    # 이미지 표시 (경로가 제공된 경우)
    if image_path and os.path.exists(image_path):
        st.image(image_path, use_container_width=True)
    else:
        st.info("이미지를 찾을 수 없습니다.")

    # 환영 메시지
    st.markdown(
        f"""
        {get_text("welcome_message", lang)}

        {get_text("app_intro", lang)}

        {get_text("app_description", lang)}
        """
    )

    # 주요 기능 설명
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
    
    # 추가 정보
    st.markdown("---")
    st.header(get_text("learn_more", lang))
    
    st.markdown(
        """
        이 애플리케이션은 MLB 데이터 분석을 위한 종합 플랫폼으로, 야구 팬과 분석가를 위해 설계되었습니다.
        다양한 기능을 활용하여 MLB 선수들의 성적을 분석하고, 향후 성과를 예측해보세요!
        """
    )
    
    # 데이터 출처 정보
    st.info(
        """
        **데이터 출처**: MLB 공식 통계 자료
        
        본 애플리케이션에 사용된 데이터는 공개된 MLB 통계 자료를 기반으로 합니다.
        데이터는 정기적으로 업데이트되며, 최신 시즌 정보를 포함하고 있습니다.
        """
    )
