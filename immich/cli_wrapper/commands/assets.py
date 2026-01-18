"""CLI wrapper commands for AssetsApiWrapped convenience methods."""

from __future__ import annotations

from pathlib import Path

import typer

from immich.cli.commands import assets as assets_commands
from immich.cli.runtime import print_response, run_command

# Reuse the existing app from the generated commands
app = assets_commands.app


@app.command("download-asset-to-file", rich_help_panel="Custom commands")
def download_asset_to_file(
    ctx: typer.Context,
    id: str = typer.Argument(..., help="Asset ID (UUID)"),
    out_dir: Path = typer.Argument(
        ..., help="Output directory for the downloaded file"
    ),
    key: str | None = typer.Option(
        None, "--key", help="Public share key (last path segment of /share/<key>)"
    ),
    slug: str | None = typer.Option(
        None, "--slug", help="Public share slug (last path segment of /s/<slug>)"
    ),
    filename: str | None = typer.Option(
        None,
        "--filename",
        help="Filename to use (defaults to original filename or orig-{asset_id})",
    ),
    show_progress: bool = typer.Option(
        True,
        "--show-progress",
        help="Show progress bar while downloading",
    ),
) -> None:
    """Download an asset to a file.

    Downloads the original asset file and saves it to the specified output directory.
    The filename can be specified or will be derived from the response headers.
    """
    kwargs = {}
    kwargs["id"] = id
    kwargs["out_dir"] = out_dir
    kwargs["show_progress"] = show_progress
    if key is not None:
        kwargs["key"] = key
    if slug is not None:
        kwargs["slug"] = slug
    if filename is not None:
        kwargs["filename"] = filename
    client = ctx.obj["client"]
    result = run_command(client, client.assets, "download_asset_to_file", **kwargs)
    print_response(result, ctx)


@app.command("play-asset-video-to-file", rich_help_panel="Custom commands")
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
        None,
        "--filename",
        help="Filename to use (defaults to original filename or video-{asset_id})",
    ),
    show_progress: bool = typer.Option(
        True,
        "--show-progress",
        help="Show progress bar while downloading",
    ),
) -> None:
    """Save an asset's video stream to a file.

    Downloads the video stream for the asset and saves it to the specified output directory.
    The filename can be specified or will be derived from the response headers.
    """
    kwargs = {}
    kwargs["id"] = id
    kwargs["out_dir"] = out_dir
    kwargs["show_progress"] = show_progress
    if key is not None:
        kwargs["key"] = key
    if slug is not None:
        kwargs["slug"] = slug
    if filename is not None:
        kwargs["filename"] = filename
    client = ctx.obj["client"]
    result = run_command(client, client.assets, "play_asset_video_to_file", **kwargs)
    print_response(result, ctx)


@app.command("view-asset-to-file", rich_help_panel="Custom commands")
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
        None,
        "--filename",
        help="Filename to use (defaults to original filename or thumb-{asset_id})",
    ),
    show_progress: bool = typer.Option(
        True,
        "--show-progress",
        help="Show progress bar while downloading",
    ),
) -> None:
    """Save an asset's thumbnail to a file.

    Downloads the thumbnail for the asset and saves it to the specified output directory.
    The filename can be specified or will be derived from the response headers.
    """
    kwargs = {}
    kwargs["id"] = id
    kwargs["out_dir"] = out_dir
    kwargs["show_progress"] = show_progress
    if key is not None:
        kwargs["key"] = key
    if slug is not None:
        kwargs["slug"] = slug
    if size is not None:
        kwargs["size"] = size
    if filename is not None:
        kwargs["filename"] = filename
    client = ctx.obj["client"]
    result = run_command(client, client.assets, "view_asset_to_file", **kwargs)
    print_response(result, ctx)


@app.command("upload", rich_help_panel="Custom commands")
def upload(
    ctx: typer.Context,
    paths: list[Path] = typer.Argument(
        ..., help="File or directory paths to upload (can specify multiple)"
    ),
    ignore_pattern: str | None = typer.Option(
        None,
        "--ignore-pattern",
        help="Wildcard pattern to ignore files (uses fnmatch, not regex)",
    ),
    include_hidden: bool = typer.Option(
        False,
        "--include-hidden/--exclude-hidden",
        help="Include hidden files (starting with '.')",
    ),
    check_duplicates: bool = typer.Option(
        True,
        "--check-duplicates/--skip-duplicates",
        help="Check for duplicates using SHA1 hashes before uploading",
    ),
    concurrency: int = typer.Option(
        5, "--concurrency", help="Number of concurrent uploads"
    ),
    show_progress: bool = typer.Option(
        True, "--show-progress", help="Show progress bars"
    ),
    include_sidecars: bool = typer.Option(
        True,
        "--include-sidecars/--exclude-sidecars",
        help="Automatically detect and upload XMP sidecar files",
    ),
    album_name: str | None = typer.Option(
        None,
        "--album-name",
        help="Album name to create or use (if not provided, no album operations are performed)",
    ),
    delete_uploads: bool = typer.Option(
        False,
        "--delete-uploads/--keep-uploads",
        help="Delete successfully uploaded files locally",
    ),
    delete_duplicates: bool = typer.Option(
        False,
        "--delete-duplicates/--keep-duplicates",
        help="Delete rejected duplicate files locally",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Simulate uploads without actually uploading",
    ),
) -> None:
    """Upload assets with smart features.

    Uploads files or directories with duplicate detection, album management, sidecar support, and dry run capability.
    Directories are automatically walked recursively.
    """
    kwargs = {}
    kwargs["paths"] = paths
    if ignore_pattern is not None:
        kwargs["ignore_pattern"] = ignore_pattern
    if include_hidden is not None:
        kwargs["include_hidden"] = include_hidden
    if check_duplicates is not None:
        kwargs["check_duplicates"] = check_duplicates
    if concurrency is not None:
        kwargs["concurrency"] = concurrency
    if show_progress is not None:
        kwargs["show_progress"] = show_progress
    if include_sidecars is not None:
        kwargs["include_sidecars"] = include_sidecars
    if album_name is not None:
        kwargs["album_name"] = album_name
    if delete_uploads is not None:
        kwargs["delete_uploads"] = delete_uploads
    if delete_duplicates is not None:
        kwargs["delete_duplicates"] = delete_duplicates
    if dry_run is not None:
        kwargs["dry_run"] = dry_run
    client = ctx.obj["client"]
    result = run_command(client, client.assets, "upload", **kwargs)
    print_response(result, ctx)
