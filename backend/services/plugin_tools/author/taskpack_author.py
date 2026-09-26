"""Author new IAI task packs from a graph-canvas spec.

This module is intentionally independent of the Copilot agent runtime. It takes a
declarative task-pack spec (produced by the "Add task pack" graph canvas in the
chat UI) and compiles it into:

- a Layer 2 planner registry entry + ``SKILL.md``
- zero or more new Layer 3 widget registry entries + ``SKILL.md`` files
- updates to the compatible_planners list of reused widgets
- a Layer 1 routing-table row (returned for review, not auto-inserted)

``preview`` computes everything in memory and writes nothing. ``generate``
validates, then writes the new skill files and appends the registry entries.

Only the standard library is used so the module can be unit-tested without the
agent SDK installed.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from backend.services.inflak_plugins import plugin_dir

PLUGIN_DIR = plugin_dir("inflak-main")
SKILLS_DIR = PLUGIN_DIR / "skills"
REGISTRY_DIR = PLUGIN_DIR / "registry"
PLANNERS_JSON = REGISTRY_DIR / "planners.json"
WIDGETS_JSON = REGISTRY_DIR / "widgets.json"
L2_CONTRACT_PATH = PLUGIN_DIR / "contract" / "l2-skill-contract.md"
L3_CONTRACT_PATH = PLUGIN_DIR / "contract" / "l3-skill-contract.md"

# The IAI model is fixed: six node roles and a whitelist of directed edges.
IAI_NODES = ["H", "T", "I", "Aug", "A", "G"]
IAI_NODE_LABELS = {
    "H": "Human",
    "T": "Text Prompt",
    "I": "Interaction",
    "Aug": "Augmented Instruction",
    "A": "Artifact",
    "G": "Generative AI",
}
IAI_EDGES = {
    "H→T", "H→I", "I→T", "I→A", "I→Aug", "T→Aug", "T→G",
    "A→Aug", "A→G", "Aug→G", "Aug→A", "G→A", "G→I",
}
# Edges that may carry an interaction gap must land on a state node the user
# updates through interaction.
GAP_TARGET_NODES = {"Aug", "A"}

SLUG_RE = re.compile(r"^[a-z][a-z0-9-]{1,48}[a-z0-9]$")
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
RENDERER_TOOLS = frozenset({"render_html_widget", "render_interactive_widget"})

# Authoring-time shared text, expanded into each generated skill. Never a
# runtime schema dependency; L3 and L4 must remain independently readable.
LOCAL_WIDGET_HANDOFF = """- Identity: nonempty strings `selected_widget_id` (exact L2 selection), `widget_id` (instance identity), `widget_type` and `surface` (exact registry values), `planner_id` (owning L2), `purpose` (contextual), and unchanged `interaction_goal`.
- `iai`: copy L2's `chain_id`, `gap_type`, and binding `reason`, `maps_to_edge`, `source_nodes`, `target_node` unchanged; require a named chain and meaningful reason, edge source in `source_nodes`, and destination equal to `target_node` and allowed `state_update_target`. Include a deterministic `merge_strategy` for L1 and `next_planner_action: "re-enter Layer 1"`.
- `display`: grounded task values, source references, current values, and unresolved status; no invented evidence, defaults, uploads, previews, or outcomes.
- `controls`: array of records with `id`, `kind`, `label`, `purpose`, `required`, `return_keys`, `constraints`; IDs are unique/nonempty, kinds supported, labels/purposes nonempty, `required` boolean, and `return_keys` a nonempty list of declared return keys. State applicable limits, types, and source/edit rules in `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`, a nonempty `content` array of records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`); every source resolves. Include `interaction` with nonempty `actions`/`feedback` lists and `submission` (nonempty `label`, nonempty `preconditions`, `return_mapping`), plus nonempty semantic `appearance` and a nonempty `signature_features` list describing relevant behavior, not implementation or invented steps.
- `expected_return`: deterministic object with exactly L2's keys and types; `presentation.profile.interaction.submission.return_mapping` has exactly the same keys, each specifying its actual source and serialization. Preserve declared optional/empty semantics; derived returns need mappings, not artificial controls.
- `widget_requirements`: four nonempty string arrays, `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`; state minimal meaningful obligations consistent with the profile, not additional interaction gates.
- `safety`: `allow_html: false`, `allow_script: false`. Optional `runtime` declares only available approved capabilities and version-pinned libraries; optional `reference_assets` are plugin-relative design-time references and extracted principles only, never runtime assets."""


def _skill_structure_issues(text: str, expected_name: str) -> list[str]:
    """Check a whole document, including legacy frontmatter glued to its tail."""
    errors = []
    if not text.startswith("---\n") or len(re.findall(r"^---\s*$", text, re.MULTILINE)) != 2:
        errors.append("requires exactly one frontmatter block")
    if re.findall(r"^name:\s*(\S+)\s*$", text, re.MULTILINE) != [expected_name]:
        errors.append("requires one matching frontmatter name")
    if len(re.findall(r"^description:\s*\S.*$", text, re.MULTILINE)) != 1:
        errors.append("requires one frontmatter description")
    if len(re.findall(r"^#\s+\S.*$", text, re.MULTILINE)) != 1:
        errors.append("requires one H1")
    headings = SECTION_RE.findall(text)
    if len(headings) != len(set(headings)):
        errors.append("duplicate semantic sections")
    return errors


def _local_widget_contract_issues(text: str, section: str = "Output and Handoff") -> list[str]:
    """Validate documentation obligations, not an invented runtime payload."""
    match = re.search(r"^## " + re.escape(section) + r"\n(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    body = match.group(1) if match else ""
    obligations = {
        "Identity": ("`selected_widget_id`", "`widget_id`", "`widget_type`", "`surface`", "`planner_id`", "`purpose`", "`interaction_goal`", "nonempty"),
        "`iai`": ("`chain_id`", "`gap_type`", "`reason`", "`maps_to_edge`", "`source_nodes`", "`target_node`", "`state_update_target`", "`merge_strategy`", 'next_planner_action: "re-enter Layer 1"', "unchanged", "destination"),
        "`display`": ("grounded", "source references", "unresolved"),
        "`controls`": ("`id`", "`kind`", "`label`", "`purpose`", "`required`", "`return_keys`", "`constraints`", "array of records", "supported", "unique", "boolean", "nonempty"),
        "`presentation.profile`": ("archetype", "summary", "content", "array", 'source: "display.<path>"', "role: primary|context|status", "purpose", "resolves", "interaction", "actions", "feedback", "submission", "label", "preconditions", "return_mapping", "appearance", "signature_features", "nonempty"),
        "`expected_return`": ("exactly L2's keys and types", "return_mapping", "exactly the same keys", "source", "serialization", "optional/empty", "derived"),
        "`widget_requirements`": ("four nonempty string arrays", "visible_information", "required_controls", "required_behavior", "submission_requirements"),
        "`safety`": ("allow_html: false", "allow_script: false", "runtime", "approved", "version-pinned", "reference_assets", "plugin-relative", "never runtime assets"),
    }
    errors = []
    if len(re.findall(r"^- ", body, re.MULTILINE)) != 8:
        errors.append(f"{section}: requires exactly eight local handoff obligations")
    for label, tokens in obligations.items():
        bullets = re.findall(r"^- " + re.escape(label) + r": (.*)$", body, re.MULTILINE)
        value = bullets[0] if len(bullets) == 1 else ""
        missing = [token for token in tokens if token not in value]
        if missing:
            errors.append(f"{section}: incomplete {label} obligation: {', '.join(missing)}")
    return errors


def _markdown_cell(value: Any) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|").strip()


def _return_schema_rows(shape: dict[str, Any], *, examples: bool = False) -> str:
    """Document each declared key; examples are shape hints, never live defaults."""
    rows = []
    for key, value in shape.items():
        if examples:
            kind = ("null" if value is None else "boolean" if isinstance(value, bool)
                    else "integer" if isinstance(value, int) else "number" if isinstance(value, float)
                    else "object" if isinstance(value, dict) else "array" if isinstance(value, list) else "string")
            declaration = f"{kind}; shape hint {json.dumps(value, ensure_ascii=False)} (not a runtime default)"
        else:
            declaration = json.dumps(value, ensure_ascii=False)
        rows.append(f"| `{_markdown_cell(key)}` | {_markdown_cell(declaration)} | Specify actual source and serialization; preserve declared optional/empty semantics and validate before submission. |")
    return "\n".join(rows)


class TaskPackError(ValueError):
    """Raised when a spec cannot be compiled."""


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def slugify(value: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def _edge_target(edge: str) -> str:
    return edge.split("→", 1)[1] if "→" in edge else ""


def _edge_source(edge: str) -> str:
    return edge.split("→", 1)[0] if "→" in edge else ""


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_required_sections(contract_text: str) -> list[str]:
    block_match = re.search(r"## Required Sections\n(.*?)(?:\n##\s+|\Z)", contract_text, re.DOTALL)
    if not block_match:
        return []
    required: list[str] = []
    for raw_line in block_match.group(1).splitlines():
        line = raw_line.strip()
        if not line.startswith("- "):
            continue
        label = line[2:].strip()
        if label.startswith("`") and label.endswith("`"):
            label = label[1:-1]
        if label:
            required.append(label)
    return required


def _load_contract_requirements() -> tuple[dict[str, list[str]], list[str]]:
    requirements: dict[str, list[str]] = {"l2": [], "l3": []}
    errors: list[str] = []
    mapping = {
        "l2": L2_CONTRACT_PATH,
        "l3": L3_CONTRACT_PATH,
    }
    for layer, path in mapping.items():
        if not path.exists():
            errors.append(f"missing contract file: {path.relative_to(PLUGIN_DIR)}")
            continue
        required = _extract_required_sections(path.read_text(encoding="utf-8"))
        if not required:
            errors.append(f"contract has no Required Sections list: {path.relative_to(PLUGIN_DIR)}")
            continue
        requirements[layer] = required
    return requirements, errors


def _contract_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _generation_request(*, layer: str, contract_path: Path, input_data: dict[str, Any]) -> dict[str, Any]:
    contract = _contract_text(contract_path)
    input_json = json.dumps(input_data, indent=2, ensure_ascii=False)
    return {
        "layer": layer,
        "authoring_guide": str(contract_path.relative_to(PLUGIN_DIR)),
        # Legacy response key; this path is documentation, not a callable skill.
        "contract_skill": str(contract_path.relative_to(PLUGIN_DIR)),
        "contract": contract,
        "input": input_data,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Generate one IAI skill that strictly follows the supplied skill contract. "
                    "The layers are L1 Router, L2 Planner, L3 Designer, and L4 Renderer. "
                    "The four pathways are Interaction Pathway, Execution Pathway, Host Agent Return, and Completion. "
                    "Interaction Pathway sends only eligible selected-widget gaps through L1 -> L2 -> L3 -> L4 -> L1. "
                    "Execution Pathway is user/return -> L1 -> L2 plan -> execute/realize -> L1: "
                    "L2 directly invokes the selected executor or active main model without L3 or L4. "
                    "Gap routing failures including no_eligible_widget return directly from L2 to L1; "
                    "L3 only designs interactions and returns every error directly to L1 without L4 entry. "
                    "Host Agent Return hands an out-of-scope request back to the host agent; only L1 decides Completion. "
                    "Emit exactly one frontmatter/name/H1 and never concatenate a previous document. "
                    "L2 preserves six node bindings and named ordered chains, derives evidence-grounded per-edge gaps "
                    "before selection, and uses one four-column Diagnosis table with a final instruction_ready row. "
                    "L3 uses the six required semantic sections, a compact design table and exact per-widget schema return requirements, "
                    "not a large mock JSON payload. Include all eight complete local handoff obligations: "
                    "chain/reason provenance, labeled typed controls, resolvable content records, actions/feedback/submission, "
                    "exact source/serialization mappings, four nonempty widget_requirements arrays and safety. "
                    "Neither L3 nor L4 may defer missing semantics to an external runtime document or invent domain facts. "
                    "Return only the complete SKILL.md content with no surrounding commentary or fences.\n\n"
                    + contract
                ),
            },
            {
                "role": "user",
                "content": "Generate the specific skill from this validated JSON input:\n\n" + input_json,
            },
        ],
    }


def build_generation_requests(spec: dict[str, Any]) -> dict[str, Any]:
    slug = str(spec["pack_slug"])
    existing_widgets = {
        str(widget.get("id")): widget
        for widget in _load_json(WIDGETS_JSON).get("widgets", [])
    }
    widget_registry_candidates: list[dict[str, Any]] = []
    for gap in _spec_gaps(spec):
        widget = gap.get("widget") or {}
        if widget.get("new"):
            entry = build_widget_entry(widget["new"], gap, slug)
        else:
            entry = dict(existing_widgets.get(str(widget.get("reuse") or "")) or {})
        if entry:
            compatible_planners = list(entry.get("compatible_planners") or [])
            if slug not in compatible_planners:
                compatible_planners.append(slug)
            entry["compatible_planners"] = compatible_planners
            entry["runtime_available"] = True
            widget_registry_candidates.append(entry)
    l2_input = {**spec, "widget_registry_candidates": widget_registry_candidates}
    l2_request = _generation_request(layer="l2", contract_path=L2_CONTRACT_PATH, input_data=l2_input)
    l3_requests: dict[str, dict[str, Any]] = {}
    for gap in _spec_gaps(spec):
        new_widget = (gap.get("widget") or {}).get("new")
        if not new_widget:
            continue
        widget_slug = str(new_widget["slug"])
        l3_requests[widget_slug] = _generation_request(
            layer="l3",
            contract_path=L3_CONTRACT_PATH,
            input_data={
                "planner_slug": slug,
                "return_to_l1": "l1-router",
                "gap": gap,
                "selected_widget_id": widget_slug,
                "selected_registry_entry": build_widget_entry(new_widget, gap, slug),
                "realization_definition": {
                    "title": str(new_widget.get("title") or _title_from_slug(widget_slug)),
                    "purpose": str(new_widget.get("purpose") or f"Realize the {gap.get('name')} gap."),
                    "display_fields": list(new_widget.get("display_fields") or ["title", "summary"]),
                    "return_shape": dict(new_widget.get("return_shape") or {}),
                },
                "runtime_context": {
                    "available_capabilities": list(new_widget.get("runtime_capabilities") or []),
                    "available_external_libraries": list(new_widget.get("external_libraries") or []),
                },
            },
        )
    return {"l2": l2_request, "l3": l3_requests}


def _extract_sections(markdown: str) -> set[str]:
    return {match.group(1).strip() for match in SECTION_RE.finditer(markdown)}


def _validate_contract_conformance(compiled: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    requirements, load_errors = _load_contract_requirements()
    if load_errors:
        return load_errors, {"requirements": requirements, "missing": {"l2": [], "l3": {}}}

    missing_l2: list[str] = []
    l2_sections = _extract_sections(compiled["l2_skill"])
    for required in requirements["l2"]:
        if required not in l2_sections:
            missing_l2.append(required)

    missing_l3: dict[str, list[str]] = {}
    for widget_slug, skill_text in compiled["l3_skills"].items():
        sections = _extract_sections(skill_text)
        missing = [required for required in requirements["l3"] if required not in sections]
        if missing:
            missing_l3[widget_slug] = missing

    errors: list[str] = []
    if RENDERER_TOOLS.intersection(compiled["planner_entry"].get("allowed_tools") or []):
        errors.append("L2 planner allowed_tools cannot include a renderer; rendering belongs to L4")
    for error in _skill_structure_issues(compiled["l2_skill"], f"l2-{compiled['pack_slug']}"):
        errors.append(f"L2 skill: {error}")
    if missing_l2:
        errors.append("L2 skill is missing required contract sections: " + ", ".join(missing_l2))
    for required_text in (
        "# L2 Planner",
        "Layer 2 directly invokes the selected executor or active main model",
        "Only eligible gaps enter Layer 3",
        "Gap routing failures including `no_eligible_widget` return directly to Layer 1",
        "Only L1 Router owns canonical workflow state and decides Completion or Host Agent Return",
    ):
        if required_text not in compiled["l2_skill"]:
            errors.append(f"L2 skill is missing pathway boundary: {required_text}")
    for widget_slug, missing in missing_l3.items():
        errors.append(
            f"L3 skill '{widget_slug}' is missing required contract sections: " + ", ".join(missing)
        )

    selectable_widget_ids = {
        str(entry.get("id")) for entry in compiled.get("new_widget_entries", [])
    }
    selectable_widget_ids.update(
        str(update.get("id")) for update in compiled.get("reuse_widget_updates", [])
    )
    for raw_json in re.findall(r"```json\s*\n(.*?)\n```", compiled["l2_skill"], re.DOTALL):
        try:
            handoff = json.loads(raw_json)
        except json.JSONDecodeError:
            continue
        if handoff.get("handoff_type") != "planner_handoff":
            continue
        for gap in handoff.get("gap_requests") or []:
            selected_widget_id = str(gap.get("selected_widget_id") or "")
            if selected_widget_id not in selectable_widget_ids:
                errors.append(
                    "L2 handoff selects an unknown widget registry id: "
                    + (selected_widget_id or "<missing>")
                )
    for widget_slug, skill_text in compiled["l3_skills"].items():
        errors.extend(f"L3 skill '{widget_slug}': {error}" for error in
                      _skill_structure_issues(skill_text, f"l3-{widget_slug}"))
        errors.extend(f"L3 skill '{widget_slug}': {error}" for error in _local_widget_contract_issues(skill_text))
        if "selected_widget_id" not in skill_text or widget_slug not in skill_text:
            errors.append(f"L3 skill '{widget_slug}' is missing its selected-widget trace")
        for required_text in (
            "# L3 Designer",
            "Layer 3 only designs interactions",
            "Every Layer 3 error returns directly to Layer 1 without Layer 4 entry",
        ):
            if required_text not in skill_text:
                errors.append(f"L3 skill '{widget_slug}' is missing pathway boundary: {required_text}")
        for field in ("handoff_type: selected_widget_invalid", "validation_errors", "return_to: l1-router"):
            if field not in skill_text:
                errors.append(f"L3 skill '{widget_slug}' is missing failure obligation: {field}")
        entry = next((item for item in compiled.get("new_widget_entries", []) if item.get("id") == widget_slug), {})
        for key in entry.get("expected_return_types", []):
            if f"| `{key}` |" not in skill_text:
                errors.append(f"L3 skill '{widget_slug}' is missing schema return requirement: {key}")
        if re.search(r"(?im)^#+ .*executor|\b(?:Layer 3|L3) (?:directly invokes|executes|calls)\b", skill_text):
            errors.append(f"L3 skill '{widget_slug}' cannot be a task executor")

    return errors, {"requirements": requirements, "missing": {"l2": missing_l2, "l3": missing_l3}}


def _existing_ids(registry: dict[str, Any], key: str) -> set[str]:
    return {str(item.get("id")) for item in registry.get(key, [])}


def _normalised_chains(spec: dict[str, Any]) -> list[dict[str, Any]]:
    chains: list[dict[str, Any]] = []
    source_chains = spec.get("chains") or []
    if not source_chains and spec.get("edges"):
        # Preserve the legacy graph API; give its supplied edge order a stable
        # identity rather than requiring clients to add new fields.
        source_chains = [{"id": "legacy-chain", "name": "Declared task flow",
                          "function": str(spec.get("description") or "Perform the declared task flow."),
                          "edges": [{"type": edge.get("type"), "explanation": edge.get("explanation") or "Preserve the declared information transfer."}
                                    for edge in spec["edges"]]}]
    for index, chain in enumerate(source_chains):
        chain_id = str(chain.get("id") or f"chain-{index + 1}")
        edges: list[dict[str, Any]] = []
        for edge in chain.get("edges") or []:
            edges.append(
                {
                    "type": str(edge.get("type") or ""),
                    "explanation": str(edge.get("explanation") or ""),
                }
            )
        chains.append(
            {
                "id": chain_id,
                "name": str(chain.get("name") or chain_id),
                "function": str(chain.get("function") or ""),
                "edges": edges,
            }
        )
    return chains


def _spec_edges(spec: dict[str, Any]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    edges: list[dict[str, Any]] = []
    for edge in spec.get("edges") or []:
        etype = str(edge.get("type") or "")
        if etype and etype not in seen:
            edges.append({"type": etype})
            seen.add(etype)
    for chain in _normalised_chains(spec):
        for edge in chain["edges"]:
            etype = str(edge.get("type") or "")
            if etype and etype not in seen:
                edges.append({"type": etype})
                seen.add(etype)
    return edges


def _spec_gaps(spec: dict[str, Any]) -> list[dict[str, Any]]:
    return list(spec.get("gaps") or [])


def _derive_mode(spec: dict[str, Any]) -> str:
    """Pilot vs. coach is derived, not declared: a pack that starts from an
    existing artifact (a chain whose first edge originates at ``A``) is a coach;
    otherwise it is a pilot. An explicit ``mode`` in the spec is still honored."""
    explicit = str(spec.get("mode") or "").strip().lower()
    if explicit in {"pilot", "coach"}:
        return explicit
    for chain in _normalised_chains(spec):
        edges = chain.get("edges") or []
        if edges and _edge_source(str(edges[0].get("type"))) == "A":
            return "coach"
    return "pilot"


def _selected_widget_id(gap: dict[str, Any]) -> str:
    widget = gap.get("widget") or {}
    new_widget = widget.get("new") or {}
    return str(new_widget.get("slug") or widget.get("reuse") or "")


def _gap_chain_id(spec: dict[str, Any], gap: dict[str, Any]) -> str:
    if gap.get("chain_id"):
        return str(gap["chain_id"])
    return next((chain["id"] for chain in _normalised_chains(spec)
                 if str(gap.get("edge")) in [edge["type"] for edge in chain["edges"]]), "")


def _gap_expected_return(gap: dict[str, Any]) -> dict[str, Any] | str:
    declared = gap.get("expected_return")
    if declared:
        return declared
    new_widget = (gap.get("widget") or {}).get("new") or {}
    if new_widget.get("return_shape"):
        return dict(new_widget["return_shape"])
    selected = next((entry for entry in _load_json(WIDGETS_JSON).get("widgets", [])
                     if str(entry.get("id")) == _selected_widget_id(gap)), {})
    if selected.get("return_mode", "schema") == "schema":
        return {key: "Preserve the selected skill's declared type and optional/empty semantics"
                for key in selected.get("expected_return_types", [])}
    return f"Preserve the selected skill's declared agent-interpreted return for {_edge_target(str(gap.get('edge')))}"


# --------------------------------------------------------------------------- #
# Validation
# --------------------------------------------------------------------------- #
def validate_spec(spec: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Return (errors, warnings). Errors block generation; warnings do not."""
    errors: list[str] = []
    warnings: list[str] = []

    pack_slug = str(spec.get("pack_slug") or "")
    if not SLUG_RE.match(pack_slug):
        errors.append(
            f"pack_slug '{pack_slug}' is invalid; use lowercase letters, digits and hyphens "
            "(e.g. 'deck-pilot')."
        )
    if not spec.get("task_family"):
        errors.append("task_family is required (e.g. 'slides').")
    if RENDERER_TOOLS.intersection(spec.get("tools") or []):
        errors.append("L2 tools cannot include a renderer; rendering belongs to L4.")

    mode = _derive_mode(spec)

    bindings = spec.get("node_bindings") or {}
    for node in IAI_NODES:
        if not str(bindings.get(node) or "").strip():
            warnings.append(f"node_bindings.{node} is empty; the {IAI_NODE_LABELS[node]} role will be generic.")

    chains = _normalised_chains(spec)
    chain_ids = {chain["id"] for chain in chains}
    chain_edge_types = {chain["id"]: {edge["type"] for edge in chain["edges"]} for chain in chains}
    for c_index, chain in enumerate(chains):
        where = f"chain #{c_index + 1} ('{chain['name']}')"
        if not chain["function"].strip():
            errors.append(f"{where}: function is required; describe what this chain implements.")
        if not chain["edges"]:
            errors.append(f"{where}: add at least one edge.")
        for e_index, edge in enumerate(chain["edges"]):
            etype = str(edge.get("type") or "")
            if etype not in IAI_EDGES:
                errors.append(f"{where}, edge #{e_index + 1}: '{etype}' is not a valid IAI edge.")
            if not str(edge.get("explanation") or "").strip():
                errors.append(f"{where}, edge '{etype}': explanation is required.")

    edges = _spec_edges(spec)
    active_edges = {str(e.get("type")) for e in edges}
    for e in edges:
        etype = str(e.get("type"))
        if etype not in IAI_EDGES:
            errors.append(f"edge '{etype}' is not a valid IAI edge.")

    # Exit edge invariant.
    if not ({"Aug→G", "T→G"} & active_edges):
        errors.append("The task never reaches G: add an exit edge 'Aug→G' (or 'T→G').")

    # Mode invariants.
    if mode == "pilot" and "G→A" not in active_edges:
        warnings.append("pilot packs usually create an artifact via 'G→A'; consider adding it.")
    if mode == "coach" and not ({"A→Aug", "I→A", "A→G", "Aug→A"} & active_edges):
        warnings.append("coach packs operate on an existing artifact; add 'A→Aug' or 'I→A'.")

    gaps = _spec_gaps(spec)
    if not gaps:
        errors.append("Add at least one gap (a mediated edge that needs a widget).")

    seen_gap_names: set[str] = set()
    has_acceptance = False
    for index, gap in enumerate(gaps):
        name = str(gap.get("name") or "").strip()
        edge = str(gap.get("edge") or "")
        where = f"gap #{index + 1}" + (f" ('{name}')" if name else "")
        if not name:
            errors.append(f"{where}: name is required.")
        elif name in seen_gap_names:
            errors.append(f"{where}: duplicate gap name '{name}'.")
        else:
            seen_gap_names.add(name)
        if edge not in IAI_EDGES:
            errors.append(f"{where}: edge '{edge}' is not a valid IAI edge.")
        elif _edge_target(edge) not in GAP_TARGET_NODES:
            errors.append(
                f"{where}: a gap edge must end at 'Aug' or 'A' (got '{edge}'); "
                "you cannot open a gap on a direct-to-model edge."
            )
        chain_id = str(gap.get("chain_id") or "")
        if chain_id:
            if chain_id not in chain_ids:
                errors.append(f"{where}: chain_id '{chain_id}' does not match any declared chain.")
            elif edge not in chain_edge_types.get(chain_id, set()):
                errors.append(f"{where}: edge '{edge}' is not part of chain '{chain_id}'.")
        if _edge_target(edge) == "A":
            has_acceptance = True
        widget = gap.get("widget") or {}
        if not (widget.get("reuse") or widget.get("new")):
            errors.append(f"{where}: choose a widget to realize it (reuse an existing one or define a new one).")
        new_widget = widget.get("new")
        if new_widget:
            w_slug = str(new_widget.get("slug") or "")
            if not SLUG_RE.match(w_slug):
                errors.append(f"{where}: new widget slug '{w_slug}' is invalid.")
            if not str(new_widget.get("widget_type") or "").strip():
                errors.append(f"{where}: new widget needs a widget_type.")
            if not isinstance(new_widget.get("return_shape"), dict) or not new_widget["return_shape"]:
                errors.append(f"{where}: new widget needs a non-empty return_shape.")
            for field in ("runtime_capabilities", "external_libraries"):
                value = new_widget.get(field)
                if value is not None and (
                    not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value)
                ):
                    errors.append(f"{where}: new widget {field} must be a list of non-empty strings.")

    if mode == "coach" and not has_acceptance:
        warnings.append(
            "coach packs that materially change the artifact should include an acceptance gap "
            "on an 'I→A' edge so the user confirms before it is applied."
        )

    return errors, warnings


# --------------------------------------------------------------------------- #
# Registry entry builders
# --------------------------------------------------------------------------- #
def build_planner_entry(spec: dict[str, Any]) -> dict[str, Any]:
    slug = spec["pack_slug"]
    mode = _derive_mode(spec)
    edges = sorted({str(e.get("type")) for e in _spec_edges(spec)}, key=_edge_sort_key)
    gap_categories = [str(g.get("name")) for g in _spec_gaps(spec)]
    allowed_tools = [tool for tool in spec.get("tools") or [] if tool not in RENDERER_TOOLS]
    required_state = ["user_text"] if mode == "pilot" else ["user_text", "artifact"]
    return {
        "id": slug,
        "task_family": str(spec.get("task_family")),
        "skill": f"l2-{slug}",
        "layer": "layer-2",
        "canonical_skill_path": f"skills/l2-{slug}/SKILL.md",
        "priority": int(spec.get("priority") or (70 if mode == "pilot" else 80)),
        "trigger_summary": str(spec.get("description") or f"Task pack '{slug}'."),
        "trigger_keywords": list(spec.get("trigger_keywords") or []),
        "domain_scope": list(spec.get("domain_scope") or [str(spec.get("task_family"))]),
        "required_state": required_state,
        "optional_state": ["prior_returns", "memory"],
        "iai_edges": edges,
        "gap_categories": gap_categories,
        "allowed_tools": allowed_tools,
        "loop_return_to": "l1-router",
        "expected_outputs": list(spec.get("expected_outputs") or []),
    }


def _edge_sort_key(edge: str) -> tuple[int, int]:
    order = {n: i for i, n in enumerate(IAI_NODES)}
    return (order.get(_edge_source(edge), 99), order.get(_edge_target(edge), 99))


def build_widget_entry(new_widget: dict[str, Any], gap: dict[str, Any], planner_slug: str) -> dict[str, Any]:
    w_slug = new_widget["slug"]
    edge = str(gap.get("edge"))
    return {
        "id": w_slug,
        "skill": f"l3-{w_slug}",
        "layer": "layer-3",
        "canonical_skill_path": f"skills/l3-{w_slug}/SKILL.md",
        "widget_type": str(new_widget.get("widget_type")),
        "surface": "conversation_widget",
        "interaction_modality": str(new_widget.get("modality") or "custom"),
        "supported_artifact_types": list(new_widget.get("supported_artifact_types") or ["any"]),
        "interaction_goals": [str(gap.get("goal") or "collect_input")],
        "iai_edges": [edge],
        "gap_categories": [str(gap.get("name"))],
        "state_update_targets": [_edge_target(edge)],
        "expected_return_types": list((new_widget.get("return_shape") or {}).keys()),
        "return_mode": "schema",
        "return_field_policy": "fixed",
        "widget_capabilities": [],
        "runtime_capabilities": list(new_widget.get("runtime_capabilities") or []),
        "external_libraries": list(new_widget.get("external_libraries") or []),
        "primary_renderer": "render_html_widget",
        "compatible_planners": [planner_slug],
    }


# --------------------------------------------------------------------------- #
# Skill markdown renderers
# --------------------------------------------------------------------------- #
def _title_from_slug(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.split("-"))


def render_l2_skill(spec: dict[str, Any]) -> str:
    slug = spec["pack_slug"]
    title = str(spec.get("title") or _title_from_slug(slug))
    mode = _derive_mode(spec)
    bindings = spec.get("node_bindings") or {}
    gaps = _spec_gaps(spec)
    chains = _normalised_chains(spec)
    tools = [tool for tool in spec.get("tools") or [] if tool not in RENDERER_TOOLS]
    guardrails = list(spec.get("guardrails") or [])
    verb = "creating new" if mode == "pilot" else "operating on existing"

    lines: list[str] = []
    lines.append("---")
    lines.append(f"name: l2-{slug}")
    desc = str(spec.get("description") or f"plan the {title} task").replace('"', "'")
    lines.append(f'description: "Use when: Layer 1 routed to {slug} to {desc}"')
    lines.append("---")
    lines.append("")
    lines.append(f"# L2 Planner — {title}")
    lines.append("")
    lines.append("## Workflow End Authority")
    lines.append("")
    lines.append(
        "Only L1 Router owns canonical workflow state and decides Completion or Host Agent Return. "
        "L2 Planner returns every result or failure directly to Layer 1 and never presents local completion as final."
    )
    lines.append("")
    lines.append("## Layer & Role")
    lines.append("")
    lines.append(
        f"Second layer. Plans the interaction for {verb} artifacts in the "
        f"`{spec.get('task_family')}` task family. Diagnoses the open IAI-graph gaps, does its own "
        "task reasoning, selects one eligible widget registry entry for an open gap, and emits a "
        "`planner_handoff`. For Execution Pathway, Layer 2 directly invokes the selected executor or active main model "
        "without Layer 3 or Layer 4. It does not author the selected widget contract or render UI."
    )
    lines.append("")
    lines.append("## IAI Domain Binding")
    lines.append("")
    lines.append(f"| IAI node | {title} binding |")
    lines.append("| --- | --- |")
    for node in IAI_NODES:
        binding = str(bindings.get(node) or IAI_NODE_LABELS[node])
        lines.append(f"| `{node}` | {binding} |")
    lines.append("")
    lines.append("## Interaction Chains")
    lines.append("")
    if chains:
        lines.append(
            "Each chain describes one task-level function as a path through the IAI graph. "
            "Use the edge explanations to preserve why each transition exists."
        )
        lines.append("")
        lines.append("| chain | function | edge sequence |")
        lines.append("| --- | --- | --- |")
        for chain in chains:
            sequence = ", ".join(edge["type"] for edge in chain["edges"])
            lines.append(f"| `{chain['id']}` — {_markdown_cell(chain['name'])} | {_markdown_cell(chain['function'])} | `{sequence}` |")
        lines.append("")
        for chain in chains:
            lines.append(f"**{chain['name']} edge explanations**")
            lines.append("")
            for edge in chain["edges"]:
                lines.append(f"- `{edge['type']}`: {edge['explanation']}")
            lines.append("")
    else:
        lines.append("No named interaction chains are declared; use the task's atomic IAI edges directly.")
        lines.append("")
    lines.append("## Diagnosis")
    lines.append("")
    lines.append(
        "Read the timing axis before/after a GenAI invocation and resources axis prompt-only/artifact-grounded. "
        "Derive the material source-to-target deficit from intent, current evidence, prior returns and scoped delegation "
        "before choosing a widget. Assess every registered category as open, resolved or not applicable with evidence; "
        "silence is not delegation. Preserve resolved choices unless relevant dependencies change. "
        "Select the next applicable gap by dependencies; a tool failure is not a semantic gap."
    )
    lines.append("")
    lines.append("| gap_type | Condition | Edge | Interaction goal |")
    lines.append("| --- | --- | --- | --- |")
    for gap in gaps:
        name = str(gap.get("name"))
        edge = str(gap.get("edge"))
        goal = str(gap.get("goal") or "collect the missing input")
        problem = str(gap.get("problem") or f"The {_edge_target(edge)} state is missing an input.")
        cause = str(gap.get("cause") or "The prompt leaves this open.")
        lines.append(f"| `{name}` | {_markdown_cell(problem)} {_markdown_cell(cause)} | `{edge}` | `{goal}` |")
    execution_edges = [edge["type"] for edge in _spec_edges(spec) if edge["type"] in {"T→G", "Aug→G", "G→A"}]
    lines.append(
        "| `instruction_ready` | All applicable gaps have evidence-backed closure, or only bounded prerequisite "
        "preparation is justified while user choices remain open; preparation never authorizes final execution. | "
        + " then ".join(f"`{edge}`" for edge in execution_edges)
        + " | Directly invoke the selected executor and return actual results to L1. |"
    )
    lines.append("")
    lines.append("Chain association: " + "; ".join(f"`{gap['name']}` → `{_gap_chain_id(spec, gap)}`" for gap in gaps) + ".")
    lines.append("")
    lines.append("## Gap Handoff")
    lines.append("")
    lines.append(
        "Emit the diagnosed gap as a semantic request. Describe the gap and the interaction goal; do "
        "not duplicate registry-derived widget metadata in the handoff."
    )
    lines.append("")
    first = gaps[0] if gaps else {"name": "example_gap", "goal": "collect_input", "edge": "I→Aug"}
    first_edge = str(first.get("edge") or "I→Aug")
    example = {
        "chain_id": _gap_chain_id(spec, first),
        "gap_type": str(first.get("name")),
        "interaction_goal": str(first.get("goal") or "collect_input"),
        "iai_binding": {
            "source_nodes": [_edge_source(first_edge)],
            "maps_to_edge": first_edge,
            "target_node": _edge_target(first_edge),
            "reason": f"On {first_edge}, {first.get('problem') or 'required target information is missing'} {first.get('cause') or 'The current evidence does not settle it.'} Pending {_edge_source(first_edge)} input has not supplied {_edge_target(first_edge)}; guessing would invent a user decision. The declared return supplies that missing transfer.",
        },
        "expected_return": _gap_expected_return(first),
        "selected_widget_id": _selected_widget_id(first),
    }
    lines.append(
        "The single widget-mode example is in Output below. At runtime use actual evidence: preserve `chain_id`, "
        "`iai_binding.reason`, source/edge/target, goal and exact required return keys/types. The source belongs "
        "to `source_nodes`; the destination equals `target_node` and L3's `state_update_target`. "
        "Explain source evidence, missing transfer/target, why guessing is unjustified and how the return closes it."
    )
    lines.append("")
    lines.append("## Inputs (from core_handoff and widget registry)")
    lines.append("")
    lines.append(f"- `selected_planner`: `{slug}`.")
    state = "`user_text`, `artifact`, `prior_returns`" if mode == "coach" else "`user_text`, `prior_returns`"
    lines.append(f"- `state_snapshot`: {state}.")
    lines.append("- The routing projection from `registry/widgets.json` and current runtime availability.")
    lines.append("")
    lines.append("## Widget Registry Routing")
    lines.append("")
    lines.append(
        "Filter the widget registry by planner compatibility, exact gap, interaction goal, IAI edge, "
        "return coverage, artifact support, and runtime availability. Select one eligible registry "
        "entry and emit only its `id` as `selected_widget_id`. Only eligible gaps enter Layer 3 for interaction design. "
        "Gap routing failures including `no_eligible_widget` return directly to Layer 1 without Layer 3 entry; "
        "preserve `planner_id`, `diagnosed_gap`, `rejected_candidates`, and `return_to`. "
        "Rank eligible entries by semantic coverage, artifact specificity, return coverage, runtime fitness, "
        "stable registry order and finally registry `id`. "
        "Layer 3 validates and designs the selected entry without rerouting it."
    )
    lines.append("")
    lines.append("## Procedure")
    lines.append("")
    lines.append("1. Inspect the core handoff and state snapshot.")
    lines.append("2. Assess every category, select the next material gap by dependencies and its named chain; only evidence-backed closure or bounded preparation permits instruction-ready work.")
    lines.append(
        "3. Emit a `gap_request` with its `gap_type`, `interaction_goal`, "
        "`iai_binding`, `expected_return`, and the selected registry `selected_widget_id`."
    )
    lines.append("4. When instruction-ready, plan the exact work and directly invoke the selected executor or active main model; preserve its parameters and purpose.")
    if tools:
        tool_list = ", ".join(f"`{t}`" for t in tools)
        lines.append(f"5. When the instruction is ready, you may call {tool_list} to produce the result.")
    return_step = 6 if tools else 5
    lines.append(
        f"{return_step}. Every interaction or execution result or failure returns directly to Layer 1, "
        "which reconstructs state and chooses the next pathway."
    )
    lines.append("")
    lines.append("## Output (planner_handoff)")
    lines.append("")
    gap = gaps[0]
    gap_request = {
        **example,
        "order": 1,
        "depends_on_previous": False,
    }
    if gap.get("chain_id"):
        gap_request["chain_id"] = str(gap.get("chain_id"))
    handoff = {
        "handoff_type": "planner_handoff",
        "planner_id": slug,
        "planner_decision": "gap_open",
        "gap_requests": [gap_request],
        "return_to": "l1-router",
    }
    lines.append("```json")
    lines.append(json.dumps(handoff, indent=2, ensure_ascii=False))
    lines.append("```")
    lines.append("")
    lines.append("## Execution Pathway")
    lines.append("")
    lines.append(
        "Follow `user/return -> L1 -> L2 plan -> execute/realize -> L1`. "
        "Layer 2 directly invokes the selected executor or active main model without Layer 3 or Layer 4. "
        "The following plan is a shape illustration, not evidence of readiness. Use it only when instruction-ready; "
        "fill actual parameters and state closure evidence/delegation scope or bounded preparation limits in purpose, "
        "and return the actual result or failure directly to `l1-router`."
    )
    lines.append("")
    execution_handoff = {
        "handoff_type": "planner_handoff",
        "planner_id": slug,
        "planner_decision": "instruction_ready",
        "execution_instruction": {
            "executor": {"kind": "tool", "name": tools[0]} if tools else {"kind": "main_model"},
            "parameters": {} if tools else {"confirmed_task_state": "current canonical state"},
            "purpose": str(spec.get("description") or f"Perform the {title} task."),
        },
        "return_to": "l1-router",
    }
    lines.append("```json")
    lines.append(json.dumps(execution_handoff, indent=2, ensure_ascii=False))
    lines.append("```")
    lines.append("")
    lines.append("## Must")
    lines.append("")
    lines.append("- Ground every result in the user's intent and any collected constraints.")
    for rule in guardrails:
        lines.append(f"- {rule}")
    lines.append("")
    lines.append("## Must Not")
    lines.append("")
    lines.append("- Do not duplicate registry-derived widget metadata or author the widget contract in Layer 2.")
    lines.append("- Do not render a widget yourself; that is Layer 4.")
    lines.append("- Do not bypass L3 Designer for an eligible interaction gap; never send a gap routing failure to Layer 3.")
    lines.append("- Do not invoke an unselected or unavailable executor, or treat an unsupported gap as instruction-ready.")
    lines.append("")
    lines.append("## Tools")
    lines.append("")
    if tools:
        tool_list = ", ".join(f"`{t}`" for t in tools)
        lines.append(
            f"L4 Renderer renders widgets with `render_html_widget`. This planner may also call {tool_list} "
            "once its instruction is ready; results are saved to the session and shown in chat."
        )
    else:
        lines.append(
            "Only Layer 4 may call renderer tools. Your task reasoning is your own, not a tool. Layer 4 "
            "generates HTML/CSS/JS and calls `render_html_widget`."
        )
    lines.append("")
    lines.append("## Stop / Continue / Escape")
    lines.append("")
    lines.append("- **Continue** when a widget return supplies what the next pass needs; the return re-enters Layer 1.")
    lines.append("- **Stop** local work by returning a nonterminal completion candidate to Layer 1; only Layer 1 may choose Completion.")
    lines.append("- **Escape** directly to Layer 1 when an indispensable capability is unavailable or necessary input cannot be safely supplied.")
    lines.append("")
    lines.append("## Next")
    lines.append("")
    lines.append(
        "Interaction Pathway sends only an eligible selected-widget gap to L3 Designer, then L4 Renderer. "
        "Execution Pathway invokes the selected executor or active main model directly from Layer 2 without Layer 3 or Layer 4. "
        "Every result or failure returns directly to `l1-router`, not to this planner. "
        "Only L1 Router chooses Host Agent Return or Completion."
    )
    lines.append("")
    return "\n".join(lines)


