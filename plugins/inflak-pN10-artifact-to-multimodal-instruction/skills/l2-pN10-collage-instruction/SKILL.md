---
name: l2-pN10-collage-instruction
description: "Use when: L1 routes P10 Analyze for grounded decisions or authorized instruction execution."
---

# L2 Planner — P10

## Workflow End Authority

Only `l1-pN10-core-module` owns canonical merging and `decision: end`. All results/failures return there; planning and patch results are nonterminal.

## Layer & Role

Diagnose one next evidence-grounded gap and select its eligible widget, or emit `instruction_ready` and load exec-pN10-svg-instruction to invoke the registered executor/active `main_model`. Execution never loads L3/L4. L3 owns semantic UI design; L2 never renders or produces a final workflow response.

## Inputs

Read `core_handoff` from L1; require `selected_planner: pN10-collage-instruction` and its `state_snapshot.source_artifact_ref`. Consume declared scene/analysis, suggestions/decisions, active object, Aug, review/candidate/execution/comparison state and prior returns from that snapshot. No user prompt is required. Read registries, current capabilities and this skill's [tool-use instructions](../exec-pN10-svg-instruction/SKILL.md) before ready execution.

## IAI Domain Binding

| Node | Meaning |
| --- | --- |
| H | User explicitly invoking Analyze and deciding suggested changes |
| T | Optional generated readable instruction, never a required input prompt |
| I | Stable-target, relation, operation, suggestion and final Aug decisions |
| Aug | Generated multimodal instruction with full decision history |
| A | Exact source SVG scene and actual revised artifact |
| G | Model evidence/proposal/compilation work and registered executors |

## Interaction Chains

| Chain ID | Function | Ordered edges |
| --- | --- | --- |
| svg-analysis | Ground artifact-first suggestions | `A→G, G→I` |
| svg-instruction | Resolve targets, relations, operations and Aug authorization | `A→G, G→I, I→Aug, A→Aug` |
| svg-execution | Validate and execute approved Aug | `A→Aug, Aug→G, G→A` |
| svg-comparison | Compare real source/revised outputs | `G→A, I→A` |

## Diagnosis

Read before/after generation and artifact-grounded resource state. Assess every registered gap as `resolved`, `open`, or `not applicable` from facts, submitted decisions and scoped permission; record evidence in reason/purpose. Silence is not delegation. Choose one next gap by dependencies: target before relation/operation, complete candidates before decisions, full decisions before final Aug. Reuse valid approval; missing scene/model-only synthesis/validation are bounded execution, not fake user gaps. Source/tool failures return directly to L1.

| gap_type | Condition | Edge | Interaction goal |
| --- | --- | --- | --- |
| `instruction_target_gap` | A candidate's primary target is materially ambiguous or unconfirmed. | `G→I` | `confirm_instruction_targets` |
| `instruction_relation_gap` | A multi-object candidate lacks explicit endpoints, roles or preserve constraints. | `I→Aug` | `define_instruction_relations` |
| `instruction_operation_gap` | A candidate lacks supported operation/required typed values. | `I→Aug` | `define_instruction_operation` |
| `suggestion_decision_gap` | Complete suggestions lack explicit accepted/edited/rejected decisions. | `G→I` | `review_object_suggestions` |
| `augmentation_review_gap` | Complete actionable Aug lacks final concrete execution authorization. | `I→Aug` | `review_augmented_instruction` |
| `artifact_comparison_gap` | Validated actual changes lack source-versus-revised comparison acceptance. | `I→A` | `compare_svg_revisions` |
| `instruction_ready` | All relevant execution choices are closed, or bounded grounding/proposal/candidate/validation preparation has its own inputs/permission. | `Aug→G` then `G→A` | Direct registered inspection/materialization/apply/validation or main-model work; return to L1. |

## Widget Registry Routing

Hard-filter exact planner/gap/goal/edge, all required returns, artifact type and capabilities/libraries/renderer availability. Rank semantic coverage, artifact specificity, return coverage, runtime fitness, stable registry order then ID. No match returns the routing-failure envelope defined below directly to L1 without L3 or readiness fiction.

## Domain Protocol

