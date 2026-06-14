"""Use Case 조립."""

from __future__ import annotations

from today_house_price.application.housing.use_cases.fetch_and_export import FetchAndExportUseCase
from today_house_price.application.housing.use_cases.prepare_dataset import PrepareDatasetUseCase
from today_house_price.infrastructure.api.seoul_open_data import SeoulOpenDataClient
from today_house_price.infrastructure.persistence.csv_reader import CsvTransactionReader
from today_house_price.infrastructure.persistence.csv_writer import CsvTransactionWriter


def build_fetch_and_export_use_case(api_key: str) -> FetchAndExportUseCase:
    fetcher = SeoulOpenDataClient(api_key=api_key)
    exporter = CsvTransactionWriter()
    return FetchAndExportUseCase(fetcher=fetcher, exporter=exporter)


def build_prepare_dataset_use_case() -> PrepareDatasetUseCase:
    reader = CsvTransactionReader()
    writer = CsvTransactionWriter()
    return PrepareDatasetUseCase(reader=reader, writer=writer)
