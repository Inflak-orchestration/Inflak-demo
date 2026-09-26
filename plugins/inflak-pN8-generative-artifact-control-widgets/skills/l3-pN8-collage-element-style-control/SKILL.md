---
name: l3-pN8-collage-element-style-control
description: "Use when: L2 selects deterministic native P8 SVG object styling."
---

# L3 Designer — Native Collage Element Style

## Layer & Role

Design only `pN8-collage-element-style-control`, type `collage_element_style_control`, surface `artifact_canvas_widget`. Interaction Pathway only; never diagnose, substitute, render or execute.

## Inputs

Read L2 selection/planner/gap/goal, chain/binding, exact return and L1 target. Require current artifact/revision, stable object and canonical `presentation` with `capabilities.style: true`. Preserve real current values and supported style channels.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Edit native presentation without rasterization. |
| Presented information | Target label, current fill/stroke, stroke width and opacity. |
| Supported interaction | Supported color/number controls, reversible preview, reset, Apply and dismiss. |
| Feedback and constraints | Show color swatches and typed validation beside changed properties. |
| Submission and return | Map only changed properties to one `set_object_style`. |
| Presentation intent | Accessible compact object-anchored inspector with live artifact context. |

## Essential Constraints

For every displayed color, populate `display.color_previews` from actual values and require L4 to render a visible swatch with an accessible label; preserve domain bindings. Raw code text (HEX/RGB) is auxiliary, never the primary or only color preview.

Stroke width is 0–1000 and opacity 0–1; preserve narrower actual capability limits. Include every current/preview/selected fill/stroke in `display.color_previews` as `{value,label,role}`; swatches are primary, code text auxiliary. Apply returns declared `artifact_id`, `base_revision`, `operations` with stable `object_id` and nonempty supported `style`, omitting unchanged fields. Host preview is reversible and is not a commit. No unsupported properties, `url(...)`, CSS selectors, SVG rewriting, image generation, network or L3 implementation code.

## Output and Handoff

Complete local contract; no success `handoff_type` or external schema read:

- Identity: nonempty exact `selected_widget_id`, instance `widget_id`, registry `widget_type`/`surface`, `planner_id`, contextual `purpose`, unchanged `interaction_goal`.
- `iai`: unchanged L2 `chain_id`, `gap_type`, binding `reason`, `source_nodes`, `maps_to_edge`, `target_node`; named chain, meaningful reason, edge source in sources, destination equal to target and allowed `state_update_target`; deterministic L1 `merge_strategy`, `next_planner_action: "re-enter Layer 1"`.
- `display`: grounded values, actual sources/revision and unresolved status; no invented defaults/evidence/assets/previews/outcomes. Preserve host artifact binding and placement.
- `controls`: unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty declared `return_keys`, applicable typed/limit/source/edit `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`, nonempty resolvable `content` records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`); `interaction` has nonempty `actions`/`feedback`, `submission` with nonempty `label`, `preconditions`, exact `return_mapping`; nonempty semantic `appearance` and `signature_features`.
- `expected_return`: exactly L2 keys/types and identical submission mapping keys; each mapping names actual source and serialization including optional/empty semantics. Derived metadata needs no artificial control.
- `widget_requirements`: nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`; consistent with profile, no extra gates.
- `safety`: `allow_html: false`, `allow_script: false`; optional `runtime` only approved available capabilities/pinned libraries; optional plugin-relative `reference_assets` are design-time, not runtime assets.

Validate exact skill/path, planner/gap/goal/edge, returns/state target and artifact/runtime support. Send to `l4-pN8-widget-renderer`. Failure: `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, `return_to: l1-pN8-core-module`; no L4 or substitute.

## Workflow End Authority

All outcomes re-enter `l1-pN8-core-module`. Only L1 merges canonical state or emits `decision: end`; a style change is nonterminal.
