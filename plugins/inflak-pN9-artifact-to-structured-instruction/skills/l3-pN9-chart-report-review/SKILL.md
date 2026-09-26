---
name: l3-pN9-chart-report-review
description: "Use when: L2 selects chart-report-review for an actual Host Agent report and its acceptance or revision."
---

# L3 Designer — P9 Chart Report Review

## Layer & Role

Design only `chart-report-review`, type `chart_report_review`, surface `conversation_widget`. Preserve L2's diagnosed report-review gap. Do not mutate the report, fabricate artifacts, render, or execute.

Use only for user-requested approval or revision. Normal report delivery is handled by the host HTML presentation and must not invoke this widget or wait for acceptance.

## Inputs

Consume L2 selection/planner/gap/goal, named chain, binding, exact expected return and L1 target; validate registry and runtime. Require the actual `generated_report` returned by the Host Agent, including title, executive summary, sections, chart recommendations, evidence register, and limitations.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Let the analyst inspect the actual Host Agent report and accept or scope a revision. |
| Presented information | Title, executive summary, report sections, chart recommendations, evidence references, and limitations. |
| Supported interaction | Accept, revise narrative/charts, edit plan, start over, or dismiss. |
| Feedback and constraints | Keep the current report and selected revision target visible; never imply a downloadable artifact exists. |
| Submission and return | Map decision/action consistently with revision target/text and note. |
| Presentation intent | Scannable structured report with reachable concise review actions. |

## Essential Constraints

- Validate exact selection/skill/path, planner/gap/goal/edge, returns, artifact/state support, runtime, `chain_id` and preserved `reason`. Never select another widget.
- Render only fields present in the actual structured report. No HTML interpolation, nested report iframe, arbitrary URL, generated download, or fabricated preview.
- Return strings `decision`, `revision_target`, `revision_instruction`, `action`, `freeform_note`. `decision` is `accept|revise`; targets `narrative|charts|report_plan|none`; actions `accept_report|revise_narrative|revise_charts|edit_report_plan|start_over|dismiss` as declared. Reject mismatched action/decision/target combinations.
- Never fabricate a report section, quality claim, validation result, download, or completion.
- One primary acceptance action confirms this actual report; no checkbox or second confirmation. Revision is semantic instruction, not an HTML patch.

## Output and Handoff

Emit the complete local eight-part contract; no success `handoff_type` or external read:

- Identity: nonempty exact `selected_widget_id`, instance `widget_id`, registry `widget_type`/`surface`, `planner_id`, contextual `purpose`, unchanged `interaction_goal`.
- `iai`: copy unchanged `chain_id`, `gap_type`, `reason`, `source_nodes`, `maps_to_edge`, `target_node`; require named chain and meaningful reason, edge source in `source_nodes`, destination equal to `target_node` and allowed `state_update_target`; deterministic L1 `merge_strategy` records draft-bound review, and `next_planner_action: "re-enter Layer 1"`.
- `display`: actual structured report fields, source references, task values, provenance, limitations, and unresolved status; no invented evidence, uploads, previews, or outcomes.
- `controls`: records with unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty declared `return_keys`, and applicable types, limits, source/edit `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`, nonempty resolvable `content` records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`); `interaction` has nonempty `actions`/`feedback` and `submission` with nonempty `label`, `preconditions`, exact `return_mapping`; include nonempty semantic `appearance` and `signature_features`.
- `expected_return`: exactly L2's keys/types and exactly identical submission `return_mapping` keys, each naming actual source and serialization including optional/empty handling. Derived draft metadata needs mappings, not artificial controls.
- `widget_requirements`: nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`, consistent with the profile and actual review obligations.
- `safety`: `allow_html: false`, `allow_script: false`; optional approved available `runtime` capabilities/pinned libraries and plugin-relative design-time `reference_assets` never authorize arbitrary runtime assets.

Send to `l4-pN9-widget-renderer`. Invalid selection or indispensable evidence/capability failure returns `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, `return_to: l1-pN9-core-module`, without L4 or substitution.

## Workflow End Authority

Acceptance is evidence only. Every result/failure re-enters `l1-pN9-core-module`; only L1 owns canonical workflow state, merges review evidence for the current generated report, and emits `decision: end` with that report.
