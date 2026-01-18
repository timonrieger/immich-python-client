from typing import Any, Optional, overload

import rtoml
import typer

from immich._internal.consts import CONFIG_DIR, CONFIG_FILE, SECRET_KEYS
from immich._internal.types import ClientConfig, _LogLevel


def set_path(data: dict[str, Any], path: str, value: Any) -> dict[str, Any]:
    """
    Set a nested dictionary value using a path list.

    Example: set_path({}, 'user.name', 'John') -> {'user': {'name': 'John'}}
    """
    parts = path.split(".")
    cur = data
    for p in parts[:-1]:
        cur = cur.setdefault(p, {})
    cur[parts[-1]] = value


def get_path(data: dict[str, Any], path: str) -> Any:
    """
    Get a nested dictionary value using a path list.
    """
    parts = path.split(".")
    cur = data
    for p in parts:
        cur = cur[p]
    return cur


def _ensure_config() -> None:
    """
    Ensure the config directory exists and the config file exists.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        CONFIG_FILE.touch()
        CONFIG_FILE.chmod(0o600)


def load_config(ensure_exists: bool = False) -> dict[str, Any]:
    """
    Load the config file.
    """
    if ensure_exists:
        _ensure_config()
    return rtoml.load(CONFIG_FILE, none_value="")


def write_config(data: dict[str, Any]) -> None:
    """
    Write the config data to the config file and set permissions.
    """
    with CONFIG_FILE.open("w") as f:
        rtoml.dump(data, f, none_value="")
    CONFIG_FILE.chmod(0o600)


def check_config() -> None:
    """
    Check if the config file exists.
    """
    if not CONFIG_FILE.exists():
        typer.echo("Config file does not exist. Run 'immich config set' to create it.")
        raise typer.Exit(code=1)
    return True


def resolve_client_config(config: ClientConfig, profile: str) -> ClientConfig:
    """
    Resolve the client config from the config file.

    :param config: The config to resolve
    :param profile: The profile to use
    :raises typer.Exit: If the profile is not found in the config
    :return: The resolved config
    """
    data = load_config()
    try:
        profile_data: dict[str, Any] = data["profiles"][profile]
    except KeyError:
        typer.echo(
            f"Profile {profile} not found in config. Run 'immich config set --profile {profile}' to create it."
        )
        raise typer.Exit(code=1)

    return ClientConfig(
        api_key=config.api_key or profile_data.get("api_key"),
        access_token=config.access_token or profile_data.get("access_token"),
        base_url=config.base_url or profile_data.get("base_url"),
    )


def _is_secret_key(key: str) -> bool:
    """Check if a key indicates a secret value."""
    return any(secret in key.lower() for secret in SECRET_KEYS)


def _redact_secret(secret: str, start: int = 3, end: int = 3) -> str:
    """
    Redact a secret by showing only the first `start` and last `end` characters.

    :param secret: The secret string to redact
    :param start: Number of characters to show at the start (default: 3)
    :param end: Number of characters to show at the end (default: 3)
    :return: The redacted secret string
    """
    if not secret:
        return ""

    length = len(secret)
    if length <= start + end:
        return "*" * length

    return secret[:start] + "*" * (length - start - end) + secret[-end:]


@overload
def mask(secret: str, start: int = 3, end: int = 3) -> str: ...


@overload
def mask(obj: Any, start: int = 3, end: int = 3, key: Optional[str] = None) -> Any: ...


def mask(obj: Any, start: int = 3, end: int = 3, key: Optional[str] = None) -> Any:
    """
    Recursively mask secret values in nested dictionaries and lists.

    :param obj: The object to mask (dict, list, or any other type)
    :param start: Number of characters to show at the start (default: 3)
    :param end: Number of characters to show at the end (default: 3)
    :param key: Optional key path for top-level values to check if they're secrets
    :return: The masked object with secrets redacted using _redact_secret
    """
    if isinstance(obj, dict):
        return {
            k: (
                _redact_secret(v, start, end)
                if _is_secret_key(k) and isinstance(v, str)
                else mask(v, start, end, k)
            )
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [mask(v, start, end) for v in obj]
    if isinstance(obj, str):
        if key is None or _is_secret_key(key):
            return _redact_secret(obj, start, end)
    return obj


def print_(
    message: str,
    *,
    level: _LogLevel = "info",
    ctx: Optional[typer.Context] = None,
    **kwargs: Any,
) -> None:
    """
    Print a message in verbose mode.
    :param message: The message to print
    :param level: The level of the message
    :param ctx: The context to use
    :param kwargs: Additional keyword arguments to pass to typer.secho
    """
    if ctx is not None and ctx.obj["verbose"] and level == "debug":
        typer.secho(message, fg="blue", **kwargs)
    elif level == "info":
        typer.secho(message, **kwargs)
    elif level == "warning":
        typer.secho(message, fg="yellow", **kwargs)
    elif level == "error":
        typer.secho(message, fg="red", **kwargs)
