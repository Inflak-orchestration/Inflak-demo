---
name: l3-pN10-object-suggestion-review
description: "Use when: L2 selects grounded P10 object suggestion decisions."
---

# L3 Designer — Object Suggestion Review

## Layer & Role

Design only `object-suggestion-review` / `object_suggestion_review` on `artifact_canvas_widget`. No diagnosis, substitution, rendering or execution.

## Inputs

Require L2 selection/planner/gap/goal, chain/binding, expected return, current artifact/revision, stable scene objects and complete suggestions with IDs, targets, objectives, operations, rationale, evidence and uncertainty.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Ground targets and collect explicit suggestion decisions. |
| Presented information | Suggestions, named targets, concrete changes and evidence/uncertainty. |
| Supported interaction | Accept, edit, reject and focus related source objects. |
| Feedback and constraints | Show proposed versus decided state; preserve unfinished edits during navigation. |
| Submission and return | Serialize `suggestion_decisions` and declared `action` by stable suggestion ID. |
| Presentation intent | Object-anchored review with synchronized Canvas and suggestion focus. |

## Essential Constraints

For every displayed color, populate `display.color_previews` from actual values and require L4 to render a visible swatch with an accessible label; preserve domain bindings. Raw code text (HEX/RGB) is auxiliary, never the primary or only color preview.

Preserve `suggestion_id`, `object_ids`, `primary_object_id`, source revision, decision order and provenance; accepted/edited/rejected are explicit user decisions, not recommendation defaults. Keep rejected history, no silent dropping. Object selection focuses related suggestions; activating a suggestion focuses its exact bound targets and anchors beside primary target. Missing target evidence stays unresolved. Semantic decisions do not patch the source or replace final concrete Aug authorization. No invented IDs, markup or selector operations.

## Output and Handoff

Complete local contract; no external read or success `handoff_type`:

- Identity: nonempty exact `selected_widget_id`, instance `widget_id`, registry `widget_type`/`surface`, `planner_id`, contextual `purpose`, unchanged `interaction_goal`.
- `iai`: unchanged L2 `chain_id`, `gap_type`, `reason`, `source_nodes`, `maps_to_edge`, `target_node`; named chain/meaningful reason, edge source in sources, destination=target and allowed `state_update_target`; deterministic L1 `merge_strategy`; `next_planner_action: "re-enter Layer 1"`.
- `display`: actual source/revision/values/unresolved status; no invented evidence/defaults/assets/previews/outcomes; preserve `artifact_binding`/`placement`.
- `controls`: unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty declared `return_keys`, typed/limit/source/edit `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`, nonempty resolvable `content` records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`); nonempty interaction `actions`/`feedback`; submission nonempty `label`/`preconditions`/exact `return_mapping`; nonempty semantic `appearance`/`signature_features`.
- `expected_return`: under `return_mode: agent_interpreted`, preserve exactly L2 keys/types for this contextual interaction and identical mapping keys with actual source/serialization/optional-empty handling. Domain field names are guidance, not fixed registry keys; retain user evidence for L1 interpretation, no artificial metadata controls or inferred consent.
- `widget_requirements`: four nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`, consistent with profile, no extra gates.
- `safety`: `allow_html: false`, `allow_script: false`; optional `runtime` approved available capabilities/pinned libraries only; optional plugin-relative `reference_assets` design-time only.

Validate exact skill/path, planner/gap/goal/edge, returns/state/artifact/runtime. Send `l4-pN10-widget-renderer`. Failure: `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, `return_to: l1-pN10-core-module`; no L4/substitution.

## Workflow End Authority

All outcomes re-enter `l1-pN10-core-module`; only L1 merges state or emits `decision: end`.
