"""Compile conversational authoring specs into independent inflak plugins.

The authoring agent owns intent interpretation. This module owns deterministic
adaptation, validation, staging, and publication. Preview never writes to the
ready plugin tree. Publication accepts only an immutable preview identity.
Uploaded source is inspected and packaged as data; it is never executed here.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import shutil
import uuid
from pathlib import Path
from typing import Any

from backend.services import uploads_store
from backend.services.chat_store import safe_session_id
from backend.services.taskpack_author import (
    LOCAL_WIDGET_HANDOFF,
    _local_widget_contract_issues,
    _return_schema_rows,
    _skill_structure_issues,
)


PROJECT_DIR = Path(__file__).resolve().parents[2]
PLUGINS_DIR = PROJECT_DIR / "plugins"
MANIFEST_PATH = PLUGINS_DIR / "inflak-plugins.json"
AUTHORING_ROOT = PROJECT_DIR / "data" / "plugin_authoring"
CONTRACT_DIR = PLUGINS_DIR / "inflak-main" / "contract"
CANONICAL_CONTRACT_PATH = CONTRACT_DIR / "CONTRACT.md"
L2_CONTRACT_PATH = CONTRACT_DIR / "l2-skill-contract.md"
L3_CONTRACT_PATH = CONTRACT_DIR / "l3-skill-contract.md"

VALID_IAI_EDGES = frozenset({
    "H→T",
    "H→I",
    "T→Aug",
    "T→G",
    "I→Aug",
    "I→T",
    "I→A",
    "Aug→G",
    "A→Aug",
    "A→G",
    "G→A",
    "G→I",
})
EXECUTION_MODES = frozenset({"host_agent", "image_tool", "imported_skill", "uploaded_runtime", "external_service"})
GPT_IMAGE_TOOL_EXECUTORS = {
    "generate_image": "Generate a new image from a confirmed prompt.",
    "edit_image": "Edit a source image from a confirmed instruction.",
    "restyle_image": "Restyle a source image while preserving its subject.",
    "outpaint_image": "Extend a source image beyond its current bounds.",
    "remove_background": "Remove a source image background and return a transparent PNG.",
    "extract_collage_cutouts": "Extract confirmed source objects as transparent cutout candidates.",
    "replace_background": "Replace the background of a source image.",
    "generate_variations": "Generate visual variations of a source image.",
}
STATE_VISIBILITY = frozenset({"visible", "summary", "internal"})
STATE_RETENTION = frozenset({"session", "revision", "final"})
STAGE_ACTORS = frozenset({"user", "ai", "shared", "executor"})
INTERACTION_SURFACES = frozenset({"conversation_widget", "artifact_canvas_widget"})
WORKFLOW_EFFECTS = frozenset({"continue", "complete", "cancel", "escape"})
INTERACTION_ARCHETYPES = frozenset({
    "structured_input",
    "decision_review",
    "comparison_review",
    "structured_editor",
    "ordered_editor",
    "selection_gallery",
    "continuous_control",
    "annotation_surface",
    "progress_inspector",
    "result_review",
    "resource_intake",
})
INTERACTION_PRIMITIVES = {
    "structured_input": "structured_input_form",
    "decision_review": "decision_review",
    "comparison_review": "comparison_review",
    "structured_editor": "structured_editor",
    "ordered_editor": "ordered_editor",
    "selection_gallery": "selection_gallery",
    "continuous_control": "continuous_control",
    "annotation_surface": "annotation_surface",
    "progress_inspector": "progress_inspector",
    "result_review": "result_review",
    "resource_intake": "resource_intake",
}
TEXT_RESOURCE_SUFFIXES = frozenset({".md", ".txt", ".py", ".json", ".yaml", ".yml"})
MAX_AUTHORING_RESOURCE_BYTES = 2 * 1024 * 1024
PLUGIN_ID_RE = re.compile(r"^inflak-[a-z][a-z0-9-]{1,54}[a-z0-9]$")
SKILL_NAME_MAX_LENGTH = 64
SAFE_ENV_RE = re.compile(r"^[A-Z][A-Z0-9_]{2,80}$")
SECRET_VALUE_RE = re.compile(
    r"(?i)(?:api[_-]?key|access[_-]?token|password|client[_-]?secret)\s*[:=]\s*['\"]?[A-Za-z0-9+/_.=-]{12,}"
)
FRONTMATTER_NAME_RE = re.compile(r"^name:\s*(\S+)\s*$", re.MULTILINE)
H1_RE = re.compile(r"^#\s+\S.*$", re.MULTILINE)


class InflakAuthoringError(ValueError):
    """Raised when an authoring resource, spec, preview, or publication is invalid."""


def _slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(value or "").strip().lower()).strip("-")


def _bounded_skill_name(*parts: str, max_length: int = SKILL_NAME_MAX_LENGTH) -> str:
    """Build an SDK-callable skill name without exceeding runtime name limits."""
    name = _slugify("-".join(str(part or "") for part in parts))
    if len(name) <= max_length:
        return name
    digest = hashlib.sha1(name.encode("utf-8")).hexdigest()[:8]
    available = max_length - len(digest) - 1
    if available < 12:
        raise InflakAuthoringError("Skill name limit is too small for stable generated names.")
    prefix = name[:available].rstrip("-")
    return f"{prefix}-{digest}"


def _identifier(value: str, fallback: str) -> str:
    identifier = re.sub(r"[^a-z0-9]+", "_", str(value or "").strip().lower()).strip("_")
    return identifier or fallback


def _markdown(value: Any) -> str:
    return str(value or "").replace("\n", " ").replace("|", "\\|").strip()


def _yaml_quote(value: Any) -> str:
    return json.dumps(str(value or ""), ensure_ascii=False)


def _safe_resource_name(path: Path) -> str:
    original = path.name.split("-", 1)[1] if "-" in path.name else path.name
    cleaned = re.sub(r"[^A-Za-z0-9._-]", "_", original)[-120:]
    return cleaned or "resource.txt"


def _load_manifest(path: Path) -> dict[str, Any]:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise InflakAuthoringError(f"Plugin manifest is unavailable or invalid: {error}") from error
    if not isinstance(manifest.get("plugins"), list):
        raise InflakAuthoringError("Plugin manifest must contain a plugins array.")
    return manifest


def canonical_contract_reference() -> dict[str, Any]:
    """Return the internal contract reference used by authoring and validation."""
    documents = []
    issues: list[str] = []
    requirements = {
        CANONICAL_CONTRACT_PATH: (
            "## Scope and References",
            "## Skill Document Structure",
            "## Protocol Invariants",
            "## Workflow End Authority",
            "## Layer Ownership",
            "## Pass State and Loop",
            "## L1 Router Contract",
            "## L2 Planner Contract",
            "## L3 Designer Contract",
            "## L4 Renderer Contract",
            "## Registry Contract",
            "## Return Field Policies",
            "## Authoring and Publication",
            "## Validation and Acceptance",
        ),
        L2_CONTRACT_PATH: (
            "# L2 Planner Skill Contract",
            "## Layer & Role",
            "## Workflow End Authority",
            "## Layer Routing",
            "## Input Contract",
            "## Required Sections",
            "## L2 Diagnosis Authoring Method",
            "## Semantic Requirements",
            "## Output Requirements",
            "## Validation",
        ),
        L3_CONTRACT_PATH: (
            "# L3 Designer Skill Contract",
            "## Layer & Role",
            "## Required Sections",
            "## Inputs",
            "## Widget Profile Authoring Method",
            "## Essential Constraints",
            "## Validation",
            "## Output and Handoff",
            "## Workflow End Authority",
        ),
    }
    for path, required_sections in requirements.items():
        if not path.is_file():
            issues.append(f"missing canonical contract: {path.name}")
            continue
        text = path.read_text(encoding="utf-8")
        headings = {line.strip() for line in text.splitlines() if line.startswith(("# ", "## "))}
        missing = [section for section in required_sections if section not in headings]
        issues.extend(f"{path.name}: missing section {section}" for section in missing)
        documents.append({
            "path": str(path.relative_to(PROJECT_DIR)),
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "required_sections": list(required_sections),
            "missing_sections": missing,
        })
    return {
        "ok": not issues,
        "documents": documents,
        "issues": issues,
        "checks": [
            "skill document identity and structure",
            "L1 state and planner routing",
            "L2 single-mode handoff and selected widget eligibility",
            "L3 selected-widget preservation and semantic contract",
            "L4 unchanged render mapping and return fields",
            "planner/widget/tool registry references",
            "return-field policy coverage",
            "runtime executor callable registration",
        ],
    }


def runtime_tool_bindings() -> dict[str, dict[str, Any]]:
    """Build the host and plugin MCP tool catalog without invoking handlers."""
    from backend.services.execution_tools.inflak_tools import build_iai_tools
    from backend.services.execution_tools.image_tools import build_image_tools
    from backend.services.inflak_plugins import runtime_mcp_tool_bindings

    tools = build_iai_tools({}) + build_image_tools({})
    bindings = {
        str(tool.name): {
            "name": str(tool.name),
            "handler_callable": callable(getattr(tool, "handler", None)),
            "transport": "host",
        }
        for tool in tools
    }
    bindings.update(runtime_mcp_tool_bindings())
    return bindings


def validate_runtime_bindings(files: dict[str, bytes]) -> dict[str, Any]:
    """Verify declared executors resolve to concrete host tool handlers."""
    try:
        tool_entries = json.loads(files["registry/tools.json"].decode("utf-8"))["tools"]
    except (KeyError, TypeError, json.JSONDecodeError, UnicodeDecodeError) as error:
        return {"ok": False, "bindings": [], "issues": [f"invalid tools registry: {error}"]}
    available = runtime_tool_bindings()
    bindings = []
    issues: list[str] = []
    for entry in tool_entries:
        tool_id = str(entry.get("id") or "")
        callable_name = str(entry.get("callable") or tool_id)
        runtime = available.get(callable_name)
        registered = runtime is not None and runtime["handler_callable"]
        bindings.append({
            "id": tool_id,
            "callable": callable_name,
            "registered": registered,
            "layer": entry.get("layer"),
            "category": entry.get("category"),
        })
        if not registered:
            issues.append(f"tool '{tool_id}' callable '{callable_name}' is not registered in the host runtime")
    return {
        "ok": not issues,
        "main_model_available": True,
        "bindings": bindings,
        "issues": issues,
    }


def _resource_kind(name: str, text: str | None) -> str:
    lower_name = name.lower()
    suffix = Path(name).suffix.lower()
    if lower_name == "skill.md" or (suffix == ".md" and text and text.startswith("---\n") and FRONTMATTER_NAME_RE.search(text)):
        return "skill"
    if suffix == ".py":
        return "python"
    if suffix in {".yaml", ".yml"} and text and re.search(r"(?m)^openapi:\s*['\"]?3", text):
        return "openapi"
    if suffix == ".json" and text:
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            return "invalid_json"
        if isinstance(value, dict) and ("openapi" in value or "swagger" in value):
            return "openapi"
        if isinstance(value, dict) and ("$schema" in value or "properties" in value):
            return "json_schema"
        return "json"
    if suffix in {".md", ".txt", ".yaml", ".yml"}:
        return "documentation"
    return "unsupported"


def _inspect_python(text: str) -> tuple[list[str], list[str], list[str]]:
    imports: set[str] = set()
    risks: set[str] = set()
    errors: list[str] = []
    try:
        tree = ast.parse(text)
    except SyntaxError as error:
        return [], [], [f"Python syntax error at line {error.lineno}: {error.msg}"]

    risky_imports = {"subprocess", "socket", "ctypes", "multiprocessing"}
    risky_calls = {"eval", "exec", "compile", "__import__", "os.system", "os.popen", "subprocess.run", "subprocess.Popen"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".", 1)[0])
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                call_name = node.func.id
            elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                call_name = f"{node.func.value.id}.{node.func.attr}"
            else:
                call_name = ""
            if call_name in risky_calls:
                risks.add(f"uses {call_name}")
    risks.update(f"imports {name}" for name in imports & risky_imports)
    return sorted(imports), sorted(risks), errors


def _inspect_resource(session_id: str, resource: dict[str, Any]) -> dict[str, Any]:
    file_id = str(resource.get("fileId") or resource.get("file_id") or "")
    if not file_id:
        return {"fileId": "", "status": "error", "errors": ["A stable fileId is required."]}
    path = uploads_store.upload_path(session_id, file_id)
    if path is None:
        return {"fileId": file_id, "status": "error", "errors": ["Uploaded resource was not found."]}
    size = path.stat().st_size
    name = _safe_resource_name(path)
    errors: list[str] = []
    warnings: list[str] = []
    capabilities: list[str] = []
    imports: list[str] = []
    text: str | None = None

    if size > MAX_AUTHORING_RESOURCE_BYTES:
        errors.append(f"Resource exceeds the {MAX_AUTHORING_RESOURCE_BYTES // (1024 * 1024)} MB authoring limit.")
    elif path.suffix.lower() in TEXT_RESOURCE_SUFFIXES:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append("Text resource must use UTF-8 encoding.")

    kind = _resource_kind(name, text)
    if kind == "unsupported":
        errors.append("Unsupported authoring resource type; use Markdown, text, Python, JSON, YAML, or OpenAPI.")
    elif kind == "invalid_json":
        errors.append("JSON resource is invalid.")
    if text and SECRET_VALUE_RE.search(text):
        errors.append("Resource appears to contain a credential value; remove secrets before uploading.")
    if kind == "skill" and text:
        name_match = FRONTMATTER_NAME_RE.search(text)
        capabilities.append(f"skill:{name_match.group(1) if name_match else 'unnamed'}")
        if not H1_RE.search(text):
            warnings.append("Skill resource has no H1 heading.")
    elif kind == "python" and text is not None:
        imports, risks, syntax_errors = _inspect_python(text)
        warnings.extend(risks)
        errors.extend(syntax_errors)
        capabilities.append("python_source_for_adapter_review")
    elif kind == "openapi":
        capabilities.append("external_service_description")
    elif kind == "json_schema":
        capabilities.append("structured_data_contract")
    elif kind in {"documentation", "json"}:
        capabilities.append("reference_material")

    return {
        "fileId": file_id,
        "name": name,
        "size": size,
        "kind": kind,
        "declared_purpose": str(resource.get("declared_purpose") or resource.get("purpose") or ""),
        "required": bool(resource.get("required", False)),
        "status": "error" if errors else "accepted",
        "capabilities": capabilities,
        "imports": imports,
        "warnings": warnings,
        "errors": errors,
    }


def inspect_authoring_resources(session_id: str, resources: list[dict[str, Any]]) -> dict[str, Any]:
    """Statically inspect uploaded resources without returning source or paths."""
    if not isinstance(resources, list) or not resources:
        return {"action": "validation_error", "message": "At least one uploaded resource is required.", "resources": []}
    records = [_inspect_resource(session_id, resource) for resource in resources if isinstance(resource, dict)]
    if len(records) != len(resources):
        return {"action": "validation_error", "message": "Every resource must be an object.", "resources": records}
    errors = [error for record in records for error in record["errors"]]
    kinds = {record.get("kind") for record in records if record.get("status") == "accepted"}
    if "python" in kinds:
        recommendation = "uploaded_runtime"
    elif "openapi" in kinds:
        recommendation = "external_service"
    elif "skill" in kinds:
        recommendation = "imported_skill"
    else:
        recommendation = "host_agent"
    return {
        "action": "resource_validation_error" if errors else "inflak_authoring_resources_inspected",
        "resources": records,
        "recommended_execution_mode": recommendation,
        "code_executed": False,
        "errors": errors,
    }


def _string_list(value: Any, field: str, *, required: bool = False) -> list[str]:
    if value is None:
        items: list[Any] = []
    elif isinstance(value, str):
        items = [value]
    elif isinstance(value, list):
        items = value
    else:
        raise InflakAuthoringError(f"{field} must be a string or list of strings.")
    result = [str(item).strip() for item in items if str(item).strip()]
    if required and not result:
        raise InflakAuthoringError(f"{field} requires at least one concrete item.")
    return result


def _normalise_state_model(target_spec: dict[str, Any], design: dict[str, Any]) -> tuple[dict[str, str], list[dict[str, Any]]]:
    raw_state = design.get("state_model") or target_spec.get("state_model")
    if not isinstance(raw_state, list) or not raw_state:
        raise InflakAuthoringError(
            "A complete state_model is required; declare each input, intermediate state, decision, status, and final result with lifecycle metadata."
        )
    state_model: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(raw_state, start=1):
        if not isinstance(item, dict):
            raise InflakAuthoringError(f"state_model item #{index} must be an object.")
        name = _identifier(item.get("name") or item.get("id"), f"state_{index}")
        if name in seen:
            raise InflakAuthoringError(f"Duplicate state field '{name}'.")
        seen.add(name)
        meaning = str(item.get("meaning") or item.get("description") or "").strip()
        value_shape = str(item.get("value_shape") or item.get("shape") or "").strip()
        initial_source = str(item.get("initial_source") or item.get("source") or "").strip()
        updated_by = _string_list(item.get("updated_by"), f"state_model.{name}.updated_by", required=True)
        visibility = str(item.get("visibility") or "").strip().lower()
        invalidation = str(item.get("invalidation") or item.get("invalidated_when") or "").strip()
        retention = str(item.get("retention") or "").strip().lower()
        if not meaning or not value_shape or not initial_source or not invalidation:
            raise InflakAuthoringError(
                f"State '{name}' requires meaning, value_shape, initial_source, updated_by, visibility, invalidation, and retention."
            )
        if visibility not in STATE_VISIBILITY:
            raise InflakAuthoringError(f"State '{name}' has unsupported visibility '{visibility}'.")
        if retention not in STATE_RETENTION:
            raise InflakAuthoringError(f"State '{name}' has unsupported retention '{retention}'.")
        state_model.append({
            "name": name,
            "meaning": meaning,
            "value_shape": value_shape,
            "initial_source": initial_source,
            "updated_by": updated_by,
            "visibility": visibility,
            "invalidation": invalidation,
            "retention": retention,
        })
    return {item["name"]: item["meaning"] for item in state_model}, state_model


def _normalise_workflow_stages(
    target_spec: dict[str, Any],
    design: dict[str, Any],
    state_fields: set[str],
) -> list[dict[str, Any]]:
    workflow = design.get("workflow") if isinstance(design.get("workflow"), dict) else {}
    if not workflow:
        workflow = target_spec.get("workflow") if isinstance(target_spec.get("workflow"), dict) else {}
    exception_paths = _string_list(
        design.get("exception_paths")
        or workflow.get("exception_paths")
        or target_spec.get("exception_paths"),
        "exception_paths",
    )
    raw_stages = workflow.get("stages") or design.get("workflow_stages") or target_spec.get("workflow_stages")
    if not isinstance(raw_stages, list) or not raw_stages:
        raise InflakAuthoringError("A task-specific workflow with at least one fully designed stage is required.")
    stages: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, stage in enumerate(raw_stages, start=1):
        if not isinstance(stage, dict):
            raise InflakAuthoringError(
                f"Workflow stage #{index} must be an object with actor, entry, activities, state effects, completion, and transition details."
            )
        stage_id = _identifier(stage.get("id") or stage.get("name"), f"stage_{index}")
        if stage_id in seen:
            raise InflakAuthoringError(f"Duplicate workflow stage '{stage_id}'.")
        seen.add(stage_id)
        name = str(stage.get("name") or stage.get("label") or "").strip()
        purpose = str(stage.get("purpose") or stage.get("description") or "").strip()
        actor = str(stage.get("actor") or "").strip().lower()
        entry_condition = str(stage.get("entry_condition") or stage.get("entry") or "").strip()
        reads = _string_list(stage.get("reads"), f"workflow.{stage_id}.reads")
        activities = _string_list(stage.get("activities") or stage.get("work"), f"workflow.{stage_id}.activities", required=True)
        writes = _string_list(stage.get("writes"), f"workflow.{stage_id}.writes")
        visible_progress = _string_list(
            stage.get("visible_progress") or stage.get("user_visible_progress"),
            f"workflow.{stage_id}.visible_progress",
            required=True,
        )
        completion_condition = str(stage.get("completion_condition") or stage.get("completion") or "").strip()
        next_stages = _string_list(stage.get("next") or stage.get("next_stages"), f"workflow.{stage_id}.next", required=True)
        failure_path = str(
            stage.get("failure_path")
            or stage.get("fallback")
            or stage.get("fallback_behavior")
            or stage.get("on_failure")
            or ""
        ).strip()
        if not failure_path and exception_paths:
            stage_text = " ".join([
                stage_id,
                name,
                purpose,
                *reads,
                *activities,
                *writes,
            ]).lower()
            ignored = {"the", "and", "or", "a", "an", "to", "of", "for", "is", "are", "user", "ai", "stage"}
            stage_tokens = {
                token for token in re.split(r"[^a-z0-9]+", stage_text)
                if len(token) > 2 and token not in ignored
            }
            ranked_paths = []
            for path_index, path in enumerate(exception_paths):
                path_tokens = {
                    token for token in re.split(r"[^a-z0-9]+", path.lower())
                    if len(token) > 2 and token not in ignored
                }
                ranked_paths.append((len(stage_tokens & path_tokens), -path_index, path))
            best_score, _, best_path = max(ranked_paths)
            failure_path = best_path if best_score else "Apply the relevant declared exception path: " + "; ".join(exception_paths)
        if not name or not purpose or not entry_condition or not completion_condition or not failure_path:
            raise InflakAuthoringError(
                f"Workflow stage '{stage_id}' requires name, purpose, actor, entry_condition, activities, visible_progress, completion_condition, next, and failure_path."
            )
        if actor not in STAGE_ACTORS:
            raise InflakAuthoringError(f"Workflow stage '{stage_id}' has unsupported actor '{actor}'.")
        undeclared = (set(reads) | set(writes)) - state_fields
        if undeclared:
            raise InflakAuthoringError(
                f"Workflow stage '{stage_id}' references undeclared state: {', '.join(sorted(undeclared))}."
            )
        stages.append({
            "id": stage_id,
            "name": name,
            "purpose": purpose,
            "actor": actor,
            "entry_condition": entry_condition,
            "reads": reads,
            "activities": activities,
            "writes": writes,
            "visible_progress": visible_progress,
            "completion_condition": completion_condition,
            "next": next_stages,
            "failure_path": failure_path,
        })
    stage_ids = {stage["id"] for stage in stages}
    for stage in stages:
        normalised_next: list[str] = []
        invalid_next: set[str] = set()
        for target in stage["next"]:
            candidate = _identifier(target, "")
            if candidate in {"complete", "stop", "escape"}:
                normalised_next.append(candidate)
                continue
            if candidate in stage_ids:
                normalised_next.append(candidate)
                continue
            candidate_tokens = set(candidate.split("_"))
            if candidate_tokens & {"complete", "completed", "final", "exported", "done", "finished"}:
                normalised_next.append("complete")
                continue
            prefix_matches = [stage_id for stage_id in stage_ids if candidate.startswith(stage_id + "_")]
            if len(prefix_matches) == 1:
                normalised_next.append(prefix_matches[0])
            else:
                invalid_next.add(target)
        if invalid_next:
            raise InflakAuthoringError(
                f"Workflow stage '{stage['id']}' has unknown next stage: {', '.join(sorted(invalid_next))}."
            )
        stage["next"] = list(dict.fromkeys(normalised_next))
    return stages


def _normalise_archetype(value: Any, interaction_goal: str) -> str:
    candidate = _identifier(value, "")
    if candidate in INTERACTION_ARCHETYPES:
        return candidate
    combined = f"{candidate} {interaction_goal}".lower()
    for keyword, archetype in (
        ("progress", "progress_inspector"),
        ("conflict", "comparison_review"),
        ("coverage", "decision_review"),
        ("compare", "comparison_review"),
        ("annotat", "annotation_surface"),
        ("reorder", "ordered_editor"),
        ("upload", "resource_intake"),
        ("resource", "resource_intake"),
        ("result", "result_review"),
        ("report", "result_review"),
        ("review", "decision_review"),
        ("approve", "decision_review"),
        ("decision", "decision_review"),
        ("edit", "structured_editor"),
        ("collect", "structured_input"),
        ("input", "structured_input"),
    ):
        if keyword in combined:
            return archetype
    raise InflakAuthoringError(
        f"Interaction goal '{interaction_goal}' requires a concrete semantic archetype such as structured_input, decision_review, progress_inspector, or result_review."
    )


def _normalise_actions(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise InflakAuthoringError(f"{field} requires at least one supported user action.")
    actions: list[dict[str, Any]] = []
    for index, item in enumerate(value, start=1):
        if isinstance(item, str):
            item = {"id": _identifier(item, f"action_{index}"), "label": item, "effect": item}
        if not isinstance(item, dict):
            raise InflakAuthoringError(f"{field} item #{index} must be a string or object.")
        action_id = _identifier(item.get("id") or item.get("label"), f"action_{index}")
        label = str(item.get("label") or item.get("name") or "").strip()
        effect = str(item.get("effect") or item.get("state_effect") or "").strip()
        if not label or not effect:
            raise InflakAuthoringError(f"{field} action '{action_id}' requires label and effect.")
        actions.append({
            "id": action_id,
            "label": label,
            "kind": str(item.get("kind") or "command"),
            "effect": effect,
            "requires_confirmation": bool(item.get("requires_confirmation", False)),
        })
    return actions


def _normalise_return_outcomes(
    value: Any,
    *,
    expected_return: dict[str, Any],
    stage_ids: set[str],
    field: str,
) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise InflakAuthoringError(
            f"{field} requires at least one outcome that maps raw widget values to state and workflow effects."
        )
    outcomes: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_matches: set[str] = set()
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            raise InflakAuthoringError(f"{field} item #{index} must be an object.")
        outcome_id = _identifier(item.get("id"), f"outcome_{index}")
        if outcome_id in seen_ids:
            raise InflakAuthoringError(f"{field} has duplicate outcome id '{outcome_id}'.")
        seen_ids.add(outcome_id)
        when = item.get("when")
        if not isinstance(when, dict) or not when:
            raise InflakAuthoringError(f"{field} outcome '{outcome_id}' requires a non-empty when object.")
        unknown_match_fields = set(when) - set(expected_return)
        if unknown_match_fields:
            raise InflakAuthoringError(
                f"{field} outcome '{outcome_id}' matches undeclared return fields: {', '.join(sorted(unknown_match_fields))}."
            )
        match_key = json.dumps(when, sort_keys=True, ensure_ascii=False)
        if match_key in seen_matches:
            raise InflakAuthoringError(f"{field} has duplicate outcome match {match_key}.")
        seen_matches.add(match_key)
        state_update_target = str(item.get("state_update_target") or "").strip()
        merge_strategy = str(item.get("merge_strategy") or "").strip()
        workflow_effect = _identifier(item.get("workflow_effect"), "")
        next_stage = _identifier(item.get("next_stage"), "")
        terminal = item.get("terminal")
        if not state_update_target or not merge_strategy:
            raise InflakAuthoringError(
                f"{field} outcome '{outcome_id}' requires state_update_target and merge_strategy."
            )
        if workflow_effect not in WORKFLOW_EFFECTS:
            raise InflakAuthoringError(
                f"{field} outcome '{outcome_id}' has unsupported workflow_effect '{workflow_effect}'."
            )
        if next_stage not in stage_ids | {"complete", "stop", "escape"}:
            raise InflakAuthoringError(
                f"{field} outcome '{outcome_id}' references unknown next_stage '{next_stage}'."
            )
        if not isinstance(terminal, bool):
            raise InflakAuthoringError(f"{field} outcome '{outcome_id}' requires a boolean terminal value.")
        expected_terminal = workflow_effect in {"complete", "cancel", "escape"}
        if terminal != expected_terminal:
            raise InflakAuthoringError(
                f"{field} outcome '{outcome_id}' terminal must be {expected_terminal} for workflow_effect '{workflow_effect}'."
            )
        outcomes.append({
            "id": outcome_id,
            "when": when,
            "state_update_target": state_update_target,
            "merge_strategy": merge_strategy,
            "workflow_effect": workflow_effect,
            "next_stage": next_stage,
            "terminal": terminal,
        })
    return outcomes


def _normalise_interactions(
    target_spec: dict[str, Any],
    design: dict[str, Any],
    stage_ids: set[str],
) -> list[dict[str, Any]]:
    raw_interactions = target_spec.get("semantic_gaps") or target_spec.get("interactions") or []
    raw_methods = design.get("interaction_methods") or target_spec.get("interaction_methods") or []
    interactions: list[dict[str, Any]] = []
    if not isinstance(raw_interactions, list) or not raw_interactions:
        raise InflakAuthoringError("At least one semantic gap is required for the designed human checkpoints.")
    if not isinstance(raw_methods, list) or not raw_methods:
        raise InflakAuthoringError(
            "interaction_methods is required; describe what each interaction shows, supports, validates, returns, and updates."
        )
    methods_by_gap: dict[str, dict[str, Any]] = {}
    methods_by_goal: dict[str, dict[str, Any]] = {}
    for method in raw_methods:
        if not isinstance(method, dict):
            raise InflakAuthoringError("Every interaction method must be an object.")
        if method.get("gap_type"):
            methods_by_gap[str(method["gap_type"])] = method
        if method.get("interaction_goal"):
            methods_by_goal[str(method["interaction_goal"])] = method
    seen_method_ids: set[str] = set()
    for index, item in enumerate(raw_interactions[:8], start=1):
        if not isinstance(item, dict):
            raise InflakAuthoringError("Every semantic gap must be an object.")
        base = _identifier(item.get("gap_type") or item.get("name"), f"collaboration_choice_{index}")
        gap_type = base if base.endswith("_gap") else f"{base}_gap"
        interaction_goal = _identifier(item.get("interaction_goal") or item.get("goal"), f"resolve_{base}")
        interaction_goal = re.sub(r"_gap$", "_issue", interaction_goal)
        method = item.get("interaction_method") if isinstance(item.get("interaction_method"), dict) else None
        method = method or methods_by_gap.get(str(item.get("gap_type") or "")) or methods_by_goal.get(str(item.get("interaction_goal") or ""))
        if method is None:
            raise InflakAuthoringError(f"Semantic gap '{gap_type}' has no matching interaction method.")
        edge = str(item.get("iai_edge") or item.get("edge") or "G→I")
        if edge not in VALID_IAI_EDGES:
            raise InflakAuthoringError(f"Interaction '{gap_type}' has invalid IAI edge '{edge}'.")
        expected_return = item.get("expected_return") or method.get("expected_return")
        if not isinstance(expected_return, dict) or not expected_return:
            raise InflakAuthoringError(f"Interaction '{gap_type}' requires a non-empty expected_return object.")
        stage_id = _identifier(method.get("stage_id"), "")
        if stage_id not in stage_ids:
            raise InflakAuthoringError(f"Interaction '{gap_type}' references unknown workflow stage '{stage_id}'.")
        method_id = _identifier(method.get("id"), f"{base}_interaction")
        if method_id in seen_method_ids:
            raise InflakAuthoringError(f"Duplicate interaction method id '{method_id}'.")
        seen_method_ids.add(method_id)
        purpose = str(method.get("purpose") or "").strip()
        if not purpose:
            raise InflakAuthoringError(f"Interaction '{gap_type}' requires a purpose.")
        approved_design = method.get("approved_widget_design") if isinstance(method.get("approved_widget_design"), dict) else method
        approved_design_id = _identifier(
            approved_design.get("approved_design_id")
            or approved_design.get("selected_design_id")
            or approved_design.get("design_id"),
            "",
        )
        interaction_mode = str(
            approved_design.get("interaction_mode")
            or approved_design.get("interaction_modality")
            or ""
        ).strip()
        widget_family = str(approved_design.get("widget_family") or "").strip()
        widget_type = _identifier(
            approved_design.get("interaction_primitive")
            or approved_design.get("widget_type"),
            "",
        )
        preview_model = approved_design.get("preview_model")
        if not approved_design_id or not interaction_mode or not widget_family or not widget_type:
            raise InflakAuthoringError(
                f"Interaction '{gap_type}' requires an approved widget design id, interaction mode, reusable widget family, and widget_type."
            )
        if not isinstance(preview_model, dict) or not str(preview_model.get("kind") or "").strip():
            raise InflakAuthoringError(f"Interaction '{gap_type}' requires a non-empty semantic preview_model.")
        display = method.get("display") if isinstance(method.get("display"), dict) else {}
        primary = _string_list(display.get("primary"), f"interaction_methods.{method_id}.display.primary", required=True)
        context = _string_list(display.get("context"), f"interaction_methods.{method_id}.display.context")
        status = _string_list(display.get("status"), f"interaction_methods.{method_id}.display.status")
        provenance = _string_list(display.get("provenance"), f"interaction_methods.{method_id}.display.provenance")
        input_modes = _string_list(method.get("input_modes"), f"interaction_methods.{method_id}.input_modes")
        actions = _normalise_actions(method.get("actions"), f"interaction_methods.{method_id}.actions")
        return_outcomes = _normalise_return_outcomes(
            method.get("return_outcomes"),
            expected_return=expected_return,
            stage_ids=stage_ids,
            field=f"interaction_methods.{method_id}.return_outcomes",
        )
        feedback = _string_list(method.get("feedback"), f"interaction_methods.{method_id}.feedback", required=True)
        validation = _string_list(method.get("validation"), f"interaction_methods.{method_id}.validation", required=True)
        raw_surface = str(method.get("surface") or method.get("surface_requirement") or "conversation_widget").lower()
        surface_options: list[str] = []
        if raw_surface in INTERACTION_SURFACES:
            surface_options.append(raw_surface)
        else:
            if "conversation" in raw_surface:
                surface_options.append("conversation_widget")
            if "artifact" in raw_surface or "sidebar" in raw_surface:
                surface_options.append("artifact_canvas_widget")
        surface_options = list(dict.fromkeys(surface_options))
        if not surface_options:
            raise InflakAuthoringError(f"Interaction '{gap_type}' has unsupported surface '{raw_surface}'.")
        surface = surface_options[0]
        presentation = method.get("presentation") if isinstance(method.get("presentation"), dict) else {}
        signature_features = _string_list(
            presentation.get("signature_features") or method.get("signature_features"),
            f"interaction_methods.{method_id}.presentation.signature_features",
        )
        if not signature_features:
            signature_features = [
                f"Prioritize {primary[0]}",
                f"Make {actions[0]['label']} explicit",
                *( [f"Keep {status[0]} visible"] if status else [] ),
                *( [f"Keep {provenance[0]} inspectable"] if provenance else [] ),
            ][:4]
        interactions.append({
            "id": method_id,
            "chain_id": str(item.get("chain_id") or method.get("chain_id") or f"{method_id.replace('_', '-')}-interaction"),
            "gap_type": gap_type,
            "interaction_goal": interaction_goal,
            "condition": str(item.get("condition") or item.get("when") or "A consequential user decision is required."),
            "stage_id": stage_id,
            "purpose": purpose,
            "prompt": str(method.get("prompt") or item.get("question") or purpose),
            "archetype": _normalise_archetype(method.get("archetype"), interaction_goal),
            "approved_design_id": approved_design_id,
            "interaction_mode": interaction_mode,
            "widget_family": widget_family,
            "widget_type": widget_type,
            "preview_model": preview_model,
            "surface": surface,
            "surface_options": surface_options,
            "display": {
                "primary": primary,
                "context": context,
                "status": status,
                "provenance": provenance,
            },
            "actions": actions,
            "input_modes": input_modes,
            "feedback": feedback,
            "validation": validation,
            "presentation": {
                "summary": str(presentation.get("summary") or purpose),
                "layout": str(presentation.get("layout") or "task-focused workspace"),
                "emphasis": str(presentation.get("emphasis") or "primary information and next decision"),
                "density": str(presentation.get("density") or "comfortable"),
                "signature_features": signature_features,
            },
            "iai_edge": edge,
            "expected_return": expected_return,
            "return_outcomes": return_outcomes,
            "state_update_target": str(item.get("state_update_target") or method.get("state_update_target") or ""),
            "merge_strategy": str(method.get("merge_strategy") or "Replace only the declared state target with this validated return."),
            "next_effect": str(method.get("next_effect") or "Re-enter Layer 1 and re-evaluate the workflow."),
            "supported_artifact_types": _string_list(method.get("supported_artifact_types"), f"interaction_methods.{method_id}.supported_artifact_types"),
        })
    return interactions


def _normalise_final_presentation(
    target_spec: dict[str, Any],
    design: dict[str, Any],
    result_requirements: dict[str, Any],
) -> dict[str, Any]:
    raw = design.get("final_presentation") or target_spec.get("final_presentation") or {}
    if not isinstance(raw, dict) or not raw:
        raise InflakAuthoringError(
            "final_presentation is required; define result surface, format, sections, hierarchy, status/provenance, actions, and non-happy states."
        )
    result_format = str(raw.get("format") or result_requirements.get("format") or "").strip()
    sections = _string_list(
        raw.get("sections") or result_requirements.get("report_sections"),
        "final_presentation.sections",
        required=True,
    )
    hierarchy = _string_list(raw.get("hierarchy"), "final_presentation.hierarchy", required=True)
    status_and_provenance = _string_list(
        raw.get("status_and_provenance") or raw.get("status") or result_requirements.get("source_visibility"),
        "final_presentation.status_and_provenance",
        required=True,
    )
    actions = _string_list(raw.get("actions"), "final_presentation.actions", required=True)
    non_happy = _string_list(
        raw.get("empty_partial_error_states") or raw.get("non_happy_states"),
        "final_presentation.empty_partial_error_states",
        required=True,
    )
    if not result_format:
        raise InflakAuthoringError("final_presentation.format is required.")
    return {
        "surface": str(raw.get("surface") or "conversation"),
        "format": result_format,
        "sections": sections,
        "hierarchy": hierarchy,
        "status_and_provenance": status_and_provenance,
        "actions": actions,
        "empty_partial_error_states": non_happy,
    }


def _normalise_validation_cases(
    target_spec: dict[str, Any],
    examples: list[Any],
    goal: str,
) -> list[dict[str, Any]]:
    raw_cases = target_spec.get("validation_cases") or target_spec.get("acceptance_test_cases") or []
    if raw_cases and not isinstance(raw_cases, list):
        raise InflakAuthoringError("validation_cases must be a list of objects.")
    cases: list[dict[str, Any]] = []
    for index, case in enumerate(raw_cases, start=1):
        if not isinstance(case, dict):
            raise InflakAuthoringError(f"validation case #{index} must be an object.")
        case_id = _identifier(case.get("id") or case.get("title"), f"case_{index}")
        user_input = str(case.get("user_input") or case.get("prompt") or "").strip()
        if not user_input:
            raise InflakAuthoringError(f"validation case '{case_id}' requires user_input.")
        mode = str(case.get("mode") or "probe")
        if mode not in {"probe", "scripted", "interactive"}:
            raise InflakAuthoringError(f"validation case '{case_id}' has unsupported mode '{mode}'.")
        assertions = case.get("assertions") if isinstance(case.get("assertions"), dict) else {}
        scripted_returns = case.get("scripted_returns") or []
        if not isinstance(scripted_returns, list) or not all(isinstance(item, dict) for item in scripted_returns):
            raise InflakAuthoringError(f"validation case '{case_id}' scripted_returns must be a list of objects.")
        cases.append({
            "id": case_id,
            "title": str(case.get("title") or case_id.replace("_", " ").title()),
            "purpose": str(case.get("purpose") or "Validate one realistic plugin path."),
            "mode": mode,
            "user_input": user_input,
            "attachments": list(case.get("attachments") or []),
            "scripted_returns": scripted_returns,
            "assertions": {
                "expected_first_interaction_goal": assertions.get("expected_first_interaction_goal"),
                "expected_first_widget_type": assertions.get("expected_first_widget_type"),
                "required_skill_layers": list(assertions.get("required_skill_layers") or ["L1", "L2", "L3", "L4"]),
                "expected_skill_sequence": list(assertions.get("expected_skill_sequence") or []),
                "required_tools": list(assertions.get("required_tools") or []),
                "forbidden_tools": list(assertions.get("forbidden_tools") or []),
                "expected_artifact_types": list(assertions.get("expected_artifact_types") or []),
                "final_content_signals": list(assertions.get("final_content_signals") or []),
            },
        })
    if cases:
        return cases

    fallback_input = ""
    for example in examples:
        if isinstance(example, dict):
            fallback_input = str(example.get("user") or example.get("user_input") or "").strip()
            if not fallback_input and str(example.get("role") or "") == "user":
                fallback_input = str(example.get("content") or "").strip()
        if fallback_input:
            break
    fallback_input = fallback_input or goal
    return [{
        "id": "default_probe",
        "title": "Default first-interaction probe",
        "purpose": "Prove that the runtime entry and L1-L4 widget path execute for a realistic input.",
        "mode": "probe",
        "user_input": fallback_input,
        "attachments": [],
        "scripted_returns": [],
        "assertions": {
            "expected_first_interaction_goal": None,
            "expected_first_widget_type": None,
            "required_skill_layers": ["L1", "L2", "L3", "L4"],
            "expected_skill_sequence": [],
            "required_tools": [],
            "forbidden_tools": [],
            "expected_artifact_types": [],
            "final_content_signals": [],
        },
    }]


def _bind_interaction_state_targets(
    interactions: list[dict[str, Any]],
    canonical_state: dict[str, str],
) -> list[dict[str, Any]]:
    state_fields = list(canonical_state)
    if not state_fields:
        raise InflakAuthoringError("Target canonical state must declare at least one field.")
    for interaction in interactions:
        explicit_target = str(interaction.get("state_update_target") or "")
        if explicit_target:
            if explicit_target not in canonical_state:
                raise InflakAuthoringError(
                    f"Interaction '{interaction['gap_type']}' targets undeclared state '{explicit_target}'."
                )
            interaction["state_update_target"] = explicit_target
        else:
            semantic_tokens = {
                token
                for value in (
                    interaction.get("gap_type"),
                    interaction.get("interaction_goal"),
                    *(interaction.get("expected_return") or {}).keys(),
                )
                for token in re.split(r"[^a-z0-9]+", str(value).lower())
                if token and token not in {"gap", "review", "collect", "request", "change", "changes"}
            }
            ranked = []
            for index, field in enumerate(state_fields):
                field_tokens = set(re.split(r"[^a-z0-9]+", field.lower()))
                score = len(semantic_tokens & field_tokens)
                ranked.append((score, -index, field))
            best_score, _, best_field = max(ranked)
            interaction["state_update_target"] = best_field if best_score else state_fields[0]
        for outcome in interaction["return_outcomes"]:
            if outcome["state_update_target"] not in canonical_state:
                raise InflakAuthoringError(
                    f"Interaction '{interaction['gap_type']}' outcome '{outcome['id']}' targets undeclared state "
                    f"'{outcome['state_update_target']}'."
                )
    return interactions


def _normalise_target_spec(target_spec: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(target_spec, dict):
        raise InflakAuthoringError("target_spec must be an object.")
    design = target_spec.get("design_blueprint") if isinstance(target_spec.get("design_blueprint"), dict) else {}
    plugin_identity = target_spec.get("plugin_identity") if isinstance(target_spec.get("plugin_identity"), dict) else {}
    experience = target_spec.get("experience") if isinstance(target_spec.get("experience"), dict) else {}
    workflow = target_spec.get("workflow") if isinstance(target_spec.get("workflow"), dict) else {}
    result_requirements = target_spec.get("result_requirements") if isinstance(target_spec.get("result_requirements"), dict) else {}
    executor_policy = target_spec.get("executor_policy") if isinstance(target_spec.get("executor_policy"), dict) else {}
    trigger_behavior = target_spec.get("trigger_behavior") if isinstance(target_spec.get("trigger_behavior"), dict) else {}
    execution = target_spec.get("execution") if isinstance(target_spec.get("execution"), dict) else {}
    title = str(
        target_spec.get("title")
        or plugin_identity.get("name")
        or target_spec.get("display_name")
        or target_spec.get("name")
        or experience.get("title")
        or ""
    ).strip()
    goal = str(
        experience.get("goal")
        or target_spec.get("goal")
        or target_spec.get("description")
        or target_spec.get("role")
        or plugin_identity.get("role")
        or plugin_identity.get("purpose")
        or ""
    ).strip()
    if not title:
        raise InflakAuthoringError("A target plugin title is required.")
    if not goal:
        raise InflakAuthoringError("Describe what the target plugin should help its user accomplish.")
    raw_plugin_id = str(target_spec.get("plugin_id") or target_spec.get("slug") or plugin_identity.get("id") or title)
    plugin_slug = _slugify(raw_plugin_id)
    plugin_id = plugin_slug if plugin_slug.startswith("inflak-") else f"inflak-{plugin_slug}"
    if not PLUGIN_ID_RE.fullmatch(plugin_id):
        raise InflakAuthoringError(f"Target plugin id '{plugin_id}' is invalid or too short/long.")
    short_slug = plugin_id.removeprefix("inflak-")
    default_executor = str(executor_policy.get("default_executor") or executor_policy.get("mode") or "")
    if default_executor in {"", "main_model", "host_agent"}:
        inferred_mode = "host_agent"
    elif default_executor in GPT_IMAGE_TOOL_EXECUTORS:
        inferred_mode = "image_tool"
    elif default_executor in EXECUTION_MODES:
        inferred_mode = default_executor
    else:
        inferred_mode = "external_service"
    mode = str(execution.get("mode") or inferred_mode)
    if mode not in EXECUTION_MODES:
        raise InflakAuthoringError(f"Unsupported execution mode '{mode}'.")
    tool_name = str(
        execution.get("tool_name")
        or executor_policy.get("tool_name")
        or (default_executor if default_executor in GPT_IMAGE_TOOL_EXECUTORS else "")
    ).strip()
    tool_parameters = execution.get("tool_parameters") or {}
    if not isinstance(tool_parameters, dict):
        raise InflakAuthoringError("execution.tool_parameters must be an object.")
    if mode == "image_tool" and tool_name not in GPT_IMAGE_TOOL_EXECUTORS:
        supported = ", ".join(sorted(GPT_IMAGE_TOOL_EXECUTORS))
        raise InflakAuthoringError(
            f"Image-tool execution requires a supported tool_name ({supported})."
        )
    if mode == "image_tool" and not tool_parameters:
        raise InflakAuthoringError(
            "Image-tool execution requires tool_parameters mapped from canonical state to the selected tool schema."
        )
    resource_refs = execution.get("resources") or target_spec.get("resources") or []
    if not isinstance(resource_refs, list) or not all(isinstance(item, dict) for item in resource_refs):
        raise InflakAuthoringError("Execution resources must be a list of uploaded-file references.")
    secret_requirements = execution.get("secret_requirements") or executor_policy.get("secret_requirements") or []
    if not isinstance(secret_requirements, list) or not all(SAFE_ENV_RE.fullmatch(str(item)) for item in secret_requirements):
        raise InflakAuthoringError("Secret requirements may contain environment-variable names only.")
    allow_host_fallback = bool(execution.get("allow_host_fallback", False))
    host_fallback_equivalent = bool(execution.get("host_fallback_equivalent", False))
    if mode in {"host_agent", "imported_skill"}:
        runtime_readiness = "ready"
        effective_executor = "main_model"
    elif mode == "image_tool":
        runtime_readiness = "ready"
        effective_executor = tool_name
    elif allow_host_fallback and host_fallback_equivalent:
        runtime_readiness = "ready_with_host_fallback"
        effective_executor = "main_model"
    else:
        runtime_readiness = "planned"
        effective_executor = "custom_adapter_required"
    if mode == "imported_skill" and not resource_refs:
        raise InflakAuthoringError("Imported-skill execution requires at least one uploaded resource.")

    description = str(target_spec.get("description") or target_spec.get("role") or plugin_identity.get("role") or goal).strip()
    report_sections = result_requirements.get("report_sections")
    derived_output = (
        "A result containing: " + ", ".join(str(item) for item in report_sections)
        if isinstance(report_sections, list) and report_sections
        else "A result aligned with the user's request."
    )
    desired_output = str(
        experience.get("desired_output")
        or target_spec.get("desired_output")
        or result_requirements.get("desired_output")
        or derived_output
    )
    canonical_state, state_model = _normalise_state_model(target_spec, design)
    normalised_stages = _normalise_workflow_stages(target_spec, design, set(canonical_state))
    final_presentation = _normalise_final_presentation(target_spec, design, result_requirements)
    examples = target_spec.get("example_dialogue") or target_spec.get("examples") or target_spec.get("user_facing_examples") or []
    if not isinstance(examples, list):
        examples = []
    interactions = _bind_interaction_state_targets(
        _normalise_interactions(
            target_spec,
            design,
            {stage["id"] for stage in normalised_stages},
        ),
        canonical_state,
    )
    exception_paths = _string_list(
        design.get("exception_paths")
        or workflow.get("exception_paths")
        or target_spec.get("exception_paths"),
        "exception_paths",
    )
    validation_cases = _normalise_validation_cases(target_spec, examples, goal)
    node_bindings = target_spec.get("node_bindings", design.get("node_bindings", {}))
    chains = target_spec.get("chains", design.get("chains", []))
    _author_chains({
        "chains": chains, "node_bindings": node_bindings,
        "interactions": interactions, "desired_output": desired_output,
    })
    return {
        "plugin_id": plugin_id,
        "short_slug": short_slug,
        "title": title,
        "label": str(target_spec.get("label") or plugin_identity.get("name") or f"inflak {title}"),
        "description": description,
        "task_family": _slugify(str(target_spec.get("task_family") or target_spec.get("domain") or short_slug)),
        "goal": goal,
        "desired_output": desired_output,
        "trigger_examples": _string_list(
            target_spec.get("trigger_examples")
            or trigger_behavior.get("enter_when")
            or plugin_identity.get("trigger_behavior"),
            "trigger_examples",
        ),
        "bypass_examples": _string_list(
            target_spec.get("bypass_examples")
            or trigger_behavior.get("bypass_when")
            or plugin_identity.get("bypass_behavior"),
            "bypass_examples",
        ),
        "canonical_state": {str(key): str(value) for key, value in canonical_state.items()},
        "node_bindings": node_bindings,
        "chains": chains,
        "state_model": state_model,
        "workflow_stages": normalised_stages,
        "ai_agency": list(experience.get("ai_agency") or workflow.get("ai_agency") or []),
        "human_checkpoints": list(experience.get("human_checkpoints") or workflow.get("human_checkpoints") or []),
        "process_visibility": str(
            experience.get("process_visibility")
            or result_requirements.get("source_visibility")
            or "Show meaningful progress and decisions."
        ),
        "revision_policy": str(
            experience.get("revision_policy")
            or result_requirements.get("revision_behavior")
            or "The user may request a revision after review."
        ),
        "trust_requirements": list(
            experience.get("trust_requirements")
            or target_spec.get("acceptance_cases")
            or []
        ),
        "interactions": interactions,
        "final_presentation": final_presentation,
        "exception_paths": exception_paths,
        "execution": {
            "mode": mode,
            "effective_executor": effective_executor,
            "runtime_readiness": runtime_readiness,
            "tool_name": tool_name or None,
            "tool_parameters": tool_parameters,
            "host_agent_role": str(
                execution.get("host_agent_role")
                or target_spec.get("role")
                or executor_policy.get("resource_policy")
                or "Perform the task and produce the requested result."
            ),
            "resources": resource_refs,
            "allow_host_fallback": allow_host_fallback,
            "host_fallback_equivalent": host_fallback_equivalent,
            "secret_requirements": [str(item) for item in secret_requirements],
        },
        "assumptions": list(target_spec.get("assumptions") or []),
        "limitations": list(target_spec.get("limitations") or []),
        "example_dialogue": examples,
        "validation_cases": validation_cases,
        "replace_existing_plugin": bool(target_spec.get("replace_existing_plugin", False)),
        "source_scenario_run_id": str(target_spec.get("source_scenario_run_id") or "").strip() or None,
    }


def _resource_bundle(
    session_id: str,
    spec: dict[str, Any],
) -> tuple[dict[str, bytes], list[dict[str, Any]], list[str]]:
    files: dict[str, bytes] = {}
    records: list[dict[str, Any]] = []
    warnings: list[str] = []
    used_names: set[str] = set()
    for resource in spec["execution"]["resources"]:
        record = _inspect_resource(session_id, resource)
        if record["errors"]:
            raise InflakAuthoringError(f"Resource {record.get('fileId') or '<missing>'}: {'; '.join(record['errors'])}")
        path = uploads_store.upload_path(session_id, record["fileId"])
        if path is None:
            raise InflakAuthoringError(f"Resource {record['fileId']} is no longer available.")
        name = record["name"]
        if name in used_names:
            stem = Path(name).stem
            suffix = Path(name).suffix
            name = f"{stem}-{record['fileId'][:8]}{suffix}"
        used_names.add(name)
        bundle_path = f"resources/{name}"
        files[bundle_path] = path.read_bytes()
        record = {**record, "bundle_path": bundle_path}
        records.append(record)
        warnings.extend(record["warnings"])
    if records:
        lines = ["# Packaged Authoring Resources", ""]
        for record in records:
            purpose = record["declared_purpose"] or "No additional purpose supplied."
            lines.append(f"- `{record['bundle_path']}` ({record['kind']}): {purpose}")
        lines.extend([
            "",
            "These files are packaged as reviewed resources. Python source is not executable merely because it is present here.",
        ])
        files["resources/README.md"] = ("\n".join(lines) + "\n").encode("utf-8")
    return files, records, warnings


def _render_root(spec: dict[str, Any], resource_records: list[dict[str, Any]]) -> str:
    short = spec["short_slug"]
    stage_rows = "\n".join(
        f"| `{stage['id']}` | {_markdown(stage['name'])} | `{stage['actor']}` | {_markdown(stage['entry_condition'])} | {_markdown('; '.join(stage['activities']))} | {_markdown('; '.join(stage['writes']) or 'No state write')} | {_markdown(stage['completion_condition'])} | {_markdown('; '.join(stage['next']))} |"
        for stage in spec["workflow_stages"]
    )
    state_rows = "\n".join(
        f"| `{state['name']}` | {_markdown(state['meaning'])} | `{state['value_shape']}` | {_markdown(state['initial_source'])} | {_markdown('; '.join(state['updated_by']))} | `{state['visibility']}` | {_markdown(state['invalidation'])} | `{state['retention']}` |"
        for state in spec["state_model"]
    )
    interaction_rows = "\n".join(
        f"| `{interaction['id']}` | `{interaction['stage_id']}` | {_markdown(interaction['interaction_mode'])} | {_markdown(interaction['widget_family'])} / `{interaction['widget_type']}` | {_markdown('; '.join(interaction['display']['primary']))} | {_markdown('; '.join(action['label'] for action in interaction['actions']))} | {_markdown('; '.join(outcome['id'] + ' → ' + outcome['workflow_effect'] + ':' + outcome['next_stage'] for outcome in interaction['return_outcomes']))} |"
        for interaction in spec["interactions"]
    )
    resources = "\n".join(
        f"- `{record['bundle_path']}`: {_markdown(record['declared_purpose'] or record['kind'])}"
        for record in resource_records
    ) or "- No packaged resource is required; the host agent performs the ready instruction."
    limitations = "\n".join(f"- {_markdown(item)}" for item in spec["limitations"]) or "- Stay within the confirmed task scope and available capabilities."
    return f"""---
