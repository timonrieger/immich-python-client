"""Main CLI entrypoint."""

from __future__ import annotations

import sys
from typing import Optional
from importlib.metadata import version

from immich._internal.consts import API_KEY_URL, DEMO_BASE_URL

try:
    import typer
    from rich.console import Console
except ImportError:
    print(
        "Error: CLI dependencies not installed. Install with: pip install immich[cli]",
        file=sys.stderr,
    )
    sys.exit(1)

from immich import AsyncClient
from immich._internal.types import _FormatMode

# Import command modules
from immich.cli.commands import api_keys as api_keys_commands
from immich.cli.commands import activities as activities_commands
from immich.cli.commands import albums as albums_commands
from immich.cli_wrapper.commands import assets as assets_wrapper
from immich.cli.commands import authentication as authentication_commands
from immich.cli.commands import authentication_admin as authentication_admin_commands
from immich.cli_wrapper.commands import download as download_wrapper
from immich.cli.commands import duplicates as duplicates_commands
from immich.cli.commands import faces as faces_commands
from immich.cli.commands import jobs as jobs_commands
from immich.cli.commands import libraries as libraries_commands
from immich.cli.commands import maintenance_admin as maintenance_admin_commands
from immich.cli.commands import map as map_commands
from immich.cli.commands import memories as memories_commands
from immich.cli.commands import notifications as notifications_commands
from immich.cli.commands import notifications_admin as notifications_admin_commands
from immich.cli.commands import partners as partners_commands
from immich.cli.commands import people as people_commands
from immich.cli.commands import plugins as plugins_commands
from immich.cli.commands import queues as queues_commands
from immich.cli.commands import search as search_commands
from immich.cli.commands import server as server_commands
from immich.cli.commands import sessions as sessions_commands
from immich.cli.commands import shared_links as shared_links_commands
from immich.cli.commands import stacks as stacks_commands
from immich.cli.commands import sync as sync_commands
from immich.cli.commands import system_config as system_config_commands
from immich.cli.commands import system_metadata as system_metadata_commands
from immich.cli.commands import tags as tags_commands
from immich.cli.commands import timeline as timeline_commands
from immich.cli.commands import trash as trash_commands
from immich.cli_wrapper.commands import users as users_wrapper
from immich.cli.commands import users_admin as users_admin_commands
from immich.cli.commands import views as views_commands
from immich.cli.commands import workflows as workflows_commands

# Global state
app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
)
console = Console()
stderr_console = Console(file=sys.stderr)

# Add command modules to the main app
app.add_typer(api_keys_commands.app, name="api-keys")
app.add_typer(activities_commands.app, name="activities")
app.add_typer(albums_commands.app, name="albums")
app.add_typer(assets_wrapper.app, name="assets")
app.add_typer(authentication_commands.app, name="authentication")
app.add_typer(authentication_admin_commands.app, name="authentication-admin")
app.add_typer(download_wrapper.app, name="download")
app.add_typer(duplicates_commands.app, name="duplicates")
app.add_typer(faces_commands.app, name="faces")
app.add_typer(jobs_commands.app, name="jobs")
app.add_typer(libraries_commands.app, name="libraries")
app.add_typer(maintenance_admin_commands.app, name="maintenance-admin")
app.add_typer(map_commands.app, name="map")
app.add_typer(memories_commands.app, name="memories")
app.add_typer(notifications_commands.app, name="notifications")
app.add_typer(notifications_admin_commands.app, name="notifications-admin")
app.add_typer(partners_commands.app, name="partners")
app.add_typer(people_commands.app, name="people")
app.add_typer(plugins_commands.app, name="plugins")
app.add_typer(queues_commands.app, name="queues")
app.add_typer(search_commands.app, name="search")
app.add_typer(server_commands.app, name="server")
app.add_typer(sessions_commands.app, name="sessions")
app.add_typer(shared_links_commands.app, name="shared-links")
app.add_typer(stacks_commands.app, name="stacks")
app.add_typer(sync_commands.app, name="sync")
app.add_typer(system_config_commands.app, name="system-config")
app.add_typer(system_metadata_commands.app, name="system-metadata")
app.add_typer(tags_commands.app, name="tags")
app.add_typer(timeline_commands.app, name="timeline")
app.add_typer(trash_commands.app, name="trash")
app.add_typer(users_wrapper.app, name="users")
app.add_typer(users_admin_commands.app, name="users-admin")
app.add_typer(views_commands.app, name="views")
app.add_typer(workflows_commands.app, name="workflows")


def version_callback(value: bool) -> None:
    if value:
        print(f"immich CLI (unofficial) {version('immich')}")
        raise typer.Exit(0)


@app.callback(invoke_without_command=False)
def _callback(
    ctx: typer.Context,
    format_mode: _FormatMode = typer.Option(
        "pretty", "--format", help="Output format of the CLI.", envvar="IMMICH_FORMAT"
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        help=f"Authorize via API key (see {API_KEY_URL}).",
        envvar="IMMICH_API_KEY",
    ),
    access_token: Optional[str] = typer.Option(
        None,
        "--access-token",
        help="Authorize via access token.",
        envvar="IMMICH_ACCESS_TOKEN",
    ),
    base_url: str = typer.Option(
        DEMO_BASE_URL,
        "--base-url",
        help="The server to connect to.",
        envvar="IMMICH_API_URL",
        show_default=DEMO_BASE_URL.replace("https://", ""),
    ),
    _version: bool = typer.Option(
        False,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """An unofficial CLI for the Immich API written in Python."""
    ctx.ensure_object(dict)
    ctx.obj["format"] = format_mode
    ctx.obj["client"] = AsyncClient(
        api_key=api_key,
        bearer_token=access_token,
        base_url=DEMO_BASE_URL if base_url == "demo" else base_url,
    )


if __name__ == "__main__":
    app()
