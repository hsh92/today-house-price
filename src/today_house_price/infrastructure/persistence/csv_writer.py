"""CSV 저장 Adapter."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from today_house_price.domain.housing.fields import CSV_COLUMNS, KOREAN_HEADERS


class CsvTransactionWriter:
    def save(
        self,
        rows: list[dict[str, Any]],
        output_path: str,
        korean_headers: bool,
    ) -> int:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        headers = (
            [KOREAN_HEADERS[col] for col in CSV_COLUMNS] if korean_headers else list(CSV_COLUMNS)
        )

        with path.open("w", encoding="utf-8-sig", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            for row in rows:
                if korean_headers:
                    writer.writerow({KOREAN_HEADERS[col]: row[col] for col in CSV_COLUMNS})
                else:
                    writer.writerow(row)

        return path.stat().st_size