name: {spec['plugin_id']}
description: {_yaml_quote('Use when: ' + spec['description'])}
---

# {spec['title']}

{spec['goal']}

Expected result: {spec['desired_output']}

## Human-AI Workflow

| stage | purpose | actor | entry | work | state writes | complete when | next |
| --- | --- | --- | --- | --- | --- | --- | --- |
{stage_rows}

AI agency: {_markdown('; '.join(map(str, spec['ai_agency'])) or 'Act within the confirmed workflow and pause at declared checkpoints.')}

Human checkpoints: {_markdown('; '.join(map(str, spec['human_checkpoints'])) or 'Review the generated result before acceptance.')}

Process visibility: {_markdown(spec['process_visibility'])}

Revision: {_markdown(spec['revision_policy'])}

## Canonical State and Lifecycle

| state | meaning | shape | initial source | updated by | visibility | invalidated when | retention |
| --- | --- | --- | --- | --- | --- | --- | --- |
{state_rows}

Every stage and interaction reads and writes only these fields. A stale revision is never silently reused.

## Interaction Methods

| method | stage | interaction mode | widget family/type | information shown | supported actions | return outcomes |
| --- | --- | --- | --- | --- | --- | --- |
{interaction_rows}

Each method preserves its own display requirements, input modes, feedback, validation, expected return, and outcome-specific merge and workflow effects. The host returns the raw widget JSON unchanged; Layer 1 matches it against these outcomes before routing. Do not flatten these methods into one generic form.

