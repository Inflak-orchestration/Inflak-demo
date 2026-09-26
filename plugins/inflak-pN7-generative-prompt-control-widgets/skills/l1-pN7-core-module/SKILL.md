---
name: l1-pN7-core-module
description: "Use when: entering P7 or resuming after a P7 widget return or image generation result. Route image-prompt-control work to its planner."
---

# L1 Router — Image Prompt Control

## Layer & Role

Read [the local root](../../SKILL.md) as documentation. Only L1 Router owns canonical state and emits `decision: end`. Reconstruct state initially and after every L2 routing failure, L3 validation failure, L4 return/failure and executor result/failure; downstream evidence is nonterminal.

## Four Pathways

| Pathway | Control flow |
| --- | --- |
| Interaction Pathway | user/return → L1 → L2 Planner gap + selection → L3 Designer → L4 Renderer → L1 |
| Execution Pathway | user/return → L1 → L2 plan → execute/realize → L1; L2 invokes its executor directly without L3 or L4. |
| Host Agent Return | user → L1 → host agent; retain decision bypass or direct_answer. |
| Completion | user/return → L1 → Completion; only L1 emits decision: end from actual production and current acceptance evidence. |

On every initial or return pass, reconstruct P7 state and choose routing to `image-prompt-control`, Host Agent Return or justified Completion. L1 owns that decision and canonical merging, not control analysis, prompt compilation, widget selection, rendering or generation.

## State

- `user_text`: current user request.
- `source_prompt`: original prompt, retained verbatim.
- `current_prompt`: most recent compiled prompt.
- `control_spec`: accepted P7 controls for entities, priority, composition, attention, candidate preferences, styles, and exclusions.
- `provider_capabilities`: whether native weighted prompt syntax or attention evidence is available.
- `prior_returns`: ordered P7 widget returns.
- `last_image`: last generated artifact reference.
- `image_feedback`: user-reported mismatch with the last image.

Merge parameter_values by stable ID into control_spec.inline_parameters and the selected existing category: entities/exclusions, subject_hierarchy, composition, attention or candidate_preferences. Preserve changed_parameter_ids provenance and other accepted values. Compiled_prompt is a review preview, not hidden Aug→T conversion. Source/control changes invalidate acceptance; raw prompt edits remain text for a fresh L2 analysis. Review accept applies only to the current displayed version; reopen_control preserves work and records one category. Only actual output and current acceptance/no-pending-action evidence permits decision end.

## Routing Table

| planner_id | Load next skill | Route when |
| --- | --- | --- |
| `image-prompt-control` | `l2-pN7-image-prompt-control` | The user requests an image, revises an image prompt, controls objects or their prominence, sets composition, selects visual directions, excludes content, or responds to a generated image. |

Bypass pure questions, document lookup, and requests unrelated to image-prompt co-creation.

## Output

```json
{
  "handoff_type": "core_handoff",
  "decision": "route_to_planner",
  "selected_planner": "image-prompt-control",
  "state_snapshot": {
    "user_text": "",
    "source_prompt": "",
    "current_prompt": "",
    "control_spec": {},
    "provider_capabilities": {},
    "prior_returns": [],
    "last_image": null,
    "image_feedback": null
  }
}
```

## Next

Load `l2-pN7-image-prompt-control` when routed. Never identify controls, compile, render or execute here; every downstream return/failure re-enters this Router before further action.