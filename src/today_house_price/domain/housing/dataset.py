"""Dataset completeness and split rules."""

from __future__ import annotations

from typing import Any

from today_house_price.domain.housing.fields import CSV_COLUMNS

# 집값 예측 등 ML에 필요한 핵심 컬럼 (API상 자주 비는 해제일·중개사 등은 제외)
ML_REQUIRED_COLUMNS: tuple[str, ...] = (
    "RCPT_YR",
    "CGG_NM",
    "STDG_NM",
    "CTRT_DAY",
    "THING_AMT",
    "ARCH_AREA",
    "ARCH_YR",
    "BLDG_USG",
    "FLR",
)


def is_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    return False


def row_is_complete(
    row: dict[str, Any],
    required_columns: tuple[str, ...],
) -> bool:
    return all(not is_blank(row.get(column)) for column in required_columns)


def filter_complete_rows(
    rows: list[dict[str, Any]],
    *,
    required_columns: tuple[str, ...] = ML_REQUIRED_COLUMNS,
    strict: bool = False,
) -> tuple[list[dict[str, Any]], int]:
    """누락 행을 제거한다. strict=True면 모든 CSV 컬럼이 채워져야 한다."""
    columns = CSV_COLUMNS if strict else required_columns
    kept: list[dict[str, Any]] = []
    for row in rows:
        if row_is_complete(row, columns):
            kept.append(row)
    removed = len(rows) - len(kept)
    return kept, removed


def split_train_test(
    rows: list[dict[str, Any]],
    *,
    train_ratio: float = 0.8,
    seed: int = 42,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not 0.0 < train_ratio < 1.0:
        raise ValueError("train_ratio는 0과 1 사이여야 합니다.")

    import random

    shuffled = list(rows)
    random.Random(seed).shuffle(shuffled)
    split_at = int(len(shuffled) * train_ratio)
    return shuffled[:split_at], shuffled[split_at:]
