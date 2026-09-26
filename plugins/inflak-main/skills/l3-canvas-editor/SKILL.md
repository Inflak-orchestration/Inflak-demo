---
name: l3-canvas-editor
description: "Use when: Layer 2 selected canvas-editor for image layout or inpaint regions."
---

# L3 Designer — Canvas Editor

## Layer & Role

L3 Designer handles interaction design only on Interaction Pathway: L2 gap + selection → L3 interaction design → L4 render → L1. Design L2's exact `selected_widget_id: canvas-editor` as a grounded spatial widget profile.
Specialize the supplied goal and task context; never diagnose another gap or select another widget.
L3 designs drawing and spatial-evidence semantics; L4 implements the canvas and required uploads.

## Inputs

- Read `planner_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `expected_return`, and `return_to` from L2.
- Resolve the exact widget registry entry, planner eligibility, and actual drawing/export/upload capabilities.
- Read spatial intent, material content and placement requirements, canvas dimensions, aspect ratio, and coordinate conventions.
- For source editing, require the actual source reference, dimensions, revision, and applicable mask or region protocol.
- Derive supported tools, labels, grouping, and geometric constraints from intent and evidence; L2 need not predesign controls.
- Distinguish design choices from missing source evidence or protocol semantics that cannot be guessed.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Explain the spatial evidence the user supplies for the existing goal, without choosing a target or executing an edit. |
| Presented information | Show the relevant source or layout context, required content, coordinate frame, mask meaning, and upload status. |
| Supported interaction | Select the needed drawing, erasing, region, mask, crop, or reset operations; provide true spatial input when diagnosed. |
| Feedback and constraints | Show marks and bounded geometry, explain mask semantics, and identify stale evidence, source changes, or upload failures. |
| Submission and return | Map current spatial evidence and required real uploads to exactly L2's return keys with source/revision binding. |
| Presentation intent | Prioritize source and marks; make tool state, geometric meaning, and submission readiness accessible. |

## Essential Constraints

- Validate exact ID, skill/path, planner, gap, goal, edge, return coverage, artifact support, state target, and runtime availability.
- Keep registered type, surface, modality, and capability boundaries unchanged; do not broaden eligibility.
- Preserve `chain_id` and `iai_binding.reason` unchanged in `iai.chain_id` and `iai.reason`.
- Preserve `source_nodes`, `maps_to_edge`, and `target_node` unchanged; pending drawing is not existing spatial evidence.
- Require the edge source in `source_nodes` and its destination in `target_node`; `state_update_target` identifies that destination.
- A diagnosed `image_layout_gap` with `draw_image_layout` requires a real drawable canvas, never a text form or generated substitute.
- Artifact labels alone never trigger a canvas; keep L2's diagnosis and material content/placement requirements unchanged.
- Preserve actual dimensions, aspect ratio, coordinate system, and source revision; map viewport input explicitly to that frame.
- Bound geometry to the canvas/source and preserve stable region identities; source-bound masks must match source dimensions.
- Inpaint masks use transparent pixels for edit and opaque pixels for preserve.
- Require actual completed uploads only for artifacts required by the handoff; do not impose a universal two-upload requirement.
- Bind required exports to current marks and source revision; invalidate stale exports after drawing changes or reset.
- Choose concrete return keys and types from L2's `expected_return`; absent masks are allowed only when its return semantics permit.
- Ground source assets and references; fabricate no file IDs, uploads, options, previews, or edited outcomes.
- Use one primary submission of current spatial evidence; no approval checkbox or second confirmation step.
- Do not impose fixed tools or stages, render, embed implementation code, or call task image tools from this L3 widget skill.

## Output and Handoff

Pass a complete semantic contract using this local definition; do not add a success `handoff_type` or require an external document read:

- Identity: nonempty strings `selected_widget_id` (exact L2 selection), `widget_id` (instance identity), `widget_type` and `surface` (exact registry values), `planner_id` (owning L2), `purpose` (contextual), and unchanged `interaction_goal`.
- `iai`: copy L2's `chain_id`, `gap_type`, and binding `reason`, `maps_to_edge`, `source_nodes`, `target_node` unchanged; require a named chain and meaningful reason, edge source in `source_nodes`, and destination equal to `target_node` and allowed `state_update_target`. Include a deterministic `merge_strategy` for L1 and `next_planner_action: "re-enter Layer 1"`.
- `display`: grounded task values, source references, current values, and unresolved status; no invented evidence, defaults, uploads, previews, or outcomes.
- `controls`: array of records with `id`, `kind`, `label`, `purpose`, `required`, `return_keys`, `constraints`; IDs are unique/nonempty, kinds supported, labels/purposes nonempty, `required` boolean, and `return_keys` a nonempty list of declared return keys. State applicable limits, types, and source/edit rules in `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`, a nonempty `content` array of records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`); every source resolves. Include `interaction` with nonempty `actions`/`feedback` lists and `submission` (nonempty `label`, nonempty `preconditions`, `return_mapping`), plus nonempty semantic `appearance` and a nonempty `signature_features` list describing relevant behavior, not implementation or invented steps.
- `expected_return`: deterministic object with exactly L2's keys and types; `presentation.profile.interaction.submission.return_mapping` has exactly the same keys, each specifying its actual source and serialization. Preserve declared optional/empty semantics; derived returns need mappings, not artificial controls.
- `widget_requirements`: four nonempty string arrays, `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`; state minimal meaningful obligations consistent with the profile, not additional interaction gates.
- `safety`: `allow_html: false`, `allow_script: false`. Optional `runtime` declares only available approved capabilities and version-pinned libraries; optional `reference_assets` are plugin-relative design-time references and extracted principles only, never runtime assets.

Check source references, coordinate/mask semantics, required uploads, and revision-bound serialization before handoff.
Then load `l4-widget-renderer` with the complete design; do not ask L4 to invent missing spatial semantics.
On invalid selection or missing indispensable evidence/capability, return `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, a nonempty deterministic `validation_errors` array identifying failed checks, and `return_to: l1-router`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 Router owns canonical workflow state and may choose Completion or emit `decision: end`.
Every widget return or failure returns to `l1-router`; spatial submission is nonterminal and is not an edited result.
L1 maps returned values into canonical state at the preserved destination; L3 never declares workflow completion.
