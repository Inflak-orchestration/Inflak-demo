from __future__ import annotations

import base64
import json
import os
import re
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from backend.services import uploads_store
from backend.services.plugin_tools.svg import accessibility as svg_accessibility
from backend.services.plugin_tools.svg import collage as svg_collage


SVG_NS = "http://www.w3.org/2000/svg"
SCENE_METADATA_ID = "inflak-svg-scene"
LEGACY_COLLAGE_METADATA_ID = "inflak-collage-scene"
REVISION_ATTRIBUTE = "data-inflak-revision"
DOCUMENT_ID_ATTRIBUTE = "data-inflak-document-id"
MAX_ELEMENTS = 5000
MAX_DEPTH = 64
OBJECT_TAGS = frozenset({"text", "rect", "circle", "ellipse", "line", "polyline", "polygon", "path", "g", "use", "image"})
SAFE_ATTRIBUTES = frozenset({
    "fill", "stroke", "stroke-width", "font-size", "font-weight", "opacity",
    "x", "y", "x1", "y1", "x2", "y2", "cx", "cy", "r", "rx", "ry",
    "width", "height", "role", "aria-label", "aria-labelledby", "visibility",
})
ID_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_.:-]{0,127}")


class SvgDocumentError(ValueError):
    pass


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _safe_root(content: bytes) -> ET.Element:
    lowered = content.lower()
    if b"<!doctype" in lowered or b"<!entity" in lowered:
        raise SvgDocumentError("SVG document types and entities are not supported.")
    try:
        root = ET.fromstring(content)
    except ET.ParseError as error:
        raise SvgDocumentError("Invalid SVG document.") from error
    if _local_name(root.tag) != "svg":
        raise SvgDocumentError("Uploaded artifact is not an SVG document.")
    elements = list(root.iter())
    if len(elements) > MAX_ELEMENTS:
        raise SvgDocumentError(f"SVG supports at most {MAX_ELEMENTS} elements.")
    parent_map = {child: parent for parent in elements for child in parent}
    for element in elements:
        depth = 0
        parent = parent_map.get(element)
        while parent is not None:
            depth += 1
            parent = parent_map.get(parent)
        if depth > MAX_DEPTH:
            raise SvgDocumentError(f"SVG nesting depth exceeds {MAX_DEPTH}.")
        tag = _local_name(element.tag)
        if tag in {"script", "foreignObject"}:
            raise SvgDocumentError(f"Unsafe SVG element is not supported: {tag}.")
        for attribute, value in element.attrib.items():
            name = _local_name(attribute).lower()
            text = str(value).strip()
            if name.startswith("on"):
                raise SvgDocumentError("SVG event-handler attributes are not supported.")
            if name == "href" and text and not text.startswith(("#", "data:image/")):
                raise SvgDocumentError("External SVG references are not supported.")
            if name == "style" and "url(" in text.lower() and "url(#" not in text.lower():
                raise SvgDocumentError("External CSS references are not supported.")
    return root


def _atomic_write(path: Path, content: bytes) -> None:
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as temporary:
            temporary.write(content)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_name, path)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)


def _legacy_manifest(root: ET.Element) -> dict[str, Any] | None:
    metadata = root.find(f"{{{SVG_NS}}}metadata[@id='{LEGACY_COLLAGE_METADATA_ID}']")
    if metadata is None or not metadata.text:
        return None
    try:
        value = json.loads(metadata.text)
    except json.JSONDecodeError as error:
        raise SvgDocumentError("Legacy collage metadata is invalid.") from error
    return value if isinstance(value, dict) else None


def _existing_manifest(root: ET.Element) -> dict[str, Any] | None:
    metadata = root.find(f"{{{SVG_NS}}}metadata[@id='{SCENE_METADATA_ID}']")
    if metadata is None or not metadata.text:
        return None
    try:
        value = json.loads(metadata.text)
    except json.JSONDecodeError as error:
        raise SvgDocumentError("SVG scene metadata is invalid.") from error
    return value if isinstance(value, dict) else None


