from __future__ import annotations

import base64
import html
import io
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from backend.services import uploads_store
from backend.services.execution_tools import svg_accessibility


SVG_NS = "http://www.w3.org/2000/svg"
SCENE_METADATA_ID = "inflak-collage-scene"
OBJECT_ID_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_.:-]{0,127}")
SAFE_COLORS = re.compile(r"(?:#[0-9A-Fa-f]{3,8}|[A-Za-z]{1,24}|none)")
SAFE_FONTS = {"Arial", "Georgia", "Helvetica", "Impact", "Times New Roman", "Verdana"}
MAX_OBJECTS = 32
MAX_STYLE_PRESETS = 4
MAX_ASSET_CANDIDATES = 3
MAX_ADDABLE_ELEMENTS = 3
MAX_TEXT_OPTIONS = 4
AUTHORING_PREPARATION_TOOLS = {
    "generate_image",
    "edit_image",
    "restyle_image",
    "outpaint_image",
    "remove_background",
    "replace_background",
    "generate_variations",
    "transform_image",
    "adjust_image",
    "apply_filter",
    "extract_collage_cutouts",
}
AUTHORING_CANDIDATE_KINDS = {
    "generated",
    "restyle",
    "semantic_edit",
    "outpaint",
    "variation",
    "background_treatment",
    "transform",
    "appearance",
    "new_element",
}


class SvgCollageError(ValueError):
    pass


