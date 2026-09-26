---
name: l4-pN10-widget-renderer
description: "Use when: rendering a validated reusable L3 primitive on the persistent P10 Artifact Canvas."
---

# Layer 4 - P10 Canvas Widget Renderer

## Workflow End Boundary

After any widget return or renderer failure, immediately load `l1-pN10-core-module` with the structured result. Layer 4 never decides workflow completion, produces the final response, or continues directly to a planner or executor.

## Render Contract

Use the self-contained Inputs and style rules below; no main skill is a runtime prerequisite. Validate the selected L3 contract and preserve its `selected_widget_id`, `display`, `controls`, `planner_id`, `interaction_goal`, and `expected_return` in the existing render request. Selection is trace metadata, never permission to replace a widget. L4 implements Interaction Pathway only; Execution Pathway, Host Agent Return and Completion do not enter L4.

Accept P10 contracts reached through `L1 → L2 → L3` and generate HTML, CSS, and JavaScript implementing the exact semantic profile. Always call `render_html_widget` with `render_mode: "generated"` and `surface: "artifact_canvas_widget"`. Do not assume a repository-owned template. Preserve `return_mode: agent_interpreted`: the generated interaction may return any JSON values grounded in its actual controls and submission mapping, not a fixed registry field list. L1 interprets the result against the current source and history; flexible serialization never supplies missing decisions, target bindings or final Aug authorization.

Never call `render_html_widget` with empty `html`, `css`, or `js`. In particular, `augmented_instruction_review` must render the generated instruction, actionable operations, complete suggestion decisions, object bindings, and confirm/edit/regenerate/start-over/dismiss controls. A full-canvas overlay with no visible review content is invalid and must be regenerated before the render call.

Ground the widget in the inspected SVG scene. Preserve `artifact_binding`, stable object ids, and `placement`; for object-bound interactions, listen for `artifact_canvas_selection` and update the visible context from `activeObjectId`, `selectedObjectIds`, `object`, and `suggestionsForObject`. The host owns hit testing and iframe placement. Never infer an SVG object id from a label when the scene or selection event supplies a stable id.

Implement bidirectional object binding for every object-grounded row, card, relation endpoint, or operation summary:

- For artifact-to-instruction navigation, an `artifact_canvas_selection` event makes the matching instruction rows the only primary content, marks the row matching `activeObjectId` as active, and moves keyboard focus or scroll position to its first actionable control without discarding decisions on other objects.
- For instruction-to-artifact navigation, clicking or pressing Enter/Space on an instruction row calls `window.focusArtifactBinding(objectIds, primaryObjectId)` with only stable ids from that row's binding. The host validates the ids, selects and highlights the objects, moves the anchored widget beside the primary object, and sends the resulting selection context back to the iframe.

Expose instruction-to-artifact focus as a separate navigation action; it must not accept, edit, reject, submit, or mutate anything. Use visible selected/active states and an object label plus stable id so the relationship is understandable without relying on color.

Render useful loading, empty, stale-binding, editing, and review states when relevant. Use accessible labels, keyboard-operable controls, visible focus, and no color-only status indicators. Initialize from `window.widgetDisplay`; validate and serialize exactly the declared submission mapping through `window.submitWidget(values)`, and dismiss through `window.dismissWidget(note)`. Do not access the parent DOM, fetch artifact URLs, or apply patches inside the iframe.

For suggestion contracts, consume `{type: "artifact_canvas_selection", widgetId, selectedObjectIds, activeObjectId, object, suggestionsForObject}`. Render only `suggestionsForObject`; never keep another object's content visible after selection changes. Preserve decisions for suggestions bound to other objects. The host remains the authority for hit testing and stable ids; ignore messages for another widget id.

P10 widgets keep the source read-only. Do not apply a preview to the source or invoke a patch endpoint. Every typed widget return re-enters `l1-pN10-core-module`, where the Agent interprets it against the current SVG scene and interaction history.

Do not add external libraries or a second SVG rendering engine.

## Inputs

Validate locally, no external read/success handoff_type:
- Identity: nonempty exact selected_widget_id, instance widget_id, registry widget_type/surface, planner_id, purpose, unchanged interaction_goal/eligibility.
- `iai`: unchanged L2 chain_id/gap_type/reason/source_nodes/maps_to_edge/target_node; named chain/meaningful reason, edge source in sources, destination=target and allowed state_update_target; deterministic L1 merge_strategy; next_planner_action:"re-enter Layer 1"; no merging here.
- `display`: actual sources/revisions/values/unresolved status, all content sources resolve, no fabricated evidence.
- `controls`: unique nonempty id, supported kind, nonempty label/purpose, boolean required, nonempty declared return_keys and typed/limit/source/edit constraints.
- `presentation.profile`: nonempty archetype/summary; nonempty content records with resolvable source:"display.<path>", role:primary|context|status, meaningful purpose; interaction nonempty actions/feedback; submission nonempty label/preconditions/exact return_mapping; nonempty semantic appearance/signature_features.
- `expected_return`: preserve exactly L2 keys/types for this contextual agent-interpreted interaction and identical mapping keys with actual source/serialization/optional-empty handling; no artificial metadata controls or enforcement of static domain keys.
- `widget_requirements`: four nonempty string arrays visible_information/required_controls/required_behavior/submission_requirements; implement every item consistently with profile.
- `safety`: allow_html:false, allow_script:false in L3; only L4 implements code. Optional runtime approved available capabilities/pinned libraries; optional reference_assets plugin-relative design-time only.
Failure returns structured renderer error to l1-pN10-core-module without rendering/repair. Compile into existing render_html_widget fields; preserve artifact_binding/placement/selected_widget_id, no new host/tool arguments.

## Universal Style and Layout Baseline

Match host typography, neutral surfaces, borders, spacing, focus and density. Usable at 266px iframe and desktop; minmax(0,1fr), min-width:0, no page overflow-x, designated internal scroll only. Labels/status/errors never overlap controls. Native accessible keyboard/focus/disabled/loading/validation states; icons have names/tooltips. Reachable persistent .iai-actions submit/dismiss/reset. Primary submission confirms current values; no approval checkbox/extra gate (checkboxes only real boolean settings). Light surface/dark text by default; justified dark design readable light labels/text. No nested decorative cards/marketing copy.

Keep source SVG read-only for every instruction widget. Suggestion/relation/operation values are semantic, no patches. Final concrete Aug confirmation returns to L1 before L2 Host checks/execution. Preserve current suggestion IDs/source revision/interaction binding/provenance, unfinished values and bidirectional object/row focus. Revision comparison uses exact host-owned Before/After snapshots with visible swatches, never raw SVG. Use only existing host APIs window.submitWidget/window.dismissWidget and approved focus/selection APIs already documented, window.widgetAssetUrl(ref) for actual assets. No parent DOM/fetch/raw SVG/remote libraries/tool calls. All outcomes return to l1-pN10-core-module, only L1 decision:end.
