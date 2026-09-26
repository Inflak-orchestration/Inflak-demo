---
name: l2-pN1-image-prompt-refinement
description: "Use when: P1 routes image-prompt-refinement for keyword-based prompt evolution or confirmed image generation."
---

# L2 Planner — Image Prompt Refinement

## Workflow End Authority

Only L1 Router owns canonical state and emits `decision: end`. L2 Planner diagnoses/selects interactions or directly invokes its instruction-ready executor; every actual result/failure returns to `l1-pN1-core-module`. L3 Designer is interaction-only; Execution Pathway never enters L3/L4.

## Layer & Role

Plan one `image-prompt-refinement` pass. Evolve T directly, not a separate Aug brief. Assess every registered gap, select one next material gap by dependencies, filter/rank eligible widgets, or emit `instruction_ready` for bounded active-model prompt preparation or confirmed `generate_image`. Do not render or design controls/profiles.

Interaction Pathway sends one gap through L3 Designer → L4 Renderer → L1. Execution Pathway directly realizes the ready plan through L2's executor → L1. Host Agent Return and Completion belong to L1 and do not enter L2; a routing failure returns directly to L1 without L3.

## IAI Domain Binding

| Node | Meaning |
| --- | --- |
| H | Image requester who owns intent and refinement choices |
| T | Current evolving image prompt |
| I | Keyword selection, manual prompt edit or acceptance |
| Aug | Not enacted separately; refinement folds into T, with no new state field |
| A | Actual generated image |
| G | Active model preparing prompt text, or separately the configured image generator |

## Interaction Chains

| Chain ID | Paradigm / function | Ordered edges |
| --- | --- | --- |
| p1-prompt-entry | Establish user-authored prompt text | `H→T` |
| p1-keyword-refinement | Extension, steering or style choice revises T | `H→I, I→T` |
| p1-prompt-review | Confirm or manually edit the current T | `H→I, I→T` |
| p1-image-generation | Generate from confirmed T, without synthetic Aug | `T→G, G→A` |

Named chains describe existing domain transformations, not required new canonical state. Prompt preparation is model realization within T, distinct from final image-generation G.

## Diagnosis

Read before/after GenAI invocation and prompt-only/artifact-grounded state. Assess every category as `open`, `resolved`, or `not applicable` using intent, actual returns and explicit scoped delegation; silence is not delegation. Record evidence/missing transfer/consequence of guessing in existing `iai_binding.reason` or `execution_instruction.purpose`. One selected widget limits this handoff, but simultaneously open keyword gaps that all route to `prompt-keyword-grid` may be bundled as separate rows in that widget. Dependencies, not table order, choose the next interaction.

| gap_type | Condition | Edge | Interaction goal |
| --- | --- | --- | --- |
| `extend_object_gap` | Material object detail or related content remains unresolved in T. | `I→T` | `select_keywords_to_extend_object` — supply expansion phrases. |
| `steer_object_gap` | A material object attribute, count, relation or direction requires a user choice. | `I→T` | `select_keywords_to_steer_object` — redirect the named content. |
| `style_gap` | Material visual treatment is unresolved or explicitly being revised. | `I→T` | `select_keywords_for_style` — choose treatment phrases. |
| `prompt_confirmation_gap` | Current prompt exists but lacks valid user acceptance after its latest changes. | `I→T` | `confirm_prompt` — accept, refine or edit exact current text. |
| `instruction_ready` (decision, not gap) | All relevant choices and current prompt acceptance are evidenced, or only bounded prompt/candidate preparation is justified. | `T→G` then `G→A` for images | Directly invoke generate_image for final work; active main_model preparation returns to L1 without final generation. |

Preserve all settled dimensions and reopen only after dependent changes. Missing intent, unavailable evidence/tools or refused indispensable choices return honestly to L1; do not fake a gap match or readiness. Final generation requires actual prompt-review acceptance; preparation never supplies that acceptance.

## Widget Registry Routing

| Gap | Widget / registered goal | Required returns |
| --- | --- | --- |
| extend_object_gap | prompt-keyword-grid / select_keywords_to_extend_object | selected_keywords, custom_keywords, freeform_note |
| steer_object_gap | prompt-keyword-grid / select_keywords_to_steer_object | selected_keywords, custom_keywords, freeform_note |
| style_gap | prompt-keyword-grid / select_keywords_for_style | selected_keywords, custom_keywords, freeform_note |
| prompt_confirmation_gap | prompt-review / confirm_prompt | action, edited_prompt, freeform_note |

Hard-filter local registry by exact planner/gap/goal/atomic edge, every required return, artifact support and actual renderer/capability/library availability. Rank by semantic coverage, artifact specificity, return coverage, runtime fitness, stable registry order then ID. Preserve one exact selected_widget_id; no type/skill/path/profile metadata in handoff. No eligible entry returns directly to L1 without L3: `reason: no_eligible_widget`, planner_id, diagnosed_gap (chain/evidence/edge/goal/returns), rejected_candidates with failed checks, return_to.

