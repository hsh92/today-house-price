# today-house-price

서울 부동산 실거래가 데이터를 수집·분석·예측하기 위한 **Python + uv** 프로젝트입니다.  
**서울 열린데이터광장 Open API**로 집값 데이터를 CSV로 저장하고, 선형 회귀 모델로 예측합니다. **Flask 웹 UI**로도 이용할 수 있습니다.

---

## 프로젝트 구조

```
today-house-price/
├── pyproject.toml              # uv 프로젝트·의존성 (정본)
├── uv.lock                     # 잠금 파일
├── requirements.txt            # pip용 런타임 (uv export 동기화)
├── requirements-dev.txt        # pip용 개발 (uv export 동기화)
├── src/today_house_price/      # Clean Architecture 패키지
│   ├── domain/housing/         # 필드 정의, 요약 VO, 연도 계산
│   ├── application/housing/    # Use Case (수집·전처리·학습)
│   ├── infrastructure/         # API, CSV, ML, DI container
│   └── presentation/web/       # Flask 웹 UI (단건·CSV 일괄 예측)
├── scripts/
│   ├── fetch_seoul_house_prices.py      # API 수집 CLI
│   ├── prepare_house_price_dataset.py   # 전처리·train/test 분할 CLI
│   ├── train_house_price_model.py       # 선형 회귀 학습 CLI
│   ├── predict_house_price.py           # 집값 예측 CLI
│   └── run_web.py                       # Flask 웹 서버
├── tests/                      # pytest
├── data/                       # 수집 결과 (gitignore)
├── .env.example
└── .cursor/rules/              # architecture, tech-stack, workflow, framework 등
```

---

## 빠른 시작

### 1. 환경 설정

```powershell
# uv 설치: https://docs.astral.sh/uv/

# 의존성 설치 (프로덕션 + dev)
uv sync

# API 키 설정
copy .env.example .env
# .env 파일에 SEOUL_OPEN_API_KEY=발급받은_인증키 입력
```

**pip만 사용하는 경우:**

```powershell
pip install -r requirements-dev.txt   # 개발·테스트·린트 포함
# 또는
pip install -r requirements.txt       # 데이터 수집(런타임)만
```

