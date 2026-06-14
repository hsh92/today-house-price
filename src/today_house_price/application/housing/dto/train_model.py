"""Train model DTO."""

from __future__ import annotations

from dataclasses import dataclass

from today_house_price.application.housing.dto.model_report import ModelPerformanceReportPaths
from today_house_price.domain.housing.metrics import RegressionMetrics


@dataclass(frozen=True)
class TrainPriceModelInput:
    train_path: str
    test_path: str
    model_output_path: str
    report_output_dir: str = "data/models/reports"
    generate_report: bool = True


@dataclass(frozen=True)
class TrainPriceModelResult:
    model_output_path: str
    train_rows: int
    test_rows: int
    train_metrics: RegressionMetrics
    test_metrics: RegressionMetrics
    report: ModelPerformanceReportPaths | None = None
