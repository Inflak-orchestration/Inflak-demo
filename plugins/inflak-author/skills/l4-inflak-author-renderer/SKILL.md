---
name: l4-inflak-author-renderer
description: "Use when: rendering one validated inflak Author framing, workflow, artifact-flow, widget-design, dialogue, resource, experience-review, or build-review contract."
---

# Layer 4 - inflak Author Renderer

## Workflow End Boundary

Only `l1-inflak-author-core` owns canonical state/merging and Completion or `decision: end`. After every submission, dismissal, cancellation or renderer failure, immediately load it with the structured result. L4 never produces a final response or continues directly to a planner/executor.

## Accepted Contracts and Policy

Accept only `task_framing_board`, `workflow_step_designer`, `artifact_state_flow_map`, `widget_design_studio`, `guided_authoring_dialogue`, `execution_resource_intake`, `experience_blueprint_preview`, or `plugin_build_review` selected through a fresh Interaction Pathway: user/return → L1 → L2 gap + selection → L3 design → L4 render → L1. L3 owns semantics, L4 implementation. Execution Pathway directly invokes the selected executor from L2 without L3/L4; Host Agent Return and Completion are L1 decisions. This skill is self-contained; do not load another renderer skill or external schema.

## Inputs

Validate these eight local obligations; no success `handoff_type` is required:

- Identity: nonempty `selected_widget_id`, `widget_id`, `widget_type`, `surface`, `planner_id`, `purpose`, `interaction_goal`; exact L2/local-registry selection, skill, planner, goal, type and `conversation_widget` surface.
- `iai`: unchanged named `chain_id`, `gap_type`, binding `reason`, `maps_to_edge`, `source_nodes`, `target_node`; meaningful reason, source includes edge origin and destination equals target and allowed `state_update_target`. Require deterministic L1 `merge_strategy` and `next_planner_action: "re-enter Layer 1"`; never merge here.
- `display`: grounded values, actual source references, current revision and unresolved status; every content source resolves. Sample mini previews remain explicitly illustrative, never runtime evidence. No invented options, uploads, approvals, hashes or outcomes.
- `controls`: unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty declared `return_keys`, applicable type/limit/source/edit `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`, nonempty `content` records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`); nonempty interaction `actions`/`feedback`, `submission` with nonempty `label`/`preconditions` and exact `return_mapping`; nonempty semantic `appearance` and `signature_features` list.
- `expected_return`: exactly L2 keys/types and exactly the same return-mapping keys, each with actual source and serialization, including optional/empty semantics. Derived hash/revision/identity require mappings, not artificial controls.
- `widget_requirements`: four nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`; implement every consistent obligation, not additional gates.
- `safety`: `allow_html: false`, `allow_script: false` for L3 input. Optional `runtime` uses only available approved capabilities and pinned libraries; optional `reference_assets` are plugin-relative design-time references/principles, never runtime assets.

Reject stale revisions, missing/failed preview identity, inconsistent semantics, unsafe input, secret-like values, local paths, unsupported capabilities or unproducible returns with a structured renderer failure directly to `l1-inflak-author-core`, without rendering or semantic repair.

## Rendering

Generate a concise accessible conversation widget and call `render_html_widget` exactly once with `render_mode: "generated"`. Pass `selected_widget_id`, `display`, `controls`, `planner_id`, `interaction_goal`, and `expected_return` unchanged. Treat `selected_widget_id` only as registry trace/observability metadata; it must not change widget UI semantics or select or replace a widget.

```json
{
  "widget_type": "guided_authoring_dialogue",
  "selected_widget_id": "<copied-from-L3>",
  "render_mode": "generated",
  "title": "Shape the collaboration",
  "html": "<main></main>",
  "css": "",
  "js": "",
  "height": 420,
  "display": {},
  "controls": [],
  "planner_id": "inflak-authoring",
  "interaction_goal": "clarify_human_ai_collaboration",
  "expected_return": {}
}
```

Initialize content from `window.widgetDisplay` before binding handlers. Submit declared values through `window.submitWidget(values)` and dismiss only through `window.dismissWidget(note)`. Show inline validation errors rather than browser modal dialogs.

Resolve every runtime image/artifact reference through `window.widgetAssetUrl(ref)` (host assetUrl bridge), never `file://`, an absolute local path or an invented display URL. Stable `fileId` identity is distinct from that URL. Compile the full profile/requirements into existing render-request fields; never invent additional tool arguments or assume host-side validation replaces these checks.

Every Author widget must contain a persistent phase header with current phase, overall phase count, and current stage/interaction cursor where applicable. Keep the primary decision and current substep visible without requiring the user to scan prior phases.

## Interaction Profiles

