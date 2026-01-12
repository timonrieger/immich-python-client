"""CLI wrapper commands for DownloadApiWrapped convenience methods."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import typer

from immich.cli.commands import download as download_commands
from immich.cli.runtime import deserialize_request_body, handle_api_error, print_response, run_async, set_nested
from immich.client.exceptions import ApiException

# Reuse the existing app from the generated commands
app = download_commands.app


@app.command("download-archive-to-file")
def download_archive_to_file(
    ctx: typer.Context,
    out_dir: Path = typer.Argument(..., help="Output directory for the downloaded ZIP archives"),
    key: str | None = typer.Option(
        None, "--key", help="Public share key (last path segment of /share/<key>)"
    ),
    slug: str | None = typer.Option(
        None, "--slug", help="Public share slug (last path segment of /s/<slug>)"
    ),
    show_progress: bool = typer.Option(
        True, "--show-progress/--no-show-progress", help="Show progress bars (per-archive bytes + overall archive count)"
    ),
    json_str: str | None = typer.Option(
        None, "--json", help="Inline JSON request body for DownloadInfoDto"
    ),
    album_id: str | None = typer.Option(
        None, "--albumId", help="Album ID to download"
    ),
    archive_size: int | None = typer.Option(
        None, "--archiveSize", help="Archive size limit in bytes"
    ),
    asset_ids: list[str] | None = typer.Option(
        None, "--assetIds", help="Asset IDs to download"
    ),
    user_id: str | None = typer.Option(
        None, "--userId", help="User ID to download assets from"
    ),
) -> None:
    """Download one or more asset archives and save them to ZIP files.

    Downloads archives sequentially (not in parallel) to avoid overloading the server.
    The download_info parameter can be provided via --json or using dotted flags.
    """
    client = ctx.obj["client"]
    api_group = client.download

    # Build DownloadInfoDto from --json or dotted flags (same pattern as get-download-info)
    has_json = json_str is not None
    has_flags = any([album_id, archive_size, asset_ids, user_id])
    
    if has_json and has_flags:
        raise SystemExit(
            "Error: Cannot use both --json and dotted body flags together. Use one or the other."
        )
    if not has_json and not has_flags:
        raise SystemExit(
            "Error: Request body is required. Provide --json or use dotted body flags."
        )
    
    if json_str is not None:
        json_data = json.loads(json_str)
        from immich.client.models.download_info_dto import DownloadInfoDto
        download_info = deserialize_request_body(json_data, DownloadInfoDto)
    elif has_flags:
        json_data = {}
        if album_id is not None:
            set_nested(json_data, ["albumId"], album_id)
        if archive_size is not None:
            set_nested(json_data, ["archiveSize"], archive_size)
        if asset_ids is not None:
            set_nested(json_data, ["assetIds"], asset_ids)
        if user_id is not None:
            set_nested(json_data, ["userId"], user_id)
        if json_data:
            from immich.client.models.download_info_dto import DownloadInfoDto
            download_info = deserialize_request_body(json_data, DownloadInfoDto)
        else:
            raise SystemExit("Error: At least one field must be provided for download_info")

    async def _call_and_close() -> list[Path]:
        try:
            return await api_group.download_archive_to_file(
                download_info=download_info,
                out_dir=out_dir,
                key=key,
                slug=slug,
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
    print_response({"paths": [str(p) for p in result]}, format_mode)
