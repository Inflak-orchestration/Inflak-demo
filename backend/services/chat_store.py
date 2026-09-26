from __future__ import annotations

import json
import re
import shutil
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


PROJECT_DIR = Path(__file__).resolve().parents[2]
CHAT_STORE_DIR = PROJECT_DIR / "data" / "chat_sessions"
UPLOADS_DIR = PROJECT_DIR / "data" / "uploads"
PLUGIN_AUTHORING_DIR = PROJECT_DIR / "data" / "plugin_authoring"


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def safe_session_id(session_id: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", session_id):
        raise ValueError("Invalid session id")
    return session_id


def session_path(session_id: str) -> Path:
    return CHAT_STORE_DIR / f"{safe_session_id(session_id)}.json"


def ensure_store_dir() -> None:
    CHAT_STORE_DIR.mkdir(parents=True, exist_ok=True)


def load_session(session_id: str) -> dict[str, Any]:
    path = session_path(session_id)
    if not path.exists():
        raise FileNotFoundError(session_id)
    return json.loads(path.read_text(encoding="utf-8"))


def save_session(record: dict[str, Any]) -> None:
    ensure_store_dir()
    path = session_path(record["sessionId"])
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")


def create_session_record(
    *,
    session_id: str,
    model: str,
    working_directory: str,
    approve_all: bool,
    default_plugin_id: str = "inflak-main",
    allow_planned_plugin: bool = False,
) -> dict[str, Any]:
    timestamp = now_iso()
    record = {
        "schemaVersion": "1.0",
        "sessionId": session_id,
        "model": model,
        "workingDirectory": working_directory,
        "approveAll": approve_all,
        "defaultPluginId": default_plugin_id,
        "allowPlannedPlugin": allow_planned_plugin,
        "favorite": False,
        "createdAt": timestamp,
        "updatedAt": timestamp,
        "title": "New chat",
        "messages": [],
    }
    save_session(record)
    return record


def ensure_session_record(
    *,
    session_id: str,
    model: str,
    working_directory: str,
    approve_all: bool,
    default_plugin_id: str = "inflak-main",
    allow_planned_plugin: bool = False,
) -> dict[str, Any]:
    try:
        return load_session(session_id)
    except FileNotFoundError:
        return create_session_record(
            session_id=session_id,
            model=model,
            working_directory=working_directory,
            approve_all=approve_all,
            default_plugin_id=default_plugin_id,
            allow_planned_plugin=allow_planned_plugin,
        )


def append_message(
    *,
    session_id: str,
    role: str,
    content: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    record = load_session(session_id)
    message = {
        "id": str(uuid.uuid4()),
        "role": role,
        "content": content,
        "createdAt": now_iso(),
        "metadata": metadata or {},
    }
    record.setdefault("messages", []).append(message)
    if record.get("title") == "New chat" and role == "user":
        compact = " ".join(content.strip().split())
        attachments = message["metadata"].get("attachments") or []
        if compact:
            record["title"] = compact[:60] + ("..." if len(compact) > 60 else "")
        elif attachments:
            artifact_name = str(attachments[0].get("name") or "artifact")
            record["title"] = f"Analyze {artifact_name}"[:60]
    record["updatedAt"] = message["createdAt"]
    save_session(record)
    return message


def touch_session(session_id: str) -> None:
    record = load_session(session_id)
    record["updatedAt"] = now_iso()
    save_session(record)


def set_session_favorite(session_id: str, favorite: bool) -> dict[str, Any]:
    record = load_session(session_id)
    record["favorite"] = bool(favorite)
    save_session(record)
    return record


def delete_session_record(session_id: str) -> dict[str, Any]:
    safe_id = safe_session_id(session_id)
    record_path = session_path(safe_id)
    if not record_path.exists():
        raise FileNotFoundError(safe_id)

    removed_directories: list[str] = []
    for name, root in (("uploads", UPLOADS_DIR), ("plugin_authoring", PLUGIN_AUTHORING_DIR)):
        directory = root / safe_id
        if directory.is_symlink():
            directory.unlink()
        elif directory.is_dir():
            shutil.rmtree(directory)
        else:
            continue
        removed_directories.append(name)
    record_path.unlink()
    return {"sessionId": safe_id, "removedDirectories": removed_directories}


def session_has_uploads(session_id: str) -> bool:
    directory = UPLOADS_DIR / safe_session_id(session_id)
    return directory.is_dir() and any(path.is_file() for path in directory.iterdir())


def session_preview(messages: list[dict[str, Any]], limit: int = 160) -> str:
    """Return a compact, stable topic preview from the first user turn."""
    for message in messages:
        if message.get("role") != "user":
            continue
        content = " ".join(str(message.get("content") or "").split())
        if content:
            return content[:limit] + ("..." if len(content) > limit else "")
        attachments = message.get("metadata", {}).get("attachments") or []
        if attachments:
            return f"Artifact analysis: {attachments[0].get('name') or 'artifact'}"
    return ""


def list_sessions() -> list[dict[str, Any]]:
    ensure_store_dir()
    sessions: list[dict[str, Any]] = []
    for path in CHAT_STORE_DIR.glob("*.json"):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        message_count = len(record.get("messages", []))
        if message_count == 0 and not session_has_uploads(str(record.get("sessionId") or "")):
            continue
        sessions.append(
            {
                "sessionId": record.get("sessionId"),
                "title": record.get("title", "New chat"),
                "model": record.get("model"),
                "workingDirectory": record.get("workingDirectory"),
                "defaultPluginId": record.get("defaultPluginId", "inflak-main"),
                "favorite": bool(record.get("favorite", False)),
                "createdAt": record.get("createdAt"),
                "updatedAt": record.get("updatedAt"),
                "messageCount": message_count,
                "preview": session_preview(record.get("messages", [])),
            }
        )
    return sorted(sessions, key=lambda item: item.get("updatedAt") or "", reverse=True)


def get_messages(session_id: str) -> list[dict[str, Any]]:
    return load_session(session_id).get("messages", [])


def pending_widget_request(session_id: str) -> dict[str, Any] | None:
    pending: dict[str, dict[str, Any]] = {}
    for message in get_messages(session_id):
        metadata = message.get("metadata") or {}
        if message.get("role") == "widget_request":
            widget_id = str(metadata.get("widgetId") or metadata.get("widget", {}).get("widget_id") or "")
            if widget_id:
                pending[widget_id] = message
        elif message.get("role") == "widget_return":
            result = metadata.get("result") or {}
            widget_id = str(metadata.get("widgetId") or result.get("widget_id") or "")
            pending.pop(widget_id, None)
    return next(reversed(pending.values()), None) if pending else None
