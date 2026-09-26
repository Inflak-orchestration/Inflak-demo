"""Trusted registry for the independent inflak plugin directories."""

from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any


PROJECT_DIR = Path(__file__).resolve().parents[2]
PLUGINS_DIR = PROJECT_DIR / "plugins"
MANIFEST_PATH = PLUGINS_DIR / "inflak-plugins.json"
DEFAULT_PLUGIN_ID = "inflak-main"


class PluginRegistryError(ValueError):
    """Raised when the plugin manifest is malformed or an id is unknown."""


@lru_cache(maxsize=1)
def plugin_registry() -> dict[str, dict[str, Any]]:
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    entries = data.get("plugins")
    if not isinstance(entries, list):
        raise PluginRegistryError("Plugin manifest must contain a plugins array.")

    registry: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise PluginRegistryError("Plugin manifest entries must be objects.")
        plugin_id = entry.get("id")
        directory = entry.get("directory")
        status = entry.get("status")
        if not isinstance(plugin_id, str) or not isinstance(directory, str) or status not in {"ready", "planned"}:
            raise PluginRegistryError("Each plugin requires id, directory, and ready/planned status.")
        if Path(directory).name != directory:
            raise PluginRegistryError(f"Plugin {plugin_id} has an invalid directory.")
        if plugin_id in registry:
            raise PluginRegistryError(f"Duplicate plugin id: {plugin_id}")
        registry[plugin_id] = entry
    if DEFAULT_PLUGIN_ID not in registry:
        raise PluginRegistryError(f"Missing default plugin: {DEFAULT_PLUGIN_ID}")
    return registry


def plugin_entry(plugin_id: str | None = None, *, require_ready: bool = True) -> dict[str, Any]:
    selected_id = plugin_id or DEFAULT_PLUGIN_ID
    entry = plugin_registry().get(selected_id)
    if entry is None:
        raise PluginRegistryError(f"Unknown inflak plugin: {selected_id}")
    if require_ready and entry["status"] != "ready":
        raise PluginRegistryError(f"Inflak plugin is not available yet: {selected_id}")
    return entry


def plugin_dir(plugin_id: str | None = None, *, require_ready: bool = True) -> Path:
    entry = plugin_entry(plugin_id, require_ready=require_ready)
    path = (PLUGINS_DIR / entry["directory"]).resolve()
    if path.parent != PLUGINS_DIR.resolve() or not (path / "SKILL.md").is_file():
        raise PluginRegistryError(f"Plugin directory is missing or invalid: {entry['id']}")
    return path


def ready_plugin_dirs() -> list[Path]:
    return [plugin_dir(plugin_id) for plugin_id, entry in plugin_registry().items() if entry["status"] == "ready"]


def runtime_plugin_dirs() -> list[Path]:
    """Return every installed bundle; selection policy still gates planned plugins."""
    return [plugin_dir(plugin_id, require_ready=False) for plugin_id in plugin_registry()]


def _plugin_relative_path(root: Path, relative_path: str, *, label: str) -> Path:
    candidate = (root / relative_path).resolve()
    if candidate != root and root not in candidate.parents:
        raise PluginRegistryError(f"{label} escapes plugin directory: {relative_path}")
    return candidate


