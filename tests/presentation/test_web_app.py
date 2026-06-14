"""Flask web presentation tests."""

from __future__ import annotations

import io
from pathlib import Path
from unittest.mock import patch

import pytest

from today_house_price.application.housing.dto.predict_price import (
    PredictPriceResult,
    PricePredictionItem,
    SkippedPredictionItem,
)
from today_house_price.presentation.web.app import create_app
from today_house_price.presentation.web.config import WebConfig


@pytest.fixture
def web_client(tmp_path: Path):
    model_path = tmp_path / "model.joblib"
    model_path.write_bytes(b"fake")
    upload_folder = tmp_path / "uploads"
    config = WebConfig(
        secret_key="test-secret",
        model_path=model_path,
        upload_folder=upload_folder,
    )
    app = create_app(config)
    app.config["TESTING"] = True
    return app.test_client(), config


def _valid_form() -> dict[str, str]:
    return {
        "cgg_nm": "강남구",
        "bldg_usg": "아파트",
        "arch_area": "84.5",
        "arch_yr": "2010",
        "flr": "10",
        "ctrt_day": "20240101",
    }


def test_index_renders_form(web_client) -> None:
    client, _ = web_client
    response = client.get("/")
    assert response.status_code == 200
    body = response.data.decode("utf-8")
    assert "매물 정보 입력" in body
    assert "강남구" in body


@patch("today_house_price.presentation.web.routes.build_predict_price_use_case")
def test_predict_success(mock_build, web_client) -> None:
    client, config = web_client
    mock_build.return_value.execute.return_value = PredictPriceResult(
        model_path=str(config.model_path),
        predictions=(
            PricePredictionItem(
                row_number=1,
                input_row={
                    "CGG_NM": "강남구",
                    "BLDG_USG": "아파트",
                    "ARCH_AREA": "84.5",
                    "ARCH_YR": "2010",
                    "FLR": "10",
                    "CTRT_DAY": "20240101",
                },
                predicted_amount=125000.0,
            ),
        ),
        skipped=(),
        total_rows=1,
        valid_rows=1,
        skipped_rows=0,
    )

    response = client.post("/predict", data=_valid_form())
    assert response.status_code == 200
    body = response.data.decode("utf-8")
    assert "125,000" in body
    assert "예측 결과" in body


def test_predict_validation_error(web_client) -> None:
    client, _ = web_client
    form = _valid_form()
    form["flr"] = ""

    response = client.post("/predict", data=form)
    assert response.status_code == 200
    body = response.data.decode("utf-8")
    assert "FLR" in body or "층" in body


@patch("today_house_price.presentation.web.routes.build_predict_price_use_case")
def test_batch_predict_csv(mock_build, web_client) -> None:
    client, config = web_client
    mock_build.return_value.execute.return_value = PredictPriceResult(
        model_path=str(config.model_path),
        predictions=(
            PricePredictionItem(
                row_number=1,
                input_row={
                    "CGG_NM": "강남구",
                    "BLDG_USG": "아파트",
                    "ARCH_AREA": "84.5",
                    "ARCH_YR": "2010",
                    "FLR": "10",
                    "CTRT_DAY": "20240101",
                },
                predicted_amount=99000.0,
            ),
        ),
        skipped=(
            SkippedPredictionItem(
                row_number=2,
                input_row={"FLR": ""},
                reason="2번째 행: FLR 누락",
            ),
        ),
        total_rows=2,
        valid_rows=1,
        skipped_rows=1,
    )

    csv_content = (
        "CGG_NM,BLDG_USG,ARCH_AREA,ARCH_YR,FLR,CTRT_DAY\n"
        "강남구,아파트,84.5,2010,10,20240101\n"
        "강남구,아파트,84.5,2010,,20240101\n"
    )
    data = {
        "csv_file": (io.BytesIO(csv_content.encode("utf-8-sig")), "batch.csv"),
    }
    response = client.post("/batch", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    body = response.data.decode("utf-8")
    assert "일괄 예측 완료" in body
    assert "건너뜀 1건" in body

    prediction_files = list(config.upload_folder.glob("*_predictions.csv"))
    assert len(prediction_files) == 1


def test_download_missing_file_redirects(web_client) -> None:
    client, _ = web_client
    response = client.get("/download/not-found.csv")
    assert response.status_code == 302
