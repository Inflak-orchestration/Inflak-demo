---
name: l3-pN2-storyboard-block-composer
description: "Use when: P2 selects storyboard-block-composer to organize, supply, repair, or confirm source-linked prompt units."
---

# L3 Designer — User-Driven Prompt Organization

## Layer & Role

Design only the exact `storyboard-block-composer` selection for `visual-story-composition`; keep its registered entry/source/repair/confirmation gap and goal. The stable ID denotes the source-linked editor, not a curated block menu. L3 Designer designs interaction on Interaction Pathway; it neither compiles Aug nor executes generation, renders, substitutes a widget, or diagnoses another gap.

Only Interaction Pathway enters L3: L1 → L2 gap + selection → L3 Designer → L4 Renderer → L1. Execution Pathway directly invokes the selected executor from L2 without L3/L4. Host Agent Return and Completion stay with L1 and do not enter this skill.

## Inputs

Read L2 `planner_id`, `selected_widget_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `expected_return`, `display_context`, and `return_to`. Resolve the selected local registry entry and runtime availability. Consume exact `source_text`, `schema_version: pN2-prompt-structure-v2`, latest `prompt_structure`, and supplied validation errors. Empty source is legitimate only for source-entry interaction, not evidence of confirmation.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Give the user authorship over source-linked units, grouping and order. |
| Presented information | Co-present source text, exact span links, editable groups/units, provenance and validity. |
| Supported interaction | Edit/resegment source; edit, activate, lock, add, remove, move and order units; edit groups and output mode. |
| Feedback and constraints | Highlight source span on focus and distinguish extracted, user-edited and user-added wording. |
| Submission and return | Review instruction submits the complete structure; generation still needs a separate preview confirmation. |
| Presentation intent | Source-and-structure workspace with clear Unsorted material and accessible structural preview. |

## Essential Constraints

- Validate exact ID, skill/path, planner, gap, goal, atomic edge, return coverage, artifact support and available capabilities. Preserve `storyboard_prompt_block_composer`, `conversation_widget` and all registered limits.
- Preserve `chain_id` and binding `reason`/source/edge/target. Edge source must occur in `source_nodes`; `state_update_target` equals destination `I` for entry or `T` for source/structure changes. The deterministic L1 merge stores the business result in `prompt_structure`; storage paths are not IAI nodes.
- The registry's `state_update_targets: [prompt_structure]` names business storage, not a literal IAI-node allowlist. Validate that storage through `merge_strategy`; validate the semantic `state_update_target` against the selected edge destination I/T. Keep both meanings without rewriting registry paths or inventing node fields.
- Return exactly `schema_version`, `source_text`, `mode`, `groups`, `units`, `submission_status`. Version is `pN2-prompt-structure-v2`; mode is `single_image` or `multi_scene`; status is `draft` or `confirmed`.
- Groups contain stable `id`, editable `label`, `order`, `scope` (global/local). Units contain stable `id`, `raw_text`, `source_span`, `group_id`, `order`, `active`, `locked`, `user_owned`, `provenance`. Preserve boolean types, unique IDs, contiguous unit order within each group, valid group references, and at least one active nonempty unit for confirmation.
- Source spans are zero-based half-open string offsets. Initially `raw_text` equals the exact source slice. A user edit retains its original span and uses `provenance: user_edited`; a user-added unit has null span and `provenance: user_added`. Never rewrite source to hide edits or claim suggestions were extracted.
- Initial source-derived units go in one local Unsorted group. Offer editable category groups but infer no semantic assignments. Preserve prior user grouping on re-entry. Do not require fixed categories or multiple scenes for a single image.
- Structure confirmation permits deterministic compilation, not generation. One primary Review instruction action, no approval checkbox or extra approval inside this widget. The separate preview is a distinct domain dependency, not a redundant checkbox.
- No HTML, CSS, JavaScript, rendering or task calls; do not invent source wording, provenance, confirmed status or output.

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

Check spans, schema, lock/ownership state and lossless mappings, then load `l4-pN2-widget-renderer`. On invalid selection or missing indispensable evidence/capability, return `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, a nonempty deterministic `validation_errors` array identifying failed checks, and `return_to: l1-pN2-core-module`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 Router merges the structure into canonical state and emits `decision: end`. Every submission, dismissal or failure re-enters `l1-pN2-core-module`; structure confirmation is nonterminal.
