---
name: l3-pN12-semantic-variant-review
description: "Use when: L2 selects materialized semantic variants for P12."
---

# L3 Designer — Semantic Variant Review

## Layer & Role

Design only `semantic-variant-review` / `semantic_variant_review` on `artifact_canvas_widget`. No diagnosis, substitution, rendering or execution.

## Inputs

L2 selection/planner/gap/goal, chain/binding, exact return; artifact/revision, interaction_spec, stable targets and already materialized same-session candidates/variants with real fileIds and provenance.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Compare concrete semantic results before committing. |
| Presented information | Materialized variants in intended artifact context and provenance. |
| Supported interaction | Variant choice, spec-declared placement, Apply/regenerate/reject/dismiss. |
| Feedback and constraints | Reversible Canvas preview and typed operation summary. |
| Submission and return | Apply returns one prepared operation plus declared placement adjustments. |
| Presentation intent | Contextual variant strip with real thumbnails, not proposed asset placeholders. |

## Essential Constraints

For every displayed color, populate `display.color_previews` from actual values and require L4 to render a visible swatch with an accessible label; preserve domain bindings. Raw code text (HEX/RGB) is auxiliary, never the primary or only color preview.

Preserve `interaction_id`, `candidate_id`, `variant_id`, `artifact_id`, `base_revision`, `operations`, `control_values`, `action: apply|regenerate|reject|dismiss` exactly. Apply uses planner-provided `add_cutout`, `replace_cutout_asset` or `remove_object`, never natural-language execution. Regenerate invalidates preview without changing artifact; Reject/Dismiss no mutation. SVG raster candidates require actual transparent pixels and session persistence. Colors use `display.color_previews` `{value,label,role,candidate_id}`. No generation/fetch/URL/data URI/SVG/invented asset IDs or iframe commit.

Fixed mapping: `interaction_id: string` from the active spec; `candidate_id: string` and `variant_id: string` from the selected supplied materialized variant; `artifact_id: string` and `base_revision: positive integer` from the current binding; `operations: object[]` from that variant's prepared typed operations plus declared placement adjustments; `control_values: object` from actual typed controls; `action: string enum apply/regenerate/reject/dismiss` from the command. Copy IDs/revision without extra metadata controls and serialize objects/arrays unchanged. Preserve declared empty/optional selections only on non-Apply outcomes; Apply requires complete current-revision operations and any necessary real candidate binding. No extra keys, invented candidates or implicit approval.

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

Validate exact skill/path/planner/gap/goal/edge/returns/state/artifact/runtime. Send `l4-pN12-widget-renderer`. Failure: `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, `return_to: l1-pN12-core-module`; bypass L4 without substitution.

## Workflow End Authority

All outcomes to `l1-pN12-core-module`; only L1 merges state or emits `decision: end`.
