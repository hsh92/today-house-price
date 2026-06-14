"""Summary printer smoke test."""

from today_house_price.domain.housing.summary import CountItem, DatasetSummary
from today_house_price.infrastructure.reporting.summary_printer import print_dataset_summary


def test_print_dataset_summary(capsys) -> None:
    summary = DatasetSummary(
        total_rows=2,
        output_path="data/test.csv",
        file_size_bytes=2048,
        korean_headers=True,
        contract_date_min="20240101",
        contract_date_max="20240201",
        rcpt_year_counts=(CountItem("2024", 2),),
        contract_year_counts=(CountItem("2024", 2),),
        district_top=(CountItem("강남구", 2),),
        building_usage_top=(CountItem("아파트", 2),),
        amount_min=100,
        amount_max=200,
        amount_avg=150.0,
    )

    print_dataset_summary(summary)
    captured = capsys.readouterr().out

    assert "데이터 요약" in captured
    assert "포함 데이터 항목" in captured
    assert "강남구" in captured


def test_print_dataset_summary_empty_sections(capsys) -> None:
    summary = DatasetSummary(
        total_rows=0,
        output_path="data/empty.csv",
        file_size_bytes=0,
        korean_headers=False,
        contract_date_min="",
        contract_date_max="",
        rcpt_year_counts=(),
        contract_year_counts=(),
        district_top=(),
        building_usage_top=(),
        amount_min=None,
        amount_max=None,
        amount_avg=None,
    )

    print_dataset_summary(summary)
    captured = capsys.readouterr().out

    assert "(없음)" in captured
