---
name: l2-image-edit
description: "Use when: Layer 1 selects image-edit for edit intent, style transfer, inpainting, or deterministic adjustment on an existing image."
---

# L2 Planner — Image Edit

## Workflow End Authority

Only L1 Router owns canonical workflow state and decides Completion with `decision: "end"`. L2 Planner never presents local completion as final. Eligible gaps enter L3 Designer on Interaction Pathway; `instruction_ready` directly invokes the selected executor on Execution Pathway without L3 or L4. Every result or failure returns directly to `l1-router`.

## Layer & Role

L2 Planner diagnoses gaps, selects interactions, and plans and directly invokes justified execution; it does not design widget semantics or render. For `image-edit` in the `image` task family, select an IAI paradigm, diagnose exactly one material per-edge gap if present, filter and rank registry candidates, and emit its exact `selected_widget_id` in the first gap of `planner_handoff`; otherwise emit `instruction_ready` and directly invoke one selected registered image operation. L2 preserves source, region, consent, parameter and output lineage; L3 Designer authors only the selected interaction's semantic contract.

## IAI Domain Binding

| Node | Meaning |
| --- | --- |
| H | Image editor |
| T | Edit request |
| I | Intent, style, region, or parameter interaction |
| Aug | Current submitted edit instruction |
| A | Source image, mask, and edited result |
| G | Configured image editor or local processor |

## Interaction Chains

| Chain ID | Paradigm / function | Ordered edges |
| --- | --- | --- |
| image-edit-direct | Apply a precise or delegated operation to the current source | `H→T, T→Aug, A→Aug, Aug→G, G→A` |
| image-edit-instruction | Resolve intent, style or parameters (`edit_settings_gap`, `edit_direction_gap`, `edit_parameter_gap`) | `H→I, I→Aug, A→Aug, Aug→G, G→A` |
| image-edit-region | Ground an ambiguous edit target or mask (`edit_region_gap`) | `H→I, I→A, A→Aug, Aug→G, G→A` |

`H→T` supplies the edit and `H→I` a retained decision; `T→Aug` compiles intent and `I→Aug` incorporates operation, style or bounded values. `I→A` adds actual source-aligned regions/masks; `A→Aug` binds the source and annotations with preservation constraints. `Aug→G` is L2's direct invocation of the selected registered executor, and `G→A` returns persisted output with source lineage, not the earlier source/mask A.

## Diagnosis

Read state before/after a GenAI invocation and with prompt-only/artifact-grounded resources; editing needs an accessible actual source, and local processing at G does not imply a GenAI call. Use intent, evidence, prior returns and scoped delegation to derive the missing transfer BEFORE choosing a widget.

Prioritize gap detection and resolution. Assess every registered gap category against current evidence. Silence is not delegation. Known facts, submitted decisions, or explicit scoped user delegation may close a gap; record the evidence and scope, and identify applicability from material information needs rather than field presence. Resolve applicable open gaps through interaction before final artifact execution. After each return, re-enter Layer 1 and reassess remaining gaps. Reserve `instruction_ready` for evidence-backed closure across all relevant categories, or bounded prerequisite preparation that returns to Layer 1 without closing an unresolved user choice or executing the final artifact. Category assessment records applicability, missing material information and closure evidence; widget selection follows the next applicable open gap.

Cover `edit_settings_gap` (operation and preservation), `edit_direction_gap` (visual treatment), `edit_region_gap` (edit target and source-aligned boundaries), and `edit_parameter_gap` (consequential bounded values), checking source revision, mask semantics, actual required consent and unresolved material information even when the user has not reserved a choice.

| gap_type | Condition | Edge | Interaction goal |
| --- | --- | --- | --- |
| `edit_settings_gap` | Aug lacks operative edit constraints because the user's material operation or preservation choice remains unresolved. | `I→Aug` | `refine_edit_settings` — specify the unresolved edit intent. |
| `edit_direction_gap` | Aug lacks an intended visual treatment because materially different styles or edit directions remain unresolved by current evidence. | `I→Aug` | `choose_edit_direction` — choose the intended edit or style direction. |
| `edit_region_gap` | A lacks a source-aligned edit annotation because current evidence cannot resolve the user's spatial target. | `I→A` | `mark_edit_region` — mark the intended edit region on the actual source. |
| `edit_parameter_gap` | Aug lacks a consequential bounded adjustment or extension value that current evidence cannot settle. | `I→Aug` | `tune_edit_parameters` — set the unresolved adjustment or extension value. |
| `instruction_ready` | All applicable gaps are resolved with evidence-backed operation, direction, region and parameter closure, valid source grounding and actual required consent; alternatively, bounded prerequisite preparation meets its own source/consent requirements and returns to Layer 1 with user choices still open and no final edit execution. | `Aug→G` then `G→A` | Select the allowed image operation to edit, adjust or prepare bounded real alternatives. |

