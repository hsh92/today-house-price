"""회귀 모델용 특성 정의·파싱 (Domain)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

TARGET_COLUMN = "THING_AMT"

NUMERIC_FEATURE_COLUMNS: tuple[str, ...] = (
    "ARCH_AREA",
    "ARCH_YR",
    "FLR",
    "CONTRACT_YEAR",
    "CONTRACT_MONTH",
)

CATEGORICAL_FEATURE_COLUMNS: tuple[str, ...] = (
    "CGG_NM",
    "BLDG_USG",
)


@dataclass(frozen=True)
class ModelFeatureRow:
    target: float
    numeric: dict[str, float]
    categorical: dict[str, str]


def parse_amount(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip().replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_numeric(value: Any) -> float | None:
    return parse_amount(value)


def parse_contract_parts(ctrt_day: Any) -> tuple[int, int] | None:
    text = str(ctrt_day).strip()
    if len(text) != 8 or not text.isdigit():
        return None
    return int(text[:4]), int(text[4:6])


def row_to_inference_input(row: dict[str, Any]) -> dict[str, Any] | None:
    """학습 때와 동일한 특성을 만든다. THING_AMT(목표값)는 필요 없다."""
    if describe_inference_row_errors(row):
        return None

    arch_area = parse_numeric(row.get("ARCH_AREA"))
    arch_yr = parse_numeric(row.get("ARCH_YR"))
    floor = parse_numeric(row.get("FLR"))
    contract = parse_contract_parts(row.get("CTRT_DAY"))
    if None in (arch_area, arch_yr, floor) or contract is None:
        return None

    contract_year, contract_month = contract
    return {
        "ARCH_AREA": arch_area,
        "ARCH_YR": arch_yr,
        "FLR": floor,
        "CONTRACT_YEAR": float(contract_year),
        "CONTRACT_MONTH": float(contract_month),
        "CGG_NM": str(row.get("CGG_NM", "")).strip(),
        "BLDG_USG": str(row.get("BLDG_USG", "")).strip(),
    }


def describe_inference_row_errors(row: dict[str, Any]) -> str:
    """유효하지 않으면 사람이 읽을 수 있는 오류 메시지를 반환한다."""
    errors: list[str] = []

    if not str(row.get("CGG_NM", "")).strip():
        errors.append("자치구명(CGG_NM)")
    if not str(row.get("BLDG_USG", "")).strip():
        errors.append("건물용도(BLDG_USG)")
    if parse_numeric(row.get("ARCH_AREA")) is None:
        errors.append("건물면적(ARCH_AREA)")
    if parse_numeric(row.get("ARCH_YR")) is None:
        errors.append("건축년도(ARCH_YR)")
    if parse_numeric(row.get("FLR")) is None:
        errors.append("층(FLR)")
    if parse_contract_parts(row.get("CTRT_DAY")) is None:
        errors.append("계약일(CTRT_DAY, YYYYMMDD)")

    if not errors:
        return ""
    return "누락 또는 형식 오류: " + ", ".join(errors)


def row_to_feature(row: dict[str, Any]) -> ModelFeatureRow | None:
    target = parse_amount(row.get(TARGET_COLUMN))
    if target is None:
        return None

    arch_area = parse_numeric(row.get("ARCH_AREA"))
    arch_yr = parse_numeric(row.get("ARCH_YR"))
    floor = parse_numeric(row.get("FLR"))
    contract = parse_contract_parts(row.get("CTRT_DAY"))
    if None in (arch_area, arch_yr, floor) or contract is None:
        return None

    contract_year, contract_month = contract
    cgg_nm = str(row.get("CGG_NM", "")).strip()
    bldg_usg = str(row.get("BLDG_USG", "")).strip()
    if not cgg_nm or not bldg_usg:
        return None

    return ModelFeatureRow(
        target=target,
        numeric={
            "ARCH_AREA": arch_area,
            "ARCH_YR": arch_yr,
            "FLR": floor,
            "CONTRACT_YEAR": float(contract_year),
            "CONTRACT_MONTH": float(contract_month),
        },
        categorical={
            "CGG_NM": cgg_nm,
            "BLDG_USG": bldg_usg,
        },
    )
