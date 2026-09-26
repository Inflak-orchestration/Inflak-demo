---
name: l3-collage-operation-control
description: "Use when: L2 selects typed SVG operation parameters or execution confirmation."
---

# L3 Designer — SVG Operation Control

## Layer & Role

Design only `collage-operation-control` with exact registry type/surface. No diagnosis, substitution, rendering or execution.

## Inputs

L2 selection/planner/gap/goal, chain/binding, exact return; proposal/current artifact revision, stable targets/capabilities, supported operations, supplied typed values, constraints and preview context.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Complete typed values or confirm the specified execution operation. |
| Presented information | Target, supported operation, current/proposed values and preserved aspects. |
| Supported interaction | Capability-bound typed controls and declared preview/confirmation actions. |
| Feedback and constraints | Reversible host preview, color swatches and missing-value validation. |
| Submission and return | Serialize exact declared values; confirmation binds homogeneous allowlisted operations. |
| Presentation intent | Precise anchored controls with live artifact context. |

## Essential Constraints

For every displayed color, populate `display.color_previews` from actual values and require L4 to render a visible swatch with an accessible label; preserve domain bindings. Raw code text (HEX/RGB) is auxiliary, never the primary or only color preview.

No invented values or unsupported families. Copy L2's actual registered binding unchanged: `I→Aug` for `proposal_operation_gap`, or `G→I` for `interaction_execution_gap`. The later authorized artifact commit may use `I→A` in L2 execution, never as this widget's interaction edge. Colors use `display.color_previews` `{value,label,role,proposal_id}` for every current/proposed/preview/selected color. Preview is transient; only explicit authorized submission enables later L2 execution. Iframe never patches. Preserve exact fileId/base_revision/targets and operation schemas; no raw markup/selectors/path data.

## Output and Handoff

Eight local parts; no external read/success `handoff_type`:

- Identity: nonempty exact `selected_widget_id`, instance `widget_id`, registry `widget_type`/`surface`, `planner_id`, contextual `purpose`, unchanged `interaction_goal`.
- `iai`: unchanged L2 `chain_id`, `gap_type`, `reason`, `source_nodes`, `maps_to_edge`, `target_node`; named chain/meaningful reason, edge source in sources, destination=target and allowed `state_update_target`; deterministic L1 `merge_strategy`, `next_planner_action: "re-enter Layer 1"`.
- `display`: actual sources/revisions/values/unresolved status; no invented evidence/defaults/assets/previews/outcomes; preserve `artifact_binding`/`placement`.
- `controls`: unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty declared `return_keys`, typed/limit/source/edit `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`; nonempty resolvable `content` records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`); nonempty interaction `actions`/`feedback`; submission nonempty `label`/`preconditions`/exact `return_mapping`; nonempty semantic `appearance`/`signature_features`.
- `expected_return`: exactly L2 keys/types and identical mapping keys, actual source/serialization/optional-empty handling; no artificial metadata controls.
- `widget_requirements`: four nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`, consistent with profile, no extra gates.
- `safety`: `allow_html: false`, `allow_script: false`; optional `runtime` approved available capabilities/pinned libraries only; optional plugin-relative `reference_assets` design-time only.

Validate exact skill/path/planner/gap/goal/edge/returns/state/artifact/runtime. Send `l4-collage-authoring-renderer`. Failure: `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, `return_to: l1-collage-authoring-core`; bypass L4 without substitution.

## Workflow End Authority

All outcomes to `l1-collage-authoring-core`; only L1 merges state or emits `decision: end`.
