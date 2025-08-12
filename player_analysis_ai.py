"""
AI 기반 선수 분석 보고서 생성 모듈
LangChain과 Google Gemini를 활용한 MLB 선수 기록 동향 분석
"""

import os
import pandas as pd
import streamlit as st
from typing import Dict, List, Optional, Any
import logging

# .env 파일 로드
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.prompts import PromptTemplate
    from langchain.schema import HumanMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# 로깅 설정
logger = logging.getLogger(__name__)

class PlayerAnalysisAI:
    """AI 기반 선수 분석 클래스"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        PlayerAnalysisAI 초기화
        
        Args:
            api_key: Google AI API 키 (없으면 환경변수에서 가져옴)
        """
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain 라이브러리가 필요합니다.")
        
        self.api_key = api_key or os.getenv("GOOGLE_AI_API_KEY")
        if not self.api_key:
            raise ValueError("Google AI API 키가 설정되지 않았습니다. 환경변수 GOOGLE_AI_API_KEY를 설정하거나 직접 전달하세요.")
        
        # Gemini 모델 초기화
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=self.api_key,
            temperature=0.3,
            max_tokens=2048
        )
        
        # 프롬프트 템플릿 설정
        self._setup_prompts()
    
    def _setup_prompts(self):
        """분석용 프롬프트 템플릿 설정"""
        
        self.batter_analysis_prompt = PromptTemplate(
            input_variables=["player_name", "player_data", "league_averages", "language"],
            template="""
당신은 MLB 데이터 분석 전문가입니다. 주어진 타자의 기록을 분석하여 종합적인 보고서를 작성해주세요.

선수명: {player_name}

선수 기록 데이터:
{player_data}

리그 평균 데이터:
{league_averages}

언어: {language}

다음 항목들을 포함하여 전문적인 분석 보고서를 작성해주세요:

1. **선수 개요 및 커리어 하이라이트**
   - 주요 성과와 기록
   - 커리어 전반적인 평가

2. **핵심 지표 분석**
   - 타율(Batting Average) 동향
   - 출루율(OBP)과 장타율(SLG) 분석
   - OPS 변화 추이
   - 홈런과 타점 성과

3. **리그 평균 대비 성과**
   - 각 시즌별 리그 평균 대비 성과
   - 상대적 강점과 약점 분석

4. **시즌별 트렌드 분석**
   - 성과 개선/악화 구간 식별
   - 피크 시즌과 부진 시즌 분석
   - 나이에 따른 성과 변화

5. **종합 평가 및 인사이트**
   - 선수의 플레이 스타일 특징
   - 강점과 개선점
   - 향후 전망

분석은 데이터에 기반하여 객관적이고 전문적으로 작성하되, {language} 언어로 작성해주세요.
마크다운 형식을 사용하여 가독성을 높여주세요.
"""
        )
        
        self.pitcher_analysis_prompt = PromptTemplate(
            input_variables=["player_name", "player_data", "league_averages", "language"],
            template="""
당신은 MLB 데이터 분석 전문가입니다. 주어진 투수의 기록을 분석하여 종합적인 보고서를 작성해주세요.

선수명: {player_name}

선수 기록 데이터:
{player_data}

리그 평균 데이터:
{league_averages}

언어: {language}

다음 항목들을 포함하여 전문적인 분석 보고서를 작성해주세요:

1. **선수 개요 및 커리어 하이라이트**
   - 주요 성과와 기록
   - 커리어 전반적인 평가

2. **핵심 지표 분석**
   - 평균자책점(ERA) 동향
   - WHIP 분석
   - 탈삼진 능력 평가
   - 이닝 소화 능력

3. **리그 평균 대비 성과**
   - 각 시즌별 리그 평균 대비 성과
   - 상대적 강점과 약점 분석

4. **시즌별 트렌드 분석**
   - 성과 개선/악화 구간 식별
   - 피크 시즌과 부진 시즌 분석
   - 나이에 따른 성과 변화

5. **종합 평가 및 인사이트**
   - 투수의 스타일과 특징
   - 강점과 개선점
   - 향후 전망

분석은 데이터에 기반하여 객관적이고 전문적으로 작성하되, {language} 언어로 작성해주세요.
마크다운 형식을 사용하여 가독성을 높여주세요.
"""
        )
    
    def _prepare_player_data_summary(self, player_data: pd.DataFrame, player_type: str) -> str:
        """선수 데이터를 AI 분석용 텍스트로 변환"""
        if player_data.empty:
            return "데이터가 없습니다."
        
        summary_lines = []
        
        for _, row in player_data.iterrows():
            if player_type == "타자":
                line = f"시즌 {row['Season']}: "
                line += f"타율 {row.get('BattingAverage', 'N/A'):.3f}, "
                line += f"홈런 {row.get('HomeRuns', 'N/A')}개, "
                line += f"타점 {row.get('RBIs', 'N/A')}개, "
                line += f"OPS {row.get('OPS', 'N/A'):.3f}, "
                line += f"출루율 {row.get('OnBasePercentage', 'N/A'):.3f}, "
                line += f"장타율 {row.get('SluggingPercentage', 'N/A'):.3f}"
            else:  # 투수
                line = f"시즌 {row['Season']}: "
                line += f"ERA {row.get('EarnedRunAverage', 'N/A'):.2f}, "
                line += f"승수 {row.get('Wins', 'N/A')}승, "
                line += f"패수 {row.get('Losses', 'N/A')}패, "
                line += f"WHIP {row.get('Whip', 'N/A'):.2f}, "
                line += f"탈삼진 {row.get('StrikeOuts', 'N/A')}개, "
                line += f"이닝 {row.get('InningsPitched', 'N/A'):.1f}"
            
            summary_lines.append(line)
        
        return "\n".join(summary_lines)
    
    def _prepare_league_averages_summary(self, league_data: pd.DataFrame, seasons: List[int], player_type: str) -> str:
        """리그 평균 데이터를 AI 분석용 텍스트로 변환"""
        if league_data.empty:
            return "리그 평균 데이터가 없습니다."
        
        relevant_data = league_data[league_data['Season'].isin(seasons)]
        if relevant_data.empty:
            return "해당 시즌의 리그 평균 데이터가 없습니다."
        
        summary_lines = []
        
        for _, row in relevant_data.iterrows():
            if player_type == "타자":
                line = f"시즌 {row['Season']} 리그 평균: "
                line += f"타율 {row.get('BattingAverage', 'N/A'):.3f}, "
                line += f"홈런 {row.get('HomeRuns', 'N/A'):.1f}개, "
                line += f"타점 {row.get('RBIs', 'N/A'):.1f}개, "
                line += f"OPS {row.get('OPS', 'N/A'):.3f}"
            else:  # 투수
                line = f"시즌 {row['Season']} 리그 평균: "
                line += f"ERA {row.get('EarnedRunAverage', 'N/A'):.2f}, "
                line += f"WHIP {row.get('Whip', 'N/A'):.2f}, "
                line += f"탈삼진 {row.get('StrikeOuts', 'N/A'):.1f}개"
            
            summary_lines.append(line)
        
        return "\n".join(summary_lines)
    
    def generate_player_analysis(
        self, 
        player_name: str,
        player_data: pd.DataFrame,
        league_averages: pd.DataFrame,
        player_type: str = "타자",
        language: str = "한국어"
    ) -> str:
        """
        선수 분석 보고서 생성
        
        Args:
            player_name: 선수명
            player_data: 선수 개인 기록 데이터
            league_averages: 리그 평균 데이터
            player_type: "타자" 또는 "투수"
            language: 분석 언어 ("한국어", "영어", "일본어")
        
        Returns:
            AI가 생성한 분석 보고서 (마크다운 형식)
        """
        try:
            # 데이터 전처리
            player_summary = self._prepare_player_data_summary(player_data, player_type)
            seasons = player_data['Season'].tolist() if not player_data.empty else []
            league_summary = self._prepare_league_averages_summary(league_averages, seasons, player_type)
            
            # 프롬프트 선택
            if player_type == "타자":
                prompt = self.batter_analysis_prompt
            else:
                prompt = self.pitcher_analysis_prompt
            
            # AI 분석 요청
            formatted_prompt = prompt.format(
                player_name=player_name,
                player_data=player_summary,
                league_averages=league_summary,
                language=language
            )
            
            response = self.llm.invoke([HumanMessage(content=formatted_prompt)])
            
            return response.content
            
        except Exception as e:
            logger.error(f"AI 분석 생성 중 오류 발생: {e}")
            return f"분석 보고서 생성 중 오류가 발생했습니다: {str(e)}"
    
    def generate_comparison_analysis(
        self,
        player1_name: str,
        player1_data: pd.DataFrame,
        player2_name: str,
        player2_data: pd.DataFrame,
        league_averages: pd.DataFrame,
        player_type: str = "타자",
        language: str = "한국어"
    ) -> str:
        """
        두 선수 비교 분석 보고서 생성
        
        Args:
            player1_name: 첫 번째 선수명
            player1_data: 첫 번째 선수 데이터
            player2_name: 두 번째 선수명
            player2_data: 두 번째 선수 데이터
            league_averages: 리그 평균 데이터
            player_type: "타자" 또는 "투수"
            language: 분석 언어
        
        Returns:
            AI가 생성한 비교 분석 보고서
        """
        try:
            comparison_prompt = f"""
당신은 MLB 데이터 분석 전문가입니다. 두 {player_type}의 기록을 비교 분석하여 종합적인 보고서를 작성해주세요.

첫 번째 선수: {player1_name}
{self._prepare_player_data_summary(player1_data, player_type)}

두 번째 선수: {player2_name}
{self._prepare_player_data_summary(player2_data, player_type)}

리그 평균 참고 데이터:
{self._prepare_league_averages_summary(league_averages, list(set(player1_data['Season'].tolist() + player2_data['Season'].tolist())), player_type)}

다음 항목들을 포함하여 {language}로 비교 분석 보고서를 작성해주세요:

1. **선수별 개요**
2. **핵심 지표 비교**
3. **강점과 약점 비교**
4. **커리어 트렌드 비교**
5. **종합 평가**

마크다운 형식으로 작성해주세요.
"""
            
            response = self.llm.invoke([HumanMessage(content=comparison_prompt)])
            return response.content
            
        except Exception as e:
            logger.error(f"비교 분석 생성 중 오류 발생: {e}")
            return f"비교 분석 보고서 생성 중 오류가 발생했습니다: {str(e)}"

def is_ai_analysis_available() -> bool:
    """AI 분석 기능 사용 가능 여부 확인"""
    return LANGCHAIN_AVAILABLE and bool(os.getenv("GOOGLE_AI_API_KEY"))

def get_ai_analysis_status() -> Dict[str, Any]:
    """AI 분석 기능 상태 정보 반환"""
    status = {
        "langchain_available": LANGCHAIN_AVAILABLE,
        "api_key_configured": bool(os.getenv("GOOGLE_AI_API_KEY")),
        "ready": is_ai_analysis_available()
    }
    return status