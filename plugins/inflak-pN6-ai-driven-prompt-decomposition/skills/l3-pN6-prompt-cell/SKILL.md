---
name: l3-pN6-prompt-cell
description: "Use when: P6 selects prompt-cell for topical grouping or component repair in an existing cell map."
---

# L3 Designer — Prompt Cell

## Layer & Role

Design only `prompt-cell` for `prompt-decomposition`, `topic_grouping_gap` or `component_gap`, with `organize_prompt_topics` or `complete_prompt_components` on `I→T`. A hierarchy mismatch fails to L1 without substitution. L3 Designer designs topical grouping only, not directed relationships, story synthesis or rendering.

Only Interaction Pathway enters L3: L1 → L2 gap + selection → L3 Designer → L4 Renderer → L1. Execution Pathway directly invokes active main_model from L2 without L3/L4. Host Agent Return and Completion stay with L1 and do not enter this skill.

The registry's `state_update_targets` lists business storage `prompt_structure`/`prompt_components`, not a literal IAI-node allowlist. Preserve those paths in `merge_strategy`; semantic `state_update_target` is T, the selected I→T destination. Do not rewrite registry paths or invent IAI state fields.

## Inputs

Read L2 `planner_id`, `selected_widget_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `expected_return`, `return_to`, and `display_context`; resolve local registry and runtime. Consume source prompts, traceable fragments, cells, unassigned_fragment_ids, selected_cell_id and missing components. Preserve prior author assignments and distinguish unassigned model proposals.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Group or repair prompt components by topic without implying hierarchy or sequence. |
| Presented information | Show named cells, active assignments, unassigned suggestions and source provenance. |
| Supported interaction | Create/rename/delete/reorder cells, assign/remove/move fragments, expand/collapse detail and edit content. |
| Feedback and constraints | Keep overview/detail synchronized; disclose which fragments deletion makes unassigned. |
| Submission and return | Serialize complete membership, unassigned IDs, selection and fragment edits. |
| Presentation intent | Linked cell overview and editable detail; ordering is presentation, not narrative dependency. |

## Essential Constraints

- Validate exact ID, skill/path, planner, gap, goal, edge, return coverage, artifact support, state destination and runtime. Preserve `prompt_cell_map`, `conversation_widget`, modality/capabilities.
- Preserve `chain_id`, binding `reason`, source/edge/target and supplied ordered-edge provenance. Source includes `I`; destination/state_update_target is `T`. L1 merges existing prompt_structure/prompt_components, not invented node fields.
- Return exactly `structure_kind: cell_map`, `cells`, `unassigned_fragment_ids`, `selected_cell_id`, `fragment_edits`, `freeform_note` with declared array/string types.
- Cells have stable `id`, `label`, `fragment_ids` and preserved optional `source_prompt_ids`. Fragments retain stable `id`, `text`, `kind`, `source_prompt_ids`; user-created fragments use `origin: user` and may have empty source lists. Never fabricate extraction provenance.
- Every fragment belongs to at most one cell. Unassigned fragments appear only in unassigned_fragment_ids; deleting a cell returns its fragments there after showing the affected items. Do not silently discard material.
- Selected cell is empty or existing. Selection synchronizes overview/detail; explicit expand/collapse exposes editable label and fragment text. Return those edits in cells/fragment_edits. Keep active grouped fragments distinct from unassigned suggestions.
- Provide accessible alternatives to drag reorder/assignment. Do not create graph edges, parent-child semantics or implicit sequence; a different need returns to L1.
- One primary submission, no approval checkbox or second confirmation. No HTML, CSS, JavaScript, rendering, brief compilation or task calls.

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

Check unique membership, unassigned preservation, provenance and mappings; load `l4-pN6-widget-renderer`. On invalid selection or missing indispensable evidence/capability, return `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, a nonempty deterministic `validation_errors` array identifying failed checks, and `return_to: l1-pN6-core-module`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 Router merges canonical state and emits `decision: end`. Every return/failure re-enters `l1-pN6-core-module`; cell submission is nonterminal and does not approve the Story Brief.
