"""Evaluation tests."""

from today_house_price.domain.housing.evaluation import subsample_predictions


def test_subsample_predictions_keeps_all_when_small() -> None:
    actuals = [1.0, 2.0, 3.0]
    predictions = [1.1, 2.1, 2.9]

    sampled_actuals, sampled_predictions = subsample_predictions(
        actuals, predictions, max_points=10
    )

    assert sampled_actuals == actuals
    assert sampled_predictions == predictions


def test_subsample_predictions_limits_size() -> None:
    actuals = list(range(100))
    predictions = [float(value) for value in actuals]

    sampled_actuals, sampled_predictions = subsample_predictions(
        actuals,
        predictions,
        max_points=20,
        seed=1,
    )

    assert len(sampled_actuals) == 20
    assert len(sampled_predictions) == 20
