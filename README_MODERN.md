# MLB Player Analysis - 현대화된 웹 애플리케이션

## 🚀 빠른 시작

### 🐳 Docker 실행 (권장)

```bash
# 프로덕션 환경
./docker-build.sh prod

# 개발 환경
./docker-build.sh dev

# 서비스 중지
./docker-build.sh stop
```

### 📦 로컬 실행

**1. 의존성 설치 (최초 실행 시)**
```bash
# 백엔드 의존성
cd backend && uv sync

# 프론트엔드 의존성  
cd ../frontend && npm install
```

**2. 서버 실행**
```bash
# 백엔드 (터미널 1)
./start_backend.sh

# 프론트엔드 (터미널 2)  
./start_frontend.sh
```

### 3. 접속 정보

**Docker 프로덕션:**
- **웹 애플리케이션**: http://localhost
- **API 문서**: http://localhost:8000/docs

**Docker 개발 / 로컬:**
- **웹 애플리케이션**: http://localhost:3000
- **API 문서**: http://localhost:8001/docs

---

## 🏗️ 아키텍처

### 백엔드 (FastAPI)
```
backend/
├── app/
│   ├── main.py              # FastAPI 앱 진입점
│   ├── core/
│   │   └── config.py        # 설정 관리
│   ├── api/v1/
│   │   ├── api.py           # API 라우터 집합
│   │   └── endpoints/
│   │       ├── players.py   # 선수 관련 API
│   │       └── analysis.py  # AI 분석 API
│   ├── models/
│   │   ├── player.py        # 선수 데이터 모델
│   │   └── analysis.py      # 분석 모델
│   └── services/
│       ├── data_service.py  # 데이터 서비스
│       └── ai_service.py    # AI 분석 서비스
└── static/                  # 정적 파일
```

### 프론트엔드 (React + TypeScript)
```
frontend/
├── src/
│   ├── main.tsx            # 앱 진입점
│   ├── App.tsx             # 메인 라우터
│   ├── pages/              # 페이지 컴포넌트
│   ├── components/         # 재사용 컴포넌트
│   │   ├── layout/         # 레이아웃
│   │   ├── forms/          # 폼 컴포넌트
│   │   ├── player/         # 선수 관련
│   │   ├── charts/         # 차트
│   │   └── common/         # 공통 컴포넌트
│   ├── services/           # API 클라이언트
│   ├── hooks/              # 커스텀 훅
│   ├── types/              # TypeScript 타입
│   └── utils/              # 유틸리티
└── public/                 # 정적 자산
```

---

## 📋 주요 기능

### ✅ 구현 완료
- **선수 검색**: 이름, 팀, 시즌, 포지션별 검색
- **통계 조회**: 타자/투수 상세 통계
- **페이지네이션**: 대용량 데이터 효율적 표시
- **반응형 UI**: 모바일/데스크톱 최적화
- **API 문서**: 자동 생성된 OpenAPI 문서

### 🔄 구현 예정
- **AI 분석**: LangChain + Google Gemini 통합
- **선수 비교**: 두 선수 직접 비교
- **통계 시각화**: Chart.js 기반 차트
- **선수 상세 페이지**: 시즌별 성과 추이

---

## 🛠️ 기술 스택

### 백엔드
- **FastAPI**: 고성능 웹 프레임워크
- **Pydantic**: 데이터 검증 및 시리얼화
- **Uvicorn**: ASGI 서버
- **Pandas**: 데이터 처리
- **LangChain + Google Gemini**: AI 분석

### 프론트엔드
- **React 18**: UI 라이브러리
- **TypeScript**: 타입 안전성
- **Vite**: 빌드 도구
- **Tailwind CSS**: 유틸리티 CSS
- **React Query**: 서버 상태 관리
- **React Router**: 클라이언트 사이드 라우팅
- **Chart.js**: 데이터 시각화

---

## 🔧 개발 도구

### 코드 품질
```bash
# TypeScript 타입 체크
cd frontend && npm run type-check

# 린트 검사
cd frontend && npm run lint

# 빌드 테스트
cd frontend && npm run build
```

### 개발 환경
- **Hot Reload**: 코드 변경 시 자동 새로고침
- **API 프록시**: 개발 중 CORS 문제 해결
- **TypeScript**: 개발 시점 타입 검사

---

## 📊 데이터

### 데이터셋
- **타자 통계**: `data/mlb_batter_stats_2000_2023.csv`
- **투수 통계**: `data/mlb_pitcher_stats_2000_2023.csv`
- **기간**: 2000년 ~ 2023년 (24시즌)

### 주요 통계 지표

**타자**
- AVG (타율), OBP (출루율), SLG (장타율), OPS
- HR (홈런), RBI (타점), H (안타), R (득점)
- SB (도루), SO (삼진), BB (볼넷)

**투수**
- ERA (평균자책점), WHIP, W (승), L (패)
- SV (세이브), SO (삼진), IP (이닝), H (피안타)

---

## 🚨 문제 해결

### 백엔드 서버가 시작되지 않는 경우
```bash
# 포트 충돌 확인
lsof -i :8001

# 다른 포트 사용
cd backend && PYTHONPATH=$(pwd) uv run uvicorn app.main:app --port 8002
```

### 프론트엔드 빌드 오류
```bash
# 의존성 재설치
cd frontend
rm -rf node_modules package-lock.json
npm install

# 캐시 정리
npm run dev -- --force
```

### AI 분석 기능 오류
```bash
# 환경변수 확인
echo $GOOGLE_API_KEY

# .env 파일 확인
cat backend/.env
```

---

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.