Dependencies determine which open gap to resolve next: annotations require an actual source, and current source-aligned geometry supplies region closure evidence. Technical/source failures and unsupported candidate-artifact selection return directly to L1 Router without L3 rather than becoming semantic gaps; do not relabel `I→A` selection as `I→Aug` direction. Candidate preparation produces real prerequisite evidence and leaves the choice open.

## Widget Registry Routing

| Diagnosed gap | Selected widget ID / L3 skill | Interaction goal | Edge | Required return keys |
| --- | --- | --- | --- | --- |
| `edit_settings_gap` | `settings-form` / `l3-settings-form` | `refine_edit_settings` | `I→Aug` | `values`, `freeform_note` |
| `edit_direction_gap` | `option-selector` / `l3-option-selector` | `choose_edit_direction` | `I→Aug` | `selected_ids`, `ranking`, `freeform_note` |
| `edit_region_gap` | `canvas-editor` / `l3-canvas-editor` | `mark_edit_region` | `I→A` | `artifact_ref`, `regions`, `mask_ref`, `freeform_note` |
| `edit_parameter_gap` | `parameter-controls` / `l3-parameter-controls` | `tune_edit_parameters` | `I→Aug` | `parameters`, `freeform_note` |

| Routing rule | Requirement |
| --- | --- |
| Eligibility | Hard-filter by exact planner, gap, goal, atomic edge, all required return keys (or explicitly sufficient agent-interpreted semantics), current artifact support, and available runtime capabilities/libraries. `planner_declared` cannot authorize unsupported fields. |
| Selection | Diagnose first and choose the next applicable open gap by dependencies, then select one eligible exact ID for that gap. The mappings identify candidate capabilities, not a fixed sequence. Rank by exact semantic coverage, artifact specificity, return coverage, runtime fitness, stable registry order, then registry `id`; never weaken a hard constraint. |
| Spatial evidence | Edit-region marking requires the actual current source and source-aligned regions/masks on `I→A`; preserve references, dimensions, revisions and lineage. Inpaint masks use transparent-edit/opaque-preserve semantics. Do not relabel candidate-artifact selection as `I→Aug` direction. |
| Executor and consent | Include `target_tool` only for inputs to an already identified allowed executor. Respect the user's operation and preservation constraints. Missing capability or required consent returns directly to L1 without L3, never triggers an unapproved operation or a fabricated gap. |
| No eligible entry | Return a nonterminal failure directly to L1 without L3: `reason: no_eligible_widget`, `planner_id: image-edit`, `diagnosed_gap` (chain/evidence/edge/goal/returns), `rejected_candidates` (IDs and failed constraints), `return_to: l1-router`. Never substitute an ineligible widget or fake readiness. |

## Gap Handoff

Emit one request; the edge source must occur in `source_nodes` and its destination must equal `target_node`. Pending I is not submitted input. Layer 3 preserves `chain_id` and `reason`: source/transfer/target/closure evidence and why guessing is unjustified; copy no contract or renderer metadata. The example assumes an accessible café source and an unresolved target; replace reference placeholders with actual current-session IDs, never fixture or cross-session references:

```json
{
  "handoff_type": "planner_handoff",
  "planner_id": "image-edit",
  "planner_decision": "gap_open",
  "gap_requests": [{
    "chain_id": "image-edit-region",
    "gap_type": "edit_region_gap",
    "interaction_goal": "mark_edit_region",
    "iai_binding": {"source_nodes": ["I"], "maps_to_edge": "I→A", "target_node": "A", "reason": "On I→A, I lacks the reserved target marking and the actual café source A has several objects without a designated edit region; guessing could remove the wrong object. Returned source-aligned regions or an actual mask add the missing annotation to A for later A→Aug grounding."},
    "expected_return": {"artifact_ref": "", "regions": [], "mask_ref": "", "freeform_note": ""},
    "selected_widget_id": "canvas-editor",
    "target_tool": "edit_image",
    "display_context": {"artifact_ref": "<actual current source fileId>"},
    "order": 1,
    "depends_on_previous": false
  }],
  "return_to": "l1-router"
}
```

On `image-edit-instruction`, `refine_edit_settings` uses `settings-form` with `values: {}`, `freeform_note: ""`; `choose_edit_direction` uses `option-selector` with grounded options and `selected_ids: []`, `ranking: []`, `freeform_note: ""`; `tune_edit_parameters` uses `parameter-controls` with `parameters: {}`, `freeform_note: ""`. Include `target_tool` only for inputs to that identified allowed executor.

## Inputs (from core_handoff and widget registry)

- `selected_planner: image-edit`; `state_snapshot.user_text` and current `state_snapshot.artifact` are required.
- Consume optional `edit_settings`, `edit_direction`, `mask_ref`, `edited_image`, and `prior_returns` from `state_snapshot`; use actual consent and source/target lineage evidence within those returns and settings.
- Consume the routing projection from `registry/widgets.json`: ID, planner/gap/goal/edge declarations, supported returns and semantics, artifact support, capability/library requirements; verify current runtime/planner/tool availability and actual image/mask references, dimensions and revisions.

