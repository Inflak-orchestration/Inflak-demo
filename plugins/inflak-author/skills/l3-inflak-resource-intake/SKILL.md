---
name: l3-inflak-resource-intake
description: "Use when: Author selects execution-resource responsibility or collection of actual supplied references."
---

# L3 Designer — Execution Resource Intake

## Layer & Role

Interaction Pathway only: L1 → L2 selection → L3 design → L4 render → L1. Validate `inflak-resource-intake` for `inflak-authoring`, `execution_dependency_gap`, `choose_execution_resources`, `G→I`; design registered `execution_resource_intake` on `conversation_widget`. No resource inspection, feasibility decision, substitution, execution or rendering.

## Inputs

Read exact `planner_id`, `selected_widget_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `expected_return`, `return_to`, actual runtime/local registry and context. Consume dependency reason, supported execution choices, actually available image operations, sanitized attachments, resource kinds/purposes and faithful fallback policy. L2 supplies intent/evidence, not controls.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Resolve responsibility or identify actual resources needed for promised behavior. |
| Presented information | Why capability matters, existing attachments, available choices and no-credentials warning. |
| Supported interaction | Choose preference, conditionally select a real image operation, reference/upload resources and choose permitted fallback. |
| Feedback and constraints | Distinguish selected/uploading/uploaded/deferred/failed; described runtime is not executable. |
| Submission and return | Exact preference/tool, sanitized stable refs, fallback boolean/note; no contents or paths. |
| Presentation intent | Focused resource decision with relevant conditional controls, not architecture questions. |

## Essential Constraints

- Validate ID, skill/path, planner/gap/goal/edge, returns, artifact kinds and runtime. Preserve chain/reason/source/edge/target; G is in sources, I is target and allowed `state_update_target`. L1 maps I to `execution_resources`, merging resources by actual `fileId` and preserving dependency status.
- Fixed returns: `execution_preference`, `image_tool_name`, `freeform_note` strings; `resource_refs` array; `allow_host_fallback` boolean. Image mode requires one actual listed available operation and no unnecessary upload. Do not use an obsolete hard-coded tool catalog or silently substitute background removal for object extraction.
- New resources require successful host upload before returning sanitized `fileId`, name, MIME, size, purpose and indispensable status. Local paths, credentials and contents are never return values. Imported/runtime/service modes can defer upload explicitly, but that does not close the dependency.
- Reject secret collection, arbitrary local paths or implicit executable approval. No inspecting contents, running uploaded Python, calling services or validating credentials. Host fallback only within supplied equivalent-behavior policy.
- One primary submit; no approval checkbox/second confirmation. No HTML/CSS/JavaScript, local runtime path, invented uploads, rendering or execution calls; L4 owns the actual upload bridge wiring.

## Output and Handoff

Use these eight local obligations; no success `handoff_type` or external schema read:

- Identity: nonempty `selected_widget_id` (exact selection), `widget_id` (instance), registry `widget_type`/`surface`, `planner_id`, contextual `purpose`, unchanged `interaction_goal`.
- `iai`: copy named `chain_id`, `gap_type`, binding `reason`, `maps_to_edge`, `source_nodes`, `target_node` unchanged; require meaningful reason, edge source in sources and destination equal to target and allowed `state_update_target`. Include deterministic L1 `merge_strategy`, `next_planner_action: "re-enter Layer 1"`.
- `display`: grounded task values, actual source references, current values and unresolved status; no invented defaults, uploads, previews or outcomes.
- `controls`: unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty declared `return_keys`, `constraints` for types/limits/source/edit rules.
- `presentation.profile`: nonempty `archetype`/`summary`; nonempty `content` records with resolvable `source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`; `interaction` with nonempty `actions`/`feedback` and `submission` (nonempty `label`, nonempty `preconditions`, exact `return_mapping`); nonempty semantic `appearance` and `signature_features` list, not extra stages or implementation.
- `expected_return`: exactly L2 keys/types; `presentation.profile.interaction.submission.return_mapping` has exactly those keys, each naming actual source and serialization, preserving optional/empty semantics. Map derived metadata without artificial controls.
- `widget_requirements`: four nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`; minimal meaningful obligations consistent with the profile, not extra gates.
- `safety`: `allow_html: false`, `allow_script: false`. Optional `runtime` only for available approved capabilities/pinned libraries; optional `reference_assets` are plugin-relative design-time references/principles, never runtime assets.

Validate references, upload-state requirements, exact mappings and producible values, then hand to `l4-inflak-author-renderer`. Invalid selection or missing indispensable evidence/capability returns `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, `return_to: l1-inflak-author-core`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 owns state/merging and Completion or `decision: end`. Every resource interaction/failure re-enters `l1-inflak-author-core`; upload or preference selection is not inspection, runtime approval or completion.
