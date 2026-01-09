"""Main CLI entrypoint."""

from __future__ import annotations

import sys

try:
    import typer
    from rich.console import Console
except ImportError:
    # Stub behavior when CLI deps not installed
    print(
        "Error: CLI dependencies not installed. Install with: pip install immich[cli]",
        file=sys.stderr,
    )
    sys.exit(1)

from immich.cli.config import create_client

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

# Track if apps have been attached to avoid re-attaching
_apps_attached = False


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


def attach_generated_apps() -> None:
    """Attach generated sub-apps to the root app."""
    global _apps_attached
    if _apps_attached:
        return
    
    try:
        from immich.cli.commands import APPS

        for tag_name, sub_app in APPS.items():
            if sub_app is not None:
                app.add_typer(sub_app, name=tag_name)
        _apps_attached = True
    except (ImportError, AttributeError):
        # Generated code not available - this is expected before first codegen run
        pass


def main() -> None:
    """Entry point for console script."""
    # Attach generated apps lazily (only when CLI is invoked, not at import time)
    # This speeds up module imports while still allowing completion to work
    # Must be called before app() so Typer can introspect commands for help/completion
    attach_generated_apps()
    app()
