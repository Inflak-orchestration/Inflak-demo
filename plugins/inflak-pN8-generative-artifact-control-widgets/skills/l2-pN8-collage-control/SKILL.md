---
name: l2-pN8-collage-control
description: "Use when: P8 routed a themed SVG collage generation or object-level collage control request."
---

# Layer 2 - P8 Collage Control Planner

## Layer & Role

L2 diagnoses and plans one evidence-grounded pass. For an interaction gap select one eligible widget; for `instruction_ready`, load `exec-pN8-collage-authoring` with the ready tool/main_model plan, then return every actual result/failure to L1. Execution never loads L3/L4. Do not author widget profiles, render UI or decide Completion.

Load the [execution skill](../exec-pN8-collage-authoring/SKILL.md) as needed for preparation, composition and manager operations; it is not a skill layer.

## Widget Routing

For a widget-path gap, query the plugin-local `registry/widgets.json` after diagnosis. Filter entries by `compatible_planners`, `gap_categories`, `interaction_goals`, `iai_edges`, expected-return coverage, and required artifact, runtime, and renderer availability. Select one eligible widget registry entry and write only its `id` to `gap_requests[0].selected_widget_id`; do not copy registry-derived concrete metadata into the handoff. Layer 3 validates and realizes the selected entry; it does not select or replace it. This layer does not author the semantic widget contract or render UI.

## Inputs

Read the selected `core_handoff.state_snapshot`. Require `user_text`; optionally read `source_prompt`, `asset_plan`, `cutout_assets`, `authoring_preparation_queue`, `prepared_authoring_results`, `collage_artifact`, `collage_scene`, `authoring_bundle`, `active_style_preset_id`, `control_opportunities`, `selected_object_ids`, `prior_returns`, `generation_state`, and `acceptance_state`. Use the newest valid artifact revision and authoring return.

## IAI Domain Binding

| Node | P8 binding |
| --- | --- |
| `H` | User who supplies a theme and manipulates the collage. |
| `T` | Theme, purpose, optional copy, and visual constraints. |
| `I` | Object selection, style choice, asset choice, text edits, transforms, layer commands, and review. |
| `Aug` | Compiled asset-generation, composition, or explicit new-generation instruction. |
| `A` | Transparent cutouts, candidate assets, layered SVG collage, scene manifest, and authoring bundle. |
| `G` | GenAI that plans/generates the first scene and prepares bounded in-situ authoring options. |

## Interaction Paradigms

| paradigm | ordered edges | function |
| --- | --- | --- |
| `intent-completion` | `H→T → I→Aug` | Resolve only material theme, canvas, or text intent. |
| `asset-generation` | `Aug→G → G→A` | Generate one missing isolated theme-consistent source asset per pass. |
| `cutout-extraction` | `A→G → G→A` | Extract a clean transparent object when a generated source is not already transparent. |
| `svg-composition` | `A→Aug → Aug→G → G→A` | Compose accepted cutouts and text, then adopt the result as one canonical SVG document. |
| `authoring-option-generation` | `A→G → G→A → G→I` | Prepare bounded style presets, replacement assets, copy choices, and object-bound controls before review. |
| `direct-authoring` | `H→I → I→A` | Apply deterministic style, asset, text, transform, or order patches from prepared options. |
| `explicit-new-generation` | `H→T → I→Aug → Aug→G → G→A` | Generate beyond the prepared bundle only after an explicit free-form user request. |
| `acceptance` | `I→A` or `I→Aug` | Accept or request a bounded follow-up. |

## Gap / Paradigm Diagnosis

Assess all registered interaction categories as `resolved`, `open`, or `not applicable` from current evidence and explicit scoped delegation, recording the missing per-edge transformation and consequence of guessing in `iai_binding.reason` or execution purpose. Silence is not delegation. Preparation, asset generation, extraction, composition, bundle synthesis and control-opportunity synthesis are `instruction_ready` work, not widget gaps. Each bounded preparation pass requires its own inputs/permission and cannot authorize final work while material choices remain open.

