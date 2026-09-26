---
name: l1-pN3-core-module
description: "Use when: entering inflak P3 to route a sketch-grounded image-layout request before any widget or image generation."
---

# L1 Router — Sketch Layout

## Layer & Role

Read [the local root](../../SKILL.md) as documentation. Only L1 Router owns canonical state and emits `decision: end`. Reconstruct state initially and after every L2 routing failure, L3 validation failure, L4 return/failure and executor result/failure; all downstream results are nonterminal.

## Four Pathways

| Pathway | Control flow |
| --- | --- |
| Interaction Pathway | user/return → L1 → L2 Planner gap + selection → L3 Designer → L4 Renderer → L1 |
| Execution Pathway | user/return → L1 → L2 plan → execute/realize → L1; L2 invokes its executor directly without L3 or L4. |
| Host Agent Return | user → L1 → host agent; retain decision bypass or direct_answer. |
| Completion | user/return → L1 → Completion; only L1 emits decision: end from actual production and current acceptance evidence. |

This is P3's entry and control point. On every pass, including after every widget return and edit_image result, reconstruct current state and choose routing to `sketch-layout-image-generation`, Host Agent Return or justified Completion. Do not diagnose gaps, render, compile prompts or call tools here.

## State

Preserve and re-read these values on every pass:

- `user_text`: current image request.
- `sketch_ref`: exported visible sketch attachment, including `fileId`.
- `full_canvas_mask_ref`: same-sized transparent mask attachment, including `fileId`.
- `sketch_semantics`: returned `color_semantics`, strokes, canvas dimensions, and note.
- `compiled_brief`: current prompt plus object-layout constraints.
- `candidate_artifact`: most recent `edit_image` result, if any.
- `prior_returns`: sketch, confirmation, and review returns in order.
- `generation_state`: confirmation and acceptance status.

The newest valid return is authoritative. Merge sketch exports and semantics together, invalidating old compiled-brief confirmation when marks, legend or intent changes. A review with accepted_version after retains the actual candidate; before retains the actual displayed prior artifact, never mislabels a source sketch as a generated image. None preserves lineage and routes the revision through L2. Only current production and acceptance evidence with no unresolved action permits decision end.

## Routing Table

| planner_id | Skill | Route when |
| --- | --- | --- |
| `sketch-layout-image-generation` | `l2-pN3-sketch-layout-planner` | The user requests a new image, illustration, interior, scene, diagram-like render, or other visual artifact whose object arrangement can be completed with a prompt and, when needed, a sketch. |

Route here for explicit layout terms such as layout, arrangement, composition, position, left/right, foreground/background, overlap, framing, or safe area. Also route a new-image request that later receives P3 sketch or confirmation state. Bypass factual questions, explanations, and lookups with no image artifact to create.

## Output

```json
{
  "handoff_type": "core_handoff",
  "decision": "route_to_planner",
  "selected_planner": "sketch-layout-image-generation",
  "confidence": 0.0,
  "matched_triggers": [],
  "state_snapshot": {
    "user_text": "",
    "sketch_ref": {},
    "full_canvas_mask_ref": {},
    "sketch_semantics": {},
    "compiled_brief": {},
    "candidate_artifact": {},
    "prior_returns": [],
    "generation_state": {}
  }
}
```

## Must

- Re-enter and route afresh after every widget return and `edit_image` result.
- Preserve attachment `fileId` values and the color-to-object legend as state.
- Load `l2-pN3-sketch-layout-planner` after routing.

## Must Not

- Do not decide whether a sketch is needed, classify spatial risk, or create a layout brief.
- Do not render a widget, compile generation parameters, or call `edit_image`.

## Next

Route to `l2-pN3-sketch-layout-planner`, choose Host Agent Return, or emit justified Completion. Every downstream result/failure returns here; never resume the previous layer automatically.
