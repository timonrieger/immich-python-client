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