The actual widget registry has no theme/canvas/text-intent/new-generation designer. If theme, consequential canvas choice, central copy or the scope of new generation is missing, return the unresolved evidence and a concrete clarification request to L1 for Host Agent Return; do not invent a widget or treat missing input as execution permission. Preserve valid supplied choices. An explicit new-generation request, including review's `revision_request`, may authorize bounded execution preparation after L1 has merged it.

| gap | condition | edge | interaction goal |
| --- | --- | --- | --- |
| `asset_generation_ready` | An asset plan item lacks a source image. | `Aug→G→A` | Generate exactly one isolated object with the approved theme/style; name `generate_image`. |
| `cutout_extraction_ready` | A source exists but needs transparent extraction. | `A→G→A` | Extract confirmed objects; name `extract_collage_cutouts`. |
| `svg_composition_ready` | Every item in the inferred asset plan is accepted, the default rich profile has at least four cutouts, and no collage artifact exists. A lower count is allowed only when the user explicitly requests a sparse/minimal composition. | `Aug→G→A` | Compile stable objects with `compose_svg_collage`; its result must be adopted by `manage_svg_document`. |
| `authoring_bundle_preparation` | Planned assets or an existing collage lack complete bounded authoring options. | `A→G → G→A` | Execution preparation: invoke one registered capability provider for a missing real asset, or `main_model` to assemble options from actual results; return to L1. |
| `control_opportunity_preparation` | The authoring bundle exists but supported object-bound controls have not been identified. | `G→I` | Execution preparation: `main_model` derives control opportunities from actual scene/capability/bundle evidence; return to L1 before selecting a registered interaction. |
| `collage_object_selection_gap` | The requested edit lacks a stable object id. | `G→I` | select_collage_objects |
| `object_target_gap` | A target remains ambiguous after current scene inspection. | `G→I` | select_collage_objects |
| `svg_element_style_gap` | A native object's supported fill/stroke/opacity choice needs user input. | `I→A` | edit_svg_element_style |
| `collage_element_insertion_gap` | Prepared addable elements need a concrete selection/placement decision. | `I→A` | insert_prepared_collage_element |
| `collage_object_actions_gap` | Removal of a known unlocked object needs its concrete command. | `I→A` | remove_collage_object |
| `collage_visual_style_gap` | Prepared global visual-style presets are available. | `I→A` | apply_collage_visual_style |
| `collage_asset_replacement_gap` | A selected cutout has prepared session asset candidates. | `I→A` | replace_collage_asset |
| `collage_object_transform_gap` | A known cutout needs move, resize, or rotation. | `I→A` | transform_collage_object |
| `collage_object_position_gap` | A known object's position remains materially unspecified. | `I→A` | transform_collage_object |
| `collage_layer_order_gap` | A known object needs z-order adjustment. | `I→A` | reorder_collage_object |
| `collage_text_edit_gap` | A known text object needs content or style changes. | `I→A` | edit_collage_text |
| `artifact_comparison_gap` | A collage revision increased and has not been compared with its immediately preceding revision. | `I→A` | compare_svg_revisions |
| `collage_acceptance_gap` | A generated or materially revised collage awaits review. | `I→A` | review_collage |

## Planning Rules

### Capability-driven authoring

Read `registry/authoring-capabilities.json` and `registry/tools.json.authoring_reference_routes` before choosing an authoring executor. Classify each opportunity by capability ID and execution skill binding, preserving capability and route IDs in `authoring_preparation_queue`. The provider must occur in declared `preparation_tools`; its actual result must bind to `result_binding` before the widget can render. `exec-pN8-collage-authoring` executes the L2 plan and invokes the provider, not a L3 skill.

Use this ordered protocol for every generative or derived authoring option:

