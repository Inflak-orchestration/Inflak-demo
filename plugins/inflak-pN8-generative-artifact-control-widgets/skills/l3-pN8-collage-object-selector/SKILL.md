---
name: l3-pN8-collage-object-selector
description: "Use when: L2 selects the P8 stable collage object selector."
---

# L3 Designer — Collage Object Selector

## Layer & Role

Design only `pN8-collage-object-selector`, type `collage_object_selector`, on `artifact_canvas_widget`. Interaction Pathway only; never diagnose, select a substitute, render or execute.

## Inputs

Read L2 planner, selection, gap, goal, chain, binding, exact expected return and L1 target. Require current artifact reference/revision, stable object IDs, labels, types, bounds, lock/visibility state and current selection. Validate the exact local registry entry and runtime capabilities.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Ground the user's selection for the already diagnosed object gap. |
| Presented information | Live collage, distinguishable object labels/types, bounds, lock/visibility and selection. |
| Supported interaction | Host hover/click selection, overlapping-object cycling and scoped multi-select. |
| Feedback and constraints | Keep Canvas/list selection synchronized; expose selected IDs without selecting on the user's behalf. |
| Submission and return | Return only declared `selected_object_ids` and `selection_scope`. |
| Presentation intent | Keep the live artifact primary and selection status compact and accessible. |

## Essential Constraints

Preserve stable IDs and artifact coordinates; reject unknown or stale objects. Selection does not mutate the artifact, authorize generation or confirm later edits. Host owns hit testing and selection; L3 specifies semantics only. Respect declared selection cardinality and visibility/lock capabilities. No markup, renderer code, invented IDs or API calls.

## Output and Handoff

Supply all eight parts locally; no external schema read or success `handoff_type`:

- Identity: nonempty exact `selected_widget_id`, unique instance `widget_id`, registry `widget_type`/`surface`, `planner_id`, contextual `purpose`, unchanged `interaction_goal`.
- `iai`: copy L2 `chain_id`, `gap_type`, binding `reason`, `source_nodes`, `maps_to_edge`, `target_node` unchanged. Require named chain, meaningful reason, edge source in sources, destination equal to target and allowed `state_update_target`; deterministic L1 `merge_strategy`, `next_planner_action: "re-enter Layer 1"`.
- `display`: grounded task values, actual source references/revision and unresolved status; no fabricated defaults, evidence, assets, previews or outcomes. Preserve artifact binding/placement separately when required by the host.
- `controls`: records with unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty declared `return_keys`, and type/limit/source/edit `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`; nonempty `content` records with resolvable `source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`; `interaction` has nonempty `actions`/`feedback`, `submission` with nonempty `label`, `preconditions`, exact `return_mapping`; nonempty semantic `appearance` and `signature_features`.
- `expected_return`: exactly L2 keys/types and identical submission mapping keys, each naming actual source and serialization, including optional/empty semantics; derived metadata needs mappings, not artificial controls.
- `widget_requirements`: four nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`, consistent with the profile, without extra gates.
- `safety`: `allow_html: false`, `allow_script: false`; optional `runtime` only approved available capabilities/pinned libraries; optional plugin-relative `reference_assets` are design-time principles, never runtime assets.

Validate exact skill/path, planner/gap/goal/edge, return coverage, state target and artifact/runtime support. Send complete design to `l4-pN8-widget-renderer`. Failure emits `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, `return_to: l1-pN8-core-module`; bypass L4 without substitution.

## Workflow End Authority

All returns/failures re-enter `l1-pN8-core-module`. Only L1 merges canonical state or emits `decision: end`; selection is nonterminal.
