"""Predict price use case tests."""

from today_house_price.application.housing.dto.predict_price import PredictPriceInput
from today_house_price.application.housing.use_cases.predict_price import PredictPriceUseCase


class FakePredictor:
    def predict(self, model_path: str, rows):
        assert model_path == "data/models/model.joblib"
        return [float(index * 10000) for index, _ in enumerate(rows, start=1)]


def _valid_row(**overrides: str) -> dict[str, str]:
    row = {
        "CGG_NM": "강남구",
        "BLDG_USG": "아파트",
        "ARCH_AREA": "84.5",
        "ARCH_YR": "2010",
        "FLR": "10",
        "CTRT_DAY": "20240101",
    }
    row.update(overrides)
    return row


def test_predict_price_use_case() -> None:
    use_case = PredictPriceUseCase(predictor=FakePredictor())
    params = PredictPriceInput(
        model_path="data/models/model.joblib",
        properties=(_valid_row(),),
    )

    result = use_case.execute(params)

    assert len(result.predictions) == 1
    assert result.predictions[0].predicted_amount == 10000.0
    assert result.skipped_rows == 0


def test_predict_price_use_case_skips_invalid_rows_in_batch_mode() -> None:
    use_case = PredictPriceUseCase(predictor=FakePredictor())
    params = PredictPriceInput(
        model_path="data/models/model.joblib",
        properties=(
            _valid_row(),
            _valid_row(FLR=""),
            _valid_row(CGG_NM="송파구"),
        ),
        skip_invalid=True,
    )

    result = use_case.execute(params)

    assert result.total_rows == 3
    assert result.valid_rows == 2
    assert result.skipped_rows == 1
    assert result.skipped[0].row_number == 2
    assert "FLR" in result.skipped[0].reason


def test_predict_price_use_case_raises_on_invalid_single_row() -> None:
    use_case = PredictPriceUseCase(predictor=FakePredictor())
    params = PredictPriceInput(
        model_path="data/models/model.joblib",
        properties=(_valid_row(FLR=""),),
        skip_invalid=False,
    )

    try:
        use_case.execute(params)
        raised = False
    except ValueError as exc:
        raised = True
        assert "1번째" in str(exc)

    assert raised
