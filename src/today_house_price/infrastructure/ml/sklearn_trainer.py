"""scikit-learn 선형 회귀 Trainer."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from today_house_price.domain.housing.evaluation import DatasetEvaluation
from today_house_price.domain.housing.features import (
    CATEGORICAL_FEATURE_COLUMNS,
    NUMERIC_FEATURE_COLUMNS,
    row_to_feature,
)
from today_house_price.domain.housing.metrics import build_regression_metrics


def _rows_to_matrix(rows: list[dict[str, Any]]) -> tuple[np.ndarray, np.ndarray, list[str]]:
    numeric_rows: list[list[float]] = []
    categorical_rows: list[list[str]] = []
    targets: list[float] = []

    for row in rows:
        feature = row_to_feature(row)
        if feature is None:
            continue
        numeric_rows.append([feature.numeric[column] for column in NUMERIC_FEATURE_COLUMNS])
        categorical_rows.append(
            [feature.categorical[column] for column in CATEGORICAL_FEATURE_COLUMNS]
        )
        targets.append(feature.target)

    if not numeric_rows:
        raise ValueError("특성 추출 가능한 행이 없습니다.")

    x = np.hstack(
        [
            np.asarray(numeric_rows, dtype=float),
            np.asarray(categorical_rows, dtype=object),
        ]
    )
    y = np.asarray(targets, dtype=float)
    feature_names = [*NUMERIC_FEATURE_COLUMNS, *CATEGORICAL_FEATURE_COLUMNS]
    return x, y, feature_names


def _build_evaluation(y_true: np.ndarray, y_pred: list[float]) -> DatasetEvaluation:
    actuals = y_true.tolist()
    return DatasetEvaluation(
        metrics=build_regression_metrics(actuals, y_pred),
        actuals=tuple(actuals),
        predictions=tuple(y_pred),
    )


class SklearnLinearRegressionTrainer:
    def build_pipeline(self, numeric_count: int) -> Pipeline:
        numeric_columns = list(range(numeric_count))
        categorical_columns = list(
            range(numeric_count, numeric_count + len(CATEGORICAL_FEATURE_COLUMNS))
        )

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", "passthrough", numeric_columns),
                (
                    "cat",
                    OneHotEncoder(handle_unknown="ignore"),
                    categorical_columns,
                ),
            ]
        )
        return Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("regressor", LinearRegression()),
            ]
        )

    def train(
        self,
        train_rows: list[dict[str, Any]],
        test_rows: list[dict[str, Any]],
    ) -> tuple[Pipeline, DatasetEvaluation, DatasetEvaluation]:
        x_train, y_train, _ = _rows_to_matrix(train_rows)
        x_test, y_test, _ = _rows_to_matrix(test_rows)

        model = self.build_pipeline(len(NUMERIC_FEATURE_COLUMNS))
        model.fit(x_train, y_train)

        train_evaluation = _build_evaluation(y_train, model.predict(x_train).tolist())
        test_evaluation = _build_evaluation(y_test, model.predict(x_test).tolist())

        return model, train_evaluation, test_evaluation

    def save(self, model: Pipeline, output_path: str) -> None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, path)
