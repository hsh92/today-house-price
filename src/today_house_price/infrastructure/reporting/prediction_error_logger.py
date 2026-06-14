"""예측 오류 행 CSV 로그."""

from __future__ import annotations

import csv
from pathlib import Path

from today_house_price.application.housing.dto.predict_price import SkippedPredictionItem

ERROR_LOG_COLUMNS = (
    "ROW_NUMBER",
    "CGG_NM",
    "BLDG_USG",
    "ARCH_AREA",
    "ARCH_YR",
    "FLR",
    "CTRT_DAY",
    "ERROR_REASON",
)


class PredictionErrorLogger:
    def save(self, output_path: str, skipped: tuple[SkippedPredictionItem, ...]) -> None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8-sig", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=list(ERROR_LOG_COLUMNS))
            writer.writeheader()
            for item in skipped:
                writer.writerow(
                    {
                        "ROW_NUMBER": item.row_number,
                        "CGG_NM": item.input_row.get("CGG_NM", ""),
                        "BLDG_USG": item.input_row.get("BLDG_USG", ""),
                        "ARCH_AREA": item.input_row.get("ARCH_AREA", ""),
                        "ARCH_YR": item.input_row.get("ARCH_YR", ""),
                        "FLR": item.input_row.get("FLR", ""),
                        "CTRT_DAY": item.input_row.get("CTRT_DAY", ""),
                        "ERROR_REASON": item.reason,
                    }
                )
