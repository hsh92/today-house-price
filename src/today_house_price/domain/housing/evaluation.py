"""모델 평가 결과 (Domain)."""

from __future__ import annotations

from dataclasses import dataclass

from today_house_price.domain.housing.metrics import RegressionMetrics


@dataclass(frozen=True)
class DatasetEvaluation:
    metrics: RegressionMetrics
    actuals: tuple[float, ...]
    predictions: tuple[float, ...]


def subsample_predictions(
    actuals: list[float] | tuple[float, ...],
    predictions: list[float] | tuple[float, ...],
    *,
    max_points: int = 5000,
    seed: int = 42,
) -> tuple[list[float], list[float]]:
    """시각화용으로 예측 쌍을 샘플링한다."""
    if len(actuals) != len(predictions):
        raise ValueError("actuals와 predictions 길이가 같아야 합니다.")
    if max_points < 1:
        raise ValueError("max_points는 1 이상이어야 합니다.")
    if len(actuals) <= max_points:
        return list(actuals), list(predictions)

    import random

    indices = list(range(len(actuals)))
    random.Random(seed).shuffle(indices)
    selected = sorted(indices[:max_points])
    return [actuals[i] for i in selected], [predictions[i] for i in selected]