def _number(value: Any, *, minimum: float, maximum: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise SvgCollageError(f"Expected a number, got {value!r}.") from error
    return min(maximum, max(minimum, number))


def _object_id(value: Any) -> str:
    object_id = str(value or "")
    if not OBJECT_ID_PATTERN.fullmatch(object_id):
        raise SvgCollageError(f"Invalid collage object id: {object_id!r}.")
    return object_id


def _color(value: Any, default: str) -> str:
    color = str(value or default)
    if not SAFE_COLORS.fullmatch(color):
        raise SvgCollageError(f"Unsupported color: {color!r}.")
    return color


def _transform(layer: dict[str, Any], canvas_width: int, canvas_height: int) -> dict[str, float]:
    return {
        "x": _number(layer.get("x", 0), minimum=-canvas_width, maximum=canvas_width * 2),
        "y": _number(layer.get("y", 0), minimum=-canvas_height, maximum=canvas_height * 2),
        "width": _number(layer.get("width", canvas_width / 3), minimum=1, maximum=canvas_width * 2),
        "height": _number(layer.get("height", canvas_height / 3), minimum=1, maximum=canvas_height * 2),
        "rotation": _number(layer.get("rotation", 0), minimum=-360, maximum=360),
    }


def _asset_data_uri(session_id: str, file_id: str) -> tuple[str, str]:
    path = uploads_store.upload_path(session_id, file_id)
    if path is None:
        raise SvgCollageError(f"Unknown session asset fileId: {file_id}.")
    mime = uploads_store.mimetypes.guess_type(path.name)[0] or "image/png"
    if not mime.startswith("image/") or mime == "image/svg+xml":
        raise SvgCollageError(f"Collage cutout {file_id} must be a raster image.")
    content = path.read_bytes()
    try:
        from PIL import Image

        with Image.open(io.BytesIO(content)) as image:
            if "A" not in image.getbands() or image.getchannel("A").getextrema()[0] == 255:
                raise SvgCollageError(f"Collage cutout {file_id} must have actual transparent background pixels.")
    except SvgCollageError:
        raise
    except Exception as error:  # noqa: BLE001
        raise SvgCollageError(f"Collage cutout {file_id} must be a decodable image with transparent background.") from error
    encoded = base64.b64encode(content).decode("ascii")
    return f"data:{mime};base64,{encoded}", mime


def _authoring_asset_file_id(session_id: str, value: Any) -> str:
    file_id = str(value or "")
    _asset_data_uri(session_id, file_id)
    return file_id


def _authoring_source_tool(value: Any, default: str = "generate_image") -> str:
    source_tool = str(value or default)
    if source_tool not in AUTHORING_PREPARATION_TOOLS:
        raise SvgCollageError(f"Unsupported authoring preparation tool: {source_tool}.")
    return source_tool


def _authoring_candidate_kind(value: Any, default: str = "generated") -> str:
    kind = str(value or default)
    if kind not in AUTHORING_CANDIDATE_KINDS:
        raise SvgCollageError(f"Unsupported authoring candidate kind: {kind}.")
    return kind


def _normalize_authoring_bundle(
    session_id: str,
    raw_bundle: Any,
    objects: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if raw_bundle is None:
        return None
    if not isinstance(raw_bundle, dict):
        raise SvgCollageError("authoring_bundle must be an object.")
    by_id = {item["id"]: item for item in objects}

    raw_candidates = raw_bundle.get("asset_candidates_by_object", {})
    if not isinstance(raw_candidates, dict):
        raise SvgCollageError("asset_candidates_by_object must be an object keyed by cutout id.")
    candidates_by_object: dict[str, list[dict[str, str]]] = {}
    for object_id, raw_items in raw_candidates.items():
        item = by_id.get(str(object_id))
        if item is None or item.get("type") != "cutout":
            raise SvgCollageError(f"Asset candidates require a known cutout object: {object_id}.")
        if not isinstance(raw_items, list) or not 1 <= len(raw_items) <= MAX_ASSET_CANDIDATES:
            raise SvgCollageError(f"Asset candidates for {object_id} require 1-{MAX_ASSET_CANDIDATES} items.")
        normalized_candidates = []
        candidate_file_ids: set[str] = set()
        for index, candidate in enumerate(raw_items):
            if not isinstance(candidate, dict):
                raise SvgCollageError(f"Every asset candidate for {object_id} must be an object.")
            file_id = _authoring_asset_file_id(session_id, candidate.get("fileId") or candidate.get("asset_file_id"))
            if file_id == item.get("asset_file_id"):
                raise SvgCollageError(f"Asset candidate for {object_id} must differ from its current asset.")
            if file_id in candidate_file_ids:
                raise SvgCollageError(f"Asset candidates for {object_id} must use unique fileIds.")
            candidate_file_ids.add(file_id)
            normalized_candidates.append({
                "id": str(candidate.get("id") or f"{object_id}-candidate-{index + 1}")[:128],
                "label": str(candidate.get("label") or f"Option {index + 1}")[:160],
                "rationale": str(candidate.get("rationale") or "")[:300],
                "fileId": file_id,
                "kind": _authoring_candidate_kind(candidate.get("kind")),
                "source_tool": _authoring_source_tool(candidate.get("source_tool")),
                "source_file_id": str(candidate.get("source_file_id") or item.get("asset_file_id") or "")[:128],
            })
        candidates_by_object[str(object_id)] = normalized_candidates
    missing_candidate_ids = [item["id"] for item in objects if item.get("type") == "cutout" and item["id"] not in candidates_by_object]
    if missing_candidate_ids:
        raise SvgCollageError(
            "Every cutout requires 1-3 pre-generated replacement candidates before composition: "
            + ", ".join(missing_candidate_ids)
            + "."
        )

    raw_addable_elements = raw_bundle.get("addable_elements", [])
    if not isinstance(raw_addable_elements, list) or len(raw_addable_elements) > MAX_ADDABLE_ELEMENTS:
        raise SvgCollageError(f"addable_elements support at most {MAX_ADDABLE_ELEMENTS} items.")
    addable_elements = []
    addable_object_ids: set[str] = set()
    for index, candidate in enumerate(raw_addable_elements):
        if not isinstance(candidate, dict):
            raise SvgCollageError("Every addable element must be an object.")
        object_id = _object_id(candidate.get("object_id") or candidate.get("id") or f"new-element-{index + 1}")
        if object_id in by_id or object_id in addable_object_ids:
            raise SvgCollageError(f"Addable element object id must be new and unique: {object_id}.")
        addable_object_ids.add(object_id)
        transform = candidate.get("default_transform") if isinstance(candidate.get("default_transform"), dict) else {}
        addable_elements.append({
            "id": str(candidate.get("id") or object_id)[:128],
            "object_id": object_id,
            "label": str(candidate.get("label") or f"Element {index + 1}")[:160],
            "rationale": str(candidate.get("rationale") or "")[:300],
            "fileId": _authoring_asset_file_id(session_id, candidate.get("fileId") or candidate.get("asset_file_id")),
            "kind": _authoring_candidate_kind(candidate.get("kind"), "new_element"),
            "source_tool": _authoring_source_tool(candidate.get("source_tool")),
            "default_transform": {
                "x": _number(transform.get("x", 80), minimum=-8192, maximum=8192),
                "y": _number(transform.get("y", 80), minimum=-8192, maximum=8192),
                "width": _number(transform.get("width", 320), minimum=1, maximum=8192),
                "height": _number(transform.get("height", 320), minimum=1, maximum=8192),
                "rotation": _number(transform.get("rotation", 0), minimum=-360, maximum=360),
            },
        })

    raw_text_options = raw_bundle.get("text_authoring_options", {})
    if not isinstance(raw_text_options, dict):
        raise SvgCollageError("text_authoring_options must be an object keyed by text id.")
    text_options: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for object_id, raw_options in raw_text_options.items():
        item = by_id.get(str(object_id))
        if item is None or item.get("type") != "text" or not isinstance(raw_options, dict):
            raise SvgCollageError(f"Text authoring options require a known text object: {object_id}.")
        raw_copy = raw_options.get("copy_options", [])
        raw_typography = raw_options.get("typography_presets", [])
        if not isinstance(raw_copy, list) or len(raw_copy) > MAX_TEXT_OPTIONS:
            raise SvgCollageError(f"Copy options for {object_id} support at most {MAX_TEXT_OPTIONS} items.")
        if not isinstance(raw_typography, list) or len(raw_typography) > MAX_TEXT_OPTIONS:
            raise SvgCollageError(f"Typography presets for {object_id} support at most {MAX_TEXT_OPTIONS} items.")
        copy_options = []
        for index, option in enumerate(raw_copy):
            if not isinstance(option, dict):
                raise SvgCollageError(f"Every copy option for {object_id} must be an object.")
            copy_options.append({
                "id": str(option.get("id") or f"{object_id}-copy-{index + 1}")[:128],
                "label": str(option.get("label") or f"Copy {index + 1}")[:160],
                "text": str(option.get("text") or "")[:500],
            })
        typography_presets = []
        for index, option in enumerate(raw_typography):
            if not isinstance(option, dict):
                raise SvgCollageError(f"Every typography preset for {object_id} must be an object.")
            style = option.get("style") if isinstance(option.get("style"), dict) else {}
            font_family = str(style.get("font_family") or item["style"]["font_family"])
            if font_family not in SAFE_FONTS:
                raise SvgCollageError(f"Unsupported font family: {font_family!r}.")
            typography_presets.append({
                "id": str(option.get("id") or f"{object_id}-type-{index + 1}")[:128],
                "label": str(option.get("label") or f"Typography {index + 1}")[:160],
                "style": {
                    "font_family": font_family,
                    "font_size": _number(style.get("font_size", item["style"]["font_size"]), minimum=8, maximum=512),
                    "font_weight": int(_number(style.get("font_weight", item["style"]["font_weight"]), minimum=100, maximum=900)),
                    "fill": _color(style.get("fill"), item["style"]["fill"]),
                    "text_anchor": str(style.get("text_anchor") or item["style"]["text_anchor"]),
                },
            })
            if typography_presets[-1]["style"]["text_anchor"] not in {"start", "middle", "end"}:
                raise SvgCollageError("Unsupported text anchor in typography preset.")
        text_options[str(object_id)] = {"copy_options": copy_options, "typography_presets": typography_presets}

    raw_presets = raw_bundle.get("visual_style_presets", [])
    if not isinstance(raw_presets, list) or not 1 <= len(raw_presets) <= MAX_STYLE_PRESETS:
        raise SvgCollageError(f"visual_style_presets require 1-{MAX_STYLE_PRESETS} items.")
    visual_presets = []
    for index, preset in enumerate(raw_presets):
        if not isinstance(preset, dict):
            raise SvgCollageError("Every visual style preset must be an object.")
        operations = preset.get("operations")
        if not isinstance(operations, list) or not operations:
            raise SvgCollageError("Every visual style preset requires deterministic operations.")
        for operation in operations:
            if not isinstance(operation, dict) or operation.get("op") not in {"set_canvas_style", "update_text", "replace_cutout_asset"}:
                raise SvgCollageError("Visual style presets contain an unsupported operation.")
            if operation.get("op") == "set_canvas_style":
                style = operation.get("style") if isinstance(operation.get("style"), dict) else {}
                _color(operation.get("background", style.get("background")), "#ffffff")
            else:
                target = by_id.get(str(operation.get("object_id") or ""))
                expected_type = "text" if operation.get("op") == "update_text" else "cutout"
                if target is None or target.get("type") != expected_type:
                    raise SvgCollageError("Visual style preset operation targets an incompatible object.")
                if operation.get("op") == "replace_cutout_asset":
                    _authoring_asset_file_id(session_id, operation.get("asset_file_id"))
        visual_presets.append({
            "id": str(preset.get("id") or f"style-{index + 1}")[:128],
            "label": str(preset.get("label") or f"Style {index + 1}")[:160],
            "rationale": str(preset.get("rationale") or "")[:300],
            "swatches": [_color(value, "#ffffff") for value in list(preset.get("swatches") or [])[:5]],
            "affected_object_ids": [str(value) for value in list(preset.get("affected_object_ids") or []) if str(value) in by_id],
            "operations": operations,
        })
    return {
        "schema_version": "1.0",
        "visual_style_presets": visual_presets,
        "asset_candidates_by_object": candidates_by_object,
        "addable_elements": addable_elements,
        "text_authoring_options": text_options,
    }


def compile_svg_collage(session_id: str, scene: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    canvas = scene.get("canvas")
    if not isinstance(canvas, dict):
        raise SvgCollageError("SVG collage requires a canvas object.")
    width = int(_number(canvas.get("width", 1200), minimum=64, maximum=4096))
    height = int(_number(canvas.get("height", 1200), minimum=64, maximum=4096))
    background = _color(canvas.get("background"), "#ffffff")
    raw_objects = scene.get("objects", scene.get("layers"))
    if not isinstance(raw_objects, list) or not raw_objects:
        raise SvgCollageError("SVG collage requires at least one object.")
    if len(raw_objects) > MAX_OBJECTS:
        raise SvgCollageError(f"SVG collage supports at most {MAX_OBJECTS} objects.")

    normalized: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, raw in enumerate(raw_objects):
        if not isinstance(raw, dict):
            raise SvgCollageError(f"Object {index + 1} must be an object.")
        object_id = _object_id(raw.get("id") or f"object-{index + 1}")
        if object_id in seen_ids:
            raise SvgCollageError(f"Duplicate collage object id: {object_id}.")
        seen_ids.add(object_id)
        object_type = str(raw.get("type") or ("text" if "text" in raw else "cutout"))
        if object_type not in {"cutout", "text"}:
            raise SvgCollageError(f"Unsupported collage object type: {object_type}.")
        transform = _transform(raw.get("transform") if isinstance(raw.get("transform"), dict) else raw, width, height)
        item: dict[str, Any] = {
            "id": object_id,
            "type": object_type,
            "label": str(raw.get("label") or object_id)[:160],
            "transform": transform,
            "z_index": int(_number(raw.get("z_index", index), minimum=-1000, maximum=1000)),
            "visible": raw.get("visible") is not False,
            "locked": raw.get("locked") is True,
        }
        if object_type == "cutout":
            file_id = str(raw.get("asset_file_id") or raw.get("asset_ref", {}).get("fileId") or "")
            data_uri, mime = _asset_data_uri(session_id, file_id)
            item.update({"asset_file_id": file_id, "asset_mime": mime, "asset_data_uri": data_uri})
        else:
            style = raw.get("style") if isinstance(raw.get("style"), dict) else {}
            font_family = str(style.get("font_family") or "Arial")
            if font_family not in SAFE_FONTS:
                font_family = "Arial"
            item.update({
                "text": str(raw.get("text") or "Text")[:500],
                "style": {
                    "font_family": font_family,
                    "font_size": _number(style.get("font_size", 64), minimum=8, maximum=512),
                    "font_weight": int(_number(style.get("font_weight", 700), minimum=100, maximum=900)),
                    "fill": _color(style.get("fill"), "#111111"),
                    "text_anchor": str(style.get("text_anchor") or "start") if str(style.get("text_anchor") or "start") in {"start", "middle", "end"} else "start",
                },
            })
        normalized.append(item)

    normalized.sort(key=lambda item: item["z_index"])
    authoring_bundle = _normalize_authoring_bundle(session_id, scene.get("authoring_bundle"), normalized)
    creation_mode = str(scene.get("creation_mode") or "")
    if creation_mode and creation_mode != "image_collage":
        raise SvgCollageError(f"Unsupported collage creation mode: {creation_mode}.")
    if creation_mode == "image_collage":
        cutout_ids = [item["id"] for item in normalized if item["type"] == "cutout"]
        if len(cutout_ids) < 2:
            raise SvgCollageError("Initial image collage requires at least two transparent cutout image objects.")
        if authoring_bundle is None:
            raise SvgCollageError("Initial image collage requires a complete authoring_bundle before composition.")
    manifest = {
        "schema_version": "1.0",
        "artifact_type": "svg-collage",
        "revision": 1,
        "canvas": {"width": width, "height": height, "background": background},
        "objects": [{key: value for key, value in item.items() if key != "asset_data_uri"} for item in normalized],
    }
    if authoring_bundle is not None:
        manifest["authoring_bundle"] = authoring_bundle
    if creation_mode:
        manifest["creation_mode"] = creation_mode
    parts = [
        f'<svg xmlns="{SVG_NS}" viewBox="0 0 {width} {height}" width="{width}" height="{height}" data-revision="1">',
        f'<metadata id="{SCENE_METADATA_ID}">{html.escape(json.dumps(manifest, separators=(",", ":")))}</metadata>',
        f'<rect id="collage-background" width="{width}" height="{height}" fill="{background}" data-role="background"/>',
        '<g id="collage-objects">',
    ]
    for item in normalized:
        transform = item["transform"]
        visibility = "visible" if item["visible"] else "hidden"
        common = f'id="{item["id"]}" data-collage-object="true" data-object-type="{item["type"]}" visibility="{visibility}"'
        rotate = f' transform="rotate({transform["rotation"]} {transform["x"] + transform["width"] / 2} {transform["y"] + transform["height"] / 2})"'
        if item["type"] == "cutout":
            parts.append(
                f'<image {common} x="{transform["x"]}" y="{transform["y"]}" width="{transform["width"]}" height="{transform["height"]}"{rotate} href="{item["asset_data_uri"]}" preserveAspectRatio="xMidYMid meet"/>'
            )
        else:
            style = item["style"]
            baseline = transform["y"] + style["font_size"]
            parts.append(
                f'<text {common} x="{transform["x"]}" y="{baseline}"{rotate} font-family="{html.escape(style["font_family"], quote=True)}" font-size="{style["font_size"]}" font-weight="{style["font_weight"]}" fill="{style["fill"]}" text-anchor="{style["text_anchor"]}">{html.escape(item["text"])}</text>'
            )
    parts.extend(["</g>", "</svg>"])
    return "".join(parts).encode("utf-8"), manifest


def _read_manifest(root: ET.Element) -> tuple[ET.Element, dict[str, Any]]:
    metadata = root.find(f"{{{SVG_NS}}}metadata[@id='{SCENE_METADATA_ID}']")
    if metadata is None or not metadata.text:
        raise SvgCollageError("SVG collage scene metadata is missing.")
    try:
        return metadata, json.loads(metadata.text)
    except json.JSONDecodeError as error:
        raise SvgCollageError("SVG collage scene metadata is invalid.") from error


def inspect_svg_collage(path: Path) -> dict[str, Any]:
    """Return a validated, markup-free scene snapshot for instruction grounding."""
    try:
        root = ET.fromstring(path.read_bytes())
    except (OSError, ET.ParseError) as error:
        raise SvgCollageError("SVG collage document is invalid.") from error
    if root.tag != f"{{{SVG_NS}}}svg":
        raise SvgCollageError("SVG collage document requires an SVG root.")
    _, manifest = _read_manifest(root)
    if manifest.get("artifact_type") != "svg-collage":
        raise SvgCollageError("Unsupported collage artifact type.")
    revision = manifest.get("revision")
    if not isinstance(revision, int) or revision < 1:
        raise SvgCollageError("SVG collage revision is invalid.")
    canvas = manifest.get("canvas")
    if not isinstance(canvas, dict):
        raise SvgCollageError("SVG collage canvas is invalid.")
    width = int(_number(canvas.get("width"), minimum=64, maximum=4096))
    height = int(_number(canvas.get("height"), minimum=64, maximum=4096))
    objects = manifest.get("objects")
    if not isinstance(objects, list) or not objects or len(objects) > MAX_OBJECTS:
        raise SvgCollageError("SVG collage object manifest is invalid.")

    normalized: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, item in enumerate(objects):
        if not isinstance(item, dict):
            raise SvgCollageError("Every collage scene object must be an object.")
        object_id = _object_id(item.get("id"))
        if object_id in seen_ids:
            raise SvgCollageError(f"Duplicate collage object id: {object_id}.")
        seen_ids.add(object_id)
        object_type = str(item.get("type") or "")
        if object_type not in {"cutout", "text"}:
            raise SvgCollageError(f"Unsupported collage object type: {object_type}.")
        record: dict[str, Any] = {
            "id": object_id,
            "type": object_type,
            "label": str(item.get("label") or object_id)[:160],
            "transform": _transform(item.get("transform") if isinstance(item.get("transform"), dict) else {}, width, height),
            "z_index": int(_number(item.get("z_index", index), minimum=-1000, maximum=1000)),
            "visible": item.get("visible") is not False,
            "locked": item.get("locked") is True,
        }
        if object_type == "text":
            record["text"] = str(item.get("text") or "")[:500]
        normalized.append(record)
    return {
        "schema_version": "1.0",
        "artifact_type": "svg-collage",
        "revision": revision,
        "canvas": {"width": width, "height": height, "background": _color(canvas.get("background"), "#ffffff")},
        "objects": normalized,
    }


def inspect_svg_artifact(path: Path) -> dict[str, Any]:
    """Inspect a layered collage or normalize a safe plain SVG for P10 grounding."""
    try:
        root = ET.fromstring(path.read_bytes())
    except (OSError, ET.ParseError) as error:
        raise SvgCollageError("SVG document is invalid.") from error
    metadata = root.find(f"{{{SVG_NS}}}metadata[@id='{SCENE_METADATA_ID}']")
    if metadata is not None:
        return inspect_svg_collage(path)
    try:
        report = svg_accessibility.inspect_svg(path)
    except svg_accessibility.SvgAccessibilityError as error:
        raise SvgCollageError(str(error)) from error

    view_box = report.get("viewport", {}).get("view_box", [])
    canvas = {
        "width": view_box[2] if len(view_box) == 4 else report.get("viewport", {}).get("width", ""),
        "height": view_box[3] if len(view_box) == 4 else report.get("viewport", {}).get("height", ""),
        "background": "transparent",
    }
    objects = []
    for item in report.get("objects", []):
        object_type = "text" if item.get("tag") == "text" else "graphic"
        label = item.get("text_content") or item.get("source_id") or item.get("tag") or item.get("object_id")
        objects.append({
            "id": item["object_id"],
            "type": object_type,
            "label": str(label)[:160],
            "tag": item.get("tag", ""),
            "bbox": item.get("bbox"),
            "z_index": item.get("z_order", 0),
            "visible": True,
            "locked": True,
            **({"text": item.get("text_content", "")} if object_type == "text" else {}),
        })
    return {
        "schema_version": "1.0",
        "artifact_type": "svg-figure",
        "revision": report["revision"],
        "canvas": canvas,
        "objects": objects,
    }


def apply_svg_collage_patch(
    path: Path,
    base_revision: int,
    operations: list[dict[str, Any]],
    *,
    session_id: str | None = None,
) -> dict[str, Any]:
    ET.register_namespace("", SVG_NS)
    root = ET.fromstring(path.read_bytes())
    metadata, manifest = _read_manifest(root)
    revision = int(manifest.get("revision", 1))
    if revision != base_revision:
        raise SvgCollageError(f"Revision conflict: expected {base_revision}, current revision is {revision}.")
    objects = manifest.get("objects")
    if not isinstance(objects, list):
        raise SvgCollageError("SVG collage object manifest is invalid.")
    by_id = {str(item.get("id")): item for item in objects if isinstance(item, dict)}
    object_group = root.find(f"{{{SVG_NS}}}g[@id='collage-objects']")
    if object_group is None:
        raise SvgCollageError("SVG collage object group is missing.")

    for operation in operations:
        if not isinstance(operation, dict):
            raise SvgCollageError("Every patch operation must be an object.")
        operation_name = str(operation.get("op") or "")
        if operation_name == "set_canvas_style":
            style_patch = operation.get("style") if isinstance(operation.get("style"), dict) else {}
            background = _color(
                operation.get("background", style_patch.get("background")),
                str(manifest["canvas"].get("background") or "#ffffff"),
            )
            background_element = root.find(f"{{{SVG_NS}}}rect[@id='collage-background']")
            if background_element is None:
                raise SvgCollageError("SVG collage background is missing.")
            manifest["canvas"]["background"] = background
            background_element.set("fill", background)
            continue
        object_id = _object_id(operation.get("object_id"))
        if operation_name == "add_cutout":
            if object_id in by_id:
                raise SvgCollageError(f"Duplicate collage object id: {object_id}.")
            if len(objects) >= MAX_OBJECTS:
                raise SvgCollageError(f"SVG collage supports at most {MAX_OBJECTS} objects.")
            if session_id is None:
                raise SvgCollageError("Semantic collage patches require an active session.")
            file_id = str(operation.get("asset_file_id") or "")
            data_uri, mime = _asset_data_uri(session_id, file_id)
            canvas = manifest["canvas"]
            transform = _transform(operation, int(canvas["width"]), int(canvas["height"]))
            item = {
                "id": object_id,
                "type": "cutout",
                "label": str(operation.get("label") or object_id)[:160],
                "asset_file_id": file_id,
                "asset_mime": mime,
                "transform": transform,
                "z_index": len(objects),
                "visible": True,
                "locked": False,
            }
            element = ET.Element(f"{{{SVG_NS}}}image", {
                "id": object_id,
                "data-collage-object": "true",
                "data-object-type": "cutout",
                "visibility": "visible",
                "x": str(transform["x"]),
                "y": str(transform["y"]),
                "width": str(transform["width"]),
                "height": str(transform["height"]),
                "transform": f'rotate({transform["rotation"]} {transform["x"] + transform["width"] / 2} {transform["y"] + transform["height"] / 2})',
                "href": data_uri,
                "preserveAspectRatio": "xMidYMid meet",
            })
            objects.append(item)
            by_id[object_id] = item
            object_group.append(element)
            continue
        if operation_name == "add_text":
            if object_id in by_id:
                raise SvgCollageError(f"Duplicate collage object id: {object_id}.")
            canvas = manifest["canvas"]
            style_patch = operation.get("style") if isinstance(operation.get("style"), dict) else {}
            font_family = str(style_patch.get("font_family") or "Arial")
            if font_family not in SAFE_FONTS:
                font_family = "Arial"
            style = {
                "font_family": font_family,
                "font_size": _number(style_patch.get("font_size", 64), minimum=8, maximum=512),
                "font_weight": int(_number(style_patch.get("font_weight", 700), minimum=100, maximum=900)),
                "fill": _color(style_patch.get("fill"), "#111111"),
                "text_anchor": "start",
            }
            transform = _transform(
                {
                    "x": operation.get("x", int(canvas["width"]) * 0.15),
                    "y": operation.get("y", int(canvas["height"]) * 0.78),
                    "width": operation.get("width", int(canvas["width"]) * 0.7),
                    "height": operation.get("height", style["font_size"] * 1.3),
                    "rotation": operation.get("rotation", 0),
                },
                int(canvas["width"]),
                int(canvas["height"]),
            )
            item = {
                "id": object_id,
                "type": "text",
                "label": str(operation.get("label") or "Text")[:160],
                "text": str(operation.get("text") or "Text")[:500],
                "style": style,
                "transform": transform,
                "z_index": len(objects),
                "visible": True,
                "locked": False,
            }
            element = ET.Element(f"{{{SVG_NS}}}text", {
                "id": object_id,
                "data-collage-object": "true",
                "data-object-type": "text",
                "visibility": "visible",
                "x": str(transform["x"]),
                "y": str(transform["y"] + style["font_size"]),
                "transform": f'rotate({transform["rotation"]} {transform["x"] + transform["width"] / 2} {transform["y"] + transform["height"] / 2})',
                "font-family": style["font_family"],
                "font-size": str(style["font_size"]),
                "font-weight": str(style["font_weight"]),
                "fill": style["fill"],
                "text-anchor": style["text_anchor"],
            })
            element.text = item["text"]
            objects.append(item)
            by_id[object_id] = item
            object_group.append(element)
            continue
        item = by_id.get(object_id)
        element = object_group.find(f"*[@id='{object_id}']")
        if item is None or element is None:
            raise SvgCollageError(f"Unknown collage object: {object_id}.")
        if item.get("locked") is True:
            raise SvgCollageError(f"Collage object is locked: {object_id}.")
        if operation_name == "replace_cutout_asset":
            if item.get("type") != "cutout":
                raise SvgCollageError("replace_cutout_asset applies only to cutout objects.")
            if session_id is None:
                raise SvgCollageError("Semantic collage patches require an active session.")
            file_id = str(operation.get("asset_file_id") or "")
            data_uri, mime = _asset_data_uri(session_id, file_id)
            item["asset_file_id"] = file_id
            item["asset_mime"] = mime
            if "label" in operation:
                item["label"] = str(operation["label"])[:160]
            element.set("href", data_uri)
        elif operation_name == "remove_object":
            if len(objects) <= 1:
                raise SvgCollageError("A collage must retain at least one object.")
            objects.remove(item)
            by_id.pop(object_id, None)
            object_group.remove(element)
        elif operation_name == "set_transform":
            canvas = manifest["canvas"]
            current = item.get("transform", {})
            next_transform = _transform({**current, **operation}, int(canvas["width"]), int(canvas["height"]))
            item["transform"] = next_transform
            if item.get("type") == "text":
                current_width = float(current.get("width") or next_transform["width"])
                width_scale = next_transform["width"] / current_width
                item["style"]["font_size"] = _number(
                    float(item["style"]["font_size"]) * width_scale,
                    minimum=8,
                    maximum=512,
                )
                element.set("x", str(next_transform["x"]))
                element.set("y", str(next_transform["y"] + float(item["style"]["font_size"])))
                element.set("font-size", str(item["style"]["font_size"]))
            else:
                for key in ("x", "y", "width", "height"):
                    element.set(key, str(next_transform[key]))
            element.set("transform", f'rotate({next_transform["rotation"]} {next_transform["x"] + next_transform["width"] / 2} {next_transform["y"] + next_transform["height"] / 2})')
        elif operation_name == "set_order":
            direction = str(operation.get("direction") or "")
            current_index = objects.index(item)
            target_index = {"front": len(objects) - 1, "back": 0, "forward": min(len(objects) - 1, current_index + 1), "backward": max(0, current_index - 1)}.get(direction)
            if target_index is None:
                raise SvgCollageError(f"Unsupported layer direction: {direction}.")
            objects.pop(current_index)
            objects.insert(target_index, item)
            children = list(object_group)
            object_group.remove(element)
            reference = min(target_index, len(children) - 1)
            object_group.insert(reference, element)
        elif operation_name == "update_text":
            if item.get("type") != "text":
                raise SvgCollageError("update_text applies only to text objects.")
            if "text" in operation:
                item["text"] = str(operation["text"])[:500]
                element.text = item["text"]
            style_patch = operation.get("style") if isinstance(operation.get("style"), dict) else {}
            style = item["style"]
            if "fill" in style_patch:
                style["fill"] = _color(style_patch["fill"], style["fill"])
                element.set("fill", style["fill"])
            if "font_size" in style_patch:
                style["font_size"] = _number(style_patch["font_size"], minimum=8, maximum=512)
                element.set("font-size", str(style["font_size"]))
            if "font_family" in style_patch:
                font_family = str(style_patch["font_family"])
                if font_family not in SAFE_FONTS:
                    raise SvgCollageError(f"Unsupported font family: {font_family!r}.")
                style["font_family"] = font_family
                element.set("font-family", font_family)
            if "font_weight" in style_patch:
                style["font_weight"] = int(_number(style_patch["font_weight"], minimum=100, maximum=900))
                element.set("font-weight", str(style["font_weight"]))
            if "text_anchor" in style_patch:
                text_anchor = str(style_patch["text_anchor"])
                if text_anchor not in {"start", "middle", "end"}:
                    raise SvgCollageError(f"Unsupported text anchor: {text_anchor!r}.")
                style["text_anchor"] = text_anchor
                element.set("text-anchor", text_anchor)
        else:
            raise SvgCollageError(f"Unsupported SVG collage patch operation: {operation_name}.")

    for index, item in enumerate(objects):
        item["z_index"] = index
    manifest["revision"] = revision + 1
    root.set("data-revision", str(manifest["revision"]))
    metadata.text = json.dumps(manifest, separators=(",", ":"))
    path.write_bytes(ET.tostring(root, encoding="utf-8", xml_declaration=True))
    return manifest