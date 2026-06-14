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
)
from today_house_price.domain.housing.metrics import build_regression_metrics
from today_house_price.infrastructure.ml.feature_matrix import rows_to_training_matrix


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
        x_train, y_train = rows_to_training_matrix(train_rows)
        x_test, y_test = rows_to_training_matrix(test_rows)

        model = self.build_pipeline(len(NUMERIC_FEATURE_COLUMNS))
        model.fit(x_train, y_train)

        train_evaluation = _build_evaluation(y_train, model.predict(x_train).tolist())
        test_evaluation = _build_evaluation(y_test, model.predict(x_test).tolist())

        return model, train_evaluation, test_evaluation

    def save(self, model: Pipeline, output_path: str) -> None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, path)
