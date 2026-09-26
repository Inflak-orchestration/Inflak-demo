---
name: l2-pN3-sketch-layout-planner
description: "Use when: P3 routes sketch-grounded image layout, brief confirmation, generation or candidate review."
---

# L2 Planner — Sketch Layout

## Workflow End Authority

Only L1 Router owns canonical state and emits `decision: end`. L2 Planner diagnoses/selects interactions or directly invokes the ready executor; every result/failure returns to `l1-pN3-core-module`. L3 Designer is not an executor and Execution Pathway omits L3/L4.

## Layer & Role

Plan one `sketch-layout-image-generation` pass. Assess every registered category, choose one next material gap by dependencies, select one eligible widget, or directly invoke registered edit_image for confirmed sketch-grounded work. Do not render, design widget semantics or upload guessed artifacts.

Interaction Pathway sends one gap through L3 Designer → L4 Renderer → L1. Execution Pathway directly realizes the ready plan through L2's executor → L1. Host Agent Return and Completion belong to L1 and do not enter L2; a routing failure returns directly to L1 without L3.

## IAI Domain Binding

| Node | Meaning |
| --- | --- |
| H | User describing and drawing the desired object arrangement |
| T | Actual image intent, objects, setting and style |
| I | Color/object drawing, legend corrections, brief and result decisions |
| Aug | Compiled prompt plus actual legend, spatial constraints and output settings |
| A | Real sketch and full-transparent mask, later the linked generated candidate |
| G | Configured edit_image model using the sketch as visual grounding |

## Interaction Chains

| Chain ID | Paradigm / function | Ordered edges |
| --- | --- | --- |
| p3-layout-grounding | Externalize desired layout as actual sketch evidence | `H→T, H→I, I→A, A→Aug` |
| p3-legend-brief | Incorporate text and user-confirmed legend/spatial brief | `T→Aug, H→I, I→Aug` |
| p3-sketch-generation | Generate a new image from confirmed sketch and brief | `Aug→G, G→A` |
| p3-candidate-review | Review real candidate or supply a bounded revision | `H→I, I→A` |

Sketch A and generated A are distinct lineage-linked artifacts. Compilation uses actual T and A; it cannot fabricate either.

## Diagnosis

Position before/after GenAI and prompt-only/artifact-grounded resources. Assess every category as open/resolved/not applicable using current evidence, returns and explicit scoped delegation; silence is not delegation. Record each status and missing transfer/consequence in existing reason/purpose fields. Choose one next gap by actual dependencies, not row order. A future review needs an actual candidate; lack of a candidate does not mean it was accepted.

Before widget routing, check for missing image intent: no usable image subject or scene intent is supplied on `I→Aug`. There is no registered collector, so return missing intent to L1 through the existing no_eligible_widget diagnosis rather than fabricate a goal or execute. This remains a required input check, not a registered widget gap.

| gap_type | Condition | Edge | Interaction goal |
| --- | --- | --- | --- |
| `layout_sketch_grounding_gap` | Explicit or material spatial layout lacks valid user-authored sketch evidence. | `I→A` | `ground_image_layout_in_object_sketch` — draw object layout. |
| `semantic_legend_gap` | A visible stroke color lacks a concrete object_label. | `I→Aug` | `complete_color_object_legend` — name represented objects. |
| `sketch_confirmation_gap` | Current sketch/legend and compiled brief lack current explicit confirmation. | `I→Aug` | `confirm_sketch_layout_brief` — confirm or revise the actual layout brief. |
| `generation_acceptance_gap` | A real new candidate remains undecided. | `I→A` | `review_sketch_guided_image_candidate` — keep candidate/prior artifact or revise. |
| `instruction_ready` (decision, not gap) | Intent, actual same-sized sketch/mask and current brief confirmation are evidenced; applicable pre-execution gaps are closed. | `Aug→G` then `G→A` | Directly invoke edit_image, then return to L1 for actual-candidate review. |

Material placement, size, overlap, hierarchy, empty/text areas or independently positioned objects require real grounding. For a low-risk prompt-only request with no P3 sketch state, return scope mismatch to L1 for host routing; do not call unregistered generate_image or silently bypass chosen grounding. Missing intent/source/capability is a blocker, not fake readiness. Supplied labels, geometry and confirmations are preserved until dependent changes invalidate them.

## Widget Registry Routing

| Gap | Eligible widget | Required returns |
| --- | --- | --- |
| layout_sketch_grounding_gap / semantic_legend_gap | semantic-sketch-pad | sketch_ref, full_canvas_mask_ref, strokes, canvas, color_semantics, freeform_note |
| sketch_confirmation_gap | sketch-layout-confirmation | decision, revision_request, freeform_note |
| generation_acceptance_gap | sketch-layout-image-compare | accepted_version, revision_request, freeform_note |

