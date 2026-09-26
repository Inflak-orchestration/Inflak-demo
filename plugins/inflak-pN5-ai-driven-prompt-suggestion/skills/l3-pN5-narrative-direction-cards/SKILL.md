---
name: l3-pN5-narrative-direction-cards
description: "Use when: P5 selects narrative-direction-cards to compare or adopt prepared narrative strategies."
---

# L3 Designer — Narrative Direction Cards

## Layer & Role

Design only `narrative-direction-cards` for `writing-brainstorm`, preserving the selected `divergence_gap`/`compare_narrative_directions` or `focus_gap`/`select_or_combine_narrative_directions` interpretation and declared compatible goal. L3 Designer exposes proposals and adoption controls; it never generates candidates, selects a direction, writes the artifact, renders or substitutes another widget.

Only Interaction Pathway enters L3: L1 → L2 gap + selection → L3 Designer → L4 Renderer → L1. Execution Pathway directly invokes active main_model from L2 without L3/L4. Host Agent Return and Completion stay with L1 and do not enter this skill.

The registry's `state_update_targets: [selected_directions]` names business storage, not a literal IAI-node allowlist. Preserve that path in `merge_strategy`; semantic `state_update_target` equals I for G→I presentation or T for I→T adoption. Showing proposals never marks them adopted.

## Inputs

Read L2 `planner_id`, `selected_widget_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `expected_return`, `return_to`, and `display_context`; resolve local registry and runtime capabilities. Require the actual seed and prepared candidate set; consume prior selection context. Each candidate has stable `id`, `title`, `logline`, `narrative_lens`, `form_or_structure`, `emotional_tone`, `creative_hook`, `tradeoff`. Missing prepared candidates require return to L1, not L3 invention.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Compare distinct strategies and choose what to develop or request more ideas. |
| Presented information | Preserve seed, all candidate fields, tradeoffs and prior selection context. |
| Supported interaction | One primary, optional supporting choices, rejected choices, more ideas, and a note. |
| Feedback and constraints | Distinguish primary/supporting/rejected states; require primary only for develop. |
| Submission and return | Serialize stable IDs and action without adopting unselected proposals. |
| Presentation intent | Comparable editorial cards, not an objective ranking of creative quality. |

## Essential Constraints

- Validate exact ID, skill/path, planner, gap, goal, edge, return coverage, artifact support, state destination and runtime. Preserve `narrative_direction_cards`, `conversation_widget`, modality and capabilities.
- Preserve `chain_id`, binding `reason`, source/edge/target and existing ordered-edge provenance. `G→I` exposes prepared directions at `I`; `I→T` records adoption at `T`. `state_update_target` equals that destination; deterministic L1 merging retains domain storage `selected_directions`.
- Preserve all 4–6 supplied strategies and their field values; never silently rank, rewrite or preselect. Require real distinguishable proposals, not empty/ID-only choices.
- Return exactly `primary_direction_id` (string), `supporting_direction_ids` (array), `rejected_direction_ids` (array), `action` (develop/more_ideas/dismiss), `freeform_note` (string).
- IDs must resolve to displayed candidates. Develop requires one primary and at most two supporting directions. Primary/supporting/rejected membership must be consistent and nonduplicated. More ideas permits empty selection and preserves note; dismissed input is not adoption.
- One primary submit action; no approval checkbox or extra confirmation. No HTML, CSS, JavaScript, render or task calls.

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

Check complete candidate content, membership and action-dependent mappings; load `l4-pN5-widget-renderer`. On invalid selection or missing indispensable evidence/capability, return `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, a nonempty deterministic `validation_errors` array identifying failed checks, and `return_to: l1-pN5-core-module`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 Router merges canonical state and emits `decision: end`. Every return/failure re-enters `l1-pN5-core-module`; direction adoption is not final-writing permission or Completion.
