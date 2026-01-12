"""CLI wrapper commands for AssetsApiWrapped convenience methods."""

from __future__ import annotations

import asyncio
from pathlib import Path
from uuid import UUID

import typer

from immich.cli.commands import assets as assets_commands
from immich.cli.runtime import handle_api_error, print_response, run_async
from immich.client.exceptions import ApiException
from immich.client.models.asset_media_size import AssetMediaSize

# Reuse the existing app from the generated commands
app = assets_commands.app


@app.command("download-asset-to-file")
def download_asset_to_file(
    ctx: typer.Context,
    id: str = typer.Argument(..., help="Asset ID (UUID)"),
    out_dir: Path = typer.Argument(..., help="Output directory for the downloaded file"),
    key: str | None = typer.Option(
        None, "--key", help="Public share key (last path segment of /share/<key>)"
    ),
    slug: str | None = typer.Option(
        None, "--slug", help="Public share slug (last path segment of /s/<slug>)"
    ),
    filename: str | None = typer.Option(
        None, "--filename", help="Filename to use (defaults to original filename or orig-{asset_id})"
    ),
    show_progress: bool = typer.Option(
        True, "--show-progress/--no-show-progress", help="Show progress bar while downloading"
    ),
) -> None:
    """Download an asset to a file.

    Downloads the original asset file and saves it to the specified output directory.
    The filename can be specified or will be derived from the response headers.
    """
    client = ctx.obj["client"]
    api_group = client.assets

    async def _call_and_close() -> Path:
        try:
            return await api_group.download_asset_to_file(
                id=UUID(id),
                out_dir=out_dir,
                key=key,
                slug=slug,
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


@app.command("play-asset-video-to-file")
def play_asset_video_to_file(
    ctx: typer.Context,
    id: str = typer.Argument(..., help="Asset ID (UUID)"),
    out_dir: Path = typer.Argument(..., help="Output directory for the video file"),
    key: str | None = typer.Option(
        None, "--key", help="Public share key (last path segment of /share/<key>)"
    ),
    slug: str | None = typer.Option(
        None, "--slug", help="Public share slug (last path segment of /s/<slug>)"
    ),
    filename: str | None = typer.Option(
        None, "--filename", help="Filename to use (defaults to original filename or video-{asset_id})"
    ),
    show_progress: bool = typer.Option(
        True, "--show-progress/--no-show-progress", help="Show progress bar while downloading"
    ),
) -> None:
    """Save an asset's video stream to a file.

    Downloads the video stream for the asset and saves it to the specified output directory.
    The filename can be specified or will be derived from the response headers.
    """
    client = ctx.obj["client"]
    api_group = client.assets

    async def _call_and_close() -> Path:
        try:
            return await api_group.play_asset_video_to_file(
                id=UUID(id),
                out_dir=out_dir,
                key=key,
                slug=slug,
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


@app.command("view-asset-to-file")
def view_asset_to_file(
    ctx: typer.Context,
    id: str = typer.Argument(..., help="Asset ID (UUID)"),
    out_dir: Path = typer.Argument(..., help="Output directory for the thumbnail file"),
    key: str | None = typer.Option(
        None, "--key", help="Public share key (last path segment of /share/<key>)"
    ),
    slug: str | None = typer.Option(
        None, "--slug", help="Public share slug (last path segment of /s/<slug>)"
    ),
    size: str | None = typer.Option(
        None, "--size", help="Thumbnail size: fullsize, preview, or thumbnail"
    ),
    filename: str | None = typer.Option(
        None, "--filename", help="Filename to use (defaults to original filename or thumb-{asset_id})"
    ),
    show_progress: bool = typer.Option(
        True, "--show-progress/--no-show-progress", help="Show progress bar while downloading"
    ),
) -> None:
    """Save an asset's thumbnail to a file.

    Downloads the thumbnail for the asset and saves it to the specified output directory.
    The filename can be specified or will be derived from the response headers.
    """
    client = ctx.obj["client"]
    api_group = client.assets

    size_enum: AssetMediaSize | None = None
    if size is not None:
        try:
            size_enum = AssetMediaSize(size)
        except ValueError:
            raise typer.BadParameter(
                f"Invalid size '{size}'. Must be one of: fullsize, preview, thumbnail"
            )

    async def _call_and_close() -> Path:
        try:
            return await api_group.view_asset_to_file(
                id=UUID(id),
                out_dir=out_dir,
                key=key,
                slug=slug,
                size=size_enum,
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


@app.command("upload")
def upload(
    ctx: typer.Context,
    paths: list[Path] = typer.Argument(..., help="File or directory paths to upload (can specify multiple)"),
    ignore_pattern: str | None = typer.Option(
        None, "--ignore-pattern", help="Wildcard pattern to ignore files (uses fnmatch, not regex)"
    ),
    include_hidden: bool = typer.Option(
        False, "--include-hidden/--no-include-hidden", help="Include hidden files (starting with '.')"
    ),
    check_duplicates: bool = typer.Option(
        True, "--check-duplicates/--no-check-duplicates", help="Check for duplicates using SHA1 hashes before uploading"
    ),
    concurrency: int = typer.Option(
        5, "--concurrency", help="Number of concurrent uploads (default: 5)"
    ),
    show_progress: bool = typer.Option(
        True, "--show-progress/--no-show-progress", help="Show progress bars"
    ),
    include_sidecars: bool = typer.Option(
        True, "--include-sidecars/--no-include-sidecars", help="Automatically detect and upload XMP sidecar files"
    ),
    album_name: str | None = typer.Option(
        None, "--album-name", help="Album name to create or use (if not provided, no album operations are performed)"
    ),
    delete_after_upload: bool = typer.Option(
        False, "--delete-after-upload/--no-delete-after-upload", help="Delete successfully uploaded files locally"
    ),
    delete_duplicates: bool = typer.Option(
        False, "--delete-duplicates/--no-delete-duplicates", help="Delete duplicate files locally"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run/--no-dry-run", help="Simulate uploads without actually uploading"
    ),
) -> None:
    """Upload assets with smart features.

    Uploads files or directories with duplicate detection, album management, sidecar support, and dry run capability.
    Directories are automatically walked recursively.
    """
    if concurrency < 1:
        raise typer.BadParameter("concurrency must be >= 1")

    client = ctx.obj["client"]
    api_group = client.assets

    async def _call_and_close():
        try:
            return await api_group.upload(
                paths=paths,
                ignore_pattern=ignore_pattern,
                include_hidden=include_hidden,
                check_duplicates=check_duplicates,
                concurrency=concurrency,
                show_progress=show_progress,
                include_sidecars=include_sidecars,
                album_name=album_name,
                delete_after_upload=delete_after_upload,
                delete_duplicates=delete_duplicates,
                dry_run=dry_run,
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
    print_response(result, format_mode)
