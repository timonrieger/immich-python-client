# Response Types

There are three different available output formats you can choose from:

## Serialized Response

You can get fully serialized responses as Pydantic models. Using this, you get the full benefits of Pydantic's type checking.

```python
res = await client.server.get_about_info()
```

The output would look like this:

```python
ServerAboutResponseDto(...)
```

## Serialized Response with HTTP Info

```python
res = await client.server.get_about_info_with_http_info()
```

The output would look like this:

```python
status_code=200 headers={'Content-Type': 'application/json'} data=ServerAboutResponseDto(...) raw_data=b'{"...": "..."}'
```

## JSON Response

You can receive a classical JSON response by suffixing the function name with `_without_preload_content`:

```python
response = await client.server.get_about_info_without_preload_content()
await response.json()
```
