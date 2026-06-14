"""환경 변수 로드."""

from __future__ import annotations

import os
from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parents[4]


def _read_env_file(env_path: Path) -> None:
    for line in env_path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def _search_roots(start: Path) -> list[Path]:
    roots: list[Path] = []
    resolved = start.resolve()
    for directory in [resolved, *resolved.parents]:
        roots.append(directory)
        if (directory / "pyproject.toml").is_file():
            break
    return roots


def _candidate_env_paths(start: Path | None = None) -> list[Path]:
    candidates: list[Path] = []
    seen_env: set[Path] = set()

    search_starts = [start or Path.cwd()]
    if _PACKAGE_ROOT not in search_starts:
        search_starts.append(_PACKAGE_ROOT)

    for search_start in search_starts:
        for directory in _search_roots(search_start):
            env_path = (directory / ".env").resolve()
            if env_path in seen_env:
                continue
            seen_env.add(env_path)
            candidates.append(env_path)

    return candidates


def load_dotenv(path: Path | None = None) -> Path | None:
    """`.env` 파일을 로드한다. 찾은 경로를 반환하고 없으면 None."""
    paths = [path.resolve()] if path else _candidate_env_paths()

    for env_path in paths:
        if env_path.is_file():
            _read_env_file(env_path)
            return env_path

    return None


def get_api_key(explicit_key: str = "") -> str:
    return explicit_key or os.environ.get("SEOUL_OPEN_API_KEY", "")
