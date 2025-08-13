# 🐳 Docker 실행 가이드

## 📋 사전 요구사항

### 1. Docker 설치
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) 설치
- Docker Compose 포함 (Docker Desktop에 기본 포함)

### 2. 환경변수 설정
```bash
# backend/.env 파일에 Google API 키 설정
GOOGLE_API_KEY=your_google_api_key_here
```

---

## 🚀 빠른 시작

### 프로덕션 환경 (권장)
```bash
./docker-build.sh prod
```

### 개발 환경
```bash
./docker-build.sh dev
```

### 서비스 중지
```bash
./docker-build.sh stop
```

---

## 🌐 접속 정보

### 프로덕션 환경
- **웹 애플리케이션**: http://localhost
- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

### 개발 환경
- **프론트엔드**: http://localhost:3000
- **백엔드 API**: http://localhost:8001
- **API 문서**: http://localhost:8001/docs

---

## 🔧 상세 명령어

### 1. 프로덕션 빌드 및 실행
```bash
# 백그라운드 실행
docker-compose up --build -d

# 포그라운드 실행 (로그 확인용)
docker-compose up --build

# 서비스 중지
docker-compose down
```

### 2. 개발 환경 실행
```bash
# 개발 서버 실행 (코드 변경 시 자동 리로드)
docker-compose -f docker-compose.dev.yml up --build

# 백그라운드 실행
docker-compose -f docker-compose.dev.yml up --build -d
```

### 3. 개별 서비스 관리
```bash
# 백엔드만 실행
docker-compose up backend

# 프론트엔드만 실행  
docker-compose up frontend

# 특정 서비스 재시작
docker-compose restart backend
```

### 4. 로그 및 디버깅
```bash
# 실시간 로그 확인
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f backend
docker-compose logs -f frontend

# 컨테이너 내부 접속
docker exec -it mlb-backend bash
docker exec -it mlb-frontend sh
```

---

## 📊 모니터링

### 서비스 상태 확인
```bash
# 실행 중인 컨테이너 확인
docker-compose ps

# 리소스 사용량 확인
docker stats

# 헬스체크 상태 확인
docker inspect mlb-backend | grep Health -A 10
```

### 데이터 볼륨 관리
```bash
# 볼륨 목록 확인
docker volume ls

# 볼륨 정보 확인
docker volume inspect predict_mlb_mlb-data
```

---

## 🛠️ 문제 해결

### 포트 충돌
```bash
# 포트 사용 확인
lsof -i :80,8000,3000,8001

# 다른 포트로 실행
docker-compose up --build -e BACKEND_PORT=8002
```

### 빌드 오류
```bash
# 캐시 없이 재빌드
docker-compose build --no-cache

# 이미지 정리
docker system prune -a
```

### 환경변수 문제
```bash
# 환경변수 확인
docker exec mlb-backend env | grep GOOGLE

# .env 파일 확인
cat backend/.env
```

### 데이터 파일 문제
```bash
# 볼륨 마운트 확인
docker exec mlb-backend ls -la /app/data/

# 권한 문제 해결
docker exec mlb-backend chmod -R 755 /app/data/
```

---

## 🏗️ 아키텍처

### 컨테이너 구조
```
mlb-network (Docker Network)
├── mlb-backend (FastAPI)
│   ├── Port: 8000
│   ├── Health Check: /api/v1/players/summary
│   └── Volumes: data/, logs/
│
└── mlb-frontend (React + Nginx)
    ├── Port: 80
    ├── Proxy: /api/* → backend:8000
    └── Static Files: /usr/share/nginx/html
```

### 데이터 흐름
1. **브라우저** → **Nginx (Frontend Container)**
2. **Nginx** → API 요청을 **FastAPI (Backend Container)**로 프록시
3. **FastAPI** → 데이터 파일에서 정보 로드 및 처리
4. **응답** → Nginx → 브라우저

---

## 🚀 프로덕션 배포

### 환경변수 최적화
```bash
# 프로덕션용 환경변수
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
```

### 리버스 프록시 설정 (선택사항)
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 자동 재시작 설정
```yaml
# docker-compose.yml에서
restart: unless-stopped
```

---

## 💡 팁 & 최적화

### 이미지 크기 최적화
- 멀티스테이지 빌드 사용 (이미 적용됨)
- Alpine 리눅스 기반 이미지 사용
- 불필요한 파일 .dockerignore에 추가

### 성능 최적화
- Nginx에서 정적 파일 캐싱 활성화 (이미 적용됨)
- Gzip 압축 활성화 (이미 적용됨)
- 헬스체크로 서비스 안정성 확보

### 보안 강화
- 보안 헤더 추가 (이미 적용됨)
- 비특권 사용자로 컨테이너 실행
- 민감한 정보는 Docker secrets 사용

---

## 📚 추가 자료

- [Docker Compose 문서](https://docs.docker.com/compose/)
- [FastAPI Docker 가이드](https://fastapi.tiangolo.com/deployment/docker/)
- [React Docker 빌드 최적화](https://docs.docker.com/language/nodejs/)