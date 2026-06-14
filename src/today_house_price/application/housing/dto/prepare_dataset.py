"""Prepare dataset DTO."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PrepareDatasetInput:
    source_path: str
    train_output_path: str
    test_output_path: str
    train_ratio: float = 0.8
    seed: int = 42
    strict: bool = False
    korean_headers: bool = False


@dataclass(frozen=True)
class PrepareDatasetResult:
    source_path: str
    train_output_path: str
    test_output_path: str
    total_rows: int
    removed_rows: int
    train_rows: int
    test_rows: int
    train_file_size_bytes: int
    test_file_size_bytes: int
