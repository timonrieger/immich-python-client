import pytest
from typer.testing import CliRunner

from immich import AsyncClient
from immich.cli.consts import (
    DEFAULT_FORMAT,
    DEFAULT_PROFILE,
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
def runner_simple() -> CliRunner:
    """Simple Typer CliRunner fixture for CLI testing without client setup."""
    return CliRunner(
        env={IMMICH_FORMAT: DEFAULT_FORMAT, IMMICH_PROFILE: DEFAULT_PROFILE}
    )
