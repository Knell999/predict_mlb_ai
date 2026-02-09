# MLB 선수 기록 조회 및 예측 서비스

## 프로젝트 개요
이 프로젝트는 MLB(Major League Baseball) 선수들의 기록을 조회하고 분석하며, 미래 성과를 예측하는 종합적인 웹 애플리케이션입니다. 사용자 친화적인 인터페이스를 통해 MLB 팬들이 쉽게 선수 기록을 분석하고 통찰력을 얻을 수 있도록 설계되었습니다.

## 주요 기능
- **선수 기록 조회**: 타자와 투수의 상세 기록 조회 및 시각화
- **리그 트렌드 분석**: MLB 리그 전체의 여러 지표 변화 추이 분석
- **성과 예측**: 머신 러닝(Prophet) 알고리즘을 활용한 선수 성과 예측
- **다국어 지원**: 한국어, 영어, 일본어 지원

## 기술 스택
- **프론트엔드**: Streamlit
- **데이터 처리**: Pandas, NumPy
- **데이터 시각화**: Matplotlib, Seaborn
- **예측 모델**: Facebook Prophet
- **기타 라이브러리**: streamlit_option_menu

## 설치 방법
```bash
# 1. 저장소 클론
git clone https://github.com/yourusername/predict_mlb.git
cd predict_mlb

# 2. 가상 환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
# .venv\\Scripts\\activate   # Windows

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 애플리케이션 실행
streamlit run app.py
```

## 파일 구조
```
predict_mlb/
├── .venv/                  # 가상 환경 폴더
├── data/                   # 데이터 파일 디렉토리
│   ├── mlb_batter_stats_2000_2023.csv   # 타자 데이터
│   └── mlb_pitcher_stats_2000_2023.csv  # 투수 데이터
├── font/                   # 폰트 파일 디렉토리
│   └── H2GTRM.TTF
├── logs/                   # 로그 파일 디렉토리
├── __pycache__/            # 파이썬 캐시 파일
├── .gitignore              # Git 무시 파일 목록
├── .idea/                  # IDE 설정 폴더 (PyCharm 등)
├── app.py                  # 메인 애플리케이션 파일
├── app_metrics.py          # 애플리케이션 메트릭 추적 모듈
├── config.py               # 설정 파일 (현재 비어 있음)
├── home.py                 # 홈 페이지 구성
├── i18n.py                 # 다국어 지원 모듈
├── main.py                 # (사용되지 않는 것으로 보이며, app.py가 메인 실행 파일)
├── mlb_logo.png            # MLB 로고 이미지
├── mlb_players.jpg         # 홈 페이지용 MLB 선수 이미지
├── predict.py              # 성과 예측 페이지
├── pyproject.toml          # 프로젝트 메타데이터 및 의존성 관리 (Poetry 또는 Hatch)
├── README.md               # 프로젝트 설명
├── requirements.txt        # 의존성 파일 (pyproject.toml과 중복될 수 있음)
├── search.py               # 선수 기록 조회 페이지
├── trend.py                # 리그 트렌드 분석 페이지
└── utils.py                # 유틸리티 함수
```

## 데이터 설명
- `data/mlb_batter_stats_2000_2023.csv`: 2000년부터 2025년까지의 MLB 타자 기록 데이터
- `data/mlb_pitcher_stats_2000_2023.csv`: 2000년부터 2025년까지의 MLB 투수 기록 데이터
- 파일명은 "2000_2023"이지만 최신 데이터까지 포함되어 있습니다.

## 사용 방법
1. 애플리케이션을 실행하면 사이드바에서 원하는 기능을 선택할 수 있습니다.
2. 사이드바에서 언어(한국어, 영어, 일본어)를 선택할 수 있습니다.
3. **홈**: 애플리케이션의 개요와 주요 기능 소개
4. **기록 조회**: 선수별 또는 시즌별 기록 조회 및 시각화
5. **트렌드 분석**: MLB 리그의 여러 지표 변화 추이 시각화
6. **기록 예측**: 선택한 선수의 향후 성과 예측

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