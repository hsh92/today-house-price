"""Additional API client tests."""

from unittest.mock import MagicMock

import pytest

from today_house_price.infrastructure.api.seoul_open_data import (
    SeoulOpenDataClient,
    build_url,
)


def test_build_url_with_year() -> None:
    url = build_url("key123", 1, 100, 2024)
    assert url.endswith("/key123/json/tbLnOpendataRtmsV/1/100/2024")


def test_fetch_year_no_data() -> None:
    client = SeoulOpenDataClient(api_key="key")
    client.fetch_page = MagicMock(
        return_value=type(
            "R",
            (),
            {"code": "INFO-200", "message": "", "total_count": 0, "rows": []},
        )()
    )
    logs: list[str] = []
    rows = client.fetch_year(2020, 1000, 0, 10, None, logs.append)
    assert rows == []
    assert any("건너뜀" in line for line in logs)


def test_fetch_year_api_error() -> None:
    client = SeoulOpenDataClient(api_key="key")
    client.fetch_page = MagicMock(
        return_value=type(
            "R",
            (),
            {"code": "ERROR-500", "message": "fail", "total_count": 0, "rows": []},
        )()
    )
    with pytest.raises(RuntimeError, match="API 오류"):
        client.fetch_year(2024, 1000, 0, 10, None, lambda _: None)
