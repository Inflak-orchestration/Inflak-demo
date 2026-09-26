---
name: l3-pN8-collage-review
description: "Use when: L2 selects review of the current P8 collage and prepared authoring options."
---

# L3 Designer — Collage Review

## Layer & Role

Design only `pN8-collage-review`, type `collage_review`, surface `artifact_canvas_widget`. Interaction Pathway only; no diagnosis, substitution, rendering, generation or completion.

## Inputs

Read L2 selection/planner/gap/goal, chain/binding, exact return and L1 target. Require actual current collage/revision, object count, canvas dimensions, comparison evidence where applicable and remaining prepared authoring options.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Accept this artifact or scope continued work. |
| Presented information | Inspectable live collage, revision, object count, size and remaining options. |
| Supported interaction | Accept, continue prepared editing, explicit new-generation request and dismiss. |
| Feedback and constraints | Distinguish prepared editing from new generation and keep current revision visible. |
| Submission and return | Map the registry's fixed `decision` and `revision_request` string fields exactly to L2; `revision_request` is nonempty for new generation and may be empty for accept/continue editing. |
| Presentation intent | Concise review beside visible artwork; download remains a host Canvas action. |

## Essential Constraints

`decision` uses declared `accept|continue_editing|request_new_generation`. New generation requires an explicit submitted nonempty request outside the prepared bundle; merely choosing a prepared option never invokes AI. Include summary/options/revision colors in `display.color_previews` as `{value,label,role,revision}` with visible swatches. Accept is evidence for L1, not completion here; no checkbox or extra acceptance stage, invented artifact, patch, markup or UI code.

## Output and Handoff

Local eight-part contract; no success `handoff_type` or external schema read:

- Identity: nonempty exact `selected_widget_id`, instance `widget_id`, registry `widget_type`/`surface`, `planner_id`, contextual `purpose`, unchanged `interaction_goal`.
- `iai`: unchanged L2 `chain_id`, `gap_type`, binding `reason`, `source_nodes`, `maps_to_edge`, `target_node`; named chain/meaningful reason, edge source in sources, destination equals target and allowed `state_update_target`; deterministic L1 `merge_strategy`, `next_planner_action: "re-enter Layer 1"`.
- `display`: grounded values, actual source/revision and unresolved status; no invented evidence/defaults/assets/previews/outcomes. Preserve host artifact binding/placement.
- `controls`: unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty declared `return_keys`, typed/limit/source/edit `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`; nonempty resolvable `content` records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`); nonempty interaction `actions`/`feedback`; `submission` with nonempty `label`, `preconditions`, exact `return_mapping`; nonempty semantic `appearance` and `signature_features`.
- `expected_return`: exactly L2 keys/types and identical submission mapping keys, each with actual source/serialization and optional/empty handling; no artificial controls for derived metadata.
- `widget_requirements`: four nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`, consistent with profile and no extra gates.
- `safety`: `allow_html: false`, `allow_script: false`, `allow_generation: false`; optional `runtime` only approved available capabilities/pinned libraries; optional plugin-relative `reference_assets` design-time only.

Validate exact skill/path, planner/gap/goal/edge, returns/state target and artifact/runtime support. Send to `l4-pN8-widget-renderer`. Failure: `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, `return_to: l1-pN8-core-module`; no L4 or substitute.

## Workflow End Authority

Every outcome re-enters `l1-pN8-core-module`; only L1 merges canonical state or emits `decision: end` against current valid acceptance.
