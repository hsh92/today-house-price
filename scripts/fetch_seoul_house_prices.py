#!/usr/bin/env python3
"""서울 열린데이터광장 부동산 실거래가 수집 CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from today_house_price.application.housing.use_cases.fetch_and_export import FetchAndExportInput
from today_house_price.domain.housing.years import get_target_years
from today_house_price.infrastructure.config.env import get_api_key, load_dotenv
from today_house_price.infrastructure.container import build_fetch_and_export_use_case
from today_house_price.infrastructure.reporting.summary_printer import print_dataset_summary

DEFAULT_PAGE_SIZE = 1000
DEFAULT_REQUEST_DELAY = 0.0
DEFAULT_WORKERS = 6
DEFAULT_YEAR_WORKERS = 2


def parse_args() -> argparse.Namespace:
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="서울 열린데이터광장 부동산 실거래가 API -> CSV 저장 및 요약 출력",
    )
    parser.add_argument(
        "--api-key",
        default=get_api_key(),
        help="서울 열린데이터광장 Open API 인증키 (환경변수 SEOUL_OPEN_API_KEY)",
    )
    parser.add_argument("--years", type=int, default=5, help="수집할 최근 연도 수 (기본: 5)")
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
        help=f"요청 간 대기(초, 병렬 시 worker당). 기본: {DEFAULT_REQUEST_DELAY}",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help=f"연도 내 페이지 병렬 worker 수 (기본: {DEFAULT_WORKERS})",
    )
    parser.add_argument(
        "--year-workers",
        type=int,
        default=DEFAULT_YEAR_WORKERS,
        help=f"연도별 병렬 worker 수 (기본: {DEFAULT_YEAR_WORKERS})",
    )
    parser.add_argument("--timeout", type=int, default=60, help="HTTP 타임아웃(초)")
    parser.add_argument("--max-pages", type=int, default=None, help="연도당 최대 페이지 (테스트용)")
    parser.add_argument("--korean-headers", action="store_true", help="CSV 헤더를 한글로 저장")
    parser.add_argument("--no-summary", action="store_true", help="저장 후 데이터 요약 출력 생략")
    return parser.parse_args()


def main() -> int:
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
    workers = max(1, args.workers)
    year_workers = max(1, args.year_workers)
    target_years = get_target_years(args.years)

    print("서울 열린데이터광장 - 부동산 실거래가 수집")
    print(f"  대상 연도: {target_years[0]} ~ {target_years[-1]} ({len(target_years)}년)")
    print(f"  저장 경로: {args.output.resolve()}")
    print(
        f"  병렬 설정  : page workers={workers}, year workers={year_workers}, delay={args.delay}s"
    )

    use_case = build_fetch_and_export_use_case(args.api_key)
    params = FetchAndExportInput(
        years_back=args.years,
        output_path=str(args.output.resolve()),
        korean_headers=args.korean_headers,
        page_size=page_size,
        delay=args.delay,
        timeout=args.timeout,
        max_pages=args.max_pages,
        workers=workers,
        year_workers=year_workers,
    )

    try:
        result = use_case.execute(params, target_years)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"\n완료: {result.summary.total_rows:,}건 -> {result.summary.output_path}")

    if not args.no_summary:
        print_dataset_summary(result.summary)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
