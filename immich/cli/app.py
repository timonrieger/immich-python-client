"""Main CLI entrypoint."""

from __future__ import annotations

import sys

try:
    import typer
    from rich.console import Console
except ImportError:
    print(
        "Error: CLI dependencies not installed. Install with: pip install immich[cli]",
        file=sys.stderr,
    )
    sys.exit(1)

from immich.cli.config import create_client

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
    help=(
        "Immich CLI (unofficial).\n\n"
        "Install: pip install immich[cli]\n"
        "Auth/config via env: IMMICH_BASE_URL + one of IMMICH_API_KEY / "
        "IMMICH_BEARER_TOKEN / IMMICH_COOKIE.\n"
        "Request bodies: --json JSON. Responses: JSON."
    ),
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


@app.callback(invoke_without_command=True)
def _callback(
    ctx: typer.Context,
    debug: bool = typer.Option(False, "--debug", help="Enable debug output"),
    format_mode: str = typer.Option(
        "pretty", "--format", help="Output format: json or pretty"
    ),
) -> None:
    """Immich API CLI."""
    # Store config in context
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug
    ctx.obj["format"] = format_mode

    # If help/completion parsing (root or subcommand), don't require config.
    if any(
        a in sys.argv
        for a in ("-h", "--help", "--install-completion", "--show-completion")
    ):
        return

    # If no command provided, show help without requiring config.
    if getattr(ctx, "resilient_parsing", False) or ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        raise typer.Exit(0)

    # Create client only when a command is actually invoked.
    try:
        ctx.obj["client"] = create_client()
    except ValueError as e:
        stderr_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None


def main() -> None:
    """Entry point for console script."""
    app()
