---
name: l3-collage-object-grounding
description: "Use when: L2 selects stable SVG targets, relation endpoints or preserve constraints."
---

# L3 Designer — SVG Object Grounding

## Layer & Role

Design only `collage-object-grounding` with exact registry type/surface. No diagnosis, substitution, rendering or execution.

## Inputs

L2 selection/planner/gap/goal, chain/binding, exact return; current artifact/revision, proposal identity, stable scene objects/labels/types, target hypotheses and relation/constraint values.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Ground the supplied proposal in explicit objects and roles. |
| Presented information | Proposal, candidate targets, endpoints and preserve constraints. |
| Supported interaction | Declared stable target/endpoint selection and role/constraint editing. |
| Feedback and constraints | Synchronized Canvas/list focus; unresolved versus user-confirmed bindings. |
| Submission and return | Exact declared target/relation values with proposal/source identity. |
| Presentation intent | Anchored object-context editor with readable labels, not bare IDs. |

## Essential Constraints

Use only supplied current stable IDs; reject unknown endpoints/self-relations/unsupported roles or constraints. Preserve source revision and proposal identity. Do not infer targets, inspect markup or change L2 edge/state target for relation gaps. User-selected provenance remains distinct from hypotheses; preserve unfinished values. Grounding is not a patch or execution authorization.

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
