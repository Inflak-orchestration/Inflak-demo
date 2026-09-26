---
name: l4-pN12-widget-renderer
description: "Use when: rendering a P12 prompt-and-artifact-derived adaptive interaction or artifact review on the persistent Artifact Canvas."
---

# Layer 4 - P12 Widget Renderer

## Workflow End Boundary

After any widget return or renderer failure, immediately load `l1-pN12-core-module` with the structured result. Layer 4 never decides workflow completion, produces the final response, or continues directly to a planner or executor.

## Inputs

Validate locally, no external read/success handoff_type:
- Identity: nonempty exact selected_widget_id, instance widget_id, registry widget_type/surface, planner_id, purpose, unchanged interaction_goal/eligibility.
- `iai`: unchanged L2 chain_id/gap_type/reason/source_nodes/maps_to_edge/target_node; named chain/meaningful reason, edge source in sources, destination=target and allowed state_update_target; deterministic L1 merge_strategy; next_planner_action:"re-enter Layer 1"; no merging here.
- `display`: actual sources/revisions/values/unresolved status and resolvable content sources, no invented evidence.
- `controls`: unique nonempty id, supported kind, nonempty label/purpose, boolean required, nonempty declared return_keys, typed/limit/source/edit constraints.
- `presentation.profile`: nonempty archetype/summary; nonempty content records resolvable source:"display.<path>", role:primary|context|status, meaningful purpose; interaction nonempty actions/feedback; submission nonempty label/preconditions/exact return_mapping; nonempty semantic appearance/signature_features.
- `expected_return`: exactly L2 keys/types and identical mapping keys with producible sources/serialization/optional-empty handling; preserve declared host-enriched layout metadata; no artificial metadata controls/extra keys.
- `widget_requirements`: four nonempty string arrays visible_information/required_controls/required_behavior/submission_requirements; implement every item consistently.
- `safety`: allow_html:false, allow_script:false in L3; only L4 codes. Optional runtime approved available capabilities/pinned libraries; reference_assets plugin-relative design-time only.
Failure returns structured renderer error to l1-pN12-core-module without render/repair. Compile into existing render_html_widget fields, preserve exact artifact_binding/placement/selected_widget_id.

## Universal Style and Layout Baseline

Match host typography/neutral surfaces/borders/spacing/focus/density. Usable at 266px iframe and desktop; minmax(0,1fr), min-width:0, no page overflow-x, designated internal scroll only. No labels/status/errors overlapping. Native accessible keyboard/focus/disabled/loading/validation controls, icons named/tooltipped. Persistent reachable .iai-actions submit/dismiss/reset; primary Apply confirms current state; no approval checkbox/extra gate, real boolean settings only. Light surface/dark text default; justified dark design readable light labels/text. No decorative card nesting/marketing.

Retain exact layout protocol: listen artifact-layout-draft; read event.detail.activeObjectId/itemTransforms/baseRevision. Reset window.resetArtifactLayoutDraft() stays open. Apply window.submitWidget({action:"apply",interaction_id}) without geometry; host injects authoritative binding/current revision/changed typed operations. Other actions never submit drafts; no iframe-local reconstruction. Selection artifact_canvas_selection supplies stable IDs. All host previews/annotations transient until explicit Apply. Real candidates use window.widgetAssetUrl(ref), no fetch. Add revision comparison: host-owned exact Before/After snapshots/current validation/color swatches, no raw SVG. Keep existing adaptive/capability/palette/variant/review rules. All returns/failures re-enter l1-pN12-core-module; no stale replay, host-committed patches never double-execute.

## Role

Generate the HTML, CSS, and JavaScript needed for one P12 interaction, call `render_html_widget` with `render_mode: "generated"`, and return the user's response to Layer 1. Preserve `surface: artifact_canvas_widget`, planner id, artifact binding, base revision, and patch safety semantics. Do not load or assume a repository-owned widget template.

After every submit or dismiss, return control to `l1-pN12-core-module`. Do not continue directly to another widget, planner action, or task tool from Layer 4.

## Rendering

- `adaptive_refinement_interaction`: render the task-specific control subset from `display.interaction_spec`, highlight `default_target_ids`, and show the generated result as a reversible preview. Do not replace the generated controls with a fixed approval form.
- `refinement_control`: render only capability-compatible direct-manipulation and typed controls declared by the interaction spec while the host owns reversible preview and handles.
- `artifact_color_palette`: anchor the palette to the primary target, render current and suggested colors as swatches plus a custom color input, switch only among supported fill/stroke/text channels, and synchronize every choice with the host-owned target preview. Keep the target visible.
- `svg_collage_layout_board`: use the live SVG scene as the stage, synchronize Canvas and object-list selection, show stable labels, direct drag and four-corner resize handles, layer order, grid/snap/alignment guides, undo/redo/reset, and optional named region assignment. The board must dominate the layout and must not become a list of numeric fields. Listen for the iframe `artifact-layout-draft` event and read `event.detail.itemTransforms` to keep selected-object values synchronized. Reset must call `window.resetArtifactLayoutDraft()` without submitting. Apply must call `window.submitWidget({action:"apply",interaction_id:...})`; the host injects authoritative artifact binding and typed operations from its draft. Never reconstruct operations from iframe-local geometry.
- `semantic_variant_review`: show already materialized candidates in artifact context with only spec-declared placement controls; never fetch assets from widget code.
- `refined_artifact_review`: show revision metadata, applied changes, validation, remaining issues, and accept/continue/revise actions.

The generated script may call `window.submitWidget(values)`, `window.dismissWidget(note)`, and, only for `svg_collage_layout_board`, `window.resetArtifactLayoutDraft()`. For object correction, listen for `artifact_canvas_selection` and use its stable ids. The iframe never applies a patch. After the Agent interprets the response and separately proposes an `I→A` operation, the host still verifies artifact id, `base_revision`, stable object ids, and allowlisted operations before committing atomically. On revision conflict, require a fresh planner pass; never replay the old patch.

Interaction annotations and previews are host-owned transient overlays. They may highlight existing stable objects and visualize typed operations, but they must not be serialized into SVG before Apply. The default state is always GenAI's generated interaction and result; never render an empty target picker or abstract approval card as the first interaction.

## Must Not

- Do not access parent DOM, inspect SVG markup, fetch artifact URLs, or load external libraries.
- Do not submit raw SVG, XML, CSS, selectors, scripts, path data, URLs, data URIs, or undeclared keys.
- Do not render in the hidden conversation transcript.
- Do not create or export Aug.