def runtime_mcp_servers() -> dict[str, dict[str, Any]]:
    """Return reviewed stdio MCP servers bundled by ready plugins."""
    servers: dict[str, dict[str, Any]] = {}
    for plugin_id, entry in plugin_registry().items():
        if entry["status"] != "ready":
            continue
        root = plugin_dir(plugin_id)
        manifest_path = root / "plugin.json"
        if not manifest_path.is_file():
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise PluginRegistryError(f"Plugin {plugin_id} has an invalid plugin.json: {error}") from error
        source = manifest.get("mcpServers")
        if source is None:
            continue
        if isinstance(source, str):
            config_path = _plugin_relative_path(root, source, label=f"Plugin {plugin_id} MCP config")
            try:
                config = json.loads(config_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as error:
                raise PluginRegistryError(f"Plugin {plugin_id} has an invalid MCP config: {error}") from error
        elif isinstance(source, dict):
            config = source
        else:
            raise PluginRegistryError(f"Plugin {plugin_id} mcpServers must be a path or object.")
        declared_servers = config.get("mcpServers", config)
        if not isinstance(declared_servers, dict):
            raise PluginRegistryError(f"Plugin {plugin_id} MCP config must contain a server map.")

        for server_name, raw_server in declared_servers.items():
            if not isinstance(server_name, str) or not server_name or not isinstance(raw_server, dict):
                raise PluginRegistryError(f"Plugin {plugin_id} has an invalid MCP server entry.")
            if server_name in servers:
                raise PluginRegistryError(f"Duplicate plugin MCP server name: {server_name}")
            server_type = str(raw_server.get("type") or "stdio")
            if server_type not in {"local", "stdio"}:
                raise PluginRegistryError(f"Plugin {plugin_id} MCP server {server_name} must use stdio.")
            command = str(raw_server.get("command") or "")
            if command not in {"python", "python3", "${PYTHON}"}:
                raise PluginRegistryError(
                    f"Plugin {plugin_id} MCP server {server_name} must use the reviewed Python interpreter."
                )
            args = raw_server.get("args") or []
            tools = raw_server.get("tools") or []
            env = raw_server.get("env") or {}
            if not isinstance(args, list) or not all(isinstance(item, str) for item in args):
                raise PluginRegistryError(f"Plugin {plugin_id} MCP server {server_name} args must be strings.")
            if not isinstance(tools, list) or not tools or "*" in tools or not all(isinstance(item, str) for item in tools):
                raise PluginRegistryError(
                    f"Plugin {plugin_id} MCP server {server_name} requires an explicit non-wildcard tool allowlist."
                )
            if not isinstance(env, dict) or not all(isinstance(key, str) and isinstance(value, str) for key, value in env.items()):
                raise PluginRegistryError(f"Plugin {plugin_id} MCP server {server_name} env must contain strings.")
            cwd = str(raw_server.get("cwd") or "${PLUGIN_ROOT}")
            working_directory = root if cwd == "${PLUGIN_ROOT}" else _plugin_relative_path(
                root,
                cwd,
                label=f"Plugin {plugin_id} MCP cwd",
            )
            resolved_env = {
                key: value.replace("${PLUGIN_ROOT}", str(root))
                for key, value in env.items()
            }
            server: dict[str, Any] = {
                "type": "stdio",
                "command": sys.executable,
                "args": args,
                "tools": tools,
                "working_directory": str(working_directory),
            }
            if resolved_env:
                server["env"] = resolved_env
            timeout = raw_server.get("timeout")
            if timeout is not None:
                if not isinstance(timeout, int) or timeout <= 0:
                    raise PluginRegistryError(f"Plugin {plugin_id} MCP server {server_name} timeout must be positive.")
                server["timeout"] = timeout
            servers[server_name] = server
    return servers


def runtime_mcp_tool_bindings() -> dict[str, dict[str, Any]]:
    bindings: dict[str, dict[str, Any]] = {}
    for server_name, server in runtime_mcp_servers().items():
        for tool_name in server["tools"]:
            if tool_name in bindings:
                raise PluginRegistryError(f"Duplicate plugin MCP tool name: {tool_name}")
            bindings[tool_name] = {
                "name": tool_name,
                "handler_callable": True,
                "transport": "mcp",
                "server": server_name,
            }
    return bindings


def canonical_runtime_tool_name(tool_name: str) -> str:
    for canonical_name, binding in runtime_mcp_tool_bindings().items():
        if tool_name == canonical_name or tool_name == f"{binding['server']}-{canonical_name}":
            return canonical_name
    return tool_name


def plugin_runtime_entry_skill(plugin_id: str, *, require_ready: bool = True) -> str:
    """Return the SDK-discoverable entry skill for a selected plugin."""
    entry = plugin_entry(plugin_id, require_ready=require_ready)
    root = plugin_dir(entry["id"], require_ready=require_ready)
    callable_root = root / "skills" / entry["id"] / "SKILL.md"
    if callable_root.is_file():
        return entry["id"]
    l1_skills = list(root.glob("skills/l1-*/SKILL.md"))
    if len(l1_skills) != 1:
        raise PluginRegistryError(
            f"Plugin {entry['id']} has no callable root alias and does not declare exactly one Layer 1 entry."
        )
    return l1_skills[0].parent.name


def public_plugins() -> list[dict[str, Any]]:
    return [
        {
            "id": entry["id"],
            "label": entry["label"],
            "description": entry["description"],
            "status": entry["status"],
        }
        for entry in plugin_registry().values()
    ]