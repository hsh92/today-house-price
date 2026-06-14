"""Model performance report tests."""

from today_house_price.domain.housing.evaluation import DatasetEvaluation
from today_house_price.domain.housing.metrics import build_regression_metrics
from today_house_price.infrastructure.reporting.model_performance_report import (
    MatplotlibModelPerformanceReporter,
)


def _evaluation(actuals: list[float], predictions: list[float]) -> DatasetEvaluation:
    return DatasetEvaluation(
        metrics=build_regression_metrics(actuals, predictions),
        actuals=tuple(actuals),
        predictions=tuple(predictions),
    )


def test_model_performance_reporter_creates_files(tmp_path) -> None:
    train_evaluation = _evaluation([100.0, 200.0, 300.0], [105.0, 195.0, 310.0])
    test_evaluation = _evaluation([150.0, 250.0], [160.0, 240.0])
    reporter = MatplotlibModelPerformanceReporter()

    report = reporter.generate(train_evaluation, test_evaluation, str(tmp_path))

    assert report.summary_json.endswith("performance_summary.json")
    assert (tmp_path / "performance_summary.json").is_file()
    assert (tmp_path / "metrics_overview.png").is_file()
    assert (tmp_path / "actual_vs_predicted_test.png").is_file()
    assert (tmp_path / "residuals_test.png").is_file()
