---
name: l1-pN5-core-module
description: "Use when: entering inflak P5 to route an interactive writing-brainstorm request before a widget interaction or final writing generation."
---

# L1 Router — Writing Brainstorm

## Layer & Role

Read [the local root](../../SKILL.md) as documentation. Only L1 Router owns canonical state and emits `decision: end`. Reconstruct state initially and after every L2 routing failure, L3 validation failure, L4 return/failure and executor result/failure; downstream evidence is nonterminal.

## Four Pathways

| Pathway | Control flow |
| --- | --- |
| Interaction Pathway | user/return → L1 → L2 Planner gap + selection → L3 Designer → L4 Renderer → L1 |
| Execution Pathway | user/return → L1 → L2 plan → execute/realize → L1; L2 invokes its executor directly without L3 or L4. |
| Host Agent Return | user → L1 → host agent; retain decision bypass or direct_answer. |
| Completion | user/return → L1 → Completion; only L1 emits decision: end from actual production and current acceptance evidence. |

This is P5's entry and control point. On every initial or return pass, reconstruct state and choose routing to `writing-brainstorm`, Host Agent Return or justified Completion. Do not generate directions, diagnose gaps, render or write here.

## State

Preserve and re-read these values on every pass:

- `user_text`: latest instruction from the writer.
- `seed_prompt`: initial subject, creative goal, or writing brief.
- `brainstorm_candidates`: model-proposed narrative directions.
- `selected_directions`: the writer's selected or combined directions.
- `writing_constraints`: selected or stated format, audience, viewpoint, tone, scope, and length.
- `confirmed_prompt`: the focused user-owned prompt, if confirmed.
- `prior_returns`: all P5 widget returns in order.
- `generated_artifact`: most recent generated writing, if any.

The newest valid writer return is authoritative. Direction returns update selected_directions by stable IDs; facets update writing_constraints and writer text. Set confirmed_prompt only from explicit current confirmation. Seed, direction or prompt changes invalidate stale confirmation; more_ideas preserves prior choices as history without treating new suggestions as selected. Do not overwrite user text with an unselected suggestion.

## Routing Table

| planner_id | Load next skill | Route when |
| --- | --- | --- |
| `writing-brainstorm` | `l2-pN5-writing-brainstorm` | The user wants to explore, expand, compare, focus, or develop an idea for a written artifact such as a story, article, program, script, essay, or outline. |

Use Host Agent Return for factual questions and explanations outside co-creation. A request to produce writing still routes to L2 for evidence-backed execution, not host bypass. Emit decision end only when actual writing exists and current acceptance evidence shows no unresolved action.

## Output

```json
{
  "handoff_type": "core_handoff",
  "decision": "route_to_planner",
  "selected_planner": "writing-brainstorm",
  "confidence": 0.0,
  "matched_triggers": [],
  "state_snapshot": {
    "user_text": "",
    "seed_prompt": "",
    "brainstorm_candidates": [],
    "selected_directions": [],
    "writing_constraints": {},
    "confirmed_prompt": "",
    "prior_returns": [],
    "generated_artifact": ""
  }
}
```

## Must

- Re-evaluate the current state on every pass.
- Preserve both selected directions and freeform writer input.
- Load `l2-pN5-writing-brainstorm` after routing.

## Must Not

- Do not choose a narrative direction, ask a creative question, render a widget, compile the final prompt, or generate the artifact.

## Next

Load `l2-pN5-writing-brainstorm` when routed; every result/failure returns here before any further action or Completion.