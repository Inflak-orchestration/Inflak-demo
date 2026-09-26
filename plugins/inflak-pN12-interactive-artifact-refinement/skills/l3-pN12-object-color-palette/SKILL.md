---
name: l3-pN12-object-color-palette
description: "Use when: L2 selects the P12 object-bound color palette."
---

# L3 Designer — Object Color Palette

## Layer & Role

Design only `object-color-palette`, registry type `artifact_color_palette`, surface `artifact_canvas_widget`. No diagnosis, substitution, rendering or execution.

## Inputs

L2 selection/planner/gap/goal, chain/binding, exact returns; current artifact/revision, interaction_spec/default_target_ids, stable target capabilities and actual colors.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Recolor the prompt-bound objects without semantic asset generation. |
| Presented information | Highlighted targets, current baseline, 3–8 artifact-aware swatches and rationale. |
| Supported interaction | Supported channel/target, custom color, apply_together mapping, reset/Apply/regenerate/reject/dismiss. |
| Feedback and constraints | Immediate reversible host preview, visible swatches and contrast/legibility context. |
| Submission and return | Only Apply authorizes current-revision complete set_object_style operations. |
| Presentation intent | Anchored palette keeps selected objects visible, not a generic approval form. |

## Essential Constraints

Only supported `fill`, `stroke`, `text_color`; no unselected recoloring. Multi-target changes require explicit per-object mapping and `apply_together`. Current colors are evidence, suggestions are proposals. All colors appear in `display.color_previews`; code text auxiliary. Reset restores initial preview; Regenerate requests a new palette; Reject/Dismiss never mutate. Preserve exact declared stable IDs, channels, concrete values, interaction ID, revision and action. No SVG/CSS/selectors/URLs/data URIs or invented operations.

The existing planner-declared return maps `interaction_id: string` from the active spec, `artifact_id: string` and `base_revision: positive integer` from its current artifact binding, `target_colors: object[]` from explicit per-object color choices (`object_id`, supported `channel`, concrete `value`, all strings), `operations: object[]` from the corresponding declared typed preview, and `action: string enum apply/reset/regenerate/reject/dismiss` from the command. Preserve exact L2 keys/types and empty optional arrays on non-Apply returns; Apply requires complete target/color operations at that revision. Keep `apply_together` in its declared control semantics, not a newly invented top-level return key. Metadata is copied, never an extra control; only Apply authorizes mutation.

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