def _normalize_ids(root: ET.Element) -> None:
    used: set[str] = set()
    counters: dict[str, int] = {}
    for element in root.iter():
        tag = _local_name(element.tag)
        if tag not in OBJECT_TAGS:
            continue
        raw_id = str(element.get("id") or "")
        if ID_PATTERN.fullmatch(raw_id) and raw_id not in used:
            object_id = raw_id
        else:
            counters[tag] = counters.get(tag, 0) + 1
            object_id = f"svgobj-{tag}-{counters[tag]:04d}"
            while object_id in used:
                counters[tag] += 1
                object_id = f"svgobj-{tag}-{counters[tag]:04d}"
            element.set("id", object_id)
        used.add(object_id)


def _revision(root: ET.Element, existing: dict[str, Any] | None, legacy: dict[str, Any] | None) -> int:
    candidates = (
        root.get(REVISION_ATTRIBUTE),
        existing.get("revision") if existing else None,
        legacy.get("revision") if legacy else None,
        root.get("data-revision"),
        root.get(svg_accessibility.REVISION_ATTRIBUTE),
        1,
    )
    revisions = []
    for candidate in candidates:
        try:
            value = int(candidate)
        except (TypeError, ValueError):
            continue
        if value > 0:
            revisions.append(value)
    return max(revisions, default=1)


def _scene_kind(existing: dict[str, Any] | None, legacy: dict[str, Any] | None, hint: str | None) -> str:
    requested = str(hint or "").strip().lower()
    if requested in {"general", "collage", "diagram", "chart", "illustration"}:
        return requested
    if existing and existing.get("scene_kind") in {"general", "collage", "diagram", "chart", "illustration"}:
        return str(existing["scene_kind"])
    return "collage" if legacy else "general"


def _capabilities(tag: str) -> dict[str, bool]:
    return {
        "inspect": True,
        "text": tag == "text",
        "style": tag in OBJECT_TAGS,
        "transform": tag in OBJECT_TAGS,
        "geometry": tag in {"rect", "circle", "ellipse", "line", "polyline", "polygon"},
        "reorder": tag in OBJECT_TAGS,
        "remove": tag in OBJECT_TAGS,
        "replace_asset": tag == "image",
    }


def _manifest_from_report(
    root: ET.Element,
    report: dict[str, Any],
    *,
    document_id: str,
    revision: int,
    scene_kind: str,
    source_kind: str,
    authoring_bundle: dict[str, Any] | None = None,
) -> dict[str, Any]:
    objects = []
    for item in report.get("objects", []):
        tag = str(item.get("tag") or "")
        capabilities = _capabilities(tag)
        locked_reasons = {}
        if not capabilities["geometry"]:
            locked_reasons["geometry"] = "Direct geometry editing is not supported for this SVG element."
        objects.append({
            "id": item["object_id"],
            "tag": tag,
            "type": "text" if tag == "text" else "image" if tag == "image" else "group" if tag == "g" else "graphic",
            "role": item.get("role_candidate", "unknown"),
            "label": item.get("text_content") or item.get("source_id") or tag or item["object_id"],
            "parent_id": item.get("parent_object_id", ""),
            "dom_order": item.get("dom_order", 0),
            "z_order": item.get("z_order", 0),
            "bbox": item.get("bbox"),
            "presentation": {
                "fill": item.get("fill", "none"),
                "stroke": item.get("stroke", "none"),
                "stroke_width": item.get("stroke_width"),
                "opacity": item.get("opacity", 1),
            },
            "capabilities": capabilities,
            "locked_reasons": locked_reasons,
            "provenance": {"id": "preserved_or_assigned_by_manager", "scene": "confirmed_from_svg"},
        })
    viewport = report.get("viewport", {})
    manifest = {
        "schema_version": "2.0",
        "artifact_type": "svg-document",
        "scene_kind": scene_kind,
        "document_id": document_id,
        "revision": revision,
        "source": {"kind": source_kind},
        "canvas": {
            "view_box": viewport.get("view_box", []),
            "width": viewport.get("width", ""),
            "height": viewport.get("height", ""),
            "background": "transparent",
        },
        "objects": objects,
        "normalization": {"normalizer_version": "2.0"},
        "limitations": report.get("limitations", []),
    }
    if authoring_bundle:
        manifest["authoring_bundle"] = authoring_bundle
    return manifest