def render_l3_skill(new_widget: dict[str, Any], gap: dict[str, Any], planner_slug: str) -> str:
    w_slug = new_widget["slug"]
    title = str(new_widget.get("title") or _title_from_slug(w_slug))
    widget_type = str(new_widget.get("widget_type"))
    modality = str(new_widget.get("modality") or "custom")
    edge = str(gap.get("edge"))
    goal = str(gap.get("goal") or "collect_input")
    target = _edge_target(edge)
    source = _edge_source(edge)
    return_shape = new_widget.get("return_shape") or {}
    display_fields = list(new_widget.get("display_fields") or ["title", "summary"])
    runtime_capabilities = list(new_widget.get("runtime_capabilities") or [])
    external_libraries = list(new_widget.get("external_libraries") or [])

    purpose = str(new_widget.get("purpose") or f"Resolve the {gap.get('name')} gap.")
    description = json.dumps(f"Use when: {planner_slug} selects {w_slug} for {gap.get('name')} and {goal}.", ensure_ascii=False)
    return f"""---
name: l3-{w_slug}
description: {description}
---

# L3 Designer — {_markdown_cell(title)}

## Layer & Role

Layer 3 only designs interactions for eligible selected-widget gaps in Interaction Pathway. Validate exact `selected_widget_id: "{w_slug}"` for planner `{planner_slug}`, gap `{gap.get('name')}`, goal `{goal}`, edge `{edge}`; retain registered `{widget_type}` on `conversation_widget` with `{modality}` modality. Purpose: {_markdown_cell(purpose)}. L3 owns design; L4 owns accessible implementation, not missing semantics.

## Inputs

Read `planner_id`, `selected_widget_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `expected_return`, `return_to`, task/artifact evidence and runtime context. Resolve the exact local registry entry, including skill/path, eligibility, returns, artifact support, state destination and capabilities. Ground display fields {_markdown_cell(', '.join(display_fields))} in current evidence, not blank mock data. L2 supplies intent and evidence, not predesigned controls.
Runtime capability requirements: {_markdown_cell(', '.join(runtime_capabilities) or 'none beyond the host sandbox')}. Repository-approved library requirements: {_markdown_cell(', '.join(external_libraries) or 'none')}; use only actual available version-pinned declarations.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Specialize purpose and summary to `{goal}` and the missing transfer on `{edge}`. |
| Presented information | Show grounded {_markdown_cell(', '.join(display_fields))}; separate evidence, editable values and unresolved status with resolvable content sources. |
| Supported interaction | Derive only supported `{modality}` controls needed to produce the declared return; preserve stable IDs and substantive user limits. |
| Feedback and constraints | Explain requiredness, type/domain errors and current-value changes; never choose missing domain facts for the user. |
| Submission and return | Map each declared key below to its actual source, type and serialization; derived metadata needs mappings, not artificial controls. |
| Presentation intent | Organize meaningful hierarchy, accessible labels and reachable actions; derive relevant appearance/signature features without extra stages. |

## Essential Constraints

Validate exact ID, skill/path, planner/gap/goal/edge, return coverage, artifact support and runtime availability without searching for or substituting another widget. Preserve `chain_id` and `iai_binding.reason` in `iai.chain_id` and `iai.reason`; `{source}` belongs to `source_nodes`, `{target}` equals `target_node` and `state_update_target`. Only L1 merges this destination. Missing or inconsistent provenance fails, never re-diagnoses.
Preserve each host-supplied image as a complete session asset reference in `display`; L4 resolves it only with `window.widgetAssetUrl(ref)`, never `file://` or a raw path. Use one primary submission of current values, no approval checkbox or second confirmation. Do not embed HTML, CSS, JavaScript, iframe code, event handlers or remote implementation assets; do not render or execute task tools.

Schema return requirements (exact keys; type declarations, not sample output):

| Return key | Declared type/shape | Mapping and validation obligation |
| --- | --- | --- |
{_return_schema_rows(return_shape)}

Preserve nested types and every declared optional/empty value. Use exactly these keys in both `expected_return` and `presentation.profile.interaction.submission.return_mapping`; unsupported returns fail instead of adding fields or guessing a value.

## Output and Handoff

Pass a complete semantic contract using these eight local obligations; no success `handoff_type` or external document read:

{LOCAL_WIDGET_HANDOFF}

Check grounded resolvable sources, unique controls, constraints, requirements and exact producible return mappings before loading `l4-widget-renderer`. Invalid selection or missing indispensable evidence/capability returns `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors` identifying failed checks, and `return_to: l1-router`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 Router merges canonical state and chooses Host Agent Return or Completion (`decision: end`). Every Layer 3 error returns directly to Layer 1 without Layer 4 entry. Gap routing failures including `no_eligible_widget` return directly from Layer 2 to Layer 1. Execution Pathway is `user/return -> L1 -> L2 plan -> execute/realize -> L1`: Layer 2 directly invokes the selected executor or active main model without Layer 3 or Layer 4. Every widget return/failure re-enters `l1-router`; submission is nonterminal.
"""


