# Exception Handling

The client raises exceptions if the API returns an error response. Most of the time, you should catch [ApiException](reference/exceptions.md#immich.client.generated.exceptions.ApiException) (and subclasses) to handle any HTTP error.

!!! note "Already have an error handling strategy?"
    Read on [how to change your code](integration-guide.md#error-handling) to use the client's exceptions to match your strategy.

!!! info "Error forwarding"
    The client forwards the error response from the API to the exception. [HTTP status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status) are not altered, but forwarded as is.

## Exception hierarchy

- [**OpenApiException**](reference/exceptions.md#immich.client.generated.exceptions.OpenApiException) (base for all client exceptions)
    - [**ApiException**](reference/exceptions.md#immich.client.generated.exceptions.ApiException) (HTTP API errors)
        - [**BadRequestException**](reference/exceptions.md#immich.client.generated.exceptions.BadRequestException) (400)
        - [**UnauthorizedException**](reference/exceptions.md#immich.client.generated.exceptions.UnauthorizedException) (401)
        - [**ForbiddenException**](reference/exceptions.md#immich.client.generated.exceptions.ForbiddenException) (403)
        - [**NotFoundException**](reference/exceptions.md#immich.client.generated.exceptions.NotFoundException) (404)
        - [**ConflictException**](reference/exceptions.md#immich.client.generated.exceptions.ConflictException) (409)
        - [**UnprocessableEntityException**](reference/exceptions.md#immich.client.generated.exceptions.UnprocessableEntityException) (422)
        - [**ServiceException**](reference/exceptions.md#immich.client.generated.exceptions.ServiceException) (5xx)
    - [**ApiTypeError**](reference/exceptions.md#immich.client.generated.exceptions.ApiTypeError) (also `TypeError`)
    - [**ApiValueError**](reference/exceptions.md#immich.client.generated.exceptions.ApiValueError) (also `ValueError`)
    - [**ApiAttributeError**](reference/exceptions.md#immich.client.generated.exceptions.ApiAttributeError) (also `AttributeError`)
    - [**ApiKeyError**](reference/exceptions.md#immich.client.generated.exceptions.ApiKeyError) (also `KeyError`)


## Examples

### Catching any HTTP error

Catch [ApiException](reference/exceptions.md#immich.client.generated.exceptions.ApiException) to handle any HTTP error.

```python
from immich import AsyncClient
from immich.client.generated.exceptions import ApiException

async def get_server_version(base_url: str, api_key: str) -> None:
    async with AsyncClient(api_key=api_key, base_url=base_url) as client:
        try:
            version = await client.server.get_server_version()
            print(f"{version.major}.{version.minor}.{version.patch}")
        except ApiException as e:
            print(f"API error: status={e.status}, body={e.body}")
            raise
```

### Timeout

When you set a timeout on the request, you can catch it with `asyncio.TimeoutError`:

```python
import asyncio
import aiohttp
from immich import AsyncClient
from immich.client.generated.exceptions import ApiException

async def get_server_version_with_timeout(base_url: str, api_key: str) -> None:
    session = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(connect=5, sock_read=60),
    )
    async with AsyncClient(
        api_key=api_key,
        base_url=base_url,
        http_client=session,
    ) as client:
        try:
            version = await client.server.get_server_version()
            print(f"{version.major}.{version.minor}.{version.patch}")
        except ApiException as e:
            print(f"API error: status={e.status}, body={e.body}")
            raise
        except asyncio.TimeoutError as e:
            print("Request timed out")
            raise
```

### Authentication errors (401, 403)

Catch [UnauthorizedException](reference/exceptions.md#immich.client.generated.exceptions.UnauthorizedException) (401) and [ForbiddenException](reference/exceptions.md#immich.client.generated.exceptions.ForbiddenException) (403) when validating an API key or user access, and surface a clear message to the user:

```python
from immich import AsyncClient
from immich.client.generated.exceptions import (
    ApiException,
    ForbiddenException,
    UnauthorizedException,
)

async def validate_api_key(base_url: str, api_key: str) -> str:
    async with AsyncClient(api_key=api_key, base_url=base_url) as client:
        try:
            user_dto = await client.users.get_my_user()
            return str(user_dto.id)
        except (UnauthorizedException, ForbiddenException) as e:
            raise ValueError("Invalid Immich API key or no access to the API.") from e
```

### Conflict or unprocessable (409, 422)

When creating a resource that might already exist (e.g. album by name), catch [ConflictException](reference/exceptions.md#immich.client.generated.exceptions.ConflictException) (409) and [UnprocessableEntityException](reference/exceptions.md#immich.client.generated.exceptions.UnprocessableEntityException) (422) to raise a clear error message.

```python
from immich import AsyncClient
from immich.client.generated import CreateAlbumDto
from immich.client.generated.exceptions import (
    ConflictException,
    UnprocessableEntityException,
)

async def ensure_album_exists(client: AsyncClient, album_name: str) -> str:
    try:
        new_album = await client.albums.create_album(
            create_album_dto=CreateAlbumDto(albumName=album_name),
        )
        return str(new_album.id)
    except (ConflictException, UnprocessableEntityException):
        raise ValueError(f"Album '{album_name}' already exists") from e
```