def _serialize_with_manifest(root: ET.Element, manifest: dict[str, Any]) -> bytes:
    metadata = root.find(f"{{{SVG_NS}}}metadata[@id='{SCENE_METADATA_ID}']")
    if metadata is None:
        metadata = ET.Element(f"{{{SVG_NS}}}metadata", {"id": SCENE_METADATA_ID})
        root.insert(0, metadata)
    metadata.text = json.dumps(manifest, separators=(",", ":"))
    root.set(DOCUMENT_ID_ATTRIBUTE, manifest["document_id"])
    root.set(REVISION_ATTRIBUTE, str(manifest["revision"]))
    root.set("data-revision", str(manifest["revision"]))
    root.set(svg_accessibility.REVISION_ATTRIBUTE, str(manifest["revision"]))
    legacy_metadata = root.find(f"{{{SVG_NS}}}metadata[@id='{LEGACY_COLLAGE_METADATA_ID}']")
    if legacy_metadata is not None and legacy_metadata.text:
        legacy_manifest = json.loads(legacy_metadata.text)
        if isinstance(legacy_manifest, dict):
            legacy_manifest["revision"] = manifest["revision"]
            legacy_metadata.text = json.dumps(legacy_manifest, separators=(",", ":"))
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def normalize_document(
    path: Path,
    *,
    document_id: str,
    scene_kind_hint: str | None = None,
    source_kind: str = "upload",
    persist: bool = True,
) -> dict[str, Any]:
    ET.register_namespace("", SVG_NS)
    root = _safe_root(path.read_bytes())
    existing = _existing_manifest(root)
    legacy = _legacy_manifest(root)
    _normalize_ids(root)
    revision = _revision(root, existing, legacy)
    scene_kind = _scene_kind(existing, legacy, scene_kind_hint)
    root.set(REVISION_ATTRIBUTE, str(revision))
    root.set(svg_accessibility.REVISION_ATTRIBUTE, str(revision))
    provisional = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as temporary:
        temporary.write(provisional)
        temporary_path = Path(temporary.name)
    try:
        report = svg_accessibility.inspect_svg(temporary_path)
    except svg_accessibility.SvgAccessibilityError as error:
        raise SvgDocumentError(str(error)) from error
    finally:
        temporary_path.unlink(missing_ok=True)
    manifest = _manifest_from_report(
        root,
        report,
        document_id=str((existing or {}).get("document_id") or document_id),
        revision=revision,
        scene_kind=scene_kind,
        source_kind=str((existing or {}).get("source", {}).get("kind") or source_kind),
        authoring_bundle=(existing or legacy or {}).get("authoring_bundle"),
    )
    content = _serialize_with_manifest(root, manifest)
    if persist:
        _atomic_write(path, content)
    return manifest


def inspect_document(path: Path, *, document_id: str, persist_normalization: bool = True) -> dict[str, Any]:
    return normalize_document(path, document_id=document_id, persist=persist_normalization)


def validate_document(path: Path, *, document_id: str) -> dict[str, Any]:
    manifest = normalize_document(path, document_id=document_id, persist=False)
    return {"valid": True, "scene": manifest}


def _find_object(root: ET.Element, object_id: str) -> ET.Element | None:
    return next((element for element in root.iter() if element.get("id") == object_id), None)


def _embed_session_asset(session_id: str, file_id: str) -> str:
    path = uploads_store.upload_path(session_id, file_id)
    if path is None:
        raise SvgDocumentError(f"Unknown session asset fileId: {file_id}.")
    mime = uploads_store.mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    if not mime.startswith("image/") or mime == "image/svg+xml":
        raise SvgDocumentError("Replacement assets must be raster images.")
    try:
        data_uri, _mime = svg_collage._asset_data_uri(session_id, file_id)
    except svg_collage.SvgCollageError as error:
        raise SvgDocumentError(str(error)) from error
    return data_uri


