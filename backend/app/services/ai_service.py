"""
AI 분석 서비스

LangChain + Google Gemini 기반 선수 분석 기능
"""

import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import pandas as pd

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.schema import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from app.models.player import PlayerType


class AIService:
    """AI 분석 서비스 클래스"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_AI_API_KEY")
        self.llm = None
        
        if LANGCHAIN_AVAILABLE and self.api_key:
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash",
                    google_api_key=self.api_key,
                    temperature=0.3,
                    max_tokens=65000
                )
            except Exception as e:
                print(f"AI 모델 초기화 실패: {e}")
    
    def is_available(self) -> bool:
        """AI 분석 기능 사용 가능 여부"""
        return LANGCHAIN_AVAILABLE and self.llm is not None and self.api_key is not None
    
    def analyze_player(
        self,
        player_name: str,
        player_data: List[Dict[str, Any]],
        player_type: PlayerType,
        language: str = "korean",
        analysis_type: str = "individual"
    ) -> str:
        """선수 개별 분석"""
        
        if not self.is_available():
            return "AI 분석 기능을 사용할 수 없습니다. API 키를 확인해주세요."
        
        try:
            # 선수 데이터를 DataFrame으로 변환
            df = pd.DataFrame(player_data)
            
            # 언어별 시스템 메시지
            system_messages = {
                "korean": self._get_korean_system_message(player_type),
                "english": self._get_english_system_message(player_type),
                "japanese": self._get_japanese_system_message(player_type)
            }
            
            # 선수 데이터 요약
            data_summary = self._create_data_summary(df, player_type, language)
            
            # 프롬프트 생성
            prompt = self._create_analysis_prompt(
                player_name, data_summary, player_type, language
            )
            
            # AI 분석 실행
            messages = [
                SystemMessage(content=system_messages.get(language, system_messages["korean"])),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm(messages)
            return response.content
            
        except Exception as e:
            return f"AI 분석 중 오류가 발생했습니다: {str(e)}"
    
    def compare_players(
        self,
        player1_name: str,
        player1_data: List[Dict[str, Any]],
        player2_name: str,
        player2_data: List[Dict[str, Any]],
        player_type: PlayerType,
        language: str = "korean"
    ) -> str:
        """선수 비교 분석"""
        
        if not self.is_available():
            return "AI 분석 기능을 사용할 수 없습니다. API 키를 확인해주세요."
        
        try:
            # 데이터를 DataFrame으로 변환
            df1 = pd.DataFrame(player1_data)
            df2 = pd.DataFrame(player2_data)
            
            # 언어별 시스템 메시지
            system_messages = {
                "korean": self._get_korean_comparison_system_message(player_type),
                "english": self._get_english_comparison_system_message(player_type),
                "japanese": self._get_japanese_comparison_system_message(player_type)
            }
            
            # 데이터 요약
            summary1 = self._create_data_summary(df1, player_type, language)
            summary2 = self._create_data_summary(df2, player_type, language)
            
            # 비교 프롬프트 생성
            prompt = self._create_comparison_prompt(
                player1_name, summary1, player2_name, summary2, player_type, language
            )
            
            # AI 분석 실행
            messages = [
                SystemMessage(content=system_messages.get(language, system_messages["korean"])),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm(messages)
            return response.content
            
        except Exception as e:
            return f"선수 비교 분석 중 오류가 발생했습니다: {str(e)}"
    
    def _create_data_summary(
        self, 
        df: pd.DataFrame, 
        player_type: PlayerType, 
        language: str
    ) -> str:
        """선수 데이터 요약 생성"""
        
        if df.empty:
            return "데이터가 없습니다."
        
        summary = []
        
        # 기본 정보
        if 'Season' in df.columns:
            seasons = sorted(df['Season'].unique())
            summary.append(f"시즌: {seasons[0]}-{seasons[-1]} ({len(seasons)}시즌)")
        
        if 'Team' in df.columns:
            teams = df['Team'].unique()
            summary.append(f"팀: {', '.join(teams)}")
        
        # 타자 통계 요약
        if player_type == PlayerType.BATTER:
            stats_summary = self._create_batter_summary(df, language)
        else:
            stats_summary = self._create_pitcher_summary(df, language)
        
        summary.extend(stats_summary)
        
        return "\n".join(summary)
    
    def _create_batter_summary(self, df: pd.DataFrame, language: str) -> List[str]:
        """타자 통계 요약"""
        summary = []
        
        # 주요 통계
        stats_columns = {
            'AVG': '타율',
            'OBP': '출루율', 
            'SLG': '장타율',
            'OPS': 'OPS',
            'HR': '홈런',
            'RBI': '타점',
            'H': '안타',
            'R': '득점'
        }
        
        for col, name in stats_columns.items():
            if col in df.columns:
                avg_val = df[col].mean()
                max_val = df[col].max()
                summary.append(f"{name}: 평균 {avg_val:.3f}, 최고 {max_val:.3f}")
        
        return summary
    
    def _create_pitcher_summary(self, df: pd.DataFrame, language: str) -> List[str]:
        """투수 통계 요약"""
        summary = []
        
        # 주요 통계
        stats_columns = {
            'ERA': '평균자책점',
            'WHIP': 'WHIP',
            'W': '승',
            'L': '패',
            'SV': '세이브',
            'SO': '삼진',
            'IP': '이닝'
        }
        
        for col, name in stats_columns.items():
            if col in df.columns:
                if col in ['ERA', 'WHIP']:
                    avg_val = df[col].mean()
                    min_val = df[col].min()
                    summary.append(f"{name}: 평균 {avg_val:.2f}, 최소 {min_val:.2f}")
                else:
                    total_val = df[col].sum()
                    avg_val = df[col].mean()
                    summary.append(f"{name}: 총 {total_val}, 평균 {avg_val:.1f}")
        
        return summary
    
    def _get_korean_system_message(self, player_type: PlayerType) -> str:
        """한국어 시스템 메시지"""
        position = "타자" if player_type == PlayerType.BATTER else "투수"
        
        return f"""당신은 MLB {position} 전문 분석가입니다. 
