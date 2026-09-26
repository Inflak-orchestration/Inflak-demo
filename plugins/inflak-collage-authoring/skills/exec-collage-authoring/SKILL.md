---
name: exec-collage-authoring
description: "Use when: the Collage authoring planner hands off an instruction-ready creation, analysis, grounding or refinement plan."
---

# Collage Authoring Execution

## Role and Handoff

Execution capability of the same Host Agent, parallel to the L3 interaction branch, not a numbered layer or another agent. Load only after L1 and L2. Require the current `planner_handoff`, `planner_decision: instruction_ready`, `execution_instruction`, registry membership, complete parameters, purpose, source revision, interaction/result bindings and actual authorization. Preserve the selected tool or `main_model` and scope. Perform one planned task per pass without L3/L4. Every result/failure returns to `l1-collage-authoring-core` before another action. Do not select gaps, replan, change approved values, render, infer permission or decide Completion. Only L1 merges state; invalid inputs return there without execution.

## Lifecycle and Composition

`manage_svg_document` uses exact action/session `file_id`, optional scene-kind hint, and current revision/nonempty typed operations only for patch. `inspect_svg_scene` returns stable scene/capabilities, never raw SVG state. Create composition uses `creation_mode: image_collage`, at least two actual alpha-validated primary cutouts, stable IDs and complete `authoring_bundle` with 1–3 distinct actual candidates per successful primary. Adopt/inspect returned artifacts on later L1/L2 passes when necessary.

## Operation Families

- Presentation: supported `set_object_style`, `set_attributes`, `set_text`, `update_text`.
- Layout: supported `set_transform`, `set_order`, `set_dom_order`.
- Structure: supported `add_cutout`, `remove_element`, `remove_object`, `replace_asset`, `replace_cutout_asset`.

Validate actual callable schema/capabilities, not interchangeable aliases. Require exact current `file_id`, `base_revision`, homogeneous nonempty approved operations, and matching interaction/proposal provenance. Semantic names are never patch names. Never replay operations already committed in host `patch_result`; only values without a successful commit may enter a later L2 ready patch. An accepted proposal authorizes only its displayed scope; standing permission restrictions survive.

## Asset Preparation

Require `authoring_capability_id`, matching mode/provider from `registry/authoring-capabilities.json`, exact source session ID when applicable, and existing `result_binding` containing proposal/candidate/state target. Allowed providers remain generate/edit/restyle/outpaint/remove-background/variations/transform/adjust/filter/extract tools listed in the registry; no invented callable.

For initial generation preserve stable object ID, `asset_role: primary|replacement_candidate`, candidate ID, actual `fileId` and transparency evidence. SVG raster elements require actual alpha; generation requests use `background: transparent`, `require_transparent_background: true`. Reject opaque output rather than weaken the requirement. Preserve kind/source tool/source/target/label/rationale provenance. At most two permitted transparent-asset attempts per plan item; timeout/provider failure or exhausted transparency attempts marks that item unavailable, returns to L1 and does not loop inside a reference. Never substitute vector/text-only output when fewer than two required cutouts can succeed.

## Optional Export and Validation

Confirmed `analyze` and `ground_prompt` Aug are checked by the Host Agent and executed directly through shared SVG tools; no plugin-local exporter or exported hash is required. Preserve exact approval, source revision, object/operation IDs and interaction history. Shared tools enforce SVG safety, revision and typed operation validation; they do not infer user approval. There is currently no registered instruction-file exporter. If export policy is required or the user explicitly requests such files, return a capability failure to L1 and resolve that requirement before completion; never invent an export binding or download link. Optional or disabled export does not block SVG execution.

Validate the actual updated revision and return to L1 for comparison/acceptance. Reject raw markup/selectors/scripts/path data/URLs/data URIs, invented IDs, stale authorization, mixed families and unsupported parameters. Return conflicts/errors unchanged; never retry stale operations or invent success.

Return actual emitted attachment, canonical scene/capabilities, next revision, applied operations and validation with the plan's result bindings. Never count a vector shape, text object, prompt, opaque image or missing tool result as a prepared cutout. Do not stop before L1 reviews the result and decides the next route or Completion.