def _apply_generic_operations(root: ET.Element, operations: list[dict[str, Any]], session_id: str) -> None:
    if not operations or len(operations) > 100:
        raise SvgDocumentError("A patch requires between 1 and 100 operations.")
    parent_map = {child: parent for parent in root.iter() for child in parent}
    for operation in operations:
        if not isinstance(operation, dict):
            raise SvgDocumentError("Every patch operation must be an object.")
        operation_name = str(operation.get("op") or "")
        object_id = str(operation.get("object_id") or "")
        before_operation = ET.tostring(root, encoding="utf-8")
        if operation_name == "add_cutout":
            if not ID_PATTERN.fullmatch(object_id) or _find_object(root, object_id) is not None:
                raise SvgDocumentError("add_cutout requires a unique valid object_id.")
            try:
                x = float(operation["x"])
                y = float(operation["y"])
                width = float(operation["width"])
                height = float(operation["height"])
            except (KeyError, TypeError, ValueError) as error:
                raise SvgDocumentError("add_cutout requires numeric x, y, width, and height.") from error
            if width <= 0 or height <= 0:
                raise SvgDocumentError("add_cutout width and height must be positive.")
            element = ET.SubElement(root, f"{{{SVG_NS}}}image", {
                "id": object_id,
                "x": str(x),
                "y": str(y),
                "width": str(width),
                "height": str(height),
                "href": _embed_session_asset(session_id, str(operation.get("asset_file_id") or "")),
                "aria-label": str(operation.get("label") or object_id)[:500],
            })
            parent_map[element] = root
            if ET.tostring(root, encoding="utf-8") == before_operation:
                raise SvgDocumentError(f"SVG operation {operation_name} on {object_id} has no effect.")
            continue
        element = _find_object(root, object_id)
        if element is None:
            raise SvgDocumentError(f"Unknown SVG object: {object_id}.")
        tag = _local_name(element.tag)
        if operation_name == "set_object_style":
            style = operation.get("style")
            if not isinstance(style, dict) or not style:
                raise SvgDocumentError("set_object_style requires a non-empty style object.")
            allowed = {"fill", "stroke", "stroke_width", "opacity"}
            if set(style) - allowed:
                raise SvgDocumentError("set_object_style contains unsupported style properties.")
            style_changes = any(
                (
                    name in {"fill", "stroke"}
                    and str(value).strip() != str(element.get(name) or "").strip()
                )
                or (
                    name == "stroke_width"
                    and float(value) != float(element.get("stroke-width") or 1)
                )
                or (
                    name == "opacity"
                    and float(value) != float(element.get("opacity") or 1)
                )
                for name, value in style.items()
            )
            if not style_changes:
                raise SvgDocumentError(f"SVG operation {operation_name} on {object_id} has no effect.")
            for name in ("fill", "stroke"):
                if name in style:
                    value = str(style[name]).strip()
                    if not value or len(value) > 128 or "url(" in value.lower():
                        raise SvgDocumentError(f"set_object_style contains an unsupported {name} value.")
                    element.set(name, value)
            if "stroke_width" in style:
                stroke_width = float(style["stroke_width"])
                if stroke_width < 0 or stroke_width > 1000:
                    raise SvgDocumentError("set_object_style stroke_width must be between 0 and 1000.")
                element.set("stroke-width", str(stroke_width))
            if "opacity" in style:
                opacity = float(style["opacity"])
                if opacity < 0 or opacity > 1:
                    raise SvgDocumentError("set_object_style opacity must be between 0 and 1.")
                element.set("opacity", str(opacity))
        elif operation_name == "set_attributes":
            attributes = operation.get("attributes")
            if not isinstance(attributes, dict) or not attributes or set(attributes) - SAFE_ATTRIBUTES:
                raise SvgDocumentError("set_attributes contains unsupported SVG attributes.")
            for name, value in attributes.items():
                element.set(name, str(value))
        elif operation_name in {"set_text", "update_text"}:
            if tag != "text":
                raise SvgDocumentError("Text operations apply only to text elements.")
            element.text = str(operation.get("text") or "")[:5000]
            style = operation.get("style") if isinstance(operation.get("style"), dict) else {}
            for name in ("fill", "font-size", "font-weight"):
                if name.replace("-", "_") in style:
                    element.set(name, str(style[name.replace("-", "_")]))
                elif name in style:
                    element.set(name, str(style[name]))
        elif operation_name == "set_transform":
            translate = operation.get("translate") if isinstance(operation.get("translate"), dict) else {}
            scale = operation.get("scale") if isinstance(operation.get("scale"), dict) else {}
            x = float(translate.get("x", operation.get("x", 0)))
            y = float(translate.get("y", operation.get("y", 0)))
            scale_x = float(scale.get("x", 1))
            scale_y = float(scale.get("y", scale_x))
            rotation = float(operation.get("rotate", operation.get("rotation", 0)))
            element.set("transform", f"translate({x} {y}) rotate({rotation}) scale({scale_x} {scale_y})")
            for name in ("width", "height"):
                if name in operation and tag in {"image", "rect"}:
                    element.set(name, str(float(operation[name])))
        elif operation_name in {"remove_element", "remove_object"}:
            parent = parent_map.get(element)
            if parent is None:
                raise SvgDocumentError("The SVG root cannot be removed.")
            parent.remove(element)
        elif operation_name in {"replace_asset", "replace_cutout_asset"}:
            if tag != "image":
                raise SvgDocumentError("replace_asset applies only to image elements.")
            element.set("href", _embed_session_asset(session_id, str(operation.get("asset_file_id") or "")))
        elif operation_name in {"set_order", "set_dom_order"}:
            parent = parent_map.get(element)
            if parent is None:
                raise SvgDocumentError("The SVG root cannot be reordered.")
            siblings = list(parent)
            current = siblings.index(element)
            direction = str(operation.get("direction") or "front")
            target = {"front": len(siblings) - 1, "back": 0, "forward": min(len(siblings) - 1, current + 1), "backward": max(0, current - 1)}.get(direction)
            if target is None:
                raise SvgDocumentError("Unsupported order direction.")
            parent.remove(element)
            parent.insert(target, element)
        else:
            raise SvgDocumentError(f"Unsupported SVG document operation: {operation_name}.")
        if ET.tostring(root, encoding="utf-8") == before_operation:
            raise SvgDocumentError(f"SVG operation {operation_name} on {object_id} has no effect.")


