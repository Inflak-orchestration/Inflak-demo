---
name: l3-pN6-prompt-structure-tree
description: "Use when: P6 selects prompt-structure-tree for traceable hierarchy organization or component repair in an existing tree."
---

# L3 Designer — Prompt Structure Tree

## Layer & Role

Design only `prompt-structure-tree` for `prompt-decomposition`, with `organize_prompt_hierarchy` or `complete_prompt_components` on `I→T`. Preserve the selected hierarchy/component gap. A flat grouping mismatch returns to L1, never substitutes the cell widget. L3 Designer neither compiles the Story Brief, renders nor generates a story.

Only Interaction Pathway enters L3: L1 → L2 gap + selection → L3 Designer → L4 Renderer → L1. Execution Pathway directly invokes active main_model from L2 without L3/L4. Host Agent Return and Completion stay with L1 and do not enter this skill.

The registry's `state_update_targets` lists business storage `prompt_structure`/`prompt_components`, not a literal IAI-node allowlist. Preserve those paths in `merge_strategy`; semantic `state_update_target` is T, the selected I→T destination. Do not rewrite registry paths or invent IAI state fields.

## Inputs

Read L2 `planner_id`, `selected_widget_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `expected_return`, `return_to`, and `display_context`; resolve local registry and runtime. Consume source prompts, traceable fragments, tree_nodes, root_ids, selected_node_id, expanded_node_ids, unresolved_ids and identified missing components. Distinguish model-proposed structure from user-confirmed structure.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Let the author organize meaningful containment and sibling order or repair identified missing components. |
| Presented information | Co-present a readable hierarchy, selected branch detail, assigned fragments and source provenance; node labels take priority over secondary status and movement controls. |
| Supported interaction | Expand/select, create/rename/delete, reparent/reorder, assign/edit/create/delete/split/merge fragments and mark status. |
| Feedback and constraints | Synchronize selection, hierarchy and detail; disclose affected descendants/fragments before destructive changes. |
| Submission and return | Serialize the complete valid tree and edit/provenance records, not just text fragments. |
| Presentation intent | Accessible hierarchy followed by a fragment panel filtered to the selected branch, not a graph canvas. |

## Essential Constraints

- Validate exact ID, skill/path, planner, gap, goal, edge, returns, artifact support, state destination and runtime. Preserve `prompt_structure_tree`, `conversation_widget`, modality/capabilities.
- Preserve `chain_id`, binding `reason`, source/edge/target and existing ordered-edge provenance. Source includes `I`; destination/state_update_target is `T`. L1 merges into existing prompt_structure/prompt_components storage.
- Return exactly `structure_kind: tree`, `tree_nodes`, `root_ids`, `selected_node_id`, `expanded_node_ids`, `fragment_edits`, `unresolved_ids`, `freeform_note`, with declared array/string types.
- Every node retains stable `id`, `parent_id`, `order`, `label`, `kind`, `status`, `fragment_ids`, `source_prompt_ids`. Empty parent identifies roots; root_ids contains all and only roots. Non-root parents exist, tree is acyclic, sibling order is unique, and status is confirmed/unresolved.
- Fragments retain stable `id`, `text`, `kind`, `origin`, `source_prompt_ids`. User-created fragments use `origin: user` and may have empty source lists; never invent source IDs. A fragment belongs to at most one node. Split preserves original provenance across new stable fragments; merge unions all contributing source IDs.
- Filter the fragment panel to selected node fragment_ids in order; selection/assignment changes immediately update it. Preserve established fragment-card editing/actions/provenance; show selected-branch empty state rather than unrelated fragments.
- Reparent/reorder needs accessible move controls as well as drag. Deletion identifies descendants/fragments and applies the user's deliberate disposition, never orphaning nodes or silently losing content. Selected/expanded/unresolved IDs reference existing nodes; preserve statuses and synchronization.
- Keep hierarchy labels readable as phrases. Each node uses a primary row for expand/collapse, label and status; place Up/Down/Out/In or equivalent movement actions in a separate action row or compact menu, never in the label's width allocation. Give the label a useful minimum width, prevent character-by-character wrapping, and truncate with an accessible full-label name only when space is genuinely exhausted.
- On desktop, use a hierarchy/detail split only when both panes retain useful widths; the hierarchy pane must be at least 280px and the selected-branch pane at least 320px. Below that threshold, stack hierarchy above selected-branch detail. Keep scrolling within each pane, avoid nested horizontal scrolling, and keep primary submit actions outside pane scroll regions.
- One primary submit, no approval checkbox or extra submission gate. Destructive-action disclosure is local safety, not workflow approval. No HTML, CSS, JavaScript, canvas/graph semantics, rendering or task calls.

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

Check valid hierarchy, unique ownership, provenance and exact mappings; load `l4-pN6-widget-renderer`. On invalid selection or missing indispensable evidence/capability, return `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, a nonempty deterministic `validation_errors` array identifying failed checks, and `return_to: l1-pN6-core-module`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 Router merges canonical state and emits `decision: end`. Every return/failure re-enters `l1-pN6-core-module`; submitting structure does not approve a Story Brief or generate a story.
