#!/usr/bin/env python3
"""train/test CSV로 선형 회귀 집값 예측 모델 학습."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from today_house_price.application.housing.dto.train_model import TrainPriceModelInput
from today_house_price.infrastructure.container import build_train_price_model_use_case


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="정리된 train/test CSV로 선형 회귀 집값 예측 모델을 학습합니다.",
    )
    parser.add_argument(
        "--train",
        type=Path,
        default=Path("data/train.csv"),
        help="훈련 CSV 경로",
    )
    parser.add_argument(
        "--test",
        type=Path,
        default=Path("data/test.csv"),
        help="테스트 CSV 경로",
    )
    parser.add_argument(
        "--model-output",
        type=Path,
        default=Path("data/models/price_linear_regression.joblib"),
        help="학습 모델 저장 경로",
    )
    parser.add_argument(
        "--report-output",
        type=Path,
        default=Path("data/models/reports"),
        help="성능 수치·차트 리포트 저장 폴더",
    )
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="성능 리포트(JSON·차트) 생성 생략",
    )
    return parser.parse_args()


def _print_metrics(label: str, metrics) -> None:
    tolerance_pct = int(metrics.accuracy_tolerance * 100)
    print(
        f"  [{label}] MAE={metrics.mae:,.0f}만원  RMSE={metrics.rmse:,.0f}만원  "
        f"R2={metrics.r2:.4f}  MAPE={metrics.mape:.2f}%  "
        f"예측정확도(±{tolerance_pct}%)={metrics.accuracy_rate:.2f}%"
    )


def main() -> int:
    args = parse_args()

    if not args.train.is_file():
        print(f"오류: 훈련 파일이 없습니다: {args.train.resolve()}", file=sys.stderr)
        return 1
    if not args.test.is_file():
        print(f"오류: 테스트 파일이 없습니다: {args.test.resolve()}", file=sys.stderr)
        return 1

    use_case = build_train_price_model_use_case()
    params = TrainPriceModelInput(
        train_path=str(args.train.resolve()),
        test_path=str(args.test.resolve()),
        model_output_path=str(args.model_output.resolve()),
        report_output_dir=str(args.report_output.resolve()),
        generate_report=not args.no_report,
    )

    try:
        result = use_case.execute(params)
    except ValueError as exc:
        print(f"오류: {exc}", file=sys.stderr)
        return 1

    print("선형 회귀 집값 예측 모델 학습 완료")
    print(f"  훈련 CSV : {result.train_rows:,}행")
    print(f"  테스트 CSV: {result.test_rows:,}행")
    print(f"  모델 저장: {result.model_output_path}")
    print("\n[성능 수치]")
    _print_metrics("훈련", result.train_metrics)
    _print_metrics("테스트", result.test_metrics)

    if result.report is not None:
        print("\n[성능 리포트 · 시각화]")
        print(f"  폴더       : {result.report.output_dir}")
        print(f"  수치 JSON  : {result.report.summary_json}")
        print(f"  지표 차트  : {result.report.metrics_chart}")
        print(f"  예측 산점도: {result.report.actual_vs_predicted_chart}")
        print(f"  잔차 분포  : {result.report.residuals_chart}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
