# Getting Started

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

## Usage

With a context manager (recommended):

```python
from immich import AsyncClient

async with AsyncClient(api_key="your-immich-api-key", base_url="http://localhost:2283/api") as client:
    await client.server.get_about_info()
```

Without a context manager:

```python
import asyncio
from immich import AsyncClient

async def main():
    client = AsyncClient(api_key="your-immich-api-key", base_url="http://localhost:2283/api")
    try:
        await client.server.get_about_info()
    finally:
        await client.close()

asyncio.run(main())
```
