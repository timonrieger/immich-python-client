import gc
import warnings

import pytest
from aiohttp import ClientSession

from immich import AsyncClient


@pytest.mark.asyncio
async def test_custom_http_client_injection():
    custom_session = ClientSession()

    client = AsyncClient(
        base_url="http://localhost:2283/api", http_client=custom_session
    )
    assert client.base_client.rest_client.pool_manager is custom_session

    await client.close()
    assert not custom_session.closed  # Client did not own it

    await custom_session.close()


@pytest.mark.asyncio
async def test_lazy_http_client_creation():
    client = AsyncClient(base_url="http://localhost:2283/api")
    assert client.base_client.rest_client.pool_manager is None

    await client.close()
    assert client.base_client.rest_client.pool_manager is None


@pytest.mark.asyncio
async def test_close_custom_http_client_not_owned():
    custom_session = ClientSession()
    client = AsyncClient(
        base_url="http://localhost:2283/api", http_client=custom_session
    )

    await client.close()
    assert not custom_session.closed  # Still open since it wasn't owned by us

    await custom_session.close()


@pytest.mark.asyncio
async def test_close_owned_http_client():
    client = AsyncClient(base_url="http://localhost:2283/api")
    session = ClientSession()
    client.base_client.rest_client.pool_manager = session

    await client.close()
    assert session.closed  # session should be closed since we own it


@pytest.mark.asyncio
async def test_unclosed_owned_session_warns():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")  # Catch all warnings

        client = AsyncClient(base_url="http://localhost:2283/api")
        client.base_client.rest_client.pool_manager = ClientSession()

        # Intentionally forget to close
        del client
        gc.collect()

        # Look for aiohttp's unclosed session warning
        unclosed_warnings = [
            warn
            for warn in w
            if "Unclosed client session" in str(warn.message)
            or "Unclosed connector" in str(warn.message)
        ]
        assert unclosed_warnings, "Expected unclosed client session warning"


@pytest.mark.asyncio
async def test_custom_session_not_closed_by_client():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        custom_session = ClientSession()
        client = AsyncClient(
            base_url="http://localhost:2283/api", http_client=custom_session
        )
        assert client.base_client.rest_client.pool_manager is custom_session

        # Don't close the custom session
        del client
        del custom_session

        # Force cleanup (otherwise it's unpredicatable when the warning will be raised)
        gc.collect()

        unclosed_warnings = [
            warn
            for warn in w
            if "Unclosed client session" in str(warn.message)
            or "Unclosed connector" in str(warn.message)
        ]
        assert unclosed_warnings, "Expected unclosed client session warning"


@pytest.mark.asyncio
async def test_context_manager_usage():
    async with AsyncClient(base_url="http://localhost:2283/api") as client:
        assert client.base_client is not None

    # Confirm session is closed after context manager
    assert client.base_client.rest_client.pool_manager is None
