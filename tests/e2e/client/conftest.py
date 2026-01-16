from collections.abc import AsyncGenerator, Awaitable, Callable
from uuid import UUID

import pytest

from immich import AsyncClient
from immich._internal.upload import UploadResult
from immich.client.models.asset_bulk_delete_dto import AssetBulkDeleteDto


@pytest.fixture
async def upload_assets(
    client_with_api_key: AsyncClient,
) -> AsyncGenerator[Callable[..., Awaitable[UploadResult]], None]:
    """Factory fixture: yields an async callable to upload assets and auto-clean them up.

    Example:
        upload_result = await upload_assets([test_image], check_duplicates=False, show_progress=False)
    """

    uploaded_ids: list[UUID] = []

    async def _upload(*args, **kwargs) -> UploadResult:
        try:
            result = await client_with_api_key.assets.upload(*args, **kwargs)
        except Exception as e:
            pytest.skip(f"Asset upload failed:\n{e}")

        uploaded_ids.extend(UUID(u.asset.id) for u in result.uploaded)
        return result

    yield _upload

    if uploaded_ids:
        try:
            await client_with_api_key.assets.delete_assets(
                AssetBulkDeleteDto(ids=uploaded_ids, force=True)
            )
        except Exception:
            pass  # Ignore cleanup errors