**인증키 발급:** [서울 열린데이터광장](https://data.seoul.go.kr/) → 마이페이지 → Open API 인증키 신청

### 2. 데이터 수집 실행

```powershell
uv run python scripts/fetch_seoul_house_prices.py --korean-headers
```

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--years` | 수집할 최근 연도 수 | `5` |
| `--output` | CSV 저장 경로 | `data/seoul_house_prices_5y.csv` |
| `--korean-headers` | CSV 헤더 한글화 | 미사용 |
| `--page-size` | 페이지당 건수 (최대 1000) | `1000` |
| `--delay` | API 요청 간 대기(초, worker당) | `0` |
| `--workers` | 연도 내 페이지 병렬 worker 수 | `6` |
| `--year-workers` | 연도별 병렬 worker 수 | `2` |
| `--max-pages` | 연도당 최대 페이지 (테스트용) | 제한 없음 |
| `--no-summary` | 저장 후 데이터 요약 출력 생략 | 출력함 |

### 3. 전처리 (누락 제거 · train/test 분할)

```powershell
uv run python scripts/prepare_house_price_dataset.py --korean-headers
```

기본값: `data/seoul_house_prices_5y.csv` → `data/train.csv` (80%) + `data/test.csv` (20%)

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--input` | 원본 CSV | `data/seoul_house_prices_5y.csv` |
| `--train-output` | 훈련 CSV | `data/train.csv` |
| `--test-output` | 테스트 CSV | `data/test.csv` |
| `--train-ratio` | 훈련 비율 (0~1) | `0.8` |
| `--seed` | 분할 재현 시드 | `42` |
| `--strict` | **모든** 컬럼 필수 (기본: ML 핵심 9컬럼만) | 미사용 |
| `--korean-headers` | 출력 헤더 한글화 | 미사용 |

**기본 필수 컬럼 (빈 칸 있으면 행 제거):** 접수년도, 자치구명, 법정동명, 계약일, 물건금액, 건물면적, 건축년도, 건물용도, 층  
(해제일·중개사 등 API상 자주 비는 컬럼은 `--strict` 없이는 검사하지 않음)

### 4. 집값 예측 모델 학습 (선형 회귀)

```powershell
uv run python scripts/train_house_price_model.py
```

기본값: `data/train.csv` + `data/test.csv` → `data/models/price_linear_regression.joblib`

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--train` | 훈련 CSV | `data/train.csv` |
| `--test` | 테스트 CSV | `data/test.csv` |
| `--model-output` | 모델 저장 경로 | `data/models/price_linear_regression.joblib` |
| `--report-output` | 성능 리포트 폴더 | `data/models/reports` |
| `--no-report` | JSON·차트 리포트 생략 | 생성함 |

**입력 특성:** 건물면적, 건축년도, 층, 계약연·월, 자치구명(원-핫), 건물용도(원-핫)  
**목표 변수:** 물건금액(만원)  
**평가 지표:** MAE, RMSE, R², MAPE, 예측정확도(±10%) — 훈련·테스트 각각 출력

**성능 리포트 (기본 생성):**

| 파일 | 내용 |
|------|------|
| `performance_summary.json` | 훈련·테스트 수치 지표 |
| `metrics_overview.png` | MAE/RMSE·MAPE/정확도 막대 차트 |
| `actual_vs_predicted_test.png` | 테스트 실제값 vs 예측값 산점도 |
| `residuals_test.png` | 테스트 잔차(실제-예측) 히스토그램 |

### 5. 집값 예측 (학습된 모델 사용)

```powershell
# 대화형 (질문·선택 메뉴) — 옵션 없이 실행해도 메뉴 표시
uv run python scripts/predict_house_price.py --interactive

# 단건 예측 (CLI 인자)
uv run python scripts/predict_house_price.py `
  --cgg-nm 강남구 --bldg-usg 아파트 `
  --arch-area 84.5 --arch-yr 2010 --flr 10 --ctrt-day 20260601

# CSV 일괄 예측
uv run python scripts/predict_house_price.py `
  --input-csv data/test.csv `
  --output-csv data/predictions.csv
```

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--model` | 학습된 모델 경로 | `data/models/price_linear_regression.joblib` |
| `--interactive`, `-i` | 질문·선택 대화형 모드 | (인자 없을 때 자동) |
| `--input-csv` | 예측할 매물 CSV | (단건 옵션 사용) |
| `--output-csv` | 예측 결과 저장 | 미저장 |
| `--error-log` | 건너뛴 행 오류 로그 CSV | `{output}_errors.csv` |
| `--cgg-nm` | 자치구명 | — |
| `--bldg-usg` | 건물용도 | — |
| `--arch-area` | 건물면적(㎡) | — |
| `--arch-yr` | 건축년도 | — |
| `--flr` | 층 | — |
| `--ctrt-day` | 계약일(YYYYMMDD) | — |

CSV 일괄 예측 시 **형식 오류 행은 건너뛰고** 유효 행만 처리합니다. 건너뛴 행은 `--error-log` CSV에서 확인할 수 있습니다.

**대화형 모드:** 자치구·건물용도 번호 선택, 면적·층·계약일 입력 후 즉시 예측. CSV 일괄 예측도 메뉴에서 선택 가능합니다.

### 6. 웹 예측 (Flask)

학습된 모델이 있어야 합니다 (`data/models/price_linear_regression.joblib`).

```powershell
uv run python scripts/run_web.py
```

브라우저에서 `http://127.0.0.1:5000` 접속.

| 기능 | URL | 설명 |
|------|-----|------|
| 단건 예측 | `/` → `POST /predict` | 자치구·건물용도 선택, 면적·층·계약일 입력 |
| CSV 일괄 | `/batch` → `POST /batch` | CSV 업로드 후 예측·오류 로그 다운로드 |

| 환경 변수 | 설명 | 기본값 |
|-----------|------|--------|
| `FLASK_SECRET_KEY` | Flask 세션·flash 서명 키 | `dev-only-change-in-production` |
| `MODEL_PATH` | 예측 모델 경로 | `data/models/price_linear_regression.joblib` |
| `WEB_UPLOAD_FOLDER` | 업로드·결과 CSV 저장 | `data/web_uploads` |
| `WEB_HOST` / `WEB_PORT` | 바인드 주소·포트 | `127.0.0.1` / `5000` |
| `FLASK_DEBUG` | `1`이면 디버그 모드 | `0` |

업로드 파일은 `data/web_uploads/`에 세션별로 저장되며 gitignore 대상입니다.

### 7. 테스트·린트

```powershell
uv run pytest
uv run pytest --cov=src/today_house_price --cov-fail-under=80
uv run ruff check .
uv run ruff format --check .
```

> 의존성 **정본**은 `pyproject.toml` + `uv.lock`입니다.  
> `requirements.txt`(런타임), `requirements-dev.txt`(개발)는 pip 호환용이며 `uv export`로 `pyproject.toml`·`uv.lock`과 동기화합니다.

### CSV 저장 후 데이터 요약

수집·저장이 끝나면 콘솔에 아래 정보가 출력됩니다.

- 파일 경로·크기·총 건수
- 계약일 범위, 거래금액(최소/최대/평균)
- 접수년도·계약연도·자치구·건물용도별 건수
- **포함 데이터 항목** (컬럼명 + 설명 21개)

---

## API 정보

| 항목 | 내용 |
|------|------|
| 제공처 | 서울 열린데이터광장 |
| 데이터셋 | [서울시 부동산 실거래가 정보](https://data.seoul.go.kr/dataList/OA-21275/A/1/datasetView.do) |
| 서비스명 | `tbLnOpendataRtmsV` |
| URL 패턴 | `http://openapi.seoul.go.kr:8088/{인증키}/json/tbLnOpendataRtmsV/{시작}/{끝}/{연도}` |

### CSV 주요 컬럼 (한글 헤더 기준)

| 컬럼 | 설명 |
|------|------|
| 접수년도 | 신고·접수 연도 (`RCPT_YR`) |
| 자치구명 | 구 이름 |
| 법정동명 | 법정동 이름 |
| 건물명 | 건물·단지명 |
| 계약일 | 거래 계약일 (`YYYYMMDD`) |
| 물건금액_만원 | 거래 금액 (만원) |
| 건물면적_㎡ | 전용·건물 면적 |
| 건물용도 | 아파트, 오피스텔, 연립다세대 등 |
| 신고구분 | 중개거래 / 직거래 |

---

## 작업 내역

| 순서 | 일자 | 작업 | 산출물 |
|------|------|------|--------|
| 1 | 2026-06-14 | 프로젝트 폴더·규칙 분석 | (문서화) Cursor 규칙 5종, 실행 코드 없음 확인 |
| 2 | 2026-06-14 | 서울 집값 API 수집 스크립트 작성 | `scripts/fetch_seoul_house_prices.py`, `requirements.txt`, `.env.example` |
| 3 | 2026-06-14 | 최근 5년치 전체 수집 실행 | `data/seoul_house_prices_5y.csv` (295,130건) |
| 4 | 2026-06-14 | README 작성 | `README.md` |
| 5 | 2026-06-14 | Python·uv 규칙 개편 | `.cursor/rules/*.mdc`, `pyproject.toml`, `src/` |
| 6 | 2026-06-14 | `framework.mdc` 생성 | `next.js-framework.mdc` 삭제·Python CLI 규칙으로 교체 |
| 7 | 2026-06-14 | `workflow.mdc` upgrade | Phase·TDD·검증·레거시 리팩터 가이드 보강 |
| 8 | 2026-06-14 | `readme-and-github.mdc` 갱신 | Python·uv 기준, GitHub 워크플로우 정리 |
| 9 | 2026-06-14 | Clean Architecture·병렬 수집·전처리 | `src/`, `prepare_house_price_dataset.py`, pytest 34건 |
| 10 | 2026-06-14 | readme-and-github 적용 점검 | README 프롬프트·작업 결과 보강, requirements 레거시 주석 |
| 11 | 2026-06-14 | 선형 회귀·예측 CLI·성능 리포트 | `train_house_price_model.py`, `predict_house_price.py`, pytest 53건 |
| 12 | 2026-06-14 | Flask 웹 예측 UI | `presentation/web/`, `run_web.py`, pytest 58건 |
| 13 | 2026-06-14 | readme-and-github 재적용 | 프롬프트·작업 결과·변경 이력 동기화 |

---

## 프롬프트

대화 세션에서 사용자가 요청한 프롬프트와 의도입니다.

### 1. 폴더 분석

> **프롬프트:** `폴더를 분석해줘`

**의도:** 프로젝트 현재 상태와 구조 파악

### 2. 데이터 수집 코드 작성

> **프롬프트:** `서울 열린 데이터 광장에서 서울 집값의 최근 5년치 데이터를 가져오고, csv로 저장하는 파이썬 코드를 작성해줘`

**의도:** 서울 열린데이터광장 Open API 연동, 최근 5년 실거래가 CSV 저장

### 3. 전체 수집 실행

> **프롬프트:** `네`

**의도:** 발급받은 API 키로 5년치 데이터 실제 수집 실행

### 4. README·규칙 개편

> **프롬프트:** `architecture, tech-stack, workflow 룰을 Python·uv 구조에 맞게 수정`

**의도:** Next.js/Supabase 템플릿 규칙을 현재 Python 데이터 수집 프로젝트에 맞게 정렬

### 5. framework.mdc 개편

> **프롬프트:** `next.js-framework.mdc도 현재 프로젝트 구조를 기반으로 변경하고 제목도 framework.mdc로 변경해`

**의도:** Next.js 규칙을 Python CLI·uv 실행 규칙으로 교체, 파일명 `framework.mdc`로 통일

### 6. workflow.mdc upgrade

> **프롬프트:** `workflow.mdc도 변경된 내용 반영해서 upgrade 해주세요`

**의도:** Python·uv·framework·레거시 scripts·프로젝트 현황을 workflow Phase 전반에 반영

### 7. readme-and-github.mdc · Git 반영

> **프롬프트:** `수정하고 커밋, 푸쉬해주세요`

**의도:** readme-and-github를 Python·uv 기준으로 수정 후 변경사항 커밋·푸시

### 8. 수집 속도 개선

> **프롬프트:** `workflow.mdc에 따라서 개발을 해주고 데이터 가져오는 속도 개선을 해주세요. 그리고 끝나면 커밋 및 푸쉬도 해주세요`

**의도:** 병렬 HTTP fetch로 수집 시간 단축, TDD·검증 후 Git 반영

### 9. `.env` 인증키 오류

> **프롬프트:** `.env` 파일에 인증키가 있는데 오류가 나옵니다. 확인

**의도:** `scripts/` 등 하위 폴더 실행 시에도 프로젝트 루트 `.env` 로드

### 10. `.env` 수정 커밋·푸시

> **프롬프트:** `커밋·푸시`

**의도:** `.env` 로드 수정 반영

### 11. train/test 데이터셋 분할

> **프롬프트:** `가져온 집값 데이터 파일에서 누락된 데이터(빈 칸)을 제거하고, 훈련용과 테스트용으로 나누는 파이썬 코드를 작성해줘`

**의도:** ML용 전처리 — 누락 행 제거, train/test CSV 분할

### 12. readme-and-github 적용 확인

> **프롬프트:** `readme-and-github.mdc 적용 했는지 확인 하고, 사용하지 않는 파일의 내용은 주석처리 해줘`

**의도:** README 필수 섹션·검증 명령 정합성 점검, 레거시 pip requirements 비활성화

### 13. 선형 회귀 집값 예측 모델

> **프롬프트:** `정리된 데이터를 이용해서 다음 집값을 예상하는 간단한 작선 예측기(선형 회귀) 모델을 학습시키는 파이썬 코드를 작성해줘`

**의도:** train/test CSV로 scikit-learn LinearRegression 학습·평가·모델 저장

### 14. 집값 예측 CLI

> **프롬프트:** `학습된 모델로 집값을 예측하는 CLI를 만들어줘` (세션 요약)

**의도:** 단건·CSV 일괄 예측 CLI, Clean Architecture Use Case 연동

### 15. 대화형 예측·오류 처리

> **프롬프트:** 대화형 모드 및 CSV 일괄 예측 시 잘못된 행 건너뛰기 (세션 요약)

**의도:** `--interactive` 메뉴, 일괄 예측 오류 로그 CSV

### 16. Flask 웹 서비스

> **프롬프트:** `flask web을 이용해서 웹으로 서비스를 이용하도록 만들어주세요`

**의도:** 브라우저에서 단건·CSV 일괄 예측, 기존 `PredictPriceUseCase` 재사용

### 17. readme-and-github 적용

> **프롬프트:** `@.cursor/rules/readme-and-github.mdc 적용해줘`

**의도:** README 필수 섹션(변경 이력·프롬프트·작업 결과·빠른 시작) 정합성 점검 및 갱신

---

## 작업 결과

### 1. 폴더 분석 결과

- 초기 상태: `.cursor/rules/` 아래 개발 규칙 5개만 존재, **애플리케이션 코드·Git 저장소 없음**
- 프로젝트명 `today-house-price`는 부동산 시세 서비스를 암시하나, 규칙에는 Next.js·Supabase·Clean Architecture 템플릿이 정의되어 있음
- `tdd.md`, `package.json`, `app/` 등은 아직 미생성

### 2. Python 수집 스크립트

- **파일:** `scripts/fetch_seoul_house_prices.py`
- **기능:**
  - 서울 열린데이터광장 `tbLnOpendataRtmsV` API 호출
  - 연도별 페이지네이션 (최대 1,000건/요청)
  - 구·신 API 필드명 통일 (`ACC_YEAR` → `RCPT_YR` 등)
  - `.env`의 `SEOUL_OPEN_API_KEY` 자동 로드
  - UTF-8 BOM CSV 저장 (Excel 한글 호환)
- **의존성:** `requests>=2.31.0`

### 3. 데이터 수집 실행 결과 (2026-06-14)

| 항목 | 값 |
|------|-----|
| 출력 파일 | `data/seoul_house_prices_5y.csv` |
| 총 건수 | **295,130건** |
| 파일 크기 | 약 **44 MB** |
| 소요 시간 | 약 **3분 36초** |
| 대상 연도 (요청) | 2022 ~ 2026 (5년) |

#### 접수년도별 건수

| 접수년도 | 건수 | 비고 |
|----------|------|------|
| 2022 | 0 | API `INFO-200` (데이터 없음) |
| 2023 | 0 | API `INFO-200` (데이터 없음) |
| 2024 | 96,906 | |
| 2025 | 134,972 | |
| 2026 | 63,252 | |

#### 계약일 기준 연도 분포 (참고)

| 계약 연도 | 건수 |
|-----------|------|
| 2021 | 2 |
| 2022 | 6 |
| 2023 | 1,823 |
| 2024 | 97,365 |
| 2025 | 135,168 |
| 2026 | 60,766 |

**한계:** 서울 열린데이터광장 API는 **접수년도** 기준 필터를 사용하며, 현재 제공 데이터는 **2024~2026년 접수분**이 대부분입니다. 2022·2023년 접수 데이터는 API에서 제공되지 않았습니다. 2021~2023년 **전체** 실거래 이력이 필요하면 [국토교통부 아파트 매매 실거래가 API](https://www.data.go.kr/data/15126468/openapi.do)(공공데이터포털) 사용을 검토해야 합니다.

### 4. Clean Architecture 리팩터·병렬 수집 (2026-06-14)

- monolithic `fetch_seoul_house_prices.py` → `src/today_house_price/` 계층 분리
- 병렬 fetch: `--workers 6`, `--year-workers 2`, 기본 `--delay 0`
- CSV 저장 후 콘솔 데이터 요약 (`--no-summary`로 생략 가능)
- pytest 22건 → 이후 전처리 추가 시 **34 passed**, coverage **~89%**

### 5. `.env` 로드 수정 (2026-06-14)

- **원인:** `load_dotenv()`가 `Path.cwd()/.env`만 탐색 → `scripts/` 실행 시 루트 `.env` 미인식
- **수정:** `pyproject.toml`·패키지 경로 기준 상위 탐색, `utf-8-sig` 지원
- 커밋 `16e398f`, push 완료

### 6. 데이터셋 전처리·train/test 분할 (2026-06-14)

- **CLI:** `scripts/prepare_house_price_dataset.py`
- **로직:** ML 핵심 9컬럼 누락 행 제거 → seed 42, 8:2 분할
- **실행 결과 (`seoul_house_prices_5y.csv`):** 원본 295,130건 → 제거 1건 → train 236,103 / test 59,026

### 7. readme-and-github.mdc 적용 점검 (2026-06-14)

| 항목 | 상태 | 조치 |
|------|------|------|
| 변경 이력 | 일부 누락 | 최신 작업 항목 추가 |
| 프롬프트 | 8번까지 | 9~12번 세션 추가 |
| 작업 결과 | 초기 수집까지만 | 4~7번 결과 보강 |
| 빠른 시작 | 전처리 CLI 반영됨 | fetch 옵션표 위치 수정, cov·format 검증 추가 |
| 검증 명령 | pytest·ruff만 | `--cov-fail-under=80`, `ruff format --check` 추가 |
| 레거시 requirements | uv 미사용 | `requirements*.txt` 의존성 줄 주석 처리 *(이후 `uv export`로 재활성·flask 포함)* |

### 8. 선형 회귀 집값 예측 모델 (2026-06-14)

- **CLI:** `scripts/train_house_price_model.py`
- **모델:** scikit-learn `LinearRegression` + OneHotEncoder
- **저장:** `data/models/price_linear_regression.joblib`
- **의존성:** `scikit-learn`, `matplotlib` (`uv add scikit-learn matplotlib`)
- **실행 결과 (295k건 기준):** 테스트 MAE ≈ 33,722만원, RMSE ≈ 56,583만원, R² ≈ 0.61
- **성능 리포트:** `data/models/reports/` — JSON + 지표·산점도·잔차 PNG 3종

### 9. 집값 예측 CLI·대화형·오류 처리 (2026-06-14)

- **CLI:** `scripts/predict_house_price.py`
- **모드:** 단건 인자, CSV 일괄, `--interactive` 대화형
- **일괄 예측:** 형식 오류 행 건너뛰기 + `{output}_errors.csv` 로그
- **Domain:** `features.py` (`row_to_inference_input`, `describe_inference_row_errors`)
- **Infrastructure:** `sklearn_predictor.py`, `prediction_error_logger.py`, `cli/predict_prompt.py`
- **smoke (test.csv 59,026건):** 성공 58,805 / 건너뜀 221

### 10. Flask 웹 예측 (2026-06-14)

- **실행:** `uv run python scripts/run_web.py` → `http://127.0.0.1:5000`
- **경로:** `src/today_house_price/presentation/web/` — `create_app()`, 단건(`/`, `/predict`), 일괄(`/batch`), 다운로드(`/download/<filename>`)
- **의존성:** `flask` (`uv add flask`), `requirements.txt` `uv export` 동기화
- **설정:** `.env.example` — `FLASK_SECRET_KEY`, `MODEL_PATH`, `WEB_UPLOAD_FOLDER`, `WEB_HOST`/`WEB_PORT`
- **업로드:** `data/web_uploads/` (gitignore)
- **테스트:** `tests/presentation/test_web_app.py` 5건

### 11. readme-and-github.mdc 적용 (2026-06-14)

| 항목 | 상태 | 조치 |
|------|------|------|
| 변경 이력 | Flask·예측 CLI 반영 | 최신 항목 유지 |
| 프롬프트 | 13번까지 | 14~17번(예측·Flask·본 점검) 추가 |
| 작업 결과 | 8번까지 | 9~11번(예측·Flask·점검) 보강 |
| 빠른 시작 | Flask §6·검증 §7 | `uv sync`, `run_web.py`, cov 80% 명령 일치 |
| requirements | `uv export` 활성 | flask 포함 런타임·dev 재생성 |
| 검증 | Phase 3 | pytest 58 passed, coverage ~89%, ruff PASS |

---

## 보안·주의사항

- `.env` 파일(API 키)은 **Git에 커밋하지 마세요**
- `sample` 인증키는 요청당 최대 **5건**만 조회 가능 (본인 키 필수)
- 대량 수집 시 API 트래픽·소요 시간을 고려하세요 (기본 `--workers 6`, `--year-workers 2`로 병렬 수집)

---

## 변경 이력

| 날짜 | 요약 |
|------|------|
| 2026-06-14 | **readme-and-github 적용** — 프롬프트·작업 결과·작업 내역 동기화, 검증 명령 정합 |
| 2026-06-14 | **Flask 웹 예측** — 단건·CSV 일괄 예측 UI, `scripts/run_web.py`, `presentation/web/` |
| 2026-06-14 | **대화형 예측** — `--interactive` 질문·선택 메뉴 (자치구·건물용도·매물 정보) |
| 2026-06-14 | **예측 오류 처리** — CSV 일괄 예측 시 잘못된 행 건너뛰기 + 오류 로그 CSV |
| 2026-06-14 | **집값 예측 CLI** — 학습 모델로 단건·CSV 일괄 예측 (`predict_house_price.py`) |
| 2026-06-14 | **모델 성능 리포트** — JSON 수치 + 지표·산점도·잔차 차트 (`data/models/reports/`) |
| 2026-06-14 | **모델 평가 보강** — 학습 결과에 MAPE·예측정확도(±10%) 출력 |
| 2026-06-14 | **선형 회귀 집값 예측** — train/test CSV 학습 CLI, scikit-learn, MAE/RMSE/R² 평가 |
| 2026-06-14 | **`requirements.txt` 동기화** — `uv export`로 pyproject.toml·uv.lock과 재생성 |
| 2026-06-14 | **readme-and-github 점검** — 프롬프트·작업 결과 보강, fetch 옵션표 정리 |
| 2026-06-14 | **데이터셋 전처리** — 누락 행 제거, train/test 분할 CLI (`prepare_house_price_dataset.py`) |
| 2026-06-14 | **`.env` 로드 수정** — `scripts/` 등 하위 폴더에서 실행해도 프로젝트 루트 `.env` 탐색 |
| 2026-06-14 | **수집 속도 개선** — 연도·페이지 병렬 fetch, `--workers`/`--year-workers`, 기본 delay 0 |
| 2026-06-14 | **데이터 요약 출력** — CSV 저장 후 건수·항목·통계 요약, Clean Architecture 리팩터 |
| 2026-06-14 | **`workflow.mdc` upgrade** — 프로젝트 스냅샷, 작업 유형표, 레거시 리팩터·실패 분석·충돌 해석 보강 |
| 2026-06-14 | **`framework.mdc`** — `next.js-framework.mdc`를 Python CLI 규칙으로 교체·개명 |
| 2026-06-14 | **Cursor 규칙** — `architecture`·`tech-stack`·`workflow`를 Python·uv 구조로 전면 개편 |
| 2026-06-14 | **uv 프로젝트** — `pyproject.toml`, `uv.lock`, `src/today_house_price/`, `tests/` 추가 |
| 2026-06-14 | **`.gitignore`** 추가 — `.env`, `.venv`, `data/*.csv` 등 Git 제외 |
| 2026-06-14 | **README.md** 최초 작성 — 작업 내역, 프롬프트, 수집 결과(295,130건) 문서화 |
| 2026-06-14 | **데이터 수집** — `data/seoul_house_prices_5y.csv` 생성 (2024~2026 접수년도, 295,130건) |
| 2026-06-14 | **fetch 스크립트** — `.env` 자동 로드 추가 |
| 2026-06-14 | **fetch 스크립트** — `scripts/fetch_seoul_house_prices.py`, `requirements.txt`, `.env.example` 추가 |

---

## 향후 계획 (참고)

- [ ] 국토교통부 API 연동으로 2021~2023년 데이터 보완
- [x] Flask 웹으로 집값 예측 서비스 제공
- [ ] Use Case·Adapter 단위 pytest 커버리지 유지 (80%+)
