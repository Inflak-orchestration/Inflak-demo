from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
REVISION_ATTRIBUTE = "data-p10-revision"
MAX_ELEMENTS = 5000
EDITABLE_ATTRIBUTES = {
    "fill",
    "stroke",
    "stroke-width",
    "font-size",
    "x",
    "y",
    "aria-label",
    "aria-labelledby",
    "role",
}
PRESENTATION_ATTRIBUTES = {"fill", "stroke", "stroke-width", "font-size", "font-weight", "opacity"}
OBJECT_TAGS = {"text", "rect", "circle", "ellipse", "line", "polyline", "polygon", "path", "g", "use", "image"}
COLOR_PATTERN = re.compile(r"(?:#[0-9A-Fa-f]{3}(?:[0-9A-Fa-f]{3})?|rgb\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*\)|[A-Za-z]{1,24}|none)")
NUMBER_PATTERN = re.compile(r"-?(?:\d+(?:\.\d*)?|\.\d+)(?:px|pt|em|rem|%)?")
SAFE_ROLE_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,63}")
NAMED_COLORS = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "red": (255, 0, 0),
    "green": (0, 128, 0),
    "blue": (0, 0, 255),
    "gray": (128, 128, 128),
    "grey": (128, 128, 128),
    "yellow": (255, 255, 0),
    "orange": (255, 165, 0),
    "purple": (128, 0, 128),
}


class SvgAccessibilityError(ValueError):
    pass


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _safe_root(content: bytes) -> ET.Element:
    lowered = content.lower()
    if b"<!doctype" in lowered or b"<!entity" in lowered:
        raise SvgAccessibilityError("SVG document types and entities are not supported.")
    try:
        root = ET.fromstring(content)
    except ET.ParseError as error:
        raise SvgAccessibilityError("Invalid SVG document.") from error
    if _local_name(root.tag) != "svg":
        raise SvgAccessibilityError("Uploaded artifact is not an SVG document.")
    elements = list(root.iter())
    if len(elements) > MAX_ELEMENTS:
        raise SvgAccessibilityError(f"SVG supports at most {MAX_ELEMENTS} elements for inspection.")
    for element in elements:
        tag = _local_name(element.tag)
        if tag in {"script", "foreignObject"}:
            raise SvgAccessibilityError(f"Unsafe SVG element is not supported: {tag}.")
        for attribute, value in element.attrib.items():
            name = _local_name(attribute).lower()
            if name.startswith("on"):
                raise SvgAccessibilityError("SVG event-handler attributes are not supported.")
            if name == "href" and value and not value.startswith(("#", "data:image/")):
                raise SvgAccessibilityError("External SVG references are not supported.")
    return root


def _parse_style(value: str | None) -> dict[str, str]:
    style: dict[str, str] = {}
    for declaration in str(value or "").split(";"):
        name, separator, item = declaration.partition(":")
        if separator and name.strip() in PRESENTATION_ATTRIBUTES:
            style[name.strip()] = item.strip()
    return style


def _number(value: str | None) -> float | None:
    match = re.match(r"-?(?:\d+(?:\.\d*)?|\.\d+)", str(value or "").strip())
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def _rgb(value: str | None) -> tuple[int, int, int] | None:
    text = str(value or "").strip().lower()
    if text in NAMED_COLORS:
        return NAMED_COLORS[text]
    if re.fullmatch(r"#[0-9a-f]{3}", text):
        return tuple(int(character * 2, 16) for character in text[1:])  # type: ignore[return-value]
    if re.fullmatch(r"#[0-9a-f]{6}", text):
        return tuple(int(text[index:index + 2], 16) for index in (1, 3, 5))  # type: ignore[return-value]
    match = re.fullmatch(r"rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)", text)
    if match:
        values = tuple(min(255, int(item)) for item in match.groups())
        return values  # type: ignore[return-value]
    return None


