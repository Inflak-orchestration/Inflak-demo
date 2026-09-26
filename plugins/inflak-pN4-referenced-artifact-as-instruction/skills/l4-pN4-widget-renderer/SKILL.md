---
name: l4-pN4-widget-renderer
description: "Use when: rendering a P4 inpaint region editor or before/after review contract as sandboxed code from its semantic and presentation.profile requirements."
---

# Layer 4 - P4 Widget Renderer

## Workflow End Boundary

After any widget return or renderer failure, immediately load `l1-pN4-core-module` with the structured result. Layer 4 never decides workflow completion, produces the final response, or continues directly to a planner or executor.

## Layer & Role

L4 Renderer implements only Interaction Pathway: user/return → L1 → L2 gap + selection → L3 Designer → L4 render → L1. Execution Pathway is L2 directly invoking edit_image without L3/L4. Host Agent Return and Completion do not enter L4; only L1 emits `decision: "end"`.

## Inputs (self-contained)

Validate the complete L3 semantic contract locally, without reading main or an authoring contract; no success `handoff_type` is added:

- Identity: require nonempty strings `selected_widget_id`, `widget_id`, `widget_type`, `surface`, `planner_id`, `purpose`, `interaction_goal`; preserve L2 selection/goal and exact local registry type, surface and eligibility.
- `iai`: preserve L2 `chain_id`, `gap_type`, binding `reason`, `maps_to_edge`, `source_nodes`, `target_node`; require a named chain and meaningful reason, edge source in `source_nodes`, and destination equal to `target_node` and allowed `state_update_target`. Require deterministic `merge_strategy` and `next_planner_action: "re-enter Layer 1"`; do not merge canonical state here.
- `display`: require grounded task values, actual source references and unresolved status; every profile content source must resolve. Never invent absent source images, masks, defaults or outcomes.
- `controls`: require unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty `return_keys` limited to declared keys, and applicable `constraints`; enforce supplied types, limits and source/edit rules.
- `presentation.profile`: require nonempty `archetype`/`summary`, nonempty `content` records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`), supported nonempty `interaction.actions`/`feedback`, and `submission` with nonempty `label`, `preconditions`, `return_mapping`. Require nonempty semantic `appearance` and `signature_features`; implement behavior, not new stages.
- `expected_return`: exactly L2 keys/types and exactly the same keys in `presentation.profile.interaction.submission.return_mapping`; each mapping names an actual producible source and serialization, including declared optional/empty handling. Validate before submission; derived metadata needs mappings, not artificial controls.
- `widget_requirements`: four nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`; implement every item consistently with profile, controls and mappings.
- `safety`: require `allow_html: false`, `allow_script: false` in L3 input. Only L4 writes code. Optional `runtime` uses available approved capabilities/version-pinned libraries; optional `reference_assets` are plugin-relative design-time principles, never runtime assets.

Missing/inconsistent semantics, unsafe input or unavailable capability returns structured renderer failure to `l1-pN4-core-module` before rendering, without semantic repair. Compile this contract into existing renderer fields, not undocumented tool arguments. Pass `selected_widget_id`, `display`, `controls`, `planner_id`, `interaction_goal`, and `expected_return` unchanged; selection is trace metadata, never permission to substitute UI semantics.

## Universal Style and Layout Baseline

Match host typography, neutral surfaces, spacing, borders, focus and control density using host `--iai-*` tokens/classes. Remain usable at 266px iframe width and desktop widths; use `minmax(0, 1fr)` and `min-width: 0` on shrinkable children. Prevent page-level `overflow-x` without clipping content; confine necessary scrolling to an explicit region. Keep labels/status/errors clear of controls and avoid nested decorative cards or marketing copy.

Use native labeled controls, keyboard navigation, accessible icon names/tooltips and visible focus. Keep persistent submit/dismiss/reset actions reachable in `.iai-actions`. No confirmation checkbox; checkboxes are only for genuine multi-value boolean settings. Implement truthful disabled/loading/error/submitted states and all declared operations. Initialize local state from `window.widgetDisplay`, guard DOM/data lookups and current event state, and display recoverable inline errors. No parent DOM, storage, secrets, local files, undeclared network, remote code or modal APIs. Use only approved available capabilities/libraries.

## Rendering Procedure

Render only `inpaint_region_editor` and `inpaint_image_compare` semantic contracts reached by a fresh `L1 -> L2 -> L3` path. Check whether all three matching P4 files in `registry/templates/<widget_type>/` exist before reading them as code-level references; do not call a file-view tool for a missing template. Generate sandboxed HTML/CSS/JS that satisfies both the task contract and L3 `presentation.profile` requirements whether or not a template exists. `render_mode: "template"` is available only as an explicit fallback when all matching template files exist.

Compile the validated profile into the image stage, editing/comparison controls, responsive layout and visible feedback. Read complete references from injected read-only `window.widgetDisplay.image_ref` or `before_ref`/`after_ref` and use only `window.widgetAssetUrl(ref)` at image sinks; never use `.path`/`.url` directly or invent file IDs. Preserve those actual references in the render call's `display`. Show unavailable state instead of inventing an image. The brush editor uploads its real source-sized RGBA PNG through `window.uploadWidgetFile`; only successful returned upload evidence can become `mask_ref`.

For the editor, preserve source aspect/dimensions and current `edit_state` (boxes, brush_actions, brush settings, prompt and mode). The stage and every overlay must share the source image's exact rendered bounds with no letterboxed interaction area. Compute pointer coordinates from those image bounds, capture one active pointer until release, render a live box outline while dragging, and discard rather than commit on pointer cancellation. Existing-box movement preserves width/height and stays bounded. Box mode returns positive normalized `{x,y,width,height}` regions within [0,1] and no active mask; brush mode returns actual `mask_ref`, empty regions, transparent-edit/opaque-preserve pixels and correctly aligned dimensions. Never invert mask semantics, mix scopes or reuse an export after edits. Require nonempty `edit_prompt` and one valid scope before submission; pending/failed upload blocks submit with a visible error. Return exactly `mode`, `image_ref`, `regions`, `mask_ref`, `edit_prompt`, `freeform_note`, `edit_state`.

For review, show actual before/after artifacts and applied prompt in one fixed-aspect comparison viewport. Stack both images on the same inset with identical rendered dimensions, `object-fit` and `object-position`; place the candidate above the source and reveal it only by clipping the candidate layer at the slider boundary (for example, `clip-path: inset(...)` or an overflow-hidden overlay whose child retains the full viewport dimensions). At 50%, each version occupies one half of the same scene while both retain the full image scale and coordinates. The slider may update only the clip boundary and divider position: never image width/height, grid tracks, flex basis, scale, zoom, transform or object fit. Do not place versions in independently sized columns and do not stretch a clipped child to the visible fraction. Return exactly `accepted_version` (before/after/none), `revision_request`, `freeform_note`; none requires nonempty revision feedback. Use `window.submitWidget(values)` only after typed validation, and `window.dismissWidget(note)` for dismissal. Call `render_html_widget` with `render_mode: "generated"`, generated `html`/`css`/`js` and unchanged semantic fields. Never expose design-time reference assets.

Do not render a review immediately after `edit_image`; a completed tool call must return to Layer 1 first. Do not call task tools. After any widget result, return control to `l1-pN4-core-module`.
