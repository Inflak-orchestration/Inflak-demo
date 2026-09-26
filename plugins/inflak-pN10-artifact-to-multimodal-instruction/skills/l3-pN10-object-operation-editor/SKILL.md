---
name: l3-pN10-object-operation-editor
description: "Use when: L2 selects object-operation-editor for typed P10 instruction values."
---

# L3 Designer — Object Operation Editor

## Layer & Role

Design only `object-operation-editor` / `object_operation_editor` on `artifact_canvas_widget`. No diagnosis, substitution, rendering or execution.

## Inputs

Require L2 selection/planner/gap/goal, chain/binding, expected return, current artifact revision, suggestion ID, confirmed stable targets, compatible operations/current values and missing parameters.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Complete one grounded semantic instruction operation. |
| Presented information | Suggestion, target labels/IDs, current operation and missing values. |
| Supported interaction | Capability-filtered operation choice and typed parameter editing. |
| Feedback and constraints | Concrete instruction preview, source focus, validation and color swatches. |
| Submission and return | Map `suggestion_id`, `instruction_operation`, `action` exactly. |
| Presentation intent | Accessible object-anchored editor, live source stays visible. |

## Essential Constraints

For every displayed color, populate `display.color_previews` from actual values and require L4 to render a visible swatch with an accessible label; preserve domain bindings. Raw code text (HEX/RGB) is auxiliary, never the primary or only color preview.

Preserve source revision, stable target/primary IDs and keyboard-focusable target bindings. Use only planner-declared semantic operations supported by object type; missing required values remain unresolved. Include operation colors in `display.color_previews` as `{value,label,role,operation_id}`. Semantic operations are not patch operations; source is read-only. No arbitrary JSON, inferred values, selectors, markup, export or patch authorization.

## Output and Handoff

Complete local contract; no external read or success `handoff_type`:

- Identity: nonempty exact `selected_widget_id`, instance `widget_id`, registry `widget_type`/`surface`, `planner_id`, contextual `purpose`, unchanged `interaction_goal`.
- `iai`: unchanged L2 `chain_id`, `gap_type`, `reason`, `source_nodes`, `maps_to_edge`, `target_node`; named chain/meaningful reason, edge source in sources, destination=target and allowed `state_update_target`; deterministic L1 `merge_strategy`; `next_planner_action: "re-enter Layer 1"`.
- `display`: actual sources/revision/values/unresolved status; no invented evidence/defaults/assets/previews/outcomes; preserve `artifact_binding`/`placement`.
- `controls`: unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty declared `return_keys`, typed/limit/source/edit `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`, nonempty resolvable `content` records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`); nonempty interaction `actions`/`feedback`; submission nonempty `label`/`preconditions`/exact `return_mapping`; nonempty semantic `appearance`/`signature_features`.
- `expected_return`: under `return_mode: agent_interpreted`, preserve exactly L2 keys/types for this contextual interaction and identical mapping keys with actual source/serialization/optional-empty handling. Domain field names are guidance, not fixed registry keys; retain user evidence for L1 interpretation, no artificial metadata controls or inferred consent.
- `widget_requirements`: four nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`, consistent with profile, no extra gates.
- `safety`: `allow_html: false`, `allow_script: false`; optional `runtime` approved available capabilities/pinned libraries only; optional plugin-relative `reference_assets` design-time only.

Validate exact skill/path, planner/gap/goal/edge, returns/state/artifact/runtime. Send `l4-pN10-widget-renderer`. Failure: `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, `return_to: l1-pN10-core-module`; no L4/substitution.

## Workflow End Authority

All outcomes re-enter `l1-pN10-core-module`; only L1 merges state or emits `decision: end`.
