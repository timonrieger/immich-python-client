import json

import pytest
from typer.testing import CliRunner

from immich.cli.app import app as cli_app
from immich.client import (
    APIKeyCreateResponseDto,
    APIKeyResponseDto,
)
from immich.client.models.permission import Permission


@pytest.mark.e2e
def test_create_api_key(runner: CliRunner) -> None:
    """Test create-api-key command and validate response structure."""
    api_key_name = "Test API Key"
    result = runner.invoke(
        cli_app,
        [
            "--format",
            "json",
            "api-keys",
            "create-api-key",
            "--name",
            api_key_name,
            "--permissions",
            "all",
        ],
    )
    assert result.exit_code == 0, result.stdout + result.stderr
    response_data = json.loads(result.output)
    api_key_response = APIKeyCreateResponseDto.model_validate(response_data)
    assert api_key_response.api_key.name == api_key_name
    assert Permission.ALL in api_key_response.api_key.permissions
    assert api_key_response.secret is not None


@pytest.mark.e2e
def test_get_api_keys(runner: CliRunner, api_key: APIKeyResponseDto) -> None:
    """Test get-api-keys command and validate response structure."""
    api_key_id = api_key.id
    result = runner.invoke(
        cli_app,
        ["--format", "json", "api-keys", "get-api-keys"],
    )
    assert result.exit_code == 0, result.stdout + result.stderr
    response_data = json.loads(result.output)
    assert isinstance(response_data, list)
    api_keys: list[APIKeyResponseDto] = []
    for item in response_data:
        api_key = APIKeyResponseDto.model_validate(item)
        api_keys.append(api_key)
    assert any(api_key.id == api_key_id for api_key in api_keys)


@pytest.mark.e2e
def test_get_api_key(runner: CliRunner, api_key: APIKeyResponseDto) -> None:
    """Test get-api-key command and validate response structure."""
    api_key_id = api_key.id
    result = runner.invoke(
        cli_app,
        [
            "--format",
            "json",
            "api-keys",
            "get-api-key",
            api_key_id,
        ],
    )
    assert result.exit_code == 0, result.stdout + result.stderr
    response_data = json.loads(result.output)
    api_key_info = APIKeyResponseDto.model_validate(response_data)
    assert api_key_info.id == api_key_id


@pytest.mark.e2e
def test_get_my_api_key(runner: CliRunner) -> None:
    """Test get-my-api-key command and validate response structure."""
    result = runner.invoke(
        cli_app,
        ["--format", "json", "api-keys", "get-my-api-key"],
    )
    assert result.exit_code == 0, result.stdout + result.stderr
    response_data = json.loads(result.output)
    APIKeyResponseDto.model_validate(response_data)


@pytest.mark.e2e
def test_update_api_key(runner: CliRunner, api_key: APIKeyResponseDto) -> None:
    """Test update-api-key command and validate response structure."""
    api_key_id = api_key.id
    updated_name = "Updated API Key Name"
    result = runner.invoke(
        cli_app,
        [
            "--format",
            "json",
            "api-keys",
            "update-api-key",
            api_key_id,
            "--name",
            updated_name,
            "--permissions",
            "asset.read",
        ],
    )
    assert result.exit_code == 0, result.stdout + result.stderr
    response_data = json.loads(result.output)
    updated_api_key = APIKeyResponseDto.model_validate(response_data)
    assert updated_api_key.id == api_key_id
    assert updated_api_key.name == updated_name
    assert Permission.ASSET_DOT_READ in updated_api_key.permissions


@pytest.mark.e2e
@pytest.mark.parametrize("teardown", [False])
def test_delete_api_key(runner: CliRunner, api_key: APIKeyResponseDto) -> None:
    """Test delete-api-key command and validate response structure."""
    api_key_id = api_key.id
    result = runner.invoke(
        cli_app,
        ["--format", "json", "api-keys", "delete-api-key", api_key_id],
    )
    assert result.exit_code == 0, result.stdout + result.stderr
    # Delete returns 204, so response should be None or empty
    if result.output.strip():
        response_data = json.loads(result.output)
        assert response_data is None
