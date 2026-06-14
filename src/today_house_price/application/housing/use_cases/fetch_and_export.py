"""Fetch and export use case."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

from today_house_price.application.housing.summary_builder import build_dataset_summary
from today_house_price.domain.housing.summary import DatasetSummary


class TransactionFetcher(Protocol):
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
    ) -> list[dict[str, Any]]: ...


class CsvExporter(Protocol):
    def save(
        self,
        rows: list[dict[str, Any]],
        output_path: str,
        korean_headers: bool,
    ) -> int: ...


@dataclass(frozen=True)
class FetchAndExportInput:
    years_back: int
    output_path: str
    korean_headers: bool
    page_size: int
    delay: float
    timeout: int
    max_pages: int | None
    workers: int = 6
    year_workers: int = 2


@dataclass(frozen=True)
class FetchAndExportResult:
    rows: list[dict[str, Any]]
    summary: DatasetSummary
    target_years: tuple[int, ...]


class FetchAndExportUseCase:
    def __init__(self, fetcher: TransactionFetcher, exporter: CsvExporter) -> None:
        self._fetcher = fetcher
        self._exporter = exporter

    def execute(self, params: FetchAndExportInput, target_years: list[int]) -> FetchAndExportResult:
        rows = self._fetcher.fetch_years(
            years=target_years,
            page_size=params.page_size,
            delay=params.delay,
            timeout=params.timeout,
            max_pages=params.max_pages,
            on_progress=print,
            workers=params.workers,
            year_workers=params.year_workers,
        )
        if not rows:
            raise ValueError("수집된 데이터가 없습니다.")

        file_size = self._exporter.save(rows, params.output_path, params.korean_headers)
        summary = build_dataset_summary(
            rows=rows,
            output_path=params.output_path,
            file_size_bytes=file_size,
            korean_headers=params.korean_headers,
        )
        return FetchAndExportResult(
            rows=rows,
            summary=summary,
            target_years=tuple(target_years),
        )
