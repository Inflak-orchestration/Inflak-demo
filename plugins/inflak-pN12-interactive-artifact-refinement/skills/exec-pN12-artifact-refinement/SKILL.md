---
name: exec-pN12-artifact-refinement
description: "Use when: P12 L2 hands off an instruction-ready SVG grounding, candidate preparation or user-applied refinement plan."
---

# P12 Artifact Refinement Execution

## Role and Handoff

Execution capability of the same Host Agent, parallel to the L3 interaction branch, not a numbered layer or another agent. Load only after L1 and L2. Require the current `planner_handoff`, `planner_decision: instruction_ready`, `execution_instruction`, exact selected tool or `main_model`, complete parameters, purpose, current source/interaction/result bindings and actual authorization. Execute one planned task per pass and return every result/failure to `l1-pN12-core-module`. Do not select gaps, replan, render or infer permission; no L3/L4 execution. Only L1 merges state and decides Completion. Missing or stale input returns there without mutation.

Manager lifecycle permits `import`, `adopt_generated`, `inspect`, `validate`, `patch`, with exact current-session `file_id`, never filename/URL/path. Import/adopt may include a supported scene-kind hint and no operations; inspect/validate carry no operations/base revision. Use `inspect_svg_scene` to obtain actual object capabilities for interaction synthesis or artifact review. Do not inspect raw markup or create unsupported handlers.

Patch requires an interaction whose newest current-revision return is **Apply**, exact bound `file_id`, positive matching `base_revision`, nonempty typed operations, compatible widget and target capabilities. If host `patch_result` already committed these operations, merge it through L1 and do not invoke another patch. Otherwise L2 may directly call one matching `apply_svg_presentation`, `apply_svg_layout`, `apply_svg_structure`, or explicitly selected manager patch with unchanged approved operations.

Presentation includes supported `set_object_style`/text/attributes; layout contains supported transform/order operations; structure contains allowed removal or actual selected transparent candidate add/replacement. Deterministic removal requires explicit destructive action, not candidate-generation consent. Do not mix unsupported families, rewrite operations or retry a conflict.

`refinement_control` supports presentation/layout and explicitly confirmed deterministic removal. `semantic_variant_review` supports only structure operations using a user-selected transparent candidate `fileId`. Check each target and operation against current scene capabilities; never widen them to make a patch succeed. Candidate preparation runs in its own pass, never inside a document or apply call.

Semantic candidate materialization is bounded preparation: one `generate_image` result per pass with `background: transparent`, `require_transparent_background: true` and actual alpha. Bind real `fileId` by interaction/candidate/variant IDs; display the candidate preview before Apply. Preparation does not authorize final mutation. Replacement preserves stable target/transform/order.

Host owns annotations, hit testing, layout drafts and revision commit. For layout Apply the host injects authoritative operations from its draft; iframe geometry is not execution evidence. Reset/Adjust remain transient; Regenerate/Correct/Reject/Dismiss never authorize a patch. Revision changes invalidate previews and uncommitted evidence.

Preserve compact successful patch output (action/file ID/new revision/scene kind/object count/applied summary/validation/attachment); do not run shell, read temporary outputs or re-inspect merely to summarize an actual success. Validate real resulting revision when needed, then return to L1 for comparison/acceptance. No Aug compilation/export. Return source, validation or capability failures unchanged, never fabricated semantic gaps.