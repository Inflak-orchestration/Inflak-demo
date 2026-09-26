---
name: inflak-pN7-generative-prompt-control-widgets
description: "Use when: controlling image-prompt entities, priority, composition, preferences, exclusions and supported weights through source-anchored parameters."
---

# inflak P7 - Generative Prompt Control Widgets

P7 implements fine-grained image-prompt control inspired by PromptCharm. Unlike prompt iteration, its interactions do not select text for open-ended rewriting. GenAI first identifies controllable semantic units in an image prompt, then the user adjusts their intended visual effect with embedded controls. Each accepted control updates a structured control specification (`Aug`); a later, separate generation pass uses that confirmed `Aug` to render the image.

## IAI Binding

| IAI node | P7 binding |
| --- | --- |
| `H` | The user who supplies intent and adjusts image-prompt controls. |
| `T` | The current human-readable image prompt used to derive controllable units. |
| `I` | Inline prompt parameters derived from anchored entities, visual priority, composition, candidate preferences, exclusions, and attention weight. |
| `Aug` | A structured control specification that records confirmed adjustments for generation. |
| `G` | GenAI in one role per pass: control analysis for `T→G→I`, or separate image generation for `Aug→G→A`. |
| `A` | The generated image and optional user-reported mismatch feedback. |

The usual path is `H→T`, `T→G→I` for AI-generated controls, `I→Aug` for user control, then the separate generation path `Aug→G→A`. After an image, reported mismatch feedback re-enters Layer 1 and may open another `I→Aug` control gap; it does not add a new artifact-to-interaction edge.

## Four Pathways and Ownership

| Pathway | Control flow |
| --- | --- |
| Interaction Pathway | user/return → L1 Router → L2 Planner gap + selection → L3 Designer → L4 Renderer → L1 |
| Execution Pathway | user/return → L1 → L2 plan → execute/realize → L1; L2 directly invokes selected generate_image or bounded active-main-model preparation without L3 or L4. |
| Host Agent Return | user → L1 → host agent; retain decision bypass or direct_answer. |
| Completion | user/return → L1 → Completion; only L1 emits decision: end. |

L1 owns canonical state. L2 assesses every registered gap as open/resolved/not applicable with actual evidence, selects one next gap by dependencies and one eligible exact widget. L3 only validates/designs the selected semantic interaction; L4 implements its inline controls. Silence is not delegation. Bounded control/candidate preparation returns to L1 with user choices open; confirmed content precedes dependent roles/weights unless the user explicitly narrowed the task. Current compiled-prompt acceptance remains required before image generation.

Every L2 routing failure, L3 validation failure, renderer return/failure and executor result/failure immediately re-enters `l1-pN7-core-module`. Keep diagnosis in existing reason/purpose fields. Local L3/L4 rules are self-contained with no runtime main/authoring read. Preserve all six distinct P7 semantic widgets, stable IDs and entry policy; add no aliases.

## P7 Control Rules

- Treat `Aug`, not the raw prompt, as the source of truth for accepted controls. Preserve the original prompt and every accepted control return for provenance.
- Only expose controls for units that are both material to the image intent and understandable without model-internal knowledge.
- A numerical attention control expresses desired visual priority. Represent it with native weighted-prompt syntax only when the selected image provider supports it; otherwise represent it as clear semantic emphasis in the generation parameters.
- Express composition allocations through independent relative frame-share sliders, not a mandatory 100-percent budget. Preserve actual values without normalization or rebalancing; resolve conflicting scene intent through L1/L2 rather than inventing a fallback.
- Keep similar and dissimilar candidate choices separate. Dissimilar candidates become exclusions or avoided directions; they are never silently added to the positive prompt.
- `generate_image` is P7's only task tool. All prompt analysis and compilation are performed by the main model.

## Stop / Continue / Escape

- **Continue:** every return re-enters Layer 1 and lets Layer 2 select the next material control or prepare the next generation prompt preview.
- **Stop:** only L1 emits `decision: end` after an actual image result and current evidence of no unresolved request; a tool invocation alone is not production.
- **Escape:** on dismissal, retain the last accepted prompt and control specification, then offer direct prompt editing or a concise non-widget alternative.

## Registry

`registry/planners.json`, `registry/widgets.json`, and `registry/tools.json` are P7's machine-readable metadata. They are independent of P1 and name only P7 skills and P7 control primitives.