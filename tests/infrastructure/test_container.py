"""Container wiring tests."""

from today_house_price.infrastructure.container import build_fetch_and_export_use_case


def test_build_fetch_and_export_use_case() -> None:
    use_case = build_fetch_and_export_use_case("test-key")
    assert use_case is not None