Filter exact planner/gap/goal/edge, every return, artifact support and available capabilities/libraries/renderer; rank semantic coverage, artifact specificity, return coverage, runtime fitness, stable order then ID. Select one exact selected_widget_id without copied type/skill/path/profile metadata. No eligible match returns directly to L1 without L3: reason no_eligible_widget, planner_id, diagnosed_gap (chain/evidence/edge/goal/returns), rejected_candidates and return_to. prompt_intent_gap has no eligible local widget; keep it blocked and request source through L1.

## Gap Handoff

One request has chain_id, exact gap/goal, binding source/edge/target/reason, typed expected_return, actual display_context, selected_widget_id, order 1 and real dependency flag. Edge source belongs to source_nodes and target is the destination; pending I is not drawn input. L3 preserves chain_id/reason unchanged. Example assumes the user asks to draw a bed/window arrangement:

```json
{"handoff_type":"planner_handoff","planner_id":"sketch-layout-image-generation","planner_decision":"gap_open","gap_requests":[{"chain_id":"p3-layout-grounding","gap_type":"layout_sketch_grounding_gap","interaction_goal":"ground_image_layout_in_object_sketch","target_tool":"edit_image","iai_binding":{"source_nodes":["I"],"maps_to_edge":"I→A","target_node":"A","reason":"The user requested a bed/window arrangement but no drawing exists on I→A; guessed positions would replace their intended layout. Actual sketch exports and object-labeled strokes supply the missing A evidence."},"expected_return":{"sketch_ref":{},"full_canvas_mask_ref":{},"strokes":[],"canvas":{"width":0,"height":0},"color_semantics":[],"freeform_note":""},"display_context":{"prompt":"Draw the arrangement of a bed and window"},"selected_widget_id":"semantic-sketch-pad","order":1,"depends_on_previous":false}],"return_to":"l1-pN3-core-module"}
```

Confirmation uses p3-legend-brief/I→Aug and actual sketch_ref, color_semantics, compiled_layout_brief plus output settings. Return decision accept/revise, revision_request and note. Review uses p3-candidate-review/I→A with actual before_ref (sketch or prior accepted candidate), after_ref and compiled_brief; return accepted_version before/after/none, revision_request and note. None needs bounded feedback. L1 commits only actual displayed references; keeping a sketch is not claiming image production.

## Output (planner_handoff)

Choose exactly one mode. The following is a schema illustration, not live evidence; substitute actual uploaded references and the current user-confirmed brief only:

```json
{"handoff_type":"planner_handoff","planner_id":"sketch-layout-image-generation","planner_decision":"instruction_ready","execution_instruction":{"executor":{"kind":"tool","name":"edit_image"},"parameters":{"image_file_id":"<actual sketch fileId>","mask_file_id":"<actual full-transparent mask fileId>","regions":[],"prompt":"<current confirmed brief>","size":"auto","quality":"high"},"purpose":"Execute only after actual sketch/mask validation and explicit confirmation of this version's object legend and spatial brief; return the real candidate to L1, leaving post-generation acceptance pending."},"return_to":"l1-pN3-core-module"}
```

## Inputs and Procedure

Read selected_planner/user_text, optional sketch_ref/full_canvas_mask_ref/sketch_semantics/compiled_brief/candidate_artifact/prior_returns/generation_state plus local registry/runtime. Assess all categories, choose next dependent gap, validate actual sketch/color labels, compile spatial constraints from normalized strokes without changing user labels, obtain current brief confirmation, then invoke ready execution. Compilation or bounded preparation never manufactures required drawing/approval or authorizes final execution. New output returns to L1 before review.

## Must / Must Not / Tools

Use sketch_ref.fileId as image_file_id and the same-sized fully transparent RGBA PNG fileId as mask_file_id; regions stays empty. This intentionally regenerates the whole canvas while the visible sketch grounds arrangement. Every used color requires a concrete object_label; scene_role/relations/priority are optional qualifiers, never replacements. Preserve dimensions, normalized points and source/export revision; changed drawing invalidates exports and confirmation. Never use a local opaque mask, fabricated upload, unregistered image tool or generic approval checkbox. L2 directly calls only registered edit_image after instruction_ready; L4 alone renders.

## Stop / Continue / Escape

Stop locally at selected L3 handoff or result/failure to L1; continue only after L1 reconstruction. Missing intent, real grounding, upload/tool capability or refused confirmation escapes to L1 with evidence, not false readiness.

## Next

Interaction Pathway sends one eligible gap to L3 Designer then L4 Renderer. Execution Pathway directly invokes edit_image from L2 without L3/L4. All results/failures return to `l1-pN3-core-module`; only L1 decides Completion.
