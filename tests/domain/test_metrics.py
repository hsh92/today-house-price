"""Metrics tests."""

from today_house_price.domain.housing.metrics import (
    build_regression_metrics,
    mean_absolute_error,
    mean_absolute_percentage_error,
    prediction_accuracy_rate,
    r2_score,
    root_mean_squared_error,
)


def test_regression_metrics() -> None:
    y_true = [100.0, 200.0, 300.0]
    y_pred = [110.0, 190.0, 310.0]

    assert mean_absolute_error(y_true, y_pred) == 10.0
    assert root_mean_squared_error(y_true, y_pred) == 10.0
    assert r2_score(y_true, y_pred) == 0.985
    assert mean_absolute_percentage_error(y_true, y_pred) == 6.111111111111112
    assert prediction_accuracy_rate(y_true, y_pred, tolerance=0.1) == 100.0

    metrics = build_regression_metrics(y_true, y_pred)
    assert metrics.sample_count == 3
    assert metrics.accuracy_rate == 100.0


def test_prediction_accuracy_rate_partial_hits() -> None:
    y_true = [100.0, 200.0, 300.0]
    y_pred = [105.0, 250.0, 310.0]

    assert prediction_accuracy_rate(y_true, y_pred, tolerance=0.1) == 66.66666666666666
