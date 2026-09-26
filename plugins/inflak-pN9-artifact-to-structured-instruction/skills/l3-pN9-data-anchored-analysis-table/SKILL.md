---
name: l3-pN9-data-anchored-analysis-table
description: "Use when: L2 selects a CSV-backed table that binds analysis recommendations to exact rows and fields."
---

# L3 Designer — Data-Anchored Analysis Table

## Layer & Role

Design only `data-anchored-analysis-table` / `data_anchored_analysis_table` on `conversation_widget`. Transform L2-supplied tabular evidence and recommendations into one precise interaction contract; do not diagnose a different gap, substitute another widget, calculate new findings, render HTML, or execute analysis.

## Inputs

Consume L2 selection/planner/gap/goal, named chain, binding, exact expected return and L1 target; validate registry, runtime, source artifact, current selection, and a bounded dataset view. Require a stable `dataset_id`, ordered column records, rows with stable `row_id`, total/visible row counts, active filters, and recommendations whose evidence bindings name existing row IDs and fields. Never infer bindings from display position.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Let the analyst verify recommendation evidence in the CSV table, refine its exact data scope, and select one primary analysis direction. |
| Presented information | Sticky field headers, bounded rows, source identity, filter/truncation status, recommendation labels, rationale, support, evidence boundaries, and explicit row/field bindings. |
| Supported interaction | Sort/filter without changing identity; focus a recommendation to highlight and reveal its cells; select rows/fields to refine scope; choose one primary and optional secondary recommendations; edit a custom direction. |
| Feedback and constraints | Keep non-bound cells readable, announce hidden bound rows, distinguish selection from recommendation, and block submission when bindings are stale, missing, or outside the supplied dataset view. |
| Submission and return | Map stable recommendation IDs, row IDs, field names, filter state, comparison groups, edits, action, and note exactly; never return visual row indexes. |
| Presentation intent | A dense data table is the primary surface, with compact inline recommendation callouts and a persistent analysis-instruction summary rather than detached suggestion cards. |

## Essential Constraints

- Accept `analysis_direction_gap` on `G→I` or `progressive_narrowing_gap` on `I→T` exactly as L2 supplied. This widget is eligible only when `data_inventory.mode` is `machine_readable` or when `confirmed_rows` include stable row IDs and confirmed field values.
- Each column record has stable `field`, human `label`, declared `data_type`, and provenance. Each row has a stable `row_id`; sorting, filtering, pagination, and virtualization preserve that identity. Never use visible row number as evidence identity.
- Each recommendation has stable `recommendation_id`, label, objective, rationale, support, additional-data requirement, and `evidence_bindings`. Every binding names `dataset_id`, nonempty `row_ids`, nonempty `fields`, and an evidence boundary. Reject unknown IDs/fields, empty bindings, duplicate recommendation IDs, or model-estimated cells.
- Hover or keyboard focus on a recommendation highlights all bound cells and scrolls the first bound row into view without selecting it. Activating a recommendation selects it and reveals an inline detail directly below the nearest bound row; it does not submit. Selecting cells or rows updates the scoped recommendation preview but never rewrites source values.
- Keep table headers visible, use a labeled horizontal table viewport, support keyboard navigation and screen-reader announcements, and expose the same evidence through text rather than color alone. If filtering hides bound rows, show the hidden count and provide a reveal action; never silently narrow evidence.
- Require one actual user-selected `primary_recommendation_id`; recommendations may be visually emphasized but never preselected. Optional secondary IDs must differ from the primary. `selected_row_ids`, `selected_fields`, and `comparison_groups` must resolve against supplied data and remain traceable after sorting/filtering.
- Return strings `primary_recommendation_id`, `custom_direction`, `action`, `freeform_note`; arrays `secondary_recommendation_ids`, `selected_row_ids`, `selected_fields`, `comparison_groups`, `recommendation_edits`; object `filter_state`. Actions are `continue|edit_recommendations|start_over|dismiss`. No invented data, causal claim, hidden mutation, task execution, or extra confirmation checkbox.

## Output and Handoff

Emit exactly eight local parts; no external read or success `handoff_type`:

- Identity: nonempty exact registered `selected_widget_id`, instance `widget_id`, registry `widget_type` and `surface`, `planner_id`, contextual `purpose`, and unchanged `interaction_goal` matching L2.
- `iai`: preserve unchanged `chain_id`, `gap_type`, meaningful `reason`, `source_nodes`, `maps_to_edge`, and `target_node`; require edge source membership, destination equal to target and an allowed `state_update_target`; include deterministic L1 `merge_strategy` for the recommendation plus data scope and `next_planner_action: "re-enter Layer 1"`.
- `display`: actual grounded dataset source reference, dataset ID, columns, rows, counts, filters, recommendations, evidence bindings, selection, and unresolved status; never invent or fill absent evidence.
- `controls`: records with unique nonempty `id`, supported `kind`, nonempty `label` and `purpose`, boolean `required`, nonempty declared `return_keys`, and applicable type, limit, source, stable-identity, and edit `constraints`.
- `presentation.profile`: nonempty `archetype` and `summary`; nonempty resolvable `content` records with `source: "display.<path>"`, `role: primary|context|status`, and meaningful purpose; `interaction` has nonempty `actions` and `feedback`, while `submission` has nonempty `label`, `preconditions`, and exact `return_mapping`; include nonempty semantic `appearance` and `signature_features` describing table/cell/recommendation linkage.
- `expected_return`: exactly L2's keys and types with exactly identical `return_mapping` keys, each naming its actual source and serialization plus optional/empty handling; no artificial metadata controls.
- `widget_requirements`: nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, and `submission_requirements`, consistent with the profile and covering stable row identity, field identity, evidence highlighting, hidden-binding warnings, scope summary, and explicit primary selection.
- `safety`: `allow_html: false`, `allow_script: false`; optional `runtime` capabilities and libraries must be approved, available, and version-pinned; optional plugin-relative `reference_assets` are design-time only and never runtime data sources.

Send the validated design to `l4-pN9-widget-renderer`. Invalid selection, stale bindings, missing stable row IDs, unavailable data, or indispensable capability failure returns `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, and `return_to: l1-pN9-core-module`; reach no L4 and perform no substitution.

## Workflow End Authority

Selection is evidence only. Every result or failure re-enters `l1-pN9-core-module`; only L1 owns canonical workflow state and emits `decision: end`.