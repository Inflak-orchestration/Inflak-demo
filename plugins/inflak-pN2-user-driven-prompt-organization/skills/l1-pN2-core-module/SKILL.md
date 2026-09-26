---
name: l1-pN2-core-module
description: "Use when: entering P2 or returning from its structure editor, instruction preview, or image generation."
---

# L1 Router — User-Driven Prompt Organization

## Layer & Role

Read [the local root](../../SKILL.md) as documentation. Only L1 Router owns canonical state and emits `decision: end`. Reconstruct state initially and after every L2 routing failure, L3 validation failure, L4 return/failure and executor result/failure. Downstream results are nonterminal, never direct continuation permission.

## Four Pathways

| Pathway | Control flow |
| --- | --- |
| Interaction Pathway | user/return → L1 → L2 Planner gap + selection → L3 Designer → L4 Renderer → L1 |
| Execution Pathway | user/return → L1 → L2 plan → execute/realize → L1; L2 invokes its executor directly without L3 or L4. |
| Host Agent Return | user → L1 → host agent; retain decision bypass or direct_answer. |
| Completion | user/return → L1 → Completion; only L1 emits decision: end from actual production and current acceptance evidence. |

Reconstruct state and choose routing, Host Agent Return or justified Completion. A routed pass loads exactly one P2 planner. Do not segment source, infer groups, perform planner-local structural diagnosis, compile an instruction, choose a widget, render or generate. L1 may validate return identity/status for canonical merging; detailed unit validation belongs to L2.

## State

- `user_text`: latest user-authored request.
- `source_text`: verbatim content being organized; default to `user_text` on first entry.
- `schema_version`: default `pN2-prompt-structure-v2`.
- `prompt_structure`: latest complete structure-editor return.
- `structure_submitted`: true only for a valid return with `submission_status: "confirmed"`.
- `compiled_instruction`: deterministic instruction compiled from the latest confirmed structure.
- `instruction_preview_status`: null, `confirmed`, or `revise`.
- `generated_artifacts` and `prior_returns`.

`source_text` is user-owned Text through `H→T`. The interface does not discard it when creating structure through `I→T`.

## Routing Table

| planner_id | Load next skill | Route when |
| --- | --- | --- |
| `visual-story-composition` | `l2-pN2-visual-story-composition` | The user wants to organize, validate, generate, or revise a visual instruction or multi-scene storyboard. |

Use Host Agent Return for unrelated factual requests. Emit `decision: end` only with an actual artifact generated from the current confirmed structure and confirmed preview and no unresolved request; submission alone is not Completion.

## Output

```json
{
  "handoff_type": "core_handoff",
  "decision": "route_to_planner",
  "selected_planner": "visual-story-composition",
  "state_snapshot": {
    "user_text": "",
    "source_text": "",
    "schema_version": "pN2-prompt-structure-v2",
    "prompt_structure": null,
    "structure_submitted": false,
    "compiled_instruction": null,
    "instruction_preview_status": null,
    "generated_artifacts": [],
    "prior_returns": []
  }
}
```

## Re-entry

- A valid editor return replaces `prompt_structure` and its returned `source_text` becomes current while prior text remains in history.
- Set `structure_submitted` only after validating the editor return envelope and explicit status; clear stale `compiled_instruction` and `instruction_preview_status` whenever the structure changes.
- A valid preview return sets `instruction_preview_status`. On `revise`, preserve the structure but set `structure_submitted` false so the editor reopens. On `confirmed`, preserve the exact reviewed `compiled_instruction` for execution.
- Append compact generation references to `generated_artifacts`.
- Always route returns through this layer.

## Next

Load `l2-pN2-visual-story-composition` only when routed; Host Agent Return and justified Completion load no downstream layer.