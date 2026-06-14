"""Sklearn predictor tests."""

from pathlib import Path

from today_house_price.infrastructure.ml.sklearn_predictor import SklearnPricePredictor
from today_house_price.infrastructure.ml.sklearn_trainer import SklearnLinearRegressionTrainer


def _sample_row(price: str, district: str = "강남구") -> dict[str, str]:
    return {
        "THING_AMT": price,
        "ARCH_AREA": "84.5",
        "ARCH_YR": "2010",
        "FLR": "10",
        "CTRT_DAY": "20240101",
        "CGG_NM": district,
        "BLDG_USG": "아파트",
    }


def test_sklearn_predictor_uses_trained_model(tmp_path: Path) -> None:
    trainer = SklearnLinearRegressionTrainer()
    train_rows = [
        _sample_row("100000", "강남구"),
        _sample_row("80000", "강북구"),
        _sample_row("120000", "강남구"),
        _sample_row("70000", "강북구"),
    ]
    model, _, _ = trainer.train(train_rows, train_rows)
    model_path = tmp_path / "model.joblib"
    trainer.save(model, str(model_path))

    predictor = SklearnPricePredictor()
    prediction = predictor.predict(
        str(model_path),
        [
            {
                "ARCH_AREA": "84.5",
                "ARCH_YR": "2010",
                "FLR": "10",
                "CTRT_DAY": "20240101",
                "CGG_NM": "강남구",
                "BLDG_USG": "아파트",
            }
        ],
    )

    assert len(prediction) == 1
    assert prediction[0] > 0
