---
name: l3-pN6-story-brief
description: "Use when: P6 selects story-brief-review for explicit author review of a compiled traceable Story Brief."
---

# L3 Designer — Story Brief Review

## Layer & Role

Design only `story-brief-review` for `prompt-decomposition`, `brief_review_gap`, `review_story_brief` on `I→Aug`. L3 Designer exposes the already compiled brief for correction and explicit approval; it never compiles missing sections, renders, generates the story or substitutes another interaction.

Only Interaction Pathway enters L3: L1 → L2 gap + selection → L3 Designer → L4 Renderer → L1. Execution Pathway directly invokes active main_model from L2 without L3/L4. Host Agent Return and Completion stay with L1 and do not enter this skill.

The registry's `state_update_targets: [augmented_instruction]` names business storage, not a literal IAI-node allowlist. Preserve that path in `merge_strategy`; semantic `state_update_target` is Aug, the selected I→Aug destination. Approval remains a current user decision, not a storage-name conversion.

## Inputs

Read L2 `planner_id`, `selected_widget_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `expected_return`, `return_to`, and `display_context`; resolve local registry and runtime. Require traceable brief_sections from the current submitted structure; consume unresolved_ids, selected_section_id, sources and current approval context. Missing required content remains unresolved, not invented.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Let the author inspect, correct and approve the instruction before story generation. |
| Presented information | Show brief sections, source provenance, selected detail and unresolved decisions. |
| Supported interaction | Select, expand/collapse, edit sections, mark status, approve or return to structure. |
| Feedback and constraints | Edits reset approval; unresolved required sections block approval visibly. |
| Submission and return | Serialize all sections, exact unresolved IDs and the actual boolean approval decision. |
| Presentation intent | Editable brief, not a fixed story-stage checklist or generic approval checkbox. |

## Essential Constraints

- Validate exact ID, skill/path, planner, gap, goal, edge, returns, artifact support, state destination and runtime. Preserve `story_brief_review`, `conversation_widget`, modality/capabilities.
- Preserve `chain_id`, binding `reason`, source/edge/target; source includes `I`, destination/state_update_target is `Aug`. L1 merges the actual brief into augmented_instruction.
- Return exactly `structure_kind: story_brief`, `brief_sections`, `selected_section_id`, `unresolved_ids`, `approved` (boolean), `freeform_note`, preserving declared array/string types.
- Sections retain stable `id`, `kind`, `label`, `text`, `status`, `source_prompt_ids`. Kinds: premise, protagonist, setting, conflict, tone_constraints, narrative_direction, unresolved_decision. These are supported kinds, not a requirement to invent every kind. User additions use `origin: user` and may have empty source lists; retain actual component/source lineage.
- Status is confirmed/unresolved; unresolved_ids contains every and only unresolved existing section. Selected ID is empty or existing. Missing indispensable sections cannot be silently marked confirmed.
- `approved: true` requires the explicit Approve Brief action on the current version and no unresolved required sections. Editing resets approval false. Return to Structure returns approved false and preserves all edits. Both paths return to L1, never directly to generation.
- Keep genuine post-structure brief approval, with one primary submit action and no confirmation checkbox or second approval step. No HTML, CSS, JavaScript, rendering or task calls.

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

Check section provenance, status sets, approval invalidation and mappings; load `l4-pN6-widget-renderer`. On invalid selection or missing indispensable evidence/capability, return `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, a nonempty deterministic `validation_errors` array identifying failed checks, and `return_to: l1-pN6-core-module`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 Router merges canonical state and emits `decision: end`. Every return/failure re-enters `l1-pN6-core-module`; approved brief is nonterminal execution evidence, not a generated story.