1. L2 emits one `instruction_ready` handoff naming `authoring_capability_id`, stable target object id when applicable, candidate kind, label, rationale, and one registered external tool.
2. L2 validates the selected capability/provider and hands the ready plan to `exec-pN8-collage-authoring`. The result returns through Layer 1; do not render a widget in the same pass.
3. L1 merges the real returned `fileId`, `kind`, `source_tool`, and source/target identity into the planned `authoring_bundle.asset_candidates_by_object`, `authoring_bundle.addable_elements`, or complete visual style preset binding.
4. Only after the bounded options are complete may L2 hand composition to the execution skill, or send its selected interaction registry entry to Layer 3 design and Layer 4 rendering. Composition never enters L3/L4.
5. Widget interaction emits only the capability's `apply_operations`; `manage_svg_document` commits them locally.

Capability mapping:

- Whole-collage style uses prepared combinations of `generate_image`, `restyle_image`, `adjust_image`, or `apply_filter`, then `collage_visual_style_control` applies `set_canvas_style`, `update_text`, and prepared `replace_cutout_asset` operations atomically.
- Native SVG element style routes through the capability's registered widget and applies only `set_object_style` for fill, stroke, stroke width, and opacity. It does not rasterize the object or call an image provider.
- Element style uses `restyle_image`; semantic element changes use `edit_image`; expansion uses `outpaint_image`; alternatives use `generate_variations`; background treatment uses only `remove_background`; raster geometry uses `transform_image`; tonal/filter appearance uses `adjust_image` or `apply_filter`. Every result must retain actual transparent pixels before it becomes an object-bound candidate consumed by `collage_asset_replacement_control`; apply emits only `replace_cutout_asset`.
- New element generation uses `generate_image` and optionally `extract_collage_cutouts`, binds the result to `addable_elements`, then `collage_element_insert_control` applies only `add_cutout`.
- Removal, SVG transform/order, and text changes require no image preparation. Their widgets apply `remove_object`, `set_transform`, `set_order`, `add_text`, or `update_text` locally.

For a new collage, default to `composition_profile: rich` unless the user explicitly asks for a sparse or minimal result. A rich first version is a complete editorial collage or poster, not a sparse arrangement that merely satisfies the compiler minimum. Infer a plan of 4-6 independently editable transparent cutout objects plus 3-5 independently editable text objects. Do not call `compose_svg_collage` until every planned primary object is accepted. Prefer one generation call per missing cutout so every tool result returns through L1. Prompt each source as one isolated full object, visually coherent with the shared theme, and require `background: transparent` plus `require_transparent_background: true`. Reject results without actual transparent pixels; if extraction is needed, only the alpha-validated extracted cutout may proceed. Compose only accepted assets. Use 1200x1200 by default unless the purpose implies a poster ratio such as 1200x1600.

Build the rich plan with a visible content hierarchy: one dominant hero, supporting characters or thematic companion objects, 2-3 secondary visual assets such as props, symbols, frames, labels, stickers, or texture accents, and meaningful overlap across foreground, middle ground, and background. Text should contribute poster-like information density: one title, one subtitle or context line, and 1-2 short slogans or energetic phrases, with an optional date, credit, or callout when the theme supports it. Vary scale, crop, rotation, and z-order; use intentional asymmetry and controlled negative space rather than distributing a few objects evenly. Decorative assets must reinforce the theme and must remain independently editable instead of being baked into a background.

If the user explicitly requests minimalism, a sparse composition, or only named supplied objects, record `composition_profile: minimal` and follow that constraint; otherwise do not reinterpret a short user prompt as a request for sparse output. The compiler's two-cutout requirement is only a technical floor, never the default creative target.

Before review, prepare one bounded `authoring_bundle`. It contains 2-4 named `visual_style_presets`, 1-3 `asset_candidates_by_object` entries for every replaceable cutout, and `text_authoring_options` for each text object. Each option includes a concise artifact-specific label and rationale. Every raster candidate must already exist in the current session, carry a `fileId`, differ from that cutout's current `asset_file_id`, and be unique within its object gallery. Keep candidate generation bounded: reuse a candidate across compatible style presets, but never count the current primary asset as a replacement candidate.

Treat candidates as generation-plan items, not prose suggestions. Before composition, generate the primary cutouts and 1-3 alternate assets for every cutout. Record each returned `fileId` under its stable target object id. Do not count layout, rotation, color sliders, duplicate assets, or the primary asset as authoring candidates. Do not render or review the artifact until these galleries are complete.

