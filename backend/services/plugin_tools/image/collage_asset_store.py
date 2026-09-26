from __future__ import annotations

import json
import os
import re
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from backend.services import uploads_store


_LIBRARY_FILENAME = "collage-assets.json"
_ASSET_ID_RE = re.compile(r"[A-Za-z0-9_-]{1,80}")
_FILE_ID_RE = re.compile(r"[A-Za-z0-9]+")
_ROLES = {"character", "background", "accessory", "texture"}
_RELATIONS = {"central", "related"}
_STATUSES = {"candidate", "approved", "rejected", "failed"}
_LOCK = threading.Lock()


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _library_path(session_id: str) -> Path:
    return uploads_store.session_dir(session_id) / _LIBRARY_FILENAME


def _empty_library(session_id: str) -> dict[str, Any]:
    timestamp = _now_iso()
    return {
        "schema_version": "1.0",
        "artifact_type": "collage-asset-library",
        "session_id": session_id,
        "created_at": timestamp,
        "updated_at": timestamp,
        "assets": [],
    }


def _validate_file_id(session_id: str, file_id: Any, field_name: str, *, required: bool) -> str | None:
    if file_id in (None, ""):
        if required:
            raise ValueError(f"{field_name} is required.")
        return None
    value = str(file_id)
    if not _FILE_ID_RE.fullmatch(value) or uploads_store.upload_path(session_id, value) is None:
        raise ValueError(f"{field_name} must reference an existing upload in this session.")
    return value


def _normalise_asset(session_id: str, asset: dict[str, Any], *, existing: dict[str, Any] | None = None) -> dict[str, Any]:
    source_file_id = _validate_file_id(session_id, asset.get("source_file_id"), "source_file_id", required=True)
    cutout_file_id = _validate_file_id(session_id, asset.get("cutout_file_id"), "cutout_file_id", required=False)
    asset_id = str(asset.get("asset_id") or (existing or {}).get("asset_id") or uuid.uuid4().hex)
    if not _ASSET_ID_RE.fullmatch(asset_id):
        raise ValueError("asset_id must contain only letters, numbers, underscores, or hyphens.")
    label = str(asset.get("label") or (existing or {}).get("label") or "").strip()
    if not label:
        raise ValueError("label is required.")
    role = str(asset.get("role") or (existing or {}).get("role") or "accessory").lower()
    if role not in _ROLES:
        raise ValueError(f"role must be one of {sorted(_ROLES)}.")
    relation = str(asset.get("story_relation") or (existing or {}).get("story_relation") or "related").lower()
    if relation not in _RELATIONS:
        raise ValueError(f"story_relation must be one of {sorted(_RELATIONS)}.")
    status = str(asset.get("status") or (existing or {}).get("status") or "candidate").lower()
    if status not in _STATUSES:
        raise ValueError(f"status must be one of {sorted(_STATUSES)}.")
    if status == "approved" and not cutout_file_id:
        raise ValueError("approved assets require a cutout_file_id.")
    aliases = asset.get("aliases", (existing or {}).get("aliases", []))
    if not isinstance(aliases, list) or not all(isinstance(value, str) and value.strip() for value in aliases):
        raise ValueError("aliases must be a list of non-empty strings.")
    cluster_path = asset.get("cluster_path", (existing or {}).get("cluster_path", []))
    if not isinstance(cluster_path, list) or not all(isinstance(value, str) and value.strip() for value in cluster_path):
        raise ValueError("cluster_path must be a list of non-empty strings.")
    source_region = asset.get("source_region", (existing or {}).get("source_region"))
    if source_region is not None:
        if not isinstance(source_region, dict):
            raise ValueError("source_region must be an object when present.")
        try:
            source_region = {key: float(source_region[key]) for key in ("x", "y", "width", "height")}
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("source_region requires numeric x, y, width, and height.") from error
        if not 0 <= source_region["x"] <= 1 or not 0 <= source_region["y"] <= 1 or not 0 < source_region["width"] <= 1 or not 0 < source_region["height"] <= 1:
            raise ValueError("source_region must use normalized 0..1 coordinates with positive width and height.")
    created_at = (existing or {}).get("created_at") or _now_iso()
    return {
        "asset_id": asset_id,
        "source_file_id": source_file_id,
        "cutout_file_id": cutout_file_id,
        "label": label,
        "aliases": [value.strip() for value in aliases],
        "role": role,
        "story_relation": relation,
        "cluster_path": [value.strip() for value in cluster_path],
        "source_region": source_region,
        "extraction_prompt": str(asset.get("extraction_prompt") or (existing or {}).get("extraction_prompt") or "").strip(),
        "quality": str(asset.get("quality") or (existing or {}).get("quality") or "high"),
        "status": status,
        "failure_reason": str(asset.get("failure_reason") or "").strip() or None,
        "created_at": created_at,
        "updated_at": _now_iso(),
    }


def load_library(session_id: str) -> dict[str, Any]:
    path = _library_path(session_id)
    if not path.exists():
        return _empty_library(session_id)
    try:
        library = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise ValueError("The collage asset library is unreadable.") from error
    if library.get("artifact_type") != "collage-asset-library" or not isinstance(library.get("assets"), list):
        raise ValueError("The collage asset library has an invalid schema.")
    return library


def save_asset(session_id: str, asset: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Validate and atomically upsert one session-owned collage asset."""
    with _LOCK:
        library = load_library(session_id)
        existing_by_id = {entry.get("asset_id"): entry for entry in library["assets"] if isinstance(entry, dict)}
        asset_id = str(asset.get("asset_id") or "")
        existing = existing_by_id.get(asset_id) if asset_id else None
        normalised = _normalise_asset(session_id, asset, existing=existing)
        if existing:
            library["assets"] = [normalised if entry.get("asset_id") == normalised["asset_id"] else entry for entry in library["assets"]]
        else:
            library["assets"].append(normalised)
        library["updated_at"] = _now_iso()
        path = _library_path(session_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(library, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(temporary, path)
    return normalised, library
