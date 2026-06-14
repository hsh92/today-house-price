"""Parallel fetch tests."""

from unittest.mock import MagicMock

from today_house_price.infrastructure.api.seoul_open_data import ApiResult, SeoulOpenDataClient


def _row(seq: str) -> dict[str, str]:
    return {
        "RCPT_YR": "2024",
        "CGG_NM": seq,
        "CTRT_DAY": "20240101",
        "THING_AMT": "10000",
        "BLDG_USG": "아파트",
    }


def test_fetch_year_parallel_preserves_page_order() -> None:
    client = SeoulOpenDataClient(api_key="key")
    probe_calls = {"count": 0}

    def mock_fetch_page(start, end, year, timeout, session=None):
        if start == 1 and end == 1:
            probe_calls["count"] += 1
            if probe_calls["count"] == 1:
                return ApiResult(
                    code="INFO-000",
                    message="ok",
                    total_count=3,
                    rows=[],
                )
        return ApiResult(
            code="INFO-000",
            message="ok",
            total_count=3,
            rows=[_row(str(start))],
        )

    client.fetch_page = MagicMock(side_effect=mock_fetch_page)

    rows = client.fetch_year(
        year=2024,
        page_size=1,
        delay=0,
        timeout=10,
        max_pages=None,
        on_progress=lambda _: None,
        workers=3,
    )

    assert [row["CGG_NM"] for row in rows] == ["1", "2", "3"]
