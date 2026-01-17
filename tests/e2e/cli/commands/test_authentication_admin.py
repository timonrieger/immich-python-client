import json
import pytest
from typer.testing import CliRunner

from immich.cli.app import app as cli_app


@pytest.mark.e2e
def test_unlink_all_o_auth_accounts_admin(runner: CliRunner) -> None:
    """Test unlink-all-o-auth-accounts-admin command and validate response structure."""
    result = runner.invoke(
        cli_app,
        [
            "--format",
            "json",
            "authentication-admin",
            "unlink-all-o-auth-accounts-admin",
        ],
    )
    assert result.exit_code == 0, result.stdout + result.stderr
    response_data = json.loads(result.stdout)
    assert response_data is None
