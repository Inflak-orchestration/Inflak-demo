---
name: l3-pN4-inpaint-region-editor
description: "Use when: P4 selects inpaint-region-editor to mark an actual source image and describe a local change."
---

# L3 Designer — Inpaint Region Editor

## Layer & Role

Design only `inpaint-region-editor` for `artifact-inpaint`, `artifact_region_gap` or `inpaint_intent_gap`, with `mark_region_and_describe_inpaint`. L3 Designer collects scope and text in one grounded interaction, preserving L2's single diagnosed edge. It never invents a source image, selects a different widget, renders, uploads or calls `edit_image`.

Only Interaction Pathway enters L3: L1 → L2 gap + selection → L3 Designer → L4 Renderer → L1. Execution Pathway directly invokes the selected executor from L2 without L3/L4. Host Agent Return and Completion stay with L1 and do not enter this skill.

## Inputs

Read L2 `planner_id`, `selected_widget_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `expected_return`, `return_to`, and `display_context`. Resolve local registry and actual canvas/upload availability. Require `image_ref` with actual source identity, dimensions and current revision context; consume supplied prompt and prior `edit_state` only for that same source. Missing source is an indispensable evidence failure.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Identify exactly where to repaint and the intended local result. |
| Presented information | Prioritize source image, visible scope, current mode, prompt and export status. |
| Supported interaction | Choose box or brush, draw/revise local scope, and edit the local prompt. |
| Feedback and constraints | Distinguish active/inactive scope; show source-bound marks and upload errors. |
| Submission and return | Serialize one active scope plus real source/mask references and editable history. |
| Presentation intent | An image-led editing stage with co-visible marks and local intent, not a text-only form. |

## Essential Constraints

- Validate exact ID, skill/path, planner, gap, goal, edge, return coverage, artifact support, state target and runtime. Preserve `inpaint_region_editor`, `conversation_widget`, modality and capabilities.
- Preserve `chain_id` and binding `reason`, source/edge/target unchanged. Edge source must occur in `source_nodes`; `I→A` targets/state-updates `A`, whereas `I→Aug` or `A→Aug` targets `Aug`. Do not reproduce the old I→A/target Aug mismatch.
- Return exactly `mode`, `image_ref`, `regions`, `mask_ref`, `edit_prompt`, `freeform_note`, `edit_state`. Text fields remain strings and scope/state remain their declared arrays/objects; echo actual `image_ref` with source `fileId`.
- Box mode returns positive normalized `{id,x,y,width,height}` rectangles bounded by 0..1 and empty mask semantics. Brush mode returns empty regions and a real uploaded source-sized RGBA PNG. Transparent pixels mean edit; opaque pixels preserve. Never activate boxes and brush simultaneously or silently widen scope.
- Preserve source aspect, coordinate mapping and revision. Explicit whole-canvas scope is required even for full-image intent. Nonempty `edit_prompt` describes the selected local change and preserves unselected content.
- Keep the interactive stage at the source image's exact aspect ratio with no letterboxed coordinate area. Map pointer coordinates against the rendered image bounds, show a live rectangle throughout box drawing, capture only one active pointer, and cancel without committing partial geometry. Moving an existing box must preserve its size and remain bounded to the image.
- Restore previous `edit_state` unchanged for the same source, including mode, boxes, brush_actions, brush settings, prompt and note. Source changes invalidate old geometry/masks; changes or reset invalidate stale exports. Never reuse an upload not representing current marks.
- Require actual completed upload only in brush mode. No fabricated fileId, preview or success; upload failure blocks submission rather than yielding partial scope.
- One primary submission confirms current scope/text, not a separate approval checkbox. No HTML, CSS, JavaScript, rendering or task calls.

## Output and Handoff

Use this complete local semantic definition; no success `handoff_type` or external document read:

- Identity: nonempty strings `selected_widget_id` (exact L2 selection), `widget_id` (instance identity), `widget_type` and `surface` (exact registry values), `planner_id` (owning L2), `purpose` (contextual), and unchanged `interaction_goal`.
- `iai`: copy L2's `chain_id`, `gap_type`, and binding `reason`, `maps_to_edge`, `source_nodes`, `target_node` unchanged; require a named chain and meaningful reason, edge source in `source_nodes`, and destination equal to `target_node` and allowed `state_update_target`. Include a deterministic `merge_strategy` for L1 and `next_planner_action: "re-enter Layer 1"`.
- `display`: grounded task values, source references, current values, and unresolved status; no invented evidence, defaults, uploads, previews, or outcomes.
- `controls`: array of records with `id`, `kind`, `label`, `purpose`, `required`, `return_keys`, `constraints`; IDs are unique/nonempty, kinds supported, labels/purposes nonempty, `required` boolean, and `return_keys` a nonempty list of declared return keys. State applicable limits, types, and source/edit rules in `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`, a nonempty `content` array of records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`); every source resolves. Include `interaction` with nonempty `actions`/`feedback` lists and `submission` (nonempty `label`, nonempty `preconditions`, `return_mapping`), plus nonempty semantic `appearance` and a nonempty `signature_features` list describing relevant behavior, not implementation or invented steps.
- `expected_return`: deterministic object with exactly L2's keys and types; `presentation.profile.interaction.submission.return_mapping` has exactly the same keys, each specifying its actual source and serialization. Preserve declared optional/empty semantics; derived returns need mappings, not artificial controls.
- `widget_requirements`: four nonempty string arrays, `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`; state minimal meaningful obligations consistent with the profile, not additional interaction gates.
- `safety`: `allow_html: false`, `allow_script: false`. Optional `runtime` declares only available approved capabilities and version-pinned libraries; optional `reference_assets` are plugin-relative design-time references and extracted principles only, never runtime assets.

Check source binding, geometry, mask meaning, edit history and exact mappings; load `l4-pN4-widget-renderer`. On invalid selection or missing indispensable evidence/capability, return `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, a nonempty deterministic `validation_errors` array identifying failed checks, and `return_to: l1-pN4-core-module`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 Router merges canonical state and emits `decision: end`. Every widget return/failure re-enters `l1-pN4-core-module`; submitted scope is nonterminal, not an edited image.
