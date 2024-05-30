# app.py

import streamlit as st
from streamlit_option_menu import option_menu
from home import run_home
from search import run_search
from predict import run_predict


def main():
    with st.sidebar:
        selected = option_menu('대시보드 메뉴', ['홈', '기록 조회', '기록 예측'],
                               icons=['house', 'file-bar-graph', 'graph-up-arrow'], menu_icon='cast', default_index=0)

    if selected == '홈':
        run_home()
    elif selected == '기록 조회':
        run_search()
    elif selected == '기록 예측':
        run_predict()


if __name__ == "__main__":
    main()
