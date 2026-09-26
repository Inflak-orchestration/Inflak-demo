---
name: l4-pN9-widget-renderer
description: "Use when: a validated P9 semantic design needs sandboxed conversation UI."
---

# L4 Renderer — P9

## Layer & Role

Implement one L3 design after L1 → L2 gap/selection → L3. Render on `conversation_widget` through `render_html_widget`; never compile reports, invoke task tools, alter semantics, or decide completion. Execution Pathway does not enter L4.

## Inputs

Validate locally; no main skill, contract read, success `handoff_type`, or undocumented tool argument is required:

- Identity: nonempty exact `selected_widget_id`, instance `widget_id`, registry `widget_type`/`surface`, `planner_id`, contextual `purpose`, unchanged `interaction_goal`.
- `iai`: unchanged L2 `chain_id`, `gap_type`, meaningful `reason`, `source_nodes`, `maps_to_edge`, `target_node`; source membership and destination equal to target/allowed `state_update_target`; deterministic L1 `merge_strategy`, `next_planner_action: re-enter Layer 1`.
- `display`: grounded values, source references and unresolved state; every content source must resolve, never fill absent evidence.
- `controls`: unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty declared `return_keys`, applicable type/limit/source/edit `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`; nonempty `content` records (`source: display.<path>`, `role: primary|context|status`, meaningful `purpose`); nonempty `interaction.actions`/`feedback`, `submission.label`/`preconditions`/exact `return_mapping`; nonempty semantic `appearance` and `signature_features`.
- `expected_return`: exactly L2 keys/types, with exactly matching mapping keys and actual source/serialization plus declared optional/empty handling; distinguish absent optional values from allowed empty strings/arrays and enforce required nonempty values. No extra controls for derived metadata.
- `widget_requirements`: four nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`; implement every item consistently with the profile.
- `safety`: L3 `allow_html: false`, `allow_script: false`; only L4 writes code. Optional runtime capabilities/libraries must be approved, available and version-pinned; plugin-relative design-time `reference_assets` are never runtime URLs.

Invalid/incomplete semantics, source or capability returns a structured renderer failure directly to `l1-pN9-core-module`, without rendering or semantic repair.

## Universal Style and Layout Baseline

Match host typography, neutral surfaces, borders, spacing rhythm, focus and control density using shared `--iai-*` tokens and `.iai-*` classes. Remain usable at **266px** and desktop widths. Use `minmax(0, 1fr)` and shrinkable `min-width: 0`; no page-level `overflow-x`, overlapping labels or obscured validation. Explicitly designated regions may scroll. Prefer native buttons/inputs/selects/textareas/radios. Checkboxes only represent genuine multi-value boolean settings, never confirmation/approval/acceptance/submission. Keep persistent submit/dismiss/reset actions reachable in `.iai-actions`. Provide keyboard operation, visible focus, labels, loading/disabled/error states and accessible icon names/tooltips. Avoid decorative card nesting or marketing copy.

## Rendering Procedure

1. Validate complete profile, references, control constraints and exact return mapping; initialize from `window.widgetDisplay` before handlers.
2. Implement semantic information hierarchy, current values, feedback and inline validation in nonempty sandboxed HTML/CSS/JS.
3. Resolve image assets using `window.widgetAssetUrl(ref)` only; never `.path`, arbitrary `.url`, `file://`, data URI, remote fetch or invented IDs. Show unavailable status truthfully.
4. Call `render_html_widget` with `render_mode: generated`, unchanged selection/type/surface/display/controls/planner/goal/expected return and generated title, HTML, CSS, JS and height. The profile is input to compilation, not an invented renderer-tool parameter.
5. Submit exactly declared typed values via `window.submitWidget(values)`; dismiss via `window.dismissWidget(note)`. Return unmodified structured outcome to L1.

## Domain Rendering

- Lens chips use source-grounded rationale, support and data requirements; exactly one primary objective, optional secondary lenses and conditional narrowing. Never preselect recommendations.
- Data-anchored analysis table makes the bounded CSV table the primary surface. Use sticky headers and an explicitly labeled horizontal table viewport; preserve stable row IDs and field names through sorting/filtering. Hover or keyboard focus on a recommendation highlights every bound cell without selecting it; activation reveals an inline detail at the nearest bound row. Cell/row selection updates a persistent scope summary and analysis-instruction preview. Show when filters hide bound rows and provide a reveal action. Keep non-bound cells readable, never preselect a recommendation, never derive findings in JavaScript, and never submit visible row indexes.
- Brief preserves eight fields and four provenance statuses, protects artifact evidence, and updates all eight preview sections. Copy Instruction is non-submitting if supported. Confirm approves this brief; no warning-ack checkbox.
- Composer shows ordered sections and dataset-backed charts. Missing values require an explicit no-invention data policy. Generate Report submits values only; no Vega-Lite/HTML generation in the widget.
- Report review renders the actual Host Agent report as structured text, section summaries, chart recommendations, evidence references, and limitations. Do not create a nested report iframe, HTML/JSON download, artifact URL, or validation claim. Accept/revise/plan/start-over actions map exactly to declared values.

## Safety and Next

No parent DOM, storage, cookies, tokens, local files, modal APIs, undeclared networks or remote code. Do not invent task facts, fields, defaults, steps, outcomes or approval controls. Every submit/dismiss/cancel/failure immediately returns to `l1-pN9-core-module`; only L1 merges state and emits `decision: end`.