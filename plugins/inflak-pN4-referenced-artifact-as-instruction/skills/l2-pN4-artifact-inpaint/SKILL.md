---
name: l2-pN4-artifact-inpaint
description: "Use when: P4 routes source-grounded local inpaint scope, intent, execution or candidate review."
---

# L2 Planner — Artifact Inpaint

## Workflow End Authority

Only L1 Router owns canonical state and emits `decision: end`. L2 Planner selects an eligible interaction or directly invokes its ready executor; every result/failure returns to `l1-pN4-core-module`. Execution Pathway omits L3/L4; L3 Designer never executes.

## Layer & Role

Plan one `artifact-inpaint` pass over an actual image. Assess all registered categories, select one next gap by dependencies and one eligible widget, or directly call registered edit_image with validated source, one scope and nonempty intent. Do not render or author semantic UI fields.

Interaction Pathway sends one gap through L3 Designer → L4 Renderer → L1. Execution Pathway directly realizes the ready plan through L2's executor → L1. Host Agent Return and Completion belong to L1 and do not enter L2; a routing failure returns directly to L1 without L3.

## IAI Domain Binding

| Node | Meaning |
| --- | --- |
| H | User owning source image and local edit intent |
| T | User's requested local addition/removal/replacement/repair |
| I | Source-bound boxes or brush marks and review decisions |
| Aug | Compiled source/scope/prompt/output instruction |
| A | Actual source with scoped evidence, then the linked edited candidate |
| G | Configured image editor invoked through edit_image |

## Interaction Chains

| Chain ID | Paradigm / function | Ordered edges |
| --- | --- | --- |
| p4-region-grounding | Bind explicit scope to the real source | `H→I, I→A, A→Aug` |
| p4-edit-intent | Incorporate user local intent | `H→T, H→I, I→Aug` |
| p4-inpaint-execution | Edit only the confirmed scope | `Aug→G, G→A` |
| p4-candidate-review | Accept real candidate/prior source or request revision | `H→I, I→A` |

A source and its edited candidate are distinct actual artifacts; no source may be invented to complete the chain.

## Diagnosis

Read before/after GenAI and prompt-only/artifact-grounded state. Assess every registered category as open/resolved/not applicable using actual facts, current returns and explicit scoped delegation. Silence is not delegation. Record evidence, missing transfer and consequence of guessing in existing reason/purpose fields; choose one next gap by real dependencies, not row order. Missing source is a blocker, not a fulfilled scope or a generative substitute.

Before widget routing, check source availability: the intended source image is missing or inaccessible on `I→A`. There is no registered source collector, so return the source requirement directly to L1 through the existing no_eligible_widget diagnosis; do not open an unusable editor or execute. This remains a required source check, not a registered widget gap.

| gap_type | Condition | Edge | Interaction goal |
| --- | --- | --- | --- |
| `inpaint_intent_gap` | Actual source exists but intended local change is unresolved. | `I→Aug` | `mark_region_and_describe_inpaint` — supply local intent with preserved scope. |
| `artifact_region_gap` | Actual source lacks a valid explicit source-bound scope. | `I→A` | `mark_region_and_describe_inpaint` — mark scope and local intent. |
| `inpaint_acceptance_gap` | A real current edited candidate remains undecided. | `I→A` | `review_inpaint_candidate` — retain source/candidate or revise. |
| `instruction_ready` (decision, not gap) | Source, local intent and exactly one valid submitted scope are evidenced and applicable pre-edit gaps are closed. | `Aug→G` then `G→A` | Directly invoke edit_image and return the actual candidate to L1. |

Post-edit review is not applicable until a candidate exists, then remains open until actual decision. Preserve settled intent/scope; source changes invalidate old geometry/masks and changed instructions invalidate old review. Box suits rectangular targets; brush suits irregular/fine contours. Full-image intent still needs explicit whole-canvas scope. Refused input or capability failure returns to L1, never false readiness.

## Widget Registry Routing

Intent/region gaps may select `inpaint-region-editor`; acceptance selects `inpaint-image-compare`. Filter exact planner/gap/goal/atomic edge, all required returns, real artifact support and available capabilities/libraries/renderer. Rank semantic coverage, artifact specificity, returns, runtime fitness, stable order then ID. Emit one exact selected_widget_id and no type/skill/path/profile metadata.

No eligible entry returns directly to L1 without L3: reason no_eligible_widget, planner_id, diagnosed_gap (chain/evidence/edge/goal/returns), rejected_candidates with failed checks, return_to. artifact_target_gap has no eligible local widget; report missing source honestly instead of opening an unusable editor.

