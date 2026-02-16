# MLB 선수 기록 조회 및 AI 분석 플랫폼

[![CI/CD](https://github.com/yourusername/predict_mlb_ai/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/yourusername/predict_mlb_ai/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 프로젝트 개요

MLB(Major League Baseball) 선수들의 기록을 조회하고 분석하며, **LangGraph 기반 6개 AI Agent**를 활용하여 대화형 분석, 지능형 예측, 유사 선수 탐색, 데이터 품질 검증, 종합 리포트 생성까지 수행하는 **멀티 에이전트 시스템** 기반 웹 애플리케이션입니다.

## 주요 기능

### 📊 데이터 분석
- **선수 기록 조회**: 타자와 투수의 상세 기록 조회 및 시각화 (선수기준/시즌기준)
- **리그 트렌드 분석**: MLB 리그 전체의 여러 지표 변화 추이 분석
- **선수 비교**: 두 선수의 기록을 직접 비교 및 시각화
- **데이터 품질 검증**: 4단계 자동 검증 (파일/스키마/범위/이상치)

### 🤖 AI 기능 (LangGraph 멀티 에이전트)
- **대화형 AI 분석**: 자연어로 선수 정보 질문 및 다회차 대화 (5개 분석 유형 자동 라우팅)
- **지능형 예측**: Prophet 예측 결과를 LLM이 해석하여 신뢰도 평가 및 자연어 설명
- **유사 선수 탐색**: 유클리드 거리 기반 유사도로 유사 선수 자동 추천 및 비교
- **종합 리포트 생성**: 선수 프로필, 지표, 트렌드, 예측, 비교를 포함한 5개 섹션 자동 생성 + 마크다운 다운로드
- **AI 데이터 품질 분석**: 통계적 이상치 자동 탐지 및 LLM 해석
- **자동 업데이트 오케스트레이션**: 소스 선택, 백업, 실행, 검증, Fail-over 자율 처리

### 🌐 기타
- **다국어 지원**: 한국어, 영어, 일본어 완전 지원
- **반응형 UI**: Streamlit 기반 직관적 인터페이스

## 기술 스택

### 핵심 기술
- **AI Framework**: LangChain, LangGraph (StateGraph 기반 멀티 에이전트)
- **LLM**: Google Gemini 2.5 Pro
- **예측 모델**: Facebook Prophet (시계열 예측)
- **프론트엔드**: Streamlit
- **데이터 처리**: Pandas, NumPy
- **데이터 시각화**: Matplotlib, Seaborn, Plotly

### 데이터 수집
- **PyBaseball**: 안정적이고 빠른 데이터 수집
- **MLB Stats API**: 최신 데이터 제공

### DevOps
- **테스트**: pytest (150개 테스트 케이스)
- **CI/CD**: GitHub Actions (자동 테스트 + Docker 빌드)
- **컨테이너**: Docker (멀티스테이지 빌드)
- **스케줄링**: schedule (시즌/비시즌 자동 업데이트)

## 빠른 시작

### 요구사항
- Python 3.11 이상
- UV 패키지 매니저 (권장) 또는 pip

### 설치 방법

#### UV 사용 (권장)
```bash
# 1. 저장소 클론
git clone https://github.com/yourusername/predict_mlb_ai.git
cd predict_mlb_ai

# 2. UV 설치 (아직 없다면)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. 의존성 설치
uv sync

# 4. 애플리케이션 실행
uv run streamlit run app.py
```

#### pip 사용
```bash
# 1. 저장소 클론
git clone https://github.com/yourusername/predict_mlb_ai.git
cd predict_mlb_ai

# 2. 가상 환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
# .venv\Scripts\activate   # Windows

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 애플리케이션 실행
streamlit run app.py
```

### AI 기능 설정 (선택 사항)

AI Agent 기능을 사용하려면 Google Gemini API 키가 필요합니다:

```bash
# 1. .env 파일 생성
echo "GOOGLE_AI_API_KEY=your_api_key_here" > .env

# 2. Google AI Studio에서 API 키 발급
# https://makersuite.google.com/app/apikey

# 3. AI 기능 상태 확인
python -c "from agents.base import is_llm_available; print('AI 사용 가능' if is_llm_available() else 'API 키 필요')"
```

**참고**: AI 기능 없이도 앱의 핵심 기능(데이터 조회, 시각화, Prophet 예측)은 정상 동작합니다 (Graceful Degradation).

## 프로젝트 구조

```
predict_mlb_ai/
├── agents/                          # LangGraph AI Agent 시스템
│   ├── base.py                      # Agent 공통 기능 (LLM 생성, 가용성 체크)
│   ├── tools/                       # Agent가 사용하는 도구 모음
│   │   ├── data_tools.py            # 데이터 조회 도구 (8개)
│   │   ├── stats_tools.py           # 통계 계산 도구 (3개)
│   │   ├── prediction_tools.py      # 예측 도구 (2개)
│   │   ├── similarity_tools.py      # 유사도 도구 (2개)
│   │   └── quality_tools.py         # 품질 검증 도구 (3개)
│   ├── conversational/              # 대화형 분석 Agent
│   │   ├── state.py                 # ConversationalState 정의
│   │   ├── nodes.py                 # 8개 노드 (의도 분류, 라우팅 등)
│   │   └── graph.py                 # StateGraph 정의
│   ├── prediction/                  # 지능형 예측 Agent
│   ├── similarity/                  # 유사 선수 탐색 Agent
│   ├── quality/                     # 데이터 품질 Agent
│   ├── report/                      # 종합 리포트 Agent
│   └── update/                      # 데이터 업데이트 Agent
├── data/                            # 데이터 파일
│   ├── mlb_batter_stats_2000_2023.csv
│   └── mlb_pitcher_stats_2000_2023.csv
├── font/                            # 한글 폰트
│   └── H2GTRM.TTF
├── logs/                            # 로그 파일
├── tests/                           # 테스트 (150개)
│   ├── unit/                        # 단위 테스트 (38개)
│   │   ├── test_agent_tools.py
│   │   ├── test_agent_states.py
│   │   └── test_agent_nodes.py
│   └── integration/                 # 통합 테스트 (12개)
│       ├── test_conversational_agent.py
│       ├── test_prediction_agent.py
│       └── test_quality_agent.py
├── .github/workflows/               # CI/CD 파이프라인
│   └── ci.yml
├── app.py                           # 메인 애플리케이션
├── chat_page.py                     # AI 채팅 페이지 (NEW)
├── search.py                        # 선수 기록 조회 (+ 리포트 생성)
├── predict.py                       # 성과 예측 (+ AI 해석)
├── compare.py                       # 선수 비교 (+ 유사 선수 탐색)
├── trend.py                         # 리그 트렌드 분석
├── data_status.py                   # 데이터 상태 (+ AI 품질 분석)
├── home.py                          # 홈 페이지
├── config.py                        # 설정 (메트릭, 경로, Agent 상수)
├── i18n.py                          # 다국어 지원 (한/영/일)
├── utils.py                         # 유틸리티 함수
├── data_processor.py                # MLB API 데이터 수집
├── pybaseball_processor.py          # PyBaseball 데이터 수집
├── update_data.py                   # 데이터 업데이트 오케스트레이터
├── auto_update.py                   # 스케줄러
├── data_quality_checker.py          # 데이터 품질 검증
├── player_analysis_ai.py            # 기존 LLM 분석 (단일 호출)
├── Dockerfile                       # Docker 이미지 정의
├── docker-compose.yml               # Docker Compose 설정
├── pyproject.toml                   # 의존성 관리 (UV/Hatch)
├── uv.lock                          # 의존성 잠금 파일
├── requirements.txt                 # pip 호환 의존성
├── PORTFOLIO.md                     # 프로젝트 포트폴리오 (NEW)
└── README.md                        # 본 문서
```

## 데이터 설명
- `data/mlb_batter_stats_2000_2023.csv`: 2000년부터 2025년까지의 MLB 타자 기록 데이터
- `data/mlb_pitcher_stats_2000_2023.csv`: 2000년부터 2025년까지의 MLB 투수 기록 데이터
- 파일명은 "2000_2023"이지만 최신 데이터까지 포함되어 있습니다.

## 사용 방법

### 기본 사용
1. 애플리케이션을 실행하면 사이드바에서 원하는 기능을 선택할 수 있습니다.
2. 사이드바 상단에서 언어(한국어, 영어, 일본어)를 선택할 수 있습니다.

### 페이지별 기능

#### 🏠 홈
- 애플리케이션 개요 및 주요 기능 소개

#### 🔍 기록 조회
- 선수별/시즌별 기록 조회 및 시각화
- 리그 평균 대비 비교
- **[AI]** 종합 분석 리포트 자동 생성 (Report Agent)
- **[AI]** 선수 심층 분석 (기존 LLM 분석)

#### 📈 트렌드 분석
- MLB 리그 전체의 여러 지표 변화 추이 시각화
- 타자 8개 지표, 투수 5개 지표 트렌드

#### 🔮 기록 예측
- Prophet 모델로 향후 5년 성적 예측
- **[AI]** 예측 결과 LLM 해석 및 신뢰도 평가 (Prediction Agent)

#### 🆚 선수 비교
- 두 선수의 기록 직접 비교 및 시각화
- **[AI]** 유사 선수 자동 탐색 및 추천 (Similarity Agent)

#### 💬 AI 채팅 (NEW)
- 자연어로 선수 정보 질문 (Conversational Agent)
- 5개 분석 유형: 프로파일, 비교, 트렌드, 예측, 원인 분석
- 다회차 대화 지원 (맥락 유지)

#### 📊 데이터 상태
- 데이터 파일 정보 및 통계
- **[AI]** 자동 품질 검증 및 이상치 탐지 (Quality Agent)

## 데이터 업데이트 방법

### 🔄 자동 업데이트 (권장)

최신 MLB 데이터를 자동으로 수집하는 여러 가지 방법을 제공합니다:

#### 1. PyBaseball 사용 (간편한 방법)
```bash
# PyBaseball 라이브러리 설치
pip install pybaseball

# 2024년부터 현재까지 데이터 업데이트
python update_data.py --method pybaseball --start-year 2024

# 백업과 함께 업데이트
python update_data.py --method pybaseball --backup
```

#### 2. MLB 공식 API 사용 (상세한 방법)
```bash
# MLB 공식 API를 사용한 업데이트
python update_data.py --method mlb-api --start-year 2024

# 특정 기간 업데이트
python update_data.py --method mlb-api --start-year 2023 --end-year 2024
```

#### 3. 자동 선택 (기본값)
```bash
# 자동으로 최적의 방법 선택 (PyBaseball → MLB API 순서)
python update_data.py --start-year 2024

# 또는 직접 실행
python pybaseball_processor.py
python data_processor.py
```

### 🕒 스케줄러를 통한 자동 업데이트

정기적인 데이터 업데이트를 위한 스케줄러를 제공합니다:

```bash
# 스케줄러 설치 (필요시)
pip install schedule

# 일회성 업데이트
python auto_update.py --mode once

# 지속적인 자동 업데이트 (백그라운드 실행)
python auto_update.py --mode scheduler

# 또는 nohup으로 백그라운드 실행
nohup python auto_update.py --mode scheduler > logs/scheduler.log 2>&1 &
```

**스케줄 정보:**
- **시즌 중 (3월~10월)**: 매일 오전 6시 자동 업데이트
- **시즌 외 (11월~2월)**: 매주 일요일 오전 8시 업데이트

### 📊 업데이트 후 확인

데이터 업데이트 후 다음과 같이 확인할 수 있습니다:

```bash
# 데이터 파일 확인
ls -la data/

# 최신 데이터 시즌 확인
python -c "
import pandas as pd
batter_df = pd.read_csv('data/mlb_batter_stats_2000_2023.csv')
print(f'타자 데이터 최신 시즌: {batter_df[\"Season\"].max()}')
print(f'타자 데이터 총 레코드: {len(batter_df)}')

pitcher_df = pd.read_csv('data/mlb_pitcher_stats_2000_2023.csv')
print(f'투수 데이터 최신 시즌: {pitcher_df[\"Season\"].max()}')
print(f'투수 데이터 총 레코드: {len(pitcher_df)}')
"
```

### ⚠️ 주의사항

1. **API 제한**: MLB 공식 API는 호출 제한이 있을 수 있습니다. 대량 데이터 수집 시 시간이 오래 걸릴 수 있습니다.

2. **데이터 품질**: PyBaseball은 더 안정적이고 빠르지만, MLB 공식 API가 더 최신 데이터를 제공할 수 있습니다.

3. **백업**: 중요한 데이터의 경우 `--backup` 옵션을 사용하여 기존 데이터를 백업하세요.

4. **네트워크**: 데이터 수집 중 네트워크 연결이 안정적이어야 합니다.

### 🛠️ 문제 해결

- **PyBaseball 설치 오류**: `pip install --upgrade pybaseball` 시도
- **API 연결 오류**: 네트워크 연결 상태 확인
- **권한 오류**: 파일 쓰기 권한 확인 (`sudo chmod 755 data/`)
- **로그 확인**: `logs/` 폴더의 로그 파일 확인

---

## LangGraph AI Agent 아키텍처

### 6개 Agent 구성

| Agent | 역할 | 주요 노드 | 도구 |
|-------|------|----------|------|
| **Conversational** | 대화형 분석 | 의도 분류 → 라우팅 → 분석 → 응답 | data_tools, stats_tools |
| **Prediction** | 지능형 예측 | 데이터 평가 → Prophet 실행 → LLM 해석 | prediction_tools |
| **Similarity** | 유사 선수 탐색 | 선수/조건 분기 → 유사도 계산 → 비교 | similarity_tools |
| **Quality** | 품질 검증 | 4단계 검증 → 이상치 탐지 → 해석 | quality_tools |
| **Report** | 종합 리포트 | 섹션별 생성 → 어셈블리 | data_tools, prediction_tools |
| **Update** | 자동 업데이트 | 소스 선택 → 백업 → 실행 → 검증 → 복구 | N/A (subprocess) |

### 주요 설계 패턴

#### 1. StateGraph 조건부 분기
```python
# 예: Prediction Agent의 데이터 충분성 판단
graph.add_conditional_edges(
    "assess",
    lambda state: "predict" if state["data_adequate"] else "insufficient"
)
```

#### 2. @tool 데코레이터로 기존 함수 재활용
```python
from langchain_core.tools import tool
from utils import load_data

@tool
def get_player_stats(player_name: str, player_type: str):
    """선수 기록 조회 도구"""
    return load_data(player_name, player_type)
```

#### 3. Graceful Degradation
```python
from agents.base import is_llm_available

if is_llm_available():
    # AI 분석 실행
else:
    # 기본 통계 반환
```

### Agent 실행 예시

```python
# 1. 대화형 Agent
from agents.conversational import create_conversational_agent

agent = create_conversational_agent()
result = agent.invoke({
    "messages": [{"role": "user", "content": "오타니 쇼헤이 분석해줘"}],
    "lang": "ko"
})

# 2. 예측 Agent
from agents.prediction import create_prediction_agent

agent = create_prediction_agent()
result = agent.invoke({
    "player_name": "Shohei Ohtani",
    "player_type": "batter",
    "metrics": ["BattingAverage", "HomeRuns"],
    "lang": "ko"
})

# 3. 유사 선수 탐색 Agent
from agents.similarity import create_similarity_agent

agent = create_similarity_agent()
result = agent.invoke({
    "reference_player": "Mike Trout",
    "player_type": "batter",
    "top_n": 5,
    "lang": "ko"
})
```

---

## 테스트

### 테스트 실행

```bash
# 모든 테스트 실행
uv run pytest tests/ -v

# 커버리지 포함
uv run pytest tests/ --cov --cov-report=html

# 카테고리별 실행
uv run pytest tests/unit/ -v              # 단위 테스트만
uv run pytest tests/integration/ -v      # 통합 테스트만
uv run pytest tests/data/ -v             # 데이터 품질 테스트만

# 느린 테스트 제외
uv run pytest tests/ -m "not slow" -v

# 커버리지 리포트 보기
open htmlcov/index.html
```

### 테스트 구조 (150개)

- **단위 테스트 (38개)**: Agent별 노드 로직, Tool 입출력 검증, TypedDict 상태 전이
- **통합 테스트 (12개)**: StateGraph 컴파일-실행 E2E, 조건부 분기 경로, Graceful Degradation
- **기존 테스트 (100개)**: 데이터 파이프라인, Prophet 예측, i18n, config 상수

---

## Docker 배포

### 로컬 개발

```bash
# Docker Compose로 빌드 및 실행
docker-compose up --build

# 백그라운드 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

앱은 http://localhost:8501 에서 접근 가능합니다.

### 프로덕션 배포

```bash
# Docker 이미지 빌드
docker build -t mlb-predict-ai .

# 컨테이너 실행 (환경 변수 포함)
docker run -p 8501:8501 \
  -e GOOGLE_AI_API_KEY=your_key \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  mlb-predict-ai

# GitHub Container Registry에서 pull
docker pull ghcr.io/yourusername/predict_mlb_ai:latest
docker run -p 8501:8501 ghcr.io/yourusername/predict_mlb_ai:latest
```

### Docker 이미지 특징

- **베이스**: python:3.11-slim
- **크기**: ~500-600MB (멀티스테이지 빌드 최적화)
- **보안**: 비루트 사용자 (mlbuser)
- **헬스체크**: 내장 Streamlit 엔드포인트 체크
- **포함 항목**: 앱 코드, 데이터, 한글 폰트, 정적 에셋

---

## CI/CD

### GitHub Actions 워크플로우

`.github/workflows/ci.yml`이 다음 작업을 자동화합니다:

1. **테스트**: pytest 150개 실행 + 커버리지 리포트
2. **빌드**: Docker 이미지 빌드 (테스트 통과 후)
3. **푸시**: GHCR에 이미지 푸시 (main 브랜치 머지 시)

### 트리거

- `main` 브랜치 Push
- `main` 브랜치로의 Pull Request
- 수동 실행 (workflow_dispatch)

### 설정 방법

1. **Permissions**: Settings → Actions → General → Workflow permissions → Read and write permissions
2. **Secrets** (선택): `CODECOV_TOKEN` (커버리지 리포트용)

---

## 문제 해결

### Docker 관련

**컨테이너 시작 실패**
```bash
docker-compose logs mlb-app
docker ps
docker-compose restart
```

**권한 오류**
```bash
sudo chown -R 1000:1000 data/ logs/
# 또는 현재 사용자로 실행
docker-compose run --user $(id -u):$(id -g) mlb-app
```

### 테스트 관련

**import 오류**
```bash
uv sync
uv pip install -e ".[test]"
```

**데이터 파일 없음**
```bash
ls -lh data/
python update_data.py --start-year 2024
```

### AI Agent 관련

**LLM API 키 오류**
```bash
# .env 파일 확인
cat .env

# API 키 유효성 테스트
python -c "from agents.base import is_llm_available; print(is_llm_available())"
```

**Agent 그래프 컴파일 실패**
```bash
# LangGraph 버전 확인
pip show langgraph

# 의존성 재설치
uv sync --reinstall
```

---

## 라이선스

MIT License

---

## 기여

이슈 리포트 및 Pull Request를 환영합니다!

---

## 참고 문서

- [CLAUDE.md](CLAUDE.md) - 프로젝트 개발 가이드
- [PORTFOLIO.md](PORTFOLIO.md) - 프로젝트 포트폴리오