"""Lazy import map for CLI commands (auto-generated, do not edit)."""

from __future__ import annotations

# Lazy import map: module_name -> CLI command name
# Modules are imported lazily in app.py for faster shell completion
_MODULE_MAP: dict[str, str] = {
    "api_keys": "api-keys",
    "activities": "activities",
    "albums": "albums",
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

# Wrapper module map: module_name -> full import path for wrapper modules
# Wrapper modules extend the auto-generated commands with convenience methods
_WRAPPERS: dict[str, str] = {
    "assets": "immich.cli_wrapper.commands.assets",
    "download": "immich.cli_wrapper.commands.download",
    "users": "immich.cli_wrapper.commands.users",
}
