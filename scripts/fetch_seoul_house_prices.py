#!/usr/bin/env python3
"""
서울 열린데이터광장 - 서울시 부동산 실거래가 정보(tbLnOpendataRtmsV) 수집

API 문서: https://data.seoul.go.kr/ (서울시 부동산 실거래가 정보)
인증키 발급: https://data.seoul.go.kr/ → 마이페이지 → Open API 인증키 신청

사용 예:
  set SEOUL_OPEN_API_KEY=발급받은_인증키
  python scripts/fetch_seoul_house_prices.py
  python scripts/fetch_seoul_house_prices.py --years 5 --output data/seoul_house_prices.csv
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import requests

BASE_URL = "http://openapi.seoul.go.kr:8088"
SERVICE_NAME = "tbLnOpendataRtmsV"
DEFAULT_PAGE_SIZE = 1000
DEFAULT_REQUEST_DELAY = 0.25
MAX_RETRIES = 3

# API 응답 필드 (신·구 스키마 공통 출력 순서)
CSV_COLUMNS = [
    "RCPT_YR",  # 접수/신고년도 (구 ACC_YEAR)
    "CGG_CD",  # 자치구코드 (구 SGG_CD)
    "CGG_NM",  # 자치구명 (구 SGG_NM)
    "STDG_CD",  # 법정동코드 (구 BJDONG_CD)
    "STDG_NM",  # 법정동명 (구 BJDONG_NM)
    "LOTNO_SE",
    "LOTNO_SE_NM",
    "MNO",  # 본번 (구 BONBEON)
    "SNO",  # 부번 (구 BUBEON)
    "BLDG_NM",
    "CTRT_DAY",  # 계약일 (구 DEAL_YMD)
    "THING_AMT",  # 물건금액 만원 (구 OBJ_AMT)
    "ARCH_AREA",  # 건물면적 (구 BLDG_AREA)
    "LAND_AREA",  # 대지권면적 (구 TOT_AREA)
    "FLR",
    "RGHT_SE",
    "RTRCN_DAY",
    "ARCH_YR",  # 건축년도 (구 BUILD_YEAR)
    "BLDG_USG",  # 건물용도 (구 HOUSE_TYPE)
    "DCLR_SE",  # 신고구분 (구 REQ_GBN)
    "OPBIZ_RESTAGNT_SGG_NM",  # 중개사 시군구 (구 RDEALER_LAWDNM)
]

# 구 API 필드명 → 신 API 필드명
LEGACY_FIELD_MAP = {
    "ACC_YEAR": "RCPT_YR",
    "SGG_CD": "CGG_CD",
    "SGG_NM": "CGG_NM",
    "BJDONG_CD": "STDG_CD",
    "BJDONG_NM": "STDG_NM",
    "BONBEON": "MNO",
    "BUBEON": "SNO",
    "DEAL_YMD": "CTRT_DAY",
    "OBJ_AMT": "THING_AMT",
    "BLDG_AREA": "ARCH_AREA",
    "TOT_AREA": "LAND_AREA",
    "BUILD_YEAR": "ARCH_YR",
    "HOUSE_TYPE": "BLDG_USG",
    "REQ_GBN": "DCLR_SE",
    "RDEALER_LAWDNM": "OPBIZ_RESTAGNT_SGG_NM",
}

KOREAN_HEADERS = {
    "RCPT_YR": "접수년도",
    "CGG_CD": "자치구코드",
    "CGG_NM": "자치구명",
    "STDG_CD": "법정동코드",
    "STDG_NM": "법정동명",
    "LOTNO_SE": "지번구분코드",
    "LOTNO_SE_NM": "지번구분",
    "MNO": "본번",
    "SNO": "부번",
    "BLDG_NM": "건물명",
    "CTRT_DAY": "계약일",
    "THING_AMT": "물건금액_만원",
    "ARCH_AREA": "건물면적_㎡",
    "LAND_AREA": "대지권면적_㎡",
    "FLR": "층",
    "RGHT_SE": "권리구분",
    "RTRCN_DAY": "해제사유발생일",
    "ARCH_YR": "건축년도",
    "BLDG_USG": "건물용도",
    "DCLR_SE": "신고구분",
    "OPBIZ_RESTAGNT_SGG_NM": "개업공인중개사_시군구",
}


@dataclass
class ApiResult:
    code: str
    message: str
    total_count: int
    rows: list[dict[str, Any]]


def normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    """구·신 스키마 필드명을 통일한다."""
    normalized: dict[str, Any] = {}
    for key, value in row.items():
        canonical = LEGACY_FIELD_MAP.get(key, key)
        normalized[canonical] = value
    return {col: normalized.get(col, "") for col in CSV_COLUMNS}


def build_url(api_key: str, start: int, end: int, year: int | None = None) -> str:
    if year is None:
        return f"{BASE_URL}/{api_key}/json/{SERVICE_NAME}/{start}/{end}"
    return f"{BASE_URL}/{api_key}/json/{SERVICE_NAME}/{start}/{end}/{year}"


def parse_response(payload: dict[str, Any]) -> ApiResult:
    if SERVICE_NAME in payload:
        body = payload[SERVICE_NAME]
        result = body.get("RESULT", {})
        rows_raw = body.get("row")
        if rows_raw is None:
            rows: list[dict[str, Any]] = []
        elif isinstance(rows_raw, list):
            rows = rows_raw
        else:
            rows = [rows_raw]
        return ApiResult(
            code=result.get("CODE", ""),
            message=result.get("MESSAGE", ""),
            total_count=int(body.get("list_total_count", 0)),
            rows=rows,
        )

    result = payload.get("RESULT", {})
    return ApiResult(
        code=result.get("CODE", "UNKNOWN"),
        message=result.get("MESSAGE", ""),
        total_count=0,
        rows=[],
    )


def fetch_page(
    session: requests.Session,
    api_key: str,
    start: int,
    end: int,
    year: int | None,
    timeout: int,
) -> ApiResult:
    url = build_url(api_key, start, end, year)
    last_error: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            return parse_response(response.json())
        except (requests.RequestException, ValueError) as exc:
            last_error = exc
            if attempt < MAX_RETRIES:
                time.sleep(attempt)

    raise RuntimeError(f"API 요청 실패 ({start}-{end}, year={year}): {last_error}")


def get_target_years(years_back: int, include_current_year: bool = True) -> list[int]:
    """최근 N년 연도 목록 (기본: 올해 포함 최근 5년)."""
    current_year = date.today().year
    if include_current_year:
        start_year = current_year - years_back + 1
        return list(range(start_year, current_year + 1))
    end_year = current_year - 1
    return list(range(end_year - years_back + 1, end_year + 1))


def fetch_year(
    session: requests.Session,
    api_key: str,
    year: int,
    page_size: int,
    delay: float,
    timeout: int,
    max_pages: int | None = None,
) -> list[dict[str, Any]]:
    """특정 연도 실거래 데이터를 페이지네이션으로 모두 수집한다."""
    first = fetch_page(session, api_key, 1, 1, year, timeout)

    if first.code == "INFO-200":
        print(f"  [{year}] 데이터 없음 - 건너뜀")
        return []

    if first.code != "INFO-000":
        raise RuntimeError(f"[{year}] API 오류: {first.code} - {first.message}")

    total_count = first.total_count
    if total_count == 0:
        print(f"  [{year}] 0건")
        return []

    collected: list[dict[str, Any]] = []
    start_index = 1
    page_no = 0

    print(f"  [{year}] 총 {total_count:,}건 수집 시작...")

    while start_index <= total_count:
        page_no += 1
        if max_pages is not None and page_no > max_pages:
            print(f"  [{year}] max-pages({max_pages}) 도달 - 중단")
            break

        end_index = min(start_index + page_size - 1, total_count)
        result = fetch_page(session, api_key, start_index, end_index, year, timeout)

        if result.code == "INFO-200":
            break
        if result.code != "INFO-000":
            raise RuntimeError(f"[{year}] API 오류: {result.code} - {result.message}")

        collected.extend(normalize_row(row) for row in result.rows)
        print(f"    페이지 {page_no}: {len(collected):,}/{total_count:,}건")

        start_index = end_index + 1
        if delay > 0:
            time.sleep(delay)

    return collected


def save_csv(rows: list[dict[str, Any]], output_path: Path, korean_headers: bool) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    headers = [KOREAN_HEADERS[col] for col in CSV_COLUMNS] if korean_headers else CSV_COLUMNS

    with output_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            if korean_headers:
                writer.writerow({KOREAN_HEADERS[col]: row[col] for col in CSV_COLUMNS})
            else:
                writer.writerow(row)


def load_dotenv(path: Path | None = None) -> None:
    """프로젝트 루트 .env 파일을 환경변수로 로드한다 (이미 설정된 값은 덮어쓰지 않음)."""
    env_path = path or Path(__file__).resolve().parent.parent / ".env"
    if not env_path.is_file():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="서울 열린데이터광장 부동산 실거래가 API → CSV 저장",
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("SEOUL_OPEN_API_KEY", ""),
        help="서울 열린데이터광장 Open API 인증키 (환경변수 SEOUL_OPEN_API_KEY)",
    )
    parser.add_argument(
        "--years",
        type=int,
        default=5,
        help="수집할 최근 연도 수 (기본: 5)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/seoul_house_prices_5y.csv"),
        help="저장할 CSV 경로",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=DEFAULT_PAGE_SIZE,
        help=f"페이지당 건수 (최대 1000, 기본: {DEFAULT_PAGE_SIZE})",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_REQUEST_DELAY,
        help=f"요청 간 대기 시간(초, 기본: {DEFAULT_REQUEST_DELAY})",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="HTTP 타임아웃(초)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="연도당 최대 페이지 (테스트용)",
    )
    parser.add_argument(
        "--korean-headers",
        action="store_true",
        help="CSV 헤더를 한글로 저장",
    )
    return parser.parse_args()


def main() -> int:
    load_dotenv()
    args = parse_args()

    if not args.api_key:
        print(
            "오류: API 인증키가 필요합니다.\n"
            "  1) https://data.seoul.go.kr/ 에서 Open API 인증키를 발급받으세요.\n"
            "  2) 환경변수 SEOUL_OPEN_API_KEY 를 설정하거나 --api-key 로 전달하세요.",
            file=sys.stderr,
        )
        return 1

    page_size = max(1, min(args.page_size, 1000))
    target_years = get_target_years(args.years)

    print("서울 열린데이터광장 - 부동산 실거래가 수집")
    print(f"  대상 연도: {target_years[0]} ~ {target_years[-1]} ({len(target_years)}년)")
    print(f"  저장 경로: {args.output.resolve()}")

    all_rows: list[dict[str, Any]] = []
    session = requests.Session()

    for year in target_years:
        year_rows = fetch_year(
            session=session,
            api_key=args.api_key,
            year=year,
            page_size=page_size,
            delay=args.delay,
            timeout=args.timeout,
            max_pages=args.max_pages,
        )
        all_rows.extend(year_rows)

    if not all_rows:
        print("수집된 데이터가 없습니다. 인증키·연도·API 상태를 확인하세요.", file=sys.stderr)
        return 1

    save_csv(all_rows, args.output, args.korean_headers)
    print(f"\n완료: {len(all_rows):,}건 -> {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