def render_l1_routing_row(spec: dict[str, Any]) -> str:
    slug = spec["pack_slug"]
    condition = str(spec.get("routing_condition") or spec.get("description") or f"the task is {slug}.")
    return f"| `{slug}` | `l2-{slug}` | {condition} |"


# --------------------------------------------------------------------------- #
# Public API: preview + generate
# --------------------------------------------------------------------------- #
def _compile(spec: dict[str, Any]) -> dict[str, Any]:
    """Compile a spec into all artifacts (pure, no writes)."""
    slug = spec["pack_slug"]
    planner_entry = build_planner_entry(spec)
    new_widget_entries: list[dict[str, Any]] = []
    l3_skills: dict[str, str] = {}
    reuse_widget_updates: list[dict[str, str]] = []
    reuse_seen: set[str] = set()

    for gap in spec.get("gaps") or []:
        widget = gap.get("widget") or {}
        if widget.get("new"):
            nw = widget["new"]
            new_widget_entries.append(build_widget_entry(nw, gap, slug))
            l3_skills[nw["slug"]] = render_l3_skill(nw, gap, slug)
        elif widget.get("reuse"):
            reuse_id = str(widget["reuse"])
            if reuse_id not in reuse_seen:
                reuse_widget_updates.append({"id": reuse_id, "add_planner": slug})
                reuse_seen.add(reuse_id)

    return {
        "pack_slug": slug,
        "chains": _normalised_chains(spec),
        "planner_entry": planner_entry,
        "new_widget_entries": new_widget_entries,
        "reuse_widget_updates": reuse_widget_updates,
        "generation_requests": build_generation_requests(spec),
        "l2_skill": render_l2_skill(spec),
        "l3_skills": l3_skills,
        "l1_routing_row": render_l1_routing_row(spec),
    }


