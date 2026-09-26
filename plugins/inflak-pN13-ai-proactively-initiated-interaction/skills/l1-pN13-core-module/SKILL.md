---
name: l1-pN13-core-module
description: "Use when: P13 receives any non-empty user intent or re-enters after intention choices, disambiguation, implementation input, execution, dismissal, or failure."
---

# Layer 1 - P13 Core Module

## Layer & Role

Read [the root contract](../../SKILL.md) as documentation on entry. This is the sole compatibility runtime entry, not a root alias. Only L1 Router owns canonical state, merging and Completion with `decision: end`. On every initial request, L2 routing failure, L3 validation failure, L4 widget/renderer return and executor result/failure, reconstruct the newest state before choosing a new pathway. Downstream evidence is nonterminal.

## Four Pathways

| Pathway | Flow |
| --- | --- |
| Interaction Pathway | user/return → L1 → L2 gap + selection → L3 design → L4 render → L1 |
| Execution Pathway | user/return → L1 → L2 plan → execute/realize → L1; L2 directly invokes the active main model without L3 or L4. |
| Host Agent Return | user → L1 → host agent; retain `decision: bypass` for a direct out-of-scope answer. |
| Completion | user/return → L1 → Completion; only L1 emits `decision: end`. |

Reconstruct P13 state and route to exactly one planner. Do not infer intent, rank recommendations, select interactions, call task tools, or mutate artifacts.

## State

- `user_text`: the current non-empty user turn.
- `conversation_context`: relevant prior turns, active topic, and unresolved decisions.
- `task_context`: active workflow, available capabilities, artifacts, constraints, and known preferences.
- `explicit_observations`: facts stated by the user or supplied by trusted context.
- `intent_hypotheses`: ranked likely goals with evidence, uncertainty, and disconfirming signals.
- `recommendations`: ranked feasible next actions, with one supported best recommendation only when the evidence supports ranking; uncertainty stays explicit.
- `active_recommendation_id`: actual recommendation currently under conversational consideration.
- `disambiguation`: one answer to a discriminating question when confidence is low.
- `user_decision`: selected, adjusted, questioned, or dismissed recommendation state.
- `selected_recommendation`: the actual user-confirmed recommendation retained for L2 implementation, not an executed result.
- `implementation_widget_return`: newest validated return from an adapted implementation widget, including its selected widget identity and declared values.
- `execution_status`: `not_started`, `ready`, `running`, `succeeded`, or `failed` for the confirmed recommendation.
- `execution_result`: the concrete answer, artifact, mutation result, or structured failure returned by the main-model executor.
- `prior_returns`: ordered interaction returns.

The newest valid return is authoritative for the state it updates. Map G→I responses at I to `disambiguation` or `user_decision`, then retain an explicitly selected recommendation with its identity and scope. Map implementation I→Aug or I→A returns at that preserved destination to `implementation_widget_return`, retaining selection identity, exact declared values, source/revision and chain provenance. These destinations are IAI nodes; the deterministic merge names the canonical domain field, not a replacement node. Never infer approval from pending controls, a ranking, dismissal or tool diagnostics. If material user text, conversation context, or available capabilities change, invalidate hypotheses and recommendations while retaining explicit observations that remain true; also invalidate dependent implementation/execution readiness without discarding historical results.

## Routing

Route any non-empty user intent to `pN13-proactive-intent-recommendation` when P13 is active, regardless of domain, modality, specificity, or whether an artifact exists. Empty turns and transport-only events bypass. A clear request is still inferred and ranked internally; user-facing output remains concise conversational choices and never exposes the analysis record.

```json
{"handoff_type":"core_handoff","decision":"route_to_planner","selected_planner":"pN13-proactive-intent-recommendation","state_snapshot":{"user_text":"","conversation_context":{},"task_context":{"available_capabilities":[]},"explicit_observations":[],"intent_hypotheses":[],"recommendations":[],"active_recommendation_id":"","disambiguation":{},"user_decision":{},"selected_recommendation":{},"prior_returns":[]}}
```

Every interaction/execution return and failure re-enters this skill. Use the selected local planner registry entry's exact skill `l2-pN13-proactive-image-edit` and compatibility path only after routing. The planner ID remains generic recommendation; no same-name skill from another plugin substitutes for this entry.

## Completion

Do not end merely because a recommendation was selected, adjusted, or refined through an implementation widget. Store each validated `implementation_widget_return`, route the confirmed recommendation back to Layer 2 until it emits an execution instruction, then accept the main-model result on re-entry. Only end after successful execution has populated `execution_result`, or after an explicit dismissal. If execution fails, retain the selected recommendation, implementation return, and failure details, then route to Layer 2 for one grounded retry, adjustment, or a concise blocked result rather than claiming completion.

## Must / Must Not / Next

Preserve actual sources, user values, selection scope and failure evidence; emit `core_handoff` with one registered `selected_planner` and `state_snapshot` limited to declared required/optional fields plus universal user text/returns. Never diagnose a gap, choose a widget, call task/render tools or invent completed work. Continue by loading the registry-selected L2; all downstream paths return here before another action.