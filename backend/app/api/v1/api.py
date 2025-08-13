"""
API v1 라우터 집합

모든 v1 엔드포인트를 하나로 모으는 메인 라우터
"""

from fastapi import APIRouter

from app.api.v1.endpoints import players, analysis

# API v1 메인 라우터
api_router = APIRouter()

# 엔드포인트 라우터 등록
api_router.include_router(players.router)
api_router.include_router(analysis.router)