def catalog() -> dict[str, Any]:
    """Return the fixed IAI graph vocabulary plus the current widget/planner catalog."""
    widgets = _load_json(WIDGETS_JSON)
    planners = _load_json(PLANNERS_JSON)
    return {
        "nodes": IAI_NODES,
        "node_labels": IAI_NODE_LABELS,
        "edges": sorted(IAI_EDGES, key=_edge_sort_key),
        "widgets": [
            {
                "id": w.get("id"),
                "widget_type": w.get("widget_type"),
                "interaction_modality": w.get("interaction_modality"),
                "iai_edges": w.get("iai_edges", []),
                "expected_return_types": w.get("expected_return_types", []),
            }
            for w in widgets.get("widgets", [])
        ],
        "planners": [
            {"id": p.get("id"), "task_family": p.get("task_family")}
            for p in planners.get("planners", [])
        ],
    }


def preview(spec: dict[str, Any]) -> dict[str, Any]:
    errors, warnings = validate_spec(spec)
    result: dict[str, Any] = {"ok": not errors, "errors": errors, "warnings": warnings}
    if errors:
        return result
    compiled = _compile(spec)
    contract_errors, contract_report = _validate_contract_conformance(compiled)
    if contract_errors:
        result["ok"] = False
        result["errors"] = [*errors, *contract_errors]
        result["contracts"] = contract_report
        return result
    # Flag collisions against the current registry / skill tree.
    planners = _load_json(PLANNERS_JSON)
    widgets = _load_json(WIDGETS_JSON)
    planner_ids = _existing_ids(planners, "planners")
    widget_ids = _existing_ids(widgets, "widgets")
    collisions: list[str] = []
    if compiled["pack_slug"] in planner_ids:
        collisions.append(f"planner '{compiled['pack_slug']}' already exists")
    for entry in compiled["new_widget_entries"]:
        if entry["id"] in widget_ids:
            collisions.append(f"widget '{entry['id']}' already exists")
    for update in compiled["reuse_widget_updates"]:
        if update["id"] not in widget_ids:
            collisions.append(f"reused widget '{update['id']}' does not exist in the catalog")
    result.update(compiled)
    result["contracts"] = contract_report
    result["collisions"] = collisions
    result["files_to_write"] = [
        f"skills/l2-{compiled['pack_slug']}/SKILL.md",
        *[f"skills/l3-{s}/SKILL.md" for s in compiled["l3_skills"]],
        "registry/planners.json (append)",
        "registry/widgets.json (append/patch)",
    ]
    return result


