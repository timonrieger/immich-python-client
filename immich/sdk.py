from __future__ import annotations

from typing import Optional

from aiohttp import ClientSession  # type: ignore[import-not-found]

from immich.client.api_client import ApiClient
from immich.client.configuration import Configuration

from immich.client.api.activities_api import ActivitiesApi
from immich.client.api.albums_api import AlbumsApi
from immich.client.api.api_keys_api import APIKeysApi
from immich.client_wrapper.assets_api_wrapped import AssetsApiWrapped
from immich.client.api.authentication_admin_api import AuthenticationAdminApi
from immich.client.api.authentication_api import AuthenticationApi
from immich.client.api.deprecated_api import DeprecatedApi
from immich.client.api.download_api import DownloadApi
from immich.client.api.duplicates_api import DuplicatesApi
from immich.client.api.faces_api import FacesApi
from immich.client.api.jobs_api import JobsApi
from immich.client.api.libraries_api import LibrariesApi
from immich.client.api.maintenance_admin_api import MaintenanceAdminApi
from immich.client.api.map_api import MapApi
from immich.client.api.memories_api import MemoriesApi
from immich.client.api.notifications_admin_api import NotificationsAdminApi
from immich.client.api.notifications_api import NotificationsApi
from immich.client.api.partners_api import PartnersApi
from immich.client.api.people_api import PeopleApi
from immich.client.api.plugins_api import PluginsApi
from immich.client.api.queues_api import QueuesApi
from immich.client.api.search_api import SearchApi
from immich.client.api.server_api import ServerApi
from immich.client.api.sessions_api import SessionsApi
from immich.client.api.shared_links_api import SharedLinksApi
from immich.client.api.stacks_api import StacksApi
from immich.client.api.sync_api import SyncApi
from immich.client.api.system_config_api import SystemConfigApi
from immich.client.api.system_metadata_api import SystemMetadataApi
from immich.client.api.tags_api import TagsApi
from immich.client.api.timeline_api import TimelineApi
from immich.client.api.trash_api import TrashApi
from immich.client.api.users_admin_api import UsersAdminApi
from immich.client.api.users_api import UsersApi
from immich.client.api.views_api import ViewsApi
from immich.client.api.workflows_api import WorkflowsApi


def _normalize_base_url(base_url: str) -> str:
    return base_url.rstrip("/")


def _build_configuration(
    *,
    api_key: Optional[str],
    bearer_token: Optional[str],
    cookie: Optional[str],
    base_url: str,
) -> Configuration:
    config = Configuration(host=_normalize_base_url(base_url))
    if api_key:
        # Security scheme name is `api_key` (header: x-api-key)
        config.api_key["api_key"] = api_key
    if cookie:
        # Security scheme name is `cookie` (cookie: immich_access_token)
        config.api_key["cookie"] = cookie
    if bearer_token:
        # JWT access token (Authorization: Bearer <token>)
        config.access_token = bearer_token
    return config


class AsyncClient:
    """
    Async client for the Immich API (OpenAPI-generated).
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        bearer_token: Optional[str] = None,
        cookie: Optional[str] = None,
        base_url: str,
        http_client: Optional[ClientSession] = None,
    ) -> None:
        self._owns_http_client = http_client is None
        self._injected_http_client = http_client
        self.config = _build_configuration(
            api_key=api_key,
            bearer_token=bearer_token,
            cookie=cookie,
            base_url=base_url,
        )
        self.base_client = ApiClient(configuration=self.config)
        self.base_client.user_agent = "immich-python-client"

        # Allow caller to inject a pre-configured aiohttp session.
        if http_client is not None:
            self.base_client.rest_client.pool_manager = http_client

        # API groups (single upstream API, not microservices)
        self.activities = ActivitiesApi(self.base_client)
        self.albums = AlbumsApi(self.base_client)
        self.api_keys = APIKeysApi(self.base_client)
        self.assets = AssetsApiWrapped(self.base_client)
        self.authentication = AuthenticationApi(self.base_client)
        self.authentication_admin = AuthenticationAdminApi(self.base_client)
        self.deprecated = DeprecatedApi(self.base_client)
        self.download = DownloadApi(self.base_client)
        self.duplicates = DuplicatesApi(self.base_client)
        self.faces = FacesApi(self.base_client)
        self.jobs = JobsApi(self.base_client)
        self.libraries = LibrariesApi(self.base_client)
        self.maintenance_admin = MaintenanceAdminApi(self.base_client)
        self.map = MapApi(self.base_client)
        self.memories = MemoriesApi(self.base_client)
        self.notifications = NotificationsApi(self.base_client)
        self.notifications_admin = NotificationsAdminApi(self.base_client)
        self.partners = PartnersApi(self.base_client)
        self.people = PeopleApi(self.base_client)
        self.plugins = PluginsApi(self.base_client)
        self.queues = QueuesApi(self.base_client)
        self.search = SearchApi(self.base_client)
        self.server = ServerApi(self.base_client)
        self.sessions = SessionsApi(self.base_client)
        self.shared_links = SharedLinksApi(self.base_client)
        self.stacks = StacksApi(self.base_client)
        self.sync = SyncApi(self.base_client)
        self.system_config = SystemConfigApi(self.base_client)
        self.system_metadata = SystemMetadataApi(self.base_client)
        self.tags = TagsApi(self.base_client)
        self.timeline = TimelineApi(self.base_client)
        self.trash = TrashApi(self.base_client)
        self.users = UsersApi(self.base_client)
        self.users_admin = UsersAdminApi(self.base_client)
        self.views = ViewsApi(self.base_client)
        self.workflows = WorkflowsApi(self.base_client)

    async def close(self) -> None:
        # If the caller injected the aiohttp session, don't close it.
        if not self._owns_http_client and self._injected_http_client is not None:
            self.base_client.rest_client.pool_manager = None
        await self.base_client.close()

    async def __aenter__(self) -> "AsyncClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()
