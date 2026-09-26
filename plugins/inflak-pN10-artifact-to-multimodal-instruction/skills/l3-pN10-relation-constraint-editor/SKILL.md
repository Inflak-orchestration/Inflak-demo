---
name: l3-pN10-relation-constraint-editor
description: "Use when: L2 selects explicit P10 object relations and preserve constraints."
---

# L3 Designer — Relation Constraint Editor

## Layer & Role

Design only `relation-constraint-editor` / `relation_constraint_editor` on `artifact_canvas_widget`. No diagnosis, substitution, rendering or execution.

## Inputs

Require L2 selection/planner/gap/goal, chain/binding, exact return, suggestion ID, current artifact revision, bound stable objects, existing relations and constraints.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Specify source/reference relationships and preserve constraints. |
| Presented information | Named endpoints, roles, current relations and constraints. |
| Supported interaction | Choose bound endpoints, allowlisted relation and real constraint values. |
| Feedback and constraints | Readable relation sentence, source focus and invalid-endpoint feedback. |
| Submission and return | Map `suggestion_id`, `relations`, `constraints`, `action`. |
| Presentation intent | Compact anchored relation rows with accessible endpoint navigation. |

## Essential Constraints

Allow `left_of`, `right_of`, `above`, `below`, `inside`, `in_front_of`, `behind`, `aligned_with`, `avoid_overlap`; preserve `source_object_id`, `type`, `target_object_id` and target/reference/preserve roles. Constraints include supported `preserve_style`, `preserve_unaffected_objects`, `stay_inside_canvas`, `avoid_overlap`, `allow_regeneration`. Reject self-relations, absent/unbound endpoints and unsupported predicates. Endpoints/rows are keyboard-focusable; Canvas selection focuses matching rows, endpoint focuses object, row focuses both and anchors beside source. Preserve unfinished edits. Source stays read-only; no arbitrary JSON or patches.

## Output and Handoff

Complete local contract; no external read or success `handoff_type`:

- Identity: nonempty exact `selected_widget_id`, instance `widget_id`, registry `widget_type`/`surface`, `planner_id`, contextual `purpose`, unchanged `interaction_goal`.
- `iai`: unchanged L2 `chain_id`, `gap_type`, `reason`, `source_nodes`, `maps_to_edge`, `target_node`; named chain/meaningful reason, edge source in sources, destination=target and allowed `state_update_target`; deterministic L1 `merge_strategy`; `next_planner_action: "re-enter Layer 1"`.
- `display`: actual source/revision/values/unresolved status; no invented evidence/defaults/assets/previews/outcomes; preserve `artifact_binding`/`placement`.
- `controls`: unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty declared `return_keys`, typed/limit/source/edit `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`, nonempty resolvable `content` records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`); nonempty interaction `actions`/`feedback`; submission nonempty `label`/`preconditions`/exact `return_mapping`; nonempty semantic `appearance`/`signature_features`.
- `expected_return`: under `return_mode: agent_interpreted`, preserve exactly L2 keys/types for this contextual interaction and identical mapping keys with actual source/serialization/optional-empty handling. Domain field names are guidance, not fixed registry keys; retain user evidence for L1 interpretation, no artificial metadata controls or inferred consent.
- `widget_requirements`: four nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`, consistent with profile, no extra gates.
- `safety`: `allow_html: false`, `allow_script: false`; optional `runtime` approved available capabilities/pinned libraries only; optional plugin-relative `reference_assets` design-time only.

Validate exact skill/path, planner/gap/goal/edge, returns/state/artifact/runtime. Send `l4-pN10-widget-renderer`. Failure: `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, `return_to: l1-pN10-core-module`; no L4/substitution.

## Workflow End Authority

All outcomes re-enter `l1-pN10-core-module`; only L1 merges state or emits `decision: end`.
