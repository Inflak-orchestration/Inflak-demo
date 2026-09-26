---
name: l3-pN8-collage-text-control
description: "Use when: L2 selects prepared copy and native typography controls for P8."
---

# L3 Designer — Collage Text

## Layer & Role

Design only `pN8-collage-text-control`, type `collage_text_control`, surface `artifact_canvas_widget`. Interaction Pathway only; no diagnosis, substitution, rendering or execution.

## Inputs

Read L2 selection/planner/gap/goal, chain/binding, exact return and L1 target. Require artifact/revision, bound text ID or authorized new stable ID, current content/style/transform and prepared `authoring_bundle.text_authoring_options[object_id]`.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Choose prepared copy/typography or edit the bound text directly. |
| Presented information | Actual text, copy options, typography presets and current properties. |
| Supported interaction | Text editing, safe font family/weight/size/fill/alignment, preview, Apply/dismiss. |
| Feedback and constraints | Live host preview, font samples, color swatches and typed validation. |
| Submission and return | One authorized `add_text` or `update_text`, not regenerated artwork. |
| Presentation intent | Editorial inspector keeps text and its artifact placement visible. |

## Essential Constraints

For every displayed color, populate `display.color_previews` from actual values and require L4 to render a visible swatch with an accessible label; preserve domain bindings. Raw code text (HEX/RGB) is auxiliary, never the primary or only color preview.

Weight options 100–900 in steps of 100; font size 8–512 subject to actual capabilities; `text_anchor: start|middle|end`. Preserve transform context and safe actual font choices. Include every current/option/preview/selected text color in `display.color_previews` as `{value,label,role}`; code text is auxiliary. Existing ID is required for updates; new ID must be collision-free and creation authorized. Apply alone submits declared `artifact_id`, `base_revision`, typed `operations`; host commits. No on-click generation, fabricated options, raw SVG, selectors or L3 code.

## Output and Handoff

Local eight-part contract; no success `handoff_type` or external schema read:

- Identity: nonempty exact `selected_widget_id`, instance `widget_id`, registry `widget_type`/`surface`, `planner_id`, contextual `purpose`, unchanged `interaction_goal`.
- `iai`: unchanged L2 `chain_id`, `gap_type`, binding `reason`, `source_nodes`, `maps_to_edge`, `target_node`; named chain/meaningful reason, edge source in sources, destination equals target and allowed `state_update_target`; deterministic L1 `merge_strategy`, `next_planner_action: "re-enter Layer 1"`.
- `display`: grounded values, actual source/revision and unresolved status; no invented evidence/defaults/assets/previews/outcomes. Preserve host artifact binding/placement.
- `controls`: unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty declared `return_keys`, typed/limit/source/edit `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`; nonempty resolvable `content` records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`); nonempty interaction `actions`/`feedback`; `submission` with nonempty `label`, `preconditions`, exact `return_mapping`; nonempty semantic `appearance` and `signature_features`.
- `expected_return`: exactly L2 keys/types and identical submission mapping keys, each with actual source/serialization and optional/empty handling; no artificial controls for derived metadata.
- `widget_requirements`: four nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`, consistent with profile and no extra gates.
- `safety`: `allow_html: false`, `allow_script: false`; optional `runtime` only approved available capabilities/pinned libraries; optional plugin-relative `reference_assets` design-time only.

Validate exact skill/path, planner/gap/goal/edge, returns/state target and artifact/runtime support. Send to `l4-pN8-widget-renderer`. Failure: `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, `return_to: l1-pN8-core-module`; no L4 or substitute.

## Workflow End Authority

Every outcome re-enters `l1-pN8-core-module`; only L1 merges canonical state or emits `decision: end`.
