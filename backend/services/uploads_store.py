from __future__ import annotations

import mimetypes
import re
import uuid
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from backend.services.chat_store import safe_session_id

PROJECT_DIR = Path(__file__).resolve().parents[2]
UPLOADS_DIR = PROJECT_DIR / "data" / "uploads"
COPILOT_SESSION_STATE_DIR = Path.home() / ".copilot" / "session-state"

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB per file

# Allowlisted MIME types: images for vision + documents/text as material.
ALLOWED_MIME_PREFIXES = ("image/",)
ALLOWED_MIME_TYPES = {
    "text/plain",
    "text/x-python",
    "text/x-python-script",
    "text/markdown",
    "text/html",
    "application/x-yaml",
    "application/yaml",
    "text/csv",
    "application/json",
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}

FALLBACK_MIME_TYPES = {
    ".htm": "text/html",
    ".html": "text/html",
    ".md": "text/markdown",
    ".py": "text/x-python",
    ".yaml": "application/yaml",
    ".yml": "application/yaml",
}


class UploadTooLargeError(ValueError):
    pass


class UploadTypeNotAllowedError(ValueError):
    pass


def is_allowed_mime(mime: str) -> bool:
    return mime in ALLOWED_MIME_TYPES or mime.startswith(ALLOWED_MIME_PREFIXES)


def infer_mime(filename: str) -> str | None:
    return mimetypes.guess_type(filename)[0] or FALLBACK_MIME_TYPES.get(Path(filename).suffix.lower())


def session_dir(session_id: str) -> Path:
    return UPLOADS_DIR / safe_session_id(session_id)


def _sanitize_name(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]", "_", (name or "").strip())[-120:]
    return cleaned or "upload.bin"


def save_upload(*, session_id: str, filename: str, content: bytes, mime: str | None) -> dict[str, Any]:
    guessed_mime = infer_mime(filename)
    resolved_mime = guessed_mime if mime in {None, "", "application/octet-stream"} and guessed_mime else mime or guessed_mime or "application/octet-stream"
    if not is_allowed_mime(resolved_mime):
        raise UploadTypeNotAllowedError(resolved_mime)
    if len(content) > MAX_UPLOAD_BYTES:
        raise UploadTooLargeError(filename)

    file_id = uuid.uuid4().hex
    safe_name = _sanitize_name(filename)
    target_dir = session_dir(session_id)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{file_id}-{safe_name}"
    target.write_bytes(content)
    return {
        "fileId": file_id,
        "name": safe_name,
        "mime": resolved_mime,
        "size": len(content),
        "path": str(target.resolve()),
    }


def save_generated_artifact(*, session_id: str, filename: str, content: str, mime: str) -> dict[str, Any]:
    """Persist a server-generated text artifact through the same safe session store."""
    return save_upload(
        session_id=session_id,
        filename=filename,
        content=content.encode("utf-8"),
        mime=mime,
    )


def list_uploads(session_id: str) -> list[dict[str, Any]]:
    directory = session_dir(session_id)
    if not directory.exists():
        return []
    uploads: list[dict[str, Any]] = []
    for path in sorted(directory.iterdir(), key=lambda item: item.stat().st_mtime):
        if not path.is_file() or "-" not in path.name:
            continue
        file_id, name = path.name.split("-", 1)
        if not re.fullmatch(r"[A-Za-z0-9]+", file_id):
            continue
        uploads.append({
            "fileId": file_id,
            "name": name,
            "mime": infer_mime(name) or "application/octet-stream",
            "size": path.stat().st_size,
        })
    return uploads


def upload_path(session_id: str, file_id: str) -> Path | None:
    if not re.fullmatch(r"[A-Za-z0-9]+", file_id):
        return None
    directory = session_dir(session_id)
    if not directory.exists():
        return None
    for candidate in directory.glob(f"{file_id}-*"):
        if candidate.is_file():
            return candidate
    return None


def runtime_files_dir(session_id: str) -> Path:
    return COPILOT_SESSION_STATE_DIR / safe_session_id(session_id) / "files"


def runtime_image_path(session_id: str, value: str) -> Path | None:
    """Resolve an image inside this Copilot session's runtime files directory."""
    root = runtime_files_dir(session_id).resolve()
    raw_value = str(value or "").strip()
    if not raw_value:
        return None
    if raw_value.startswith("file:"):
        raw_value = unquote(urlparse(raw_value).path)
    candidate = Path(raw_value).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        return None
    mime = mimetypes.guess_type(resolved.name)[0] or ""
    return resolved if resolved.is_file() and mime.startswith("image/") else None


def runtime_image_relative_path(session_id: str, value: str) -> str | None:
    path = runtime_image_path(session_id, value)
    if path is None:
        return None
    return path.relative_to(runtime_files_dir(session_id).resolve()).as_posix()


def list_runtime_images(session_id: str) -> list[Path]:
    root = runtime_files_dir(session_id)
    if not root.exists():
        return []
    return [
        path.resolve()
        for path in root.rglob("*")
        if path.is_file() and runtime_image_path(session_id, str(path)) is not None
    ]
