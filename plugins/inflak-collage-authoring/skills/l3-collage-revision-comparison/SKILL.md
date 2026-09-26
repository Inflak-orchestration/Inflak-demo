---
name: l3-collage-revision-comparison
description: "Use when: L2 selects actual SVG revision comparison."
---

# L3 Designer — SVG Revision Comparison

## Layer & Role

Design only `collage-revision-comparison` / `svg_revision_comparison` on `artifact_canvas_widget`. No diagnosis, substitution, rendering or execution.

## Inputs

L2 selection/planner/gap/goal, chain/binding, exact returns; same actual fileId, before_revision/after_revision, applied changes and validation. Require after_revision > before_revision.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Compare actual source and revised artifact before acceptance. |
| Presented information | Host-owned Before/After snapshots, changes and validation. |
| Supported interaction | Inspect, accept_revision or continue_editing. |
| Feedback and constraints | Exact revision identities and visible color swatches. |
| Submission and return | Map declared action to this actual revision pair. |
| Presentation intent | Host two-pane comparison, stacked at narrow widths. |

## Essential Constraints

For every displayed color, populate `display.color_previews` from actual values and require L4 to render a visible swatch with an accessible label; preserve domain bindings. Raw code text (HEX/RGB) is auxiliary, never the primary or only color preview.

Fixed return mapping is only `action: string enum accept_revision/continue_editing`, sourced from the explicit command. The actual source fileId and before/after revisions remain in the unchanged artifact binding, not extra return keys or editable metadata controls. Empty/missing action is invalid; dismissal follows the existing dismiss channel without synthesizing acceptance.

Preserve same fileId/exact revisions and `canvas_comparison` placement. Host owns both snapshots; no raw SVG/XML/data URI/selectors/scripts or fabricated result. Colors use `display.color_previews` `{value,label,role,revision}` with visible swatches. Comparison never applies a patch. Stale or missing snapshots fail instead of substituting another document/revision.

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
