"""Predict house price use case."""

from __future__ import annotations

from typing import Any, Protocol

from today_house_price.application.housing.dto.predict_price import (
    PredictPriceInput,
    PredictPriceResult,
    PricePredictionItem,
    SkippedPredictionItem,
)
from today_house_price.domain.housing.features import describe_inference_row_errors


class PriceModelPredictor(Protocol):
    def predict(self, model_path: str, rows: list[dict[str, Any]]) -> list[float]: ...


class PredictPriceUseCase:
    def __init__(self, predictor: PriceModelPredictor) -> None:
        self._predictor = predictor

    def execute(self, params: PredictPriceInput) -> PredictPriceResult:
        if not params.properties:
            raise ValueError("예측할 매물 정보가 없습니다.")

        valid_rows: list[tuple[int, dict[str, Any]]] = []
        skipped: list[SkippedPredictionItem] = []

        for row_number, row in enumerate(params.properties, start=1):
            reason = describe_inference_row_errors(row)
            if reason:
                if params.skip_invalid:
                    skipped.append(
                        SkippedPredictionItem(
                            row_number=row_number,
                            input_row=row,
                            reason=reason,
                        )
                    )
                    continue
                raise ValueError(f"{row_number}번째 입력이 올바르지 않습니다. {reason}")

            valid_rows.append((row_number, row))

        if not valid_rows:
            raise ValueError("예측에 사용할 수 있는 유효한 행이 없습니다.")

        predicted_amounts = self._predictor.predict(
            params.model_path,
            [row for _, row in valid_rows],
        )
        predictions = tuple(
            PricePredictionItem(
                row_number=row_number,
                input_row=row,
                predicted_amount=predicted_amount,
            )
            for (row_number, row), predicted_amount in zip(
                valid_rows, predicted_amounts, strict=True
            )
        )

        return PredictPriceResult(
            model_path=params.model_path,
            predictions=predictions,
            skipped=tuple(skipped),
            total_rows=len(params.properties),
            valid_rows=len(valid_rows),
            skipped_rows=len(skipped),
        )
