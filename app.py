import streamlit as st
from streamlit_option_menu import option_menu
from home import run_home


def main():
    with st.sidebar:
        selected = option_menu('대시보드 메뉴', ['홈', '기록 조회', '기록 예측'],
                               icons=['house', 'file-bar-graph', 'graph-up-arrow'], menu_icon='cast', default_index=0)

    # 각 메뉴에 대한 동작 정의
    if selected == '홈':
        run_home()
    elif selected == '기록 조회':
        st.title('기록 조회')
        st.write('여기에서 기록을 조회할 수 있습니다.')
    elif selected == '기록 예측':
        st.title('기록 예측')
        st.write('여기에서 기록을 예측할 수 있습니다.')


if __name__ == "__main__":
    main()
