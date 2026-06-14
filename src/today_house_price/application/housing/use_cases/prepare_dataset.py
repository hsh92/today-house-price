"""Prepare ML train/test dataset use case."""

from __future__ import annotations

from typing import Any, Protocol

from today_house_price.application.housing.dto.prepare_dataset import (
    PrepareDatasetInput,
    PrepareDatasetResult,
)
from today_house_price.domain.housing.dataset import filter_complete_rows, split_train_test


class TransactionDatasetReader(Protocol):
    def load(self, source_path: str) -> list[dict[str, Any]]: ...


class TransactionDatasetWriter(Protocol):
    def save(
        self,
        rows: list[dict[str, Any]],
        output_path: str,
        korean_headers: bool,
    ) -> int: ...


class PrepareDatasetUseCase:
    def __init__(
        self,
        reader: TransactionDatasetReader,
        writer: TransactionDatasetWriter,
    ) -> None:
        self._reader = reader
        self._writer = writer

    def execute(self, params: PrepareDatasetInput) -> PrepareDatasetResult:
        rows = self._reader.load(params.source_path)
        if not rows:
            raise ValueError("입력 CSV에 데이터 행이 없습니다.")

        complete_rows, removed = filter_complete_rows(rows, strict=params.strict)
        if not complete_rows:
            raise ValueError("누락값 제거 후 남은 데이터가 없습니다.")

        train_rows, test_rows = split_train_test(
            complete_rows,
            train_ratio=params.train_ratio,
            seed=params.seed,
        )

        train_size = self._writer.save(
            train_rows,
            params.train_output_path,
            params.korean_headers,
        )
        test_size = self._writer.save(
            test_rows,
            params.test_output_path,
            params.korean_headers,
        )

        return PrepareDatasetResult(
            source_path=params.source_path,
            train_output_path=params.train_output_path,
            test_output_path=params.test_output_path,
            total_rows=len(rows),
            removed_rows=removed,
            train_rows=len(train_rows),
            test_rows=len(test_rows),
            train_file_size_bytes=train_size,
            test_file_size_bytes=test_size,
        )
