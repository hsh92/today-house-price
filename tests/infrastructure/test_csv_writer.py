"""CSV writer tests."""

from pathlib import Path

from today_house_price.infrastructure.persistence.csv_writer import CsvTransactionWriter

SAMPLE_ROW = {
    "RCPT_YR": "2024",
    "CGG_CD": "11680",
    "CGG_NM": "강남구",
    "STDG_CD": "10100",
    "STDG_NM": "역삼동",
    "LOTNO_SE": "1",
    "LOTNO_SE_NM": "대지",
    "MNO": "0001",
    "SNO": "0000",
    "BLDG_NM": "테스트아파트",
    "CTRT_DAY": "20240101",
    "THING_AMT": "100000",
    "ARCH_AREA": "84.5",
    "LAND_AREA": "0",
    "FLR": "10",
    "RGHT_SE": "",
    "RTRCN_DAY": "",
    "ARCH_YR": "2000",
    "BLDG_USG": "아파트",
    "DCLR_SE": "중개거래",
    "OPBIZ_RESTAGNT_SGG_NM": "서울 강남구",
}


def _full_row(**overrides: str) -> dict[str, str]:
    row = SAMPLE_ROW.copy()
    row.update(overrides)
    return row


def test_csv_writer_korean_headers(tmp_path: Path) -> None:
    output = tmp_path / "out.csv"
    writer = CsvTransactionWriter()
    size = writer.save([_full_row()], str(output), korean_headers=True)

    content = output.read_text(encoding="utf-8-sig")
    assert size > 0
    assert "접수년도" in content
    assert "강남구" in content


def test_csv_writer_english_headers(tmp_path: Path) -> None:
    output = tmp_path / "out_en.csv"
    writer = CsvTransactionWriter()
    writer.save([_full_row()], str(output), korean_headers=False)

    first_line = output.read_text(encoding="utf-8-sig").splitlines()[0]
    assert "RCPT_YR" in first_line
