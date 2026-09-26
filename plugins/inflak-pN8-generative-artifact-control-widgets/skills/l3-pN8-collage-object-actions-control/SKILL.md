---
name: l3-pN8-collage-object-actions-control
description: "Use when: L2 selects explicit removal of one editable P8 object."
---

# L3 Designer — Collage Object Actions

## Layer & Role

Design only `pN8-collage-object-actions-control`, type `collage_object_actions_control`, surface `artifact_canvas_widget`. Interaction Pathway only; no diagnosis, substitution, rendering or execution.

## Inputs

Read L2 selection/planner/gap/goal, chain/binding, exact return and L1 target. Require current artifact/revision, selected stable object label/type, lock/capability state and remaining object count.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Explicitly authorize removal of the named object. |
| Presented information | Exact target identity and the removal consequence in live context. |
| Supported interaction | One primary destructive Remove command and dismiss. |
| Feedback and constraints | Clearly identify the target; disable locked or final-object removal. |
| Submission and return | Remove itself confirms one revision-bound `remove_object`. |
| Presentation intent | Compact anchored action with accessible destructive styling. |

## Essential Constraints

No automatic removal, confirmation checkbox or second generic confirmation gate. Preserve explicit authorization via the primary Remove action. Never remove a locked object or the final remaining object. Return only declared `artifact_id`, `base_revision`, `operations` with `op: remove_object`, stable `object_id`. Do not combine with generation, replacement, transform or layer operations. Host commits; L3 has no UI code or tool calls.

## Output and Handoff

Local eight-part contract; no success `handoff_type` or external schema read:

- Identity: nonempty exact `selected_widget_id`, instance `widget_id`, registry `widget_type`/`surface`, `planner_id`, contextual `purpose`, unchanged `interaction_goal`.
- `iai`: unchanged L2 `chain_id`, `gap_type`, binding `reason`, `source_nodes`, `maps_to_edge`, `target_node`; named chain/meaningful reason, edge source in sources, destination equals target and allowed `state_update_target`; deterministic L1 `merge_strategy`, `next_planner_action: "re-enter Layer 1"`.
- `display`: grounded values, actual source/revision and unresolved status; no invented evidence/defaults/assets/previews/outcomes. Preserve host artifact binding/placement.
- `controls`: unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty declared `return_keys`, typed/limit/source/edit `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`; nonempty resolvable `content` records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`); nonempty interaction `actions`/`feedback`; `submission` with nonempty `label`, `preconditions`, exact `return_mapping`; nonempty semantic `appearance` and `signature_features`.
- `expected_return`: exactly L2 keys/types and identical submission mapping keys, each with actual source/serialization and optional/empty handling; no artificial controls for derived metadata.
- `widget_requirements`: four nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`, consistent with profile and no extra gates.
- `safety`: `allow_html: false`, `allow_script: false`, `requires_confirmation: true`; optional `runtime` only approved available capabilities/pinned libraries; optional plugin-relative `reference_assets` design-time only.

Validate exact skill/path, planner/gap/goal/edge, returns/state target and artifact/runtime support. Send to `l4-pN8-widget-renderer`. Failure: `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, `return_to: l1-pN8-core-module`; no L4 or substitute.

## Workflow End Authority

Every outcome re-enters `l1-pN8-core-module`; only L1 merges canonical state or emits `decision: end`.
