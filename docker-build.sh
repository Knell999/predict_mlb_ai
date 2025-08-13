#!/bin/bash

echo "🐳 MLB Analysis Docker 빌드 및 실행"
echo "=================================="

# 환경변수 파일 확인
if [ ! -f ./backend/.env ]; then
    echo "❌ backend/.env 파일이 없습니다."
    echo "   GOOGLE_API_KEY를 포함한 환경변수를 설정해주세요."
    exit 1
fi

echo "📋 사용 가능한 명령어:"
echo "  dev  : 개발 환경 실행 (코드 변경 시 자동 리로드)"
echo "  prod : 프로덕션 환경 실행"
echo "  stop : 모든 컨테이너 중지"
echo "  logs : 로그 확인"
echo ""

# 첫 번째 인자가 없으면 prod로 기본 설정
COMMAND=${1:-prod}

case $COMMAND in
    "dev")
        echo "🔧 개발 환경 실행 중..."
        echo ""
        echo "접속 정보:"
        echo "  프론트엔드: http://localhost:3000"
        echo "  백엔드 API: http://localhost:8001"
        echo "  API 문서: http://localhost:8001/docs"
        echo ""
        docker-compose -f docker-compose.dev.yml up --build
        ;;
    
    "prod")
        echo "🚀 프로덕션 환경 실행 중..."
        echo ""
        echo "접속 정보:"
        echo "  웹 애플리케이션: http://localhost"
        echo "  백엔드 API: http://localhost:8000"
        echo "  API 문서: http://localhost:8000/docs"
        echo ""
        docker-compose up --build -d
        echo "✅ 서비스가 백그라운드에서 실행 중입니다."
        echo "📊 상태 확인: docker-compose ps"
        echo "📝 로그 확인: ./docker-build.sh logs"
        ;;
    
    "stop")
        echo "🛑 모든 컨테이너 중지 중..."
        docker-compose down
        docker-compose -f docker-compose.dev.yml down
        echo "✅ 모든 컨테이너가 중지되었습니다."
        ;;
    
    "logs")
        echo "📝 실시간 로그 확인 (Ctrl+C로 종료)"
        docker-compose logs -f
        ;;
    
    *)
        echo "❌ 잘못된 명령어입니다."
        echo "사용법: $0 [dev|prod|stop|logs]"
        exit 1
        ;;
esac