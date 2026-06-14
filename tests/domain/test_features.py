"""Feature parsing tests."""

from today_house_price.domain.housing.features import (
    parse_amount,
    parse_contract_parts,
    row_to_feature,
)


def test_row_to_feature() -> None:
    feature = row_to_feature(
        {
            "THING_AMT": "50000",
            "ARCH_AREA": "84.5",
            "ARCH_YR": "2010",
            "FLR": "12",
            "CTRT_DAY": "20240315",
            "CGG_NM": "강남구",
            "BLDG_USG": "아파트",
        }
    )

    assert feature is not None
    assert feature.target == 50000.0
    assert feature.numeric["CONTRACT_YEAR"] == 2024.0
    assert feature.numeric["CONTRACT_MONTH"] == 3.0
    assert feature.categorical["CGG_NM"] == "강남구"


def test_row_to_feature_returns_none_when_invalid() -> None:
    assert row_to_feature({"THING_AMT": ""}) is None
    assert parse_amount(" 12,000 ") == 12000.0
    assert parse_contract_parts("20240101") == (2024, 1)
    assert parse_contract_parts("invalid") is None
