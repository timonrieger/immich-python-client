# Immich API Client

Unofficial Python client for the [Immich](https://immich.app) API.

> [!IMPORTANT]
> This repository is **auto-generated** from the Immich OpenAPI specification.
> **Do not open pull requests**: PRs will be closed. See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

## Status

- **Unofficial**: This project is not affiliated with or endorsed by the Immich project.
- **Auto-sync with Immich**: The client is kept in **automatic sync with the latest Immich release** (generated/updated as upstream changes land).

## Installation

You need Python 3.10–3.14 installed to be able to use this library.

Install the latest stable version from PyPI:

```bash
pip install immich
```

If you want the latest version (which may be a pre-release):

```bash
pip install --pre immich
```

## Structure

This SDK is available as an asynchronous Python client:

- `AsyncClient` — for async/await usage

```python
from immich import AsyncClient
```

## Authentication

Immich supports API keys. Create an API key in your Immich server, then pass it to the client via `api_key=...`.

## Basic usage

### Asynchronous client

Recommended (context manager):

```python
from immich import AsyncClient

async def main():
    async with AsyncClient(api_key="your-immich-api-key", base_url="http://localhost:2283/api") as client:
        # Call generated API methods here
        ...
```

Without a context manager:

```python
import asyncio
from immich import AsyncClient

async def main():
    client = AsyncClient(api_key="your-immich-api-key", base_url="http://localhost:2283/api")
    try:
        ...
    finally:
        await client.close()

asyncio.run(main())
```

## Session management

- The **async client** can manage a shared `aiohttp.ClientSession` internally, or you can inject your own `aiohttp.ClientSession` via `http_client=...` (you then own its lifecycle).

## Versioning

This package follows **Semantic Versioning (SemVer)**.

- **Package version does NOT imply the supported Immich version**: `immich` package `X.Y.Z` is the client’s own version, not an encoded Immich server version.
- **Upstream breaking changes ⇒ major bump**: Breaking Immich API/upstream changes that require breaking client changes will result in a new **major** version of this package.
- **Supported Immich server version**: `IMMICH-VERSION` (at the repository root) tracks the upstream Immich server version the generated client is built against.
  - If you run an **older** Immich server version, you can install an **older** `immich` package release where `IMMICH-VERSION` matches your server.
  - This client supports **Immich v2.4.1** and above.
