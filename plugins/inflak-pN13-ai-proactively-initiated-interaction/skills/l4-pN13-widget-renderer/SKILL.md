---
name: l4-pN13-widget-renderer
description: "Use when: a fresh P13 L1/L2/L3 pass provides a complete intention-choice or implementation-input semantic contract."
---

# L4 Renderer — P13

## Layer & Role and Workflow End Authority

Implement Interaction Pathway only: user/return → L1 → L2 selection → L3 design → L4 render → L1. Accept registered `adaptive_basic_widget` or `adaptive_implementation_widget` on `inline_widget`. L3 owns semantics; L4 implements without changing selection/goal/operations/returns. Execution Pathway is L2 direct executor invocation without L3/L4. Host Agent Return and Completion belong to L1; only `l1-pN13-core-module` owns state and `decision: end`. All results/failures immediately return there.

## Inputs

Validate locally, without loading main's renderer or an external contract; no success `handoff_type`:

- Identity: nonempty `selected_widget_id`, `widget_id`, `widget_type`, `surface`, `planner_id`, `purpose`, `interaction_goal`; exact L2/local registry ID, skill, planner, type/surface and eligibility.
- `iai`: unchanged named `chain_id`, `gap_type`, binding `reason`, `maps_to_edge`, `source_nodes`, `target_node`; meaningful reason, source includes origin, destination equals target and allowed `state_update_target`; deterministic L1 `merge_strategy`, `next_planner_action: "re-enter Layer 1"`.
- `display`: grounded values/current sources/unresolved status; resolve every profile content source. No invented options/evidence/previews/file IDs/results.
- `controls`: unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty declared `return_keys`, applicable types/limits/source/edit `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`, nonempty content records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`); nonempty interaction `actions`/`feedback`, submission nonempty `label`/`preconditions`, exact `return_mapping`; nonempty semantic `appearance` and `signature_features` list.
- `expected_return`: exactly L2 keys/types and exactly the same mapping keys with producible source/serialization and optional/empty handling; derived metadata needs no artificial field.
- `widget_requirements`: four nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`; implement every consistent item, not extra gates.
- `safety`: L3 input `allow_html: false`, `allow_script: false`; optional runtime only approved available capabilities/pinned libraries; optional reference assets only plugin-relative design-time principles, never runtime assets.

Inconsistent/incomplete semantics, stale source, unsafe input or missing runtime capability returns a structured renderer failure to L1 without rendering or semantic repair. A primitive name or visual adjectives alone are not a complete profile. Resolve every content source, preserve every label/purpose/required status/constraint and implement every supported action, feedback item and submission precondition. No contract part replaces or weakens another.

## Rendering Procedure

1. Validate profile, return mappings and mode eligibility. Initialize deterministic state from `window.widgetDisplay` before handlers.
2. Generate sandboxed self-contained HTML/CSS/JavaScript. No parent DOM, storage, cookies, secrets, local files, arbitrary networks or browser modals. Only approved pinned libraries permitted by CSP may load; no invented endpoints.
3. Resolve runtime images/artifacts only through `window.widgetAssetUrl(ref)` (host assetUrl bridge), never local paths or `file://`; keep source `fileId` distinct from display URL. Declared user-selected exports/uploads use only `window.uploadWidgetFile(file)` and require actual success.
4. Call `render_html_widget` once with `render_mode: "generated"`, exact type/surface and unchanged `selected_widget_id`, `display`, `controls`, `planner_id`, `interaction_goal`, `expected_return`. Compile profile/requirements into existing tool fields, not new arguments; host validation does not replace these local checks.
5. Wire every visible control to state, feedback or values. Validate exact typed mapping before `window.submitWidget(values)`; visible dismissal uses `window.dismissWidget(note)`. Forward unchanged host envelope to L1.

## Universal Host UI Baseline

- Match host typography, neutral surfaces, borders, spacing, focus and density using `--iai-*` tokens/`.iai-*` classes. No domain-theme override or marketing decoration.
- Usable at 266px and desktop; `box-sizing: border-box`, bounded `minmax(0, 1fr)` tracks, `min-width: 0` on shrinkable children, `max-width: 100%` on controls/media. Stack narrow layouts and wrap IDs/actions; labels, values, status and validation must not overlap controls.
- No page-level `overflow-x`; only labeled data/graph regions scroll. Prefer native buttons, inputs, selects, textareas and radios. Checkboxes only for actual multi-value boolean settings, never confirmation/approval/acceptance/submission.
- Persistent primary submit/dismiss/reset in `.iai-actions`; one submit confirms current values, no extra confirm checkbox/step. Familiar commands use icons where available, with accessible names/tooltips; no nested decorative cards.
- Implement keyboard, focus, labels, inline errors, disabled/loading/submitting states and non-color status. Drag/resize/reorder/drawing needs an accessible alternate path; shortcuts need buttons and must not capture text typing.

## Domain and Return Invariants

- Basic choices retain stable IDs and optional declared freeform intent; no ranking/confidence inspector, auto-selection or execution.
- Implementation renders only one registered mode and complete L3 profile, preserving numeric bounds, full colors/order/groups/edges, actual item/source/version IDs and complete editable text with consistent offsets. Actual baseline/proposed versions are mandatory for comparison; local adjustment previews are not task outputs.
- Spatial input preserves source aspect, normalized coordinates, current revision, exact mask protocol, successful uploads and deterministic strokes/patches/snapshots. Reviewed cutout requests are not extraction; no image/task tools.
- Rich modes require actually available approved pinned libraries/capabilities. No silent canvas-to-form fallback or host document access; remain in the isolated iframe.
- Return exact declared values with host `widget_id`, `planner_id`, `action`, `values`, `freeform_note`, `timestamp`. Do not infer plugin state or execution success from a label/submission.

## Stop / Continue / Escape / Next

After submit, dismissal, cancellation or failure, load `l1-pN13-core-module` with the exact result. Never resume L2/L3, call task tools, produce final workflow responses or decide Completion.