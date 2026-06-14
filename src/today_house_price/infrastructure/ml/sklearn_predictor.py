"""scikit-learn 모델 예측 Adapter."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
from sklearn.pipeline import Pipeline

from today_house_price.infrastructure.ml.feature_matrix import rows_to_inference_matrix


class SklearnPricePredictor:
    def load(self, model_path: str) -> Pipeline:
        path = Path(model_path)
        if not path.is_file():
            raise FileNotFoundError(f"모델 파일을 찾을 수 없습니다: {path.resolve()}")
        model = joblib.load(path)
        if not hasattr(model, "predict"):
            raise ValueError("로드한 객체가 예측 모델이 아닙니다.")
        return model

    def predict(self, model_path: str, rows: list[dict[str, Any]]) -> list[float]:
        model = self.load(model_path)
        matrix = rows_to_inference_matrix(rows)
        predictions = model.predict(matrix)
        return [float(value) for value in predictions.tolist()]