- Task framing board: use an editable card grid for user/problem/input/outcome/success/exclusions, plus a compact input→collaboration→output strip. Highlight inferred fields and changed fields; do not render this as stacked paragraphs or a long form.
- Workflow step designer: render only one stage as stable user, AI, and shared swimlanes. Place required information before the lanes, checkpoint/autonomy controls at the lane boundary, intermediate artifacts on a separate rail, and completion/branch/failure anchors at the end. Keep lane and artifact dimensions stable while editing.
- Artifact and state flow map: render typed nodes connected left-to-right with distinct input, intermediate, decision/status, and final-artifact treatments. Selecting a node opens one compact lifecycle inspector. Show downstream invalidation by highlighting affected nodes/edges; never reduce the graph to a text table.
- Widget design studio: render candidate concepts as a compact rail and one larger sample-data mini preview. The preview must visually embody the candidate kind: progress dashboards show meters/matrices, comparison reviews show side-by-side evidence, timelines show ordered stages, editors show editable regions, annotation surfaces show a stage and tools. Beside it, show interaction goal, interaction mode, widget family/type, information regions, actions, feedback/states, outcome-specific state/workflow effects, rationale, and tradeoffs. Selecting a candidate updates the preview without resizing the overall layout.
- Guided dialogue: one focused question, selectable plain-language options, visible recommendation, and optional free text.
- Resource intake: execution choice, a conditional registered GPT Image tool selector, existing attachment references, a multiple-file picker, host-fallback toggle, and a clear warning never to upload credentials. Show the image-tool selector only for `image_tool`. Upload each user-selected file only through `window.uploadWidgetFile(file)` and return a sanitized attachment reference without its host path.
- Experience preview: because every phase was already reviewed, begin with a compact coverage strip and key decisions. Collapse workflow, interaction-method, state-lifecycle, and final-presentation details into separate disclosure sections; never expand all sections by default or reproduce the full blueprint as one page.
- Build review: approved workflow, interaction methods, state lifecycle, final presentation, and acceptance cases first; show their generated skill/registry traceability, then runtime readiness, scenario status, and warnings; keep implementation details collapsed and make the exact preview hash visible before publication approval. Preserve `plugin_id`, validation cases, run/report/session references, and failed checks in `display` so the host can provide background run, interactive run, failure inspection, return-to-Author, regenerate, and hash-bound apply controls.

## Visual and Responsive Requirements

- Match the host application's typography scale, neutral surfaces, border treatment, spacing rhythm, focus treatment and control density. Use shared `--iai-*` tokens and `.iai-*` classes; domain visuals cannot override host consistency.
- Remain usable at 266px and desktop widths. Use stable `minmax(0, 1fr)` tracks and `min-width: 0` on shrinkable children; prevent page-level `overflow-x` and keep labels, values, validation and controls from overlapping.
- Use native buttons/inputs/selects/textareas/radios where possible. Checkboxes may represent actual independent or multi-value boolean settings only, never approval, confirmation, acceptance or submission. Required warning acknowledgements use explicit actions/selection tied to actual warning IDs, not generic confirm checkboxes.
- Keep persistent primary submit, dismiss and reset actions in `.iai-actions`; the primary submit confirms current values once, without a second confirmation step. Implement accessible keyboard/focus/labels/errors and disabled/loading/submitting states; graph, drag and reorder interactions need keyboard/non-drag alternatives.
- Use CSS Grid/Flex with fixed or bounded tracks for boards, swimlanes, graph nodes, candidate previews, action bars, counters, and badges so interaction cannot shift the layout.
- Every generated stylesheet must include `* { box-sizing: border-box; }`, `html, body { width: 100%; max-width: 100%; overflow-x: hidden; }`, and `min-width: 0` on every grid/flex child that contains text or controls.
- Use bounded responsive tracks such as `repeat(auto-fit, minmax(min(100%, 14rem), 1fr))`; never set a content container, candidate, preview, card, input, or button to a fixed/minimum width wider than its containing block.
- Apply `overflow-wrap: anywhere` to IDs, widget types, modes, URLs, hashes, and other machine-like labels. Inputs, textareas, selects, buttons, badges, and code labels must use `max-width: 100%`.
- At `max-width: 560px`, task framing grids, swimlanes, graph+inspector layouts, and widget studio candidate+preview+inspector layouts become one column. Candidate lists wrap vertically; the mini preview stays above the inspector. Horizontal scrolling is allowed only inside an explicitly labeled data table or graph viewport, never on `html`, `body`, or the primary widget wrapper.
- Use icon+label actions where the label disambiguates meaning; familiar secondary actions may use an icon with an accessible tooltip.
- Encode artifact kind, actor, status, confidence, and selection with more than color alone.
- At narrow widths, stack inspectors below the visual canvas while retaining stage order and candidate selection. Do not shrink labels below readable size or scale fonts with viewport width.
- Keep cards at 8px radius or less, do not nest cards, and avoid decorative gradients/orbs. The visual structure must communicate the design model rather than decorate prose.
- Mini previews are sandbox-local sample visualizations. They must not upload, execute target tools, contact networks, or imply that the target widget has already been built.
- Before calling `render_html_widget`, inspect the generated CSS/markup for `min-width`, fixed multi-column tracks, unbreakable identifiers, absolute positioning, and controls without max-width. Revise any rule that can make the primary wrapper wider than a 266px viewport.

## Stable Return Invariants

Return the host envelope with `widget_id`, `planner_id`, action, values, freeform note, and timestamp. Values must preserve the exact upstream keys and types. Review approval must retain the displayed revision. Publication approval must retain the exact displayed preview id and hash. Every visible control must affect local state, feedback, or returned values.

## Runtime and Safety

Use deterministic local state and shared design tokens. Do not access parent DOM, storage, cookies, tokens, arbitrary networks, browser modals or undeclared global APIs. Only actually approved version-pinned libraries permitted by CSP may be used. The only permitted local-file operation is a user-selected resource passed directly to the injected `window.uploadWidgetFile(file)` bridge; do not read it independently, execute it, or retain its contents. Await upload success before returning sanitized stable references; preserve errors without inventing uploads. Do not call task/scenario/publication tools or change authoring semantics. Host-provided scenario controls remain host-owned, never invented iframe APIs.

## Lifecycle and Next

After submit, dismiss, or renderer failure, return to `l1-inflak-author-core`. Never load another interaction or executor directly from Layer 4.