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
        "Request bodies: --json PATH. Responses: JSON."
    ),
    context_settings={"help_option_names": ["-h", "--help"]},
)
console = Console()
stderr_console = Console(file=sys.stderr)


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
    try:
        from immich.cli.generated import APPS

        for tag_name, sub_app in APPS.items():
            if sub_app is not None:
                app.add_typer(sub_app, name=tag_name)
    except (ImportError, AttributeError):
        # Generated code not available - this is expected before first codegen run
        pass


# Attach generated apps when module is imported
attach_generated_apps()


def main() -> None:
    """Entry point for console script."""
    app()
