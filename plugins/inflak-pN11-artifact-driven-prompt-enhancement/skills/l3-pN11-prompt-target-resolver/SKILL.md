---
name: l3-pN11-prompt-target-resolver
description: "Use when: L2 selects resolution of ambiguous prompt targets."
---

# L3 Designer — Prompt Target Resolver

## Layer & Role

Design only `prompt-target-resolver` / `prompt_target_resolver` on `artifact_canvas_widget`. No diagnosis, substitution, rendering or execution.

## Inputs

Require L2 selection/planner/gap/goal, chain/binding, exact return, prompt units/source spans, current artifact/revision, candidate stable IDs/labels/types and target evidence/uncertainty.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Resolve a materially ambiguous prompt reference. |
| Presented information | Exact source phrase and candidate objects with readable labels/evidence. |
| Supported interaction | Choose declared targets and inspect them in Canvas. |
| Feedback and constraints | Highlight exact IDs; show unresolved versus confirmed binding. |
| Submission and return | Map the unit-bound target decision to exactly L2's declared fields. |
| Presentation intent | Source phrase and live object context stay together in an anchored control. |

## Essential Constraints

Preserve exact prompt text/spans, `prompt_unit_id`, stable IDs, source revision and target provenance; never infer IDs from labels/proximity or decide targets for the user. Canvas selection focuses corresponding rows; row activation focuses exact bound objects. Respect selection cardinality and optional semantics. Unfinished values survive navigation. Selection is not instruction approval or patch authorization; no arbitrary JSON, markup, selectors, fabricated objects or source mutation.

Typical semantic return mapping (adapt keys to L2's current agent-interpreted interaction, retaining the binding evidence):

| Return field | Type and source/serialization |
| --- | --- |
| prompt_unit_id | Nonempty string copied unchanged from the bound ambiguous-reference unit. |
| resolved_object_ids | String array from explicit selection among the supplied stable scene IDs, never inferred from proximity. |
| replacement_label | String from the declared phrase editor/current user-confirmed phrase; preserve exact text. |
| action | String enum `continue`, `dismiss` from the invoked command. |

Continue requires the declared target cardinality and a complete replacement phrase; optional/empty handling follows L2 without inventing a referent. Dismiss preserves unfinished values but never resolves the unit. Source metadata is copied, not exposed as artificial controls; arrays remain arrays.

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

Validate exact skill/path, planner/gap/goal/edge, returns/state/artifact/runtime. Send `l4-pN11-widget-renderer`. Failure: `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, `return_to: l1-pN11-core-module`; no L4/substitution.

## Workflow End Authority

All outcomes re-enter `l1-pN11-core-module`; only L1 merges state or emits `decision: end`.
