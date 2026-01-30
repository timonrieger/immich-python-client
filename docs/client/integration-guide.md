# Integration Guide

This guide shows how to replace raw HTTP requests with immich-py with minimal changes. You get typed responses, no manual headers (`x-api-key`, `Accept`), no URL or path construction, and the client raises specific exceptions.

## Synchronous clients

If you use a synchronous HTTP client (e.g. `requests`) to fetch server version, you can keep a sync entrypoint and call the async client via a small helper. All examples below call the fetch-server-version endpoint.

=== "requests"

    ``` python
    import requests

    base_url = "http://localhost:2283/api"
    api_key = "your-immich-api-key"

    def main():
        r = requests.get(
            f"{base_url}/server/version",
            headers={"x-api-key": api_key, "Accept": "application/json"},
            timeout=20,
        )
        r.raise_for_status()
        data = r.json()
        print(f"Server version: {data['major']}.{data['minor']}.{data['patch']}")
    ```

=== "immich-py"

    ``` python
    import asyncio
    from typing import Awaitable, Callable, TypeVar
    from aiohttp import ClientSession, ClientTimeout
    from immich import AsyncClient

    base_url = "http://localhost:2283/api"
    api_key = "your-immich-api-key"

    T = TypeVar("T")

    def request_api(fn: Callable[[AsyncClient], Awaitable[T]]) -> T:
        async def _run():
            async with AsyncClient(
                api_key=api_key,
                base_url=base_url
            ) as client:
                return await fn(client)

        return asyncio.run(_run())

    def main():
        version = request_api(lambda c: c.server.get_server_version()) # (1)!
        print(f"Server version: {version.major}.{version.minor}.{version.patch}") # (2)!
    ```

    1. Here we pass a callable that returns the result of the API call. Python knows the return type from the function signature…
    2. …so we can safely access attributes without type errors.

## Asynchronous clients

If you use an async HTTP client (`aiohttp` or `httpx`) to talk to the Immich API, you can swap to `AsyncClient`.

=== "aiohttp"

    ``` python
    import asyncio
    import aiohttp

    BASE_URL = "http://localhost:2283/api"
    API_KEY = "your-immich-api-key"

    def _get_client():
        return aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(connect=5, sock_read=60),
        )

    async def main():
        async with _get_client() as client:
            # Fetch server version
            headers = {"x-api-key": API_KEY, "Accept": "application/json"}
            async with client.get(
                f"{BASE_URL}/server/version", headers=headers
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
            print(f"Server version: {data['major']}.{data['minor']}.{data['patch']}")

    asyncio.run(main())
    ```

=== "httpx"

    ``` python
    import asyncio
    import httpx

    BASE_URL = "http://localhost:2283/api"
    API_KEY = "your-immich-api-key"

    def _get_client():
        return httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=5.0, read=60.0, write=10.0, pool=5.0
            )
        )

    async def main():
        async with _get_client() as client:
            # Fetch server version
            headers = {"x-api-key": API_KEY, "Accept": "application/json"}
            r = await client.get(f"{BASE_URL}/server/version", headers=headers)
            r.raise_for_status()
            data = r.json()
            print(f"Server version: {data['major']}.{data['minor']}.{data['patch']}")

    asyncio.run(main())
    ```

=== "immich-py"

    ``` python
    import asyncio
    import aiohttp
    from immich import AsyncClient

    BASE_URL = "http://localhost:2283/api"
    API_KEY = "your-immich-api-key"

    def _get_client():
        session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(connect=5, sock_read=60),
        )
        return AsyncClient(
            api_key=API_KEY,
            base_url=BASE_URL,
            http_client=session,
        )

    async def main():
        async with _get_client() as client:
            version = await client.server.get_server_version()
            print(f"Server version: {version.major}.{version.minor}.{version.patch}")

    asyncio.run(main())
    ```

## Error handling

Each library raises different exceptions for connection failures, timeouts, and HTTP errors. immich-py makes the error handling easy with custom exceptions. Read on [Exception Handling](exception-handling.md) for more details.

=== "requests"

    ``` python
    import requests

    try:
        # ... your API call here (e.g. r = requests.get(...)); r.raise_for_status() ...
        pass
    except requests.ConnectionError:
        # Connection failed (DNS, refused, etc.)
        raise
    except requests.Timeout: # (1)!
        # Connect or read timeout
        raise
    except requests.HTTPError as e:
        # r.raise_for_status() raised (4xx, 5xx)
        raise
    ```

    1. Not needed if you don't set a timeout on the request.

=== "aiohttp"

    ``` python
    import aiohttp

    try:
        # ... your API call here (e.g. async with client.get(...) as resp; resp.raise_for_status()) ...
        pass
    except aiohttp.ClientConnectionError:
        # Connection failed (DNS, refused, etc.)
        raise
    except aiohttp.ClientResponseError as e:
        # resp.raise_for_status() or timeout on response
        raise
    ```

    1. Not needed if you don't set a timeout on the request.

=== "httpx"

    ``` python
    import httpx

    try:
        # ... your API call here (e.g. r = await client.get(...); r.raise_for_status()) ...
        pass
    except httpx.RequestError:
        # Connection failed or timeout
        raise
    except httpx.HTTPStatusError as e:
        # r.raise_for_status() raised (4xx, 5xx)
        raise
    ```

=== "immich-py"

    ``` python
    import logging
    import aiohttp
    from immich.client.generated.exceptions import ApiException

    try:
        # ... your API call here (e.g. await client.server.get_server_version()) ...
        pass
    except ApiException as e:
        msg = str(e.body) if e.body else "API error"
        logging.error("%s (status %s)", msg, e.status)
        raise
    except asyncio.TimeoutError as e: # (1)!
        # Timeout error
        raise
    ```

    1. Not needed if you don't set a timeout.
