#!/bin/bash

# MLB Analytics Backend 시작 스크립트
echo "🚀 FastAPI 백엔드 서버를 시작합니다..."

cd "$(dirname "$0")/backend"

# 환경변수 설정
export PYTHONPATH="$(pwd)"

# uv를 통해 서버 실행
echo ""
echo "📡 서버가 http://localhost:8001 에서 실행됩니다"
echo "📖 API 문서: http://localhost:8001/docs"
echo "🔍 API 테스트: http://localhost:8001/api/v1/players/summary"
echo "🛑 종료하려면 Ctrl+C를 누르세요"
echo ""

uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8001