def generate(spec: dict[str, Any], overwrite: bool = False) -> dict[str, Any]:
    errors, warnings = validate_spec(spec)
    if errors:
        return {"ok": False, "errors": errors, "warnings": warnings}

    compiled = _compile(spec)
    contract_errors, _ = _validate_contract_conformance(compiled)
    if contract_errors:
        return {"ok": False, "errors": contract_errors, "warnings": warnings}
    slug = compiled["pack_slug"]

    planners = _load_json(PLANNERS_JSON)
    widgets = _load_json(WIDGETS_JSON)
    planner_ids = _existing_ids(planners, "planners")
    widget_ids = _existing_ids(widgets, "widgets")

    if slug in planner_ids and not overwrite:
        return {"ok": False, "errors": [f"planner '{slug}' already exists (set overwrite to replace)."], "warnings": warnings}

    l2_dir = SKILLS_DIR / f"l2-{slug}"
    if l2_dir.exists() and not overwrite:
        return {"ok": False, "errors": [f"{l2_dir.relative_to(PLUGIN_DIR)} already exists (set overwrite)."], "warnings": warnings}

    written: list[str] = []

    # --- Layer 2 skill --------------------------------------------------- #
    l2_dir.mkdir(parents=True, exist_ok=True)
    (l2_dir / "SKILL.md").write_text(compiled["l2_skill"], encoding="utf-8")
    written.append(str((l2_dir / "SKILL.md").relative_to(PLUGIN_DIR)))

    # --- Layer 3 skills -------------------------------------------------- #
    for w_slug, text in compiled["l3_skills"].items():
        l3_dir = SKILLS_DIR / f"l3-{w_slug}"
        l3_dir.mkdir(parents=True, exist_ok=True)
        (l3_dir / "SKILL.md").write_text(text, encoding="utf-8")
        written.append(str((l3_dir / "SKILL.md").relative_to(PLUGIN_DIR)))

    # --- planners.json --------------------------------------------------- #
    planners["planners"] = [p for p in planners["planners"] if p.get("id") != slug]
    planners["planners"].append(compiled["planner_entry"])
    PLANNERS_JSON.write_text(json.dumps(planners, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    written.append("registry/planners.json")

    # --- widgets.json ---------------------------------------------------- #
    changed = False
    for entry in compiled["new_widget_entries"]:
        widgets["widgets"] = [w for w in widgets["widgets"] if w.get("id") != entry["id"]]
        widgets["widgets"].append(entry)
        changed = True
    by_id = {w.get("id"): w for w in widgets["widgets"]}
    for update in compiled["reuse_widget_updates"]:
        widget = by_id.get(update["id"])
        if widget is not None:
            planners_list = widget.setdefault("compatible_planners", [])
            if slug not in planners_list:
                planners_list.append(slug)
                changed = True
    if changed:
        WIDGETS_JSON.write_text(json.dumps(widgets, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written.append("registry/widgets.json")

    return {
        "ok": True,
        "errors": [],
        "warnings": warnings,
        "written": written,
        "l1_routing_row": compiled["l1_routing_row"],
        "manual_step": (
            "Add this row to the routing table in skills/l1-router/SKILL.md so Layer 1 can "
            "route to the new planner:\n" + compiled["l1_routing_row"]
        ),
    }
