---
name: l4-pN8-widget-renderer
description: "Use when: rendering a P8 collage object-control contract inside the persistent Artifact Canvas inspector."
---

# Layer 4 - P8 Widget Renderer

## Workflow End Boundary

After any widget return or renderer failure, immediately load `l1-pN8-core-module` with the structured result. Layer 4 never decides workflow completion, produces the final response, or continues directly to a planner or executor.

## Inputs

Validate the complete L3 semantic contract locally, no external read or success handoff_type:
- Identity: nonempty exact selected_widget_id, instance widget_id, registry widget_type/surface, planner_id, purpose, unchanged interaction_goal and eligibility.
- `iai`: unchanged L2 chain_id/gap_type/reason/source_nodes/maps_to_edge/target_node; named chain/meaningful reason, source includes edge origin, destination=target and allowed state_update_target; deterministic L1 merge_strategy and next_planner_action:"re-enter Layer 1"; never merge here.
- `display`: grounded actual values/source/revision/unresolved status, all content sources resolve; no fabricated data.
- `controls`: unique nonempty id, supported kind, label/purpose, boolean required, nonempty declared return_keys and typed/limit/source/edit constraints.
- `presentation.profile`: nonempty archetype/summary; nonempty content records with resolvable source:"display.<path>", role:primary|context|status and meaningful purpose; interaction nonempty actions/feedback and submission nonempty label/preconditions/exact return_mapping; semantic appearance/signature_features nonempty.
- `expected_return`: exactly L2 keys/types and identical mapping keys with actual producible sources/serialization/optional-empty handling; validate values, no artificial metadata controls.
- `widget_requirements`: four nonempty string arrays visible_information/required_controls/required_behavior/submission_requirements; implement every item consistently with profile.
- `safety`: allow_html:false, allow_script:false in L3; only L4 creates code. Optional runtime approved available capabilities/pinned libraries; reference_assets plugin-relative design-time only.
Missing/inconsistent semantics or capabilities return structured renderer failure to l1-pN8-core-module, no render or repair. Compile semantic contract into existing render_html_widget fields, not new API arguments. Preserve artifact_binding/placement/selected_widget_id.

## Universal Style and Layout Baseline

Match host typography, neutral surfaces, borders, spacing, focus and density. Usable at 266px iframe and desktop; minmax(0,1fr), min-width:0, no page overflow-x; only designated internal scroll. Labels/status/errors never overlap. Native accessible controls, keyboard/focus/disabled/loading/validation; familiar icons with accessible names/tooltips. Reachable persistent .iai-actions submit/dismiss/reset. Primary Apply/Add/Remove confirms displayed values; no approval checkbox or extra confirmation stage. Checkboxes only genuine boolean/multivalue settings. Light surface/dark text by default; any justified dark design requires readable light text/labels. No decorative card nesting/marketing copy.

Retain all P8 object/preset/candidate/alpha/provenance/coordinate/typed-operation constraints and host commit behavior. Add revision comparison handling: host-owned Before/After snapshots bound to exact fileId/revisions, never raw SVG or invented image; acceptance only returns to L1. Retain window.widgetDisplay, window.widgetAssetUrl(ref), window.submitWidget, window.dismissWidget existing usage; no fetch/network/generation/parent DOM. Host-committed patches return actual next scene/revision to L1, never replay via L2.

## Layer & Role

Validate one P8 Layer 3 contract, generate sandboxed HTML/CSS/JS, call `render_html_widget`, and return structured values to Layer 1. Preserve `surface: artifact_canvas_widget` and `artifact_binding`; the host places the iframe beside the live collage. Do not diagnose gaps or change patch semantics.

## Rendering

- `collage_object_selector`: render a compact candidate list; the host Canvas performs object hit testing and synchronizes selected ids.
- `collage_visual_style_control`: render 2-4 prepared artifact-specific presets with names, rationales, swatches, affected objects, reversible preview, and atomic apply.
- `collage_asset_replacement_control`: render an object-anchored gallery of 1-3 prepared current-session candidates, all different from the current asset, with thumbnail, label, preparation-kind badge, rationale, reversible preview, and apply.
- `collage_element_style_control`: render native fill, stroke, stroke-width, and opacity controls from canonical object presentation. Apply emits only `set_object_style` and never rasterizes the object.
- `collage_element_insert_control`: render 1-3 pre-generated addable elements with thumbnail, provenance badge, default placement preview, and Add. Add emits only `add_cutout`.
- `collage_object_actions_control`: render a confirmed Remove command for one unlocked object. Remove emits only `remove_object`.
- `collage_transform_control`: render x/y/width/height/rotation fields, aspect lock, reset, apply, and dismiss. The host Canvas owns direct handles and live preview.
- `collage_layer_control`: render explicit front/forward/backward/back commands and current stack context.
- `collage_text_control`: render prepared copy and typography choices plus text, font family, weight, size, color, and alignment controls with apply/dismiss.
- `collage_review`: render accept/continue/revise actions.

Use the shared widget design system. Generate no fixed template and load no external library. Copy `selected_widget_id` unchanged from Layer 3 into `render_html_widget`; use it only for registry trace/observability, never to change widget UI semantics or select or replace a widget. Call:

```json
{"title":"display title or interaction goal","widget_type":"collage_transform_control","selected_widget_id":"<copied-from-L3>","render_mode":"generated","html":"semantic markup","css":"layout only","js":"event wiring that calls window.submitWidget(values) or window.dismissWidget(note)","height":420,"surface":"artifact_canvas_widget","artifact_binding":{"artifact_id":"","object_ids":[]},"planner_id":"pN8-collage-control","interaction_goal":"transform_collage_object","expected_return":{}}
```

For `I→A` controls, submit the exact allowlisted operation shape from `expected_return`; do not apply it inside the iframe. The host intercepts the return, commits the patch against `base_revision`, refreshes the SVG and scene, then sends the normalized widget return so control re-enters `l1-pN8-core-module`.

Authoring widgets consume only options embedded in their Layer 3 contract. When a contract cites an image, read the complete host-supplied reference from `window.widgetDisplay` and assign only `window.widgetAssetUrl(ref)` to its image URL sink. Never use `.path` or `.url` directly, construct `file://`, or invent an asset id or remote image URL; show an explicit unavailable state when absent. Widgets must not call `fetch`, generate an image, submit a prompt, or fabricate an operation or `fileId`. Preset operations are indivisible: preview all of them locally and return all of them together on Apply.

## Must

- Keep the live artifact visible and the active object identity explicit.
- Provide Apply and Dismiss actions.
- Return JSON-compatible values with no extra keys.
- Keep preview changes reversible until Apply.
- Make labels, recommendations, and option ordering specific to the live collage rather than generic editor categories.

## Must Not

- Do not access parent DOM, fetch artifact URLs, rewrite SVG, or load libraries.
- Do not call GenAI, image generation, chat submission, or any network API after user interaction.
- Do not submit arbitrary selectors, XML, CSS, path data, or event handlers.
- Do not render P8 widgets in the hidden conversation transcript.

## Next

Wait for the return, then re-enter `l1-pN8-core-module`.