## Final Presentation

- **Surface:** {_markdown(spec['final_presentation']['surface'])}
- **Format:** {_markdown(spec['final_presentation']['format'])}
- **Sections:** {_markdown('; '.join(spec['final_presentation']['sections']))}
- **Hierarchy:** {_markdown('; '.join(spec['final_presentation']['hierarchy']))}
- **Status and provenance:** {_markdown('; '.join(spec['final_presentation']['status_and_provenance']))}
- **Actions:** {_markdown('; '.join(spec['final_presentation']['actions']))}
- **Empty, partial, and error states:** {_markdown('; '.join(spec['final_presentation']['empty_partial_error_states']))}

## Exception Paths

{chr(10).join('- ' + _markdown(item) for item in spec['exception_paths']) or '- Follow each stage failure path and expose the blocked state to the user.'}

## Validation Cases

{chr(10).join(f"- `{case['id']}` ({case['mode']}): {_markdown(case['title'])} — {_markdown(case['purpose'])}" for case in spec['validation_cases'])}

The machine-readable scenarios are stored in `tests/scenarios.json`. They are executable validation inputs, not runtime user defaults.

## Execution

Mode: `{spec['execution']['mode']}`. Effective executor: `{spec['execution']['effective_executor']}`. Runtime readiness: `{spec['execution']['runtime_readiness']}`.

