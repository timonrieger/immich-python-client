import pytest
from typer.testing import CliRunner
from immich.cli.app import app as cli_app


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "subcommand",
    [
        # Exclude license mutation/check endpoints to keep the test suite idempotent.
        # The goal is to validate the standard public ServerApi surface end-to-end.
        "get-about-info",
        "get-apk-links",
        "get-server-config",
        "get-server-features",
        "get-server-statistics",
        "get-server-version",
        "get-storage",
        "get-supported-media-types",
        "get-theme",
        "get-version-check",
        "get-version-history",
        "ping-server",
    ],
)
async def test_server_cli_standard_commands_smoke(
    runner: CliRunner,
    subcommand: str,
) -> None:
    """Smoke test each safe server subcommand via the real Typer CLI."""
    result = runner.invoke(
        cli_app,
        ["--format", "json", "server", subcommand],
    )
    assert result.exit_code == 0, result.stdout + result.stderr