## Gap Handoff

Emit one gap request with chain_id, a primary exact gap/goal, binding source/edge/target/reason, display_context, typed expected_return, selected_widget_id, order 1 and actual depends_on_previous. Source includes edge source, destination equals target; pending I is not submitted input. For `prompt-keyword-grid`, also emit `included_keyword_gaps`: a nonempty ordered array containing every simultaneously open compatible keyword gap represented in this widget. Each record has exact `gap_type`, `interaction_goal`, `dimension` (`extend_object`, `steer_object`, or `style`) and an evidence-grounded `reason`; the primary gap is first. `display_context.candidates` is keyed by those dimensions. Include no resolved, not-applicable, confirmation, or execution gap. L3 preserves this grouping and evidence unchanged.

Illustration assumes both garden content extension and visual style are open; prepared choices are proposals and become two rows in one widget:

```json
{"handoff_type":"planner_handoff","planner_id":"image-prompt-refinement","planner_decision":"gap_open","gap_requests":[{"chain_id":"p1-keyword-refinement","gap_type":"extend_object_gap","interaction_goal":"select_keywords_to_extend_object","included_keyword_gaps":[{"gap_type":"extend_object_gap","interaction_goal":"select_keywords_to_extend_object","dimension":"extend_object","reason":"The garden content is unresolved."},{"gap_type":"style_gap","interaction_goal":"select_keywords_for_style","dimension":"style","reason":"The visual treatment is unresolved."}],"iai_binding":{"source_nodes":["I"],"maps_to_edge":"I→T","target_node":"T","reason":"Content extension and visual style are both open on I→T; each needs a separate candidate row before T can preserve the user's choices."},"display_context":{"current_prompt":"A garden","candidates":{"extend_object":[{"id":"flowers","keyword":"wildflower borders"},{"id":"pond","keyword":"a small lily pond"}],"style":[{"id":"watercolor","keyword":"soft watercolor"},{"id":"linocut","keyword":"bold linocut"}]}},"expected_return":{"selected_keywords":{"extend_object":[],"steer_object":[],"style":[]},"custom_keywords":{"extend_object":"","steer_object":"","style":""},"freeform_note":""},"selected_widget_id":"prompt-keyword-grid","order":1,"depends_on_previous":false}],"return_to":"l1-pN1-core-module"}
```

Do not require all dimensions, merge candidates across dimension rows, or flatten keyword objects. A singleton keyword gap still produces one row; two or three compatible open keyword gaps produce two or three rows in the same widget. Review uses action accept/refine/edit, edited_prompt string (empty outside edit), freeform_note string. Refinement gaps do not set target_tool: their object is T, not an image tool.

## Output (planner_handoff)

Exactly one mode: `gap_open` with one request, or `instruction_ready` with explicit executor, parameters and evidence-backed purpose. Example assumes actual current prompt-review acceptance of the quoted text and closure of all material refinement choices:

```json
{"handoff_type":"planner_handoff","planner_id":"image-prompt-refinement","planner_decision":"instruction_ready","execution_instruction":{"executor":{"kind":"tool","name":"generate_image"},"parameters":{"prompt":"A watercolor garden with wildflower borders"},"purpose":"The current prompt-review return accepted this exact text; extension, steering and style are settled by that review and prior choices. Generate only this confirmed prompt and return the actual artifact to L1."},"return_to":"l1-pN1-core-module"}
```

## Inputs and Procedure

Consume selected_planner, state_snapshot.user_text, optional prompt_draft/prior_returns/last_image, local registry projection and runtime availability. (1) Reconstruct current evidence. (2) Assess every category and dependency. (3) If needed, plan bounded active-main-model preparation of initial prompt/candidates or faithful incorporation of returned keyword/custom phrases; return actual prepared material through L1, never silently treat it as approved. (4) Route one eligible gap or directly execute a ready plan. (5) Return every result/failure to L1 before another action.

## Must / Must Not / Tools

Preserve prompt text, dimensions, selected/custom phrases and changed-version acceptance. Never add unselected content or a separate Aug brief. Only L2 directly invokes `generate_image` after current confirmation; use only supported actual size/quality/background parameters when supplied. Active main_model performs bounded text preparation with explicit purpose, not a fictitious tool. L4 alone invokes rendering. No task execution before instruction_ready, invented artifacts, generic approval checkbox or registry substitutions.

## Stop / Continue / Escape

Stop this local pass after eligible L3 handoff or actual execution result/failure to L1. Continue only through fresh L1 reassessment. Missing indispensable intent/capability or refusal escapes to L1, not false readiness.

## Next

Interaction Pathway: selected gap → L3 Designer → L4 Renderer → L1. Execution Pathway: L2 directly invokes the selected executor without L3/L4 or an executor skill. All routing/execution failures return directly to `l1-pN1-core-module`; only L1 chooses Completion.
