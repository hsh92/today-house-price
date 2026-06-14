"""Prediction error logger tests."""

from today_house_price.application.housing.dto.predict_price import SkippedPredictionItem
from today_house_price.infrastructure.reporting.prediction_error_logger import PredictionErrorLogger


def test_prediction_error_logger_writes_csv(tmp_path) -> None:
    skipped = (
        SkippedPredictionItem(
            row_number=274,
            input_row={
                "CGG_NM": "강남구",
                "BLDG_USG": "아파트",
                "ARCH_AREA": "84.5",
                "ARCH_YR": "2010",
                "FLR": "",
                "CTRT_DAY": "20240101",
            },
            reason="누락 또는 형식 오류: 층(FLR)",
        ),
    )
    log_path = tmp_path / "errors.csv"

    PredictionErrorLogger().save(str(log_path), skipped)

    content = log_path.read_text(encoding="utf-8-sig")
    assert "274" in content
    assert "층(FLR)" in content
