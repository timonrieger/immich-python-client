"""CLI wrapper commands for UsersApiWrapped convenience methods."""

from __future__ import annotations

import asyncio
from pathlib import Path
from uuid import UUID

import typer

from immich.cli.commands import users as users_commands
from immich.cli.runtime import handle_api_error, print_response, run_async
from immich.client.exceptions import ApiException

# Reuse the existing app from the generated commands
app = users_commands.app


@app.command("get-profile-image-to-file")
def get_profile_image_to_file(
    ctx: typer.Context,
    id: str = typer.Argument(..., help="User ID (UUID)"),
    out_dir: Path = typer.Argument(..., help="Output directory for the profile image file"),
    filename: str | None = typer.Option(
        None, "--filename", help="Filename to use (defaults to original filename or profile-{user_id})"
    ),
    show_progress: bool = typer.Option(
        True, "--show-progress/--no-show-progress", help="Show progress bar while downloading"
    ),
) -> None:
    """Download a user's profile image and save it to a file.

    Downloads the profile image for the specified user and saves it to the specified output directory.
    The filename can be specified or will be derived from the response headers.
    """
    client = ctx.obj["client"]
    api_group = client.users

    async def _call_and_close() -> Path:
        try:
            return await api_group.get_profile_image_to_file(
                id=UUID(id),
                out_dir=out_dir,
                filename=filename,
                show_progress=show_progress,
            )
        finally:
            await client.close()

    try:
        result = asyncio.run(run_async(_call_and_close()))
    except Exception as e:
        if isinstance(e, ApiException):
            handle_api_error(e)
        raise

    format_mode = ctx.obj.get("format", "pretty")
    print_response({"path": str(result)}, format_mode)
