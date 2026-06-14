"""Predict price DTO."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PricePredictionItem:
    row_number: int
    input_row: dict[str, Any]
    predicted_amount: float


@dataclass(frozen=True)
class SkippedPredictionItem:
    row_number: int
    input_row: dict[str, Any]
    reason: str


@dataclass(frozen=True)
class PredictPriceInput:
    model_path: str
    properties: tuple[dict[str, Any], ...]
    skip_invalid: bool = False


@dataclass(frozen=True)
class PredictPriceResult:
    model_path: str
    predictions: tuple[PricePredictionItem, ...]
    skipped: tuple[SkippedPredictionItem, ...]
    total_rows: int
    valid_rows: int
    skipped_rows: int
