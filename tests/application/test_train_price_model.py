"""Train price model use case tests."""

from today_house_price.application.housing.dto.model_report import ModelPerformanceReportPaths
from today_house_price.application.housing.dto.train_model import TrainPriceModelInput
from today_house_price.application.housing.use_cases.train_price_model import TrainPriceModelUseCase
from today_house_price.domain.housing.evaluation import DatasetEvaluation
from today_house_price.domain.housing.metrics import RegressionMetrics


class FakeReader:
    def __init__(self, mapping):
        self.mapping = mapping

    def load(self, source_path: str):
        return self.mapping[source_path]


def _metrics(sample_count: int) -> RegressionMetrics:
    return RegressionMetrics(
        mae=1.0,
        rmse=2.0,
        r2=0.9,
        mape=5.0,
        accuracy_rate=60.0,
        sample_count=sample_count,
    )


def _evaluation(sample_count: int) -> DatasetEvaluation:
    actuals = tuple(float(i) for i in range(sample_count))
    predictions = actuals
    return DatasetEvaluation(
        metrics=_metrics(sample_count),
        actuals=actuals,
        predictions=predictions,
    )


class FakeTrainer:
    def train(self, train_rows, test_rows):
        return (
            {"model": True},
            _evaluation(len(train_rows)),
            _evaluation(len(test_rows)),
        )

    def save(self, model, output_path: str) -> None:
        self.saved_path = output_path


class FakeReporter:
    def generate(self, train_evaluation, test_evaluation, output_dir: str):
        return ModelPerformanceReportPaths(
            output_dir=output_dir,
            summary_json=f"{output_dir}/performance_summary.json",
            metrics_chart=f"{output_dir}/metrics_overview.png",
            actual_vs_predicted_chart=f"{output_dir}/actual_vs_predicted_test.png",
            residuals_chart=f"{output_dir}/residuals_test.png",
        )


def _sample_row(price: str) -> dict[str, str]:
    return {
        "THING_AMT": price,
        "ARCH_AREA": "84.5",
        "ARCH_YR": "2010",
        "FLR": "10",
        "CTRT_DAY": "20240101",
        "CGG_NM": "강남구",
        "BLDG_USG": "아파트",
    }


def test_train_price_model_use_case_generates_report() -> None:
    reader = FakeReader(
        {
            "train.csv": [_sample_row("100000")],
            "test.csv": [_sample_row("90000")],
        }
    )
    trainer = FakeTrainer()
    reporter = FakeReporter()
    use_case = TrainPriceModelUseCase(reader=reader, trainer=trainer, reporter=reporter)
    params = TrainPriceModelInput(
        train_path="train.csv",
        test_path="test.csv",
        model_output_path="data/models/model.joblib",
        report_output_dir="data/models/reports",
    )

    result = use_case.execute(params)

    assert result.train_rows == 1
    assert result.test_metrics.r2 == 0.9
    assert result.report is not None
    assert result.report.summary_json.endswith("performance_summary.json")
