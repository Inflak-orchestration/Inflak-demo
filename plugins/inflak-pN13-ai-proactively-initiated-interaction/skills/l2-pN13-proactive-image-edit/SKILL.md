---
name: l2-pN13-proactive-image-edit
description: "Use when: L1 selects generic P13 intent recommendation or implementation of a confirmed action; the image-edit filename is compatibility only."
---

# L2 Planner — P13 AI-Proactively-Initiated Interaction

## Workflow End Authority

Only `l1-pN13-core-module` owns canonical state/merging and Completion (`decision: end`). Every interaction/execution result or failure returns there immediately. Selection, implementation input and readiness are nonterminal.

## Layer & Role

For `pN13-proactive-intent-recommendation`, infer any non-empty user intent, diagnose one material per-edge gap, select one eligible registry ID or directly execute a ready instruction through the active main model. L3 only designs interactions; L4 renders. L2 never renders, authors semantic controls, silently switches plugins or produces the final workflow response. Its physical filename is compatibility, not an image-edit business contract.

## IAI Domain Binding

| Node | P13 meaning |
| --- | --- |
| H | User confirming, adjusting or declining a proposed next action. |
| T | Current text, relevant conversation and explicit constraints. |
| I | Conversational choice or task-specific implementation input. |
| Aug | Confirmed actionable intent with submitted implementation constraints. |
| A | Actual sources, annotations, prior decisions and execution result. |
| G | Active main model inferring goals and performing authorized work. |

## Interaction Chains

| Chain ID | Paradigm / function | Ordered edges |
| --- | --- | --- |
| p13-recommendation | Ground alternatives and select an intended action | `H→T, T→G, A→G, G→I, I→A, A→Aug, Aug→G, G→A` |
| p13-implementation | Resolve confirmed-action parameters/content/review | `H→I, I→Aug, A→Aug, Aug→G, G→A` |
| p13-spatial-implementation | Collect real source-aligned drawing/annotation | `H→I, I→A, A→Aug, Aug→G, G→A` |

Recommendation A→G uses real artifacts only when present; I→A records selection. Spatial I→A adds annotation, not the final result. A→Aug incorporates existing evidence rather than requesting it again. Aug→G is L2's direct invocation; G→A returns actual output.

## Diagnosis

Read before/after invocation and prompt-only/artifact-grounded resources. Assess every registered category as `open`, `resolved`, or `not applicable` with source evidence, missing transfer, consequence of guessing and closure/delegation scope in existing reason/purpose. Silence is not delegation; preserve settled decisions. Choose exactly one next gap by dependencies, not table order: disambiguation before selection when necessary, implementation after confirmed intent and actual source availability. Missing model synthesis is bounded execution, not a human gap.

| gap_type | Condition | Edge | Interaction goal |
| --- | --- | --- | --- |
| `intent_disambiguation_gap` | Evidence supports materially different goals and one answer changes the intended next action. | `G→I` | `present_confirmed_intention` — ask one discriminating question. |
| `intention_presentation_gap` | Feasible suggestions exist but the user has not selected or explicitly authorized a next action. | `G→I` | `present_confirmed_intention` — offer conversational choices and freeform intention. |
| `implementation_interaction_gap` | A confirmed action lacks consequential user parameters, editable content, selection or review evidence. | `I→Aug` | `refine_confirmed_implementation` — supply missing implementation constraints. |
| `implementation_interaction_gap` | A confirmed action lacks necessary actual source-aligned drawing or annotation. | `I→A` | `ground_confirmed_implementation` — submit spatial evidence. |
| `instruction_ready` | All applicable gaps are evidenced closed and execution authorized; alternatively only bounded inference/preparation is needed, leaving choices open and forbidding final execution. | `Aug→G` then `G→A` | Direct active-main-model synthesis or confirmed implementation, then L1. |

Store observations separately from inferences. Infer 1–3 hypotheses where useful and 2–5 distinct recommendations with stable identity, label, next action and private evidence, uncertainty, feasibility, tradeoffs and reversibility. Rank one supported best recommendation internally unless uncertainty prevents it. Show concise possibilities, not numeric confidence/rationale dossiers. A direct answer may be a suggestion; images are never the default. Precise supplied/confirmed intent can close selection without repetition.

## Widget Registry Routing

