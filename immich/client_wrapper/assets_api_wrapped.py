from __future__ import annotations

from pathlib import Path
from typing import Any, Optional
from uuid import UUID

from pydantic import StrictStr

from immich.client.api.assets_api import AssetsApi
from immich.client.models.asset_media_size import AssetMediaSize
from immich.utils import download_file, resolve_output_filename


class AssetsApiWrapped(AssetsApi):
    async def download_asset_to_file(
        self,
        id: UUID,
        out_dir: Path,
        key: Optional[StrictStr] = None,
        slug: Optional[StrictStr] = None,
        filename: Optional[str] = None,
        show_progress: bool = True,
        **kwargs: Any,
    ) -> Path:
        """
        Download an asset to a file.

        :param id: The asset ID.
        :param out_dir: The directory to write the asset to.
        :param key: Public share key (the last path segment of a public share URL, i.e. `/share/<key>`). When provided, the asset can be accessed via the public share link without an API key. Typically you pass either `key` or `slug`.
        :param slug: Public share slug for custom share URLs (the last path segment of `/s/<slug>`). Allows access without authentication. Typically you pass either `slug` or `key`.
        :param filename: The filename to use. If not provided, we use the original filename from the headers or default to "orig-" + asset_id.
        :param show_progress: Whether to show a tqdm progress bar while downloading.
        :param kwargs: Additional arguments to pass to the `download_asset_without_preload_content` method.

        For exact request/response behavior, inspect `AssetsApi.download_asset_without_preload_content`
        in the generated client.
        """
        out_dir.mkdir(parents=True, exist_ok=True)

        def make_request(extra_headers: Optional[dict[str, str]]):
            return self.download_asset_without_preload_content(
                id=id,
                key=key,
                slug=slug,
                _headers=kwargs.get("_headers", {}) | (extra_headers or {}),
                **kwargs,
            )

        return await download_file(
            make_request=make_request,
            out_dir=out_dir,
            resolve_filename=lambda headers: resolve_output_filename(
                headers,
                name=filename,
                default_base=f"orig-{id}",
            ),
            show_progress=show_progress,
        )

    async def play_asset_video_to_file(
        self,
        id: UUID,
        out_dir: Path,
        key: Optional[StrictStr] = None,
        slug: Optional[StrictStr] = None,
        filename: Optional[str] = None,
        show_progress: bool = True,
        **kwargs: Any,
    ) -> Path:
        """
        Save an asset's video stream to a file.

        :param id: The asset ID.
        :param out_dir: The directory to write the video to.
        :param key: Public share key (the last path segment of a public share URL, i.e. `/share/<key>`). When provided, the asset can be accessed via the public share link without an API key. Typically you pass either `key` or `slug`.
        :param slug: Public share slug for custom share URLs (the last path segment of `/s/<slug>`). Allows access without authentication. Typically you pass either `slug` or `key`.
        :param filename: The filename to use. If not provided, we use the original filename from the headers or default to "video-" + asset_id.
        :param show_progress: Whether to show a tqdm progress bar while downloading.
        :param kwargs: Additional arguments to pass to the `play_asset_video_without_preload_content` method.

        For exact request/response behavior, inspect `AssetsApi.play_asset_video_without_preload_content`
        in the generated client.
        """
        out_dir.mkdir(parents=True, exist_ok=True)

        def make_request(extra_headers: Optional[dict[str, str]]):
            return self.play_asset_video_without_preload_content(
                id=id,
                key=key,
                slug=slug,
                _headers=kwargs.get("_headers", {}) | (extra_headers or {}),
                **kwargs,
            )

        return await download_file(
            make_request=make_request,
            out_dir=out_dir,
            resolve_filename=lambda headers: resolve_output_filename(
                headers,
                name=filename,
                default_base=f"video-{id}",
            ),
            show_progress=show_progress,
        )

    async def view_asset_to_file(
        self,
        id: UUID,
        out_dir: Path,
        key: Optional[StrictStr] = None,
        size: Optional[AssetMediaSize] = None,
        slug: Optional[StrictStr] = None,
        filename: Optional[str] = None,
        show_progress: bool = True,
        **kwargs: Any,
    ) -> Path:
        """
        Save an asset's thumbnail to a file.

        :param id: The asset ID.
        :param out_dir: The directory to write the asset to.
        :param key: Public share key (the last path segment of a public share URL, i.e. `/share/<key>`). When provided, the thumbnail can be fetched via the public share link without an API key. Typically you pass either `key` or `slug`.
        :param size: Thumbnail size.
        :param slug: Public share slug for custom share URLs (the last path segment of `/s/<slug>`). Allows access without authentication. Typically you pass either `slug` or `key`.
        :param filename: The filename to use. If not provided, we use the original filename from the headers or default to "thumb-" + asset_id.
        :param show_progress: Whether to show a tqdm progress bar while downloading.
        :param kwargs: Additional arguments to pass to the `view_asset_without_preload_content` method.

        For exact request/response behavior, inspect `AssetsApi.view_asset_without_preload_content`
        in the generated client.
        """
        out_dir.mkdir(parents=True, exist_ok=True)

        def make_request(extra_headers: Optional[dict[str, str]]):
            return self.view_asset_without_preload_content(
                id=id,
                key=key,
                size=size,
                slug=slug,
                _headers=kwargs.get("_headers", {}) | (extra_headers or {}),
                **kwargs,
            )

        return await download_file(
            make_request=make_request,
            out_dir=out_dir,
            resolve_filename=lambda headers: resolve_output_filename(
                headers,
                name=filename,
                default_base=f"thumb-{id}",
            ),
            show_progress=show_progress,
        )
