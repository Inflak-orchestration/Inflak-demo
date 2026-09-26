---
name: inflak-pN8-generative-artifact-control-widgets
description: "Use when: creating a layered SVG collage with prepared deterministic authoring options."
---

# P8 — Generative Artifact Control Widgets

Root documentation read by sole callable entry `l1-pN8-core-module`. L1 owns canonical state/routing, L2 plans and hands ready work to exec-pN8-collage-authoring, L3 designs semantic interaction only, L4 implements the selected widget. Persistent Artifact Canvas is active; never call `render_canvas_workspace`.

## Four Pathways

| Pathway | Flow |
| --- | --- |
| Interaction Pathway | user/return → L1 → L2 gap + registry selection → L3 design → L4 render → L1 |
| Execution Pathway | user/return → L1 → L2 ready plan → direct registered executor or main_model → L1; no L3/L4 |
| Host Agent Return | user → L1 → host agent; bypass or direct_answer |
| Completion | user/return → L1 → Completion; only L1 emits decision: end |

Every result/failure, widget return and host patch re-enters L1. No lower layer merges canonical state or concludes work.

## Domain Invariants

- Canonical `svg-document` with `scene_kind: collage`; stable object IDs shared by SVG and scene. Independent transparent raster cutouts and editable text, never flattened bitmap.
- Actual transparent pixels required for every inserted/replaced SVG raster. Generation requires `background: transparent`, `require_transparent_background: true`; reject opaque output before binding/composition.
- Default rich collage: 4–6 cutouts and 3–5 text objects with coherent theme, hierarchy, overlap and negative space. Explicit minimal/sparse/named-only intent overrides creative defaults; two-cutout compiler floor is not the default target.
- Before composition/review, complete `authoring_bundle`: 2–4 coherent presets, 1–3 actual distinct replacement candidates per replaceable object, relevant copy/typography and prepared addable elements. Complete bundle travels inside `compose_svg_collage.scene`; host displays authoring options immediately.
- Candidate `fileId` exists in current session, differs from current asset and is unique per gallery. Preserve `kind`, `source_tool`, source/target identity, label/rationale, stable new IDs and default transforms.
- Registry capabilities select provider preparation and result bindings before tools. L2 hands its ready plan to the discoverable [execution skill](skills/exec-pN8-collage-authoring/SKILL.md), parallel to the L3 interaction branch.
- Widgets consume prepared options only. No on-click generation/fetch. Explicit new request beyond bundle is a separate generation task, never implicit option behavior.
- Deterministic operations remain `set_transform`, `set_order`, `set_object_style`, `add_cutout`, `remove_object`, `add_text`, `update_text`, `replace_cutout_asset`, `set_canvas_style`; atomic presets preserve order and revision.
- Host owns selection, handles, reversible preview and commit. Only explicit Apply/Add/Remove authorizes corresponding typed operations. Never replay host-committed patches; stale revisions return to planning. Compare actual changed revision before valid acceptance.

## Registry and Handoffs

Local planner/widget/tool/capability registries remain authoritative; no main skill or external schema is a runtime prerequisite. Each L3 defines all eight semantic parts locally; each L4 validates local Inputs and 266px host UI. MCP and host tool names/parameter schemas remain unchanged. Native vector styling stays native and never triggers raster generation.

## Next

Enter `l1-pN8-core-module`; all downstream outcomes return there. Only L1 completes after current valid acceptance or records explicit cancellation.
