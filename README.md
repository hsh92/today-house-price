# today-house-price

서울 부동산 실거래가 데이터를 수집·분석하기 위한 프로젝트입니다.  
현재는 **서울 열린데이터광장 Open API**를 이용해 집값(실거래가) 데이터를 CSV로 저장하는 Python 스크립트가 구현되어 있습니다.

---

## 프로젝트 구조

```
today-house-price/
├── .cursor/rules/          # Cursor 개발 규칙 (아키텍처, TDD, Next.js 등)
├── scripts/
│   └── fetch_seoul_house_prices.py   # 서울 실거래가 API → CSV 수집
├── data/
│   ├── seoul_house_prices_5y.csv     # 수집 결과 (295,130건)
│   └── test_sample.csv               # sample 키 테스트용
├── requirements.txt        # Python 의존성 (requests)
├── .env.example            # API 키 설정 예시
└── README.md
```

> 향후 Next.js + Supabase 기반 웹 서비스로 확장할 계획이며, `.cursor/rules/`에 Clean Architecture·TDD 워크플로우가 정의되어 있습니다.

---

## 빠른 시작

### 1. 환경 설정

```powershell
# 가상환경 (선택)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 의존성 설치
pip install -r requirements.txt

# API 키 설정
copy .env.example .env
# .env 파일에 SEOUL_OPEN_API_KEY=발급받은_인증키 입력
```

**인증키 발급:** [서울 열린데이터광장](https://data.seoul.go.kr/) → 마이페이지 → Open API 인증키 신청

### 2. 데이터 수집 실행

```powershell
python scripts/fetch_seoul_house_prices.py --korean-headers
```

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--years` | 수집할 최근 연도 수 | `5` |
| `--output` | CSV 저장 경로 | `data/seoul_house_prices_5y.csv` |
| `--korean-headers` | CSV 헤더 한글화 | 미사용 |
| `--page-size` | 페이지당 건수 (최대 1000) | `1000` |
| `--delay` | API 요청 간 대기(초) | `0.25` |
| `--max-pages` | 연도당 최대 페이지 (테스트용) | 제한 없음 |

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

### 4. README 작성

> **프롬프트:** `README 파일을 만들어서 작업내역, 프롬프트, 작업 결과를 작성해 주세요. 룰의 README-and-gitbub를 적용해 주세요`

**의도:** 작업 이력·프롬프트·결과를 README에 정리, `readme-and-github` 룰의 변경 이력 형식 적용

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

---

## 보안·주의사항

- `.env` 파일(API 키)은 **Git에 커밋하지 마세요**
- `sample` 인증키는 요청당 최대 **5건**만 조회 가능 (본인 키 필수)
- 대량 수집 시 API 트래픽·소요 시간을 고려하세요 (5년치 약 300페이지 이상)

---

## 변경 이력

| 날짜 | 요약 |
|------|------|
| 2026-06-14 | **`.gitignore`** 추가 — `.env`, `.venv`, `data/*.csv` 등 Git 제외 |
| 2026-06-14 | **README.md** 최초 작성 — 작업 내역, 프롬프트, 수집 결과(295,130건) 문서화 |
| 2026-06-14 | **데이터 수집** — `data/seoul_house_prices_5y.csv` 생성 (2024~2026 접수년도, 295,130건) |
| 2026-06-14 | **fetch 스크립트** — `.env` 자동 로드 추가 |
| 2026-06-14 | **fetch 스크립트** — `scripts/fetch_seoul_house_prices.py`, `requirements.txt`, `.env.example` 추가 |

---

## 향후 계획 (참고)

- [ ] 국토교통부 API 연동으로 2021~2023년 데이터 보완
- [ ] Next.js + Supabase 웹 서비스 스캐폴드 (`workflow.mdc` / `architecture.mdc` 기준)
- [ ] `test/` TDD 및 `npm run test` / `npm run build` 파이프라인 구성