def _luminance(color: tuple[int, int, int]) -> float:
    channels = []
    for value in color:
        channel = value / 255
        channels.append(channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def _contrast(foreground: str | None, background: str | None) -> float | None:
    first = _rgb(foreground)
    second = _rgb(background)
    if first is None or second is None:
        return None
    high, low = sorted((_luminance(first), _luminance(second)), reverse=True)
    return round((high + 0.05) / (low + 0.05), 2)


def _color_distance(first: tuple[float, float, float], second: tuple[float, float, float]) -> float:
    return round(math.sqrt(sum((left - right) ** 2 for left, right in zip(first, second))), 2)


def _deuteranopia_approximation(color: tuple[int, int, int]) -> tuple[float, float, float]:
    red, green, blue = color
    return (
        0.625 * red + 0.375 * green,
        0.7 * red + 0.3 * green,
        0.3 * green + 0.7 * blue,
    )


def _bbox(element: ET.Element) -> dict[str, float] | None:
    tag = _local_name(element.tag)
    x = _number(element.get("x")) or 0.0
    y = _number(element.get("y")) or 0.0
    if tag in {"rect", "image", "use"}:
        width = _number(element.get("width"))
        height = _number(element.get("height"))
        return {"x": x, "y": y, "width": width or 0.0, "height": height or 0.0}
    if tag == "circle":
        radius = _number(element.get("r")) or 0.0
        center_x = _number(element.get("cx")) or 0.0
        center_y = _number(element.get("cy")) or 0.0
        return {"x": center_x - radius, "y": center_y - radius, "width": radius * 2, "height": radius * 2}
    if tag == "ellipse":
        radius_x = _number(element.get("rx")) or 0.0
        radius_y = _number(element.get("ry")) or 0.0
        center_x = _number(element.get("cx")) or 0.0
        center_y = _number(element.get("cy")) or 0.0
        return {"x": center_x - radius_x, "y": center_y - radius_y, "width": radius_x * 2, "height": radius_y * 2}
    if tag == "line":
        x1, y1 = _number(element.get("x1")) or 0.0, _number(element.get("y1")) or 0.0
        x2, y2 = _number(element.get("x2")) or 0.0, _number(element.get("y2")) or 0.0
        return {"x": min(x1, x2), "y": min(y1, y2), "width": abs(x2 - x1), "height": abs(y2 - y1)}
    if tag == "text":
        size = _number(element.get("font-size")) or 16.0
        content = " ".join("".join(element.itertext()).split())
        return {"x": x, "y": y - size, "width": round(len(content) * size * 0.6, 2), "height": size * 1.2}
    return None


def _role_candidate(element: ET.Element) -> str:
    tag = _local_name(element.tag)
    if tag == "text":
        return "label"
    if tag in {"line", "polyline", "path"} and (element.get("marker-end") or element.get("marker-start")):
        return "arrow"
    if tag == "g":
        return "group"
    if tag in {"use", "image"}:
        return "icon"
    if tag in {"rect", "circle", "ellipse", "polygon"}:
        return "shape"
    return "unknown"


def inspect_svg(path: Path) -> dict[str, Any]:
    root = _safe_root(path.read_bytes())
    revision = int(root.get(REVISION_ATTRIBUTE, "1"))
    parent_map = {child: parent for parent in root.iter() for child in parent}
    computed: dict[ET.Element, dict[str, str]] = {}
    objects: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    used_ids: set[str] = set()

    for index, element in enumerate(root.iter()):
        parent_style = computed.get(parent_map.get(element), {})
        own_style = _parse_style(element.get("style"))
        style = dict(parent_style)
        for name in PRESENTATION_ATTRIBUTES:
            value = element.get(name)
            if value is not None:
                style[name] = value
        style.update(own_style)
        computed[element] = style
        tag = _local_name(element.tag)
        if tag not in OBJECT_TAGS:
            continue
        raw_id = str(element.get("id") or "")
        object_id = raw_id or f"p10-auto-{index}"
        if object_id in used_ids:
            object_id = f"{object_id}-{index}"
        used_ids.add(object_id)
        text = " ".join("".join(element.itertext()).split()) if tag == "text" else ""
        fill = style.get("fill", "black" if tag == "text" else "none")
        font_size = _number(style.get("font-size")) if tag == "text" else None
        ratio = _contrast(fill, "white") if tag == "text" else None
        item = {
            "object_id": object_id,
            "source_id": raw_id,
            "dom_index": index,
            "tag": tag,
            "role_candidate": _role_candidate(element),
            "parent_object_id": "",
            "text_content": text,
            "fill": fill,
            "stroke": style.get("stroke", "none"),
            "stroke_width": _number(style.get("stroke-width")),
            "opacity": _number(style.get("opacity")) if style.get("opacity") is not None else 1,
            "font_size": font_size,
            "bbox": _bbox(element),
            "dom_order": index,
            "z_order": index,
            "contrast": {"ratio": ratio, "background": "white", "background_basis": "default_canvas_assumption"} if tag == "text" else None,
            "editable_properties": sorted(EDITABLE_ATTRIBUTES | ({"text_content"} if tag == "text" else set())),
            "provenance": "confirmed_from_svg",
        }
        objects.append(item)
        if tag == "text" and text:
            if font_size is not None and font_size < 12:
                findings.append({"id": f"small-text-{object_id}", "category": "small_text", "severity": "warning", "object_ids": [object_id], "evidence": {"font_size": font_size}, "provenance": "computed_by_checker"})
            if ratio is not None:
                large_text = (font_size or 16) >= 24
                required = 3.0 if large_text else 4.5
                if ratio < required:
                    findings.append({"id": f"contrast-{object_id}", "category": "low_contrast", "severity": "error", "object_ids": [object_id], "evidence": {"ratio": ratio, "required": required, "background_basis": "default_canvas_assumption"}, "provenance": "computed_by_checker"})

    id_for_element = {element: (str(element.get("id") or "") or f"p10-auto-{index}") for index, element in enumerate(root.iter())}
    for item in objects:
        element = list(root.iter())[item["dom_index"]]
        parent = parent_map.get(element)
        item["parent_object_id"] = id_for_element.get(parent, "")

    title = next((" ".join("".join(item.itertext()).split()) for item in root if _local_name(item.tag) == "title"), "")
    description = next((" ".join("".join(item.itertext()).split()) for item in root if _local_name(item.tag) == "desc"), "")
    if not title and not root.get("aria-label") and not root.get("aria-labelledby"):
        findings.append({"id": "missing-accessible-name", "category": "missing_accessible_name", "severity": "error", "object_ids": [], "evidence": {}, "provenance": "computed_by_checker"})
    if not description:
        findings.append({"id": "missing-description", "category": "missing_description", "severity": "warning", "object_ids": [], "evidence": {}, "provenance": "computed_by_checker"})

    colors: dict[str, list[str]] = {}
    for item in objects:
        for color in (item["fill"], item["stroke"]):
            if color and color != "none":
                colors.setdefault(color, []).append(item["object_id"])
    if len(colors) > 1:
        findings.append({"id": "color-semantics-review", "category": "possible_color_only_encoding", "severity": "needs_confirmation", "object_ids": sorted({object_id for ids in colors.values() for object_id in ids}), "evidence": {"palette": [{"color": color, "object_ids": ids} for color, ids in colors.items()]}, "provenance": "inferred_by_genai"})

    palette_comparisons: list[dict[str, Any]] = []
    parsed_colors = [(color, _rgb(color)) for color in colors]
    for index, (first_name, first_rgb) in enumerate(parsed_colors):
        if first_rgb is None:
            continue
        for second_name, second_rgb in parsed_colors[index + 1:]:
            if second_rgb is None:
                continue
            grayscale_delta = round(abs(_luminance(first_rgb) - _luminance(second_rgb)) * 100, 2)
            deuteranopia_distance = _color_distance(_deuteranopia_approximation(first_rgb), _deuteranopia_approximation(second_rgb))
            comparison = {
                "colors": [first_name, second_name],
                "grayscale_luminance_delta": grayscale_delta,
                "deuteranopia_rgb_distance": deuteranopia_distance,
                "method": "deterministic_approximation",
            }
            palette_comparisons.append(comparison)
            if grayscale_delta < 10:
                findings.append({"id": f"grayscale-{index}-{len(palette_comparisons)}", "category": "grayscale_ambiguity", "severity": "warning", "object_ids": colors[first_name] + colors[second_name], "evidence": comparison, "provenance": "computed_by_checker"})
            if deuteranopia_distance < 45:
                findings.append({"id": f"color-vision-{index}-{len(palette_comparisons)}", "category": "color_vision_ambiguity", "severity": "warning", "object_ids": colors[first_name] + colors[second_name], "evidence": comparison, "provenance": "computed_by_checker"})

    reading_objects = [item for item in objects if item["tag"] in {"text", "g"}]
    dom_reading_order = [item["object_id"] for item in reading_objects]
    geometric_objects = [item for item in reading_objects if item["bbox"] is not None]
    visual_reading_order = [item["object_id"] for item in sorted(geometric_objects, key=lambda item: (item["bbox"]["y"], item["bbox"]["x"]))]
    visual_ids = set(visual_reading_order)
    comparable_dom_order = [object_id for object_id in dom_reading_order if object_id in visual_ids]
    if len(visual_reading_order) > 1 and comparable_dom_order != visual_reading_order:
        findings.append({"id": "reading-order-conflict", "category": "reading_order_conflict", "severity": "needs_confirmation", "object_ids": visual_reading_order, "evidence": {"dom_order": comparable_dom_order, "visual_order": visual_reading_order}, "provenance": "computed_by_checker"})

    root_elements = list(root.iter())
    candidate_connections = []
    for item in objects:
        element = root_elements[item["dom_index"]]
        if item["role_candidate"] == "arrow":
            candidate_connections.append({
                "id": f"connection-{item['object_id']}",
                "arrow_object_id": item["object_id"],
                "source_object_id": element.get("data-source", ""),
                "target_object_id": element.get("data-target", ""),
                "status": "confirmed_from_svg" if element.get("data-source") and element.get("data-target") else "missing_or_uncertain",
            })

    view_box = [_number(part) for part in str(root.get("viewBox") or "").replace(",", " ").split()]
    return {
        "action": "svg_accessibility_inspected",
        "artifact_type": "svg-figure",
        "revision": revision,
        "viewport": {
            "view_box": view_box if len(view_box) == 4 and all(value is not None for value in view_box) else [],
            "width": root.get("width", ""),
            "height": root.get("height", ""),
        },
        "accessible_name": {"title": title, "aria_label": root.get("aria-label", ""), "aria_labelledby": root.get("aria-labelledby", "")},
        "description": description,
        "objects": objects,
        "candidate_reading_order": {"dom": dom_reading_order, "visual": visual_reading_order},
        "candidate_connections": candidate_connections,
        "palette": [{"color": color, "object_ids": ids} for color, ids in colors.items()],
        "palette_comparisons": palette_comparisons,
        "findings": findings,
        "limitations": [
            "Bounding boxes for paths, polygons, transformed elements, and externally styled content require browser geometry.",
            "Text contrast uses a white canvas assumption unless a rendered background is available.",
            "Color-vision and grayscale comparisons are deterministic approximations; browser-rendered sampling is required for final verification.",
        ],
    }


def _find_object(root: ET.Element, object_id: str) -> ET.Element | None:
    elements = list(root.iter())
    for index, element in enumerate(elements):
        if element.get("id") == object_id or (not element.get("id") and f"p10-auto-{index}" == object_id):
            return element
    return None


def _validate_attribute(name: str, value: Any) -> str:
    text = str(value)
    if name in {"fill", "stroke"} and not COLOR_PATTERN.fullmatch(text):
        raise SvgAccessibilityError(f"Unsupported color value for {name}.")
    if name in {"stroke-width", "font-size", "x", "y"} and not NUMBER_PATTERN.fullmatch(text):
        raise SvgAccessibilityError(f"Unsupported numeric value for {name}.")
    if name == "role" and not SAFE_ROLE_PATTERN.fullmatch(text):
        raise SvgAccessibilityError("Unsupported role value.")
    if name in {"aria-label", "aria-labelledby"} and len(text) > 1000:
        raise SvgAccessibilityError(f"{name} is too long.")
    return text


def apply_svg_patch(path: Path, base_revision: int, operations: list[dict[str, Any]]) -> dict[str, Any]:
    ET.register_namespace("", SVG_NS)
    ET.register_namespace("xlink", XLINK_NS)
    root = _safe_root(path.read_bytes())
    revision = int(root.get(REVISION_ATTRIBUTE, "1"))
    if revision != base_revision:
        raise SvgAccessibilityError(f"Revision conflict: expected {base_revision}, current revision is {revision}.")
    if not operations or len(operations) > 100:
        raise SvgAccessibilityError("A patch requires between 1 and 100 operations.")

    applied: list[dict[str, Any]] = []
    for operation in operations:
        if not isinstance(operation, dict):
            raise SvgAccessibilityError("Every patch operation must be an object.")
        operation_name = str(operation.get("op") or "")
        object_id = str(operation.get("object_id") or "")
        element = _find_object(root, object_id) if object_id else root
        if element is None:
            raise SvgAccessibilityError(f"Unknown SVG object: {object_id}.")
        if operation_name == "set_attributes":
            attributes = operation.get("attributes")
            if not isinstance(attributes, dict) or not attributes:
                raise SvgAccessibilityError("set_attributes requires attributes.")
            unknown = set(attributes) - EDITABLE_ATTRIBUTES
            if unknown:
                raise SvgAccessibilityError(f"Unsupported SVG attributes: {', '.join(sorted(unknown))}.")
            for name, value in attributes.items():
                element.set(name, _validate_attribute(name, value))
        elif operation_name == "set_text":
            if _local_name(element.tag) != "text":
                raise SvgAccessibilityError("set_text applies only to text elements.")
            text = str(operation.get("text") or "")
            if len(text) > 5000:
                raise SvgAccessibilityError("SVG text is too long.")
            element.text = text
        elif operation_name == "set_accessible_name":
            label = str(operation.get("label") or "").strip()
            if not label or len(label) > 1000:
                raise SvgAccessibilityError("Accessible name must contain 1 to 1000 characters.")
            element.set("aria-label", label)
        elif operation_name == "set_description":
            description = str(operation.get("text") or "").strip()
            if not description or len(description) > 10000:
                raise SvgAccessibilityError("Description must contain 1 to 10000 characters.")
            desc = next((child for child in root if _local_name(child.tag) == "desc"), None)
            if desc is None:
                desc = ET.Element(f"{{{SVG_NS}}}desc")
                root.insert(0, desc)
            desc.text = description
        elif operation_name == "set_dom_order":
            ordered_ids = operation.get("ordered_object_ids")
            if not isinstance(ordered_ids, list) or len(ordered_ids) < 2:
                raise SvgAccessibilityError("set_dom_order requires at least two object ids.")
            targets = [_find_object(root, str(item)) for item in ordered_ids]
            if any(target is None for target in targets):
                raise SvgAccessibilityError("set_dom_order contains an unknown object id.")
            parent_map = {child: parent for parent in root.iter() for child in parent}
            parents = {parent_map.get(target) for target in targets}
            if len(parents) != 1 or None in parents:
                raise SvgAccessibilityError("set_dom_order objects must be siblings.")
            parent = next(iter(parents))
            assert parent is not None
            positions = sorted(list(parent).index(target) for target in targets if target is not None)
            for target in targets:
                assert target is not None
                parent.remove(target)
            for position, target in zip(positions, targets):
                assert target is not None
                parent.insert(position, target)
        else:
            raise SvgAccessibilityError(f"Unsupported SVG accessibility operation: {operation_name}.")
        applied.append({"op": operation_name, "object_id": object_id})

    root.set(REVISION_ATTRIBUTE, str(revision + 1))
    path.write_bytes(ET.tostring(root, encoding="utf-8", xml_declaration=True))
    report = inspect_svg(path)
    return {"revision": revision + 1, "applied_operations": applied, "report": report}
