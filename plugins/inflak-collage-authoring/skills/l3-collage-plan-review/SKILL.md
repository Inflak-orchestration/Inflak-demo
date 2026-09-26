---
name: l3-collage-plan-review
description: "Use when: L2 selects provenance-aware SVG Aug review."
---

# L3 Designer — SVG Plan Review

## Layer & Role

Design only `collage-plan-review` with exact registry type/surface. No diagnosis, substitution, rendering or execution.

## Inputs

L2 selection/planner/gap/goal, chain/binding, exact returns; analyze/ground_prompt augmented intent, actual source/revision, current draft hash, operations/constraints, decisions and provenance.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Confirm the current complete grounded Aug. |
| Presented information | Readable intent, stable targets, changes/preserve constraints and provenance. |
| Supported interaction | Declared confirm/edit/reject/dismiss values. |
| Feedback and constraints | Missing/uncertain values explicit; stale hashes cannot be accepted. |
| Submission and return | Map exact instruction/draft decision fields to current source. |
| Presentation intent | Artifact-grounded review with reachable primary action. |

## Essential Constraints

For every displayed color, populate `display.color_previews` from actual values and require L4 to render a visible swatch with an accessible label; preserve domain bindings. Raw code text (HEX/RGB) is auxiliary, never the primary or only color preview.

Retain exact source IDs/revision/hash and complete decision/provenance history. Proposed values are not user confirmation. Only complete displayed Aug may be confirmed; no new approval checkbox or second confirmation. No export/patch here, no source rewriting, invented targets or omission of rejected/uncertain evidence. L1 receives the return before L2 chooses direct execution.

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
