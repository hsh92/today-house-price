"""API 페이지 범위 계산 (Domain)."""

from __future__ import annotations


def page_ranges(
    total_count: int,
    page_size: int,
    max_pages: int | None = None,
) -> list[tuple[int, int]]:
    """(start_index, end_index) 페이지 구간 목록을 반환한다."""
    if total_count <= 0 or page_size <= 0:
        return []

    ranges: list[tuple[int, int]] = []
    start_index = 1
    page_no = 0

    while start_index <= total_count:
        page_no += 1
        if max_pages is not None and page_no > max_pages:
            break
        end_index = min(start_index + page_size - 1, total_count)
        ranges.append((start_index, end_index))
        start_index = end_index + 1

    return ranges
