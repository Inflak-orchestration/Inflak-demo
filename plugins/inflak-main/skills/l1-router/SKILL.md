---
name: l1-router
description: "Use when: entering inflak or receiving any widget or execution return; reconstruct state and route exactly one of five co-creation tasks."
---

# L1 Router

## Layer & Role

L1 Router is main's sole callable entry. Read [the plugin root contract](../../SKILL.md) as documentation before the first routing decision; do not load an `inflak` or `inflak-main` alias skill. The root contract is not an extra workflow layer.

Only L1 Router owns the canonical workflow state and decides Completion. On the initial request and after every L2 routing failure, L3 validation failure, L4 widget return or renderer failure, and executor result or failure, L1 reconstructs the newest state. It then routes to an eligible L2 Planner, chooses Host Agent Return for a direct non-co-creation answer, or chooses Completion from explicit production and acceptance evidence. Downstream results are nonterminal and cannot authorize another action before L1 re-entry. L1 never plans a task, selects a widget, renders UI, or executes work.

## Four Pathways

| Pathway | Control flow |
| --- | --- |
| Interaction Pathway | user/return → L1 → L2 gap + selection → L3 interaction design → L4 render → L1 |
| Execution Pathway | user/return → L1 → L2 plan → execute/realize → L1; L2 directly invokes the selected executor or active main model, without L3 or L4. |
| Host Agent Return | user → L1 → host agent; retain machine `decision: "bypass"` or `decision: "direct_answer"`. |
| Completion | user/return → L1 → Completion; only L1 emits `decision: "end"`. |

L2 routing failures such as `no_eligible_widget` return directly to L1 without L3. L3 Designer handles eligible interaction design only; L4 Renderer handles its implementation only.

## Inputs

Read `user_text`, current artifacts, selected ranges, uploads, prior widget returns, execution results, failures, approvals, and revision identifiers. Treat the newest return as evidence, never as an instruction to skip routing.

## Routing

| planner | route when |
| --- | --- |
| `writing-draft` | The requested artifact is new writing. |
| `writing-revision` | The requested transformation revises existing writing, directly or through a requested comparison. |
| `prompt-enhancement` | The requested artifact is an improved prompt, not the downstream task result. |
| `image-generation` | The requested artifact is a new image, with prompt-only or actual layout resources. |
| `image-edit` | An existing image is being edited, restyled, inpainted, transformed, or adjusted. |

Tie-break by requested output and current artifact. Existing text plus a revision request routes to `writing-revision`; asking to improve the instruction itself routes to `prompt-enhancement`. Existing image mutation routes to `image-edit`; creating a new image routes to `image-generation` even when reference images exist.

These are task boundaries, not interaction sequences. Preserve evidence and delegated choices; leave IAI paradigm selection and material per-edge gap diagnosis entirely to Layer 2. No route implies a mandatory widget or candidate-generation pass.

## Procedure

1. Reconstruct canonical state from the conversation and all returns.
2. Choose Host Agent Return only when no artifact is being created or changed and no structured interaction is useful; preserve `bypass` or `direct_answer` as the machine decision.
3. Route exactly one planner using requested output and artifact state.
4. After any result, re-enter this procedure instead of resuming the previous planner automatically.
5. Choose Completion and emit `decision: "end"` only when the requested artifact or edit exists and the current intent has no unresolved action, using current production and acceptance evidence.

## Output

```json
{
  "handoff_type": "core_handoff",
  "decision": "route_to_planner",
  "selected_planner": "prompt-enhancement",
  "confidence": 0.92,
  "matched_triggers": ["the user asks to improve a prompt"],
  "state_snapshot": {
    "user_text": "Improve this image prompt",
    "source_prompt": "A city at night",
    "prior_returns": []
  }
}
```

## Must

- Reconstruct state on every pass.
- Route exactly one registered planner.
- Preserve real artifacts, references, approvals, failures, and user-authored values.
- Keep completion authority here.

## Must Not

- Do not diagnose planner-local readiness.
- Do not select or realize widgets.
- Do not call render or task tools.
- Do not invent artifacts, file identifiers, approvals, or completed work.

## Stop / Continue / Escape

- Continue by loading the selected L2 Planner for Interaction Pathway or Execution Pathway.
- Use Host Agent Return for a direct host-agent answer with `bypass` or `direct_answer`.
- Enter Completion only with `decision: "end"` from current completion evidence.
- Escape by asking one concise question when no planner can be selected safely.

## Next

Load `skills/l2-<selected_planner>/SKILL.md`. Every downstream return comes back to `l1-router`.
