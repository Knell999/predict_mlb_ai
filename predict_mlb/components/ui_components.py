"""
UI 컴포넌트 모듈: 사용자 인터페이스 요소를 제공합니다.
"""
import streamlit as st
from PIL import Image
import os
from typing import Dict, List, Any, Optional, Tuple

class UIComponents:
    """UI 컴포넌트 클래스"""
    
    def __init__(self, logo_path: Optional[str] = None):
        """
        UIComponents 클래스 초기화
        
        Args:
            logo_path: 로고 이미지 경로
        """
        self.logo_path = logo_path
        
    def load_logo_image(self) -> Optional[Image.Image]:
        """
        로고 이미지를 로드합니다.
        
        Returns:
            Optional[Image.Image]: 로드된 이미지 객체 또는 None
        """
        if not self.logo_path:
            return None
            
        try:
            if not os.path.exists(self.logo_path):
                st.error(f"로고 파일을 찾을 수 없습니다: {self.logo_path}")
                return None
            return Image.open(self.logo_path)
        except Exception as e:
            st.error(f"로고 이미지 로드 중 오류 발생: {e}")
            return None
            
    @staticmethod
    def create_sidebar(title: str, logo_image: Optional[Image.Image] = None, 
                       language_selector: bool = True, languages: Dict[str, str] = None) -> None:
        """
        사이드바를 생성합니다.
        
        Args:
            title: 사이드바 제목
            logo_image: 로고 이미지 객체
            language_selector: 언어 선택기 표시 여부
            languages: 언어 옵션 (코드-이름 쌍의 딕셔너리)
        """
        st.sidebar.title(title)
        
        # 로고 이미지 표시
        if logo_image:
            st.sidebar.image(logo_image, use_container_width=True)
        
        # 언어 선택기 표시
        if language_selector and languages:
            if 'lang' not in st.session_state:
                st.session_state.lang = "ko"
                
            selected_lang = st.sidebar.selectbox(
                "🌐 Language / 언어",
                options=list(languages.keys()),
                format_func=lambda x: languages[x],
                index=list(languages.keys()).index(st.session_state.lang)
            )
            
            if selected_lang != st.session_state.lang:
                st.session_state.lang = selected_lang
                st.rerun()
    
    @staticmethod
    def create_player_info_section(player_data: pd.DataFrame, lang: str = "ko") -> None:
        """
        선수 정보 섹션을 생성합니다.
        
        Args:
            player_data: 선수 데이터
            lang: 언어 코드
        """
        if player_data.empty:
            st.warning("선수 데이터를 찾을 수 없습니다.")
            return
            
        player_name = player_data['PlayerName'].iloc[0]
        player_id = player_data['PlayerID'].iloc[0]
        
        # 프로필 URL 생성
        profile_url = f"https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_426,q_auto:best/v1/people/{player_id}/headshot/67/current"
        
        # 레이블 설정
        profile_caption = {
            'ko': f"{player_name}의 프로필 사진",
            'en': f"{player_name}'s Profile Picture",
            'ja': f"{player_name}のプロフィール写真"
        }
        
        error_msg = {
            'ko': "프로필 사진을 불러올 수 없습니다.",
            'en': "Unable to load profile picture.",
            'ja': "プロフィール写真を読み込めません。"
        }
        
        # 레이아웃 생성
        col1, col2 = st.columns([1, 2])
        
        with col1:
            try:
                st.image(profile_url, caption=profile_caption.get(lang, profile_caption['ko']), width=200)
            except:
                st.warning(error_msg.get(lang, error_msg['ko']))
                
        with col2:
            st.write(f"**{player_name}**")
            
            # 시즌별 데이터가 있는 경우 최신 시즌 표시
            if 'Season' in player_data.columns:
                latest_season = player_data['Season'].max()
                st.write(f"**{latest_season} {get_text('year', lang)}**")
                
            # 주요 지표 표시
            st.write("### 주요 지표")
            latest_data = player_data.sort_values('Season', ascending=False).iloc[0]
            
            # 타자인 경우
            if 'BattingAverage' in player_data.columns:
                st.write(f"타율(AVG): {latest_data.get('BattingAverage', 'N/A'):.3f}")
                st.write(f"홈런(HR): {int(latest_data.get('HomeRuns', 0))}")
                st.write(f"타점(RBI): {int(latest_data.get('RBIs', 0))}")
            # 투수인 경우
            elif 'EarnedRunAverage' in player_data.columns:
                st.write(f"평균자책점(ERA): {latest_data.get('EarnedRunAverage', 'N/A'):.2f}")
                st.write(f"승리(W): {int(latest_data.get('Wins', 0))}")
                st.write(f"삼진(SO): {int(latest_data.get('StrikeOuts', 0))}")
                
    @staticmethod
    def create_metrics_selector(metrics: List[str], key: str, lang: str = "ko") -> List[str]:
        """
        지표 선택기를 생성합니다.
        
        Args:
            metrics: 선택 가능한 지표 목록
            key: 위젯의 고유 키
            lang: 언어 코드
            
        Returns:
            List[str]: 선택된 지표 목록
        """
        # 언어별 메시지
        messages = {
            'ko': "분석할 지표 선택",
            'en': "Select metrics to analyze",
            'ja': "分析する指標を選択"
        }
        
        message = messages.get(lang, messages['ko'])
        
        return st.multiselect(message, options=metrics, key=key)
