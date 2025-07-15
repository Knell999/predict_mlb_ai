import streamlit as st

# 페이지 제목 설정 (반드시 코드의 맨 처음 부분에 위치)
st.set_page_config(page_title="MLB 선수 분석 대시보드", page_icon="⚾️", layout="wide")

# 나머지 임포트문들
from streamlit_option_menu import option_menu
import time
import datetime
from home import run_home
from search import run_search
from predict import run_predict
from trend import run_trend
from compare import run_compare
from data_status import show_data_status
from PIL import Image
from utils import set_chart_style, load_logo_image # load_logo_image 추가
from app_metrics import init_metrics, timing_decorator
from i18n import get_text, get_languages
from config import MLB_LOGO_PATH # 설정 파일에서 로고 경로 가져오기

# 테마와 메트릭 초기화
set_chart_style()
metric_tracker = init_metrics()

@timing_decorator
def main():
    """MLB 선수 분석 대시보드 메인 함수"""
    
    # 세션 상태에 언어 설정이 없으면 기본값 설정
    if 'lang' not in st.session_state:
        st.session_state.lang = "ko"
    
    # 사이드바 설정 및 메뉴 옵션 정의
    with st.sidebar:
        st.title("⚾ " + get_text("app_title", st.session_state.lang))
        
        # 로고 이미지 로드 (utils.py의 함수 사용)
        logo_image = load_logo_image(MLB_LOGO_PATH) 
        if logo_image:
            st.image(logo_image, use_container_width=True)
        else:
            st.warning("로고 이미지를 불러올 수 없습니다.")
        
        # 언어 선택 옵션
        languages = get_languages()
        selected_lang = st.selectbox(
            "🌐 Language / 언어",
            options=list(languages.keys()),
            format_func=lambda x: languages[x],
            index=list(languages.keys()).index(st.session_state.lang)
        )
        
        # 언어가 변경되면 세션 상태 업데이트
        if selected_lang != st.session_state.lang:
            st.session_state.lang = selected_lang
            st.rerun()  # 언어 변경 시 앱 다시 실행
        
        selected = option_menu(
            None,
            [
                get_text("home", st.session_state.lang), 
                get_text("trend_analysis", st.session_state.lang), 
                get_text("search_records", st.session_state.lang), 
                get_text("compare_players", st.session_state.lang),
                get_text("predict_records", st.session_state.lang),
                "📊 데이터 상태"
            ],
            icons=["house", "activity", "search", "people", "magic", "database"],
            menu_icon="cast",
            default_index=0,
            orientation="vertical",  # 메뉴 세로 방향으로 변경
        )
        
        # 사이드바 하단에 앱 정보 표시
        st.markdown("---")
        st.markdown(f"<small>© {datetime.datetime.now().year} MLB Stats App</small>", unsafe_allow_html=True)
        st.markdown("<small>v1.0.0</small>", unsafe_allow_html=True)

    # 페이지 로깅 및 실행
    metric_tracker.log_page_view(selected)
    
    # 페이지별 함수 실행
    lang = st.session_state.lang
    home_text = get_text("home", lang)
    search_text = get_text("search_records", lang)
    predict_text = get_text("predict_records", lang)
    trend_text = get_text("trend_analysis", lang)
    compare_text = get_text("compare_players", lang)
    
    if selected == home_text:
        run_home(lang)
    elif selected == search_text:
        run_search(lang)
    elif selected == predict_text:
        run_predict(lang)
    elif selected == trend_text:
        run_trend(lang)
    elif selected == compare_text:
        run_compare(lang)
    elif selected == "📊 데이터 상태":
        show_data_status()

    # 성능 모니터링 - 사이드바 하단에 표시
    with st.sidebar.expander("📊 앱 성능 메트릭"):
        metrics = metric_tracker.get_summary()
        st.write(f"총 페이지뷰: {metrics['total_page_views']}")
        st.write(f"평균 응답시간: {metrics['avg_response_time']:.2f} ms")
        st.write(f"에러 수: {metrics['error_count']}")

if __name__ == "__main__":
    main()