Each visual preset contains only allowlisted deterministic operations. Raster style changes require pre-generated candidate assets referenced by `replace_cutout_asset`; never promise an on-click restyle. Text presets use `update_text`, and background changes use `set_canvas_style`. Asset candidates remain bound to one stable cutout id and preserve that object's transform and z-order.

After composition and authoring-option generation, inspect `collage_scene.objects` and propose only controls supported by object type and prepared data. Cutouts support prepared asset replacement, transform, and layer order; text supports prepared copy and typography choices plus free-form content, font family, font weight, size, fill, alignment, transform, and layer order. Global style controls require at least two complete presets. If the user names a clear object, skip selection. Deterministic edits never name a GenAI executor: emit an `I→A` gap whose expected return is an allowlisted patch, then the downstream interaction returns typed operations for the host to commit.

After any successful deterministic patch, use the returned canonical scene and revision. Mark only the applied opportunity complete and preserve unapplied authoring options. Before `collage_acceptance_gap`, emit `artifact_comparison_gap` once for the immediately preceding and revised SVG revisions and route it to `svg_revision_comparison`. Never end the loop with a patch acknowledgement alone.

The direct patch allowlist is `set_transform`, `set_order`, `set_object_style`, `add_cutout`, `remove_object`, `add_text`, `update_text`, `replace_cutout_asset`, and `set_canvas_style`. Submit confirmed operations through `manage_svg_document` with `action: patch`; do not invent arbitrary SVG, selector, style, path, or XML operations. A style preset may return multiple allowlisted operations in one revision; preserve their declared order and submit them atomically.

## SVG Document Manager

Use `manage_svg_document` only through an `instruction_ready` handoff naming the registered executor:

- After `compose_svg_collage`, use `action: adopt_generated`, its exact `file_id`, and `scene_kind_hint: collage` if the compose tool has not already returned `artifactType: svg-document` plus a canonical scene.
- For an uploaded or restored SVG lacking canonical `inflak-svg-scene` state, use `action: import`, exact `file_id`, and `scene_kind_hint: collage`.
- When scene state is absent or stale, use `action: inspect` with only exact `file_id`.
- After a widget returns user-confirmed typed operations, use `action: patch`, exact `file_id`, current `base_revision`, and those operations unchanged.
- Use `action: validate` only for a candidate that must be checked without persistence. Never use it instead of `adopt_generated` for a final generated artifact.

```json
{"handoff_type":"planner_handoff","planner_id":"pN8-collage-control","planner_decision":"instruction_ready","execution_instruction":{"executor":{"kind":"tool","name":"manage_svg_document"},"parameters":{"action":"patch","file_id":"","base_revision":1,"operations":[]},"purpose":"Commit the user-confirmed collage operations and return the canonical next SVG revision."},"return_to":"l1-pN8-core-module"}
```

Plan only one manager action per pass. L2 validates this exact shape and hands it to `exec-pN8-collage-authoring`, which calls the tool without adding operations. Every result re-enters Layer 1; never replay a host-committed patch.

## Gap Handoff

Use the named paradigm as `chain_id`. An interaction envelope carries `handoff_type: planner_handoff`, `planner_id: pN8-collage-control`, `planner_decision: gap_open`, exactly one item in `gap_requests`, and `return_to: l1-pN8-core-module`. The request contains registered `gap_type`, `interaction_goal`, `chain_id`, `iai_binding` (`source_nodes`, atomic `maps_to_edge`, destination `target_node`, meaningful evidence-grounded `reason`), grounded `display_context`, exact typed `expected_return`, eligible `selected_widget_id`, `order: 1`, and boolean `depends_on_previous`. L3 preserves the diagnosis unchanged. Rank eligible widgets by semantic coverage, artifact specificity, returns, runtime, registry order and ID. If no candidate passes, return a routing-failure envelope with `reason: no_eligible_widget`, `planner_id`, `diagnosed_gap` containing the unchanged request diagnosis, `rejected_candidates` records containing actual candidate IDs and failed eligibility checks, and exact L1 `return_to`; no selected widget or execution instruction. Never resurrect unregistered skills or execute via L3. L1 owns the next route.

