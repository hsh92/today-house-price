#!/usr/bin/env python3
"""실거래 CSV 전처리: 누락 행 제거 후 train/test 분할."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from today_house_price.application.housing.dto.prepare_dataset import PrepareDatasetInput
from today_house_price.domain.housing.dataset import ML_REQUIRED_COLUMNS
from today_house_price.infrastructure.container import build_prepare_dataset_use_case


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="집값 CSV에서 누락 행을 제거하고 train/test 파일로 분할합니다.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/seoul_house_prices_5y.csv"),
        help="원본 CSV 경로",
    )
    parser.add_argument(
        "--train-output",
        type=Path,
        default=Path("data/train.csv"),
        help="훈련용 CSV 저장 경로",
    )
    parser.add_argument(
        "--test-output",
        type=Path,
        default=Path("data/test.csv"),
        help="테스트용 CSV 저장 경로",
    )
    parser.add_argument(
        "--train-ratio",
        type=float,
        default=0.8,
        help="훈련 데이터 비율 (0~1, 기본 0.8)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="train/test 분할 재현용 난수 시드",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="모든 컬럼이 채워진 행만 유지 (기본: ML 핵심 컬럼만 검사)",
    )
    parser.add_argument(
        "--korean-headers",
        action="store_true",
        help="출력 CSV 헤더를 한글로 저장",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.input.is_file():
        print(f"오류: 입력 파일이 없습니다: {args.input.resolve()}", file=sys.stderr)
        return 1

    if not 0.0 < args.train_ratio < 1.0:
        print("오류: --train-ratio는 0과 1 사이여야 합니다.", file=sys.stderr)
        return 1

    use_case = build_prepare_dataset_use_case()
    params = PrepareDatasetInput(
        source_path=str(args.input.resolve()),
        train_output_path=str(args.train_output.resolve()),
        test_output_path=str(args.test_output.resolve()),
        train_ratio=args.train_ratio,
        seed=args.seed,
        strict=args.strict,
        korean_headers=args.korean_headers,
    )

    try:
        result = use_case.execute(params)
    except (ValueError, FileNotFoundError) as exc:
        print(f"오류: {exc}", file=sys.stderr)
        return 1

    mode = "strict(전체 컬럼)" if args.strict else "핵심 컬럼"
    required = "전체" if args.strict else ", ".join(ML_REQUIRED_COLUMNS)

    print("집값 데이터셋 전처리 완료")
    print(f"  입력       : {result.source_path}")
    print(f"  검사 기준   : {mode}")
    print(f"  필수 컬럼   : {required}")
    print(f"  원본 건수   : {result.total_rows:,}")
    print(f"  제거 건수   : {result.removed_rows:,}")
    print(f"  훈련       : {result.train_rows:,}건 -> {result.train_output_path}")
    print(f"  테스트     : {result.test_rows:,}건 -> {result.test_output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
