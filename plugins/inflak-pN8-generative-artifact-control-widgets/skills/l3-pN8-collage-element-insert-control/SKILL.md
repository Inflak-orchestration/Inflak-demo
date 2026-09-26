---
name: l3-pN8-collage-element-insert-control
description: "Use when: L2 selects insertion of prepared P8 collage elements."
---

# L3 Designer — Collage Element Insert

## Layer & Role

Design only `pN8-collage-element-insert-control`, type `collage_element_insert_control`, surface `artifact_canvas_widget`. Interaction Pathway only; do not plan, substitute, render or execute.

## Inputs

Read L2 selection/planner/gap/goal, chain/binding, exact return and L1 target. Require current artifact/revision, existing object IDs, canvas coordinates and 1–3 `authoring_bundle.addable_elements` with actual session `fileId`, new stable `object_id`, label/rationale, registered provenance and default transform.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Insert one already prepared element. |
| Presented information | Thumbnails, identity, preparation kind/provenance and intended placement. |
| Supported interaction | Choose, preview default placement, Add and dismiss. |
| Feedback and constraints | Reversible preview distinguishes pending insertion from persisted objects. |
| Submission and return | Add returns one revision-bound `add_cutout` operation. |
| Presentation intent | Compact prepared gallery beside the live collage. |

## Essential Constraints

Reject absent/opaque assets, unregistered provenance and IDs already present in the scene. Preserve supplied `x`, `y`, `width`, `height`, `rotation` in artifact coordinates; do not invent placement. Return exact declared `artifact_id`, `base_revision`, `operations` containing `op: add_cutout`, `object_id`, `label`, `asset_file_id` and typed geometry. Only Add authorizes host commit; no generation, fetch, restyle/outpaint, raw markup or implementation code.

## Output and Handoff

Complete local contract; no success `handoff_type` or external schema read:

- Identity: nonempty exact `selected_widget_id`, instance `widget_id`, registry `widget_type`/`surface`, `planner_id`, contextual `purpose`, unchanged `interaction_goal`.
- `iai`: unchanged L2 `chain_id`, `gap_type`, binding `reason`, `source_nodes`, `maps_to_edge`, `target_node`; named chain, meaningful reason, edge source in sources, destination equal to target and allowed `state_update_target`; deterministic L1 `merge_strategy`, `next_planner_action: "re-enter Layer 1"`.
- `display`: grounded values, actual sources/revision and unresolved status; no invented defaults/evidence/assets/previews/outcomes. Preserve host artifact binding and placement.
- `controls`: unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty declared `return_keys`, applicable typed/limit/source/edit `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`, nonempty resolvable `content` records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`); `interaction` has nonempty `actions`/`feedback`, `submission` with nonempty `label`, `preconditions`, exact `return_mapping`; nonempty semantic `appearance` and `signature_features`.
- `expected_return`: exactly L2 keys/types and identical submission mapping keys; each mapping names actual source and serialization including optional/empty semantics. Derived metadata needs no artificial control.
- `widget_requirements`: nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`; consistent with profile, no extra gates.
- `safety`: `allow_html: false`, `allow_script: false`, `allow_network: false`, `allow_generation: false`; optional `runtime` only approved available capabilities/pinned libraries; optional plugin-relative `reference_assets` are design-time, not runtime assets.

Validate exact skill/path, planner/gap/goal/edge, returns/state target and artifact/runtime support. Send to `l4-pN8-widget-renderer`. Failure: `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, `return_to: l1-pN8-core-module`; no L4 or substitute.

## Workflow End Authority

All results/failures return to `l1-pN8-core-module`. Only L1 merges actual next scene/revision or emits `decision: end`; insertion is nonterminal.
