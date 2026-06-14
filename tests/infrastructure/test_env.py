"""Environment loader tests."""

from __future__ import annotations

import os
from pathlib import Path

from today_house_price.infrastructure.config.env import get_api_key, load_dotenv


def test_load_dotenv_from_explicit_path(tmp_path: Path, monkeypatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("SEOUL_OPEN_API_KEY=from-file\n", encoding="utf-8")
    monkeypatch.delenv("SEOUL_OPEN_API_KEY", raising=False)

    load_dotenv(env_file)

    assert os.environ["SEOUL_OPEN_API_KEY"] == "from-file"


def test_load_dotenv_finds_project_root_from_subdirectory(
    tmp_path: Path, monkeypatch
) -> None:
    project_root = tmp_path / "project"
    scripts_dir = project_root / "scripts"
    scripts_dir.mkdir(parents=True)
    (project_root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    (project_root / ".env").write_text("SEOUL_OPEN_API_KEY=root-key\n", encoding="utf-8")
    monkeypatch.chdir(scripts_dir)
    monkeypatch.delenv("SEOUL_OPEN_API_KEY", raising=False)

    load_dotenv()

    assert os.environ["SEOUL_OPEN_API_KEY"] == "root-key"


def test_load_dotenv_does_not_override_existing_env(tmp_path: Path, monkeypatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("SEOUL_OPEN_API_KEY=file-key\n", encoding="utf-8")
    monkeypatch.setenv("SEOUL_OPEN_API_KEY", "existing-key")

    load_dotenv(env_file)

    assert os.environ["SEOUL_OPEN_API_KEY"] == "existing-key"


def test_get_api_key_prefers_explicit_value(monkeypatch) -> None:
    monkeypatch.setenv("SEOUL_OPEN_API_KEY", "env-key")

    assert get_api_key("cli-key") == "cli-key"
    assert get_api_key() == "env-key"
