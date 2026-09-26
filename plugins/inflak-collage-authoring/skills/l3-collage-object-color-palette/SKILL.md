---
name: l3-collage-object-color-palette
description: "Use when: L2 selects the unified SVG object palette."
---

# L3 Designer — SVG Object Palette

## Layer & Role

Design only `collage-object-color-palette` / `artifact_color_palette` on `artifact_canvas_widget`. No diagnosis, substitution, rendering or execution.

## Inputs

L2 selection/planner/gap/goal, chain/binding, exact return; actual artifact/revision, interaction_spec/default_target_ids, stable capabilities and current colors.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Recolor prompt-bound objects with visible local alternatives. |
| Presented information | Current colors, target labels, 3–8 artifact-aware swatches and rationale. |
| Supported interaction | Supported channel, custom color, explicit multi-target mapping/apply_together, reset/Apply/regenerate/reject/dismiss. |
| Feedback and constraints | Immediate reversible host preview and visible swatches with contrast context. |
| Submission and return | Only Apply authorizes complete current-revision set_object_style. |
| Presentation intent | Anchored palette keeps the target visible; color codes are auxiliary. |

## Essential Constraints

Only supported `fill`, `stroke`, `text_color`; current scene colors are evidence, suggestions are proposals. No unselected recolor; multiple targets require per-object mapping and explicit `apply_together`. Reset restores initial preview; Regenerate/Reject/Dismiss no mutation. Preserve declared IDs/channels/concrete values/interaction/revision/action and `display.color_previews`. No CSS/selectors/SVG/URLs/data URIs/invented operations.

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