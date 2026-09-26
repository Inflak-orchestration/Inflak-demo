---
name: l3-pN8-collage-visual-style-control
description: "Use when: L2 selects prepared whole-collage visual presets in P8."
---

# L3 Designer — Collage Visual Style

## Layer & Role

Design only `pN8-collage-visual-style-control`, type `collage_visual_style_control`, surface `artifact_canvas_widget`. Interaction Pathway only; do not diagnose, substitute, render or execute.

## Inputs

Read L2 selection/planner/gap/goal, chain/binding, exact return and L1 target. Require current artifact/revision and 2–4 complete `authoring_bundle.visual_style_presets` with actual labels, rationales, affected IDs, swatches, operations and prepared assets.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Compare prepared visual directions without another AI call. |
| Presented information | Live collage, active preset, affected objects, swatches and rationale. |
| Supported interaction | Preset selection, reversible preview, reset, Apply/dismiss. |
| Feedback and constraints | Preview every preset operation together and distinguish pending from active. |
| Submission and return | Return selected preset ID and all its unchanged operations atomically. |
| Presentation intent | Compact visual strip, not generic style categories or code text. |

## Essential Constraints

For every displayed color, populate `display.color_previews` from actual values and require L4 to render a visible swatch with an accessible label; preserve domain bindings. Raw code text (HEX/RGB) is auxiliary, never the primary or only color preview.

Allow only `replace_cutout_asset`, `update_text`, `set_canvas_style`. Replacement fileIds must already be current-session, alpha-validated bundle assets. Every preset/operation color appears in `display.color_previews` as `{value,label,role,preset_id}` with visible swatches. Apply returns declared `artifact_id`, `base_revision`, `active_style_preset_id`, `operations` in original order. Never split a preset across revisions. No missing-variant synthesis/fetch, generation, arbitrary style code or commit before Apply; host owns reversible preview and patch.

## Output and Handoff

Local eight-part contract; no success `handoff_type` or external schema read:

- Identity: nonempty exact `selected_widget_id`, instance `widget_id`, registry `widget_type`/`surface`, `planner_id`, contextual `purpose`, unchanged `interaction_goal`.
- `iai`: unchanged L2 `chain_id`, `gap_type`, binding `reason`, `source_nodes`, `maps_to_edge`, `target_node`; named chain/meaningful reason, edge source in sources, destination equals target and allowed `state_update_target`; deterministic L1 `merge_strategy`, `next_planner_action: "re-enter Layer 1"`.
- `display`: grounded values, actual source/revision and unresolved status; no invented evidence/defaults/assets/previews/outcomes. Preserve host artifact binding/placement.
- `controls`: unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty declared `return_keys`, typed/limit/source/edit `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`; nonempty resolvable `content` records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`); nonempty interaction `actions`/`feedback`; `submission` with nonempty `label`, `preconditions`, exact `return_mapping`; nonempty semantic `appearance` and `signature_features`.
- `expected_return`: exactly L2 keys/types and identical submission mapping keys, each with actual source/serialization and optional/empty handling; no artificial controls for derived metadata.
- `widget_requirements`: four nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`, consistent with profile and no extra gates.
- `safety`: `allow_html: false`, `allow_script: false`, `allow_network: false`, `allow_generation: false`; optional `runtime` only approved available capabilities/pinned libraries; optional plugin-relative `reference_assets` design-time only.

Validate exact skill/path, planner/gap/goal/edge, returns/state target and artifact/runtime support. Send to `l4-pN8-widget-renderer`. Failure: `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, `return_to: l1-pN8-core-module`; no L4 or substitute.

## Workflow End Authority

Every outcome re-enters `l1-pN8-core-module`; only L1 merges canonical state or emits `decision: end`.
