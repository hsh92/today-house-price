#!/usr/bin/env python3
"""훈련된 모델로 집값(거래금액)을 예측."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from today_house_price.application.housing.dto.predict_price import PredictPriceInput
from today_house_price.infrastructure.cli.predict_prompt import (
    ask_yes_no,
    collect_csv_paths,
    collect_property_input,
    select_interactive_mode,
)
from today_house_price.infrastructure.container import build_predict_price_use_case
from today_house_price.infrastructure.persistence.csv_reader import CsvTransactionReader
from today_house_price.infrastructure.reporting.prediction_error_logger import PredictionErrorLogger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="훈련된 선형 회귀 모델로 서울 부동산 거래금액(만원)을 예측합니다.",
        epilog=(
            "예: uv run python scripts/predict_house_price.py --interactive\n"
            "    uv run python scripts/predict_house_price.py --cgg-nm 강남구 ..."
        ),
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=Path("data/models/price_linear_regression.joblib"),
        help="학습된 모델 파일 경로",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="질문·선택 메뉴로 대화형 예측",
    )
    parser.add_argument(
        "--input-csv",
        type=Path,
        default=None,
        help="예측할 매물 CSV (한글/영문 헤더 지원)",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=None,
        help="예측 결과 CSV 저장 경로 (--input-csv 사용 시)",
    )
    parser.add_argument(
        "--error-log",
        type=Path,
        default=None,
        help="건너뛴 행 오류 로그 CSV (--input-csv 사용 시, 기본: output-csv_errors.csv)",
    )
    parser.add_argument("--cgg-nm", default="", help="자치구명 (예: 강남구)")
    parser.add_argument("--bldg-usg", default="", help="건물용도 (예: 아파트)")
    parser.add_argument("--arch-area", default="", help="건물면적(㎡)")
    parser.add_argument("--arch-yr", default="", help="건축년도")
    parser.add_argument("--flr", default="", help="층")
    parser.add_argument(
        "--ctrt-day",
        default="",
        help="계약일 YYYYMMDD (예: 20260601)",
    )
    return parser.parse_args()


def _resolve_data_path(path: Path) -> Path:
    """cwd 기준 경로가 없으면 프로젝트 루트 기준으로 재시도."""
    if path.is_file():
        return path.resolve()

    project_root = Path(__file__).resolve().parents[1]
    candidate = (project_root / path).resolve()
    if candidate.is_file():
        return candidate
    return path.resolve()


def _default_error_log_path(output_csv: Path | None) -> Path:
    if output_csv is not None:
        return output_csv.with_name(f"{output_csv.stem}_errors{output_csv.suffix or '.csv'}")
    return Path("data/predictions_errors.csv")


def _has_cli_property_args(args: argparse.Namespace) -> bool:
    return any(
        str(getattr(args, field)).strip()
        for field in ("cgg_nm", "bldg_usg", "arch_area", "arch_yr", "flr", "ctrt_day")
    )


def _build_single_row(args: argparse.Namespace) -> dict[str, str]:
    required = {
        "CGG_NM": args.cgg_nm,
        "BLDG_USG": args.bldg_usg,
        "ARCH_AREA": args.arch_area,
        "ARCH_YR": args.arch_yr,
        "FLR": args.flr,
        "CTRT_DAY": args.ctrt_day,
    }
    missing = [name for name, value in required.items() if not str(value).strip()]
    if missing:
        raise ValueError(f"단건 예측에 필요한 값이 없습니다: {', '.join(missing)}")
    return required


def _save_predictions(output_path: Path, predictions) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "ROW_NUMBER",
        "CGG_NM",
        "BLDG_USG",
        "ARCH_AREA",
        "ARCH_YR",
        "FLR",
        "CTRT_DAY",
        "PREDICTED_THING_AMT",
    ]
    with output_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for item in predictions:
            row = {key: item.input_row.get(key, "") for key in fieldnames[1:-1]}
            row["ROW_NUMBER"] = item.row_number
            row["PREDICTED_THING_AMT"] = f"{item.predicted_amount:.0f}"
            writer.writerow(row)


def _run_prediction(
    model_path: Path,
    properties: tuple[dict[str, str], ...],
    *,
    skip_invalid: bool,
    output_csv: Path | None,
    error_log: Path | None,
) -> int:
    use_case = build_predict_price_use_case()
    params = PredictPriceInput(
        model_path=str(model_path),
        properties=properties,
        skip_invalid=skip_invalid,
    )

    try:
        result = use_case.execute(params)
    except (ValueError, FileNotFoundError) as exc:
        print(f"오류: {exc}", file=sys.stderr)
        return 1

    print("집값 예측 결과 (단위: 만원)")
    print(
        f"  처리 요약: 전체 {result.total_rows:,}건 / "
        f"성공 {result.valid_rows:,}건 / 건너뜀 {result.skipped_rows:,}건"
    )

    preview_limit = 10 if skip_invalid else len(result.predictions)
    for item in result.predictions[:preview_limit]:
        row = item.input_row
        print(
            f"  [{item.row_number}] {row.get('CGG_NM', '')} / {row.get('BLDG_USG', '')} / "
            f"{row.get('ARCH_AREA', '')}㎡ / {row.get('FLR', '')}층 -> "
            f"{item.predicted_amount:,.0f}만원"
        )
    if skip_invalid and len(result.predictions) > preview_limit:
        print(f"  ... 외 {len(result.predictions) - preview_limit:,}건 (CSV 저장 시 전체 확인)")

    if output_csv:
        _save_predictions(output_csv.resolve(), result.predictions)
        print(f"\n예측 결과 저장: {output_csv.resolve()}")

    if result.skipped_rows > 0:
        error_log_path = (
            error_log.resolve()
            if error_log
            else _default_error_log_path(output_csv.resolve() if output_csv else None)
        )
        PredictionErrorLogger().save(str(error_log_path), result.skipped)
        print(f"오류 로그 저장: {error_log_path} ({result.skipped_rows:,}건)")

    return 0


def _run_interactive_session(model_path: Path) -> int:
    while True:
        mode = select_interactive_mode()
        if mode == 3:
            print("종료합니다.")
            return 0

        if mode == 1:
            try:
                property_row = collect_property_input()
            except ValueError as exc:
                print(f"오류: {exc}", file=sys.stderr)
                continue

            exit_code = _run_prediction(
                model_path,
                (property_row,),
                skip_invalid=False,
                output_csv=None,
                error_log=None,
            )
            if exit_code != 0:
                return exit_code

            if not ask_yes_no("다른 매물도 예측하시겠습니까?"):
                return 0
            continue

        input_text, output_text, error_text = collect_csv_paths()
        input_path = _resolve_data_path(Path(input_text))
        output_path = Path(output_text)
        error_path = Path(error_text) if error_text else None

        if not input_path.is_file():
            print(f"오류: 입력 CSV를 찾을 수 없습니다: {input_path}", file=sys.stderr)
            continue

        rows = CsvTransactionReader().load(str(input_path))
        if not rows:
            print("오류: 입력 CSV에 데이터 행이 없습니다.", file=sys.stderr)
            continue

        return _run_prediction(
            model_path,
            tuple(rows),
            skip_invalid=True,
            output_csv=output_path,
            error_log=error_path,
        )


def main() -> int:
    args = parse_args()
    model_path = _resolve_data_path(args.model)

    if not model_path.is_file():
        print(f"오류: 모델 파일이 없습니다: {model_path}", file=sys.stderr)
        print("  먼저 train_house_price_model.py 로 모델을 학습하세요.", file=sys.stderr)
        return 1

    if args.interactive or (
        not args.input_csv and not _has_cli_property_args(args)
    ):
        return _run_interactive_session(model_path)

    batch_mode = args.input_csv is not None

    try:
        if batch_mode:
            input_path = _resolve_data_path(args.input_csv)
            if not input_path.is_file():
                raise FileNotFoundError(f"입력 CSV를 찾을 수 없습니다: {input_path}")
            rows = CsvTransactionReader().load(str(input_path))
            if not rows:
                raise ValueError("입력 CSV에 데이터 행이 없습니다.")
            properties = tuple(rows)
        else:
            properties = (_build_single_row(args),)
    except (ValueError, FileNotFoundError) as exc:
        print(f"오류: {exc}", file=sys.stderr)
        return 1

    return _run_prediction(
        model_path,
        properties,
        skip_invalid=batch_mode,
        output_csv=args.output_csv,
        error_log=args.error_log,
    )


if __name__ == "__main__":
    raise SystemExit(main())
