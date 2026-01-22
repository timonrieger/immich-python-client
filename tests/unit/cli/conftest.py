from pathlib import Path

from immich.cli.consts import (
    DEFAULT_FORMAT,
    DEFAULT_PROFILE,
    IMMICH_FORMAT,
    IMMICH_PROFILE,
)
import pytest
from typer.testing import CliRunner


@pytest.fixture
def runner() -> CliRunner:
    """Typer CliRunner fixture for CLI testing."""
    return CliRunner(
        env={IMMICH_FORMAT: DEFAULT_FORMAT, IMMICH_PROFILE: DEFAULT_PROFILE}
    )


@pytest.fixture
def mock_config_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Fixture that patches CONFIG_DIR and CONFIG_FILE to use tmp_path."""
    config_dir = tmp_path / ".immich-py"
    config_file = config_dir / "config.toml"

    monkeypatch.setattr("immich.cli.consts.CONFIG_DIR", config_dir)
    monkeypatch.setattr("immich.cli.consts.CONFIG_FILE", config_file)
    monkeypatch.setattr("immich.cli.utils.CONFIG_FILE", config_file)
    monkeypatch.setattr("immich.cli.wrapper.setup.CONFIG_FILE", config_file)
    monkeypatch.setattr("immich.cli.wrapper.config.CONFIG_FILE", config_file)

    return config_file
