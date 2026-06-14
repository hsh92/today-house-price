"""CSV 읽기 Adapter."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from today_house_price.domain.housing.fields import CSV_COLUMNS, KOREAN_HEADERS

KOREAN_TO_KEY = {label: key for key, label in KOREAN_HEADERS.items()}


def normalize_header(header: str) -> str:
    stripped = header.strip()
    if stripped in CSV_COLUMNS:
        return stripped
    if stripped in KOREAN_TO_KEY:
        return KOREAN_TO_KEY[stripped]
    return stripped


class CsvTransactionReader:
    def load(self, source_path: str) -> list[dict[str, Any]]:
        path = Path(source_path)
        if not path.is_file():
            raise FileNotFoundError(f"입력 파일을 찾을 수 없습니다: {path.resolve()}")

        with path.open(encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames is None:
                return []

            rows: list[dict[str, Any]] = []
            for raw_row in reader:
                normalized: dict[str, Any] = {column: "" for column in CSV_COLUMNS}
                for original_name, value in raw_row.items():
                    if original_name is None:
                        continue
                    key = normalize_header(original_name)
                    if key in CSV_COLUMNS:
                        normalized[key] = value if value is not None else ""
                rows.append(normalized)

        return rows