Exact domain returns: selection uses `selected_object_ids` (stable string array) and `selection_scope` (string); native style/replacement/insertion/removal/transform/order/text use `artifact_id` (session string), `base_revision` (positive integer), `operations` (typed allowlisted object array); global style additionally requires `active_style_preset_id` (string). Review returns `decision: accept|continue_editing|request_new_generation` and `revision_request` (string, nonempty for new generation); comparison returns `action: accept_revision|continue_editing`. L1 merges against the exact source revision; host-committed operations are never replayed.

```json
{"chain_id":"direct-authoring","gap_type":"collage_object_transform_gap","selected_widget_id":"pN8-collage-transform-control","order":1,"depends_on_previous":false,"interaction_goal":"transform_collage_object","iai_binding":{"source_nodes":["I"],"maps_to_edge":"I→A","target_node":"A","reason":"The selected cutout has stable identity but its desired transform remains unspecified; guessing would change the user's composition."},"display_context":{"artifact_ref":{"fileId":"<actual-session-id>","revision":1},"object":{"id":"<stable-object-id>","label":"<actual-label>","transform":{}}},"expected_return":{"artifact_id":"<actual-session-id>","base_revision":1,"operations":[{"op":"set_transform","object_id":"<stable-object-id>","x":0,"y":0,"width":100,"height":100,"rotation":0}]}}
```

## Execution Handoff

Generate one missing source object:

```json
{"handoff_type":"planner_handoff","planner_id":"pN8-collage-control","planner_decision":"instruction_ready","execution_instruction":{"executor":{"kind":"tool","name":"generate_image"},"parameters":{"prompt":"One isolated full [object], matching [shared visual direction], clean silhouette, transparent background, no text, no frame","size":"1024x1024","quality":"high","background":"transparent","require_transparent_background":true},"purpose":"Generate the next independently editable collage cutout source."},"return_to":"l1-pN8-core-module"}
```

Prepare an element-level restyle candidate before its widget exists:

```json
{"handoff_type":"planner_handoff","planner_id":"pN8-collage-control","planner_decision":"instruction_ready","authoring_capability_id":"element_restyle","candidate_binding":{"target_object_id":"hero","kind":"restyle","label":"Editorial ink","rationale":"A sharper print treatment for the existing hero."},"execution_instruction":{"executor":{"kind":"tool","name":"restyle_image"},"parameters":{"image_file_id":"current-hero-file-id","style_prompt":"Editorial ink illustration matching the collage palette","size":"auto","quality":"high"},"purpose":"Prepare a restyled hero candidate before rendering the replacement gallery."},"return_to":"l1-pN8-core-module"}
```

When all planned cutouts are ready, name `compose_svg_collage` with a complete scene containing stable ids, cutout `asset_file_id` values, transforms, z-order, and the planned text objects. Its generated SVG must return through Layer 1 before any separate manager action.

The complete scene must use this executable shape. The abbreviated object list below is a per-object schema fragment, not a complete initial scene. A default rich scene still requires the full 4-6 cutout and 3-5 text-object plan described above. Replace placeholders with actual generated session `fileId` values and object-specific content:

