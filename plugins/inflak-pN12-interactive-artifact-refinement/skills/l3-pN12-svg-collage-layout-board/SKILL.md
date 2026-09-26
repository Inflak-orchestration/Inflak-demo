---
name: l3-pN12-svg-collage-layout-board
description: "Use when: L2 selects the P12 artifact-grounded spatial layout board."
---

# L3 Designer — SVG Collage Layout Board

## Layer & Role

Design only `svg-collage-layout-board` / `svg_collage_layout_board` on `artifact_canvas_widget`. No diagnosis, substitution, rendering or execution.

## Inputs

L2 selection/planner/gap/goal, chain/binding, exact return; current artifact_scene/revision, interaction_spec, actual canvas dimensions/coordinate_space, stable items with label/type/transform/aspect/z_order/visibility/lock/capabilities and declared regions.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Arrange actual scene objects and specify requested spatial regions. |
| Presented information | Live SVG stage, stable labeled objects, region bounds and current geometry. |
| Supported interaction | Capability-limited drag/four-corner resize/rotate/align/distribute/snap/layers and region assignment. |
| Feedback and constraints | Synchronized Canvas/list, guides/grid/center/safe bounds, undo/redo/reset and before-after preview. |
| Submission and return | Apply submits action/interaction ID; host supplies authoritative changed typed geometry. |
| Presentation intent | Real spatial board dominates, never blank cards or numeric-fields-only. |

## Essential Constraints

All geometry stays in artifact coordinates under zoom. Locked objects remain visible and immovable. Regions have stable IDs/bounds/labels/accepted types/assignments; labels never become SVG text without separately authorized typed text operations. Host owns draft transforms and serialization. Apply returns changed `set_transform` and changed `set_order` only, enriched by host with artifact/revision; iframe never reconstructs geometry. Reset keeps widget open; Regenerate/Reject/Dismiss submit no draft operations and never mutate. Reject stale revisions, unknown IDs, unsupported transforms and bounds violations. L4 implements host events/reset/submit API; L3 specifies semantics only.

## Output and Handoff

Eight local parts; no external read/success `handoff_type`:

- Identity: nonempty exact `selected_widget_id`, instance `widget_id`, registry `widget_type`/`surface`, `planner_id`, contextual `purpose`, unchanged `interaction_goal`.
- `iai`: unchanged L2 `chain_id`, `gap_type`, `reason`, `source_nodes`, `maps_to_edge`, `target_node`; named chain/meaningful reason, edge source in sources, destination=target and allowed `state_update_target`; deterministic L1 `merge_strategy`, `next_planner_action: "re-enter Layer 1"`.
- `display`: actual sources/revisions/values/unresolved status; no invented evidence/defaults/assets/previews/outcomes; preserve `artifact_binding`/`placement`.
- `controls`: unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty declared `return_keys`, typed/limit/source/edit `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`; nonempty resolvable `content` records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`); nonempty interaction `actions`/`feedback`; submission nonempty `label`/`preconditions`/exact `return_mapping`; nonempty semantic `appearance`/`signature_features`.
- `expected_return`: exactly L2 keys/types and identical mapping keys, explicit host-enriched actual source/serialization/optional-empty handling; no artificial metadata controls.
- `widget_requirements`: four nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`, consistent with profile, no extra gates.
- `safety`: `allow_html: false`, `allow_script: false`; `runtime` only approved available host_artifact_canvas capabilities/pinned libraries; optional plugin-relative `reference_assets` design-time only.

Validate exact skill/path/planner/gap/goal/edge/returns/state/artifact/runtime. Send `l4-pN12-widget-renderer`. Failure: `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, `return_to: l1-pN12-core-module`; bypass L4 without substitution.

## Workflow End Authority

All outcomes to `l1-pN12-core-module`; only L1 merges state or emits `decision: end`.
