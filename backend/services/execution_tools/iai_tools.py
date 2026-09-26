from __future__ import annotations

import json
import re
import uuid
from html import escape as _html_escape
from pathlib import Path
from typing import Any, Literal
from urllib.parse import quote, unquote

from copilot import Tool, ToolInvocation, define_tool
from pydantic import BaseModel, Field

from backend.services import inflak_plugin_author, plugin_scenario_runner, uploads_store
from backend.services.execution_tools import svg_accessibility, svg_collage, svg_document_manager
from backend.services.inflak_plugins import plugin_dir, ready_plugin_dirs

PLUGIN_DIR = plugin_dir("inflak-main")
TEMPLATES_DIR = PLUGIN_DIR / "registry" / "templates"


# --- Template library (deterministic, server-side rendering) -----------------
# Layer 4 declares which widget types use a fixed template; the renderer loads
# the template from registry/templates/<widget_type>/ and fills its {{...}}
# placeholders from the semantic contract. This does NOT depend on the model
# reading files, so a templated widget always renders identically.

_TAG_RE = re.compile(r"\{\{\s*([#^&/]?)\s*([\w.]+)\s*\}\}")


def _lookup(stack: list[Any], name: str) -> Any:
    if name == ".":
        return stack[-1] if stack else None
    first, _, rest = name.partition(".")
    for frame in reversed(stack):
        if isinstance(frame, dict) and first in frame:
            value = frame[first]
            for part in [p for p in rest.split(".") if p]:
                value = value.get(part) if isinstance(value, dict) else None
            return value
    return None


def _falsy(value: Any) -> bool:
    return value is None or value is False or value == "" or value == [] or value == {}


def _render_mustache(template: str, stack: list[Any]) -> str:
    out: list[str] = []
    idx = 0
    while True:
        match = _TAG_RE.search(template, idx)
        if not match:
            out.append(template[idx:])
            break
        out.append(template[idx:match.start()])
        sigil, name = match.group(1), match.group(2)
        if sigil in ("#", "^"):
            close = re.search(r"\{\{/\s*" + re.escape(name) + r"\s*\}\}", template[match.end():])
            if not close:
                idx = match.end()
                continue
            inner = template[match.end():match.end() + close.start()]
            value = _lookup(stack, name)
            if sigil == "#":
                if isinstance(value, list):
                    for item in value:
                        out.append(_render_mustache(inner, stack + [item]))
                elif not _falsy(value):
                    out.append(_render_mustache(inner, stack + [value if isinstance(value, dict) else {}]))
            elif _falsy(value):
                out.append(_render_mustache(inner, stack))
            idx = match.end() + close.end()
        elif sigil == "/":
            idx = match.end()
        else:
            value = _lookup(stack, name)
            text = "" if value is None else str(value)
            out.append(text if sigil == "&" else _html_escape(text, quote=True))
            idx = match.end()
    return "".join(out)


def _candidate_template_dirs() -> list[Path]:
    """Template directories to search, covering every ready plugin (main + P1..P12)
    so a plugin's own widgets render from its own registry/templates/."""
    dirs: list[Path] = [TEMPLATES_DIR]
    try:
        for plugin_path in ready_plugin_dirs():
            candidate = plugin_path / "registry" / "templates"
            if candidate not in dirs:
                dirs.append(candidate)
    except Exception:
        pass
    return dirs


def load_widget_template(widget_type: str | None) -> dict[str, Any] | None:
    """Load a fixed template for widget_type from any ready plugin's
    registry/templates/, or None."""
    if not widget_type:
        return None
    for templates_dir in _candidate_template_dirs():
        base = templates_dir / widget_type
        html_path = base / "template.html"
        if not html_path.is_file():
            continue
        meta: dict[str, Any] = {}
        meta_path = base / "meta.json"
        if meta_path.is_file():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except (ValueError, OSError):
                meta = {}
        css_path = base / "template.css"
        js_path = base / "template.js"
        return {
            "html": html_path.read_text(encoding="utf-8"),
            "css": css_path.read_text(encoding="utf-8") if css_path.is_file() else "",
            "js": js_path.read_text(encoding="utf-8") if js_path.is_file() else "",
            "height": meta.get("height"),
            "meta": meta,
        }
    return None


