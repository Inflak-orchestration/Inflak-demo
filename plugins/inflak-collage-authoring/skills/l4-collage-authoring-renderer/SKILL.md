---
name: l4-collage-authoring-renderer
description: "Use when: rendering one validated unified SVG interaction contract on the persistent Artifact Canvas."
---

# Layer 4 - Unified Collage Authoring Renderer

## Workflow End Boundary

After any widget return or renderer failure, immediately load `l1-collage-authoring-core` with the structured result. Layer 4 never decides workflow completion, produces the final response, or continues directly to a planner or executor.

## Render Contract

Use the self-contained Inputs and style rules below; no main skill is a runtime prerequisite. Validate the selected L3 contract and preserve `selected_widget_id`, `display`, `controls`, `planner_id`, `interaction_goal`, and `expected_return` in the existing render request. Selection is trace metadata, never permission to replace a widget. L4 implements Interaction Pathway only; Execution Pathway, Host Agent Return and Completion do not enter L4.

## Role

Validate and render only contracts produced through Layer 1, Layer 2, and a registered Layer 3 interaction skill. Call `render_html_widget` on `artifact_canvas_widget`; do not diagnose gaps, choose interactions, call task tools, inspect raw SVG, or change return semantics.

## Rendering

- Object grounding and relation controls anchor to stable object bounding boxes.
- `svg_proposal_review` must call `render_html_widget`; anchor the widget beside the recommended proposal's first stable target, preserve every proposal's `selected_stable_ids`/`target_hypotheses`, and let Canvas selection move the widget to another related object.
- Typed operation controls expose only object capabilities and planner-provided values; Canvas previews are reversible.
- `artifact_color_palette` anchors to the generated interaction's stable target ids, renders current and artifact-aware colors as swatches, and previews only capability-compatible fill, stroke, or text-color operations.
- `svg_collage_layout_board` uses the live SVG scene as its spatial stage. Keep Canvas and object-list selection synchronized; host draft transforms, guides, region assignments, undo/redo/reset, and Apply remain in artifact coordinates and never become iframe-authored SVG.
- Candidate selection shows only current-session bound assets and provenance.
- Augmented-intent review uses a Canvas overlay. Artifact review uses the inspector sidebar so the revised SVG remains visible.
- In `create`, keep the host-native object inspector visible beside the Canvas. Selecting a stable object binds palette presets, candidate cutouts, copy options, font family, font size, font weight, fill/stroke, transform, layer order, add, replace, and remove controls from the canonical scene and `authoring_bundle`.
- `svg_artifact_review` must render in the inspector sidebar, never as a Canvas overlay. Keep the revised artwork visible while the user checks validation, accepts the revision, or requests a bounded follow-up.
- The host owns SVG hit testing, active selection, transient annotations, previews, patch commit, revision refresh, and stale-state messages.
- Adaptive interactions preserve `interaction_id` and the exact `base_revision`. Adjust and Reset update host-owned preview state only; Regenerate, Reject, and Dismiss do not mutate the artifact; only Apply may return complete typed operations for a later patch pass.

Initialize from `window.widgetDisplay` and render nonempty sandboxed HTML/CSS/JS implementing the exact profile with `render_mode: "generated"`. Validate and serialize exactly its submission mapping through `window.submitWidget(values)` or dismiss through `window.dismissWidget(note)`. Runtime assets use `window.widgetAssetUrl(ref)` only. The layout-board reset exception and host-owned draft protocol below do not authorize arbitrary APIs. Never access parent DOM, fetch artifact URLs, invoke tools, or load external libraries.

Do not reduce any required interaction to explanatory prose, Markdown tables, JSON examples, or a request for a chat reply. Calling the renderer and waiting for its structured return is mandatory. Candidate assets render as image thumbnails, palettes as swatches, fonts in their represented family, numeric values as typed controls, and object operations as concrete commands.

## Return

Submit exactly the Layer 3 `expected_return`. For operation returns preserve exact artifact id, `base_revision`, and typed operations. The iframe never applies them. Every return re-enters `l1-collage-authoring-core`.

## Safety

Reject raw SVG/XML/CSS selectors, scripts, handlers, path data, URLs, data URIs, undeclared keys, stale artifact bindings, and operation values not present in the semantic contract.

Preserve host-native inspector, selection, preview and sidebar behavior. Do not repair missing semantics or add undocumented host/API arguments.

## Inputs

Validate locally, no external read/success handoff_type:
- Identity: nonempty exact selected_widget_id, instance widget_id, registry widget_type/surface, planner_id, purpose, unchanged interaction_goal/eligibility.
- `iai`: unchanged L2 chain_id/gap_type/reason/source_nodes/maps_to_edge/target_node; named chain/meaningful reason, edge source in sources, destination=target and allowed state_update_target; deterministic L1 merge_strategy; next_planner_action:"re-enter Layer 1"; no merging here.
- `display`: actual source/revision/values/unresolved status, all profile content sources resolve, no invented evidence.
- `controls`: unique nonempty id, supported kind, nonempty label/purpose, boolean required, nonempty declared return_keys, typed/limit/source/edit constraints.
- `presentation.profile`: nonempty archetype/summary; nonempty content records resolvable source:"display.<path>", role:primary|context|status, meaningful purpose; interaction nonempty actions/feedback; submission nonempty label/preconditions/exact return_mapping; nonempty semantic appearance/signature_features.
- `expected_return`: exactly L2 keys/types and identical mapping keys with producible sources/serialization/optional-empty handling; preserve declared host-enriched layout fields, no artificial metadata controls/extra keys.
- `widget_requirements`: four nonempty string arrays visible_information/required_controls/required_behavior/submission_requirements; implement every item consistently.
- `safety`: allow_html:false, allow_script:false in L3; only L4 codes. Optional runtime approved available capabilities/pinned libraries; reference_assets plugin-relative design-time only.
Failure returns structured renderer error to l1-collage-authoring-core without render/repair. Compile into existing render_html_widget fields, preserve artifact_binding/placement/selected_widget_id.

## Universal Style and Layout Baseline

Match host typography/neutral surfaces/borders/spacing/focus/density. Usable at 266px iframe and desktop; minmax(0,1fr), min-width:0, no page overflow-x, designated internal scroll only. Labels/status/errors never overlap. Native accessible keyboard/focus/disabled/loading/validation controls, named icons/tooltips. Persistent reachable .iai-actions submit/dismiss/reset, primary submission confirms state; no approval checkbox/extra gate, real boolean settings only. Light surface/dark text default; justified dark design readable light labels/text. No nested decorative cards/marketing.

The layout board listens for `artifact-layout-draft` with `event.detail.activeObjectId`, `itemTransforms`, and `baseRevision`. Only this board may call `window.resetArtifactLayoutDraft()`. Apply uses `window.submitWidget({action:"apply",interaction_id})` without geometry; the host enriches exact binding/revision and changed typed operations. Declare these host-derived sources in the return mapping, not artificial controls. Reset stays open; Regenerate/Reject/Dismiss never submit draft geometry or mutate. Do not reconstruct host geometry in the iframe. Listen for `artifact_canvas_selection` for stable IDs and preserve artifact coordinates under zoom.
All previews/annotations host-owned transient until explicit Apply; host validates IDs/revision/typed allowlists atomically; if already committed, return actual result to L1 without replay. Stale revision fails to L1, never silently refresh/replay. svg_artifact_review stays sidebar not overlay, create inspector remains visible, proposals anchored automatically. Revision comparison uses host-owned Before/After snapshots with exact source/revisions and color swatches. No parent DOM/fetch/raw SVG/network/tools. Only L1 merges/decision:end.