다음 지침을 따라 선수를 분석해주세요:

1. 제공된 통계 데이터를 기반으로 객관적이고 전문적인 분석을 제공
2. 선수의 강점과 약점을 명확히 구분하여 설명
3. 시즌별 성장 또는 하락 추세 분석
4. 리그 평균 대비 성능 평가
5. 향후 전망에 대한 합리적 예측

분석은 한국어로 작성하며, 전문 용어를 사용하되 이해하기 쉽게 설명해주세요."""
    
    def _get_english_system_message(self, player_type: PlayerType) -> str:
        """영어 시스템 메시지"""
        position = "batter" if player_type == PlayerType.BATTER else "pitcher"
        
        return f"""You are a professional MLB {position} analyst. 
Please follow these guidelines for player analysis:

1. Provide objective and professional analysis based on the statistical data
2. Clearly distinguish and explain player's strengths and weaknesses  
3. Analyze seasonal growth or decline trends
4. Evaluate performance compared to league averages
5. Provide reasonable predictions for future prospects

Write the analysis in English using professional terminology while keeping it accessible."""
    
    def _get_japanese_system_message(self, player_type: PlayerType) -> str:
        """일본어 시스템 메시지"""
        position = "打者" if player_type == PlayerType.BATTER else "投手"
        
        return f"""あなたはMLB{position}の専門分析者です。
以下のガイドラインに従って選手を分析してください：

1. 提供された統計データに基づいた客観的で専門的な分析を提供
2. 選手の長所と短所を明確に区別して説明
3. シーズン別の成長または下降トレンドを分析  
4. リーグ平均との比較による成績評価
5. 今後の展望について合理的な予測

分析は日本語で作成し、専門用語を使用しながらも分かりやすく説明してください。"""
    
    def _get_korean_comparison_system_message(self, player_type: PlayerType) -> str:
        """한국어 비교 분석 시스템 메시지"""
        return f"""당신은 MLB 선수 비교 전문 분석가입니다.
두 선수의 통계를 비교하여 다음과 같이 분석해주세요:

1. 주요 통계 지표별 직접 비교
2. 각 선수의 스타일과 특징 분석
3. 상황별 성능 비교 (홈/원정, 시즌별 등)
4. 팀에 대한 기여도 평가
5. 전반적인 선수 등급 비교