{_markdown(spec['execution']['host_agent_role'])}

## Resources

{resources}

Packaged resources are subordinate to this plugin contract. Do not execute packaged Python source unless a separately registered, reviewed tool explicitly provides that capability. Never request secrets in chat; use only declared environment-variable names at runtime.

## Pathways

The layers are L1 Router, L2 Planner, L3 Designer, and L4 Renderer.

- **Interaction Pathway:** user/return -> L1 -> L2 -> L3 -> L4 -> L1. L2 selects one eligible widget registry entry by `selected_widget_id`; L3 designs its interaction and L4 renders it.
- **Execution Pathway:** user/return -> L1 -> L2 plan -> execute/realize -> L1. L2 directly invokes the selected executor or active main model without L3 or L4.
- **Host Agent Return:** L1 returns an out-of-scope request to the host agent.
- **Completion:** only L1 decides the current intent is complete.

Enter or re-enter `l1-{short}-core` for every result or failure. Only an eligible gap enters L3; gap routing failures including `no_eligible_widget` return directly to L1. L3 errors return directly to L1 without L4 entry.

## Limitations

{limitations}

## Registries

`registry/planners.json`, `registry/widgets.json`, and `registry/tools.json` are authoritative.
"""


def _render_l1(spec: dict[str, Any]) -> str:
    short = spec["short_slug"]
    planner_id = short
    state_lines = "\n".join(
        f"| `{state['name']}` | {_markdown(state['meaning'])} | `{state['value_shape']}` | {_markdown(state['initial_source'])} | {_markdown('; '.join(state['updated_by']))} | `{state['visibility']}` | {_markdown(state['invalidation'])} | `{state['retention']}` |"
        for state in spec["state_model"]
    )
    state_snapshot = {
        "user_text": "",
        "conversation_context": [],
        **{field: "" for field in spec["canonical_state"]},
        "prior_returns": [],
    }
    return f"""---
name: l1-{short}-core
description: {_yaml_quote('Use when: entering or re-entering ' + spec['title'] + ' after any user message, interaction return, or execution result.')}
---

# L1 Router - {spec['title']}

## Layer & Role

Only Layer 1 owns the canonical workflow state and decides whether the workflow is complete. On every initial request and after every interaction or execution result or failure, Layer 1 reconstructs the newest state and chooses the next action: route to an eligible Layer 2 planner for Interaction Pathway or Execution Pathway, use Host Agent Return when outside the plugin's scope, or choose Completion when the current intent is complete. Downstream layers return their results to Layer 1 and do not decide completion or produce the final workflow response.

Read the plugin root `SKILL.md` as documentation on entry. Reconstruct the newest canonical task state and route to exactly one planner. The newest explicit user decision is authoritative for the state it changes.

- **Interaction Pathway:** user/return -> L1 -> L2 gap + selection -> L3 design -> L4 render -> L1.
- **Execution Pathway:** user/return -> L1 -> L2 plan -> execute/realize -> L1; L2 directly invokes the selected executor without L3/L4 or an executor skill.
- **Host Agent Return:** use existing `bypass` for requests outside this workflow.
- **Completion:** only L1 emits `decision: end` after current-state reconstruction.

| state | meaning | shape | initial source | updated by | visibility | invalidated when | retention |
| --- | --- | --- | --- | --- | --- | --- | --- |
{state_lines}

Do not diagnose gaps, plan the task, choose interactions, render UI, or execute the task.

## Routing

Route requests that match this purpose to `{planner_id}`: {_markdown(spec['goal'])}

Bypass a pure informational request or an unrelated task that does not ask for this workflow.

```json
{{
  "handoff_type": "core_handoff",
  "decision": "route_to_planner",
  "selected_planner": "{planner_id}",
    "state_snapshot": {json.dumps(state_snapshot, ensure_ascii=False)}
}}
```

Use the existing bypass or direct-answer path only when applicable. End only after reconstructing the newest state and confirming that no required workflow action remains.

## Re-entry and Lifecycle

Consume the unmodified host envelope and its `values` object after every widget return. Match `values` against exactly one selected interaction `return_outcomes[].when` object, then apply only that outcome's state target, merge strategy, workflow effect, and next stage. The preserved IAI edge destination identifies the information-flow node; only L1 maps it into the declared canonical domain target. Never ask the host to translate an action into workflow state. Apply each field's invalidation rule before routing, preserve revision identity, and never merge an interaction return into another state target. A terminal outcome, cancellation or unavailable capability is evidence for L1's next decision, not automatic completion.

## Prohibitions and Next

