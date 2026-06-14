"""summary_builder tests."""

from today_house_price.application.housing.summary_builder import build_dataset_summary

SAMPLE_ROWS = [
    {
        "RCPT_YR": "2024",
        "CGG_NM": "강남구",
        "CTRT_DAY": "20240315",
        "THING_AMT": "100000",
        "BLDG_USG": "아파트",
    },
    {
        "RCPT_YR": "2024",
        "CGG_NM": "서초구",
        "CTRT_DAY": "20241101",
        "THING_AMT": "200000",
        "BLDG_USG": "아파트",
    },
    {
        "RCPT_YR": "2025",
        "CGG_NM": "강남구",
        "CTRT_DAY": "20250110",
        "THING_AMT": "150000",
        "BLDG_USG": "오피스텔",
    },
]


def test_build_dataset_summary_counts_and_amounts() -> None:
    summary = build_dataset_summary(
        rows=SAMPLE_ROWS,
        output_path="data/test.csv",
        file_size_bytes=1024,
        korean_headers=True,
    )

    assert summary.total_rows == 3
    assert summary.file_size_bytes == 1024
    assert summary.contract_date_min == "20240315"
    assert summary.contract_date_max == "20250110"
    assert summary.amount_min == 100_000
    assert summary.amount_max == 200_000
    assert summary.amount_avg == 150_000

    rcpt_labels = [item.label for item in summary.rcpt_year_counts]
    assert "2024" in rcpt_labels
    assert "2025" in rcpt_labels

    contract_labels = [item.label for item in summary.contract_year_counts]
    assert "2024" in contract_labels
    assert "2025" in contract_labels

    top_districts = [item.label for item in summary.district_top]
    assert "강남구" in top_districts


def test_summary_builder_invalid_amount() -> None:
    rows = [
        {
            "RCPT_YR": "2024",
            "CGG_NM": "a",
            "CTRT_DAY": "20240101",
            "THING_AMT": "abc",
            "BLDG_USG": "x",
        }
    ]
    summary = build_dataset_summary(rows, "data/x.csv", 1, False)
    assert summary.amount_min is None


def test_build_dataset_summary_empty_rows() -> None:
    summary = build_dataset_summary(
        rows=[],
        output_path="data/empty.csv",
        file_size_bytes=0,
        korean_headers=False,
    )

    assert summary.total_rows == 0
    assert summary.amount_min is None
    assert summary.contract_date_min == ""
