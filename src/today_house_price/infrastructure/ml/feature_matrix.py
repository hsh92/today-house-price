"""특성 행 -> sklearn 입력 행렬 변환."""

from __future__ import annotations

from typing import Any

import numpy as np

from today_house_price.domain.housing.features import (
    CATEGORICAL_FEATURE_COLUMNS,
    NUMERIC_FEATURE_COLUMNS,
    row_to_feature,
    row_to_inference_input,
)


def _vector_from_parsed(parsed: dict[str, Any]) -> list[Any]:
    return [parsed[column] for column in NUMERIC_FEATURE_COLUMNS] + [
        parsed[column] for column in CATEGORICAL_FEATURE_COLUMNS
    ]


def rows_to_training_matrix(rows: list[dict[str, Any]]) -> tuple[np.ndarray, np.ndarray]:
    feature_rows: list[list[Any]] = []
    targets: list[float] = []

    for row in rows:
        feature = row_to_feature(row)
        if feature is None:
            continue
        parsed = {
            **feature.numeric,
            **feature.categorical,
        }
        feature_rows.append(_vector_from_parsed(parsed))
        targets.append(feature.target)

    if not feature_rows:
        raise ValueError("특성 추출 가능한 행이 없습니다.")

    x_matrix = np.asarray(feature_rows, dtype=object)
    x_matrix[:, : len(NUMERIC_FEATURE_COLUMNS)] = x_matrix[
        :, : len(NUMERIC_FEATURE_COLUMNS)
    ].astype(float)
    y_vector = np.asarray(targets, dtype=float)
    return x_matrix, y_vector


def rows_to_inference_matrix(rows: list[dict[str, Any]]) -> np.ndarray:
    feature_rows: list[list[Any]] = []

    for row in rows:
        parsed = row_to_inference_input(row)
        if parsed is None:
            continue
        feature_rows.append(_vector_from_parsed(parsed))

    if not feature_rows:
        raise ValueError("예측에 사용할 수 있는 입력이 없습니다.")

    x_matrix = np.asarray(feature_rows, dtype=object)
    x_matrix[:, : len(NUMERIC_FEATURE_COLUMNS)] = x_matrix[
        :, : len(NUMERIC_FEATURE_COLUMNS)
    ].astype(float)
    return x_matrix
