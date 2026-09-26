---
name: inflak-pN4-referenced-artifact-as-instruction
description: "Use when: locally inpainting an existing image through source-bound region marking and edit intent."
---

# inflak P4 - Referenced Artifact as Instruction

This independent inflak plugin specializes the four-layer IAI protocol for local image inpainting. The user interacts with an existing image artifact, marks the part to alter, describes the replacement, then reviews the generated result before accepting it.

## IAI Model

| Node | P4 binding |
| --- | --- |
| `H` | The user who owns the source image and editing intent. |
| `T` | The textual inpaint request: what should appear in the selected region. |
| `I` | Direct manipulation of the image: rectangular selection or a freehand brush mask. |
| `Aug` | The compiled edit instruction: source `fileId`, edit prompt, region boxes or mask `fileId`, and output settings. |
| `A` | The original image artifact and the generated edited candidate. |
| `G` | The image editing model called through `edit_image`. |

The active path is `H -> I -> A`, `H -> T`, then `A + T -> Aug -> G -> A'`. A local edit is not ready until both a source artifact and an explicit scope exist. The interaction object is the artifact itself, not a prompt span.

## Four Pathways and Ownership

| Pathway | Control flow |
| --- | --- |
| Interaction Pathway | user/return → L1 Router → L2 Planner gap + selection → L3 Designer → L4 Renderer → L1 |
| Execution Pathway | user/return → L1 → L2 plan → execute/realize → L1; L2 directly invokes registered edit_image without L3 or L4. |
| Host Agent Return | user → L1 → host agent; retain decision bypass or direct_answer. |
| Completion | user/return → L1 → Completion; only L1 emits decision: end. |

L1 owns canonical state. L2 assesses every registered category as open/resolved/not applicable, with actual evidence, then selects one next gap by dependencies and one eligible widget. L3 only validates/designs that interaction; L4 implements generated UI, retaining explicit complete-template fallback. Silence is not delegation. A missing source is a real blocker, never a generated replacement; keep diagnosis in existing reason/purpose fields.

Every L2 routing failure, L3 validation failure, L4 return/failure and executor result/failure immediately re-enters `l1-pN4-core-module`. Actual source/scope/prompt precede execution, and every new candidate requires fresh L1/L2/L3 review. Only L1 may end from actual production/acceptance evidence. Local L3/L4 contracts are self-contained without runtime main/authoring reads; keep stable IDs and entry policy, without new aliases.

## Scope Modes

The P4 region editor supports exactly one active scope mode per submission:

- **Box:** one or more normalized `{x, y, width, height}` rectangles. L2 passes them as `edit_image.regions` after L1 re-entry.
- **Brush:** a source-sized RGBA PNG uploaded through `window.uploadWidgetFile`. Transparent pixels are edit area and opaque pixels preserve. L2 passes its actual `fileId` as `edit_image.mask_file_id` after L1 re-entry.

Use box mode for compact or approximate targets. Use brush mode for irregular boundaries, silhouettes, overlaps, or when the user explicitly paints the edit area. A brush mask overrides boxes; never send both modes as active scope inputs. Full-image edits still require an explicit whole-canvas box or mask.

## Result Review

Every successful inpaint creates a candidate artifact and must be reviewed on the next pass. The review compares the source and candidate and returns one of:

- `after`: accept the edited artifact.
- `before`: retain the original artifact.
- `none` with `revision_request`: re-enter Layer 1 and plan another scoped edit.

## Tools

- `render_html_widget`: Layer 4 only; renders generated sandboxed implementations or an explicit template fallback.
- `edit_image`: L2 Planner directly invokes it after instruction_ready with actual source, one valid scope and nonempty inpaint prompt; every result/failure returns to L1.

## Registries

`registry/planners.json`, `registry/widgets.json`, and `registry/tools.json` are P4's machine-readable catalog. P4-specific templates live under `registry/templates/`; existing renderer, upload, and image-editing services are reused without a separate platform implementation.
