"""Train linear regression price model use case."""

from __future__ import annotations

from typing import Any, Protocol

from today_house_price.application.housing.dto.model_report import ModelPerformanceReportPaths
from today_house_price.application.housing.dto.train_model import (
    TrainPriceModelInput,
    TrainPriceModelResult,
)
from today_house_price.domain.housing.evaluation import DatasetEvaluation


class TransactionDatasetReader(Protocol):
    def load(self, source_path: str) -> list[dict[str, Any]]: ...


class PriceModelTrainer(Protocol):
    def train(
        self,
        train_rows: list[dict[str, Any]],
        test_rows: list[dict[str, Any]],
    ) -> tuple[Any, DatasetEvaluation, DatasetEvaluation]: ...

    def save(self, model: Any, output_path: str) -> None: ...


class ModelPerformanceReporter(Protocol):
    def generate(
        self,
        train_evaluation: DatasetEvaluation,
        test_evaluation: DatasetEvaluation,
        output_dir: str,
    ) -> ModelPerformanceReportPaths: ...


class TrainPriceModelUseCase:
    def __init__(
        self,
        reader: TransactionDatasetReader,
        trainer: PriceModelTrainer,
        reporter: ModelPerformanceReporter | None = None,
    ) -> None:
        self._reader = reader
        self._trainer = trainer
        self._reporter = reporter

    def execute(self, params: TrainPriceModelInput) -> TrainPriceModelResult:
        train_rows = self._reader.load(params.train_path)
        test_rows = self._reader.load(params.test_path)

        if not train_rows:
            raise ValueError("훈련 CSV에 데이터 행이 없습니다.")
        if not test_rows:
            raise ValueError("테스트 CSV에 데이터 행이 없습니다.")

        model, train_evaluation, test_evaluation = self._trainer.train(train_rows, test_rows)
        self._trainer.save(model, params.model_output_path)

        report = None
        if params.generate_report:
            if self._reporter is None:
                raise ValueError("리포트 생성기가 설정되지 않았습니다.")
            report = self._reporter.generate(
                train_evaluation,
                test_evaluation,
                params.report_output_dir,
            )

        return TrainPriceModelResult(
            model_output_path=params.model_output_path,
            train_rows=len(train_rows),
            test_rows=len(test_rows),
            train_metrics=train_evaluation.metrics,
            test_metrics=test_evaluation.metrics,
            report=report,
        )
