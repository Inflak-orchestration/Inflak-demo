---
name: l3-pN3-semantic-sketch-pad
description: "Use when: P3 selects semantic-sketch-pad for object-layout drawing or sketch-layout-confirmation for its compiled brief."
---

# L3 Designer — Semantic Sketch and Layout Confirmation

## Layer & Role

Design L2's exact `semantic-sketch-pad` or `sketch-layout-confirmation` selection for `sketch-layout-image-generation`; never switch between them. The first collects real color-to-object spatial evidence, the second reviews that evidence and the compiled brief. L3 Designer neither compiles the brief nor renders, uploads, executes image work or diagnoses another gap.

Only Interaction Pathway enters L3: L1 → L2 gap + selection → L3 Designer → L4 Renderer → L1. Execution Pathway directly invokes the selected executor from L2 without L3/L4. Host Agent Return and Completion stay with L1 and do not enter this skill.

## Inputs

Read L2 `planner_id`, `selected_widget_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `expected_return`, `return_to`, and `display_context`; resolve local registry and actual drawing/export/upload capabilities. Consume text intent, dimensions/aspect, normalized strokes, legend and current source/export context. Confirmation requires the actual sketch reference, legend and compiled layout brief. Empty canvas is legitimate for initial drawing, not confirmation.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Externalize object placement, complete a used-color legend, or confirm the compiled spatial meaning, as selected. |
| Presented information | Prioritize canvas and marks with object-color labels; confirmation co-presents actual sketch and brief. |
| Supported interaction | Drawing supports pen, eraser, undo/redo, clear, brush width and object labels; confirmation supports accept/revise. |
| Feedback and constraints | Show active color/object, unlabeled used colors, source/export changes and upload status. |
| Submission and return | Drawing returns actual same-sized sketch/mask exports and geometry; confirmation returns only the declared decision fields. |
| Presentation intent | Drawing-led workspace or sketch-led review, never a text-only layout substitute. |

## Essential Constraints

- Validate exact ID, skill/path, planner, gap, goal, atomic edge, return coverage, artifact support, state target and actual capabilities. Preserve each entry's type, surface and modality.
- Preserve `chain_id`, binding `reason`, source/edge/target; require source membership and destination equal to `state_update_target`. Drawing targets `A`; legend/confirmation targets `Aug` when L2 selects `I→Aug`.
- `semantic-sketch-pad` uses `ground_image_layout_in_object_sketch` or `complete_color_object_legend` and returns exactly `sketch_ref`, `full_canvas_mask_ref` (real reference objects), `strokes` (array), `canvas` (width/height), `color_semantics` (array), `freeform_note` (string).
- Every non-erased stroke retains normalized points and color. Each used color has nonempty `hex` and concrete `object_label`; role-only foreground/background/safe-area labels are insufficient. Preserve optional `scene_role`, `relations`, `priority`; they never replace the object name. Multiple same-color strokes mean the same object type unless user evidence distinguishes them.
- The sketch PNG contains visible colored strokes. The second PNG has identical dimensions and entirely transparent RGBA pixels for full-canvas regeneration. Require both actual completed uploads for this P3 return, never fabricated IDs or partial artifacts. Bind exports to current strokes/dimensions; invalidate after drawing/reset or source changes.
- `sketch-layout-confirmation` uses exact goal `confirm_sketch_layout_brief` and returns `decision` (accept/revise, retaining dismiss only if declared), `revision_request`, `freeform_note`. Show actual sketch, legend, compiled spatial constraints and output settings; revise needs a nonempty request. Do not modify strokes in confirmation.
- One primary submission per widget; explicit brief confirmation remains a separate domain interaction, never an approval checkbox. Preserve dimensions, aspect and normalized coordinate mapping. No HTML, CSS, JavaScript, rendering or task calls.

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

Check exact variant, object labels, coordinates, upload protocol and serialization; load `l4-pN3-widget-renderer`. On invalid selection or missing indispensable evidence/capability, return `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, a nonempty deterministic `validation_errors` array identifying failed checks, and `return_to: l1-pN3-core-module`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 Router merges state and emits `decision: end`. Every widget return/failure re-enters `l1-pN3-core-module`; drawing and brief acceptance are nonterminal, not generated images.
