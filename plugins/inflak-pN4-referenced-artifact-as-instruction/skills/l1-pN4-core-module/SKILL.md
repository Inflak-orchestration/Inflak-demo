---
name: l1-pN4-core-module
description: "Use when: entering inflak P4 and routing an artifact-grounded local image inpaint request before any widget or image edit."
---

# L1 Router — Artifact Inpaint

## Layer & Role

Read [the local root](../../SKILL.md) as documentation. Only L1 Router owns canonical state and emits `decision: end`. Reconstruct state initially and after every L2 routing failure, L3 validation failure, L4 return/failure and executor result/failure; downstream evidence never resumes a layer directly.

## Four Pathways

| Pathway | Control flow |
| --- | --- |
| Interaction Pathway | user/return → L1 → L2 Planner gap + selection → L3 Designer → L4 Renderer → L1 |
| Execution Pathway | user/return → L1 → L2 plan → execute/realize → L1; L2 invokes its executor directly without L3 or L4. |
| Host Agent Return | user → L1 → host agent; retain decision bypass or direct_answer. |
| Completion | user/return → L1 → Completion; only L1 emits decision: end from actual production and current acceptance evidence. |

This is P4's entry and control point. On every pass, including after every widget return and edit_image result, reconstruct state and choose routing to `artifact-inpaint`, Host Agent Return or justified Completion. Do not plan, render or call tools here.

## State

Preserve and re-read these values on every pass:

- `user_text`: current request.
- `source_artifact`: current image attachment, including `fileId`.
- `candidate_artifact`: most recent `edit_image` result, if any.
- `prior_returns`: region-editor and review-widget returns in order.
- `inpaint_state`: prior edit prompt, scope mode, normalized regions, mask ref, and accepted/rejected status.

The newest valid return is authoritative. Merge source-bound scope, mask and edit_state without losing source/revision identity. Source changes invalidate old masks/scope; edits invalidate old candidate acceptance. After retains the actual candidate, before retains the source, none keeps lineage and revision request for L2. Only current production/acceptance evidence with no unresolved action permits decision end.

## Routing Table

| planner_id | Skill | Route when |
| --- | --- | --- |
| `artifact-inpaint` | `l2-pN4-artifact-inpaint` | The user asks to locally add, remove, replace, repair, or repaint part or all of an existing image artifact. |

Route attached images and the most recent generated image as `source_artifact` when the user requests their local modification. Bypass factual questions, explanations, and lookups that do not alter an image.

## Output

```json
{
  "handoff_type": "core_handoff",
  "decision": "route_to_planner",
  "selected_planner": "artifact-inpaint",
  "confidence": 0.0,
  "matched_triggers": [],
  "state_snapshot": {
    "user_text": "",
    "source_artifact": {},
    "candidate_artifact": {},
    "prior_returns": []
  }
}
```

## Must

- Re-enter and route afresh after every widget return and tool result.
- Keep image attachment `fileId` values attached to their artifact state.
- Load `l2-pN4-artifact-inpaint` after routing.

## Must Not

- Do not decide scope mode, write an inpaint prompt, render a widget, or call `edit_image`.
- Do not send an artifact-less edit request directly to Layer 3.

## Next

Load `l2-pN4-artifact-inpaint` for a routed pass. Missing source or unavailable capability returns here for an honest escape, not invented evidence; only this Router decides Host Agent Return or Completion.