객관적이고 균형잡힌 시각으로 분석해주세요."""
    
    def _get_english_comparison_system_message(self, player_type: PlayerType) -> str:
        """영어 비교 분석 시스템 메시지"""
        return f"""You are a professional MLB player comparison analyst.
Please compare the two players' statistics as follows:

1. Direct comparison of major statistical indicators
2. Analysis of each player's style and characteristics
3. Situational performance comparison (home/away, by season, etc.)
4. Team contribution evaluation
5. Overall player rating comparison

Please provide objective and balanced analysis."""
    
    def _get_japanese_comparison_system_message(self, player_type: PlayerType) -> str:
        """일본어 비교 분석 시스템 메시지"""
        return f"""あなたはMLB選手比較の専門分析者です。
二人の選手の統計を比較して以下のように分析してください：

1. 主要統計指標の直接比較
2. 各選手のスタイルと特徴分析
3. 状況別パフォーマンス比較（ホーム/アウェイ、シーズン別など）
4. チームへの貢献度評価
5. 総合的な選手評価比較

客観的でバランスの取れた視点で分析してください。"""
    
    def _create_analysis_prompt(
        self,
        player_name: str,
        data_summary: str,
        player_type: PlayerType,
        language: str
    ) -> str:
        """분석 프롬프트 생성"""
        
        prompts = {
            "korean": f"""
{player_name} 선수에 대한 상세한 분석을 요청합니다.

선수 데이터:
{data_summary}

다음 항목들을 포함하여 종합적으로 분석해주세요:
1. 전반적인 성능 평가
2. 주요 강점과 약점
3. 시즌별 변화 추이
4. 리그 내 위치와 비교
5. 향후 전망

분석 결과는 마크다운 형식으로 작성해주세요.
""",
            "english": f"""
Please provide a detailed analysis of player {player_name}.

Player Data:
{data_summary}

Please include comprehensive analysis covering:
1. Overall performance evaluation
2. Key strengths and weaknesses  
3. Season-by-season trends
4. League position and comparisons
5. Future prospects

Please format the analysis in markdown.
""",
            "japanese": f"""
{player_name}選手の詳細な分析をお願いします。

選手データ：
{data_summary}

以下の項目を含めて総合的に分析してください：
1. 全体的なパフォーマンス評価
2. 主な長所と短所
3. シーズン別変化トレンド
4. リーグ内での位置と比較
5. 今後の展望

分析結果はマークダウン形式で作成してください。
"""
        }
        
        return prompts.get(language, prompts["korean"])
    
    def _create_comparison_prompt(
        self,
        player1_name: str,
        summary1: str,
        player2_name: str,
        summary2: str,
        player_type: PlayerType,
        language: str
    ) -> str:
        """비교 분석 프롬프트 생성"""
        
        prompts = {
            "korean": f"""
{player1_name}과 {player2_name} 두 선수의 비교 분석을 요청합니다.

{player1_name} 데이터:
{summary1}

{player2_name} 데이터:
{summary2}

다음 항목들을 포함하여 비교 분석해주세요:
1. 주요 통계 지표 비교
2. 각 선수의 특징과 스타일
3. 강점과 약점 비교
4. 팀 기여도 평가
5. 종합적인 선수 평가

분석 결과는 마크다운 형식으로 작성해주세요.
""",
            "english": f"""
Please provide a comparative analysis between {player1_name} and {player2_name}.

{player1_name} Data:
{summary1}

{player2_name} Data:  
{summary2}

Please include comparative analysis covering:
1. Major statistical indicators comparison
2. Each player's characteristics and style
3. Strengths and weaknesses comparison
4. Team contribution evaluation
5. Overall player assessment

Please format the analysis in markdown.
""",
            "japanese": f"""
{player1_name}と{player2_name}の比較分析をお願いします。

{player1_name}のデータ：
{summary1}

{player2_name}のデータ：
{summary2}

以下の項目を含めて比較分析してください：
1. 主要統計指標の比較
2. 各選手の特徴とスタイル
3. 長所と短所の比較
4. チーム貢献度評価
5. 総合的な選手評価

分析結果はマークダウン形式で作成してください。
"""
        }
        
        return prompts.get(language, prompts["korean"])


# 싱글톤 인스턴스
_ai_service_instance = None

def get_ai_service() -> AIService:
    """AI 서비스 인스턴스 반환"""
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    return _ai_service_instance