Never invent approval, reuse stale state, expose secret values, or skip the layer loop. Load `l2-{short}-planner` after routing.
"""


def _author_chains(spec: dict[str, Any]) -> list[dict[str, Any]]:
    """Keep declared paradigms; adapt legacy stage specs without new API fields."""
    bindings = spec.get("node_bindings", {})
    if not isinstance(bindings, dict) or any(
        node not in {"H", "T", "I", "Aug", "A", "G"}
        or not isinstance(value, str) or not value.strip()
        for node, value in bindings.items()
    ):
        raise InflakAuthoringError("node_bindings must be an object mapping IAI nodes to non-empty strings.")
    declared = spec.get("chains", [])
    if not isinstance(declared, list):
        raise InflakAuthoringError("chains must be a list of objects.")
    seen_ids: set[str] = set()
    for chain in declared:
        if not isinstance(chain, dict):
            raise InflakAuthoringError("Every chains entry must be an object.")
        chain_id = chain.get("id")
        if not isinstance(chain_id, str) or not chain_id.strip():
            raise InflakAuthoringError("Every chain requires a non-empty string id.")
        if chain_id in seen_ids:
            raise InflakAuthoringError(f"Duplicate chain id '{chain_id}'.")
        seen_ids.add(chain_id)
        for field in ("name", "function"):
            if field in chain and not isinstance(chain[field], str):
                raise InflakAuthoringError(f"Chain '{chain_id}' {field} must be a string.")
        edges = chain.get("edges")
        if not isinstance(edges, list) or not edges:
            raise InflakAuthoringError(f"Chain '{chain_id}' requires a non-empty edges list.")
        for edge in edges:
            if (not isinstance(edge, dict) or not isinstance(edge.get("type"), str)
                    or edge["type"] not in VALID_IAI_EDGES):
                raise InflakAuthoringError(f"Chain '{chain_id}' edges must be objects with a valid IAI edge type.")
            if "explanation" in edge and not isinstance(edge["explanation"], str):
                raise InflakAuthoringError(f"Chain '{chain_id}' edge explanation must be a string.")
    if declared:
        for interaction in spec["interactions"]:
            chain = next((item for item in declared if item.get("id") == interaction["chain_id"]), None)
            if not chain or interaction["iai_edge"] not in [edge.get("type") for edge in chain.get("edges", [])]:
                raise InflakAuthoringError(f"Interaction '{interaction['id']}' requires its declared chain and edge.")
        return declared
    prefixes = {"H": [], "T": ["H→T"], "I": ["H→I"], "Aug": ["H→T", "T→Aug"],
                "A": ["H→T", "T→G", "G→A"], "G": ["H→T", "T→G"]}
    suffixes = {"T": ["T→Aug", "Aug→G", "G→A"], "I": ["I→Aug", "Aug→G", "G→A"],
                "Aug": ["Aug→G", "G→A"], "A": ["A→Aug", "Aug→G", "G→A"], "G": ["G→A"]}
    chains = [{"id": "task-direct", "name": "Evidence-backed execution", "function": spec["desired_output"],
               "edges": [{"type": edge} for edge in ("H→T", "T→Aug", "Aug→G", "G→A")]}]
    for item in spec["interactions"]:
        source, target = item["iai_edge"].split("→")
        chains.append({"id": item["chain_id"], "name": item["id"],
                       "function": f"{item['purpose']} ({item['gap_type']})",
                       "edges": [{"type": edge} for edge in [*prefixes[source], item["iai_edge"], *suffixes[target]]]})
    return chains


def _render_l2(spec: dict[str, Any]) -> str:
    short = spec["short_slug"]
    interactions = spec["interactions"]
    stage_rows = "\n".join(
        f"| `{stage['id']}` | {_markdown(stage['name'])} | {_markdown(stage['purpose'])} | `{stage['actor']}` | {_markdown(stage['entry_condition'])} | {_markdown('; '.join(stage['reads']) or 'No declared read')} | {_markdown('; '.join(stage['activities']))} | {_markdown('; '.join(stage['writes']) or 'No declared write')} | {_markdown('; '.join(stage['visible_progress']))} | {_markdown(stage['completion_condition'])} | {_markdown('; '.join(stage['next']))} | {_markdown(stage['failure_path'])} |"
        for stage in spec["workflow_stages"]
    )
    rows = "\n".join(
        f"| `{item['gap_type']}` | {_markdown(item['condition'])} | `{item['iai_edge']}` | `{item['interaction_goal']}` |"
        for item in interactions
    )
    bindings = {
        "H": "User retaining or explicitly delegating task decisions",
        "T": spec["goal"], "I": "Declared task-specific user decisions and returns",
        "Aug": "Instruction grounded in current canonical state and scoped delegation",
        "A": spec["desired_output"], "G": spec["execution"]["effective_executor"],
        **(spec.get("node_bindings") or {}),
    }
    binding_rows = "\n".join(f"| {node} | {_markdown(bindings[node])} |" for node in ("H", "T", "I", "Aug", "A", "G"))
    chains = _author_chains(spec)
    chain_rows = "\n".join(
        f"| `{chain['id']}` | {_markdown(chain.get('name') or chain['id'])}: {_markdown(chain.get('function') or '')} | `{', '.join(edge['type'] for edge in chain['edges'])}` |"
        for chain in chains
    )
    chain_notes = "\n".join(
        f"- `{chain['id']}` / `{edge['type']}`: {_markdown(edge['explanation'])}"
        for chain in chains for edge in chain["edges"] if edge.get("explanation")
    )
    routing_rows = "\n".join(
        f"| `{item['gap_type']}` | `{short}-{_slugify(item['id'])}` | `{item['interaction_goal']}` | `{item['iai_edge']}` | {', '.join(f'`{key}`' for key in item['expected_return'])} |"
        for item in interactions
    )
    outcome_rows = "\n".join(
        f"| `{item['id']}` | `{outcome['id']}` | `{_markdown(json.dumps(outcome['when'], ensure_ascii=False))}` | `{outcome['state_update_target']}` | {_markdown(outcome['merge_strategy'])} | `{outcome['workflow_effect']}` | `{outcome['next_stage']}` | `{str(outcome['terminal']).lower()}` |"
        for item in interactions
        for outcome in item["return_outcomes"]
    )
    first = interactions[0]
    source, target = first["iai_edge"].split("→", 1)
    gap_example = {
        "handoff_type": "planner_handoff",
        "planner_id": short,
        "planner_decision": "gap_open",
        "gap_requests": [{
            "chain_id": first["chain_id"],
            "gap_type": first["gap_type"],
            "selected_widget_id": f"{short}-{_slugify(first['id'])}",
            "interaction_goal": first["interaction_goal"],
            "iai_binding": {
                "source_nodes": [source],
                "maps_to_edge": first["iai_edge"],
                "target_node": target,
                "reason": f"On {first['iai_edge']}, {first['condition']} Pending {source} evidence has not supplied the required {target} transfer; guessing would invent the user's decision. The declared return resolves that deficit for Layer 1's outcome-specific merge.",
            },
            "display_context": {
                "stage_id": first["stage_id"],
                "purpose": first["purpose"],
                "prompt": first["prompt"],
                "information_requirements": first["display"],
            },
            "expected_return": first["expected_return"],
            "order": 1,
            "depends_on_previous": False,
        }],
        "return_to": f"l1-{short}-core",
    }
    selected_tool = spec["execution"]["tool_name"]
    executor = (
        {"kind": "tool", "name": selected_tool}
        if spec["execution"]["mode"] == "image_tool"
        else {"kind": "main_model"}
    )
    execution_parameters = (
        spec["execution"]["tool_parameters"]
        if spec["execution"]["mode"] == "image_tool"
        else {"confirmed_task_state": "current canonical state"}
    )
    execution_example = {
        "handoff_type": "planner_handoff",
        "planner_id": short,
        "planner_decision": "instruction_ready",
        "execution_instruction": {
            "executor": executor,
            "parameters": execution_parameters,
            "purpose": spec["desired_output"],
        },
        "return_to": f"l1-{short}-core",
    }
    if spec["execution"]["effective_executor"] == "main_model":
        readiness_text = "Layer 2 directly invokes the active main model to execute the ready instruction."
    elif spec["execution"]["mode"] == "image_tool":
        readiness_text = (
            f"Layer 2 directly invokes the selected registered image tool `{selected_tool}` with the declared canonical-state parameter mapping."
        )
    else:
        readiness_text = "Do not emit an execution instruction until a reviewed custom adapter has been registered; escape with the missing capability."
    return f"""---
name: l2-{short}-planner
description: {_yaml_quote('Use when: Layer 1 routed the current ' + spec['task_family'] + ' task to the ' + short + ' planner.')}
---

# L2 Planner - {spec['title']}

## Workflow End Authority

Only Layer 1 owns canonical workflow state and decides workflow completion. Layer 2 returns every result or failure directly to Layer 1 and never presents planner-local completion as final.

## Layer & Role

Layer 2 freely plans the current pass and decides whether it needs user interaction, main-model work, one or more registered tools, inspection, preparation, or execution. For Execution Pathway, Layer 2 directly invokes the selected executor or active main model, preserving the planned parameters and purpose without L3 or L4.

Plan exactly one pass toward this outcome: {_markdown(spec['goal'])}. Read interaction timing, available user resources, prior decisions, and execution state; choose one atomic paradigm, diagnose its smallest material semantic gap, and select one eligible widget registry entry. Perform domain reasoning, but do not author the selected widget contract or render UI.

## Inputs (from core_handoff and widget registry)

Require `selected_planner: {short}`, `state_snapshot.user_text` and `conversation_context`. Optionally consume {', '.join(f'`{field}`' for field in spec['canonical_state'])} and `prior_returns`. Read the routing projection from `registry/widgets.json` and actual runtime availability.

## IAI Domain Binding

| Node | Meaning |
| --- | --- |
{binding_rows}

## Interaction Chains

| Chain ID | Paradigm / function | Ordered edges |
| --- | --- | --- |
{chain_rows}

These are information-flow paradigms, not mandatory user stages. H supplies intent or a retained decision; I is pending until submitted. Aug compiles evidence; G performs selected execution; distinguish any existing A from the new result A by actual revision. Preserve each declared chain's order and repeated edges.
{chain_notes}

## Task Workflow

Choose the next eligible work or interaction by current evidence and actual dependencies, not stage-list order. Stage entry/completion conditions, declared reads/writes, lifecycle invalidation and genuinely required user authorization constrain that choice; they are not a mechanical sequence or invented approval gates. Do not advance merely because work was attempted. Preserve valid prior decisions and scoped delegation; silence is not authorization, and bounded preparation never authorizes final execution.

| stage | name | purpose | actor | entry | reads | activities | writes | visible progress | complete when | next | failure path |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
{stage_rows}

On failure, return the actual failure to L1 with the active stage's declared recovery path. If a user change invalidates upstream state, let L1 invalidate affected dependencies; re-evaluate the next necessary work from current evidence rather than restarting unaffected stages or continuing from stale progress.

## Diagnosis

Read state before/after a GenAI invocation and along prompt-only/artifact-grounded resources. Derive the material source-to-target deficit from intent, current evidence and scoped delegation before selecting a widget. Assess domain gaps as open, resolved or not applicable with evidence; silence is not delegation. Preserve this plugin's approved stages and lifecycle rather than importing main's categories or inventing new checkpoints.

| gap_type | Condition | Edge | Interaction goal |
| --- | --- | --- | --- |
{rows}
| `instruction_ready` | Applicable domain gaps are closed by current evidence, or only bounded prerequisite preparation is justified with unresolved choices left open. | `Aug→G` then `G→A` | Directly invoke the selected executor and return actual results to L1; preparation never authorizes final execution. |

Select one next material gap by real dependencies, preserving resolved evidence unless invalidated. Record source/transfer/target/closure and why guessing is unjustified in `iai_binding.reason`; record readiness evidence and scope in `execution_instruction.purpose`. Technical failures are failures, not fabricated gaps or false readiness.

## Widget Registry Routing

| Diagnosed gap | Selected widget ID | Interaction goal | Edge | Required return keys |
| --- | --- | --- | --- | --- |
{routing_rows}

Filter widget registry entries by planner compatibility, exact gap, interaction goal, IAI edge, expected-return coverage, artifact support, and renderer/runtime availability. Rank by semantic coverage, artifact specificity, return coverage, runtime fitness, stable registry order, then registry `id`. Select one eligible entry and emit only its registry `id` as `selected_widget_id`. Only eligible gaps enter Layer 3 for interaction design. Gap routing failures including `no_eligible_widget` return directly to Layer 1 without Layer 3 entry; preserve `planner_id`, `diagnosed_gap`, `rejected_candidates`, and `return_to`. Layer 3 validates and designs the selected entry without rerouting it.

## Return Outcome Semantics

Layer 1 interprets the raw widget `values` after re-entry. Match one declared `when` subset there; apply that row's state update and merge rule before selecting the next stage. A nonterminal outcome continues in the same agent turn through a fresh L1 pass. Only Layer 1 may decide that a terminal outcome authorizes End.

| interaction | outcome | match values | state target | merge | workflow effect | next stage | terminal |
| --- | --- | --- | --- | --- | --- | --- | --- |
{outcome_rows}

## Gap Handoff

```json
{json.dumps(gap_example, indent=2, ensure_ascii=False)}
```

This example assumes the declared condition holds for an actual current revision; replace its design-time context with real evidence. Layer 3 must preserve `selected_widget_id`, `chain_id`, the exact gap, goal, binding including `reason`, and expected return. The edge source belongs to `source_nodes`; its destination equals `target_node` and `iai.state_update_target`. Layer 1 alone maps that node to the outcome's canonical domain target. L3 must not search for or substitute another widget.

## Execution Handoff

{readiness_text}

The following plan is a shape illustration, not evidence of readiness. Before invocation, fill parameters from actual canonical state and make `purpose` identify closure evidence or bounded preparation scope; never fabricate a result, approval or delegation.

```json
{json.dumps(execution_example, indent=2, ensure_ascii=False)}
```

## Procedure

1. Inspect the complete core handoff and L1-reconstructed lifecycle state; choose eligible work by current evidence and dependencies within the declared stage conditions and actual authorization scope, not stage-list order.
2. Read only the state declared by that stage and perform its task-specific activities.
3. Diagnose the next material per-edge gap by dependencies, select its named chain, filter/rank eligible entries, and emit one semantic request when current evidence requires a declared human interaction.
4. Return only the active stage's declared outputs and progress/evidence to Layer 1 for canonical merging; never mutate canonical state here.
5. When execution is ready, plan and directly invoke the selected executor or active main model only if runtime readiness permits it. Return actual results or failures directly to Layer 1.
6. After any return, re-enter Layer 1; then transition, loop, stop, or escape from the newest canonical state.

## Domain Invariants

- Deliver: {_markdown(spec['desired_output'])}
- Process visibility: {_markdown(spec['process_visibility'])}
- Revision policy: {_markdown(spec['revision_policy'])}
- Final surface and format: {_markdown(spec['final_presentation']['surface'])}; {_markdown(spec['final_presentation']['format'])}.
- Final hierarchy: {_markdown('; '.join(spec['final_presentation']['hierarchy']))}
- Final status and provenance: {_markdown('; '.join(spec['final_presentation']['status_and_provenance']))}
- Final actions: {_markdown('; '.join(spec['final_presentation']['actions']))}
- Empty, partial, and error presentation: {_markdown('; '.join(spec['final_presentation']['empty_partial_error_states']))}
{chr(10).join('- ' + _markdown(item) for item in spec['trust_requirements']) or '- Preserve explicit user control and do not fabricate completion.'}

## Stop, Continue, and Escape

Continue through Layer 1 after a return supplies new state. Return a nonterminal completion candidate after the result is executed and accepted; only Layer 1 may choose Completion. Escape directly to Layer 1 when an indispensable capability is unavailable or the user declines required input.

## Prohibitions

Do not duplicate registry-derived widget metadata, author the selected widget contract, render, invoke an unselected executor, invent approval, or claim an unavailable runtime.

## Next