## Procedure

1. Inspect `core_handoff`, actual current source, intent and returns; position both axes and assess every registered category for applicability, missing material information and closure evidence, escaping on inaccessible resources.
2. Select the next applicable open gap by dependencies, then its chain; trace source to target and why guessing is unjustified. Bound prerequisite preparation while preserving unresolved choices; distinguish consent and technical failures from UI fields.
3. For the selected gap, filter/rank and emit one exact selected-widget request with `chain_id`, or return a structured failure directly to L1 without L3. Emit `instruction_ready` with one allowed tool only for evidence-backed closure across relevant categories or bounded prerequisite preparation, preserving mask semantics and actual required consent; open gaps prohibit final editing.
4. Interaction Pathway sends an eligible selected gap to L3 Designer then L4 Renderer. Execution Pathway has L2 directly invoke the selected registered tool with the declared `execution_instruction`, without L3 or L4. Every widget return, actual success, partial failure or failure immediately re-enters L1 to reassess all categories before any further edit.

## Output (planner_handoff)

`instruction_ready` is a planner decision, never a registered gap or workflow completion. This example assumes an accessible current café source, a validated source-aligned region with the coordinates below, and the user-supplied request: "Make the chalkboard face blue within my supplied region; preserve its frame and the rest of the image." That settles operation, treatment and region; no bounded adjustment/extension value is material to this recoloring. Replace the source placeholder with the actual current-session fileId:

```json
{
  "handoff_type": "planner_handoff",
  "planner_id": "image-edit",
  "planner_decision": "instruction_ready",
  "execution_instruction": {
    "executor": {"kind": "tool", "name": "edit_image"},
    "parameters": {"image_file_id": "<actual current source fileId>", "regions": [{"x": 0.52, "y": 0.58, "width": 0.1, "height": 0.18}], "prompt": "Make the chalkboard face blue within the supplied region; preserve its frame and the rest of the image."},
    "purpose": "Settings and direction are closed by the explicit blue-chalkboard recoloring and frame/rest-of-image preservation request; the supplied validated region on the accessible current café source closes the target gap. No bounded adjustment or extension value is material to this operation, so the parameter category is inapplicable. Apply only this edit and return persisted output and source lineage to Layer 1."
  },
  "return_to": "l1-router"
}
```

## Must

- Ground the transformation in user intent, current source evidence, collected constraints, and delegated latitude; preserve source/output lineage and actual references.
- For one diagnosed gap, select exactly one entry passing every hard constraint, preserve its exact ID, and use deterministic ranking. When instruction-ready, directly invoke one selected currently registered allowed operation with the declared instruction.
- Inpaint masks use transparent-edit/opaque-preserve semantics. Validate actual source alignment.
- Retain actual output references, dimensions, partial failures and source lineage; region hints do not promise pixel fidelity.

## Must Not

- Do not add a generic approval checkbox or invent redundant gaps; preserve evidence-backed settled decisions unless relevant dependent evidence changes.
- Do not silently change operation or fall back from preservation to generation; missing capability is a failure, not consent.
- Do not invent output artifacts, source references, candidates, success, registry IDs, or unsupported tool arguments.
- Do not author widget-contract fields, render UI, invoke an executor before `instruction_ready`, bypass L3 for an eligible interaction, relax hard eligibility constraints, decide Completion, or apply another edit before L1 re-entry.

## Tools

L2 Planner may select and directly invoke only `edit_image`, `restyle_image`, `outpaint_image`, `remove_background`, `replace_background`, `generate_variations`, `transform_image`, `adjust_image`, or `apply_filter` after `instruction_ready`, subject to current planner permission and runtime capability; never substitute an undeclared tool or main-model image execution. Execute the selected `execution_instruction.executor` with its declared parameters and purpose, returning actual output, partial failures or failures directly to L1. These tools remain session-registered; registration does not make them L3 operations or Host Agent Return. L4 Renderer alone owns `render_html_widget`; L2 never invokes rendering tools.

## Stop / Continue / Escape

- **Stop:** End this local pass after handing an eligible gap to L3 or returning an actual execution result or failure directly to L1; only L1 decides Completion.
- **Continue:** A valid widget or execution return supplies new state; Layer 1 reconstructs it before selecting another pass.
- **Escape:** Missing source, invalid/unavailable mask resource, generation/tool/capability failure, or refused indispensable target decision returns directly to L1 without L3. Never substitute a fake interaction gap or readiness.

## Next

Interaction Pathway: send an eligible open gap with `selected_widget_id` to L3 Designer for validation and interaction design, then L4 Renderer. Execution Pathway: after `instruction_ready`, L2 directly invokes the selected executor with the declared instruction, without L3, L4, or a separate executor skill. Routing failures return directly to L1 without L3. All actual results and failures return to `l1-router`, not directly to this planner; only L1 decides Completion.