def patch_document(
    path: Path,
    *,
    document_id: str,
    session_id: str,
    base_revision: int,
    operations: list[dict[str, Any]],
) -> dict[str, Any]:
    current = normalize_document(path, document_id=document_id, persist=True)
    if current["revision"] != base_revision:
        raise SvgDocumentError(f"Revision conflict: expected {base_revision}, current revision is {current['revision']}.")
    operation_names = {str(item.get("op") or "") for item in operations if isinstance(item, dict)}
    legacy = _legacy_manifest(_safe_root(path.read_bytes()))
    legacy_operations = {"set_transform", "set_order", "add_text", "update_text", "add_cutout", "replace_cutout_asset", "remove_object", "set_canvas_style"}
    if legacy and operation_names and operation_names <= legacy_operations:
        try:
            svg_collage.apply_svg_collage_patch(path, base_revision, operations, session_id=session_id)
        except svg_collage.SvgCollageError as error:
            raise SvgDocumentError(str(error)) from error
    else:
        root = _safe_root(path.read_bytes())
        _apply_generic_operations(root, operations, session_id)
        next_revision = base_revision + 1
        root.set(REVISION_ATTRIBUTE, str(next_revision))
        root.set(svg_accessibility.REVISION_ATTRIBUTE, str(next_revision))
        existing = _existing_manifest(root) or {}
        existing["revision"] = next_revision
        content = _serialize_with_manifest(root, existing)
        candidate = path.with_name(f".{path.name}.candidate")
        candidate.write_bytes(content)
        try:
            normalize_document(candidate, document_id=document_id, persist=True)
            _atomic_write(path, candidate.read_bytes())
        finally:
            candidate.unlink(missing_ok=True)
    scene = normalize_document(path, document_id=document_id, persist=True)
    return {"revision": scene["revision"], "scene": scene, "applied_operations": operations}


def manage_document(
    path: Path,
    *,
    action: str,
    document_id: str,
    session_id: str,
    scene_kind_hint: str | None = None,
    base_revision: int | None = None,
    operations: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if action == "validate":
        return {"action": "svg_document_validated", **validate_document(path, document_id=document_id)}
    if action in {"import", "adopt_generated"}:
        scene = normalize_document(
            path,
            document_id=document_id,
            scene_kind_hint=scene_kind_hint,
            source_kind="generated" if action == "adopt_generated" else "upload",
            persist=True,
        )
        return {"action": "svg_document_managed", "scene": scene}
    if action == "inspect":
        return {"action": "svg_document_inspected", "scene": inspect_document(path, document_id=document_id)}
    if action == "patch":
        if base_revision is None:
            raise SvgDocumentError("patch requires base_revision.")
        return {
            "action": "svg_document_patched",
            **patch_document(
                path,
                document_id=document_id,
                session_id=session_id,
                base_revision=base_revision,
                operations=operations or [],
            ),
        }
    raise SvgDocumentError(f"Unsupported SVG document action: {action}.")