- Analysis records only current IDs/types/labels/transforms/order/visibility/relationships/uncertainty. Prepare 3–6 grounded suggestions when supported, never padded duplicates. Cover compatible image replacement/restyle, layout/scale, editable text and visual style; record missing capability families.
- Candidates preserve `suggestion_id`, `object_ids`, `primary_object_id`, `title`, `objective`, `operations`, optional `relations`/`constraints`, rationale, `support: strong|partial`, uncertainty/recommendation and concrete before/after values. Recommendations are not accepted.
- Prefer materially distinct changes: normal layout moves at least 2% of canvas dimension and uniform resize at least 10%, unless a precise smaller user change is evidenced. Reject unchanged style/order/zero movement. IDs/targets are not inferred from proximity.
- Decision records preserve suggestion ID, `accepted|edited|rejected`, confirmed object IDs, edited objective/operations/relations/constraints, order/timestamp and provenance. Every candidate gets a decision; all-rejected work returns to L1 for explicit regeneration/dismissal instead of empty execution.
- Semantic vocabulary: `move`, `resize`, `rotate`, `reorder`, `align`, `edit_text`, `add`, `remove`, `replace`, `restyle`, `increase_prominence`, `change_palette`. Relations: `left_of`, `right_of`, `above`, `below`, `inside`, `in_front_of`, `behind`, `aligned_with`, `avoid_overlap`; records use `source_object_id`, `type`, `target_object_id`, roles target/reference/preserve. Reject self-relations, unsupported types and raw markup.
- Canonical instruction retains `schema_version`, `source_artifact` (`fileId`, positive revision, `artifact_type`), objective, object bindings, actionable operations, relations, constraints, generated natural-language instruction, complete suggestion decisions, field provenance and status. Provenance is artifact-confirmed/model-suggested/user-selected/missing. Rejected items remain history only.
- Final Aug confirmation authorizes displayed accepted/edited operations without per-operation reconfirmation. The Host Agent checks semantic completeness, scene bindings and actual approval against the execution reference, then materializes required alpha candidates and applies one homogeneous family per pass through shared Host tools. Preserve exact confirmed instruction and interaction bindings, advance own execution revisions through L1, verify actual before/after deltas and validate separately. No export file or exported hash is required. Never submit semantic names as manager operations.
- Source changes invalidate stale decisions; missing material value reopens its real gap. Renderer source stays read-only. Validation alone is not completion; final comparison binds original source and actual resulting revision.

## Gap Handoff

Assess all categories, choose one dependency-ready gap and filter/rank before emitting `handoff_type: planner_handoff`, `planner_id: pN10-collage-instruction`, `planner_decision: gap_open`, exactly one item in `gap_requests`, and `return_to: l1-pN10-core-module`. The request requires `chain_id` from the named chains, registered `gap_type` and `interaction_goal`, exact eligible registry `selected_widget_id`, `order: 1`, boolean `depends_on_previous`, grounded `display_context`, and exact typed `expected_return`. Its `iai_binding` contains `source_nodes` (nonempty node array), one registered atomic `maps_to_edge`, `target_node` and nonempty evidence-grounded `reason`. The edge source belongs to `source_nodes`; its destination equals `target_node` and an allowed state target. L3 preserves all binding fields and the chain unchanged; no copied L3 type/skill/render metadata.

If none is eligible, emit a routing-failure envelope with `reason: no_eligible_widget`, copied `planner_id`, `diagnosed_gap` retaining `chain_id`, `gap_type`, `interaction_goal`, `iai_binding`, evidence in `display_context` and exact `expected_return`; `rejected_candidates` is a deterministic array of actual candidate IDs and their nonempty failed-check lists (empty only when the registry has no candidates). Set `return_to: l1-pN10-core-module`. Omit `selected_widget_id` and `execution_instruction`; do not disguise failure as `instruction_ready`, substitute a widget or enter L3/L4.

All P10 widgets use `return_mode: agent_interpreted`, not a fixed registry schema. `expected_return` and the L3 submission mapping describe this interaction's producible JSON values; retain their types and semantics without restricting every instance to a static key list. L1 interprets the actual return against current context before merging by suggestion/interaction/revision, never by guessed IDs. Unclear values reopen the material gap, not implied consent.

Typical target/decision values include `suggestion_decisions`, `action`; operation values `suggestion_id`, `instruction_operation`, `action`; relation values `suggestion_id`, `relations`, `constraints`, `action`; review values complete `instruction`, `action`; comparison values `action`. These are domain guidance, not mandatory transport keys. Complete explicit decisions, real target/source bindings and final concrete Aug authorization remain necessary before execution regardless of serialization.

## Execution Handoff

Ready handoff carries `handoff_type: planner_handoff`, `planner_id: pN10-collage-instruction`, `planner_decision: instruction_ready`, `return_to: l1-pN10-core-module`, and `execution_instruction` with `executor` (`kind: tool` plus registered allowed `name`, or `kind: main_model`), real typed `parameters`, evidence-backed nonempty `purpose` and existing interaction/result bindings. Omit `gap_requests` and `selected_widget_id`. Directly invoke the selected executor, then return actual result/failure to L1. Only bounded preparation may run while choices remain open; never final mutation. The active Host Agent performs semantic checks and compilation; shared tools perform revision-bound execution and deterministic SVG validation.

## Must / Must Not

No invented targets/values/assets/approval, no no-op completion, no mixed operation families, no unconfirmed mutation, no generic approval checkbox, no rendering or final response. Actual tools remain registry-bound; reference documents are noncallable.

## Execution Skill Routing

For `instruction_ready`, finish the existing `execution_instruction` and load `exec-pN10-svg-instruction`. Keep `executor.kind`, tool name when selected, parameters, purpose and approval/result bindings unchanged. L2 plans; the execution skill performs one planned task and returns to L1. Do not invoke task tools or realize model work in the planner before this handoff, or route execution through L3/L4. Gap selection still routes to the selected L3 designer. Failures return directly to L1.

## Next

Gap → L3 design → L4 → L1. Ready plan → `exec-pN10-svg-instruction` → L1. Any failure → `l1-pN10-core-module` before further planning or execution.