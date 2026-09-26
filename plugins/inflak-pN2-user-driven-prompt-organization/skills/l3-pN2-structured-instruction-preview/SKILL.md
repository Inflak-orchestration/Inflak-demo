---
name: l3-pN2-structured-instruction-preview
description: "Use when: P2 selects structured-instruction-preview to review the exact instruction compiled from a confirmed structure."
---

# L3 Designer — Structured Instruction Preview

## Layer & Role

Design only `structured-instruction-preview` for `visual-story-composition`, `instruction_preview_gap`, `review_compiled_instruction`, on `T→Aug`. L3 Designer exposes the already compiled instruction; it never compiles or edits it, substitutes another widget, renders, or calls generation.

Only Interaction Pathway enters L3: L1 → L2 gap + selection → L3 Designer → L4 Renderer → L1. Execution Pathway directly invokes the selected executor from L2 without L3/L4. Host Agent Return and Completion stay with L1 and do not enter this skill.

The registry's `state_update_targets: [instruction_preview_status]` names business storage, not a literal IAI-node allowlist. Preserve it in `merge_strategy`; semantic `state_update_target` equals Aug, the T→Aug edge selected by this planner's preview diagnosis, never a business path. Broader registry edge support does not authorize L3 to change L2's selected edge.

## Inputs

Read L2 `planner_id`, `selected_widget_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `expected_return`, `return_to`, and grounded `display_context`. Resolve the exact local registry entry and available runtime. Require the nonempty exact `compiled_instruction`, confirmed source-structure context, schema version, mode, and actual provenance note. Missing compilation is not permission to fabricate a preview.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Confirm what will actually be sent for image generation or return to structure editing. |
| Presented information | Show the exact compiled instruction, mode, version and source provenance. |
| Supported interaction | Back to structure or Confirm & generate decisions; no inline instruction edits. |
| Feedback and constraints | Make the reviewed version and nonterminal decision unambiguous. |
| Submission and return | Return only preview_status; current confirmed text stays bound through L1. |
| Presentation intent | Read-only instruction-led review with reachable decisions, not a generic approval checkbox. |

## Essential Constraints

- Validate exact ID, skill/path, planner, gap, goal, edge, return coverage, artifact support and runtime availability. Preserve `structured_instruction_preview`, `conversation_widget`, modality and capabilities.
- Preserve `chain_id`, binding `reason`, source/edge/target unchanged; edge source is `T`, destination and `state_update_target` are `Aug`. L1 stores the business decision at `instruction_preview_status` without replacing the IAI destination.
- Reproduce `compiled_instruction` exactly: no additions, omissions, reordering, normalization or rewriting. Require it to correspond to the latest confirmed structure; source changes invalidate stale review.
- Return exactly `preview_status` as `confirmed` or `revise`. Do not add freeform fields, instruction text or execution flags.
- `revise` preserves structure and returns via L1; `confirmed` is permission for the next L2 execution pass only. Keep the distinct structure-confirmation and compiled-preview-confirmation dependency.
- One primary confirmation action and a back action; no confirmation checkbox, forced change or additional approval. No HTML, CSS, JavaScript, rendering or task calls.

## Output and Handoff

Pass a complete semantic contract using this local definition; no success `handoff_type` or external document read:

- Identity: nonempty strings `selected_widget_id` (exact L2 selection), `widget_id` (instance identity), `widget_type` and `surface` (exact registry values), `planner_id` (owning L2), `purpose` (contextual), and unchanged `interaction_goal`.
- `iai`: copy L2's `chain_id`, `gap_type`, and binding `reason`, `maps_to_edge`, `source_nodes`, `target_node` unchanged; require a named chain and meaningful reason, edge source in `source_nodes`, and destination equal to `target_node` and allowed `state_update_target`. Include a deterministic `merge_strategy` for L1 and `next_planner_action: "re-enter Layer 1"`.
- `display`: grounded task values, source references, current values, and unresolved status; no invented evidence, defaults, uploads, previews, or outcomes.
- `controls`: array of records with `id`, `kind`, `label`, `purpose`, `required`, `return_keys`, `constraints`; IDs are unique/nonempty, kinds supported, labels/purposes nonempty, `required` boolean, and `return_keys` a nonempty list of declared return keys. State applicable limits, types, and source/edit rules in `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`, a nonempty `content` array of records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`); every source resolves. Include `interaction` with nonempty `actions`/`feedback` lists and `submission` (nonempty `label`, nonempty `preconditions`, `return_mapping`), plus nonempty semantic `appearance` and a nonempty `signature_features` list describing relevant behavior, not implementation or invented steps.
- `expected_return`: deterministic object with exactly L2's keys and types; `presentation.profile.interaction.submission.return_mapping` has exactly the same keys, each specifying its actual source and serialization. Preserve declared optional/empty semantics; derived returns need mappings, not artificial controls.
- `widget_requirements`: four nonempty string arrays, `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`; state minimal meaningful obligations consistent with the profile, not additional interaction gates.
- `safety`: `allow_html: false`, `allow_script: false`. Optional `runtime` declares only available approved capabilities and version-pinned libraries; optional `reference_assets` are plugin-relative design-time references and extracted principles only, never runtime assets.

Check exact instruction and single-key mapping, then load `l4-pN2-widget-renderer`. On invalid selection or missing indispensable evidence/capability, return `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, a nonempty deterministic `validation_errors` array identifying failed checks, and `return_to: l1-pN2-core-module`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 Router owns canonical merging and emits `decision: end`. Every result or failure re-enters `l1-pN2-core-module`; confirmation does not itself generate or complete a workflow.
