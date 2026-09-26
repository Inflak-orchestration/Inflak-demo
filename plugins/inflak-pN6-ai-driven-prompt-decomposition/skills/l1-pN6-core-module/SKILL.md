---
name: l1-pN6-core-module
description: "Use when: entering inflak P6 and routing a prompt-decomposition request before a conversation widget interaction or story generation."
---

# L1 Router — Prompt Decomposition

## Layer & Role

Read [the local root](../../SKILL.md) as documentation. Only L1 Router owns canonical state and emits `decision: end`. Reconstruct state initially and after every L2 routing failure, L3 validation failure, L4 return/failure and executor result/failure; downstream evidence is nonterminal.

## Four Pathways

| Pathway | Control flow |
| --- | --- |
| Interaction Pathway | user/return → L1 → L2 Planner gap + selection → L3 Designer → L4 Renderer → L1 |
| Execution Pathway | user/return → L1 → L2 plan → execute/realize → L1; L2 invokes its executor directly without L3 or L4. |
| Host Agent Return | user → L1 → host agent; retain decision bypass or direct_answer. |
| Completion | user/return → L1 → Completion; only L1 emits decision: end from actual production and current acceptance evidence. |

This is P6's entry and control point. On every initial or return pass, reconstruct state and choose routing to `prompt-decomposition`, Host Agent Return or justified Completion. Do not extract components, select a widget, render or write here.

## State

Preserve and re-read these values on every pass:

- `user_text`: latest instruction.
- `source_prompts`: prompt records `{id, text}` from the current turn and prior revisions.
- `prompt_components`: extracted, traceable intent, context, constraints, audience, process, and output requirements.
- `prompt_structure`: the latest prompt structure tree or cell map return.
- `augmented_instruction`: the latest Story Brief and its approval state, if one exists.
- `prior_returns`: all P6 widget returns in order.
- `generated_story`: most recent story candidate, if any.

The newest valid return is authoritative. Merge complete tree/cell structures and fragment_edits into prompt_structure/prompt_components without discarding source_prompt_ids or origin. Merge Story Brief sections and actual approval into augmented_instruction; source, structure or section edits invalidate prior approval. Return-to-structure preserves edits with approved false. Only an actual story from the current approved brief and no unresolved request permits decision end.

## Routing Table

| planner_id | Load next skill | Route when |
| --- | --- | --- |
| `prompt-decomposition` | `l2-pN6-prompt-decomposition` | The user wants to improve, expand, structure, or revise a prompt through editable fine-grained components. |

Bypass factual questions, explanations, and requests that do not improve or decompose a prompt.

## Output

```json
{
  "handoff_type": "core_handoff",
  "decision": "route_to_planner",
  "selected_planner": "prompt-decomposition",
  "confidence": 0.0,
  "matched_triggers": [],
  "state_snapshot": {
    "user_text": "",
    "source_prompts": [],
    "prompt_components": [],
    "prompt_structure": {},
    "augmented_instruction": {},
    "prior_returns": [],
    "generated_story": ""
  }
}
```

## Must

- Update the routing decision from the current state on every pass.
- Keep prompt and structure provenance first-class state.
- Load `l2-pN6-prompt-decomposition` after routing.

## Must Not

- Do not infer decomposition gaps, render a widget, compile `Aug`, or generate the story.

## Next

Load `l2-pN6-prompt-decomposition` when routed. Every downstream result/failure returns here; no direct continuation from a submitted structure or approved brief.