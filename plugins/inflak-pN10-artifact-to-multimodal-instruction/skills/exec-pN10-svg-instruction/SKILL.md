---
name: exec-pN10-svg-instruction
description: "Use when: P10 L2 hands off an instruction-ready grounded SVG analysis, candidate or confirmed modification plan."
---

# P10 SVG Instruction Execution

## Role and Handoff

Execution capability of the same Host Agent, parallel to the L3 interaction branch, not a numbered layer or another agent. Load only after L1 and L2. Require the current `planner_handoff`, `planner_decision: instruction_ready`, `execution_instruction`, complete parameters, purpose, source/interaction/result bindings and actual authorization. Preserve the exact selected tool or `main_model` and planned scope. Perform one planned model task or registered tool call; return all results/failures to `l1-pN10-core-module`. Do not select gaps, replan, render or infer permission; no L3/L4 execution. Only L1 merges state and decides Completion. Missing, stale or incompatible inputs return there without execution.

## Grounding and Authorization

Use `inspect_svg_scene(file_id)` for stable IDs and capabilities. `manage_svg_document` accepts `import`, `inspect`, `validate`, or an explicitly selected typed `patch`; never `adopt_generated` in this artifact-first flow. Use an exact current-session fileId, never a filename, URL, path, raw SVG or selector. Inspect/validate omit patch parameters; patch requires current `base_revision` and nonempty compatible operations. Do not combine inspection and mutation in one pass.

Suggestion, relation and operation widgets collect semantic values, not patch authorization. Only final concrete Aug confirmation unlocks execution of accepted/edited decisions. Preserve suggestion IDs, full rejected history, source revision, exact confirmed instruction and interaction binding. The Host Agent checks complete decisions, unique current object bindings, supported object types, text-only text edits, relations, constraints and provenance. Edited decisions require concrete edited values; all-rejected work returns to L1 without mutation.

No plugin-local runtime, export tool, generated Markdown/JSON file or exported hash is required. Shared Host tools enforce session isolation, SVG safety, revision, object IDs and typed parameters; manager validation is not proof of user approval. Retain executed operation IDs and returned revisions in `execution_state` to prevent replay. Source, target, parameter or constraint changes invalidate affected approval and return through L1.

## Operation Compilation

Compile only complete approved values using the actual callable schema and scene capabilities. Prefer narrow `apply_svg_*` tools with exact `file_id`, current `base_revision` and nonempty homogeneous operations:

- Presentation: compatible `set_object_style`, `set_attributes`, `set_text`, `update_text`.
- Layout: `set_transform`, `set_order`, supported `set_dom_order`.
- Structure: supported `add_cutout`, `remove_object`/`remove_element`, `replace_cutout_asset`/`replace_asset`.

Aliases are not interchangeable. Semantic move/resize/align/restyle names are not patch names. `translate.x/y` are deltas, not desired absolute coordinates; group/text resize requires explicit uniform scale where required by schema. Do not invent missing values or widen operation families. Remove no-ops, verify meaningful before/after scene changes and retain an object-level applied-change summary.

## Candidates and Validation

Semantic add/replace/restyle may prepare one `generate_image` candidate per pass from the confirmed objective, source evidence and preserve constraints. Require `background: transparent`, `require_transparent_background: true`, actual transparent pixels and a real current-session `fileId`, bound by suggestion and operation ID. Never generate for deterministic text/transform/order/remove/concrete attributes. Each result re-enters L1 before binding or another tool call.

After applying all approved families against successively returned revisions, validate separately and compare original source to final validated revision. Return actual canonical scene, capabilities, revisions, applied operations, limitations or errors; never fabricate evidence or rewrite approved operations. L4 is read-only and never commits patches. Errors/conflicts return unchanged; no stale replay. Only L1 may conclude after comparison acceptance and visible updated artifact.