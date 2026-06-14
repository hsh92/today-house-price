"""회귀 평가 지표 (Domain)."""

from __future__ import annotations

import math
from dataclasses import dataclass

DEFAULT_ACCURACY_TOLERANCE = 0.10


@dataclass(frozen=True)
class RegressionMetrics:
    mae: float
    rmse: float
    r2: float
    mape: float
    accuracy_rate: float
    sample_count: int
    accuracy_tolerance: float = DEFAULT_ACCURACY_TOLERANCE


def mean_absolute_error(y_true: list[float], y_pred: list[float]) -> float:
    if len(y_true) != len(y_pred) or not y_true:
        raise ValueError("예측값과 실제값 길이가 같고 비어 있지 않아야 합니다.")
    return sum(abs(t - p) for t, p in zip(y_true, y_pred, strict=True)) / len(y_true)


def root_mean_squared_error(y_true: list[float], y_pred: list[float]) -> float:
    if len(y_true) != len(y_pred) or not y_true:
        raise ValueError("예측값과 실제값 길이가 같고 비어 있지 않아야 합니다.")
    mse = sum((t - p) ** 2 for t, p in zip(y_true, y_pred, strict=True)) / len(y_true)
    return math.sqrt(mse)


def r2_score(y_true: list[float], y_pred: list[float]) -> float:
    if len(y_true) != len(y_pred) or not y_true:
        raise ValueError("예측값과 실제값 길이가 같고 비어 있지 않아야 합니다.")
    mean = sum(y_true) / len(y_true)
    ss_tot = sum((value - mean) ** 2 for value in y_true)
    if ss_tot == 0:
        return 1.0 if all(t == p for t, p in zip(y_true, y_pred, strict=True)) else 0.0
    ss_res = sum((t - p) ** 2 for t, p in zip(y_true, y_pred, strict=True))
    return 1.0 - (ss_res / ss_tot)


def mean_absolute_percentage_error(y_true: list[float], y_pred: list[float]) -> float:
    """평균 절대 오차율(MAPE, %)."""
    valid = [(t, p) for t, p in zip(y_true, y_pred, strict=True) if t != 0]
    if not valid:
        raise ValueError("MAPE 계산에 사용할 유효한 실제값이 없습니다.")
    return sum(abs(t - p) / abs(t) for t, p in valid) / len(valid) * 100.0


def prediction_accuracy_rate(
    y_true: list[float],
    y_pred: list[float],
    *,
    tolerance: float = DEFAULT_ACCURACY_TOLERANCE,
) -> float:
    """실제값 대비 오차가 tolerance 이내인 예측 비율(%)."""
    if not 0.0 < tolerance < 1.0:
        raise ValueError("tolerance는 0과 1 사이여야 합니다.")
    valid = [(t, p) for t, p in zip(y_true, y_pred, strict=True) if t != 0]
    if not valid:
        raise ValueError("정확도 계산에 사용할 유효한 실제값이 없습니다.")
    hits = sum(1 for t, p in valid if abs(p - t) / abs(t) <= tolerance)
    return hits / len(valid) * 100.0


def build_regression_metrics(
    y_true: list[float],
    y_pred: list[float],
    *,
    tolerance: float = DEFAULT_ACCURACY_TOLERANCE,
) -> RegressionMetrics:
    return RegressionMetrics(
        mae=mean_absolute_error(y_true, y_pred),
        rmse=root_mean_squared_error(y_true, y_pred),
        r2=r2_score(y_true, y_pred),
        mape=mean_absolute_percentage_error(y_true, y_pred),
        accuracy_rate=prediction_accuracy_rate(y_true, y_pred, tolerance=tolerance),
        sample_count=len(y_true),
        accuracy_tolerance=tolerance,
    )
