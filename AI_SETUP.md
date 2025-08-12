# 🤖 AI 분석 기능 설정 가이드

MLB 선수 기록 조회 및 예측 서비스에 AI 기반 선수 분석 기능이 추가되었습니다. 이 기능은 LangChain과 Google Gemini 모델을 활용하여 선수의 기록 동향에 대한 전문적인 분석 보고서를 자동 생성합니다.

## 🔧 설정 방법

### 1. 필요한 라이브러리 설치

AI 분석 기능을 사용하려면 추가 라이브러리를 설치해야 합니다:

```bash
# pip을 사용하는 경우
pip install langchain langchain-google-genai google-generativeai

# uv를 사용하는 경우 (권장)
uv add langchain langchain-google-genai google-generativeai
```

### 2. Google AI API 키 발급

1. [Google AI Studio](https://makersuite.google.com/app/apikey)에 접속
2. Google 계정으로 로그인
3. "Create API Key" 버튼 클릭
4. 생성된 API 키를 복사

### 3. 환경 변수 설정

#### 방법 1: .env 파일 사용 (권장)
프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음과 같이 설정:

```bash
# .env 파일
GOOGLE_AI_API_KEY=your_actual_api_key_here
```

#### 방법 2: 시스템 환경 변수 설정

**macOS/Linux:**
```bash
export GOOGLE_AI_API_KEY="your_actual_api_key_here"
```

**Windows:**
```cmd
set GOOGLE_AI_API_KEY=your_actual_api_key_here
```

### 4. 기능 확인

애플리케이션을 실행한 후:
1. "기록 조회" 메뉴로 이동
2. 선수를 선택
3. "🤖 AI 기반 선수 분석 보고서" 섹션이 표시되는지 확인

## 🎯 기능 소개

### AI 분석 보고서 생성
- **선수 개요 및 커리어 하이라이트**: 주요 성과와 기록 요약
- **핵심 지표 분석**: 타율, OPS, ERA, WHIP 등 상세 분석
- **리그 평균 대비 성과**: 각 시즌별 상대적 성과 평가
- **시즌별 트렌드 분석**: 성과 변화 패턴 및 피크/부진 시즌 식별
- **종합 평가 및 인사이트**: 선수 스타일, 강점, 향후 전망

### 지원 언어
- 한국어 (기본)
- 영어
- 일본어

### 보고서 형식
- 마크다운 형식으로 생성
- 웹에서 즉시 확인 가능
- 파일 다운로드 지원 (.md 형식)

## 🛠️ 문제 해결

### "LangChain 라이브러리가 설치되지 않았습니다" 오류
```bash
pip install langchain langchain-google-genai google-generativeai
```

### "Google AI API 키가 설정되지 않았습니다" 오류
1. API 키가 올바르게 발급되었는지 확인
2. 환경 변수가 정확히 설정되었는지 확인
3. 애플리케이션을 재시작

### API 호출 제한 오류
- Google AI API는 무료 티어에서 사용량 제한이 있습니다
- 과도한 요청 시 잠시 기다린 후 다시 시도
- 필요 시 유료 플랜으로 업그레이드

### 분석 결과가 부정확한 경우
- AI 모델의 온도(temperature) 설정은 0.3으로 설정되어 일관성을 높였습니다
- 분석은 제공된 데이터에 기반하므로 데이터 품질이 중요합니다
- 결과는 참고용으로 활용하시기 바랍니다

## 📊 사용 예시

1. **타자 분석**: Aaron Judge 선택 시
   - 홈런 기록 분석
   - 타율과 OPS 트렌드
   - 리그 평균 대비 우수성 평가

2. **투수 분석**: Jacob deGrom 선택 시
   - ERA와 WHIP 성과 분석
   - 탈삼진 능력 평가
   - 부상 전후 성과 비교

## ⚠️ 주의사항

1. **API 키 보안**: API 키를 코드에 직접 포함하지 마세요
2. **사용량 모니터링**: Google AI API 사용량을 정기적으로 확인하세요
3. **결과 해석**: AI 분석 결과는 참고 자료로만 활용하세요
4. **데이터 의존성**: 분석 품질은 입력 데이터의 정확성에 의존합니다

## 🔮 향후 계획

- [ ] 선수 간 비교 분석 기능
- [ ] 더 다양한 언어 지원
- [ ] 커스텀 분석 항목 설정
- [ ] 분석 결과 시각화 개선
- [ ] 예측 모델과의 통합

---

문제가 발생하거나 궁금한 점이 있으시면 GitHub Issues에 문의해 주세요.