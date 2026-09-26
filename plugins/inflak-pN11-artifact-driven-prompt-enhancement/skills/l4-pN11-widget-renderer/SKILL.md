---
name: l4-pN11-widget-renderer
description: "Use when: rendering a validated P11 prompt-grounding or target-bound action contract on the persistent Artifact Canvas."
---

# Layer 4 - P11 Widget Renderer

## Workflow End Boundary

After any widget return or renderer failure, immediately load `l1-pN11-core-module` with the structured result. Layer 4 never decides workflow completion, produces the final response, or continues directly to a planner or executor.

## Render Contract

Use the self-contained Inputs and style rules below; no main skill is a runtime prerequisite. Validate the selected L3 contract and preserve `selected_widget_id`, `display`, `controls`, `planner_id`, `interaction_goal`, and `expected_return` in the existing render request. Selection is trace metadata, never permission to replace a widget.

Render only after `L1 → L2 → L3`. Generate nonempty HTML, CSS, and JavaScript implementing the exact semantic profile and call `render_html_widget` with `render_mode: "generated"` on `artifact_canvas_widget`. Do not assume a repository-owned template. Preserve `return_mode: agent_interpreted`: the generated interaction may return any JSON values grounded in its actual controls and submission mapping, not a fixed registry field list. L1 interprets them against the source-bound interaction; flexible serialization never substitutes for explicit target-bound approval or complete action evidence. Execution Pathway, Host Agent Return and Completion do not enter L4.

Preserve prompt source spans, artifact binding, placement, and safety policy. Initialize from `window.widgetDisplay`. Ground object-bound interactions in stable SVG ids and listen for `artifact_canvas_selection`; update from `activeObjectId`, `selectedObjectIds`, and `object` rather than guessing from labels. There is no aggregate final-review widget. The source artifact is read-only.

After every widget result, return to `l1-pN11-core-module`. Do not chain another widget or tool from Layer 4.

## Must

- Render one contract at a time.
- Keep prompt source spans and stable ids intact.
- Use host-provided active-object context only for filtering and placement.
- Validate and serialize the exact declared submission mapping through `window.submitWidget(values)`; dismiss with `window.dismissWidget(note)`. Every result returns to Layer 1 for interpretation.
- Resolve each real source/candidate image reference from `window.widgetDisplay` with `window.widgetAssetUrl(ref)` before assigning an image source. Use only the supplied current-session fileId or approved asset reference; never invent a URL, use `file://`, fetch remote assets, or substitute a mock image. Missing/unresolvable references remain visibly unavailable and block dependent submission. The live SVG remains host-owned, not iframe-fetched markup.

## Must Not

- Do not submit `operations` or any artifact patch.
- Do not execute the enhanced prompt.
- Do not inspect or mutate parent DOM or SVG markup.
- Do not add undeclared controls, capabilities, remote assets, or return fields.

## Inputs

Validate complete semantic contract locally, no external read/success handoff_type:
- Identity: nonempty exact selected_widget_id, instance widget_id, registry widget_type/surface, planner_id, purpose, unchanged interaction_goal/eligibility.
- `iai`: unchanged L2 chain_id/gap_type/reason/source_nodes/maps_to_edge/target_node; named chain/meaningful reason, edge source in sources, destination=target and allowed state_update_target; deterministic L1 merge_strategy; next_planner_action:"re-enter Layer 1"; no merging here.
- `display`: actual sources/revisions/values/unresolved status, all profile sources resolve, no fabricated evidence.
- `controls`: unique nonempty id, supported kind, nonempty label/purpose, boolean required, nonempty declared return_keys, typed/limit/source/edit constraints.
- `presentation.profile`: nonempty archetype/summary; nonempty content records resolvable source:"display.<path>", role:primary|context|status, meaningful purpose; interaction nonempty actions/feedback; submission nonempty label/preconditions/exact return_mapping; nonempty semantic appearance/signature_features.
- `expected_return`: preserve exactly L2 keys/types for this contextual agent-interpreted interaction and identical mapping keys with actual source/serialization/optional-empty handling; no artificial metadata controls or enforcement of static domain keys.
- `widget_requirements`: four nonempty string arrays visible_information/required_controls/required_behavior/submission_requirements; implement all consistently.
- `safety`: allow_html:false, allow_script:false in L3; only L4 codes. Optional runtime approved available capabilities/pinned libraries; reference_assets plugin-relative design-time only.
Failure returns structured renderer error to l1-pN11-core-module without render/repair. Compile into existing render_html_widget fields, preserve artifact_binding/placement/selected_widget_id.

## Universal Style and Layout Baseline

Match host typography/neutral surfaces/borders/spacing/focus/density. Usable at 266px iframe and desktop; minmax(0,1fr), min-width:0, no page overflow-x, designated internal scroll only. No overlapping labels/status/errors. Native keyboard-accessible controls and focus/disabled/loading/validation; icons named with tooltips. Persistent reachable .iai-actions submit/dismiss/reset; no approval checkbox/extra gate, checkboxes only real boolean settings. Light surface/dark text default, justified dark designs readable light labels/text; no decorative nested cards/marketing.

Automatic target-bound editor appears without requiring a prior object click. Concrete instruction preview updates with operation/parameters/separate constraints; one Approve instruction command confirms current target-bound values. Prefill/edit/view is not approval; no aggregate prompt-enhancement review or second confirmation. Preserve prompt_unit_id/source spans/stable targets/revision and provenance. All colors have swatches. Source stays read-only; only L2 after L1 may perform Host checks and execute. Use existing documented submit/dismiss/focus/selection APIs and window.widgetAssetUrl(ref) for real assets; no parent DOM/fetch/markup/remote libraries/tool calls. Every outcome re-enters l1-pN11-core-module, only L1 decision:end.