"""Model performance report DTO."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelPerformanceReportPaths:
    output_dir: str
    summary_json: str
    metrics_chart: str
    actual_vs_predicted_chart: str
    residuals_chart: str