def apply_widget_template(
    widget_type: str | None,
    *,
    display: dict[str, Any] | None = None,
    controls: list[Any] | None = None,
    interaction_goal: str | None = None,
    iai: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Return {html, css, js, height} with the template's {{placeholders}} filled
    from the semantic contract, or None if widget_type has no template."""
    template = load_widget_template(widget_type)
    if template is None:
        return None
    template_display = dict(display or {})
    if "edit_state" in template_display:
        template_display["edit_state_json"] = json.dumps(
            template_display["edit_state"], separators=(",", ":")
        )
    for key in (
        "edges",
        "cells",
        "relations",
        "blueprint",
        "provenance_summary",
        "prompt_catalog",
        "storyboard_composition",
        "source_text",
        "prompt_structure",
        "validation_errors",
    ):
        if key in template_display:
            template_display[f"{key}_json"] = json.dumps(
                template_display[key], separators=(",", ":")
            )
    context = {
        "display": template_display,
        "controls": controls or [],
        "interaction_goal": interaction_goal or "",
        "iai": iai or {},
    }
    return {
        "html": _render_mustache(template["html"], [context]),
        "css": template["css"],
        "js": template["js"],
        "height": template["height"],
        "meta": template["meta"],
    }


def normalize_upload_file_id(value: Any, session_id: str) -> str:
    candidate_id = Path(str(value or "")).name.split("-", 1)[0]
    if candidate_id and uploads_store.upload_path(session_id, candidate_id) is not None:
        return candidate_id
    return ""


def widget_asset_url(value: Any, session_id: str) -> str:
    if isinstance(value, dict):
        value = (
            value.get("fileId")
            or value.get("file_id")
            or value.get("asset_file_id")
            or value.get("source_file_id")
            or value.get("url")
            or value.get("path")
            or value.get("src")
            or value.get("filename")
            or ""
        )
    raw_value = str(value or "").strip()
    file_id = normalize_upload_file_id(raw_value, session_id)
    if file_id:
        return f"/api/sessions/{session_id}/uploads/{file_id}"
    routed_runtime = re.search(r"/api/sessions/[^/]+/widget-assets/(.+)$", raw_value)
    runtime_value = unquote(routed_runtime.group(1)) if routed_runtime else raw_value
    relative_path = uploads_store.runtime_image_relative_path(session_id, runtime_value)
    if relative_path:
        return f"/api/sessions/{session_id}/widget-assets/{quote(relative_path, safe='/')}"
    return ""


def normalize_widget_image_refs(display: dict[str, Any], session_id: str) -> dict[str, Any]:
    """Canonicalize widget image refs to browser-safe session asset URLs.

    Models sometimes echo a stored filename, absolute upload path, or Copilot
    runtime path. Resolve only files owned by the current session.
    """
    def normalize(value: Any) -> Any:
        if isinstance(value, list):
            return [normalize(item) for item in value]
        if not isinstance(value, dict):
            return value

        normalized_ref = {key: normalize(item) for key, item in value.items()}
        asset_keys = {
            "fileId", "file_id", "asset_file_id", "source_file_id",
            "url", "path", "src", "filename",
        }
        if not asset_keys.intersection(normalized_ref):
            return normalized_ref
        url = widget_asset_url(normalized_ref, session_id)
        if not url:
            return normalized_ref
        normalized_ref["url"] = url
        normalized_ref["path"] = url
        if "src" in normalized_ref:
            normalized_ref["src"] = url
        upload_id = re.search(r"/uploads/([A-Za-z0-9]+)$", url)
        if upload_id:
            normalized_ref["fileId"] = upload_id.group(1)
        return normalized_ref

    return normalize(display)


def normalize_widget_upload_urls(source: str, session_id: str) -> str:
    """Replace local session image references with browser-safe API URLs."""
    normalized = str(source or "")
    for upload in uploads_store.list_uploads(session_id):
        file_id = str(upload.get("fileId") or "")
        path = uploads_store.upload_path(session_id, file_id)
        if path is None:
            continue
        resolved = path.resolve()
        url = f"/api/sessions/{session_id}/uploads/{file_id}"
        for local_reference in (resolved.as_uri(), str(resolved)):
            normalized = normalized.replace(local_reference, url)
    declared_runtime_root = uploads_store.runtime_files_dir(session_id)
    runtime_root = declared_runtime_root.resolve()
    for path in uploads_store.list_runtime_images(session_id):
        relative_path = path.relative_to(runtime_root).as_posix()
        url = f"/api/sessions/{session_id}/widget-assets/{quote(relative_path, safe='/')}"
        declared_path = declared_runtime_root / relative_path
        for local_reference in (path.as_uri(), str(path), declared_path.as_uri(), str(declared_path)):
            normalized = normalized.replace(local_reference, url)
    return normalized


class RenderWidgetParams(BaseModel):
    widget_id: str | None = Field(default=None, description="Stable widget id. Generated if omitted.")
    selected_widget_id: str | None = Field(default=None, description="Widget registry id selected by Layer 2 and preserved by Layer 3.")
    widget_type: str = Field(description="Widget primitive type, e.g. choice_cards, structured_form, review_list, diff_view.")
    planner_id: str | None = Field(default=None, description="Planner requesting this widget.")
    interaction_goal: str = Field(description="What this widget should collect from the user.")
    display: dict[str, Any] = Field(default_factory=dict, description="Display content for the widget.")
    controls: list[dict[str, Any]] = Field(default_factory=list, description="Interactive controls to render.")
    expected_return: dict[str, Any] = Field(default_factory=dict, description="Optional return-shape guidance for the Agent; the host does not enforce it.")
    surface: Literal["conversation_widget", "artifact_canvas_widget"] = Field(default="conversation_widget", description="Host surface that owns the schema widget.")
    artifact_binding: dict[str, Any] = Field(default_factory=dict, description="Optional artifact id, revision, and stable object ids for a Canvas-bound schema widget.")
    placement: dict[str, Any] = Field(default_factory=dict, description="Canvas placement contract for a schema widget.")


class RenderHtmlWidgetParams(BaseModel):
    widget_id: str | None = Field(default=None, description="Stable widget id. Generated if omitted.")
    selected_widget_id: str | None = Field(default=None, description="Widget registry id selected by Layer 2 and preserved by Layer 3.")
    title: str = Field(default="Interactive HTML widget", description="Title shown around the widget iframe.")
    widget_type: str | None = Field(default=None, description="Semantic widget type (e.g. choice_cards, highlighted_text_editor). A matching registry template is used only when render_mode is template.")
    render_mode: Literal["generated", "template"] = Field(default="generated", description="Use generated to preserve Layer 4 HTML/CSS/JS; use template only to apply a repository-owned fixed widget template.")
    html: str = Field(default="", description="HTML body markup, rendered in a sandboxed iframe. Required for generated mode; optional for template mode.")
    css: str = Field(default="", description="Inline CSS for the iframe document.")
    js: str = Field(default="", description="Inline JavaScript for the iframe. It must call window.submitWidget(values) to return data.")
    height: int = Field(default=520, description="Requested iframe height in pixels.")
    display: dict[str, Any] = Field(default_factory=dict, description="Semantic display content used by the widget. Keep image references as complete session asset objects; widget JavaScript must resolve them with window.widgetAssetUrl(ref), never file:// or a raw path.")
    controls: list[dict[str, Any]] = Field(default_factory=list, description="Semantic controls used to fill a templated widget.")
    planner_id: str | None = Field(default=None, description="Planner requesting this widget.")
    interaction_goal: str | None = Field(default=None, description="What this widget should collect from the user.")
    expected_return: dict[str, Any] = Field(default_factory=dict, description="Optional return-shape guidance for the Agent; generated widgets may submit any JSON values.")
    surface: Literal["conversation_widget", "artifact_canvas_widget"] = Field(default="conversation_widget", description="Host surface that owns the widget iframe.")
    artifact_binding: dict[str, Any] = Field(default_factory=dict, description="Optional artifact id, revision, and stable object ids for a Canvas-bound widget.")
    placement: dict[str, Any] = Field(default_factory=dict, description="Canvas placement contract: anchored, sidebar, or canvas_overlay with an optional sidebar fallback.")


SVG_OBJECT_WIDGET_TYPES = frozenset({
    "svg_object_grounding",
    "svg_operation_control",
    "svg_candidate_selector",
})
PROMPT_OBJECT_WIDGET_TYPES = frozenset({
    "prompt_object_alignment",
    "prompt_target_resolver",
    "prompt_action_specificity_editor",
})
P12_ARTIFACT_WIDGET_TYPES = frozenset({
    "adaptive_refinement_interaction",
    "artifact_color_palette",
    "refinement_control",
    "semantic_variant_review",
    "refined_artifact_review",
})


def normalize_svg_widget_binding(widget_contract: dict[str, Any]) -> None:
    widget_type = str(widget_contract.get("semantic_widget_type") or widget_contract.get("widget_type") or "")
    if not widget_type.startswith("svg_") and widget_type not in PROMPT_OBJECT_WIDGET_TYPES | P12_ARTIFACT_WIDGET_TYPES:
        return

    widget_contract["surface"] = "artifact_canvas_widget"
    display = widget_contract.get("display") or {}
    binding = widget_contract.setdefault("artifact_binding", {})
    artifact_ref = display.get("artifact_ref")
    if isinstance(artifact_ref, dict):
        binding.setdefault("artifact_id", artifact_ref.get("fileId") or artifact_ref.get("artifact_id") or "")
        binding.setdefault("base_revision", artifact_ref.get("revision"))

    object_ids = list(binding.get("object_ids") or binding.get("stable_object_ids") or [])

    def add_object_ids(value: Any) -> None:
        records = value if isinstance(value, list) else [value]
        for record in records:
            if isinstance(record, str):
                object_ids.append(record)
            elif isinstance(record, dict):
                object_id = record.get("object_id") or record.get("id")
                if object_id:
                    object_ids.append(str(object_id))
                for key in ("object_ids", "target_object_ids", "target_hypotheses", "targets", "selected_stable_ids"):
                    if isinstance(record.get(key), list):
                        add_object_ids(record[key])

    for key in ("target_object_id", "target_object_ids", "target_objects", "objects", "targets", "compiled_operations", "proposals"):
        add_object_ids(display.get(key, []))
    add_object_ids(display.get("proposal", {}))
    interaction_spec = display.get("interaction_spec")
    if isinstance(interaction_spec, dict):
        add_object_ids(interaction_spec.get("default_target_ids", []))
        add_object_ids(interaction_spec.get("target_hypotheses", []))
        add_object_ids(interaction_spec.get("preview_operations", []))
    binding["object_ids"] = list(dict.fromkeys(object_id for object_id in object_ids if object_id))
    binding.setdefault("stable_object_ids", list(binding["object_ids"]))

    if widget_type == "svg_proposal_review":
        proposals = display.get("proposals") if isinstance(display.get("proposals"), list) else []
        recommended_id = str(display.get("recommended_proposal_id") or "")
        ordered_proposals = sorted(
            (proposal for proposal in proposals if isinstance(proposal, dict)),
            key=lambda proposal: str(proposal.get("proposal_id") or "") != recommended_id,
        )
        anchor_ids: list[str] = []
        for proposal in ordered_proposals:
            for key in ("target_object_ids", "targets", "selected_stable_ids"):
                if isinstance(proposal.get(key), list):
                    anchor_ids.extend(str(item) for item in proposal[key] if item)
            for target in proposal.get("target_hypotheses", []):
                if isinstance(target, dict) and target.get("object_id"):
                    anchor_ids.append(str(target["object_id"]))
        widget_contract["placement"] = {
            "mode": "anchored",
            "anchor": {"object_ids": list(dict.fromkeys(anchor_ids)), "preferred_side": "right"},
        }
    elif widget_type == "svg_artifact_review":
        widget_contract["placement"] = {"mode": "sidebar"}
    elif not widget_contract.get("placement"):
        if widget_type in SVG_OBJECT_WIDGET_TYPES | PROMPT_OBJECT_WIDGET_TYPES | P12_ARTIFACT_WIDGET_TYPES:
            widget_contract["placement"] = {"mode": "anchored", "anchor": {"object_ids": list(binding["object_ids"])}}
        elif widget_type == "svg_plan_review":
            widget_contract["placement"] = {"mode": "canvas_overlay"}
        else:
            widget_contract["placement"] = {"mode": "sidebar"}


def canonicalize_svg_widget_revision(widget_contract: dict[str, Any], session_id: str) -> None:
    widget_type = str(widget_contract.get("semantic_widget_type") or widget_contract.get("widget_type") or "")
    if not widget_type.startswith("svg_") and widget_type not in P12_ARTIFACT_WIDGET_TYPES:
        return
    display = widget_contract.get("display") or {}
    artifact_ref = display.get("artifact_ref")
    binding = widget_contract.get("artifact_binding") or {}
    file_id = str(
        (artifact_ref.get("fileId") if isinstance(artifact_ref, dict) else "")
        or binding.get("artifact_id")
        or binding.get("fileId")
        or ""
    )
    canonical_file_id = normalize_upload_file_id(file_id, session_id)
    path = uploads_store.upload_path(session_id, canonical_file_id)
    if path is None:
        return
    try:
        scene = svg_collage.inspect_svg_artifact(path)
    except svg_collage.SvgCollageError:
        try:
            scene = svg_document_manager.inspect_document(path, document_id=canonical_file_id, persist_normalization=False)
        except svg_document_manager.SvgDocumentError:
            return
    revision = scene.get("revision")
    if not isinstance(revision, int) or revision < 1:
        return
    if isinstance(artifact_ref, dict):
        artifact_ref["fileId"] = canonical_file_id
        artifact_ref["revision"] = revision
    binding["artifact_id"] = canonical_file_id
    binding["fileId"] = canonical_file_id
    binding["base_revision"] = revision
    binding["revision"] = revision
    widget_contract["artifact_binding"] = binding


class RenderCanvasWorkspaceParams(BaseModel):
    workspace_id: str | None = Field(default=None, description="Stable workspace id. Generated if omitted.")
    selected_widget_id: str | None = Field(default=None, description="Widget registry id selected by Layer 2 and preserved by Layer 3.")
    workspace_type: str = Field(description="Adapter id, for example prompt_node_graph.")
    planner_id: str | None = Field(default=None, description="Planner requesting the workspace.")
    interaction_goal: str = Field(description="What the workspace lets the user organize.")
    display: dict[str, Any] = Field(default_factory=dict, description="Semantic graph or map content from Layer 3; missing canonical state fields are copied into initial_state.")
    initial_state: dict[str, Any] = Field(default_factory=dict, description="Canonical adapter state used to open or restore the workspace.")
    capabilities: list[str] = Field(default_factory=list, description="Semantic interaction capabilities the adapter must expose.")
    presentation: dict[str, Any] = Field(default_factory=dict, description="Semantic workspace presentation profile from Layer 3.")
    expected_submit: dict[str, Any] = Field(default_factory=dict, description="Exact structured result returned on explicit workspace submission.")


def normalize_canvas_workspace(workspace: dict[str, Any]) -> dict[str, Any]:
    """Fill missing adapter state from the Layer 3 Canvas display contract."""
    display = workspace.pop("display", {})
    initial_state = workspace.setdefault("initial_state", {})
    for key in ("nodes", "edges", "relations", "fragments", "components", "cells", "viewport", "selected_node_id"):
        if key not in initial_state and key in display:
            initial_state[key] = display[key]
    if workspace.get("workspace_type") == "prompt_cell_map":
        workspace["workspace_type"] = "prompt_node_graph"
        workspace["interaction_goal"] = "organize_prompt_components"
        initial_state.setdefault("nodes", initial_state.get("cells", []))
        initial_state.setdefault("edges", initial_state.get("relations", []))
    if workspace.get("workspace_type") == "prompt_node_graph":
        _materialize_prompt_graph_nodes(initial_state)
    return workspace


def _materialize_prompt_graph_nodes(initial_state: dict[str, Any]) -> None:
    """Adapt P6 component lists into the node shape required by React Flow."""
    fragments = initial_state.get("fragments")
    if not isinstance(fragments, list):
        fragments = initial_state.get("components")
    if not isinstance(fragments, list):
        fragments = []
    initial_state["fragments"] = fragments

    nodes = initial_state.get("nodes")
    if isinstance(nodes, list) and nodes:
        return

    materialized_nodes: list[dict[str, Any]] = []
    for index, fragment in enumerate(fragments):
        if not isinstance(fragment, dict):
            continue
        fragment_id = str(fragment.get("id") or f"component-{index + 1}")
        fragment.setdefault("id", fragment_id)
        label = str(fragment.get("kind") or "Prompt component").replace("_", " ").title()
        materialized_nodes.append({
            "id": f"node-{fragment_id}",
            "stage": str(fragment.get("kind") or "component"),
            "label": label,
            "fragment_ids": [fragment_id],
            "source_prompt_ids": list(fragment.get("source_prompt_ids") or []),
            "x": 80 + (index % 3) * 290,
            "y": 100 + (index // 3) * 190,
        })
    initial_state["nodes"] = materialized_nodes


class InspectSvgAccessibilityParams(BaseModel):
    file_id: str = Field(description="Stable fileId of an uploaded SVG in the active session.")


class PatchSvgAccessibilityParams(BaseModel):
    file_id: str = Field(description="Stable fileId of an uploaded SVG in the active session.")
    base_revision: int = Field(description="Revision returned by the latest SVG inspection.")
    operations: list[dict[str, Any]] = Field(description="Allowlisted SVG accessibility patch operations.")


class InspectSvgCollageParams(BaseModel):
    file_id: str = Field(description="Stable fileId of an uploaded layered SVG collage in the active session.")


class ManageSvgDocumentParams(BaseModel):
    action: Literal["validate", "import", "adopt_generated", "inspect", "patch"] = Field(description="One SVG document lifecycle action.")
    file_id: str = Field(description="Stable fileId of an SVG in the active session; never pass raw SVG or a filesystem path.")
    scene_kind_hint: Literal["general", "collage", "diagram", "chart", "illustration"] | None = Field(default=None, description="Optional profile hint used only while importing or adopting a generated SVG.")
    base_revision: int | None = Field(default=None, description="Required optimistic-concurrency revision for patch.")
    operations: list[dict[str, Any]] = Field(default_factory=list, description="Allowlisted typed operations for patch; raw XML, CSS, selectors, and path data are forbidden.")


class InspectSvgSceneParams(BaseModel):
    file_id: str = Field(description="Stable fileId of the SVG bound to the current widget workflow.")


class ApplySvgOperationsParams(BaseModel):
    file_id: str = Field(description="Stable fileId of the SVG bound to the current widget workflow.")
    base_revision: int = Field(description="Current canonical SVG revision bound to the widget return.")
    operations: list[dict[str, Any]] = Field(description="Non-empty typed operations from the compatible widget family.")


SVG_PRESENTATION_OPERATIONS = frozenset({"set_object_style", "set_attributes", "set_text", "update_text"})
SVG_LAYOUT_OPERATIONS = frozenset({"set_transform", "set_order", "set_dom_order"})
SVG_STRUCTURE_OPERATIONS = frozenset({"add_cutout", "remove_element", "remove_object", "replace_asset", "replace_cutout_asset"})


def _validate_svg_operation_family(operations: list[dict[str, Any]], allowed: frozenset[str], family: str) -> str | None:
    if not operations:
        return f"{family} requires at least one operation."
    for index, operation in enumerate(operations, start=1):
        if not isinstance(operation, dict):
            return f"{family} operation {index} must be an object."
        name = str(operation.get("op") or "")
        if name not in allowed:
            return f"{family} does not support operation '{name or 'missing'}'."
    return None


class InspectInflakAuthoringResourcesParams(BaseModel):
    resources: list[dict[str, Any]] = Field(description="Uploaded authoring resources identified by stable fileId, purpose, and whether each is required.")


class PreviewInflakPluginParams(BaseModel):
    target_spec: dict[str, Any] = Field(description="Internal target-plugin specification derived from the approved experience blueprint.")
    approved_revision: int = Field(description="Positive authoring revision approved in the experience review.")


class PublishInflakPluginParams(BaseModel):
    preview_id: str = Field(description="Immutable preview id returned by preview_inflak_plugin.")
    preview_hash: str = Field(description="Exact SHA-256 bundle hash explicitly approved by the user.")
    approved_revision: int = Field(description="Exact authoring revision bound to the approved preview.")


def validate_p12_interaction_display(display: dict[str, Any]) -> list[str]:
    interaction_spec = display.get("interaction_spec")
    if not isinstance(interaction_spec, dict):
        return ["display.interaction_spec is required"]
    if not str(interaction_spec.get("interaction_id") or "").strip():
        return ["interaction_spec.interaction_id is required"]
    if not isinstance(interaction_spec.get("controls"), list) or not interaction_spec["controls"]:
        return ["interaction_spec.controls must contain at least one task-specific control"]
    operations = interaction_spec.get("preview_operations")
    if not isinstance(operations, list) or not operations:
        return ["at least one concrete preview operation is required"]
    errors: list[str] = []
    targeted = {"update_text", "remove_object", "replace_cutout_asset", "set_transform", "set_order", "set_object_style"}
    supported = targeted | {"add_text", "add_cutout"}
    for index, operation in enumerate(operations, start=1):
        if not isinstance(operation, dict):
            errors.append(f"operation {index} must be an object")
            continue
        name = str(operation.get("op") or "")
        if name not in supported:
            errors.append(f"operation {index} has unsupported op '{name or 'missing'}'")
            continue
        if name in targeted and not str(operation.get("object_id") or "").strip():
            errors.append(f"operation {index} ({name}) requires object_id")
        if name in {"update_text", "add_text"} and not str(operation.get("text") or "").strip():
            errors.append(f"operation {index} ({name}) requires the actual non-empty text")
        if name == "set_object_style" and not isinstance(operation.get("style"), dict):
            errors.append(f"operation {index} (set_object_style) requires a style object")
        if name in {"add_cutout", "replace_cutout_asset"} and not str(operation.get("asset_file_id") or "").strip():
            errors.append(f"operation {index} ({name}) requires asset_file_id")
        if name == "set_order" and operation.get("direction") not in {"front", "back", "forward", "backward"}:
            errors.append(f"operation {index} (set_order) requires a supported direction")
        if name == "set_transform" and not any(key in operation for key in ("translate", "scale", "rotate", "rotation", "x", "y")):
            errors.append(f"operation {index} (set_transform) requires transform values")
    return errors


def validate_p12_recommendation_display(display: dict[str, Any]) -> list[str]:
    """Compatibility wrapper for callers migrating to interaction specs."""
    recommendation = display.get("recommendation")
    if isinstance(recommendation, dict) and "interaction_spec" not in display:
        display = {
            "interaction_spec": {
                "interaction_id": recommendation.get("recommendation_id", "legacy-recommendation"),
                "controls": [],
                "preview_operations": recommendation.get("proposed_operations"),
            }
        }
    return validate_p12_interaction_display(display)


def build_iai_tools(session_ref: dict[str, Any]) -> list[Tool]:
    """Build the two renderer bridge tools that the inflak plugin needs.

    Everything else in the chain (state assessment, routing, drafting, rewriting,
    claim generation) is performed by the model directly under the layer skills.
    Only frontend rendering requires a tool because it needs the live web session's
    async widget round-trip (Future + WebSocket).
    """

    @define_tool(
        "render_interactive_widget",
        description="Render a schema-driven interactive widget in the Web Chat frontend and return structured human input to the agent loop.",
        skip_permission=True,
        defer="never",
    )
    async def render_interactive_widget(params: RenderWidgetParams, invocation: ToolInvocation) -> dict[str, Any]:
        web_session = session_ref.get("session")
        if web_session is None:
            return {"action": "error", "message": "No active web session is available for widget rendering."}
        tracker = getattr(web_session, "layer_order", None)
        if tracker is not None:
            blocked = tracker.block_render("render_interactive_widget")
            if blocked is not None:
                return blocked
        widget_contract = params.model_dump()
        widget_contract["widget_id"] = widget_contract.get("widget_id") or str(uuid.uuid4())
        widget_contract["display"] = normalize_widget_image_refs(widget_contract["display"], web_session.session_id)
        normalize_svg_widget_binding(widget_contract)
        canonicalize_svg_widget_revision(widget_contract, web_session.session_id)
        artifact_ref = widget_contract["display"].get("artifact_ref")
        if widget_contract["widget_type"] == "svg_proposal_review" and isinstance(artifact_ref, dict):
            widget_contract["surface"] = "artifact_canvas_widget"
            binding = widget_contract["artifact_binding"]
            binding.setdefault("artifact_id", artifact_ref.get("fileId", ""))
            binding.setdefault("base_revision", artifact_ref.get("revision"))
            proposals = widget_contract["display"].get("proposals", [])
            binding.setdefault("object_ids", list(dict.fromkeys(
                str(object_id)
                for proposal in proposals if isinstance(proposal, dict)
                for object_id in proposal.get("target_object_ids", [])
                if object_id
            )))
        return await web_session.render_widget(widget_contract)

    @define_tool(
        "render_html_widget",
        description=(
            "Render an LLM-generated HTML/CSS/JS widget in a sandboxed iframe in the Web Chat frontend, "
            "then return structured user input. The widget JavaScript must call window.submitWidget(values). "
            "Images must come from display and use window.widgetAssetUrl(ref); never construct file:// URLs or assign raw local paths."
        ),
        skip_permission=True,
        defer="never",
    )
    async def render_html_widget(params: RenderHtmlWidgetParams, invocation: ToolInvocation) -> dict[str, Any]:
        web_session = session_ref.get("session")
        if web_session is None:
            return {"action": "error", "message": "No active web session is available for HTML widget rendering."}
        tracker = getattr(web_session, "layer_order", None)
        if tracker is not None:
            blocked = tracker.block_render("render_html_widget")
            if blocked is not None:
                return blocked
        widget_contract = params.model_dump()
        if params.widget_type == "adaptive_refinement_interaction":
            validation_errors = validate_p12_interaction_display(widget_contract["display"])
            if validation_errors:
                return {"action": "validation_error", "message": "; ".join(validation_errors)}
        widget_contract["widget_id"] = widget_contract.get("widget_id") or str(uuid.uuid4())
        widget_contract["display"] = normalize_widget_image_refs(widget_contract["display"], web_session.session_id)
        widget_contract["semantic_widget_type"] = params.widget_type
        normalize_svg_widget_binding(widget_contract)
        canonicalize_svg_widget_revision(widget_contract, web_session.session_id)
        artifact_binding = widget_contract.get("artifact_binding")
        if isinstance(artifact_binding, dict) and artifact_binding.get("artifact_id"):
            canonical_artifact_id = normalize_upload_file_id(artifact_binding["artifact_id"], web_session.session_id)
            if canonical_artifact_id:
                artifact_binding["artifact_id"] = canonical_artifact_id
        if params.render_mode == "template":
            templated = apply_widget_template(
                params.widget_type,
                display=widget_contract["display"],
                controls=params.controls,
                interaction_goal=params.interaction_goal,
            )
            if templated is not None:
                widget_contract["html"] = templated["html"]
                widget_contract["css"] = templated["css"]
                widget_contract["js"] = templated["js"]
                if templated.get("height"):
                    widget_contract["height"] = templated["height"]
                widget_contract["templated_widget_type"] = params.widget_type
                widget_contract["template_meta"] = templated["meta"]
        for field in ("html", "css", "js"):
            widget_contract[field] = normalize_widget_upload_urls(
                widget_contract.get(field, ""), web_session.session_id
            )
        widget_contract["widget_type"] = "html_widget"
        return await web_session.render_widget(widget_contract)

    @define_tool(
        "render_canvas_workspace",
        description=(
            "Open a persistent host-level canvas workspace for a Layer 3 graph, spatial, or timeline interaction. "
            "It returns structured input only when the user explicitly submits or dismisses the workspace."
        ),
        skip_permission=True,
        defer="never",
    )
    async def render_canvas_workspace(params: RenderCanvasWorkspaceParams, invocation: ToolInvocation) -> dict[str, Any]:
        web_session = session_ref.get("session")
        if web_session is None:
            return {"action": "error", "message": "No active web session is available for canvas rendering."}
        tracker = getattr(web_session, "layer_order", None)
        if tracker is not None:
            blocked = tracker.block_render("render_canvas_workspace")
            if blocked is not None:
                return blocked
        workspace = normalize_canvas_workspace(params.model_dump())
        workspace["workspace_id"] = workspace.get("workspace_id") or str(uuid.uuid4())
        return await web_session.render_workspace(workspace)

    @define_tool(
        "inspect_svg_collage",
        description="Read and validate a layered SVG collage scene for stable object-grounded instruction authoring without returning SVG markup.",
        skip_permission=True,
        defer="never",
    )
    async def inspect_svg_collage(params: InspectSvgCollageParams, invocation: ToolInvocation) -> dict[str, Any]:
        web_session = session_ref.get("session")
        if web_session is None:
            return {"action": "error", "message": "No active web session is available for collage inspection."}
        tracker = getattr(web_session, "layer_order", None)
        if tracker is not None:
            blocked = tracker.block_tool("inspect_svg_collage")
            if blocked is not None:
                return blocked
        file_id = normalize_upload_file_id(params.file_id, web_session.session_id)
        path = uploads_store.upload_path(web_session.session_id, file_id)
        if path is None or path.suffix.lower() != ".svg":
            return {"action": "error", "message": "SVG collage artifact not found."}
        try:
            scene = svg_collage.inspect_svg_artifact(path)
        except svg_collage.SvgCollageError as error:
            return {"action": "validation_error", "message": str(error)}
        return {"action": "svg_collage_inspected", "fileId": file_id, **scene}

    async def _manage_svg_document(params: ManageSvgDocumentParams, tool_name: str) -> dict[str, Any]:
        web_session = session_ref.get("session")
        if web_session is None:
            return {"action": "error", "message": "No active web session is available for SVG document management."}
        tracker = getattr(web_session, "layer_order", None)
        if tracker is not None:
            blocked = tracker.block_tool(tool_name)
            if blocked is not None:
                return blocked
        file_id = normalize_upload_file_id(params.file_id, web_session.session_id)
        path = uploads_store.upload_path(web_session.session_id, file_id)
        if path is None or path.suffix.lower() != ".svg":
            return {"action": "error", "message": "SVG document not found."}
        try:
            result = svg_document_manager.manage_document(
                path,
                action=params.action,
                document_id=file_id,
                session_id=web_session.session_id,
                scene_kind_hint=params.scene_kind_hint,
                base_revision=params.base_revision,
                operations=params.operations,
            )
        except svg_document_manager.SvgDocumentError as error:
            action = "revision_conflict" if "Revision conflict" in str(error) else "validation_error"
            return {"action": action, "message": str(error)}
        scene = result.get("scene")
        attachment = {
            "fileId": file_id,
            "name": path.name.split("-", 1)[-1],
            "mime": "image/svg+xml",
            "size": path.stat().st_size,
            "artifactType": "svg-document",
            "revision": scene.get("revision") if isinstance(scene, dict) else None,
            "scene": scene,
            "url": f"/api/sessions/{web_session.session_id}/uploads/{file_id}",
        }
        if params.action in {"import", "adopt_generated", "patch"}:
            emit = getattr(web_session, "emit", None)
            if callable(emit):
                await emit({
                    "type": "artifact_generated",
                    "attachment": attachment,
                    "artifactType": "svg-document",
                    "scene": scene,
                })
        if params.action == "patch":
            return {
                "action": result.get("action", "svg_document_patched"),
                "fileId": file_id,
                "revision": scene.get("revision") if isinstance(scene, dict) else None,
                "scene": scene,
                "scene_kind": scene.get("scene_kind") if isinstance(scene, dict) else None,
                "object_count": len(scene.get("objects", [])) if isinstance(scene, dict) else 0,
                "applied_operations": result.get("applied_operations", params.operations),
                "validation": result.get("validation"),
                "attachment": {
                    "fileId": attachment["fileId"],
                    "name": attachment["name"],
                    "mime": attachment["mime"],
                    "artifactType": attachment["artifactType"],
                    "revision": attachment["revision"],
                    "url": attachment["url"],
                },
            }
        return {**result, "fileId": file_id, "attachment": attachment}

    @define_tool(
        "manage_svg_document",
        description=(
            "Manage any safe uploaded or generated SVG through validate, sanitize, normalize, persist, and inspect. "
            "Import/adopt assigns persistent object ids and canonical metadata; inspect returns capabilities; patch "
            "commits typed operations against base_revision and then revalidates the resulting artifact."
        ),
        skip_permission=True,
        defer="never",
    )
    async def manage_svg_document(params: ManageSvgDocumentParams, invocation: ToolInvocation) -> dict[str, Any]:
        return await _manage_svg_document(params, "manage_svg_document")

    @define_tool(
        "inspect_svg_scene",
        description="Inspect one canonical SVG scene for object-grounded widget binding without exposing raw SVG markup.",
        skip_permission=True,
        defer="never",
    )
    async def inspect_svg_scene(params: InspectSvgSceneParams, invocation: ToolInvocation) -> dict[str, Any]:
        return await _manage_svg_document(ManageSvgDocumentParams(action="inspect", file_id=params.file_id), "inspect_svg_scene")

    @define_tool(
        "apply_svg_presentation",
        description="Apply only user-confirmed SVG presentation or text operations from a compatible property/action widget.",
        skip_permission=True,
        defer="never",
    )
    async def apply_svg_presentation(params: ApplySvgOperationsParams, invocation: ToolInvocation) -> dict[str, Any]:
        error = _validate_svg_operation_family(params.operations, SVG_PRESENTATION_OPERATIONS, "apply_svg_presentation")
        if error:
            return {"action": "validation_error", "message": error}
        return await _manage_svg_document(
            ManageSvgDocumentParams(action="patch", file_id=params.file_id, base_revision=params.base_revision, operations=params.operations),
            "apply_svg_presentation",
        )

    @define_tool(
        "apply_svg_layout",
        description="Apply only user-confirmed transform or order operations from a compatible SVG layout widget.",
        skip_permission=True,
        defer="never",
    )
    async def apply_svg_layout(params: ApplySvgOperationsParams, invocation: ToolInvocation) -> dict[str, Any]:
        error = _validate_svg_operation_family(params.operations, SVG_LAYOUT_OPERATIONS, "apply_svg_layout")
        if error:
            return {"action": "validation_error", "message": error}
        return await _manage_svg_document(
            ManageSvgDocumentParams(action="patch", file_id=params.file_id, base_revision=params.base_revision, operations=params.operations),
            "apply_svg_layout",
        )

    @define_tool(
        "apply_svg_structure",
        description="Apply only user-confirmed add, remove, or raster replacement operations from a compatible semantic SVG widget.",
        skip_permission=True,
        defer="never",
    )
    async def apply_svg_structure(params: ApplySvgOperationsParams, invocation: ToolInvocation) -> dict[str, Any]:
        error = _validate_svg_operation_family(params.operations, SVG_STRUCTURE_OPERATIONS, "apply_svg_structure")
        if error:
            return {"action": "validation_error", "message": error}
        return await _manage_svg_document(
            ManageSvgDocumentParams(action="patch", file_id=params.file_id, base_revision=params.base_revision, operations=params.operations),
            "apply_svg_structure",
        )

    @define_tool(
        "inspect_inflak_authoring_resources",
        description="Statically inspect uploaded Skill, Python, OpenAPI, schema, template, or documentation resources for plugin authoring without executing source code.",
        skip_permission=True,
        defer="never",
    )
    async def inspect_inflak_authoring_resources(params: InspectInflakAuthoringResourcesParams, invocation: ToolInvocation) -> dict[str, Any]:
        web_session = session_ref.get("session")
        if web_session is None:
            return {"action": "error", "message": "No active web session is available for plugin authoring."}
        if getattr(web_session, "current_plugin_id", "") != "inflak-author":
            return {"action": "error", "message": "Authoring resource inspection is available only through inflak-author."}
        tracker = getattr(web_session, "layer_order", None)
        if tracker is not None:
            blocked = tracker.block_tool("inspect_inflak_authoring_resources")
            if blocked is not None:
                return blocked
        return inflak_plugin_author.inspect_authoring_resources(web_session.session_id, params.resources)

    @define_tool(
        "preview_inflak_plugin",
        description="Compile and validate an immutable staging preview of a complete four-layer inflak plugin without changing the ready plugin tree.",
        skip_permission=True,
        defer="never",
    )
    async def preview_inflak_plugin(params: PreviewInflakPluginParams, invocation: ToolInvocation) -> dict[str, Any]:
        web_session = session_ref.get("session")
        if web_session is None:
            return {"action": "error", "message": "No active web session is available for plugin authoring."}
        if getattr(web_session, "current_plugin_id", "") != "inflak-author":
            return {"action": "error", "message": "Plugin preview is available only through inflak-author."}
        tracker = getattr(web_session, "layer_order", None)
        if tracker is not None:
            blocked = tracker.block_tool("preview_inflak_plugin")
            if blocked is not None:
                return blocked
        try:
            return inflak_plugin_author.preview_plugin(
                web_session.session_id,
                params.target_spec,
                params.approved_revision,
            )
        except inflak_plugin_author.InflakAuthoringError as error:
            return {"action": "validation_error", "message": str(error)}

    @define_tool(
        "publish_inflak_plugin",
        description="Publish exactly one immutable inflak plugin staging bundle after matching the user's hash-bound build approval in the current session.",
        skip_permission=True,
        defer="never",
    )
    async def publish_inflak_plugin(params: PublishInflakPluginParams, invocation: ToolInvocation) -> dict[str, Any]:
        web_session = session_ref.get("session")
        if web_session is None:
            return {"action": "error", "message": "No active web session is available for plugin authoring."}
        if getattr(web_session, "current_plugin_id", "") != "inflak-author":
            return {"action": "error", "message": "Plugin publication is available only through inflak-author."}
        tracker = getattr(web_session, "layer_order", None)
        if tracker is not None:
            blocked = tracker.block_tool("publish_inflak_plugin")
            if blocked is not None:
                return blocked
        approved = False
        acknowledged_warnings: list[str] = []
        for result in reversed(getattr(web_session, "widget_returns", [])):
            values = result.get("values") if isinstance(result.get("values"), dict) else {}
            if (
                result.get("planner_id") == "inflak-authoring"
                and str(values.get("decision") or "").lower() == "publish"
                and values.get("preview_id") == params.preview_id
                and values.get("preview_hash") == params.preview_hash
                and values.get("approved_revision") == params.approved_revision
            ):
                approved = True
                acknowledged_warnings = [
                    str(item) for item in values.get("acknowledged_warnings") or []
                ]
                break
        if not approved:
            return {
                "action": "approval_required",
                "message": "Publish requires a matching build-review return for this preview id, hash, and revision.",
            }
        try:
            result = inflak_plugin_author.publish_plugin(
                web_session.session_id,
                params.preview_id,
                params.preview_hash,
                params.approved_revision,
                acknowledged_warnings=acknowledged_warnings,
            )
        except inflak_plugin_author.InflakAuthoringError as error:
            return {"action": "validation_error", "message": str(error)}
        if result.get("plugin_status") != "ready" or not (result.get("installed_validation") or {}).get("ok"):
            return result
        owner_service = getattr(web_session, "owner_service", None)
        if owner_service is None:
            runtime_validation = {
                "ok": False,
                "plugin_id": result["plugin_id"],
                "root_skill_loaded": False,
                "error": "Host service is unavailable for runtime smoke validation.",
            }
        else:
            runtime_validation = await owner_service.validate_published_plugin_runtime(result["plugin_id"])
        result["runtime_validation"] = runtime_validation
        result["runtime_restart_required"] = not runtime_validation["ok"]
        if not runtime_validation["ok"]:
            inflak_plugin_author.set_plugin_status(result["plugin_id"], "planned")
            result["action"] = "inflak_plugin_published_validation_failed"
            result["plugin_status"] = "planned"
            result["message"] = "Plugin files were installed, but runtime skill loading failed; status was downgraded to planned."
        else:
            try:
                scenario_run = await plugin_scenario_runner.run_probe_case(owner_service, result["plugin_id"])
                result["scenario_validation"] = {
                    "ok": bool(scenario_run.get("evaluation", {}).get("passed")),
                    "run_id": scenario_run["run_id"],
                    "case_id": scenario_run.get("case", {}).get("id"),
                    "session_id": scenario_run["session_id"],
                    "status": scenario_run["status"],
                    "evaluation": scenario_run.get("evaluation") or {},
                    "report_url": f"/api/inflak/plugins/{result['plugin_id']}/scenario-runs/{scenario_run['run_id']}/report",
                }
            except Exception as error:  # noqa: BLE001
                result["scenario_validation"] = {
                    "ok": False,
                    "status": "runner_error",
                    "error": str(error),
                }
            if not result["scenario_validation"]["ok"]:
                inflak_plugin_author.set_plugin_status(result["plugin_id"], "planned")
                result["action"] = "inflak_plugin_published_validation_failed"
                result["plugin_status"] = "planned"
                result["runtime_ready"] = False
                result["message"] = "Plugin files were installed, but the required real-session scenario failed; status was downgraded to planned."
            else:
                result["runtime_ready"] = True
                result["message"] = "Plugin installed, its root skill loaded, and its required real-session scenario passed."
        await web_session.emit({
            "type": "plugins_updated",
            "pluginId": result["plugin_id"],
            "status": result["plugin_status"],
            "runtimeReady": bool(result.get("runtime_ready")),
        })
        return result

    @define_tool(
        "inspect_svg_accessibility",
        description="Safely parse an uploaded SVG and return stable objects, presentation properties, reading-order evidence, and deterministic accessibility findings.",
        skip_permission=True,
        defer="never",
    )
    async def inspect_svg_accessibility(params: InspectSvgAccessibilityParams, invocation: ToolInvocation) -> dict[str, Any]:
        web_session = session_ref.get("session")
        if web_session is None:
            return {"action": "error", "message": "No active web session is available for SVG inspection."}
        tracker = getattr(web_session, "layer_order", None)
        if tracker is not None:
            blocked = tracker.block_tool("inspect_svg_accessibility")
            if blocked is not None:
                return blocked
        path = uploads_store.upload_path(web_session.session_id, params.file_id)
        if path is None or path.suffix.lower() != ".svg":
            return {"action": "error", "message": "SVG artifact not found."}
        try:
            report = svg_accessibility.inspect_svg(path)
        except svg_accessibility.SvgAccessibilityError as error:
            return {"action": "validation_error", "message": str(error)}
        return {**report, "fileId": params.file_id}

    @define_tool(
        "patch_svg_accessibility",
        description="Apply revisioned allowlisted property, text, accessible-name, description, or sibling-order changes to an uploaded SVG.",
        skip_permission=True,
        defer="never",
    )
    async def patch_svg_accessibility(params: PatchSvgAccessibilityParams, invocation: ToolInvocation) -> dict[str, Any]:
        web_session = session_ref.get("session")
        if web_session is None:
            return {"action": "error", "message": "No active web session is available for SVG patching."}
        tracker = getattr(web_session, "layer_order", None)
        if tracker is not None:
            blocked = tracker.block_tool("patch_svg_accessibility")
            if blocked is not None:
                return blocked
        path = uploads_store.upload_path(web_session.session_id, params.file_id)
        if path is None or path.suffix.lower() != ".svg":
            return {"action": "error", "message": "SVG artifact not found."}
        try:
            result = svg_accessibility.apply_svg_patch(path, params.base_revision, params.operations)
        except svg_accessibility.SvgAccessibilityError as error:
            action = "revision_conflict" if "Revision conflict" in str(error) else "validation_error"
            return {"action": action, "message": str(error)}
        return {
            "action": "svg_accessibility_patched",
            "fileId": params.file_id,
            "revision": result["revision"],
            "applied_operations": result["applied_operations"],
            "accessibility_report": result["report"],
        }

    return [
        render_interactive_widget,
        render_html_widget,
        render_canvas_workspace,
        inspect_svg_collage,
        manage_svg_document,
        inspect_svg_scene,
        apply_svg_presentation,
        apply_svg_layout,
        apply_svg_structure,
        inspect_inflak_authoring_resources,
        preview_inflak_plugin,
        publish_inflak_plugin,
        inspect_svg_accessibility,
        patch_svg_accessibility,
    ]
