"""Flask routes."""

from __future__ import annotations

import csv
import uuid
from datetime import date
from pathlib import Path

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)

from today_house_price.application.housing.dto.predict_price import PredictPriceInput
from today_house_price.domain.housing.features import describe_inference_row_errors
from today_house_price.domain.housing.prediction_options import BUILDING_USAGES, SEOUL_DISTRICTS
from today_house_price.infrastructure.container import build_predict_price_use_case
from today_house_price.infrastructure.persistence.csv_reader import CsvTransactionReader
from today_house_price.infrastructure.reporting.prediction_error_logger import PredictionErrorLogger
from today_house_price.presentation.web.config import WebConfig

web_bp = Blueprint("web", __name__)


def _web_config() -> WebConfig:
    return current_app.config["WEB_CONFIG"]


def _form_row() -> dict[str, str]:
    return {
        "CGG_NM": request.form.get("cgg_nm", "").strip(),
        "BLDG_USG": request.form.get("bldg_usg", "").strip(),
        "ARCH_AREA": request.form.get("arch_area", "").strip(),
        "ARCH_YR": request.form.get("arch_yr", "").strip(),
        "FLR": request.form.get("flr", "").strip(),
        "CTRT_DAY": request.form.get("ctrt_day", "").strip() or date.today().strftime("%Y%m%d"),
    }


@web_bp.get("/")
def index():
    return render_template(
        "index.html",
        districts=SEOUL_DISTRICTS,
        usages=BUILDING_USAGES,
        today=date.today().strftime("%Y%m%d"),
    )


@web_bp.post("/predict")
def predict():
    config = _web_config()
    if not config.model_path.is_file():
        flash("모델 파일이 없습니다. 먼저 train_house_price_model.py 로 학습하세요.", "error")
        return redirect(url_for("web.index"))

    row = _form_row()
    reason = describe_inference_row_errors(row)
    if reason:
        flash(reason, "error")
        return render_template(
            "index.html",
            districts=SEOUL_DISTRICTS,
            usages=BUILDING_USAGES,
            today=date.today().strftime("%Y%m%d"),
            form=row,
        )

    use_case = build_predict_price_use_case()
    result = use_case.execute(
        PredictPriceInput(
            model_path=str(config.model_path),
            properties=(row,),
            skip_invalid=False,
        )
    )
    item = result.predictions[0]
    return render_template(
        "result.html",
        row=row,
        predicted_amount=item.predicted_amount,
    )


@web_bp.get("/batch")
def batch_form():
    return render_template("batch.html")


@web_bp.post("/batch")
def batch_predict():
    config = _web_config()
    if not config.model_path.is_file():
        flash("모델 파일이 없습니다.", "error")
        return redirect(url_for("web.batch_form"))

    upload = request.files.get("csv_file")
    if upload is None or not upload.filename:
        flash("CSV 파일을 선택해 주세요.", "error")
        return redirect(url_for("web.batch_form"))

    session_id = uuid.uuid4().hex[:12]
    input_path = config.upload_folder / f"{session_id}_input.csv"
    output_path = config.upload_folder / f"{session_id}_predictions.csv"
    error_path = config.upload_folder / f"{session_id}_errors.csv"

    upload.save(input_path)
    rows = CsvTransactionReader().load(str(input_path))
    if not rows:
        flash("CSV에 데이터 행이 없습니다.", "error")
        return redirect(url_for("web.batch_form"))

    use_case = build_predict_price_use_case()
    result = use_case.execute(
        PredictPriceInput(
            model_path=str(config.model_path),
            properties=tuple(rows),
            skip_invalid=True,
        )
    )

    _write_predictions_csv(output_path, result.predictions)
    if result.skipped_rows > 0:
        PredictionErrorLogger().save(str(error_path), result.skipped)

    return render_template(
        "batch_result.html",
        total_rows=result.total_rows,
        valid_rows=result.valid_rows,
        skipped_rows=result.skipped_rows,
        download_predictions=url_for("web.download_file", filename=output_path.name),
        download_errors=(
            url_for("web.download_file", filename=error_path.name)
            if result.skipped_rows > 0
            else None
        ),
    )


@web_bp.get("/download/<filename>")
def download_file(filename: str):
    config = _web_config()
    safe_name = Path(filename).name
    file_path = config.upload_folder / safe_name
    if not file_path.is_file():
        flash("파일을 찾을 수 없습니다.", "error")
        return redirect(url_for("web.index"))
    return send_file(file_path, as_attachment=True, download_name=safe_name)


def _write_predictions_csv(output_path: Path, predictions) -> None:
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
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for item in predictions:
            row = {key: item.input_row.get(key, "") for key in fieldnames[1:-1]}
            row["ROW_NUMBER"] = item.row_number
            row["PREDICTED_THING_AMT"] = f"{item.predicted_amount:.0f}"
            writer.writerow(row)
