"""Generated CLI commands for Activities tag (auto-generated, do not edit)."""

from __future__ import annotations

import typer

from immich.cli.runtime import (
    deserialize_request_body,
    print_response,
    run_command,
    set_nested,
)
from immich.client.models import *

app = typer.Typer(
    help="""An activity is a like or a comment made by a user on an asset or album.

Docs: https://api.immich.app/endpoints/activities""",
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.command("create-activity")
def create_activity(
    ctx: typer.Context,
    album_id: str = typer.Option(..., "--albumId", help="""Album ID"""),
    asset_id: str | None = typer.Option(
        None, "--assetId", help="""Asset ID (if activity is for an asset)"""
    ),
    comment: str | None = typer.Option(
        None, "--comment", help="""Comment text (required if type is comment)"""
    ),
    type: str = typer.Option(..., "--type", help="""Activity type (like or comment)"""),
) -> None:
    """Create an activity

    Docs: https://api.immich.app/endpoints/activities/createActivity
    """
    kwargs = {}
    has_flags = any([album_id, asset_id, comment, type])
    if not has_flags:
        raise SystemExit("Error: Request body is required. Use dotted body flags.")
    if any([album_id, asset_id, comment, type]):
        json_data = {}
        set_nested(json_data, ["albumId"], album_id)
        if asset_id is not None:
            set_nested(json_data, ["assetId"], asset_id)
        if comment is not None:
            set_nested(json_data, ["comment"], comment)
        set_nested(json_data, ["type"], type)
        from immich.client.models.activity_create_dto import ActivityCreateDto

        activity_create_dto = deserialize_request_body(json_data, ActivityCreateDto)
        kwargs["activity_create_dto"] = activity_create_dto
    client = ctx.obj["client"]
    result = run_command(client, client.activities, "create_activity", **kwargs)
    format_mode = ctx.obj.get("format", "pretty")
    print_response(result, format_mode)


@app.command("delete-activity")
def delete_activity(
    ctx: typer.Context,
    id: str,
) -> None:
    """Delete an activity

    Docs: https://api.immich.app/endpoints/activities/deleteActivity
    """
    kwargs = {}
    kwargs["id"] = id
    client = ctx.obj["client"]
    result = run_command(client, client.activities, "delete_activity", **kwargs)
    format_mode = ctx.obj.get("format", "pretty")
    print_response(result, format_mode)


@app.command("get-activities")
def get_activities(
    ctx: typer.Context,
    album_id: str = typer.Option(..., "--album-id", help="""Album ID"""),
    asset_id: str | None = typer.Option(
        None, "--asset-id", help="""Asset ID (if activity is for an asset)"""
    ),
    level: ReactionLevel | None = typer.Option(
        None, "--level", help="""Filter by activity level"""
    ),
    type: ReactionType | None = typer.Option(
        None, "--type", help="""Filter by activity type"""
    ),
    user_id: str | None = typer.Option(None, "--user-id", help="""Filter by user ID"""),
) -> None:
    """List all activities

    Docs: https://api.immich.app/endpoints/activities/getActivities
    """
    kwargs = {}
    kwargs["album_id"] = album_id
    if asset_id is not None:
        kwargs["asset_id"] = asset_id
    if level is not None:
        kwargs["level"] = level
    if type is not None:
        kwargs["type"] = type
    if user_id is not None:
        kwargs["user_id"] = user_id
    client = ctx.obj["client"]
    result = run_command(client, client.activities, "get_activities", **kwargs)
    format_mode = ctx.obj.get("format", "pretty")
    print_response(result, format_mode)


@app.command("get-activity-statistics")
def get_activity_statistics(
    ctx: typer.Context,
    album_id: str = typer.Option(..., "--album-id", help="""Album ID"""),
    asset_id: str | None = typer.Option(
        None, "--asset-id", help="""Asset ID (if activity is for an asset)"""
    ),
) -> None:
    """Retrieve activity statistics

    Docs: https://api.immich.app/endpoints/activities/getActivityStatistics
    """
    kwargs = {}
    kwargs["album_id"] = album_id
    if asset_id is not None:
        kwargs["asset_id"] = asset_id
    client = ctx.obj["client"]
    result = run_command(client, client.activities, "get_activity_statistics", **kwargs)
    format_mode = ctx.obj.get("format", "pretty")
    print_response(result, format_mode)
