"""
MLB 선수 분석 FastAPI 애플리케이션

LangChain과 Google Gemini를 활용한 MLB 선수 기록 분석 및 예측 API
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from pathlib import Path

from app.core.config import settings
from app.api.v1.api import api_router


# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 라이프사이클 관리"""
    logger.info("🚀 MLB Analysis API 시작")
    logger.info(f"환경: {settings.environment}")
    logger.info(f"디버그 모드: {settings.debug}")
    
    yield
    
    logger.info("🛑 MLB Analysis API 종료")


# FastAPI 앱 생성
app = FastAPI(
    title=settings.project_name,
    description="""
    MLB 선수 기록 조회, 분석 및 예측을 위한 RESTful API
    
    ## 주요 기능
    - 선수 기록 조회 및 검색
    - 통계 분석 및 시각화 데이터
    - AI 기반 선수 분석 보고서
    - Prophet 기반 성과 예측
    - 리그 트렌드 분석
    
    ## 기술 스택
    - FastAPI (웹 프레임워크)
    - Pandas (데이터 처리)
    - Prophet (시계열 예측)
    - LangChain + Google Gemini (AI 분석)
    """,
    version=settings.version,
    openapi_url=f"{settings.api_v1_str}/openapi.json" if settings.debug else None,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙
static_path = Path(__file__).parent.parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# API 라우터 등록
app.include_router(api_router, prefix=settings.api_v1_str)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "MLB 선수 분석 API",
        "version": settings.version,
        "docs_url": "/docs" if settings.debug else "Documentation disabled in production",
        "api_base": settings.api_v1_str
    }


@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": settings.version
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )