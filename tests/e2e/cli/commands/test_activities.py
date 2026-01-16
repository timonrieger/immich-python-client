# """E2E tests for immich.cli.commands.activities."""

# from __future__ import annotations

# import os
# from pathlib import Path
# from uuid import UUID

# import pytest
# import typer

# from immich import AsyncClient
# from immich.client.exceptions import BadRequestException
# from immich.client.models.admin_onboarding_update_dto import AdminOnboardingUpdateDto
# from immich.client.models.api_key_create_dto import APIKeyCreateDto
# from immich.client.models.asset_bulk_delete_dto import AssetBulkDeleteDto
# from immich.client.models.login_credential_dto import LoginCredentialDto
# from immich.client.models.permission import Permission
# from immich.client.models.sign_up_dto import SignUpDto

# from immich.cli.commands.activities import (
#     create_activity,
#     delete_activity,
#     get_activities,
#     get_activity_statistics,
# )


# def _make_random_image() -> bytes:
#     """Generate a minimal JPEG image for testing."""
#     import io
#     from PIL import Image

#     img = Image.new("RGB", (1, 1), (128, 128, 128))
#     buffer = io.BytesIO()
#     img.save(buffer, format="JPEG", quality=95)
#     return buffer.getvalue()


# @pytest.fixture
# async def client_with_api_key():
#     """Set up admin user, create API key, and return authenticated client."""
#     base_url = os.environ.get("IMMICH_API_URL", "http://127.0.0.1:2283/api")

#     # Create unauthenticated client for setup
#     setup_client = AsyncClient(base_url=base_url)

#     try:
#         # Sign up admin (idempotent: subsequent tests will hit "already has an admin")
#         try:
#             await setup_client.authentication.sign_up_admin(
#                 SignUpDto(
#                     email="admin@immich.cloud", name="Immich Admin", password="password"
#                 )
#             )
#         except BadRequestException as e:
#             if not (e.status == 400 and e.body and "already has an admin" in e.body):
#                 raise

#         # Login to get access token
#         login_response = await setup_client.authentication.login(
#             LoginCredentialDto(email="admin@immich.cloud", password="password")
#         )

#         # Mark admin as onboarded
#         await setup_client.system_metadata.update_admin_onboarding(
#             # NOTE: type ignore likely a ty issue
#             AdminOnboardingUpdateDto(is_onboarded=True),  # type: ignore[missing-argument]
#             _headers={"Authorization": f"Bearer {login_response.access_token}"},
#         )

#         # Create API key with all permissions
#         api_key_response = await setup_client.api_keys.create_api_key(
#             APIKeyCreateDto(name="e2e", permissions=[Permission.ALL]),
#             _headers={"Authorization": f"Bearer {login_response.access_token}"},
#         )

#         # Create authenticated client with API key
#         client = AsyncClient(base_url=base_url, api_key=api_key_response.secret)

#         yield client

#         await client.close()
#     finally:
#         await setup_client.close()


# @pytest.fixture
# def test_image(tmp_path: Path) -> Path:
#     """Create a minimal JPEG test image."""
#     img_path = tmp_path / "test.jpg"
#     img_path.write_bytes(_make_random_image())
#     return img_path


# @pytest.fixture
# async def test_album(client_with_api_key: AsyncClient):
#     """Create a test album for activities."""
#     album = await client_with_api_key.albums.create_album(
#         name="Test Album for Activities"
#     )
#     yield album
#     # Cleanup
#     try:
#         await client_with_api_key.albums.delete_album(album.id)
#     except Exception:
#         pass


# @pytest.fixture
# async def test_asset(client_with_api_key: AsyncClient, test_image: Path):
#     """Create a test asset for activities."""
#     upload_result = await client_with_api_key.assets.upload(
#         [test_image], check_duplicates=False, show_progress=False
#     )
#     assert len(upload_result.uploaded) == 1
#     asset_id = UUID(upload_result.uploaded[0].asset.id)
#     yield asset_id
#     # Cleanup
#     try:
#         await client_with_api_key.assets.delete_assets(
#             AssetBulkDeleteDto(ids=[asset_id], force=True)
#         )
#     except Exception:
#         pass


# @pytest.fixture
# async def mock_ctx(client_with_api_key: AsyncClient):
#     """Create a mock typer.Context for CLI commands."""
#     ctx = typer.Context(typer.Typer())
#     ctx.ensure_object(dict)
#     ctx.obj["client"] = client_with_api_key
#     ctx.obj["format"] = "json"
#     return ctx


# @pytest.fixture
# async def activity_cleanup():
#     """Fixture to track created activities for cleanup."""
#     activity_ids: list[str] = []
#     yield activity_ids
#     # Cleanup handled in individual tests


# @pytest.mark.asyncio
# @pytest.mark.e2e
# async def test_create_activity_like(
#     mock_ctx: typer.Context,
#     test_album,
#     test_asset,
#     activity_cleanup: list[str],
# ):
#     """Test create-activity command with like type and all optional parameters."""
#     # Create a like activity with asset_id
#     create_activity(
#         ctx=mock_ctx,
#         album_id=str(test_album.id),
#         asset_id=str(test_asset),
#         type="like",
#     )

