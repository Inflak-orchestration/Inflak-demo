---
name: l3-pN8-collage-transform-control
description: "Use when: L2 selects deterministic P8 object transforms."
---

# L3 Designer — Collage Transform

## Layer & Role

Design only `pN8-collage-transform-control`, type `collage_transform_control`, surface `artifact_canvas_widget`. Interaction Pathway only: no diagnosis, substitution, rendering or task execution.

## Inputs

Consume L2 selection, planner, gap, goal, chain/binding, exact return and L1 target. Require actual artifact/revision, stable selected object, transform, bounds, canvas coordinate convention and supported unlocked capabilities.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Move, resize or rotate the selected object precisely. |
| Presented information | Live object, bounds and current x/y/width/height/rotation. |
| Supported interaction | Host drag/resize/rotate handles, synchronized numeric fields, aspect lock, reset, Apply/dismiss. |
| Feedback and constraints | Reversible preview with visible geometry and bounded typed values. |
| Submission and return | One `set_transform` for the exact object and current revision. |
| Presentation intent | Direct manipulation remains primary; inspector is concise and accessible. |

## Essential Constraints

Preserve artifact coordinates and transform conventions; do not confuse viewport pixels, deltas and absolute positions. Positive dimensions, finite values and capability/lock limits apply. Host owns handles and reversible preview. Apply alone returns declared `artifact_id`, `base_revision`, `operations` with `object_id`, `x`, `y`, `width`, `height`, `rotation`; reset/dismiss never commits. No SVG/path rewriting, generation or L3 code.

## Output and Handoff

Local eight-part contract; no success `handoff_type` or external schema read:

- Identity: nonempty exact `selected_widget_id`, instance `widget_id`, registry `widget_type`/`surface`, `planner_id`, contextual `purpose`, unchanged `interaction_goal`.
- `iai`: copy unchanged L2 `chain_id`, `gap_type`, binding `reason`, `source_nodes`, `maps_to_edge`, `target_node`; named chain/meaningful reason, edge source in sources, destination equals target and allowed `state_update_target`; deterministic L1 `merge_strategy`, `next_planner_action: "re-enter Layer 1"`.
- `display`: grounded values, actual source/revision, unresolved status; no invented evidence/defaults/assets/previews/outcomes. Preserve required host artifact binding/placement.
- `controls`: unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty declared `return_keys`, typed/limit/source/edit `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`; nonempty resolvable `content` records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`); nonempty interaction `actions`/`feedback`; `submission` with nonempty `label`, `preconditions`, exact `return_mapping`; nonempty semantic `appearance` and `signature_features`.
- `expected_return`: exactly L2 keys/types and identical submission mapping keys, each with actual source/serialization and optional/empty handling; no artificial controls for derived metadata.
- `widget_requirements`: four nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`, consistent with profile and no extra gates.
- `safety`: `allow_html: false`, `allow_script: false`; optional `runtime` only approved available capabilities/pinned libraries; optional plugin-relative `reference_assets` design-time only.

Validate exact skill/path, planner/gap/goal/edge, returns/state target and artifact/runtime support. Send to `l4-pN8-widget-renderer`. Failure returns `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, `return_to: l1-pN8-core-module`; bypass L4 without replacement.

## Workflow End Authority

Every outcome re-enters `l1-pN8-core-module`; only L1 merges canonical state or emits `decision: end`.
