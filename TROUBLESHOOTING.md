# 🚨 문제 해결 가이드

## 📋 실행 전 체크리스트

### 1. 백엔드 실행 확인
```bash
# 터미널 1
cd /Users/hyunjong/Desktop/dev/personal/predict_mlb
./start_backend.sh

# 다음 메시지가 표시되어야 합니다:
# ✅ "INFO: Application startup complete."
# ✅ "🚀 MLB Analysis API 시작"
```

### 2. 프론트엔드 실행 확인
```bash
# 터미널 2  
cd /Users/hyunjong/Desktop/dev/personal/predict_mlb
./start_frontend.sh

# 다음 메시지가 표시되어야 합니다:
# ✅ "VITE v5.x.x ready"
# ✅ "Local: http://localhost:3000/" (또는 3001)
```

### 3. 연결 테스트
- 백엔드: http://localhost:8001/api/v1/players/summary
- 프론트엔드: http://localhost:3000 (또는 3001)
- API 문서: http://localhost:8001/docs

---

## 🔧 일반적인 오류 해결

### 백엔드 오류

#### "ModuleNotFoundError: No module named 'app.core'"
```bash
cd backend
export PYTHONPATH=$(pwd)
uv run uvicorn app.main:app --reload --port 8001
```

#### "Address already in use" (포트 충돌)
```bash
# 포트 사용 확인
lsof -i :8001

# 프로세스 종료
kill -9 [PID]

# 또는 다른 포트 사용
uv run uvicorn app.main:app --reload --port 8002
```

#### "ValidationError: google_api_key"
```bash
# .env 파일 확인
cat backend/.env

# GOOGLE_API_KEY가 설정되어 있는지 확인
# 없다면 추가:
echo "GOOGLE_API_KEY=your_api_key_here" >> backend/.env
```

### 프론트엔드 오류

#### "npm install" 의존성 오류
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### TypeScript 컴파일 오류
```bash
cd frontend
npm run type-check

# 오류가 있다면:
npm run lint -- --fix
```

#### "Port 3000 is in use"
```bash
# 자동으로 3001로 변경됨 (정상)
# 브라우저에서 표시된 포트로 접속
```

---

## 🌐 브라우저 접속 시 오류

### "백엔드 서버 연결 실패" 표시
1. 백엔드 서버가 실행 중인지 확인
2. http://localhost:8001/api/v1/players/summary 직접 접속
3. 방화벽/보안 소프트웨어 확인

### 페이지가 로드되지 않음
1. 브라우저 캐시 삭제 (Cmd+Shift+R)
2. 개발자 도구 Console 탭에서 오류 확인
3. Network 탭에서 API 요청 실패 확인

### API 요청 실패 (CORS 오류)
```bash
# 백엔드 CORS 설정 확인
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     http://localhost:8001/api/v1/players/summary
```

---

## 🔍 상세 디버깅

### 백엔드 로그 확인
```bash
cd backend
tail -f logs/app_*.log
```

### API 직접 테스트
```bash
# 통계 요약
curl http://localhost:8001/api/v1/players/summary

# 선수 검색
curl "http://localhost:8001/api/v1/players/search?query=Ohtani"

# 팀 목록
curl http://localhost:8001/api/v1/players/teams
```

### 프론트엔드 디버깅
1. 브라우저 개발자 도구 열기 (F12)
2. Console 탭에서 JavaScript 오류 확인
3. Network 탭에서 API 요청/응답 확인
4. 홈페이지에 "✅ 백엔드 연결 성공" 메시지 확인

---

## 🚨 긴급 문제 해결

### 모든 서버 종료 후 재시작
```bash
# 모든 관련 프로세스 종료
pkill -f uvicorn
pkill -f vite
pkill -f node

# 5초 대기
sleep 5

# 백엔드 재시작 (터미널 1)
cd /Users/hyunjong/Desktop/dev/personal/predict_mlb
./start_backend.sh

# 프론트엔드 재시작 (터미널 2)  
./start_frontend.sh
```

### 완전 초기화
```bash
cd /Users/hyunjong/Desktop/dev/personal/predict_mlb

# 프론트엔드 의존성 재설치
cd frontend
rm -rf node_modules package-lock.json
npm install

# 백엔드 의존성 재설치
cd ../
uv sync

# 캐시 정리
rm -rf frontend/.vite
rm -rf backend/__pycache__ backend/app/__pycache__
```

---

## 📞 추가 도움

### 로그 파일 위치
- 백엔드 로그: `backend/logs/`
- 프론트엔드 로그: 브라우저 개발자 도구

### 포트 정보
- 백엔드: 8001
- 프론트엔드: 3000 (사용 중일 경우 3001)
- API 문서: 8001/docs

### 주요 파일
- 백엔드 설정: `backend/app/core/config.py`
- 환경변수: `backend/.env`
- 프론트엔드 설정: `frontend/vite.config.ts`