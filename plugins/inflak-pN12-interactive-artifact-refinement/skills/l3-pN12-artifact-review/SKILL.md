---
name: l3-pN12-artifact-review
description: "Use when: L2 selects review of the actual P12 refinement result."
---

# L3 Designer — Refined Artifact Review

## Layer & Role

Design only `registry_id: refined-artifact-review`, with `selected_widget_id: refined-artifact-review`, registry type `refined_artifact_review` and surface `artifact_canvas_widget`. No diagnosis, substitution, rendering or execution.

## Inputs

L2 selection/planner/gap/goal, chain/binding, exact returns; actual artifact/revision, applied changes, validation, remaining issues and prior interaction provenance.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Inspect actual refined output and decide acceptance or follow-up. |
| Presented information | Live artwork, revision, changes, validation and remaining issues. |
| Supported interaction | Exact declared accept/continue/revise/dismiss actions and follow-up text. |
| Feedback and constraints | Bind decision to current revision, visibly separate unresolved issues. |
| Submission and return | Map declared action/revision/follow-up fields without inventing success. |
| Presentation intent | Concise artifact review keeps the actual SVG visible. |

## Essential Constraints

For every displayed color, populate `display.color_previews` from actual values and require L4 to render a visible swatch with an accessible label; preserve domain bindings. Raw code text (HEX/RGB) is auxiliary, never the primary or only color preview.

Accept is evidence only, not completion here. No extra confirmation checkbox or stage. Preserve stable source/object IDs, revision, actual validation and expected-return types. Color summaries use `display.color_previews` with visible swatches. Never patch, fabricate revised images, hide errors or interpret dismissal as successful acceptance.

The existing planner-declared schema maps `revision: positive integer` unchanged from the actual reviewed artifact, `decision: string enum accept/continue/revise/dismiss` from the explicit review command, `selected_issue_id: string` from an actual supplied issue, and `revision_request: string` / `freeform_note: string` from their declared text controls. Preserve empty optional issue/follow-up strings; do not invent an issue or replace `decision` with an extra `action` field. Copy metadata without artificial controls, serialize exact L2 keys/types, and bind any acceptance only to the displayed revision.

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
