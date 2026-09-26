---
name: inflak-pN6-ai-driven-prompt-decomposition
description: "Use when: decomposing source prompts into traceable editable components and an approved Story Brief before story generation."
---

# inflak P6 - AI-Driven Prompt Decomposition

P6 uses GenAI to restructure one or more source prompts into fine-grained, user-owned components before generating a story. Components include characters, setting, plot events, relationships, tone, constraints, and ending direction. Every component preserves its `source_prompt_ids`, allowing the user to inspect and manipulate what the model inferred.

## IAI Binding

| Node | P6 binding |
| --- | --- |
| `H` | The author who supplies source prompts and edits their decomposition in a conversation widget. |
| `T` | The source prompts and their extracted prompt components. |
| `I` | A prompt structure tree or topical cell map used to inspect and reorganize components. |
| `Aug` | The author-approved Story Brief compiled from the chosen components and traceability. |
| `G` | Copilot SDK's main model in one role per pass: first decomposition, later separate story generation after approval. |
| `A` | The generated story artifact. |

The normal path is `H→T`, `T→G→I` for AI-driven decomposition, `I→T` for author organization or `I→Aug` for Story Brief review, then the separate execution path `Aug→G→A`. The decomposition pass gives `G` only the decomposition role; final story generation is a later atomic execution role after explicit brief approval.

## Four Pathways and Ownership

| Pathway | Control flow |
| --- | --- |
| Interaction Pathway | user/return → L1 Router → L2 Planner gap + selection → L3 Designer → L4 Renderer → L1 |
| Execution Pathway | user/return → L1 → L2 plan → execute/realize → L1; L2 directly invokes the active main_model without L3 or L4. |
| Host Agent Return | user → L1 → host agent; retain decision bypass or direct_answer. |
| Completion | user/return → L1 → Completion; only L1 emits decision: end. |

L1 owns canonical state. L2 assesses every registered category as open/resolved/not applicable from actual evidence, selects one next gap by dependencies and one eligible widget. L3 validates/designs only that selection; L4 implements. Silence is not delegation and missing sources cannot be fabricated. Bounded decomposition uses a distinct model role and returns to L1 before author organization; it never authorizes final story generation. Preserve the real organization → traceable brief → explicit current brief approval dependency; hierarchy and cells are alternative representations chosen by meaning, not consecutive mandatory stages.

Every L2 routing failure, L3 validation failure, renderer return/failure and executor result/failure immediately re-enters `l1-pN6-core-module`. Keep assessment in existing reason/purpose fields. Local L3/L4 contracts are self-contained without runtime main/authoring reads; keep stable IDs and entry policy, with no new aliases.

## Decomposition Widget

P6 uses one conversation widget per pass. `prompt_structure_tree` organizes components through editable containment and sibling order; `prompt_cell_map` groups related components into named topical cells without implying hierarchy or sequence. Both organization paths compile to a separately reviewed `story_brief_review` before story generation.

## Traceability Rules

- Every source prompt has a stable `id`.
- Every extracted component and derived structure/brief record preserves actual `source_prompt_ids`; user-created additions use truthful `origin: user` and may have empty source lists. Do not invent graph edges or sources.
- Layer 2 includes this provenance in `Aug`; it remains available in the widget structure and story artifact metadata.

## Tools

- `render_html_widget` is called only by Layer 4 for P6 decomposition widgets.
- Story generation is a no-tool execution path: after the user approves the Story Brief, the main model produces the story and returns to Layer 1.

## Stop / Continue / Escape

- **Continue:** any widget return re-enters L1, which routes again from the current structure and returns.
- **Stop:** only L1 emits `decision: end` from an actual story produced from the approved current brief and no unresolved request.
- **Escape:** when the user dismisses a widget or has not supplied enough material, preserve existing components and offer a direct text alternative.
