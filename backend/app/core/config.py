"""
애플리케이션 설정 관리

환경변수와 기본값을 통한 설정 관리
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정 클래스"""
    
    # 프로젝트 기본 정보
    project_name: str = "MLB Player Analysis API"
    version: str = "1.0.0"
    description: str = "MLB 선수 기록 분석 및 예측 API"
    
    # 환경 설정
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")
    
    # API 설정
    api_v1_str: str = "/api/v1"
    
    # CORS 설정
    allowed_hosts: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5173",  # Vite 개발 서버
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173"
        ],
        alias="ALLOWED_HOSTS"
    )
    
    # 데이터베이스 설정 (향후 확장용)
    database_url: Optional[str] = Field(default=None, alias="DATABASE_URL")
    
    # Google AI API 설정
    google_api_key: Optional[str] = Field(default=None, alias="GOOGLE_API_KEY")
    
    # 데이터 파일 경로
    base_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent)
    data_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent / "data")
    
    @property
    def batter_stats_file(self) -> Path:
        """타자 통계 파일 경로"""
        return self.data_dir / "mlb_batter_stats_2000_2023.csv"
    
    @property
    def pitcher_stats_file(self) -> Path:
        """투수 통계 파일 경로"""
        return self.data_dir / "mlb_pitcher_stats_2000_2023.csv"
    
    # 로그 설정
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent / "logs")
    
    # 캐싱 설정
    cache_expire_seconds: int = Field(default=3600, alias="CACHE_EXPIRE_SECONDS")  # 1시간
    
    # AI 분석 설정
    ai_analysis_enabled: bool = Field(default=True, alias="AI_ANALYSIS_ENABLED")
    ai_model_name: str = Field(default="gemini-2.5-flash", alias="AI_MODEL_NAME")
    ai_temperature: float = Field(default=0.3, alias="AI_TEMPERATURE")
    ai_max_tokens: int = Field(default=65000, alias="AI_MAX_TOKENS")
    
    # 예측 모델 설정
    prediction_enabled: bool = Field(default=True, alias="PREDICTION_ENABLED")
    prediction_cache_hours: int = Field(default=24, alias="PREDICTION_CACHE_HOURS")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # extra 필드 무시


# 글로벌 설정 인스턴스
settings = Settings()


def get_settings() -> Settings:
    """설정 인스턴스 반환 (의존성 주입용)"""
    return settings