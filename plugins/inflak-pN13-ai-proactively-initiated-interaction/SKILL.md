---
name: inflak-pN13-ai-proactively-initiated-interaction
description: "Use when: infer any user intent, offer grounded conversational next-action choices, and implement the user's confirmed recommendation."
---

# inflak P13 — AI-Proactively-Initiated Interaction

P13 serves any user intent, not an image-edit task family. The physical plugin directory and L2 path retain their image-edit spelling solely for compatibility. The manifest identity remains `inflak-pN13-ai-proactively-initiated-interaction`. This root is documentation read by the sole compatibility entry `l1-pN13-core-module`, not another discovered alias.

## Four Pathways and Ownership

| Pathway | Control flow |
| --- | --- |
| Interaction Pathway | user/return → L1 → L2 gap + selection → L3 interaction design → L4 render → L1 |
| Execution Pathway | user/return → L1 → L2 plan → execute/realize → L1; L2 directly invokes the active main model, without L3, L4, or an executor skill. |
| Host Agent Return | user → L1 → host agent for an out-of-scope direct answer; `decision: bypass`. |
| Completion | user/return → L1 → Completion; only L1 emits `decision: end`. |

L1 reconstructs and merges canonical state. L2 binds all six IAI nodes, reasons about intent, assesses every registered gap with evidence, selects one next gap by dependencies, or executes one ready main-model instruction. L3 validates the exact selected entry and designs a complete local semantic profile. `l4-pN13-widget-renderer` validates and implements that profile. Every widget/executor result, dismissal, routing failure, validation failure, and renderer failure re-enters `l1-pN13-core-module` before further action.

## Domain Policy

- Separate explicit observations from inferred goals; private ranking includes evidence, uncertainty, feasibility, tradeoffs and reversibility.
- Offer 2–5 grounded, materially distinct conversational possibilities (`recommendation_id`, `label`, `next_action`) and optional freeform intention. Do not display a diagnostic inspector, confidence score or ranking dossier. Low confidence warrants one discriminating question.
- A recommendation is not authorization. Confirm selection from actual user evidence, then retain the chosen recommendation and resolve material implementation needs before execution. Do not silently switch plugins or favor images/tools.
- The registered implementation interaction collects actual parameters, editable content, grounded selection, review or spatial evidence needed by that confirmed recommendation. It is not a mandatory extra confirmation and does not execute the task.
- Assess each registered category as `open`, `resolved`, or `not applicable`, with evidence in `iai_binding.reason` or `execution_instruction.purpose`. Silence is not delegation. Reopen settled decisions only when relevant evidence changes.
- `instruction_ready` permits evidence-backed execution or bounded prerequisite synthesis that returns to L1 with unresolved choices still open. It never authorizes final work while a material user choice remains open.
- The active main model executes the confirmed instruction within actual available capabilities and consent. No task tool is registered here; do not fabricate tool bindings, artifact mutations, uploads, previews or successful results. Unavailable capabilities return a truthful blocked result to L1.
- Selection and implementation returns are nonterminal. Only L1 may complete after actual execution evidence or explicit dismissal.

## Registries and Discovery

The three local registries are authoritative. `p13-intention-basic-widget` presents choices; `p13-implementation-widget` gathers task-grounded implementation input. Neither an unregistered widget nor a same-named skill from another plugin is callable through this plugin. Use only the exact registered local paths.

Both P13 L3 contracts and L4 Inputs are self-contained; no external recipe or main skill read is required. The implementation designer retains each registered mode's domain constraints locally.

## Next

Load `l1-pN13-core-module` initially and after every downstream return. It resolves the selected planner through its exact local registry path; the compatibility filename does not change the generic business purpose.