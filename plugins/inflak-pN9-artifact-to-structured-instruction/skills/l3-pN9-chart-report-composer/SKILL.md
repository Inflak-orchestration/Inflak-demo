---
name: l3-pN9-chart-report-composer
description: "Use when: L2 selects report structure or a no-invention data policy."
---

# L3 Designer — Chart Report Composer

## Layer & Role

Design only `chart-report-composer` / `chart_report_composer` on `conversation_widget`. No diagnosis, substitution, rendering, report generation or execution.

## Inputs

L2 selection/planner/gap/goal, chain/binding, exact returns; current artifact profile/data inventory, confirmed brief, proposed sections/charts, dataset provenance and prior plan decisions.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Resolve report structure or unsupported-data policy. |
| Presented information | Title/audience/ordered sections, chart purposes/metrics/dimensions/marks, sources and limitations. |
| Supported interaction | Arrange sections, include supported chart recommendations, choose report depth and a real fallback. |
| Feedback and constraints | Show dataset support beside charts; unavailable derived charts cannot be selected. |
| Submission and return | Map complete report_plan, data_policy, action and freeform_note. |
| Presentation intent | Compact evidence-aware outline, not another generic approval. |

## Essential Constraints

Optional customization only: do not require this widget after a direction or brief submission. Keep settled audience, scope and evidence constraints as context. Ask only about the current material conflict or user-requested structural changes; ordinary section and chart choices do not require approval.

Policy exactly `request_machine_readable_data`, `use_confirmed_visible_values_only` or `describe_source_without_derived_chart`. No model-estimated rows. Plan keeps title, audience, ordered sections, supported chart recommendations, and report depth. Actions generate_report/edit_analysis_brief/start_over or host dismissal. generate_report needs a complete plan and confirmed field bindings for all chart recommendations; an explicit source-only narrative fallback is valid. Requested upload is not a completed upload. No executable HTML, task-tool calls, fabricated data, file-export promises, or extra confirmation. Submission is not successful report generation.

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
