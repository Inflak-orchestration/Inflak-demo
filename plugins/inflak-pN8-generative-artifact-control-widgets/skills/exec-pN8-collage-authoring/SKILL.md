---
name: exec-pN8-collage-authoring
description: "Use when: P8 L2 hands off an instruction-ready collage preparation, composition or SVG document plan."
---

# P8 Collage Execution

## Role and Handoff

Execution capability of the same Host Agent, parallel to the L3 interaction branch, not a numbered layer or another agent. Load only after L1 and L2. Require the current `planner_handoff`, `planner_decision: instruction_ready`, `execution_instruction`, complete parameters, purpose, source/interaction/result bindings and existing authorization. Preserve the exact selected tool and parameters; do not select gaps, replan, render, change scope or infer permission. Invoke one registered tool per pass; return every actual result/failure to `l1-pN8-core-module` before another action. Only L1 merges canonical state and decides Completion. Missing or stale input returns to L1 without execution; no L3/L4 execution.

## Preparation and Capability Binding

Read `registry/authoring-capabilities.json` and `registry/tools.json.authoring_reference_routes`. Require matching capability/provider, actual source session `fileId`, target object, candidate kind, label, rationale and result binding. Preserve the capability ID and reference route ID in the existing preparation queue, not a callable skill name.

- `global_visual_style`: one `generate_image`, `restyle_image`, `adjust_image` or `apply_filter` call per pass. Preserve style direction ID; 2–4 complete distinct presets bind canvas/text presentation and actual raster replacements. A single filtered asset is not a whole-collage preset.
- Element restyle/semantic edit/outpaint/variation/background/geometric/tonal capabilities use only their declared provider. Bind 1–3 alpha-validated distinct results to `authoring_bundle.asset_candidates_by_object[target_object_id]`, retaining original transform/z-order and provenance.
- `new_element_generation`: generate one isolated transparent object; later extraction may produce a valid transparent cutout. Bind 1–3 addable records before insertion, each with a new stable object ID and bounded default transform.
- Primary source preparation and `extract_collage_cutouts` obey the same actual-alpha rule. Generation requires `background: transparent`, `require_transparent_background: true`. Opaque output is failure, not an asset; extraction uses real returned sources only.

Candidate records retain `id`, `label`, `rationale`, `fileId`, `kind`, `source_tool`, `source_file_id`, `target_object_id`; new elements additionally retain `object_id`, `default_transform` (`x`,`y`,`width`,`height`,`rotation`) and prompt/option description. Kinds distinguish generated/restyle/semantic_edit/outpaint/variation/background_treatment/transform/appearance/new_element. Never count the current primary or duplicate fileIds as replacement candidates.

Preparation completes before the corresponding widget renders. Preserve prompt/option description and the current collage visual direction; pass approved provider parameters unchanged. Only L1 merges actual outputs into `authoring_bundle.asset_candidates_by_object`, `authoring_bundle.addable_elements` or a complete `visual_style_preset`. At most three candidates per target per bundle. Preparation never composes or patches in the same pass, changes an unrelated object, or flattens provenance to a generic generated label.

Later widget selection uses only its declared operations: global presets use `set_canvas_style`, `update_text`, `set_object_style`, `replace_cutout_asset`; element replacement uses `replace_cutout_asset`; insertion uses `add_cutout`. These selections do not permit external provider calls from the widget.

## Composition

`compose_svg_collage` receives one complete `scene` with canvas, stable objects, actual `asset_file_id` values, transforms/z-order, text and `authoring_bundle`. Default rich profile retains 4–6 independently editable transparent cutouts and 3–5 text objects; explicit minimalism or named-only constraints override creative defaults while the compiler's two-cutout floor still applies. Complete all accepted plan items and required candidate galleries before composition. Preserve 2–4 presets, 1–3 candidates per replaceable cutout, text copy/typography options and prepared addable elements. Never flatten to bitmap, invent references or call a second tool in that pass.

## Lifecycle and Patch

`manage_svg_document` takes exact session `file_id`, never filename/URL/path/raw markup. `import` and `adopt_generated` may include `scene_kind_hint: collage` and no operations; adopt only if composition did not already return canonical `svg-document` plus scene. `inspect`/`validate` carry no operations or base revision. One action per pass.

`patch` requires current positive `base_revision`, nonempty confirmed operations and stable capability-compatible IDs. Preserve operation order atomically: `set_transform`, `set_order`, `set_object_style`, `add_cutout`, `remove_object`, `add_text`, `update_text`, `replace_cutout_asset`, `set_canvas_style`. Use the existing scene/tool parameter schema, never raw selectors/XML/CSS/path data. Host-applied widget `patch_result` is already committed; never replay it. If a widget returns values only, L2 may execute its approved patch after L1 re-entry. Return actual canonical attachment/scene/revision or error; only L1 merges and decides completion.