#     # Verify by getting activities
#     activities = await mock_ctx.obj["client"].activities.get_activities(
#         album_id=str(test_album.id)
#     )
#     assert len(activities) > 0
#     like_activity = next((a for a in activities if a.type == "like"), None)
#     assert like_activity is not None
#     assert like_activity.album_id == test_album.id
#     assert like_activity.asset_id == test_asset
#     activity_cleanup.append(like_activity.id)


# @pytest.mark.asyncio
# @pytest.mark.e2e
# async def test_create_activity_comment(
#     mock_ctx: typer.Context,
#     test_album,
#     test_asset,
#     activity_cleanup: list[str],
# ):
#     """Test create-activity command with comment type and comment text."""
#     # Create a comment activity with asset_id and comment text
#     create_activity(
#         ctx=mock_ctx,
#         album_id=str(test_album.id),
#         asset_id=str(test_asset),
#         comment="This is a test comment",
#         type="comment",
#     )

#     # Verify by getting activities
#     activities = await mock_ctx.obj["client"].activities.get_activities(
#         album_id=str(test_album.id)
#     )
#     assert len(activities) > 0
#     comment_activity = next((a for a in activities if a.type == "comment"), None)
#     assert comment_activity is not None
#     assert comment_activity.album_id == test_album.id
#     assert comment_activity.asset_id == test_asset
#     assert comment_activity.comment == "This is a test comment"
#     activity_cleanup.append(comment_activity.id)


# @pytest.mark.asyncio
# @pytest.mark.e2e
# async def test_delete_activity(
#     mock_ctx: typer.Context,
#     test_album,
#     test_asset,
# ):
#     """Test delete-activity command."""
#     # First create an activity
#     activity = await mock_ctx.obj["client"].activities.create_activity(
#         album_id=str(test_album.id),
#         asset_id=str(test_asset),
#         type="like",
#     )
#     activity_id = activity.id

#     # Delete the activity
#     delete_activity(ctx=mock_ctx, id=str(activity_id))

#     # Verify deletion by trying to get activities (should not include deleted one)
#     activities = await mock_ctx.obj["client"].activities.get_activities(
#         album_id=str(test_album.id)
#     )
#     assert not any(a.id == activity_id for a in activities)


# @pytest.mark.asyncio
# @pytest.mark.e2e
# async def test_get_activities_all_filters(
#     mock_ctx: typer.Context,
#     test_album,
#     test_asset,
# ):
#     """Test get-activities command with all optional filters."""
#     # Create multiple activities with different types
#     like_activity = await mock_ctx.obj["client"].activities.create_activity(
#         album_id=str(test_album.id),
#         asset_id=str(test_asset),
#         type="like",
#     )
#     comment_activity = await mock_ctx.obj["client"].activities.create_activity(
#         album_id=str(test_album.id),
#         asset_id=str(test_asset),
#         comment="Test comment",
#         type="comment",
#     )

#     # Get current user for user_id filter
#     my_user = await mock_ctx.obj["client"].users.get_my_user()

#     # Test with all filters: album_id, asset_id, type, user_id
#     get_activities(
#         ctx=mock_ctx,
#         album_id=str(test_album.id),
#         asset_id=str(test_asset),
#         type="like",
#         user_id=str(my_user.id),
#     )

#     # Test with level filter (if supported)
#     get_activities(
#         ctx=mock_ctx,
#         album_id=str(test_album.id),
#         asset_id=str(test_asset),
#         level="user",
#     )

#     # Cleanup
#     await mock_ctx.obj["client"].activities.delete_activity(like_activity.id)
#     await mock_ctx.obj["client"].activities.delete_activity(comment_activity.id)


# @pytest.mark.asyncio
# @pytest.mark.e2e
# async def test_get_activity_statistics_with_asset(
#     mock_ctx: typer.Context,
#     test_album,
#     test_asset,
# ):
#     """Test get-activity-statistics command with asset_id."""
#     # Create some activities first
#     await mock_ctx.obj["client"].activities.create_activity(
#         album_id=str(test_album.id),
#         asset_id=str(test_asset),
#         type="like",
#     )
#     await mock_ctx.obj["client"].activities.create_activity(
#         album_id=str(test_album.id),
#         asset_id=str(test_asset),
#         comment="Test comment",
#         type="comment",
#     )

#     # Get statistics with asset_id
#     get_activity_statistics(
#         ctx=mock_ctx,
#         album_id=str(test_album.id),
#         asset_id=str(test_asset),
#     )


# @pytest.mark.asyncio
# @pytest.mark.e2e
# async def test_get_activity_statistics_without_asset(
#     mock_ctx: typer.Context,
#     test_album,
# ):
#     """Test get-activity-statistics command without asset_id."""
#     # Create an activity without asset_id (album-level)
#     await mock_ctx.obj["client"].activities.create_activity(
#         album_id=str(test_album.id),
#         type="like",
#     )

#     # Get statistics without asset_id
#     get_activity_statistics(
#         ctx=mock_ctx,
#         album_id=str(test_album.id),
#     )
