from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from typer.testing import CliRunner

from immich import AsyncClient
from immich.cli.consts import (
    DEFAULT_FORMAT,
    DEFAULT_PROFILE,
    IMMICH_ACCESS_TOKEN,
    IMMICH_API_URL,
    IMMICH_API_KEY,
    IMMICH_FORMAT,
    IMMICH_PROFILE,
)


@pytest.fixture
def runner(client_with_api_key: AsyncClient) -> CliRunner:
    """Typer CliRunner fixture for CLI testing."""
    return CliRunner(
        env={
            IMMICH_API_URL: client_with_api_key.base_client.configuration.host,
            IMMICH_API_KEY: client_with_api_key.base_client.configuration.api_key[
                "api_key"
            ],
            IMMICH_FORMAT: DEFAULT_FORMAT,
            IMMICH_PROFILE: DEFAULT_PROFILE,
        }
    )


@pytest.fixture
def runner_with_access_token(client_with_access_token: AsyncClient) -> CliRunner:
    """Fixture to create a runner with an access token."""
    return CliRunner(
        env={
            IMMICH_API_URL: client_with_access_token.base_client.configuration.host,
            IMMICH_ACCESS_TOKEN: client_with_access_token.base_client.configuration.access_token,
            IMMICH_FORMAT: DEFAULT_FORMAT,
            IMMICH_PROFILE: DEFAULT_PROFILE,
        }
    )


@pytest.fixture
def runner_simple() -> CliRunner:
    """Simple Typer CliRunner fixture for CLI testing without client setup."""
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


@pytest.fixture
def mock_api_calls():
    """Fixture that intercepts API calls by mocking AsyncClient and run_command."""

    def mock_run_command(*args, **kwargs):
        return {}

    with (
        patch("immich.cli.main.AsyncClient") as mock_client,
        patch("immich.cli.runtime.run_command", side_effect=mock_run_command),
    ):
        mock_client_instance = MagicMock()
        mock_client_instance.server = MagicMock()
        mock_client_instance.server.get_about_info = AsyncMock(return_value={})
        mock_client_instance.close = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance
        yield mock_client
