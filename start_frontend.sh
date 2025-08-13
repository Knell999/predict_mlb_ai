#!/bin/bash

# MLB Analytics Frontend 시작 스크립트
echo "🎨 React 프론트엔드를 시작합니다..."

cd "$(dirname "$0")/frontend"

# 프론트엔드 개발 서버 실행
echo "🌐 프론트엔드가 http://localhost:3000 (또는 3001) 에서 실행됩니다"
echo "🔗 백엔드 API: http://localhost:8001"
echo "🛑 종료하려면 Ctrl+C를 누르세요"

npm run dev