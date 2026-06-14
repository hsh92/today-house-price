"""연도 범위 계산."""

from __future__ import annotations

from datetime import date


def get_target_years(years_back: int, include_current_year: bool = True) -> list[int]:
    current_year = date.today().year
    if include_current_year:
        start_year = current_year - years_back + 1
        return list(range(start_year, current_year + 1))
    end_year = current_year - 1
    return list(range(end_year - years_back + 1, end_year + 1))
