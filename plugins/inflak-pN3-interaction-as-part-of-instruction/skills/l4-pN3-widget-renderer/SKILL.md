---
name: l4-pN3-widget-renderer
description: "Use when: rendering P3's semantic object-layout sketch pad, brief confirmation, or sketch-guided image review as a generated sandboxed widget."
---

# Layer 4 - P3 Widget Renderer

## Workflow End Boundary

After any widget return or renderer failure, immediately load `l1-pN3-core-module` with the structured result. Layer 4 never decides workflow completion, produces the final response, or continues directly to a planner or executor.

## Shared Render Contract

L4 Renderer validates locally, without main/authoring-contract reads. Pass selected_widget_id, display, controls, planner_id, interaction_goal and expected_return unchanged to render_html_widget; selected ID is trace metadata, not substitution authority. Only Interaction Pathway enters L4; L2 Planner directly executes on Execution Pathway; only L1 Router emits decision end.

Host Agent Return and Completion belong to L1 and never enter this renderer.

## Inputs

- Identity: nonempty selected_widget_id, widget_id, widget_type, surface, planner_id, purpose, interaction_goal; exact L2 selection/goal and registered type/surface/eligibility.
- `iai`: unchanged chain_id, gap_type, binding reason, maps_to_edge, source_nodes, target_node; named chain and meaningful reason; edge source in source_nodes, destination equals target_node and allowed state_update_target. Require deterministic merge_strategy and next_planner_action "re-enter Layer 1"; never merge canonical state here.
- `display`: actual sketch/legend/brief/candidate references and current unresolved state; every profile source resolves; no invented evidence/defaults/uploads.
- `controls`: unique nonempty id, supported kind, nonempty label/purpose, boolean required, nonempty declared return_keys, applicable constraints for types/limits/source rules.
- `presentation.profile`: nonempty archetype/summary, nonempty content array of records with source "display.<path>", role primary|context|status and meaningful purpose; interaction with nonempty actions/feedback and submission label/preconditions/return_mapping; nonempty semantic appearance and signature_features.
- `expected_return`: exactly L2 keys/types and matching return_mapping keys, actual source/serialization with optional/empty handling; validate before submit, no artificial controls for derived metadata.
- `widget_requirements`: nonempty string arrays visible_information, required_controls, required_behavior, submission_requirements; implement every item consistently with profile/controls/mappings.
- `safety`: allow_html false, allow_script false in L3 input; only L4 writes code. Optional runtime is available/approved with version-pinned libraries; optional reference_assets are plugin-relative design-time principles, never runtime assets.

No success handoff_type. Invalid semantics/missing indispensable evidence/capability returns structured failure to l1-pN3-core-module without rendering or semantic repair. Compile into existing tool arguments only.

## Universal Style and Layout Baseline

Match host typography, neutral surfaces, spacing/borders/focus and density with --iai-* tokens/classes. Remain usable at 266px and desktop, use minmax(0, 1fr) and min-width: 0 on shrinkable children, and prevent page-level overflow-x without clipping content. Only designated regions scroll; preserve canvas aspect and coordinate transforms when resized. Native controls, labels/tooltips, keyboard operation, visible focus, truthful disabled/loading/error/submission states and unobscured messages are required. Keep persistent submit/dismiss/reset in .iai-actions. No confirmation checkbox or decorative nested cards; checkboxes only for actual multi-value boolean settings.

Initialize local state from window.widgetDisplay and guard DOM/data/event lookups. Inline errors must preserve a working dismiss action. No parent DOM, secrets, storage/local files, undeclared network/remote code or browser modal APIs. Only available approved runtime capabilities/libraries; canvas drawing has keyboard-accessible tools and focusable pointer/keyboard drawing support without substituting generic form input for a real sketch.

Render only P3 contracts reached through a fresh `L1 -> L2 -> L3` path. Call `render_html_widget` with `render_mode: "generated"`; do not add frontend files, templates, or task-tool calls. Every return goes to `l1-pN3-core-module`.

## Supported Contracts

- `semantic_sketch_pad`: build a native Canvas drawing surface with pen, eraser, undo, redo, clear, brush width, preset/custom colors, and a co-visible color-to-object legend.
- `sketch_layout_confirmation`: render the prompt, exported sketch preview, color legend, inferred spatial constraints, and accept/revise controls.
- `sketch_layout_image_compare`: render the sketch or prior image against the candidate and collect accept/keep/revise.

Reject any other widget type or a contract that lacks `presentation.profile`.

## Sketch-Pad Requirements

The generated JavaScript must keep each color paired to an editable concrete object label. A color used in a visible stroke cannot be submitted while its `object_label` is blank. Generic roles are optional companion fields only; never offer a role-only legend as valid P3 output.

Track strokes as JSON-compatible normalized point paths with their color. On submit:

1. Rasterize the visible canvas to `image/png` and upload it through `window.uploadWidgetFile`; return the result as `sketch_ref`.
2. Create a second same-sized RGBA canvas with no painted pixels, export it as `image/png`, upload it through `window.uploadWidgetFile`, and return it as `full_canvas_mask_ref`.
3. Call `window.submitWidget` with both refs, strokes, `{width, height}`, the legend as `color_semantics`, and `freeform_note`.

Bind both exports to the same current drawing revision and dimensions. Lock or invalidate submission during edits/uploads; changed strokes or legend invalidate stale exports/confirmation. Require two actual completed uploads before submitting; the mask must remain entirely transparent, not the visible drawing or opaque canvas. Show upload failure inline and never submit partial artifacts. Include a visible dismiss control calling window.dismissWidget(note).

## Asset Handling

For confirmation and comparison, resolve session uploads only through `window.widgetDisplay` and `window.widgetAssetUrl(...)`. Every preview must use this exact pattern, never the ref object or its `url` directly:

```js
function previewUrl(ref) {
	return ref ? window.widgetAssetUrl(ref) : '';
}

sketchImage.src = previewUrl(window.widgetDisplay.before_ref);
candidateImage.src = previewUrl(window.widgetDisplay.after_ref);
```

Render inline unavailable/error state when an actual reference cannot resolve, set image alt text and guard image/data lookups. Confirmation uses display.sketch_ref; comparison uses before_ref/after_ref. Never inline guessed IDs/paths/URLs or access parent DOM, storage, cookies or tokens. Use host --iai-* tokens and .iai-* classes.

## Return Shapes

- Sketch: `{ sketch_ref, full_canvas_mask_ref, strokes, canvas, color_semantics, freeform_note }`
- Confirmation: `{ decision: "accept|revise", revision_request: "", freeform_note: "" }`
- Review: `{ accepted_version: "before|after|none", revision_request: "", freeform_note: "" }`

## Must Not

- Do not call edit_image; L2 directly invokes it only after its confirmed instruction_ready, without L3/L4.
- Do not render a review directly after a tool result; it must first re-enter L1 and be routed through L2 and L3.
- Do not use a template fallback or add files under `frontend/`.
