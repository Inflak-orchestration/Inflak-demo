---
name: l3-pN9-analysis-lens-chips
description: "Use when: L2 selects a grounded analysis objective or conditional narrowing."
---

# L3 Designer — Analysis Lens Chips

## Layer & Role

Design only `analysis-lens-chips` / `analysis_lens_chips` on `conversation_widget`. No diagnosis, substitution, rendering or execution.

## Inputs

L2 selection/planner/gap/goal, chain/binding, exact returns; source profile, current choices and artifact-grounded suggestion groups with stable IDs/rationale/support/additional-data requirements.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Resolve the selected objective or material scope deficit. |
| Presented information | Source evidence before analysis-focus/scope/depth/output choices. |
| Supported interaction | One primary objective, optional secondary lenses, conditional narrowing, custom direction and edits. |
| Feedback and constraints | Recommendations emphasized but not preselected; show support/data requirements. |
| Submission and return | Map stable selected IDs, edits, text and action exactly. |
| Presentation intent | Compact grouped choices and accessible current-selection summary. |

## Essential Constraints

Validate `analysis_direction_gap` on `G→I` or narrowing on `I→T` as L2 supplied; do not change the binding. Require one actual user-selected primary objective; reuse submitted selection, never recommendation-as-selection. Narrowing depends on primary objective. Strings `primary_objective_id`, `depth_id`, `output_format_id`, `custom_direction`, `action`, `freeform_note`; arrays `secondary_lens_ids`, `scope_ids`, `removed_or_edited_suggestions`. Actions continue/edit_selection/start_over or declared host dismissal. No invented data, extra approval checkbox or reanalysis here.

## Output and Handoff

Eight local parts; no external read/success `handoff_type`:

- Identity: nonempty exact `selected_widget_id`, instance `widget_id`, registry `widget_type`/`surface`, `planner_id`, contextual `purpose`, unchanged `interaction_goal`.
- `iai`: unchanged L2 `chain_id`, `gap_type`, `reason`, `source_nodes`, `maps_to_edge`, `target_node`; named chain/meaningful reason, edge source in sources, destination=target and allowed `state_update_target`; deterministic L1 `merge_strategy`, `next_planner_action: "re-enter Layer 1"`.
- `display`: actual source/values/unresolved status; no invented evidence/defaults/assets/previews/outcomes.
- `controls`: unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty declared `return_keys`, typed/limit/source/edit `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`; nonempty resolvable `content` records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`); nonempty interaction `actions`/`feedback`; submission nonempty `label`/`preconditions`/exact `return_mapping`; nonempty semantic `appearance`/`signature_features`.
- `expected_return`: exactly L2 keys/types and identical mapping keys, actual source/serialization/optional-empty handling; no artificial metadata controls.
- `widget_requirements`: four nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`, consistent with profile, no extra gates.
- `safety`: `allow_html: false`, `allow_script: false`; optional `runtime` approved available capabilities/pinned libraries only; optional plugin-relative `reference_assets` design-time only.

Validate exact skill/path/planner/gap/goal/edge/returns/state/artifact/runtime. Send `l4-pN9-widget-renderer`. Failure: `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, `return_to: l1-pN9-core-module`; bypass L4 without substitution.

## Workflow End Authority

All outcomes to `l1-pN9-core-module`; only L1 merges state or emits `decision: end`.
