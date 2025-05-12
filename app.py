import streamlit as st
from streamlit_option_menu import option_menu
from home import run_home
from search import run_search
from predict import run_predict
from trend import run_trend
from PIL import Image

# 페이지 제목 설정 (반드시 코드의 맨 처음 부분에 위치)
st.set_page_config(page_title="MLB 선수 분석 대시보드", page_icon="⚾️", layout="wide")

def main():
    # 사이드바 설정 및 메뉴 옵션 정의
    with st.sidebar:
        st.title("⚾ MLB 선수 분석 대시보드")
        logo_image = Image.open("mlb_logo.png")  # MLB 로고 이미지 추가 (파일 이름에 맞게 수정)
        st.image(logo_image,  use_container_width=True)  # 이미지 폭 조절
        selected = option_menu(
            None,
            ["홈", "트렌드 분석", "기록 조회", "기록 예측"],
            icons=["house", "activity", "search", "magic"],
            menu_icon="cast",
            default_index=0,
            orientation="vertical",  # 메뉴 세로 방향으로 변경
        )

    # 페이지별 함수 실행
    if selected == "홈":
        run_home()
    elif selected == "기록 조회":
        run_search()
    elif selected == "기록 예측":
        run_predict()
    elif selected == "트렌드 분석":
        run_trend()

if __name__ == "__main__":
    main()