## Gap Handoff

One request contains chain_id, exact gap/goal, source/edge/target/reason, typed expected_return, grounded display_context, selected_widget_id, order 1 and actual dependency flag. Edge source belongs to source_nodes and target equals destination; pending marks are not evidence. L3 preserves chain_id/reason unchanged. Schema illustration below requires replacing the source placeholder with an actual available reference:

```json
{"handoff_type":"planner_handoff","planner_id":"artifact-inpaint","planner_decision":"gap_open","gap_requests":[{"chain_id":"p4-region-grounding","gap_type":"artifact_region_gap","interaction_goal":"mark_region_and_describe_inpaint","target_tool":"edit_image","iai_binding":{"source_nodes":["I"],"maps_to_edge":"I→A","target_node":"A","reason":"The requested local change has a real source but no user-marked scope on I→A; guessed boundaries could change protected pixels. Source-bound boxes or a real mask provide the missing scope evidence."},"expected_return":{"mode":"box","image_ref":{},"regions":[],"mask_ref":{},"edit_prompt":"","freeform_note":"","edit_state":{}},"display_context":{"image_ref":{"fileId":"<actual source fileId>"},"suggested_prompt":"<actual local intent>","edit_state":{}},"selected_widget_id":"inpaint-region-editor","order":1,"depends_on_previous":false}],"return_to":"l1-pN4-core-module"}
```

Intent uses p4-edit-intent/I→Aug with the same seven-key return. Reopen same-source edit_state unchanged; it preserves boxes, brush_actions, brush settings, text and mode. Review uses p4-candidate-review/I→A with actual before_ref/after_ref and applied prompt; expected_return is accepted_version before/after/none, revision_request and freeform_note strings. None requires nonempty feedback; L1 commits after/before or retains context for replanning.

## Output (planner_handoff)

Choose exactly one mode. This is a schema illustration, not evidence of an uploaded source or confirmed scope:

```json
{"handoff_type":"planner_handoff","planner_id":"artifact-inpaint","planner_decision":"instruction_ready","execution_instruction":{"executor":{"kind":"tool","name":"edit_image"},"parameters":{"image_file_id":"<actual source fileId>","mask_file_id":"<actual uploaded brush mask fileId>","regions":[],"prompt":"<current submitted local prompt>","size":"auto","quality":"high"},"purpose":"Use only the actual source and current submitted brush scope/prompt after validating their alignment and closure; preserve unselected pixels and return the actual candidate to L1 for review."},"return_to":"l1-pN4-core-module"}
```

For box mode copy positive normalized regions and omit mask_file_id. Brush mode uses mask_ref.fileId and empty regions; source-sized RGBA transparent pixels edit and opaque pixels preserve. Never activate both or reuse stale exports. Compilation of existing scope is not permission to fill missing source or choices with model preparation.

Each box is `{x: number, y: number, width: number, height: number}` with finite values, x/y >= 0, width/height > 0, and x+width/y+height <= 1. `mode` is box or brush; `image_ref` and active `mask_ref` are actual reference objects, `regions` is an array, `edit_prompt`/`freeform_note` are strings, and `edit_state` is the source-bound editor-state object. Preserve its existing brush_actions/settings/boxes/text fields rather than invent a second serialization format.

## Inputs and Procedure

Consume selected_planner/user_text; optional source_artifact/candidate_artifact/prior_returns/inpaint_state plus local registry/runtime. Validate source, assess all categories, choose next dependent gap, preserve existing edit state, validate current submitted scope and intent, emit selected interaction or ready execution, return every actual result/partial failure/failure to L1. Every successful edit requires a fresh L1/L2/L3 candidate-review pass, never direct tool-to-review rendering.

## Must / Must Not / Tools

L2 directly invokes only registered edit_image after instruction_ready. Require actual source identity, dimensions, one bounded scope and nonempty local prompt. Preserve unselected pixels, masks, provenance and revisions. No invented image/upload, silent whole-image scope, unready executor, generic approval checkbox or semantic UI design. L4 alone renders and uploads brush masks through its approved host capability.

## Stop / Continue / Escape

Stop locally at eligible L3 handoff or actual result/failure to L1. Continue only after L1 reconstruction. Missing/refused source, scope or capability escapes to L1 with the real reason.

## Next

Interaction Pathway goes through selected L3 Designer and L4 Renderer. Execution Pathway has L2 directly invoke edit_image without L3/L4. All results/failures return to `l1-pN4-core-module`; only L1 decides Completion.
