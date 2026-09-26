---
name: l1-pN1-core-module
description: "Use when: entering inflak P1 and routing the current state to the prompt-refinement planner before any widget or image generation."
---

# L1 Router — User-Driven Prompt Refinement

## Layer & Role

Read [the local root](../../SKILL.md) as documentation. Only L1 Router owns canonical state and emits `decision: end`. Reconstruct state initially and after every L2 routing failure, L3 validation failure, L4 return/failure and executor result/failure; downstream evidence is nonterminal and cannot resume another layer directly.

## Four Pathways

| Pathway | Control flow |
| --- | --- |
| Interaction Pathway | user/return → L1 → L2 Planner gap + selection → L3 Designer → L4 Renderer → L1 |
| Execution Pathway | user/return → L1 → L2 plan → execute/realize → L1; L2 directly invokes its executor without L3 or L4. |
| Host Agent Return | user → L1 → host agent; retain decision bypass or direct_answer. |
| Completion | user/return → L1 → Completion; only L1 emits decision: end from actual production and current acceptance evidence. |

This is P1's entry and control point. On every initial or return pass, reconstruct state and choose exactly one outcome: route to the P1 planner, Host Agent Return, or evidence-backed Completion. Never assume the previous planner or pathway still applies. Do not plan, draft, render or execute tools.

## Core IAI Model

This plugin enacts one fixed subgraph. Use it as the routing lens.

| Node | Meaning in this plugin |
| --- | --- |
| `H` Human | The end user who owns the image intent and selects which prompt parts to refine. |
| `T` Text Prompt | The drafted image-generation prompt — the single evolving object of every interaction. |
| `I` Interaction | The user selecting prompt keywords or segments to extend, steer, or restyle. |
| `Aug` Augmented Instruction | Not enacted as a separate node here; refinement folds directly back into `T`. |
| `A` Artifact | The generated image, produced once the prompt is confirmed. |
| `G` Generative AI | The model — both the prompt-refinement generation (main agent) and the image model (`generate_image`). |

Edge vocabulary this plugin actually enacts:

| Edge | Meaning |
| --- | --- |
| `H→T` | The user drafts or revises the image prompt. |
| `H→I` | The user provides selections through the widget. |
| `I→T` | The selection rewrites the prompt itself (extend / steer / restyle). |
| `T→G` | The confirmed prompt is passed to the image model. |
| `G→A` | The model produces the image artifact. |

## When IAI Is Needed

Route into the chain when the user wants to create or iterate on an image by refining its prompt — drafting a new prompt, extending or steering objects, or adjusting image style, then generating. Bypass the chain when the request is a pure factual question, explanation, or lookup with no prompt to co-create.

## Inputs

Gather from the conversation (no tool needed):

- `user_text`: latest user instruction or question.
- `prompt_draft`: the current working image prompt, if any (the primary state this plugin evolves).
- `prior_returns`: every widget return collected so far this session, in order — keyword-grid selections and prompt-review decisions. On a post-widget pass these are the freshest state and usually decide the next action.
- `last_image`: reference to the most recently generated image, if any.

Each pass re-reads this state. A return added since the last pass is the freshest state and decides how the planner acts next.

## Routing Table

Match the state against this table and pick the planner. The machine-readable source of truth is `registry/planners.json`.

| planner_id | load next skill | enter this planner when |
| --- | --- | --- |
| `image-prompt-refinement` | `l2-pN1-image-prompt-refinement` | The user wants to draft, iterate on, or refine an image-generation prompt — extend object detail, steer object attributes, or adjust image style — and ultimately generate the image once the prompt is confirmed. |

Tie-break: every co-creation request in this plugin routes to `image-prompt-refinement`; there is no other planner. If the request is not about an image prompt at all (a pure question or lookup), bypass the chain instead of routing.

## Procedure

1. Assemble the state above, including every prior widget return and the current `prompt_draft`.
2. Decide whether the request is co-creation. If it is a pure answer, explanation, or lookup with no prompt to build or refine, **bypass** the chain and answer directly.
3. If the current intent has already been fulfilled by actual production and current acceptance with no pending request, emit `decision: "end"`. Otherwise route to `image-prompt-refinement` with `route_to_planner`; planner-local gaps and execution readiness belong to L2.
4. Preserve registered state only; do not add an iai_model field or diagnose planner-local gaps here. Apply returned edits to prompt_draft, retaining source/history; changed text invalidates prior acceptance. Keywords remain returned evidence for L2 preparation, not an automatically rewritten prompt.
5. Hand off by loading `l2-pN1-image-prompt-refinement`. On the next return — a widget return or an image result — re-enter here and route again from scratch.

## Output (core_handoff)

```json
{
  "handoff_type": "core_handoff",
  "decision": "route_to_planner",
  "selected_planner": "image-prompt-refinement",
  "confidence": 0.0,
  "matched_triggers": [],
  "state_snapshot": {}
}
```

## Must

- Choose a fresh routed pass, Host Agent Return or justified Completion from current evidence.
- Preserve `prior_returns` and the current `prompt_draft` as first-class state on every pass.
- Re-enter and re-route from scratch on every return — a widget return or an image result.

## Must Not

- Do not plan, refine the prompt, render a widget, or call `generate_image` here — Layer 1 only routes.
- Do not decide whether the prompt is ready to generate; that is Layer 2's judgment.
- Do not skip to Layer 3 or Layer 4.

## Stop / Continue / Escape

- **Continue** to Layer 2 only when routing is still needed; every result/failure first returns here for a fresh pathway decision.
- **Stop** only by emitting `decision: "end"` after actual confirmed-prompt production and current acceptance with no unresolved action. Silence, timeout or a prompt-only approval is not image production or acceptance.
- **Escape** only when the request is too ambiguous to know whether an image prompt is even intended; ask one concise clarifying question.

## Next

- **Route:** load `l2-pN1-image-prompt-refinement`. L2 diagnoses a gap for L3 Designer or directly invokes its instruction-ready executor; all results/failures return here.
- **Bypass:** if the request is not co-creation, answer directly without loading another layer.
- **Completion:** emit evidence-backed `decision: "end"` without loading L2–L4.
