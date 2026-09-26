---
name: exec-pN11-prompt-refinement
description: "Use when: P11 L2 hands off an instruction-ready prompt grounding, candidate or approved SVG refinement plan."
---

# P11 Prompt Refinement Execution

## Role and Handoff

Execution capability of the same Host Agent, parallel to the L3 interaction branch, not a numbered layer or another agent. Load only after L1 and L2. Require the current `planner_handoff`, `planner_decision: instruction_ready`, `execution_instruction`, complete parameters, purpose, source/interaction/result bindings and actual authorization. Preserve the exact selected tool or `main_model` and scope. Perform one planned task per pass; every result/failure returns to `l1-pN11-core-module`. Do not select gaps, replan, render or infer permission; no L3/L4 execution. Only L1 merges state and decides Completion. Missing, stale or incompatible inputs return there without execution.

Ground with `inspect_svg_scene(file_id)` and safe manager `import` where needed. Manager `inspect`/`validate` use exact session `file_id` without operations/base revision. No raw SVG, filename/URL/path/selectors or `adopt_generated`. Select `executor.kind: tool` and exact registered `executor.name`; pass only actual schema parameters. A manager patch requires matching target-bound action approval, current revision and nonempty typed operations; narrow family tools remain the normal execution interface. Do not combine inspection, candidate generation and patching in one pass. Return actual canonical scene, stable IDs, capabilities, revision, applied operations, limitations or errors unchanged through L1.

`prompt_object_alignment` and `prompt_target_resolver` collect meaning only. Each executable action requires its target-bound `prompt_action_specificity_editor` approval, including exact prompt-unit ID, targets, operation, object-valued parameters/constraints, `interaction: action_specificity` and `selected_by: user`. Aggregate review, inferred facts or model suggestions cannot supply this permission.

The Host Agent validates the confirmed enhancement directly: preserve exact original prompt, `source_artifact.fileId`, positive revision, prompt units, source spans, bindings and history. Source spans must match the original prompt; unit IDs are unique and all binding/refinement/history references name existing units and current scene objects. Unit status is `resolved|not_present|skipped`; `validation.unresolved_prompt_unit_ids: []` is valid only on actual closure. Skipped or absent targets never authorize mutations. Each executable refinement must match its user-approved target, operation, parameters and constraints. No second aggregate prompt confirmation.

No plugin-local runtime, export tool, generated Markdown/JSON file or exported hash is required. The Host Agent checks semantic completeness and authorization; shared Host tools deterministically enforce session isolation, safe SVG, revision, object IDs and typed operation parameters. Manager validation does not establish user approval. Preserve executed refinement IDs and returned revisions in `execution_state` to prevent replay. Source prompt, target, parameter or constraint changes invalidate affected approval and return to L1 for replanning.

Compile only approved complete semantics. Presentation uses supported `set_object_style`/`set_attributes`/`set_text`/`update_text`; layout uses `set_transform`/`set_order`/supported `set_dom_order`; structure uses supported `add_cutout`/`remove_object`/`remove_element`/`replace_cutout_asset`/`replace_asset`. Use actual family schema and capabilities, not interchangeable aliases or semantic operation names. Preserve exact source, positive current revision and nonempty homogeneous operations, plus prompt-unit/enhancement/interaction provenance. Do not infer targets or parameter values; no-op or unsupported work returns for reassessment.

Semantic add/replace/restyle may use one `generate_image` per pass, bound to prompt unit/action refinement. Require actual same-session alpha output with `background: transparent`, `require_transparent_background: true`; never generate for deterministic operations. Return every real result before proceeding.

Validate after all patch families; P11 L4 remains read-only. Target-bound approval is the only instruction confirmation; do not add artifact-acceptance UI. Return the actual validated updated SVG to L1 for Completion assessment. Errors, conflicts and missing capabilities remain failures, never success or authorization to retry stale work.