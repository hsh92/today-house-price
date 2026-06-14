"""CSV reader tests."""

from pathlib import Path

from today_house_price.infrastructure.persistence.csv_reader import CsvTransactionReader


def test_csv_reader_loads_english_headers() -> None:
    fixture = Path("tests/fixtures/sample_transactions.csv")
    rows = CsvTransactionReader().load(str(fixture))

    assert len(rows) == 3
    assert rows[0]["CGG_NM"] == "강남구"
    assert rows[1]["THING_AMT"] == ""


def test_csv_reader_loads_korean_headers(tmp_path: Path) -> None:
    csv_path = tmp_path / "korean.csv"
    csv_path.write_text(
        "접수년도,자치구명,법정동명,계약일,물건금액_만원,건물면적_㎡,건축년도,건물용도,층\n"
        "2024,강남구,역삼동,20240101,100000,84.5,2010,아파트,10\n",
        encoding="utf-8-sig",
    )

    rows = CsvTransactionReader().load(str(csv_path))

    assert rows[0]["RCPT_YR"] == "2024"
    assert rows[0]["THING_AMT"] == "100000"