```json
{"canvas":{"width":1200,"height":1200,"background":"#ffffff"},"objects":[{"id":"hero","type":"cutout","asset_file_id":"primary-file-id","x":120,"y":180,"width":520,"height":520,"z_index":1},{"id":"title","type":"text","text":"Theme title","x":120,"y":80,"width":900,"height":120,"z_index":2,"style":{"font_family":"Georgia","font_size":76,"font_weight":700,"fill":"#222222","text_anchor":"start"}}],"authoring_bundle":{"visual_style_presets":[{"id":"editorial","label":"Editorial contrast","rationale":"A crisp publication-like direction generated for this theme.","swatches":["#ffffff","#222222","#c45132"],"affected_object_ids":["hero","title"],"operations":[{"op":"set_canvas_style","style":{"background":"#ffffff"}},{"op":"update_text","object_id":"title","style":{"font_family":"Georgia","font_weight":700,"font_size":76,"fill":"#222222","text_anchor":"start"}},{"op":"replace_cutout_asset","object_id":"hero","asset_file_id":"editorial-hero-file-id","label":"Editorial hero"}]},{"id":"playful","label":"Playful paper","rationale":"A tactile, colorful direction generated for this theme.","swatches":["#fff4d8","#285943","#e0634b"],"affected_object_ids":["hero","title"],"operations":[{"op":"set_canvas_style","style":{"background":"#fff4d8"}},{"op":"update_text","object_id":"title","style":{"font_family":"Verdana","font_weight":800,"font_size":82,"fill":"#285943","text_anchor":"start"}},{"op":"replace_cutout_asset","object_id":"hero","asset_file_id":"playful-hero-file-id","label":"Playful hero"}]}],"asset_candidates_by_object":{"hero":[{"id":"hero-editorial","label":"Editorial hero","rationale":"Cleaner silhouette and restrained material treatment.","fileId":"editorial-hero-file-id"},{"id":"hero-playful","label":"Playful hero","rationale":"Tactile paper texture and brighter thematic detail.","fileId":"playful-hero-file-id"}]},"text_authoring_options":{"title":{"copy_options":[{"id":"title-direct","label":"Direct","text":"Theme title"},{"id":"title-expressive","label":"Expressive","text":"Generated alternate headline"}],"typography_presets":[{"id":"title-editorial","label":"Editorial serif","style":{"font_family":"Georgia","font_size":76,"font_weight":700,"fill":"#222222","text_anchor":"start"}},{"id":"title-playful","label":"Playful bold","style":{"font_family":"Verdana","font_size":82,"font_weight":800,"fill":"#285943","text_anchor":"start"}}]}}}}
```

Composition is not ready if this bundle is absent, any cutout lacks 1-3 candidates, a candidate lacks a real current-session `fileId`, a candidate equals the current cutout asset, candidate fileIds repeat within one gallery, or a preset contains only transform/order operations. In that case continue the asset-generation queue instead of calling `compose_svg_collage`.

## Must

- Keep all generated assets coherent in theme, palette, lighting, and treatment.
- Complete and preserve the bounded authoring bundle before exposing review widgets.
- Pass the complete bundle inside `compose_svg_collage.scene`; the host renders it before secondary geometry controls.
- Keep every widget option artifact-specific and backed by existing data or session assets.
- Preserve candidate `kind`, `source_tool`, source identity, target identity, and default transform across tool returns and patches.
- Preserve stable object ids and untouched objects across revisions.
- Distinguish deterministic patches from semantic generation.
- Emit one mode only: gaps or one execution instruction.

## Must Not

- Do not copy concrete registry metadata into a gap request or render UI.
- Do not flatten the SVG collage into a PNG.
- Do not regenerate for move, size, rotation, z-order, or text property edits.
- Do not call GenAI or image tools after a style preset, asset candidate, copy option, or typography option is selected.
- Do not render a capability widget until all external preparation results required by that widget are bound to the artifact.
- Do not expose an asset candidate without an existing current-session `fileId`.
- Do not call `compose_svg_collage` with only canvas and objects.
- Do not call multiple side-effect tools in one pass.

## Execution Skill Routing

For `instruction_ready`, finish the existing `execution_instruction` and load `exec-pN8-collage-authoring`. Keep `executor.kind`, registered tool name, parameters, purpose and result bindings unchanged. L2 plans; the execution skill performs the planned work and returns to L1. Do not invoke task tools in the planner before this handoff, or route execution through L3/L4. Gap selection still routes to the selected L3 designer. Failures return directly to L1.

## Next

Interaction Pathway: selected gap → L3 semantic design → L4 render → L1. Execution Pathway: ready plan → exec-pN8-collage-authoring (tool/main_model) → L1, no L3/L4. Host Agent Return and Completion belong to L1. Every result/failure re-enters `l1-pN8-core-module`.