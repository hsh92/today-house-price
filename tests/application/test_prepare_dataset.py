"""Prepare dataset use case tests."""

from today_house_price.application.housing.dto.prepare_dataset import PrepareDatasetInput
from today_house_price.application.housing.use_cases.prepare_dataset import PrepareDatasetUseCase


class FakeReader:
    def __init__(self, rows):
        self.rows = rows

    def load(self, source_path: str):
        return self.rows


class FakeWriter:
    def __init__(self):
        self.saved: dict[str, list] = {}

    def save(self, rows, output_path, korean_headers):
        self.saved[output_path] = rows
        return len(rows) * 10


def test_prepare_dataset_use_case() -> None:
    rows = [
        {
            "RCPT_YR": "2024",
            "CGG_NM": "강남구",
            "STDG_NM": "역삼동",
            "CTRT_DAY": "20240101",
            "THING_AMT": "100000",
            "ARCH_AREA": "84.5",
            "ARCH_YR": "2010",
            "BLDG_USG": "아파트",
            "FLR": "10",
        },
        {
            "RCPT_YR": "2024",
            "CGG_NM": "서초구",
            "STDG_NM": "반포동",
            "CTRT_DAY": "20240201",
            "THING_AMT": "",
            "ARCH_AREA": "59.9",
            "ARCH_YR": "2005",
            "BLDG_USG": "아파트",
            "FLR": "8",
        },
        {
            "RCPT_YR": "2024",
            "CGG_NM": "송파구",
            "STDG_NM": "잠실동",
            "CTRT_DAY": "20240301",
            "THING_AMT": "90000",
            "ARCH_AREA": "84.5",
            "ARCH_YR": "2012",
            "BLDG_USG": "아파트",
            "FLR": "15",
        },
        {
            "RCPT_YR": "2024",
            "CGG_NM": "마포구",
            "STDG_NM": "공덕동",
            "CTRT_DAY": "20240401",
            "THING_AMT": "80000",
            "ARCH_AREA": "59.9",
            "ARCH_YR": "2008",
            "BLDG_USG": "아파트",
            "FLR": "5",
        },
        {
            "RCPT_YR": "2024",
            "CGG_NM": "용산구",
            "STDG_NM": "이촌동",
            "CTRT_DAY": "20240501",
            "THING_AMT": "120000",
            "ARCH_AREA": "84.5",
            "ARCH_YR": "2015",
            "BLDG_USG": "아파트",
            "FLR": "20",
        },
    ]
    writer = FakeWriter()
    use_case = PrepareDatasetUseCase(reader=FakeReader(rows), writer=writer)
    params = PrepareDatasetInput(
        source_path="data/in.csv",
        train_output_path="data/train.csv",
        test_output_path="data/test.csv",
        train_ratio=0.8,
        seed=42,
    )

    result = use_case.execute(params)

    assert result.total_rows == 5
    assert result.removed_rows == 1
    assert result.train_rows == 3
    assert result.test_rows == 1
    assert len(writer.saved["data/train.csv"]) == 3
    assert len(writer.saved["data/test.csv"]) == 1
