"""Flask 웹 설정."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]


@dataclass(frozen=True)
class WebConfig:
    secret_key: str
    model_path: Path
    upload_folder: Path
    max_upload_mb: int = 32

    @classmethod
    def from_env(cls) -> WebConfig:
        model = os.environ.get(
            "MODEL_PATH",
            str(PROJECT_ROOT / "data" / "models" / "price_linear_regression.joblib"),
        )
        upload = os.environ.get("WEB_UPLOAD_FOLDER", str(PROJECT_ROOT / "data" / "web_uploads"))
        secret = os.environ.get("FLASK_SECRET_KEY", "dev-only-change-in-production")
        max_mb = int(os.environ.get("WEB_MAX_UPLOAD_MB", "32"))
        return cls(
            secret_key=secret,
            model_path=_resolve_model_path(Path(model)),
            upload_folder=Path(upload),
            max_upload_mb=max_mb,
        )


def _resolve_model_path(path: Path) -> Path:
    if path.is_file():
        return path.resolve()
    candidate = (PROJECT_ROOT / path).resolve()
    if candidate.is_file():
        return candidate
    return path.resolve()
