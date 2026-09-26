---
name: inflak-pN3-interaction-as-part-of-instruction
description: "Use when: generating a new image grounded by a user-drawn color-to-object layout sketch."
---

# inflak P3 - Interaction as Part of Instruction

P3 is an independent inflak plugin for generating a new image from a text prompt plus a user-authored layout sketch. It is for requests where the placement, scale, overlap, or relative position of objects materially affects the result. Each drawing color represents a concrete object type, for example `red = bed`, `green = window`, and `blue = sofa`; a legend makes the sketch interpretable rather than merely decorative.

## IAI Model

| Node | P3 binding |
| --- | --- |
| `H` | The user who describes the image and draws its desired object arrangement. |
| `T` | The text prompt describing the requested image, objects, setting, and style. |
| `I` | Canvas actions: selecting a color, binding it to an object, drawing strokes, and confirming the compiled layout. |
| `Aug` | The compiled generation brief: prompt, color-to-object legend, normalized stroke layout, inferred spatial constraints, and output settings. |
| `A` | The exported sketch PNG, transparent full-canvas mask, and later the generated image candidate. |
| `G` | The image model called through `edit_image` with the sketch as its source image. |

The active path is `H -> T`, `H -> I -> A`, then `T + A -> Aug -> G -> A'`. The sketch is both a visual source for the image model and a structured description of where each user-named object belongs.

## Four Pathways and Ownership

| Pathway | Control flow |
| --- | --- |
| Interaction Pathway | user/return → L1 Router → L2 Planner gap + selection → L3 Designer → L4 Renderer → L1 |
| Execution Pathway | user/return → L1 → L2 plan → execute/realize → L1; L2 directly invokes registered edit_image without L3 or L4. |
| Host Agent Return | user → L1 → host agent; retain decision bypass or direct_answer. |
| Completion | user/return → L1 → Completion; only L1 emits decision: end. |

L1 owns canonical state. L2 assesses every registered gap as open/resolved/not applicable from current evidence, chooses one next gap by real dependencies, and selects one eligible registry entry. L3 only validates and designs the exact selected interaction; L4 implements it. Silence is not delegation; missing source/intent cannot be fabricated. Keep diagnosis in existing reason/purpose fields, not new mandatory state. Preserve actual sketch/legend → compiled-brief confirmation → generation → actual-candidate review dependencies.

Every L2 routing failure, L3 validation failure, renderer return/failure and executor result/failure immediately re-enters `l1-pN3-core-module`. Never jump from a tool result to review. Only L1 may end from actual production and acceptance evidence. Local L3 handoffs and L4 Inputs are self-contained, with no runtime main/authoring read. Preserve stable IDs and entry policy; add no aliases.

## Sketch-Guided Generation

The sketch pad exports two same-sized PNG artifacts:

- `sketch_ref`: visible colored strokes used as the source image. Each color is bound to a required `object_label`.
- `full_canvas_mask_ref`: an entirely transparent PNG. It makes the existing `edit_image` tool regenerate the complete canvas while still receiving the sketch as visual grounding.

The Layer 2 execution instruction must use the sketch `fileId` as `image_file_id`, the transparent mask `fileId` as `mask_file_id`, and a complete compiled prompt. This places the visible sketch and textual brief in the same image-model request without introducing a new provider-specific tool.

## Tools

- `render_html_widget`: Layer 4 only; renders the sketch, confirmation, and candidate-review widgets in a sandboxed iframe.
- `edit_image`: L2 Planner directly invokes it after instruction_ready for confirmed full-canvas sketch-guided generation; return actual output or failure to L1.

## Registries

`registry/planners.json`, `registry/widgets.json`, and `registry/tools.json` contain P3's machine-readable planner, widget, and tool metadata. P3 does not add frontend JavaScript, CSS, or widget templates; Layer 4 generates the isolated widget implementation from the semantic contract.
