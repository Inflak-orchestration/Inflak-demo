---
name: inflak-pN11-artifact-driven-prompt-enhancement
description: "Use when: grounding and enhancing an existing user prompt against a stable SVG artifact."
---

# P11 — Artifact-Driven Prompt Enhancement

Root documentation read by sole entry `l1-pN11-core-module`, not an additional workflow layer.

## Four-Layer Contract

L1 Router owns state/routing/Completion. L2 Planner assesses registered gaps, selects one next gap by dependencies and its eligible widget, or emits `instruction_ready` and loads exec-pN11-prompt-refinement to invoke its registered executor or `main_model`. L3 Designer validates the exact selection and designs semantic interactions only. L4 Renderer implements them on `artifact_canvas_widget`; host hit testing and placement remain authoritative. P11 widgets author instructions, never artifact patches.

## Four Pathways

| Pathway | Control flow |
| --- | --- |
| Interaction Pathway | user/return → L1 → L2 gap + registry selection → L3 semantic design → L4 render → L1 |
| Execution Pathway | user/return → L1 → L2 ready plan → exec-pN11-prompt-refinement (tool/main_model) → L1; no L3/L4 |
| Host Agent Return | user → L1 → host agent; `decision: bypass` or `direct_answer` |
| Completion | user/return → L1 → Completion; only L1 emits `decision: end` |

Every result, dismissal, routing/validation failure, executor error and revision conflict re-enters L1 before another action. No downstream return is completion.

## Domain Invariants

- Require exact original prompt and source `fileId`/revision. Keep named concepts, ambiguous references and action spans separate; never resolve pronouns by proximity.
- Ground targets in the inspected scene; preserve source spans, prompt-unit IDs, field provenance and interaction history.
- Each executable action requires target-bound approval of its concrete operation, typed parameters and object-valued constraints. Prefilling, viewing, editing, or aggregate review is not approval.
- After all action approvals, the Host Agent validates the confirmed enhancement directly, executes approved operations through shared Host tools and validates the resulting SVG. No additional aggregate prompt review or revision-acceptance widget.
- Semantic names are not manager operations. Compile only complete approved values, invoke one supported presentation/layout/structure family per pass and return to L1.
- Semantic add/replace/restyle may prepare one actual transparent session candidate per pass; deterministic text, transform, order and removal do not imply regeneration.
- Approval is not completion. Source/prompt changes invalidate dependent evidence; never replay stale operations or invent success.

## Registry and Handoffs

Local registries are authoritative. One `planner_handoff` carries either one selected gap with named chain/reason and exact returns, or an explicit ready executor/parameters/purpose. Each L3 contains its complete local eight-part output; L4 validates locally. No main skill or authoring contract is a runtime prerequisite.

No plugin-local runtime or export prerequisite is used. Shared SVG tools keep their actual Host registration and deterministic safety/revision checks. The L2 skill's [tool-use instructions](skills/exec-pN11-prompt-refinement/SKILL.md) describe semantic and authorization checks, not a callable executor layer.

## Next

Enter `l1-pN11-core-module` and re-enter after every downstream outcome. Only L1 can conclude after approved work produces a validated current artifact, or explicit dismissal.