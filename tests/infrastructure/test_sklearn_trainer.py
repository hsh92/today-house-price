"""Sklearn trainer tests."""

from pathlib import Path

from today_house_price.infrastructure.ml.sklearn_trainer import SklearnLinearRegressionTrainer


def _sample_row(price: str, district: str = "강남구", usage: str = "아파트") -> dict[str, str]:
    return {
        "THING_AMT": price,
        "ARCH_AREA": "84.5",
        "ARCH_YR": "2010",
        "FLR": "10",
        "CTRT_DAY": "20240101",
        "CGG_NM": district,
        "BLDG_USG": usage,
    }


def test_sklearn_trainer_fit_and_save(tmp_path: Path) -> None:
    train_rows = [
        _sample_row("100000", "강남구"),
        _sample_row("80000", "강북구"),
        _sample_row("120000", "강남구", "오피스텔"),
        _sample_row("70000", "강북구"),
    ]
    test_rows = [
        _sample_row("95000", "강남구"),
        _sample_row("75000", "강북구"),
    ]
    trainer = SklearnLinearRegressionTrainer()
    model_path = tmp_path / "model.joblib"

    model, train_metrics, test_metrics = trainer.train(train_rows, test_rows)
    trainer.save(model, str(model_path))

    assert model_path.is_file()
    assert train_metrics.metrics.sample_count == 4
    assert test_metrics.metrics.sample_count == 2
    assert train_metrics.metrics.r2 > 0.5
