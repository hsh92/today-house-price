"""years helper tests."""

from datetime import date

from today_house_price.domain.housing.years import get_target_years


def test_get_target_years_count_and_range() -> None:
    years = get_target_years(5)
    current = date.today().year

    assert len(years) == 5
    assert years[0] == current - 4
    assert years[-1] == current


def test_get_target_years_excludes_current() -> None:
    years = get_target_years(3, include_current_year=False)
    current = date.today().year

    assert len(years) == 3
    assert years[-1] == current - 1
