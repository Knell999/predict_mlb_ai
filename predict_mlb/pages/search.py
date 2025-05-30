"""
검색 페이지 모듈: 선수 기록 검색 및 조회 기능을 제공합니다.
"""
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

from ..data.data_manager import DataManager
from ..components.charts import ChartComponents
from ..components.ui_components import UIComponents
from ..i18n import get_text
from ..config.settings import BATTING_METRICS, PITCHING_METRICS
from ..utils.error_handler import ErrorHandler

def run_search(data_manager: DataManager, chart_components: ChartComponents, 
               ui_components: UIComponents, error_handler: ErrorHandler, lang: str = "ko") -> None:
    """
    MLB 선수 기록을 조회하고 시각화하는 함수입니다.
    
    Args:
        data_manager: 데이터 관리자 인스턴스
        chart_components: 차트 컴포넌트 인스턴스
        ui_components: UI 컴포넌트 인스턴스
        error_handler: 에러 핸들러 인스턴스
        lang: 언어 코드
    """
    st.title(get_text("search_title", lang))

    # 메뉴 옵션 설정
    menu_options = {
        'ko': ['타자(선수기준)', '타자(시즌기준)', '투수(선수기준)', '투수(시즌기준)'],
        'en': ['Batters (By Player)', 'Batters (By Season)', 'Pitchers (By Player)', 'Pitchers (By Season)'],
        'ja': ['打者(選手基準)', '打者(シーズン基準)', '投手(選手基準)', '投手(シーズン基準)']
    }
    
    selected_lang_options = menu_options.get(lang, menu_options['ko'])
    
    # 상단 메뉴 생성
    selected = option_menu(
        None,
        selected_lang_options,
        icons=['person-fill', 'calendar-date', 'person', 'calendar'],
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

    # 데이터 로드
    try:
        batter_data, pitcher_data = data_manager.load_all_data()
    except Exception as e:
        error_handler.handle_ui_error(e, "데이터를 로드하는 중 오류가 발생했습니다.")
        return

    # 선택된 메뉴에 따라 다른 뷰 표시
    if selected == selected_lang_options[0]:  # 타자(선수기준)
        view_player_stats(batter_data, data_manager, chart_components, ui_components, 
                          'batter', list(BATTING_METRICS.keys()), lang)
    elif selected == selected_lang_options[1]:  # 타자(시즌기준)
        view_season_stats(batter_data, data_manager, chart_components, 
                          'batter', list(BATTING_METRICS.keys()), lang)
    elif selected == selected_lang_options[2]:  # 투수(선수기준)
        view_player_stats(pitcher_data, data_manager, chart_components, ui_components,
                          'pitcher', list(PITCHING_METRICS.keys()), lang)
    elif selected == selected_lang_options[3]:  # 투수(시즌기준)
        view_season_stats(pitcher_data, data_manager, chart_components,
                          'pitcher', list(PITCHING_METRICS.keys()), lang)

def view_player_stats(data: pd.DataFrame, data_manager: DataManager, 
                     chart_components: ChartComponents, ui_components: UIComponents,
                     player_type: str, metrics: list, lang: str = "ko", season: int = None) -> None:
    """
    선수별 기록을 조회하고 시각화합니다.
    
    Args:
        data: 선수 데이터
        data_manager: 데이터 관리자 인스턴스
        chart_components: 차트 컴포넌트 인스턴스
        ui_components: UI 컴포넌트 인스턴스
        player_type: 선수 유형 ('batter' 또는 'pitcher')
        metrics: 표시할 메트릭 목록
        lang: 언어 코드
        season: 특정 시즌 (None이면 모든 시즌)
    """
    # 시즌 필터링
    if season:
        data = data[data['Season'] == season]

    # 선수 선택
    player_names = [""] + sorted(data['PlayerName'].unique())
    player = st.selectbox(get_text('select_player', lang), player_names, index=0)

    if player:
        # 선수 데이터 조회
        player_data = data[data['PlayerName'] == player].sort_values(by='Season')
        
        # 리그 평균 계산
        league_avg = data_manager.calculate_league_averages(metrics, player_type)
        
        if season:
            league_avg = league_avg[league_avg['Season'] == season]

        # 데이터 스타일링
        player_data_styled = player_data.style
        
        if player_type == 'pitcher':
            player_data_styled = player_data.style.format({
                "EarnedRunAverage": "{:.2f}",
                "Whip": "{:.2f}",
                "InningsPitched": "{:.1f}"
            })
        else:
            player_data_styled = player_data.style.format({
                "BattingAverage": "{:.3f}",
                "OnBasePercentage": "{:.3f}",
                "SluggingPercentage": "{:.3f}",
                "OPS": "{:.3f}"
            })

        if not player_data.empty:
            # 선수 정보 표시
            st.header(get_text("player_info", lang))
            UIComponents.create_player_info_section(player_data, lang)
            
            # 기록 표시
            st.subheader(get_text("stats", lang))
            st.dataframe(player_data_styled)
            
            # 시각화
            st.header(get_text("visualization_title", lang))
            
            for metric in metrics:
                if metric in player_data.columns:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # 선수 트렌드 차트
                        try:
                            fig = chart_components.create_player_comparison_chart(player_data, league_avg, metric, lang)
                            st.pyplot(fig)
                        except Exception as e:
                            st.error(f"차트 생성 중 오류 발생: {e}")
                    
                    with col2:
                        # 히스토그램
                        try:
                            latest_data = player_data.iloc[-1]
                            latest_value = latest_data[metric]
                            latest_season = latest_data['Season']
                            
                            season_data = data[data['Season'] == latest_season]
                            fig = chart_components.create_histogram(season_data, metric, latest_value, lang=lang)
                            st.pyplot(fig)
                        except Exception as e:
                            st.error(f"히스토그램 생성 중 오류 발생: {e}")
        else:
            st.warning(get_text("no_record", lang))

def view_season_stats(data: pd.DataFrame, data_manager: DataManager, 
                     chart_components: ChartComponents, player_type: str, 
                     metrics: list, lang: str = "ko") -> None:
    """
    시즌별 기록을 조회하고 시각화합니다.
    
    Args:
        data: 선수 데이터
        data_manager: 데이터 관리자 인스턴스
        chart_components: 차트 컴포넌트 인스턴스
        player_type: 선수 유형 ('batter' 또는 'pitcher')
        metrics: 표시할 메트릭 목록
        lang: 언어 코드
    """
    # 시즌 선택
    seasons = sorted(data['Season'].unique(), reverse=True)
    season = st.selectbox(get_text('select_season', lang), seasons)

    if season:
        # 해당 시즌 데이터 필터링
        season_data = data[data['Season'] == season]
        
        # 리그 평균 계산
        league_avg = data_manager.calculate_league_averages(metrics, player_type)
        league_avg_season = league_avg[league_avg['Season'] == season]
        
        # 시즌 정보 표시
        st.header(f"{season} {get_text('year', lang)}")
        
        # 상위 선수 표시
        st.subheader("Top Players")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if player_type == 'batter':
                # 타율 상위 10명
                st.write("Batting Average Leaders")
                top_avg = season_data.sort_values(by='BattingAverage', ascending=False).head(10)
                st.dataframe(top_avg[['PlayerName', 'BattingAverage']].style.format({"BattingAverage": "{:.3f}"}))
                
                # 홈런 상위 10명
                st.write("Home Run Leaders")
                top_hr = season_data.sort_values(by='HomeRuns', ascending=False).head(10)
                st.dataframe(top_hr[['PlayerName', 'HomeRuns']])
            else:
                # 평균자책점 상위 10명 (낮은 순)
                st.write("ERA Leaders")
                top_era = season_data.sort_values(by='EarnedRunAverage').head(10)
                st.dataframe(top_era[['PlayerName', 'EarnedRunAverage']].style.format({"EarnedRunAverage": "{:.2f}"}))
                
                # 승리 상위 10명
                st.write("Win Leaders")
                top_wins = season_data.sort_values(by='Wins', ascending=False).head(10)
                st.dataframe(top_wins[['PlayerName', 'Wins']])
        
        with col2:
            if player_type == 'batter':
                # 타점 상위 10명
                st.write("RBI Leaders")
                top_rbi = season_data.sort_values(by='RBIs', ascending=False).head(10)
                st.dataframe(top_rbi[['PlayerName', 'RBIs']])
                
                # OPS 상위 10명
                st.write("OPS Leaders")
                top_ops = season_data.sort_values(by='OPS', ascending=False).head(10)
                st.dataframe(top_ops[['PlayerName', 'OPS']].style.format({"OPS": "{:.3f}"}))
            else:
                # 삼진 상위 10명
                st.write("Strikeout Leaders")
                top_so = season_data.sort_values(by='StrikeOuts', ascending=False).head(10)
                st.dataframe(top_so[['PlayerName', 'StrikeOuts']])
                
                # WHIP 상위 10명 (낮은 순)
                st.write("WHIP Leaders")
                top_whip = season_data.sort_values(by='Whip').head(10)
                st.dataframe(top_whip[['PlayerName', 'Whip']].style.format({"Whip": "{:.2f}"}))
        
        # 분포 시각화
        st.header("Distribution")
        
        selected_metric = st.selectbox(
            "Select Metric",
            options=metrics,
            format_func=lambda x: f"{x}"
        )
        
        if selected_metric:
            try:
                fig = chart_components.create_histogram(season_data, selected_metric, bins=30, lang=lang)
                st.pyplot(fig)
            except Exception as e:
                st.error(f"히스토그램 생성 중 오류 발생: {e}")
