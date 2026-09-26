---
name: inflak-pN10-artifact-to-multimodal-instruction
description: "Use when: artifact-first SVG Analyze needs grounded suggestions and confirmed multimodal instructions."
---

# P10 — Artifact to Multimodal Instruction

Root documentation read by sole callable entry `l1-pN10-core-module`. Analyze is artifact-first; no prompt is required. L1 owns state/routing/Completion, L2 planning and direct execution, L3 semantic design only, L4 rendering on persistent Artifact Canvas. Do not activate another canvas workspace.

## Four Pathways

| Pathway | Flow |
| --- | --- |
| Interaction Pathway | user/return → L1 → L2 gap + registry selection → L3 design → L4 render → L1 |
| Execution Pathway | user/return → L1 → L2 ready plan → direct registered executor or main_model → L1; no L3/L4 |
| Host Agent Return | user → L1 → host agent; bypass or direct_answer |
| Completion | user/return → L1 → Completion; only L1 emits decision: end |

Every result/failure re-enters L1 before another action.

## Domain Invariants

- Ground canonical source fileId/revision, stable objects and capabilities. Preserve suggestions, accepted/edited/rejected history, targets/relations, provenance and concrete typed values.
- Source remains read-only throughout instruction widgets. Suggestions/relations/operation edits are semantic values, not patches. Only final concrete Aug confirmation authorizes its displayed accepted/edited scope; no per-operation reconfirmation.
- L2 prepares a ready plan; the Host Agent loads `exec-pN10-svg-instruction` to validate confirmed Aug semantics and call shared Host tools for authorized candidate preparation/apply/validation as separate passes. Preserve source revision, exact approved instruction, suggestion/operation IDs and interaction binding; no export prerequisite.
- Typed presentation/layout/structure families use actual allowlists and schemas; semantic move/restyle names are not patch names. No invented IDs/values, mixed unsupported families, raw SVG/selectors or no-op completion.
- Semantic candidates require actual transparent current-session assets before use; deterministic changes never invoke image generation.
- Compare actual original source and validated resulting revision; only L1 assesses current acceptance and completion. Conflicts invalidate stale bindings, never replay stale patches.

## Registry and Handoffs

Local registries and [execution skill](skills/exec-pN10-svg-instruction/SKILL.md) retain actual APIs. References are noncallable, L3 output has complete local eight parts, L4 local Inputs and 266px host baseline. No main skill dependency or plugin-local runtime. Shared Host tools retain deterministic SVG safety and revision validation.

## Next

Enter `l1-pN10-core-module`; all downstream outcomes return there.
