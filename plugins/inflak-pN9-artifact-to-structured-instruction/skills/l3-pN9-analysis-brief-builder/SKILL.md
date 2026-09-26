---
name: l3-pN9-analysis-brief-builder
description: "Use when: L2 selects substantive evidence-aware P9 brief editing."
---

# L3 Designer — Analysis Brief Builder

## Layer & Role

Design only `analysis-brief-builder` / `analysis_brief_builder` on `conversation_widget`. No diagnosis, substitution, rendering or execution.

## Inputs

L2 selection/planner/gap/goal, chain/binding, exact returns; source profile, selected direction, field values/statuses, material warnings and grounded instruction preview.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Resolve brief values and actual evidence policy. |
| Presented information | Objective, time, metrics, categories, baseline, evidence, audience, format and provenance. |
| Supported interaction | Edit non-artifact-confirmed values, preview, confirm/edit_selection/start_over/dismiss. |
| Feedback and constraints | Protect artifact facts, distinguish suggested/user-selected/missing values. |
| Submission and return | Map brief_values, field_provenance, warnings, instruction_preview, action and freeform_note. |
| Presentation intent | Readable provenance-aware brief and live preview, not approval checklist. |

## Essential Constraints

Fields: `objective`, `time_scope`, `metrics`, `categories_or_regions`, `comparison_baseline`, `evidence_constraints`, `audience`, `output_format`. Statuses: `confirmed_from_artifact`, `suggested_by_genai`, `selected_by_user`, `missing_or_uncertain`. Artifact-confirmed values remain evidence. Preview updates after edits and includes Objective, Artifact Context, Analysis Scope, Comparison Targets, Analysis Steps, Evidence Policy, Output Requirements, Missing or Additional Data. Copy Instruction is non-submitting via supported safe host API only. Confirm approves this brief, not rows or final report; no second approval/checkbox.

This optional editor is only for L2's actual unresolved material fields or user-requested changes. Keep settled values as compact context, not required controls. Focus editing on the diagnosed missing information and submit it once; do not demand a subsequent composer pass or final acceptance. Preserve full typed returns by merging edits into the supplied valid brief, without relabeling unedited model suggestions as user selections.

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
