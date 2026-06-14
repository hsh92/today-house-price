"""서울 열린데이터광장 API 클라이언트 (병렬 페이지·연도 수집)."""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any

import requests
from requests.adapters import HTTPAdapter

from today_house_price.domain.housing.fields import CSV_COLUMNS, LEGACY_FIELD_MAP
from today_house_price.domain.housing.pagination import page_ranges

BASE_URL = "http://openapi.seoul.go.kr:8088"
SERVICE_NAME = "tbLnOpendataRtmsV"
MAX_RETRIES = 3
DEFAULT_POOL_SIZE = 16


@dataclass
class ApiResult:
    code: str
    message: str
    total_count: int
    rows: list[dict[str, Any]]


_thread_local = threading.local()


def normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in row.items():
        canonical = LEGACY_FIELD_MAP.get(key, key)
        normalized[canonical] = value
    return {col: normalized.get(col, "") for col in CSV_COLUMNS}


def build_url(api_key: str, start: int, end: int, year: int | None = None) -> str:
    if year is None:
        return f"{BASE_URL}/{api_key}/json/{SERVICE_NAME}/{start}/{end}"
    return f"{BASE_URL}/{api_key}/json/{SERVICE_NAME}/{start}/{end}/{year}"


def parse_response(payload: dict[str, Any]) -> ApiResult:
    if SERVICE_NAME in payload:
        body = payload[SERVICE_NAME]
        result = body.get("RESULT", {})
        rows_raw = body.get("row")
        if rows_raw is None:
            rows: list[dict[str, Any]] = []
        elif isinstance(rows_raw, list):
            rows = rows_raw
        else:
            rows = [rows_raw]
        return ApiResult(
            code=result.get("CODE", ""),
            message=result.get("MESSAGE", ""),
            total_count=int(body.get("list_total_count", 0)),
            rows=rows,
        )

    result = payload.get("RESULT", {})
    return ApiResult(
        code=result.get("CODE", "UNKNOWN"),
        message=result.get("MESSAGE", ""),
        total_count=0,
        rows=[],
    )


def _create_session(pool_size: int) -> requests.Session:
    session = requests.Session()
    adapter = HTTPAdapter(pool_connections=pool_size, pool_maxsize=pool_size)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def _get_thread_session(pool_size: int) -> requests.Session:
    session = getattr(_thread_local, "session", None)
    if session is None:
        session = _create_session(pool_size)
        _thread_local.session = session
    return session


