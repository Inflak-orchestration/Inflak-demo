---
name: l3-pN8-collage-asset-replacement-control
description: "Use when: L2 selects prepared asset replacement for a stable P8 cutout."
---

# L3 Designer — Collage Asset Replacement

## Layer & Role

Design only `pN8-collage-asset-replacement-control`, type `collage_asset_replacement_control`, surface `artifact_canvas_widget`. Interaction Pathway only; no diagnosis, substitution, rendering or execution.

## Inputs

Read L2 selection/planner/gap/goal, chain/binding, exact return and L1 target. Require current artifact/revision, stable cutout ID, current asset/transform/order and 1–3 candidates from `authoring_bundle.asset_candidates_by_object[object_id]`; each has actual session `fileId`, label, rationale, kind and source tool.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Choose a prepared replacement without another AI call. |
| Presented information | Current cutout, candidate thumbnails, labels, preparation kind and provenance. |
| Supported interaction | Preview candidate, reset, Apply and dismiss. |
| Feedback and constraints | Reversible host preview preserves transform and z-order. |
| Submission and return | Apply maps exactly one `replace_cutout_asset` to current artifact/revision. |
| Presentation intent | Compact object-anchored gallery keeps the collage visible. |

## Essential Constraints

Reject absent session IDs, opaque/unvalidated assets, current-asset candidates and duplicate fileIds. Return only declared `artifact_id`, `base_revision`, `operations` with `op`, stable `object_id`, prepared `asset_file_id`, `label`. No transforms or unrelated object changes. Preview is transient; only Apply authorizes host commit. Never generate, fetch, invent assets, rewrite SVG or implement UI here.

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

Every outcome re-enters `l1-pN8-core-module`. Only L1 merges canonical state or emits `decision: end`; replacement is nonterminal.
