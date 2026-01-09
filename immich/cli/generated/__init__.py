"""Generated CLI commands (auto-generated, do not edit)."""

from __future__ import annotations

from typing import Any
import typer
import importlib

# Module name to app name mapping
_MODULE_MAP: dict[str, str] = {
    "activities": "activities",
    "albums": "albums",
    "api_keys": "api-keys",
    "assets": "assets",
    "authentication": "authentication",
    "authentication_admin": "authentication-admin",
    "download": "download",
    "duplicates": "duplicates",
    "faces": "faces",
    "jobs": "jobs",
    "libraries": "libraries",
    "maintenance_admin": "maintenance-admin",
    "map": "map",
    "memories": "memories",
    "notifications": "notifications",
    "notifications_admin": "notifications-admin",
    "partners": "partners",
    "people": "people",
    "plugins": "plugins",
    "queues": "queues",
    "search": "search",
    "server": "server",
    "sessions": "sessions",
    "shared_links": "shared-links",
    "stacks": "stacks",
    "sync": "sync",
    "system_config": "system-config",
    "system_metadata": "system-metadata",
    "tags": "tags",
    "timeline": "timeline",
    "trash": "trash",
    "users": "users",
    "users_admin": "users-admin",
    "views": "views",
    "workflows": "workflows",
}

_imported_modules: dict[str, Any] = {}
_APPS_CACHE: dict[str, typer.Typer] | None = None


def _lazy_import(module_name: str) -> Any:
    """Lazy import a module, caching the result."""
    if module_name not in _imported_modules:
        _imported_modules[module_name] = importlib.import_module(
            f"immich.cli.commands.{module_name}"
        )
    return _imported_modules[module_name]


def _get_apps() -> dict[str, typer.Typer]:
    """Get all apps, using lazy imports."""
    global _APPS_CACHE
    if _APPS_CACHE is not None:
        return _APPS_CACHE

    _APPS_CACHE = {}
    for module_name, app_name in _MODULE_MAP.items():
        module = _lazy_import(module_name)
        _APPS_CACHE[app_name] = module.app
    return _APPS_CACHE


class _AppsDict:
    """Lazy dict-like wrapper for APPS that imports modules on demand."""

    def __getitem__(self, key: str) -> typer.Typer:
        return _get_apps()[key]

    def __contains__(self, key: str) -> bool:
        return key in _get_apps()

    def items(self):
        return _get_apps().items()

    def keys(self):
        return _get_apps().keys()

    def values(self):
        return _get_apps().values()

    def __iter__(self):
        return iter(_get_apps())

    def get(self, key: str, default: Any = None) -> Any:
        return _get_apps().get(key, default)

    def __len__(self) -> int:
        return len(_get_apps())


APPS: dict[str, typer.Typer] = _AppsDict()  # type: ignore[assignment]
