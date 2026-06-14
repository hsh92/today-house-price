"""Seoul Open Data API parser tests."""

from today_house_price.infrastructure.api.seoul_open_data import (
    normalize_row,
    parse_response,
)


def test_parse_response_single_row() -> None:
    payload = {
        "tbLnOpendataRtmsV": {
            "list_total_count": 1,
            "RESULT": {"CODE": "INFO-000", "MESSAGE": "ok"},
            "row": {
                "RCPT_YR": "2024",
                "CGG_NM": "강남구",
                "CTRT_DAY": "20241231",
                "THING_AMT": "50000",
                "BLDG_USG": "아파트",
            },
        }
    }

    result = parse_response(payload)

    assert result.code == "INFO-000"
    assert result.total_count == 1
    assert len(result.rows) == 1
    assert result.rows[0]["CGG_NM"] == "강남구"


def test_normalize_row_legacy_fields() -> None:
    row = normalize_row(
        {
            "ACC_YEAR": "2022",
            "SGG_NM": "종로구",
            "DEAL_YMD": "20221231",
            "OBJ_AMT": "30000",
            "HOUSE_TYPE": "아파트",
        }
    )

    assert row["RCPT_YR"] == "2022"
    assert row["CGG_NM"] == "종로구"
    assert row["CTRT_DAY"] == "20221231"
    assert row["THING_AMT"] == "30000"
    assert row["BLDG_USG"] == "아파트"


def test_parse_response_no_data() -> None:
    payload = {"RESULT": {"CODE": "INFO-200", "MESSAGE": "no data"}}

    result = parse_response(payload)

    assert result.code == "INFO-200"
    assert result.total_count == 0
    assert result.rows == []
