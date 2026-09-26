---
name: l3-collage-layout-board
description: "Use when: L2 selects the unified SVG spatial layout board."
---

# L3 Designer — SVG Collage Layout Board

## Layer & Role

Design only `collage-layout-board` / `svg_collage_layout_board` on `artifact_canvas_widget`. No diagnosis, substitution, rendering or execution.

## Inputs

L2 selection/planner/gap/goal, chain/binding, exact return; current scene/revision, interaction_spec, canvas dimensions/coordinates, stable items with labels/types/transforms/aspect/z-order/visibility/lock/capabilities and declared regions.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Arrange actual objects and resolve spatial assignments. |
| Presented information | Live SVG stage, object labels, region bounds and geometry. |
| Supported interaction | Capability-limited drag/four-corner resize/rotate/align/distribute/snap/layers/region assignment. |
| Feedback and constraints | Canvas/list synchronization, guides/grid/safe bounds, undo/redo/reset and before-after. |
| Submission and return | Apply supplies action/interaction ID; host enriches changed typed geometry. |
| Presentation intent | Real spatial stage dominates, not blank cards or numeric-only fields. |

## Essential Constraints

Artifact coordinates never change with zoom. Locked objects remain visible/immovable. Regions preserve IDs/bounds/labels/types/assignments; labels are metadata, not SVG text without separate authorized text operations. Host owns draft and serialization. Apply alone yields changed `set_transform`/`set_order`, current binding/revision; iframe never reconstructs geometry. Reset keeps open; Regenerate/Reject/Dismiss no draft submission or mutation. Reject unknown IDs/stale revisions/unsupported transforms/spec-violating bounds. L4 implements draft events/reset/submit; L3 has no implementation code.

## Output and Handoff

Eight local parts; no external read/success `handoff_type`:

- Identity: nonempty exact `selected_widget_id`, instance `widget_id`, registry `widget_type`/`surface`, `planner_id`, contextual `purpose`, unchanged `interaction_goal`.
- `iai`: unchanged L2 `chain_id`, `gap_type`, `reason`, `source_nodes`, `maps_to_edge`, `target_node`; named chain/meaningful reason, edge source in sources, destination=target and allowed `state_update_target`; deterministic L1 `merge_strategy`, `next_planner_action: "re-enter Layer 1"`.
- `display`: actual sources/revisions/values/unresolved status; no invented evidence/defaults/assets/previews/outcomes; preserve `artifact_binding`/`placement`.
- `controls`: unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty declared `return_keys`, typed/limit/source/edit `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`; nonempty resolvable `content` records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`); nonempty interaction `actions`/`feedback`; submission nonempty `label`/`preconditions`/exact `return_mapping`; nonempty semantic `appearance`/`signature_features`.
- `expected_return`: exactly L2 keys/types and identical mapping keys, explicit host-enriched source/serialization/optional-empty handling; no artificial metadata controls.
- `widget_requirements`: four nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`, consistent with profile, no extra gates.
- `safety`: `allow_html: false`, `allow_script: false`; `runtime` only approved available host_artifact_canvas capabilities/pinned libraries; optional plugin-relative `reference_assets` design-time only.

Validate exact skill/path/planner/gap/goal/edge/returns/state/artifact/runtime. Send `l4-collage-authoring-renderer`. Failure: `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, `return_to: l1-collage-authoring-core`; bypass L4 without substitution.

## Workflow End Authority

All outcomes to `l1-collage-authoring-core`; only L1 merges state or emits `decision: end`.