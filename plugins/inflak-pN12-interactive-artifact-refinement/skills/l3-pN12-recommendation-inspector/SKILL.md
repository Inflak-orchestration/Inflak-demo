---
name: l3-pN12-recommendation-inspector
description: "Use when: L2 selects a prompt-and-scene-derived adaptive P12 interaction."
---

# L3 Designer — Adaptive Refinement Interaction

## Layer & Role

Design only `refinement-recommendation-inspector` / `adaptive_refinement_interaction` on `artifact_canvas_widget`. No diagnosis, substitution, rendering or execution.

## Inputs

L2 selection/planner/gap/goal, chain/binding, exact return; current artifact/revision, `interaction_spec` with interaction_id/prompt_span/default_target_ids/target_hypotheses/artifact_evidence/confidence/controls/preview_operations/return_schema/annotation.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Manipulate the concrete interaction derived from this prompt and scene. |
| Presented information | Generated initial result, bound targets, evidence/confidence and relevant alternatives. |
| Supported interaction | Spec controls, Apply/Regenerate/Reject; conditional target correction and adjustment. |
| Feedback and constraints | Reversible host preview, typed changes and incomplete-interaction warning. |
| Submission and return | Map exact interaction identity, action, stable targets and declared typed adjustments. |
| Presentation intent | Artifact-anchored adaptive controls, never empty picker or abstract approval. |

## Essential Constraints

For every displayed color, populate `display.color_previews` from actual values and require L4 to render a visible swatch with an accessible label; preserve domain bindings. Raw code text (HEX/RGB) is auxiliary, never the primary or only color preview.

Missing preview/execution values remain incomplete and disable Apply, never placeholders. Use only spec-declared capability-compatible controls. Correct target only with alternatives; free Canvas selection only after `None of these` and only host-reported IDs. Adjust preserves default targets and unchanged generated values. Return `interaction_id`, `action: apply|adjust|regenerate|correct|reject|dismiss`, `target_object_ids`, `operations`, `control_values`, optional `selected_alternative_rank`/`new_constraint` exactly as L2 declares. Only Apply authorizes spec preview operations plus explicit typed adjustments; all other actions nonmutating. Colors use `display.color_previews` `{value,label,role,interaction_id}`. Host annotations transient; no SVG/selectors/invented IDs/code.

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
