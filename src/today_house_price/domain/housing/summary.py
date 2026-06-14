"""수집·저장 데이터 요약 Value Object."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CountItem:
    label: str
    count: int


@dataclass(frozen=True)
class DatasetSummary:
    total_rows: int
    output_path: str
    file_size_bytes: int
    korean_headers: bool
    contract_date_min: str
    contract_date_max: str
    rcpt_year_counts: tuple[CountItem, ...]
    contract_year_counts: tuple[CountItem, ...]
    district_top: tuple[CountItem, ...]
    building_usage_top: tuple[CountItem, ...]
    amount_min: int | None
    amount_max: int | None
    amount_avg: float | None