Interaction Pathway sends only an eligible selected-widget gap to Layer 3 for design and then Layer 4 for rendering. Execution Pathway follows `user/return -> L1 -> L2 plan -> execute/realize -> L1`: Layer 2 directly invokes the selected executor or active main model without Layer 3 or Layer 4. All gap routing failures, execution results, and failures return directly to `l1-{short}-core`. Layer 2 never produces the final workflow response or decides completion; Host Agent Return and Completion belong to Layer 1.
"""


def _control_kind(default: Any) -> str:
    if isinstance(default, bool):
        return "toggle"
    if isinstance(default, list):
        return "multi_input"
    if isinstance(default, (int, float)):
        return "number"
    return "textarea"


def _render_l3(spec: dict[str, Any], interaction: dict[str, Any], skill_name: str) -> str:
    short = spec["short_slug"]
    method_slug = _slugify(interaction["id"])
    source, target = interaction["iai_edge"].split("→", 1)
    widget_type = interaction["widget_type"]
    selected_widget_id = f"{short}-{method_slug}"
    outcome_rows = "\n".join(
        f"| `{outcome['id']}` | `{_markdown(json.dumps(outcome['when'], ensure_ascii=False))}` | `{outcome['state_update_target']}` | {_markdown(outcome['merge_strategy'])} | `{outcome['workflow_effect']}` | `{outcome['next_stage']}` | `{str(outcome['terminal']).lower()}` |"
        for outcome in interaction["return_outcomes"]
    )
    action_rows = "; ".join(
        f"{action['id']} ({action['label']}): {action['effect']}; requires_confirmation={str(action['requires_confirmation']).lower()}"
        for action in interaction["actions"]
    )
    return f"""---
name: {skill_name}
description: {_yaml_quote('Use when: the ' + short + ' planner opens ' + interaction['gap_type'] + ' for ' + interaction['interaction_goal'] + '.')}
---

# L3 Designer - {spec['title']} {interaction['id'].replace('_', ' ').title()}

## Layer & Role

Layer 3 only designs interactions for an eligible selected-widget gap in Interaction Pathway. Require `selected_widget_id: "{selected_widget_id}"` for planner `{short}`, gap `{interaction['gap_type']}`, goal `{interaction['interaction_goal']}` and stage `{interaction['stage_id']}`. Retain registry `{widget_type}` on `{interaction['surface']}` and approved design `{interaction['approved_design_id']}`. L3 owns information and interaction design; L4 implements it without inventing missing semantics.

## Inputs

Read `planner_id`, `selected_widget_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `expected_return`, `return_to`, current stage state, display context, exact local registry entry and actual runtime availability. Materialize every declared primary, context, status and provenance item from canonical state. L2 supplies intent/evidence, not a predesigned UI. Preserve approved `preview_model` design metadata: `{_markdown(json.dumps(interaction['preview_model'], ensure_ascii=False))}`; it is sample-only guidance, never a fabricated current result. Prompt intent: {_markdown(interaction['prompt'])}.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | {_markdown(interaction['purpose'])} Profile summary: {_markdown(interaction['presentation']['summary'])}. |
| Presented information | Primary: {_markdown('; '.join(interaction['display']['primary']))}. Context: {_markdown('; '.join(interaction['display']['context']) or 'none required')}. Status: {_markdown('; '.join(interaction['display']['status']) or 'none required')}. Provenance: {_markdown('; '.join(interaction['display']['provenance']) or 'none required')}. Ground each item in a resolvable display source. |
| Supported interaction | Preserve {_markdown(interaction['interaction_mode'])}, family {_markdown(interaction['widget_family'])}, archetype `{interaction['archetype']}`; actions {_markdown(action_rows)}. Input modes: {_markdown('; '.join(interaction['input_modes']) or 'action controls only')}. Derive minimal typed controls without changing approved behavior. |
| Feedback and constraints | {_markdown('; '.join(interaction['feedback']))} Validation: {_markdown('; '.join(interaction['validation']))}. Preserve declared action safeguards without inventing an extra confirmation step. |
| Submission and return | Map exactly the schema below, including actual source/serialization and optional/empty handling; preserve outcome matching and revision identity. |
| Presentation intent | Layout: {_markdown(interaction['presentation']['layout'])}; emphasis: {_markdown(interaction['presentation']['emphasis'])}; density: {_markdown(interaction['presentation']['density'])}; signature features: {_markdown('; '.join(interaction['presentation']['signature_features']))}. Use semantic hierarchy, not implementation code. |

## Essential Constraints

- Validate exact selection ID, skill/path, planner/gap/goal/edge, return coverage, artifact support, allowed destination and runtime availability. Never search for or substitute another widget.
- Preserve `chain_id` and `iai_binding.reason` unchanged in `iai.chain_id` and `iai.reason`. On `{interaction['iai_edge']}`, `{source}` belongs to `source_nodes`; `{target}` equals `target_node` and `iai.state_update_target`. Pending input is not submitted evidence.
- Canonical domain destination remains `{interaction['state_update_target']}` via L1 outcome interpretation, not a replacement IAI node. Retain deterministic domain merge policy: {_markdown(interaction['merge_strategy'])}. Preserve all declared `outcome_semantics` below; only L1 applies their domain targets and terminal flags.
- Ground actual values, candidates, assets, uploads and revisions; never turn a shape hint or sample preview into evidence. Preserve complete host asset references for L4's `window.widgetAssetUrl(ref)`.
- One primary submission of current values; no invented approval checkbox or second confirmation. Preserve declared actions and safeguards. Produce no HTML, CSS, JavaScript, iframe code, scripts, event handlers, remote implementation assets, rendering calls or task execution.

Schema return requirements (exact keys and types; hints are not runtime defaults):

| Return key | Declared type/shape | Mapping and validation obligation |
| --- | --- | --- |
{_return_schema_rows(interaction['expected_return'], examples=True)}

Both `expected_return` and `presentation.profile.interaction.submission.return_mapping` must contain exactly these keys. Preserve nested shapes and optional/empty semantics, grounded sources and producible serialization, not mock JSON.

L1 outcome semantics (copy as `iai.outcome_semantics`; do not execute here):

| outcome | match raw values | canonical state target | merge strategy | workflow effect | next stage | terminal |
| --- | --- | --- | --- | --- | --- | --- |
{outcome_rows}

Interpret the unmodified widget return in Layer 1 by matching raw `values` against exactly one `outcome_semantics[].when`; only then apply its state target, merge strategy, workflow effect and next stage. Retain unrelated confirmed state; never ask the host to translate returns into workflow state. Declared next effect for L1: {_markdown(interaction['next_effect'])}.

## Output and Handoff

Pass a complete semantic contract using these eight local obligations; no success `handoff_type` or external document read:

{LOCAL_WIDGET_HANDOFF}

Check grounded resolvable sources, unique controls, constraints, requirements, raw outcome coverage and exact producible return mappings before loading `l4-{short}-renderer`. Invalid selection or missing indispensable evidence/capability returns `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors` identifying failed checks, and `return_to: l1-{short}-core`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only Layer 1 owns canonical workflow state and decides Completion (`decision: end`) or Host Agent Return. Every Layer 3 error returns directly to Layer 1 without Layer 4 entry. Gap routing failures including `no_eligible_widget` return directly from Layer 2 to Layer 1. Execution Pathway belongs to Layer 2, which directly invokes the selected executor or active main model without Layer 3 or Layer 4. Every widget or renderer return/failure re-enters `l1-{short}-core`; submission and outcome terminal flags are nonterminal evidence until L1 decides.
"""


def _render_l4(spec: dict[str, Any]) -> str:
    short = spec["short_slug"]
    first = spec["interactions"][0]
    first_widget_type = first["widget_type"]
    accepted_types = list(dict.fromkeys(
        interaction["widget_type"]
        for interaction in spec["interactions"]
    ))
    profile_rows = "\n".join(
        f"| `{interaction['widget_type']}` | `{interaction['stage_id']}` | {_markdown(interaction['interaction_mode'])} | {_markdown('; '.join(interaction['display']['primary']))} | {_markdown('; '.join(action['label'] for action in interaction['actions']))} |"
        for interaction in spec["interactions"]
    )
    request = {
        "widget_type": first_widget_type,
        "selected_widget_id": f"{short}-{_slugify(first['id'])}",
        "render_mode": "generated",
        "title": spec["title"],
        "html": "<main></main>",
        "css": "",
        "js": "",
        "height": 440,
        "display": {},
        "controls": [],
        "planner_id": short,
        "interaction_goal": first["interaction_goal"],
        "expected_return": first["expected_return"],
    }
    return f"""---
name: l4-{short}-renderer
description: {_yaml_quote('Use when: rendering a validated ' + spec['title'] + ' guided interaction contract in the conversation.')}
---

# L4 Renderer - {spec['title']}

## Workflow End Authority

After any widget return or renderer failure, immediately load `l1-{short}-core` with the structured result. Layer 4 never decides workflow completion, emits the final response, or continues directly to a planner or executor.

## Layer & Role

Accept only {', '.join(f'`{item}`' for item in accepted_types)} reached through a fresh `L1 -> L2 -> L3` pass on Interaction Pathway. L3 owns semantic design; L4 owns concrete accessible implementation. Execution Pathway, Host Agent Return and Completion do not enter L4. This skill is self-contained: no other renderer skill or external contract read is required.

## Inputs

Validate all eight local obligations before rendering; no success `handoff_type` is added:

{LOCAL_WIDGET_HANDOFF}

Require planner `{short}` and exact selected registry type/surface, including an artifact surface only when declared with actual current binding. Resolve every content source against `display`, validate unique controls, supported actions and constraints, exact expected-return mappings and all four requirements arrays. Preserve domain `iai.outcome_semantics` for L1; it alone maps the IAI destination into canonical fields. Missing/inconsistent semantics, unsafe input, stale references or unavailable capabilities produce a structured renderer failure to `l1-{short}-core` without rendering or semantic repair. A profile summary is not a complete contract.

## Interaction Profiles

| contract | workflow stage | interaction mode | required information | supported actions |
| --- | --- | --- | --- | --- |
{profile_rows}

Render the contract's primary information before context, status, and provenance. Preserve its declared input modes, disabled states, feedback, validation, and signature features. Do not flatten distinct contracts into one generic form.

## Shared Style and Layout Baseline

Use one `.iai-widget` root with a title/summary region, one primary content region, and a trailing `.iai-actions` region. Reuse only the host's `.iai-*` classes and `--iai-*` tokens for shared roles; task-specific styling may control layout and emphasis but must not redefine the palette, typography, spacing language, cards, or buttons.

- Keep the root and primary content at `width: 100%` and `max-width: 100%`, with no fixed outer width or body-level horizontal scrolling.
- Give every Grid/Flex child `min-width: 0` and use shrink-safe tracks such as `minmax(0, 1fr)`. At `max-width: 560px`, collapse multi-column content to one column and move inspectors below their stage or preview.
- Keep the widget usable at a 266px viewport. Wrap machine-like labels anywhere, constrain controls and media to their container, and never overlap text, controls, feedback, or actions.
- Keep `.iai-actions` in normal flow after the content; actions may wrap or stack, but submit/accept remains visually primary and dismiss/cancel remains secondary.
- Match the host application's typography scale, neutral surfaces, borders, spacing, focus and control density. Use native accessible controls and familiar command icons with accessible names/tooltips when available. Checkboxes represent actual boolean/multi-value settings, never confirmation, approval, acceptance or submission.
- No nested decorative cards or marketing copy. Keep keyboard, focus, disabled, loading, error and submission states accessible; never use browser modal APIs.
- Use stable bounded dimensions for canvases, previews, boards, and toolbars so selection, validation, loading, expansion, and error states do not shift the whole interaction unexpectedly.
- Before rendering, inspect generated markup and CSS for hardcoded visual styles, fixed/minimum widths, non-shrinking tracks, unbreakable content, nested card decoration, absolute positioning, and unreachable actions; repair every violation.

## Input Validation

Require a supported type and its exact registered surface, planner `{short}`, purpose, goal, complete IAI metadata, display, controls, presentation profile, widget requirements, expected return and disabled embedded content. Reject stale artifact bindings, undeclared controls, or changed return keys. Implement every `widget_requirements` item and each submission precondition without adding a new stage or guessing missing values.

## Rendering and Mapping

Generate concrete accessible HTML, CSS, and JavaScript and call `render_html_widget` exactly once. Pass `selected_widget_id`, `display`, `controls`, `planner_id`, `interaction_goal`, and `expected_return` unchanged. Treat `selected_widget_id` as trace metadata only.

Compile profile, requirements, safety and applicable runtime declarations into existing render request fields and sandbox behavior, not new undocumented tool arguments. The host does not validate the profile or return schema on your behalf. The shape below is not ready markup; construct a working accessible implementation from the validated profile.

```json
{json.dumps(request, indent=2, ensure_ascii=False)}
```

Initialize from `window.widgetDisplay`, then bind handlers. Submit only through `window.submitWidget(values)` and dismiss through `window.dismissWidget(note)`. Validate inline before submission and make every visible control affect state, feedback, or return data.

## Image Asset Protocol

When the contract cites an image, keep the complete host-supplied asset reference in `display`, read that reference from `window.widgetDisplay`, and assign only `window.widgetAssetUrl(ref)` to `src`, `srcset`, SVG image `href`, poster, or CSS image URLs. Never read a local `path` or `url` and never construct `file://`; do not invent asset ids or remote image URLs. Render an explicit unavailable state when the contract has no image reference.

## Stable Return Invariants

Return the host envelope with widget id, planner id, action, values, free-form note, and timestamp. Preserve the exact expected keys and types. Do not infer user approval from dismissal or missing values.

## Final Presentation Alignment

When rendering the final result review, preserve this approved presentation: format `{_markdown(spec['final_presentation']['format'])}` on `{_markdown(spec['final_presentation']['surface'])}`; sections {_markdown('; '.join(spec['final_presentation']['sections']))}; hierarchy {_markdown('; '.join(spec['final_presentation']['hierarchy']))}; status and provenance {_markdown('; '.join(spec['final_presentation']['status_and_provenance']))}; actions {_markdown('; '.join(spec['final_presentation']['actions']))}; non-happy states {_markdown('; '.join(spec['final_presentation']['empty_partial_error_states']))}.

## Runtime, Prohibitions, and Next

