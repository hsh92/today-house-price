"""데이터셋 요약 생성 (Application)."""

from __future__ import annotations

from collections import Counter
from typing import Any

from today_house_price.domain.housing.summary import CountItem, DatasetSummary

TOP_N = 10
EMPTY_LABEL = "(미입력)"


def _label(value: Any) -> str:
    text = str(value).strip() if value is not None else ""
    return text if text else EMPTY_LABEL


def _sorted_counts(counter: Counter[str]) -> tuple[CountItem, ...]:
    return tuple(
        CountItem(label=label, count=count)
        for label, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    )


def _top_n(counter: Counter[str], n: int = TOP_N) -> tuple[CountItem, ...]:
    return _sorted_counts(counter)[:n]


def _parse_amount(value: Any) -> int | None:
    text = _label(value)
    if text == EMPTY_LABEL:
        return None
    try:
        return int(text.replace(",", ""))
    except ValueError:
        return None


def build_dataset_summary(
    rows: list[dict[str, Any]],
    output_path: str,
    file_size_bytes: int,
    korean_headers: bool,
) -> DatasetSummary:
    rcpt_years: Counter[str] = Counter()
    contract_years: Counter[str] = Counter()
    districts: Counter[str] = Counter()
    usages: Counter[str] = Counter()
    contract_dates: list[str] = []
    amounts: list[int] = []

    for row in rows:
        rcpt_years[_label(row.get("RCPT_YR"))] += 1
        districts[_label(row.get("CGG_NM"))] += 1
        usages[_label(row.get("BLDG_USG"))] += 1

        contract_day = _label(row.get("CTRT_DAY"))
        if contract_day != EMPTY_LABEL and len(contract_day) >= 4:
            contract_years[contract_day[:4]] += 1
            contract_dates.append(contract_day)

        amount = _parse_amount(row.get("THING_AMT"))
        if amount is not None:
            amounts.append(amount)

    date_min = min(contract_dates) if contract_dates else ""
    date_max = max(contract_dates) if contract_dates else ""

    return DatasetSummary(
        total_rows=len(rows),
        output_path=output_path,
        file_size_bytes=file_size_bytes,
        korean_headers=korean_headers,
        contract_date_min=date_min,
        contract_date_max=date_max,
        rcpt_year_counts=_sorted_counts(rcpt_years),
        contract_year_counts=_sorted_counts(contract_years),
        district_top=_top_n(districts),
        building_usage_top=_top_n(usages),
        amount_min=min(amounts) if amounts else None,
        amount_max=max(amounts) if amounts else None,
        amount_avg=sum(amounts) / len(amounts) if amounts else None,
    )
