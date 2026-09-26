---
name: l3-pN11-prompt-object-alignment
description: "Use when: L2 selects prompt-to-object alignment review."
---

# L3 Designer — Prompt Object Alignment

## Layer & Role

Design only `prompt-object-alignment` / `prompt_object_alignment` on `artifact_canvas_widget`. No diagnosis, substitution, rendering or execution.

## Inputs

Require L2 selection/planner/gap/goal, chain/binding, exact return, source prompt/spans, prompt units, current artifact/revision, stable objects and proposed/current alignments with role/evidence/provenance.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Make prompt units and their object roles explicit. |
| Presented information | Source phrases, object labels/IDs, alignments and uncertainty. |
| Supported interaction | Review or correct only declared unit/object bindings and roles. |
| Feedback and constraints | Bidirectional Canvas/row focus and visible confirmed/unresolved status. |
| Submission and return | Serialize exact L2-declared alignment fields with source-unit identity. |
| Presentation intent | Grounded compact alignment view beside the live artifact. |

## Essential Constraints

Preserve prompt text/spans, unit IDs, stable object IDs, source revision, relation roles and field provenance. Do not replace L2's edge/state target, fabricate targets, silently approve model suggestions or drop unfinished edits on navigation. Activating a row focuses its actual objects; Canvas selection focuses associated units. Alignment is semantic evidence, not approval of concrete operations or source mutation. No arbitrary JSON, raw SVG, selectors or execution code.

Typical semantic return mapping (adapt keys to L2's current agent-interpreted interaction, retaining the binding evidence):

| Return field | Type and source/serialization |
| --- | --- |
| prompt_unit_id | Nonempty string copied unchanged from the bound source prompt unit; no editable metadata control. |
| object_ids | String array of explicitly selected current stable object IDs; serialize as an array, not labels. |
| resolution | String enum `confirmed`, `not_present`, `skip` from the explicit resolution control. |
| action | String enum `continue`, `dismiss` from the invoked command. |

Confirmed alignment requires its declared nonempty selection. `not_present`/`skip` may return an empty object array; dismissal preserves declared unfinished values without implying confirmation. Do not add a provenance key: L1 derives provenance from the actual user return bound to this unit/source/revision.

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