Use deterministic local state and shared design tokens. Do not access parent DOM, storage, cookies, tokens, local files, or undeclared networks. Do not diagnose gaps, select another interaction, call task tools, or change semantics. Every outcome returns to `l1-{short}-core`.
"""


def _compile_bundle(session_id: str, spec: dict[str, Any]) -> tuple[dict[str, bytes], list[dict[str, Any]], list[str]]:
    short = spec["short_slug"]
    resource_files, resource_records, resource_warnings = _resource_bundle(session_id, spec)
    gap_categories = [item["gap_type"] for item in spec["interactions"]]
    edges = list(dict.fromkeys(edge["type"] for chain in _author_chains(spec) for edge in chain["edges"]))
    selected_tool = spec["execution"]["tool_name"] if spec["execution"]["mode"] == "image_tool" else None
    allowed_tools = [selected_tool] if selected_tool else []
    planner = {
        "id": short,
        "skill": f"l2-{short}-planner",
        "layer": "layer-2",
        "canonical_skill_path": f"skills/l2-{short}-planner/SKILL.md",
        "task_family": spec["task_family"],
        "required_state": ["user_text", "conversation_context"],
        "optional_state": [*spec["canonical_state"], "prior_returns"],
        "iai_edges": list(dict.fromkeys([*edges, "Aug→G", "G→A"])),
        "gap_categories": gap_categories,
        "allowed_tools": allowed_tools,
        "loop_return_to": f"l1-{short}-core",
        "trigger_summary": spec["description"],
    }
    widgets: list[dict[str, Any]] = []
    l3_files: dict[str, str] = {}
    for interaction in spec["interactions"]:
        method_slug = _slugify(interaction["id"])
        l3_skill = _bounded_skill_name("l3", short, method_slug)
        widget_type = interaction["widget_type"]
        capabilities = [
            "show_primary_information",
            *(["show_supporting_context"] if interaction["display"]["context"] else []),
            *(["show_status"] if interaction["display"]["status"] else []),
            *(["show_provenance"] if interaction["display"]["provenance"] else []),
            *(f"action_{action['id']}" for action in interaction["actions"]),
            *(_identifier(mode, "input") for mode in interaction["input_modes"]),
        ]
        widgets.append({
            "id": f"{short}-{method_slug}",
            "skill": l3_skill,
            "layer": "layer-3",
            "canonical_skill_path": f"skills/{l3_skill}/SKILL.md",
            "widget_type": widget_type,
            "surface": interaction["surface"],
            "interaction_modality": _identifier(interaction["interaction_mode"], interaction["archetype"]),
            "supported_artifact_types": interaction["supported_artifact_types"] or ["any"],
            "interaction_goals": [interaction["interaction_goal"]],
            "iai_edges": [interaction["iai_edge"]],
            "gap_categories": [interaction["gap_type"]],
            "state_update_targets": [interaction["iai_edge"].split("→", 1)[1]],
            "return_mode": "schema",
            "return_field_policy": "fixed",
            "expected_return_types": list(interaction["expected_return"]),
            "widget_capabilities": list(dict.fromkeys(capabilities)),
            "primary_renderer": "render_html_widget",
            "compatible_planners": [short],
        })
        l3_files[f"skills/{l3_skill}/SKILL.md"] = _render_l3(spec, interaction, l3_skill)
    tools = [{
        "id": "render_html_widget",
        "callable": "render_html_widget",
        "layer": "layer-4",
        "category": "html_widget_renderer",
        "description": f"Render {spec['title']} guided interaction contracts.",
    }]
    if selected_tool:
        tools.append({
            "id": selected_tool,
            "callable": selected_tool,
            "layer": "layer-2",
            "category": "gpt_image_executor",
            "description": GPT_IMAGE_TOOL_EXECUTORS[selected_tool],
        })
    text_files = {
        "SKILL.md": _render_root(spec, resource_records),
        f"skills/l1-{short}-core/SKILL.md": _render_l1(spec),
        f"skills/l2-{short}-planner/SKILL.md": _render_l2(spec),
        **l3_files,
        f"skills/l4-{short}-renderer/SKILL.md": _render_l4(spec),
        "registry/planners.json": json.dumps({"schema_version": "1.0", "planners": [planner]}, indent=2, ensure_ascii=False) + "\n",
        "registry/widgets.json": json.dumps({"schema_version": "1.0", "widgets": widgets}, indent=2, ensure_ascii=False) + "\n",
        "registry/tools.json": json.dumps({"schema_version": "1.0", "tools": tools}, indent=2, ensure_ascii=False) + "\n",
        "tests/scenarios.json": json.dumps({"schema_version": "1.0", "cases": spec["validation_cases"]}, indent=2, ensure_ascii=False) + "\n",
    }
    text_files[f"skills/{spec['plugin_id']}/SKILL.md"] = text_files["SKILL.md"]
    files = {path: text.encode("utf-8") for path, text in text_files.items()}
    files.update(resource_files)
    return files, resource_records, resource_warnings


def _bundle_hash(files: dict[str, bytes]) -> str:
    digest = hashlib.sha256()
    for relative_path in sorted(files):
        digest.update(relative_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(files[relative_path])
        digest.update(b"\0")
    return digest.hexdigest()


def validate_bundle(files: dict[str, bytes]) -> dict[str, Any]:
    """Validate the generated cross-file contract without loading it as ready."""
    issues: dict[str, list[str]] = {
        "format_issues": [],
        "contract_reference_issues": [],
        "registry_reference_issues": [],
        "state_contract_issues": [],
        "return_contract_issues": [],
        "unreferenced_l3_skills": [],
        "l2_registry_gap_drift": [],
        "unmatched_l2_handoffs": [],
        "invalid_executors": [],
        "invalid_renderer_refs": [],
        "invalid_runtime_bindings": [],
        "layer_boundary_violations": [],
    }
    contract_reference = canonical_contract_reference()
    issues["contract_reference_issues"].extend(contract_reference["issues"])
    required_registry = ("registry/planners.json", "registry/widgets.json", "registry/tools.json")
    for path in ("SKILL.md", *required_registry):
        if path not in files:
            issues["format_issues"].append(f"missing {path}")
    root_declares_scenarios = b"## Validation Cases" in files.get("SKILL.md", b"")
    if root_declares_scenarios or "tests/scenarios.json" in files:
        try:
            scenarios = json.loads(files["tests/scenarios.json"].decode("utf-8"))["cases"]
            if not isinstance(scenarios, list) or not scenarios:
                issues["format_issues"].append("tests/scenarios.json requires at least one validation case")
            elif not all(isinstance(case, dict) and case.get("id") and case.get("user_input") for case in scenarios):
                issues["format_issues"].append("every validation case requires id and user_input")
        except (KeyError, TypeError, json.JSONDecodeError, UnicodeDecodeError) as error:
            issues["format_issues"].append(f"invalid tests/scenarios.json: {error}")
    skill_paths = [path for path in files if re.fullmatch(r"(?:skills/[^/]+/)?SKILL\.md", path)]
    skill_names: dict[str, str] = {}
    for path in skill_paths:
        text = files[path].decode("utf-8", errors="replace")
        if not text.startswith("---\n") or len(re.findall(r"^---\s*$", text, re.MULTILINE)) != 2:
            issues["format_issues"].append(f"{path}: invalid frontmatter")
        if len(FRONTMATTER_NAME_RE.findall(text)) != 1 or len(H1_RE.findall(text)) != 1:
            issues["format_issues"].append(f"{path}: requires one name and one H1")
        name_match = FRONTMATTER_NAME_RE.search(text)
        if name_match:
            skill_names[path] = name_match.group(1)
            expected_name = Path(path).parent.name if path != "SKILL.md" else name_match.group(1)
            issues["format_issues"].extend(f"{path}: {error}" for error in _skill_structure_issues(text, expected_name))
            if path != "SKILL.md" and name_match.group(1) != expected_name:
                issues["registry_reference_issues"].append(
                    f"{path}: frontmatter name '{name_match.group(1)}' does not match directory '{expected_name}'"
                )
    root_name_match = FRONTMATTER_NAME_RE.search(files.get("SKILL.md", b"").decode("utf-8", errors="replace"))
    if root_name_match:
        callable_root_path = f"skills/{root_name_match.group(1)}/SKILL.md"
        if callable_root_path not in files:
            issues["registry_reference_issues"].append(
                f"missing callable root skill alias: {callable_root_path}"
            )
        elif files[callable_root_path] != files["SKILL.md"]:
            issues["registry_reference_issues"].append(
                f"callable root skill alias differs from root contract: {callable_root_path}"
            )
    try:
        planners = json.loads(files[required_registry[0]].decode("utf-8"))["planners"]
        widgets = json.loads(files[required_registry[1]].decode("utf-8"))["widgets"]
        tools = json.loads(files[required_registry[2]].decode("utf-8"))["tools"]
    except (KeyError, TypeError, json.JSONDecodeError, UnicodeDecodeError) as error:
        issues["format_issues"].append(f"invalid registry JSON: {error}")
        planners, widgets, tools = [], [], []
    tool_ids = {str(tool.get("id")) for tool in tools}
    renderer_ids = {"render_html_widget", "render_interactive_widget"} | {
        str(tool.get("id")) for tool in tools if tool.get("layer") == "layer-4"
    }
    planner_ids = {str(planner.get("id")) for planner in planners}
    widgets_by_id = {str(widget.get("id")): widget for widget in widgets}
    referenced_l3 = {str(widget.get("canonical_skill_path")) for widget in widgets}
    l1_paths = [path for path in skill_paths if path.startswith("skills/l1-")]
    l4_paths = [path for path in skill_paths if path.startswith("skills/l4-")]
    if len(l1_paths) != 1:
        issues["registry_reference_issues"].append(f"expected exactly one L1 skill, found {len(l1_paths)}")
    if len(l4_paths) != 1:
        issues["registry_reference_issues"].append(f"expected exactly one L4 skill, found {len(l4_paths)}")
    for path in files:
        if path.startswith("skills/l3-") and path.endswith("/SKILL.md") and path not in referenced_l3:
            issues["unreferenced_l3_skills"].append(path)
    for planner in planners:
        planner_id = str(planner.get("id"))
        skill_path = str(planner.get("canonical_skill_path") or "")
        if skill_path not in files:
            issues["registry_reference_issues"].append(f"planner '{planner_id}' skill path is missing: {skill_path}")
        elif skill_names.get(skill_path) != str(planner.get("skill") or ""):
            issues["registry_reference_issues"].append(f"planner '{planner_id}' skill identity does not match registry")
        if l1_paths and planner.get("loop_return_to") != skill_names.get(l1_paths[0]):
            issues["state_contract_issues"].append(f"planner '{planner_id}' loop_return_to does not match installed L1")
        if not set(planner.get("allowed_tools") or []) <= tool_ids:
            issues["invalid_executors"].append(planner_id)
        if renderer_ids.intersection(planner.get("allowed_tools") or []):
            issues["layer_boundary_violations"].append(f"planner '{planner_id}' allowed_tools cannot include an L4 renderer")
        text = files.get(skill_path, b"").decode("utf-8", errors="replace")
        for required_text in (
            "# L2 Planner -",
            "Layer 2 directly invokes the selected executor or active main model",
            "Only eligible gaps enter Layer 3",
            "Gap routing failures including `no_eligible_widget` return directly to Layer 1",
        ):
            if required_text not in text:
                issues["layer_boundary_violations"].append(f"{skill_path}: missing {required_text}")
        for pattern in (r"\btarget_widget\b", r"\bwidget_type\b", r"\binteraction_modality\b", r"l3-[A-Za-z0-9-]+"):
            if re.search(pattern, text):
                issues["layer_boundary_violations"].append(f"{skill_path}: {pattern}")
        declared_gaps = set(re.findall(r'"gap_type"\s*:\s*"([A-Za-z][A-Za-z0-9_-]*_gap)"', text))
        if not declared_gaps <= set(planner.get("gap_categories") or []):
            issues["l2_registry_gap_drift"].append(planner_id)
        for gap_type in declared_gaps:
            if not any(
                planner_id in (widget.get("compatible_planners") or [])
                and gap_type in (widget.get("gap_categories") or [])
                for widget in widgets
            ):
                issues["unmatched_l2_handoffs"].append(f"{planner_id}:{gap_type}")
        for raw_json in re.findall(r"```json\s*\n(.*?)\n```", text, re.DOTALL):
            try:
                handoff = json.loads(raw_json)
            except json.JSONDecodeError:
                continue
            if handoff.get("handoff_type") != "planner_handoff":
                continue
            for gap in handoff.get("gap_requests") or []:
                selected_widget_id = str(gap.get("selected_widget_id") or "")
                selected_widget = widgets_by_id.get(selected_widget_id)
                edge = str((gap.get("iai_binding") or {}).get("maps_to_edge") or "")
                if not selected_widget or not (
                    planner_id in (selected_widget.get("compatible_planners") or [])
                    and str(gap.get("gap_type")) in (selected_widget.get("gap_categories") or [])
                    and str(gap.get("interaction_goal")) in (selected_widget.get("interaction_goals") or [])
                    and edge in (selected_widget.get("iai_edges") or [])
                ):
                    issues["unmatched_l2_handoffs"].append(
                        f"{planner_id}:{gap.get('gap_type')}:{selected_widget_id or 'missing-selection'}"
                    )
                    continue
                expected_return = gap.get("expected_return")
                if isinstance(expected_return, dict):
                    expected_fields = set(expected_return)
                    policy = str(selected_widget.get("return_field_policy") or "fixed")
                    return_mode = str(selected_widget.get("return_mode") or "schema")
                    if policy != "planner_declared" and return_mode == "schema" and not expected_fields <= set(selected_widget.get("expected_return_types") or []):
                        issues["return_contract_issues"].append(
                            f"{planner_id}:{gap.get('gap_type')} expected return is not covered by '{selected_widget_id}'"
                        )
    if l1_paths:
        l1_text = files[l1_paths[0]].decode("utf-8", errors="replace")
        for pathway in ("Interaction Pathway", "Execution Pathway", "Host Agent Return", "Completion"):
            for path in ("SKILL.md", l1_paths[0]):
                if f"**{pathway}:**" not in files.get(path, b"").decode("utf-8", errors="replace"):
                    issues["layer_boundary_violations"].append(f"{path}: missing pathway {pathway}")
        for required_text in (
            "## Layer & Role",
            "Only Layer 1 owns the canonical workflow state",
            "after every interaction or execution result or failure",
            "do not decide completion",
        ):
            if required_text not in l1_text:
                issues["state_contract_issues"].append(
                    f"{l1_paths[0]}: missing workflow End authority contract: {required_text}"
                )
        declared_state = {
            field
            for planner in planners
            for field in [*(planner.get("required_state") or []), *(planner.get("optional_state") or [])]
        }
        for raw_json in re.findall(r"```json\s*\n(.*?)\n```", l1_text, re.DOTALL):
            try:
                handoff = json.loads(raw_json)
            except json.JSONDecodeError:
                continue
            if handoff.get("handoff_type") != "core_handoff" or handoff.get("decision") != "route_to_planner":
                continue
            state_fields = set((handoff.get("state_snapshot") or {}).keys()) - {"user_text", "prior_returns"}
            undeclared = state_fields - declared_state
            if undeclared:
                issues["state_contract_issues"].append(
                    "L1 state_snapshot contains fields absent from planner registry: " + ", ".join(sorted(undeclared))
                )
    for widget in widgets:
        if str(widget.get("primary_renderer")) not in tool_ids:
            issues["invalid_renderer_refs"].append(str(widget.get("id")))
        if not set(widget.get("compatible_planners") or []) <= planner_ids:
            issues["unmatched_l2_handoffs"].append(str(widget.get("id")))
        skill_path = str(widget.get("canonical_skill_path") or "")
        if skill_path not in files:
            issues["registry_reference_issues"].append(f"widget '{widget.get('id')}' skill path is missing: {skill_path}")
        elif skill_names.get(skill_path) != str(widget.get("skill") or ""):
            issues["registry_reference_issues"].append(f"widget '{widget.get('id')}' skill identity does not match registry")
        skill_text = files.get(skill_path, b"").decode("utf-8", errors="replace")
        if "selected_widget_id" not in skill_text or str(widget.get("id")) not in skill_text:
            issues["unmatched_l2_handoffs"].append(f"{widget.get('id')}:missing-l3-selection-trace")
        if "selected_widget_invalid" not in skill_text:
            issues["unmatched_l2_handoffs"].append(f"{widget.get('id')}:missing-invalid-selection-output")
        issues["return_contract_issues"].extend(
            f"{skill_path}: {error}" for error in _local_widget_contract_issues(skill_text)
        )
        for key in widget.get("expected_return_types") or []:
            if f"| `{key}` |" not in skill_text:
                issues["return_contract_issues"].append(f"{skill_path}: missing schema return requirement: {key}")
        for required in ("handoff_type: selected_widget_invalid", "validation_errors", "return_to:"):
            if required not in skill_text:
                issues["return_contract_issues"].append(f"{skill_path}: missing failure obligation: {required}")
        if re.search(r"(?im)^#+ .*executor|\b(?:Layer 3|L3) (?:directly invokes|executes|calls)\b", skill_text):
            issues["layer_boundary_violations"].append(f"{skill_path}: L3 cannot be a task executor")
        for required_text in (
            "# L3 Designer -",
            "Layer 3 only designs interactions",
            "Every Layer 3 error returns directly to Layer 1 without Layer 4 entry",
        ):
            if required_text not in skill_text:
                issues["layer_boundary_violations"].append(f"{skill_path}: missing {required_text}")
    for l4_path in l4_paths:
        l4_text = files[l4_path].decode("utf-8", errors="replace")
        if "selected_widget_id" not in l4_text:
            issues["invalid_renderer_refs"].append(f"{l4_path}:missing-selected-widget-trace")
        issues["return_contract_issues"].extend(
            f"{l4_path}: {error}" for error in _local_widget_contract_issues(l4_text, "Inputs")
        )
    for tool in tools:
        tool_id = str(tool.get("id") or "")
        if tool.get("layer") == "layer-3" or str(tool.get("canonical_skill_path") or "").startswith("skills/l3-"):
            issues["layer_boundary_violations"].append(f"tool '{tool_id}' cannot register an L3 executor")
        if tool.get("category") == "gpt_image_executor" and tool.get("layer") != "layer-2":
            issues["layer_boundary_violations"].append(f"tool '{tool_id}' must be invoked by L2 Planner")
        skill_path = str(tool.get("canonical_skill_path") or "")
        if skill_path:
            if skill_path not in files:
                issues["registry_reference_issues"].append(f"tool '{tool_id}' skill path is missing: {skill_path}")
            elif tool.get("skill") and skill_names.get(skill_path) != str(tool.get("skill")):
                issues["registry_reference_issues"].append(f"tool '{tool_id}' skill identity does not match registry")
    runtime_bindings = validate_runtime_bindings(files)
    issues["invalid_runtime_bindings"].extend(runtime_bindings["issues"])
    counts = {name: len(values) for name, values in issues.items()}
    return {
        "ok": not any(counts.values()),
        "counts": counts,
        "issues": issues,
        "contract_reference": contract_reference,
        "runtime_bindings": runtime_bindings,
    }


def _write_bundle(root: Path, files: dict[str, bytes]) -> None:
    for relative_path, content in files.items():
        target = root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)


def _preview_root(authoring_root: Path, session_id: str, preview_id: str) -> Path:
    if not re.fullmatch(r"[a-f0-9]{32}", preview_id):
        raise InflakAuthoringError("Invalid preview id.")
    return authoring_root / safe_session_id(session_id) / preview_id


def preview_plugin(
    session_id: str,
    target_spec: dict[str, Any],
    approved_revision: int,
    *,
    authoring_root: Path | None = None,
    plugins_root: Path | None = None,
    manifest_path: Path | None = None,
) -> dict[str, Any]:
    """Compile an immutable staging bundle and return a behavior-first review."""
    if not isinstance(approved_revision, int) or approved_revision < 1:
        raise InflakAuthoringError("approved_revision must be a positive integer.")
    resolved_authoring_root = authoring_root or AUTHORING_ROOT
    resolved_plugins_root = plugins_root or PLUGINS_DIR
    resolved_manifest_path = manifest_path or MANIFEST_PATH
    spec = _normalise_target_spec(target_spec)
    manifest = _load_manifest(resolved_manifest_path)
    existing_entry = next(
        (
            entry
            for entry in manifest["plugins"]
            if entry.get("id") == spec["plugin_id"] or entry.get("directory") == spec["plugin_id"]
        ),
        None,
    )
    destination_exists = (resolved_plugins_root / spec["plugin_id"]).exists()
    if existing_entry is not None or destination_exists:
        if not spec["replace_existing_plugin"]:
            raise InflakAuthoringError(f"Plugin '{spec['plugin_id']}' already exists; choose a different name.")
        if (
            existing_entry is None
            or existing_entry.get("id") != spec["plugin_id"]
            or existing_entry.get("directory") != spec["plugin_id"]
            or existing_entry.get("status") != "planned"
            or not destination_exists
        ):
            raise InflakAuthoringError("Only an installed planned plugin with an exact matching id may be replaced.")
    files, resource_records, resource_warnings = _compile_bundle(session_id, spec)
    validation = validate_bundle(files)
    if not validation["ok"]:
        raise InflakAuthoringError("Generated plugin failed contract validation: " + json.dumps(validation["counts"], sort_keys=True))
    preview_hash = _bundle_hash(files)
    preview_id = uuid.uuid4().hex
    parent = resolved_authoring_root / safe_session_id(session_id)
    parent.mkdir(parents=True, exist_ok=True)
    temporary = parent / f".{preview_id}.tmp"
    final = _preview_root(resolved_authoring_root, session_id, preview_id)
    if temporary.exists():
        shutil.rmtree(temporary)
    temporary.mkdir(parents=True)
    try:
        _write_bundle(temporary / "bundle", files)
        status = "ready" if spec["execution"]["runtime_readiness"] in {"ready", "ready_with_host_fallback"} else "planned"
        warnings = list(dict.fromkeys([
            *resource_warnings,
            *spec["limitations"],
            *(["A reviewed runtime adapter is still required before this plugin can run."] if status == "planned" else []),
            *([f"Configure environment variable {name} outside chat before runtime use."] for name in spec["execution"]["secret_requirements"]),
        ]))
        metadata = {
            "preview_id": preview_id,
            "preview_hash": preview_hash,
            "approved_revision": approved_revision,
            "plugin_id": spec["plugin_id"],
            "status": status,
            "replace_existing_plugin": bool(existing_entry),
            "source_scenario_run_id": spec["source_scenario_run_id"],
            "spec": spec,
            "resources": resource_records,
            "warnings": warnings,
            "validation": validation,
            "files": [{"path": path, "size": len(content)} for path, content in sorted(files.items())],
        }
        (temporary / "metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        os.replace(temporary, final)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    example_dialogue = spec["example_dialogue"] or [
        {"role": "user", "content": spec["goal"]},
        {"role": "assistant", "content": spec["workflow_stages"][0]["purpose"]},
    ]
    return {
        "action": "inflak_plugin_previewed",
        "artifact_type": "inflak-plugin-preview",
        "preview_id": preview_id,
        "preview_hash": preview_hash,
        "approved_revision": approved_revision,
        "plugin_id": spec["plugin_id"],
        "plugin_status": metadata["status"],
        "plugin_summary": {
            "title": spec["title"],
            "goal": spec["goal"],
            "desired_output": spec["desired_output"],
            "workflow_stages": spec["workflow_stages"],
            "state_model": spec["state_model"],
            "interaction_methods": spec["interactions"],
            "final_presentation": spec["final_presentation"],
            "exception_paths": spec["exception_paths"],
            "validation_cases": spec["validation_cases"],
            "human_checkpoints": spec["human_checkpoints"],
            "process_visibility": spec["process_visibility"],
        },
        "execution_summary": {
            **spec["execution"],
            "resources": resource_records,
        },
        "runtime_readiness": spec["execution"]["runtime_readiness"],
        "assumptions": spec["assumptions"],
        "limitations": spec["limitations"],
        "warnings": metadata["warnings"],
        "example_dialogue": example_dialogue,
        "validation": validation,
        "files": metadata["files"],
        "published": False,
    }


def set_plugin_status(
    plugin_id: str,
    status: str,
    *,
    manifest_path: Path | None = None,
) -> None:
    if status not in {"ready", "planned"}:
        raise InflakAuthoringError(f"Unsupported plugin status '{status}'.")
    resolved_manifest_path = manifest_path or MANIFEST_PATH
    manifest = _load_manifest(resolved_manifest_path)
    entry = next((item for item in manifest["plugins"] if item.get("id") == plugin_id), None)
    if entry is None:
        raise InflakAuthoringError(f"Plugin '{plugin_id}' is not registered.")
    entry["status"] = status
    temporary = resolved_manifest_path.with_name(f".{resolved_manifest_path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        os.replace(temporary, resolved_manifest_path)
    finally:
        temporary.unlink(missing_ok=True)
    if resolved_manifest_path.resolve() == MANIFEST_PATH.resolve():
        from backend.services.inflak_plugins import plugin_registry

        plugin_registry.cache_clear()


def validate_installed_plugin(
    plugin_id: str,
    *,
    plugins_root: Path | None = None,
    manifest_path: Path | None = None,
) -> dict[str, Any]:
    resolved_plugins_root = plugins_root or PLUGINS_DIR
    resolved_manifest_path = manifest_path or MANIFEST_PATH
    manifest = _load_manifest(resolved_manifest_path)
    entry = next((item for item in manifest["plugins"] if item.get("id") == plugin_id), None)
    issues: list[str] = []
    if entry is None:
        return {"ok": False, "plugin_id": plugin_id, "issues": ["plugin is missing from manifest"]}
    directory = str(entry.get("directory") or "")
    plugin_root = (resolved_plugins_root / directory).resolve()
    if plugin_root.parent != resolved_plugins_root.resolve() or not plugin_root.is_dir():
        return {"ok": False, "plugin_id": plugin_id, "issues": ["plugin directory is missing or unsafe"]}
    files = {
        str(path.relative_to(plugin_root)): path.read_bytes()
        for path in plugin_root.rglob("*")
        if path.is_file()
    }
    validation = validate_bundle(files)
    root_text = files.get("SKILL.md", b"").decode("utf-8", errors="replace")
    root_name = FRONTMATTER_NAME_RE.search(root_text)
    if root_name is None or root_name.group(1) != plugin_id:
        issues.append(f"root skill name must equal manifest id '{plugin_id}'")
    if entry.get("directory") != plugin_root.name:
        issues.append("manifest directory does not match installed directory")
    if not validation["ok"]:
        issues.append("installed bundle failed contract validation")
    return {
        "ok": not issues,
        "plugin_id": plugin_id,
        "manifest_status": entry.get("status"),
        "root_skill_name": root_name.group(1) if root_name else None,
        "bundle_hash": _bundle_hash(files),
        "file_count": len(files),
        "validation": validation,
        "issues": issues,
    }


def publish_plugin(
    session_id: str,
    preview_id: str,
    preview_hash: str,
    approved_revision: int,
    *,
    acknowledged_warnings: list[str] | None = None,
    authoring_root: Path | None = None,
    plugins_root: Path | None = None,
    manifest_path: Path | None = None,
) -> dict[str, Any]:
    """Atomically publish the exact staged bundle identified by hash and revision."""
    resolved_authoring_root = authoring_root or AUTHORING_ROOT
    resolved_plugins_root = plugins_root or PLUGINS_DIR
    resolved_manifest_path = manifest_path or MANIFEST_PATH
    preview_root = _preview_root(resolved_authoring_root, session_id, preview_id)
    metadata_path = preview_root / "metadata.json"
    bundle_root = preview_root / "bundle"
    if not metadata_path.is_file() or not bundle_root.is_dir():
        raise InflakAuthoringError("Preview is missing or expired.")
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise InflakAuthoringError("Preview metadata is invalid.") from error
    if metadata.get("preview_hash") != preview_hash:
        raise InflakAuthoringError("Preview hash does not match the approved bundle.")
    if metadata.get("approved_revision") != approved_revision:
        raise InflakAuthoringError("Authoring revision does not match the approved preview.")
    warnings = {str(item) for item in metadata.get("warnings") or []}
    acknowledged = {str(item) for item in acknowledged_warnings or []}
    missing_acknowledgements = sorted(warnings - acknowledged)
    if missing_acknowledgements:
        raise InflakAuthoringError(
            "Publication requires acknowledgement of every preview warning: "
            + "; ".join(missing_acknowledgements)
        )
    staged_files = {
        str(path.relative_to(bundle_root)): path.read_bytes()
        for path in bundle_root.rglob("*")
        if path.is_file()
    }
    actual_hash = _bundle_hash(staged_files)
    if actual_hash != preview_hash:
        raise InflakAuthoringError("Staging bundle changed after preview; generate a new preview.")
    validation = validate_bundle(staged_files)
    if not validation["ok"]:
        raise InflakAuthoringError("Staging bundle no longer passes contract validation.")
    preview_contract_reference = (metadata.get("validation") or {}).get("contract_reference") or {}
    preview_contract_hashes = {
        str(document.get("path")): str(document.get("sha256"))
        for document in preview_contract_reference.get("documents") or []
    }
    current_contract_hashes = {
        str(document.get("path")): str(document.get("sha256"))
        for document in validation["contract_reference"]["documents"]
    }
    if not preview_contract_hashes or preview_contract_hashes != current_contract_hashes:
        raise InflakAuthoringError(
            "Canonical skill contract changed after preview; generate and approve a new preview."
        )

    plugin_id = str(metadata.get("plugin_id") or "")
    if not PLUGIN_ID_RE.fullmatch(plugin_id):
        raise InflakAuthoringError("Preview contains an invalid plugin id.")
    manifest = _load_manifest(resolved_manifest_path)
    existing_entry = next(
        (entry for entry in manifest["plugins"] if entry.get("id") == plugin_id or entry.get("directory") == plugin_id),
        None,
    )
    replacing = bool(metadata.get("replace_existing_plugin"))
    destination = resolved_plugins_root / plugin_id
    if replacing:
        if (
            existing_entry is None
            or existing_entry.get("id") != plugin_id
            or existing_entry.get("directory") != plugin_id
            or existing_entry.get("status") != "planned"
            or not destination.is_dir()
        ):
            raise InflakAuthoringError("Approved replacement no longer targets an exact installed planned plugin.")
        existing_entry.update({
            "label": metadata["spec"]["label"],
            "description": metadata["spec"]["description"],
            "status": metadata["status"],
        })
    else:
        if existing_entry is not None:
            raise InflakAuthoringError(f"Plugin '{plugin_id}' was published already.")
        if destination.exists():
            raise InflakAuthoringError(f"Plugin directory '{plugin_id}' already exists.")
        manifest["plugins"].append({
            "id": plugin_id,
            "directory": plugin_id,
            "label": metadata["spec"]["label"],
            "description": metadata["spec"]["description"],
            "status": metadata["status"],
        })
    transaction_id = uuid.uuid4().hex
    temporary_bundle = resolved_plugins_root / f".{plugin_id}.{transaction_id}.tmp"
    backup_bundle = resolved_plugins_root / f".{plugin_id}.{transaction_id}.backup"
    temporary_manifest = resolved_manifest_path.with_name(f".{resolved_manifest_path.name}.{transaction_id}.tmp")
    resolved_plugins_root.mkdir(parents=True, exist_ok=True)
    installed = False
    try:
        shutil.copytree(bundle_root, temporary_bundle)
        temporary_manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        if replacing:
            os.replace(destination, backup_bundle)
        os.replace(temporary_bundle, destination)
        try:
            os.replace(temporary_manifest, resolved_manifest_path)
        except Exception:
            shutil.rmtree(destination, ignore_errors=True)
            if replacing and backup_bundle.exists():
                os.replace(backup_bundle, destination)
            raise
        installed = True
    finally:
        if not installed and replacing and backup_bundle.exists() and not destination.exists():
            os.replace(backup_bundle, destination)
        shutil.rmtree(temporary_bundle, ignore_errors=True)
        if installed:
            shutil.rmtree(backup_bundle, ignore_errors=True)
        temporary_manifest.unlink(missing_ok=True)

    if resolved_manifest_path.resolve() == MANIFEST_PATH.resolve():
        from backend.services.inflak_plugins import plugin_registry

        plugin_registry.cache_clear()
    installed_validation = validate_installed_plugin(
        plugin_id,
        plugins_root=resolved_plugins_root,
        manifest_path=resolved_manifest_path,
    )
    if not installed_validation["ok"]:
        set_plugin_status(plugin_id, "planned", manifest_path=resolved_manifest_path)
    return {
        "action": "inflak_plugin_published",
        "plugin_id": plugin_id,
        "plugin_status": metadata["status"] if installed_validation["ok"] else "planned",
        "preview_id": preview_id,
        "preview_hash": preview_hash,
        "approved_revision": approved_revision,
        "written": sorted(staged_files),
        "validation": validation,
        "installed_validation": installed_validation,
        "replaced_existing_plugin": replacing,
        "source_scenario_run_id": metadata.get("source_scenario_run_id"),
        "runtime_restart_required": metadata["status"] == "ready" and installed_validation["ok"],
    }