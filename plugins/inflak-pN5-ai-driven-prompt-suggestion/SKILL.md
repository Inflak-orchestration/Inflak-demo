---
name: inflak-pN5-ai-driven-prompt-suggestion
description: "Use when: exploring distinct narrative directions, focusing writer-owned choices, and generating from a confirmed writing prompt."
---

# inflak P5 - AI-Driven Prompt Suggestion

P5 helps a writer move from a seed idea to a confirmed writing prompt. It does not begin by drafting the artifact: GenAI first proposes distinct, actionable narrative directions, the writer selects or combines them, and later passes focus the chosen direction into a new `Text Prompt`.

## IAI Binding

| Node | P5 binding |
| --- | --- |
| `H` | The writer who supplies an initial idea, chooses directions, and adds constraints. |
| `T` | The seed prompt and, after confirmation, the focused writing prompt. |
| `I` | Direction selection and focused creative decisions. |
| `Aug` | The internally compiled instruction assembled from the confirmed prompt and constraints. |
| `G` | Copilot SDK's main model, which suggests directions and later writes the requested artifact. |
| `A` | The generated writing artifact. |

The exploration path is `H -> T -> G -> I -> T`. Once the writer confirms the focused prompt, the generation path is `T -> Aug -> G -> A`.

## Four Pathways and Ownership

| Pathway | Control flow |
| --- | --- |
| Interaction Pathway | user/return → L1 Router → L2 Planner gap + selection → L3 Designer → L4 Renderer → L1 |
| Execution Pathway | user/return → L1 → L2 plan → execute/realize → L1; L2 directly invokes the active main_model without L3 or L4. |
| Host Agent Return | user → L1 → host agent; retain decision bypass or direct_answer. |
| Completion | user/return → L1 → Completion; only L1 emits decision: end. |

L1 owns canonical state. L2 assesses every registered gap as open/resolved/not applicable with actual evidence, selects one next gap by dependencies and one eligible widget. L3 only validates/designs that selected interaction; L4 implements it. Silence is not delegation. Bounded direction preparation is not final writing: it returns to L1 with author choices still open. Preserve actual seed → distinct proposals → writer adoption → focused prompt confirmation dependencies, not a mechanical list of required facets.

Every L2 routing failure, L3 validation failure, renderer return/failure and execution result/failure immediately re-enters `l1-pN5-core-module`. Keep assessment in existing reason/purpose fields and retain stable IDs/entry policy without new aliases. Local L3 handoffs and L4 Inputs are self-contained, with no runtime main/authoring contract load.

## Brainstorming Rules

- Generate 4 to 6 meaningfully different narrative strategies, not paraphrases of the same idea.
- A direction includes a title, logline, narrative lens, proposed form or structure, emotional tone, creative hook, and tradeoff.
- Resolve one material creative gap per pass. Do not turn brainstorming into a long questionnaire.
- Preserve user-selected material verbatim where possible. Model suggestions remain optional until selected.
- The confirmed prompt is the user-owned `T`; `Aug` may compile it internally but is not a separate interaction target.

## Tools

- `render_html_widget` is called only by Layer 4 for P5 widgets.
- Final writing uses the main model directly after the writer confirms the focused prompt; no task tool is required.

## Stop / Continue / Escape

- **Continue:** every widget return re-enters Layer 1, which routes from current brainstorming state.
- **Stop:** only L1 emits `decision: end` from the actual writing artifact, current acceptance evidence and no unresolved request.
- **Escape:** if the writer dismisses a widget or lacks a usable seed, preserve existing text and offer a concise direct-text alternative.
