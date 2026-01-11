import pytest
from aiohttp import ClientSession

from immich import AsyncClient
from immich.client.api.assets_api import AssetsApi
from immich.client.api.users_api import UsersApi


@pytest.mark.asyncio
async def test_client_requires_base_url():
    with pytest.raises(TypeError):
        AsyncClient()  # type: ignore[call-arg]


@pytest.mark.asyncio
async def test_client_exposes_api_groups():
    client = AsyncClient(base_url="http://localhost:2283/api", api_key="test")
    try:
        assert isinstance(client.assets, AssetsApi)
        assert isinstance(client.users, UsersApi)
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_client_close_does_not_close_injected_session():
    custom_session = ClientSession()
    client = AsyncClient(
        base_url="http://localhost:2283/api",
        api_key="test",
        http_client=custom_session,
    )
    await client.close()
    assert not custom_session.closed
    await custom_session.close()


@pytest.mark.asyncio
async def test_client_close_closes_owned_session_if_present():
    client = AsyncClient(base_url="http://localhost:2283/api", api_key="test")
    session = ClientSession()
    client.base_client.rest_client.pool_manager = session
    await client.close()
    assert session.closed