class SeoulOpenDataClient:
    def __init__(
        self,
        api_key: str,
        session: requests.Session | None = None,
        pool_size: int = DEFAULT_POOL_SIZE,
    ) -> None:
        self._api_key = api_key
        self._pool_size = pool_size
        self._session = session or _create_session(pool_size)
        self._progress_lock = threading.Lock()

    def fetch_page(
        self,
        start: int,
        end: int,
        year: int | None,
        timeout: int,
        session: requests.Session | None = None,
    ) -> ApiResult:
        url = build_url(self._api_key, start, end, year)
        http = session or self._session
        last_error: Exception | None = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = http.get(url, timeout=timeout)
                response.raise_for_status()
                return parse_response(response.json())
            except (requests.RequestException, ValueError) as exc:
                last_error = exc
                if attempt < MAX_RETRIES:
                    time.sleep(attempt)

        raise RuntimeError(f"API 요청 실패 ({start}-{end}, year={year}): {last_error}")

    def _log(self, on_progress: Callable[[str], None], message: str) -> None:
        with self._progress_lock:
            on_progress(message)

    def _fetch_page_task(
        self,
        start: int,
        end: int,
        year: int,
        timeout: int,
        delay: float,
    ) -> tuple[int, list[dict[str, Any]]]:
        if delay > 0:
            time.sleep(delay)
        session = _get_thread_session(self._pool_size)
        result = self.fetch_page(start, end, year, timeout, session=session)
        if result.code == "INFO-200":
            return start, []
        if result.code != "INFO-000":
            raise RuntimeError(f"[{year}] API 오류: {result.code} - {result.message}")
        return start, [normalize_row(row) for row in result.rows]

    def fetch_year(
        self,
        year: int,
        page_size: int,
        delay: float,
        timeout: int,
        max_pages: int | None,
        on_progress: Callable[[str], None],
        workers: int = 1,
    ) -> list[dict[str, Any]]:
        first = self.fetch_page(1, 1, year, timeout)

        if first.code == "INFO-200":
            self._log(on_progress, f"  [{year}] 데이터 없음 - 건너뜀")
            return []

        if first.code != "INFO-000":
            raise RuntimeError(f"[{year}] API 오류: {first.code} - {first.message}")

        total_count = first.total_count
        if total_count == 0:
            self._log(on_progress, f"  [{year}] 0건")
            return []

        ranges = page_ranges(total_count, page_size, max_pages)
        self._log(
            on_progress,
            f"  [{year}] 총 {total_count:,}건, {len(ranges)}페이지 (workers={workers})...",
        )

        if workers <= 1 or len(ranges) <= 1:
            return self._fetch_year_sequential(
                year, ranges, delay, timeout, on_progress, total_count
            )

        return self._fetch_year_parallel(
            year, ranges, delay, timeout, on_progress, total_count, workers
        )

    def _fetch_year_sequential(
        self,
        year: int,
        ranges: list[tuple[int, int]],
        delay: float,
        timeout: int,
        on_progress: Callable[[str], None],
        total_count: int,
    ) -> list[dict[str, Any]]:
        collected: list[dict[str, Any]] = []
        for page_no, (start_index, end_index) in enumerate(ranges, start=1):
            _, rows = self._fetch_page_task(start_index, end_index, year, timeout, delay)
            collected.extend(rows)
            self._log(
                on_progress,
                (
                    f"    [{year}] 페이지 {page_no}/{len(ranges)}: "
                    f"{len(collected):,}/{total_count:,}건"
                ),
            )
        return collected

    def _fetch_year_parallel(
        self,
        year: int,
        ranges: list[tuple[int, int]],
        delay: float,
        timeout: int,
        on_progress: Callable[[str], None],
        total_count: int,
        workers: int,
    ) -> list[dict[str, Any]]:
        page_results: dict[int, list[dict[str, Any]]] = {}
        completed_pages = 0

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(self._fetch_page_task, start, end, year, timeout, delay): (
                    start,
                    end,
                )
                for start, end in ranges
            }
            for future in as_completed(futures):
                start_index, rows = future.result()
                page_results[start_index] = rows
                completed_pages += 1
                done_rows = sum(len(page_results[key]) for key in page_results)
                self._log(
                    on_progress,
                    f"    [{year}] 페이지 {completed_pages}/{len(ranges)}: "
                    f"{done_rows:,}/{total_count:,}건",
                )

        collected: list[dict[str, Any]] = []
        for start_index, _ in ranges:
            collected.extend(page_results.get(start_index, []))
        return collected

    def fetch_years(
        self,
        years: list[int],
        page_size: int,
        delay: float,
        timeout: int,
        max_pages: int | None,
        on_progress: Callable[[str], None],
        workers: int = 1,
        year_workers: int = 1,
    ) -> list[dict[str, Any]]:
        if year_workers <= 1 or len(years) <= 1:
            all_rows: list[dict[str, Any]] = []
            for year in years:
                all_rows.extend(
                    self.fetch_year(
                        year,
                        page_size,
                        delay,
                        timeout,
                        max_pages,
                        on_progress,
                        workers,
                    )
                )
            return all_rows

        year_rows: dict[int, list[dict[str, Any]]] = {}
        with ThreadPoolExecutor(max_workers=year_workers) as executor:
            futures = {
                executor.submit(
                    self.fetch_year,
                    year,
                    page_size,
                    delay,
                    timeout,
                    max_pages,
                    on_progress,
                    workers,
                ): year
                for year in years
            }
            for future in as_completed(futures):
                year = futures[future]
                year_rows[year] = future.result()

        collected: list[dict[str, Any]] = []
        for year in years:
            collected.extend(year_rows.get(year, []))
        return collected
