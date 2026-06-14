"""모델 성능 리포트(수치·시각화) 생성."""

from __future__ import annotations

import json
import platform
from dataclasses import asdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from today_house_price.application.housing.dto.model_report import ModelPerformanceReportPaths
from today_house_price.domain.housing.evaluation import DatasetEvaluation, subsample_predictions


def _configure_plot_style() -> None:
    if platform.system() == "Windows":
        plt.rcParams["font.family"] = "Malgun Gothic"
    plt.rcParams["axes.unicode_minus"] = False


class MatplotlibModelPerformanceReporter:
    def generate(
        self,
        train_evaluation: DatasetEvaluation,
        test_evaluation: DatasetEvaluation,
        output_dir: str,
    ) -> ModelPerformanceReportPaths:
        report_dir = Path(output_dir)
        report_dir.mkdir(parents=True, exist_ok=True)

        summary_path = report_dir / "performance_summary.json"
        metrics_chart_path = report_dir / "metrics_overview.png"
        scatter_chart_path = report_dir / "actual_vs_predicted_test.png"
        residuals_chart_path = report_dir / "residuals_test.png"

        summary = {
            "train": asdict(train_evaluation.metrics),
            "test": asdict(test_evaluation.metrics),
        }
        summary_path.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        _configure_plot_style()
        self._save_metrics_chart(
            train_evaluation.metrics,
            test_evaluation.metrics,
            metrics_chart_path,
        )
        self._save_actual_vs_predicted_chart(test_evaluation, scatter_chart_path)
        self._save_residuals_chart(test_evaluation, residuals_chart_path)
        plt.close("all")

        return ModelPerformanceReportPaths(
            output_dir=str(report_dir.resolve()),
            summary_json=str(summary_path.resolve()),
            metrics_chart=str(metrics_chart_path.resolve()),
            actual_vs_predicted_chart=str(scatter_chart_path.resolve()),
            residuals_chart=str(residuals_chart_path.resolve()),
        )

    def _save_metrics_chart(self, train_metrics, test_metrics, output_path: Path) -> None:
        figure, axes = plt.subplots(1, 2, figsize=(12, 5))

        amount_labels = ["MAE", "RMSE"]
        train_amounts = [train_metrics.mae, train_metrics.rmse]
        test_amounts = [test_metrics.mae, test_metrics.rmse]
        amount_positions = range(len(amount_labels))
        width = 0.35
        axes[0].bar(
            [pos - width / 2 for pos in amount_positions],
            train_amounts,
            width,
            label="훈련",
        )
        axes[0].bar(
            [pos + width / 2 for pos in amount_positions],
            test_amounts,
            width,
            label="테스트",
        )
        axes[0].set_title("오차 지표 (만원)")
        axes[0].set_xticks(list(amount_positions))
        axes[0].set_xticklabels(amount_labels)
        axes[0].legend()

        rate_labels = ["MAPE", "예측정확도"]
        train_rates = [train_metrics.mape, train_metrics.accuracy_rate]
        test_rates = [test_metrics.mape, test_metrics.accuracy_rate]
        rate_positions = range(len(rate_labels))
        axes[1].bar(
            [pos - width / 2 for pos in rate_positions],
            train_rates,
            width,
            label="훈련",
        )
        axes[1].bar(
            [pos + width / 2 for pos in rate_positions],
            test_rates,
            width,
            label="테스트",
        )
        axes[1].set_title("비율 지표 (%)")
        axes[1].set_xticks(list(rate_positions))
        axes[1].set_xticklabels(rate_labels)
        axes[1].legend()

        figure.suptitle("모델 성능 지표 비교")
        figure.tight_layout()
        figure.savefig(output_path, dpi=120)
        plt.close(figure)

    def _save_actual_vs_predicted_chart(
        self,
        evaluation: DatasetEvaluation,
        output_path: Path,
    ) -> None:
        actuals, predictions = subsample_predictions(
            evaluation.actuals,
            evaluation.predictions,
        )
        figure, axis = plt.subplots(figsize=(8, 8))
        axis.scatter(actuals, predictions, alpha=0.35, s=12, label="예측")
        max_value = max(max(actuals), max(predictions))
        min_value = min(min(actuals), min(predictions))
        axis.plot([min_value, max_value], [min_value, max_value], "r--", label="완벽 예측")
        axis.set_title("테스트 실제값 vs 예측값")
        axis.set_xlabel("실제 거래금액 (만원)")
        axis.set_ylabel("예측 거래금액 (만원)")
        axis.legend()
        figure.tight_layout()
        figure.savefig(output_path, dpi=120)
        plt.close(figure)

    def _save_residuals_chart(self, evaluation: DatasetEvaluation, output_path: Path) -> None:
        actuals, predictions = subsample_predictions(evaluation.actuals, evaluation.predictions)
        residuals = [actual - pred for actual, pred in zip(actuals, predictions, strict=True)]

        figure, axis = plt.subplots(figsize=(8, 6))
        axis.hist(residuals, bins=40, color="#4C78A8", edgecolor="white")
        axis.axvline(0, color="red", linestyle="--", linewidth=1)
        axis.set_title("테스트 잔차 분포 (실제 - 예측)")
        axis.set_xlabel("잔차 (만원)")
        axis.set_ylabel("건수")
        figure.tight_layout()
        figure.savefig(output_path, dpi=120)
        plt.close(figure)
