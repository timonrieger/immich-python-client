import pytest
from typer.testing import CliRunner

from immich import AsyncClient


@pytest.fixture
def runner(client_with_api_key: AsyncClient) -> CliRunner:
    """Typer CliRunner fixture for CLI testing."""
    return CliRunner(
        env={
            "IMMICH_API_URL": client_with_api_key.base_client.configuration.host,
            "IMMICH_API_KEY": client_with_api_key.base_client.configuration.api_key[
                "api_key"
            ],
        }
    )
