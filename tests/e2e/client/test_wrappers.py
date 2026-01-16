"""E2E tests for immich.client_wrapper modules against running Immich server."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

import pytest

from immich import AsyncClient
from immich.client.models.asset_media_size import AssetMediaSize
from immich.client.models.download_info_dto import DownloadInfoDto


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_assets_upload(
    client_with_api_key: AsyncClient,
    test_image: Path,
    test_video: Path,
    asset_cleanup: dict,
):
    """Test AssetsApiWrapped.upload method."""
    result = await client_with_api_key.assets.upload(
        [test_image, test_video],
        check_duplicates=False,  # Disable duplicate checking for test independence
        concurrency=2,
        show_progress=False,
    )

    assert result.stats.total == 2
    assert result.stats.uploaded == 2
    assert len(result.uploaded) == 2
    assert len(result.rejected) == 0
    assert len(result.failed) == 0

    # Track uploaded assets for cleanup
    for uploaded in result.uploaded:
        asset_cleanup["asset_ids"].append(UUID(uploaded.asset.id))


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_assets_download_asset_to_file(
    client_with_api_key: AsyncClient,
    test_image: Path,
    tmp_path: Path,
    asset_cleanup: dict,
):
    """Test AssetsApiWrapped.download_asset_to_file method."""
    # Upload an asset first
    upload_result = await client_with_api_key.assets.upload(
        [test_image], check_duplicates=False, show_progress=False
    )
    assert len(upload_result.uploaded) == 1
    asset_id = UUID(upload_result.uploaded[0].asset.id)
    asset_cleanup["asset_ids"].append(asset_id)

    # Download the asset
    out_dir = tmp_path / "downloads"
    downloaded_path = await client_with_api_key.assets.download_asset_to_file(
        id=asset_id, out_dir=out_dir, show_progress=False
    )

    assert downloaded_path.exists()
    assert downloaded_path.is_file()
    assert downloaded_path.read_bytes() == test_image.read_bytes()


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_assets_view_asset_to_file(
    client_with_api_key: AsyncClient,
    test_image: Path,
    tmp_path: Path,
    asset_cleanup: dict,
):
    """Test AssetsApiWrapped.view_asset_to_file method."""
    # Upload an asset first
    upload_result = await client_with_api_key.assets.upload(
        [test_image], check_duplicates=False, show_progress=False
    )
    assert len(upload_result.uploaded) == 1
    asset_id = UUID(upload_result.uploaded[0].asset.id)
    asset_cleanup["asset_ids"].append(asset_id)

    # Download thumbnail
    out_dir = tmp_path / "thumbnails"
    thumbnail_path = await client_with_api_key.assets.view_asset_to_file(
        id=asset_id, out_dir=out_dir, size=AssetMediaSize.THUMBNAIL, show_progress=False
    )

    assert thumbnail_path.exists()
    assert thumbnail_path.is_file()


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_assets_play_asset_video_to_file(
    client_with_api_key: AsyncClient,
    test_video: Path,
    tmp_path: Path,
    asset_cleanup: dict,
):
    """Test AssetsApiWrapped.play_asset_video_to_file method."""
    # Upload a video first
    upload_result = await client_with_api_key.assets.upload(
        [test_video], check_duplicates=False, show_progress=False
    )
    assert len(upload_result.uploaded) == 1
    asset_id = UUID(upload_result.uploaded[0].asset.id)
    asset_cleanup["asset_ids"].append(asset_id)

    # Download video stream
    out_dir = tmp_path / "videos"
    video_path = await client_with_api_key.assets.play_asset_video_to_file(
        id=asset_id, out_dir=out_dir, show_progress=False
    )

    assert video_path.exists()
    assert video_path.is_file()


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_download_archive_to_file(
    client_with_api_key: AsyncClient,
    test_image: Path,
    tmp_path: Path,
    asset_cleanup: dict,
):
    """Test DownloadApiWrapped.download_archive_to_file method."""
    # Upload assets first
    upload_result = await client_with_api_key.assets.upload(
        [test_image], check_duplicates=False, show_progress=False
    )
    assert len(upload_result.uploaded) == 1
    asset_id = UUID(upload_result.uploaded[0].asset.id)
    asset_cleanup["asset_ids"].append(asset_id)

    # Create download info
    download_info = DownloadInfoDto(asset_ids=[asset_id])

    # Download archive
    out_dir = tmp_path / "archives"
    archive_paths = await client_with_api_key.download.download_archive_to_file(
        download_info=download_info, out_dir=out_dir, show_progress=False
    )

    assert len(archive_paths) == 1
    assert archive_paths[0].exists()
    assert archive_paths[0].suffix == ".zip"


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_users_get_profile_image_to_file(
    client_with_api_key: AsyncClient,
    test_image: Path,
    tmp_path: Path,
    asset_cleanup: dict,
):
    """Test UsersApiWrapped.get_profile_image_to_file method."""
    # Get current user info
    my_user = await client_with_api_key.users.get_my_user()
    user_id = UUID(my_user.id)

    # Upload profile image
    img_bytes = test_image.read_bytes()
    # Pass as tuple (filename, bytes) to ensure proper content type detection
    await client_with_api_key.users.create_profile_image(
        file=("profile.jpg", img_bytes)
    )
    asset_cleanup["profile_image"] = True

    # Download profile image
    out_dir = tmp_path / "profiles"
    profile_path = await client_with_api_key.users.get_profile_image_to_file(
        id=user_id, out_dir=out_dir, show_progress=False
    )

    assert profile_path.exists()
    assert profile_path.is_file()