| Gap / goal | Candidate ID | Domain return |
| --- | --- | --- |
| disambiguation/presentation / `present_confirmed_intention` | `p13-intention-basic-widget` | Exact planner-declared basic values, stable selection and optional freeform intention. |
| implementation / `refine_confirmed_implementation` | `p13-implementation-widget` | Typed parameters/content/selection/review on I→Aug. |
| implementation / `ground_confirmed_implementation` | `p13-implementation-widget` | Real source-bound annotation/drawing on I→A. |

Hard-filter exact planner/gap/goal/edge, all returns under declared policy, artifact support and actual capabilities/libraries/renderer. For implementation require one registered `implementation_mode` with supported operations producing the requested types; mode is task context, not another gap. Rich modes require actually available approved pinned libraries, not promised fallbacks. Rank eligible entries by semantic coverage, artifact specificity, return coverage, runtime fitness, registry order then ID. No match returns `reason: no_eligible_widget`, `planner_id`, `diagnosed_gap` (chain/evidence/edge/goal/returns), `rejected_candidates`, `return_to: l1-pN13-core-module` directly to L1 without L3 or false readiness.

## Inputs (from core_handoff and widget registry)

Require `selected_planner: pN13-proactive-intent-recommendation`, `user_text`, `conversation_context`, `task_context`. Consume registered optional observations/hypotheses/recommendations, active identity, disambiguation, decision, confirmed recommendation, `implementation_widget_return`, `execution_status`, `execution_result`, `prior_returns`; use actual capability context and local registry projections. Stable source IDs are not paths or filenames.

## Gap Handoff

Emit `handoff_type: planner_handoff`, exact `planner_id`, `planner_decision: gap_open`, one `gap_requests` item and exact L1 `return_to`. Include named `chain_id`, exact `gap_type`/`interaction_goal`, `selected_widget_id`, `iai_binding` (`source_nodes`, `maps_to_edge`, `target_node`, meaningful `reason`), exact typed `expected_return`, `order`, `depends_on_previous`, grounded `display_context`. Edge source belongs to sources; destination equals target and allowed `state_update_target`. Explain source → missing transfer → target deficit → return closure in one/two sentences; pending input is not submitted evidence. L3 preserves chain/reason unchanged; copy no type/modality/skill/path/controls/renderer metadata.

Recommendation context contains actual `{recommendation_id,label,next_action}` possibilities and optional declared freeform input. Implementation context contains confirmed recommendation, exact registered mode, actual items/sources and constraints. Returns are exact producible task keys/types, never fake successful payloads.

## Procedure and Output (planner_handoff)

1. Read L1 evidence, position both axes, assess every category and select one dependency-ready action.
2. Route one eligible gap through L3/L4 or return a genuine routing/capability failure directly to L1.
3. Ready work emits `planner_decision: instruction_ready`, `execution_instruction`, exact `planner_id`, `handoff_type: planner_handoff`, `return_to: l1-pN13-core-module`, without gaps.
4. `execution_instruction.executor` is `{kind: main_model}`. `parameters` preserves confirmed action, source refs, newest validated implementation return and compiled instruction. `purpose` states category closure, delegation, consent and scope, or bounded preparation with choices open. L2 directly performs it without L3/L4 or an executor skill.
5. Return actual `execution_result`/status or failure immediately to L1. Preparation returns hypotheses/recommendations, never selected-task success. Do not repeat successful work after re-entry.

## Must / Must Not / Tools

Keep selection nonterminal and preserve implementation evidence. Do not execute the recommended action before confirmed intent, gap closure, capability and risk/consent checks. No task tools are registered/allowed; main-model work does not fabricate image/file mutations or authorize hidden tools. Unsupported work returns a blocker to L1. L4 alone calls `render_html_widget`; L2 never renders, substitutes operations or decides Completion.

## Stop / Continue / Escape

Stop locally at a handoff or actual result/failure return; continue only through L1. Escape on refusal, missing source/capability or unsafe action without inventing results or replacement gaps.

## Next

Interaction Pathway sends the exact selection to L3 then `l4-pN13-widget-renderer`. Execution Pathway directly invokes the active main model without L3/L4. Every result/failure re-enters `l1-pN13-core-module`; Host Agent Return and Completion belong only to L1.