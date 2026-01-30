# Response Types

There are three different available output formats you can choose from:

## Serialized Response

By default, the client returns fully serialized responses as [Pydantic](https://docs.pydantic.dev/) models.

```python
await client.server.get_about_info() # (1)!
```

1. See [ServerApi.get_about_info](reference/api/server_api.md#immich.client.generated.api.server_api.ServerApi.get_about_info) for more details.

The output would look like this:

```python
ServerAboutResponseDto(
    build='20375083601',
    build_image='main',
    ...
    version='v2.4.1',
    version_url='https://github.com/immich-app/immich/releases/tag/v2.4.1'
)
```


## Serialized Response with HTTP Info

To get additional metadata about the HTTP response, you can suffix the function name with `_with_http_info`. This returns an [ApiResponse](reference/responses.md#immich.client.generated.api_response.ApiResponse) object.

```python
await client.server.get_about_info_with_http_info() # (1)!
```

1. See [ServerApi.get_about_info_with_http_info](reference/api/server_api.md#immich.client.generated.api.server_api.ServerApi.get_about_info_with_http_info) for more details.

```python
ApiResponse(
    status_code=200,
    headers={'Content-Type': 'application/json'},
    data=ServerAboutResponseDto(
        build='20375083601',
        build_image='main',
        ...
        version='v2.4.1',
        version_url='https://github.com/immich-app/immich/releases/tag/v2.4.1'
    ),
    raw_data=b'{"build":"20375083601","buildImage":"main",...}'
)
```

## JSON Response

To receive a classical JSON response, you can suffix the function name with `_without_preload_content`. This returns a [RESTResponseType](reference/responses.md#immich.client.generated.rest.RESTResponseType) object, which needs to be awaited to get the JSON data.

```python
response = await client.server.get_about_info_without_preload_content() # (1)!
await response.json()
```

1. See [ServerApi.get_about_info_without_preload_content](reference/api/server_api.md#immich.client.generated.api.server_api.ServerApi.get_about_info_without_preload_content) for more details.

```json
{
    "build": "20375083601",
    "buildImage": "main",
    ...
    "version": "v2.4.1",
    "versionUrl": "https://github.com/immich-app/immich/releases/tag/v2.4.1"
}
```
