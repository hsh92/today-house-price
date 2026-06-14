"""Feature parsing tests."""

from today_house_price.domain.housing.features import (
    describe_inference_row_errors,
    parse_amount,
    parse_contract_parts,
    row_to_feature,
    row_to_inference_input,
)


def test_describe_inference_row_errors() -> None:
    assert describe_inference_row_errors({"FLR": ""}) != ""
    assert describe_inference_row_errors(
        {
            "CGG_NM": "강남구",
            "BLDG_USG": "아파트",
            "ARCH_AREA": "84.5",
            "ARCH_YR": "2010",
            "FLR": "10",
            "CTRT_DAY": "20240101",
        }
    ) == ""


def test_row_to_inference_input_without_target() -> None:
    parsed = row_to_inference_input(
        {
            "ARCH_AREA": "84.5",
            "ARCH_YR": "2010",
            "FLR": "12",
            "CTRT_DAY": "20240315",
            "CGG_NM": "강남구",
            "BLDG_USG": "아파트",
        }
    )

    assert parsed is not None
    assert parsed["ARCH_AREA"] == 84.5
    assert parsed["CONTRACT_YEAR"] == 2024.0


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
