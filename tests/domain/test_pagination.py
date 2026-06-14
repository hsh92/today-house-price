"""pagination tests."""

from today_house_price.domain.housing.pagination import page_ranges


def test_page_ranges_full_pages() -> None:
    assert page_ranges(2500, 1000) == [(1, 1000), (1001, 2000), (2001, 2500)]


def test_page_ranges_max_pages() -> None:
    assert page_ranges(5000, 1000, max_pages=2) == [(1, 1000), (1001, 2000)]


def test_page_ranges_empty() -> None:
    assert page_ranges(0, 1000) == []
