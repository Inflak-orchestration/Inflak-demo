---
name: l4-daily-paper-conclusion-renderer
description: "Use when: a validated daily-paper L3 semantic contract is ready for sandboxed rendering."
---

# L4 Renderer — Daily Paper Interaction

## Workflow End Authority

Only `l1-daily-paper-conclusion-core` owns canonical state, merges returns and may emit `decision: "end"`. Submission, dismissal, cancellation, partial return and renderer failure immediately return there. Never resume L2/L3 directly or decide Completion from digest acceptance.

## Layer & Role

Implement Interaction Pathway only: L1 → L2 gap/selection → L3 semantic design → L4 render → L1. Compile one validated contract into accessible sandboxed HTML/CSS/JavaScript and call render_html_widget; preserve exact selection, purpose, actions and return schema. Execution Pathway, Host Agent Return and Completion never enter L4.

## Inputs

Validate locally; no external guide/schema read or success handoff_type is required:

- Identity: nonempty exact `selected_widget_id`, `widget_id`, `widget_type`, `surface`, `planner_id`, `purpose`, `interaction_goal`; match L2 and registered type/surface/eligibility.
- `iai`: unchanged named `chain_id`, `gap_type`, meaningful `reason`, `source_nodes`, `maps_to_edge`, `target_node`; source belongs to source_nodes, destination equals target_node and allowed `state_update_target`. Require deterministic L1 `merge_strategy` and `next_planner_action: "re-enter Layer 1"`; do not merge here.
- `display`: grounded values, actual sources/revisions and unresolved status; every profile content source must resolve against it. No invented evidence/defaults/outcomes.
- `controls`: unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty declared `return_keys`, applicable type/limit/source/edit `constraints`.
- `presentation.profile`: nonempty archetype/summary, nonempty `content` array of resolvable `source: "display.<path>"`, `role: primary|context|status`, meaningful purpose records; interaction has nonempty actions/feedback and submission with nonempty label/preconditions and exact return_mapping; nonempty semantic appearance and signature_features list.
- `expected_return`: exactly L2 keys/types and exactly matching `presentation.profile.interaction.submission.return_mapping` keys. Each mapping has actual source, serialization and optional/empty semantics; derived metadata needs no fake control.
- `widget_requirements`: four nonempty string arrays visible_information, required_controls, required_behavior, submission_requirements; implement every item consistently with the profile and mappings.
- `safety`: allow_html false and allow_script false in semantic input; only L4 writes implementation. Optional runtime is restricted to approved available capabilities/version-pinned libraries; reference_assets are plugin-relative design-time references/principles, never runtime assets.

Missing/inconsistent semantics, unsupported capabilities or unsafe input returns structured renderer failure with actual validation errors and exact L1 return_to without rendering or semantic repair.

## Domain Rendering

| Registered type | Required semantic fidelity |
| --- | --- |
| source_filter_panel | Actual public source/range/focus/output and derived readiness; no fake candidate count. |
| collection_status_timeline | Real fetch/extract/filter/dedup status, candidate identities and skipped/partial/failure records. |
| inspection_warning_dialogue | Affected paper evidence boundaries, accessible links and inclusion/reinspection choices. |
| theme_evidence_matrix | Actual themes, paper-support matrix, confidence basis and priorities. |
| evidence_linked_artifact_review | Current conclusion, highlights/themes, source links, caveats and explicitly labeled evidence-grounded 1-2 sentence critical review. |

Keep arXiv paper identities and actual public links; listing-only metadata is not an abstract. Preserve partial success and clearly distinguish weak/unavailable evidence. Missing critical review or unsupported claims return L1 for L2 repair, not renderer-authored criticism. Scope/reinspection/revision/retry actions are requests, not completed work. Copy/export is not acceptance or an invented new digest.

## Rendering Procedure

Validate every profile source/control/constraint/mapping and widget_requirements item. Compile to existing title/html/css/js/height/planner_id/interaction_goal/expected_return fields with `render_mode: generated`, no undocumented host args. Initialize display from actual supplied data, including window.widgetDisplay when used. Resolve runtime artifacts/images with `window.widgetAssetUrl(ref)`, not local paths/file://. Public paper links are safe ordinary links, not fetch requests. Escape paper/digest text as data. Validate and serialize exactly `window.submitWidget(values)`; dismiss through `window.dismissWidget(note)`; return original envelope unchanged L1.

## Universal Style and Layout Baseline

Match host typography, neutral surfaces, borders, spacing, focus and density with available host `--iai-*` tokens and `.iai-*` classes, not a forced light theme. Usable at **266px** iframe and desktop widths; minmax(0, 1fr), min-width: 0 and no page-level overflow-x. Give the evidence matrix an explicitly bounded scroll region only if needed; wrap source titles/URLs without control overlap. Keep `.iai-actions` persistent and submit/dismiss/reset reachable. Primary submit confirms current values; no confirmation checkbox or second approval gate. Native controls, accessible icons/tooltips, no decorative nested cards/marketing copy; checkboxes only for actual multi-value boolean settings.

## Must / Must Not

Implement keyboard, visible focus, labels, validation errors, loading/disabled/submitting states and duplicate-submit prevention. Preserve values after errors and exact optional/empty return semantics. Never invent papers/progress/options/defaults, change IAI meaning, access parent DOM, use remote code/undocumented network or modal APIs, invoke collection/task tools, merge state or produce final workflow response.

## Stop / Continue / Escape

Immediately return submitted/dismissed/cancelled evidence or renderer failure to `l1-daily-paper-conclusion-core`. Do not repair source evidence or resume L2/L3 directly.
