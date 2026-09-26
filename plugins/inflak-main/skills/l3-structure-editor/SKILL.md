---
name: l3-structure-editor
description: "Use when: Layer 2 selected structure-editor for prompt structure."
---

# L3 Designer — Structure Editor

## Layer & Role

L3 Designer handles interaction design only on Interaction Pathway: L2 gap + selection → L3 interaction design → L4 render → L1. Design L2's exact `selected_widget_id: structure-editor` as a lossless structural widget profile.
Specialize the supplied goal and task context; never diagnose another gap or select another widget.
L3 designs semantic structure operations; L4 implements them without changing their meaning.

## Inputs

- Read `planner_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `expected_return`, and `return_to` from L2.
- Resolve the exact widget registry entry, planner eligibility, and actual runtime capabilities.
- Read actual nodes, stable IDs, links, content, roles, provenance, and unresolved structural relationships.
- Preserve supplied ordering meaning, protected nodes, substantive relationship rules, and editing limits.
- Derive supported controls, labels, grouping, and structural validity constraints from intent and evidence; L2 need not design fields.
- Missing domain relationships must not become invented hierarchy merely to populate an editor.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Explain which structural decision serves the existing goal while preserving settled content. |
| Presented information | Show the relevant real structure, node identity, links, and the meaning of order or relationships. |
| Supported interaction | Derive needed ordering, grouping, hierarchy, or relationship operations within supported and permitted scope. |
| Feedback and constraints | Expose current structure and invalid operations; enforce identity, link consistency, and hierarchy validity where applicable. |
| Submission and return | Return the complete required structure and metadata under exactly L2's return keys, without losing unchanged nodes. |
| Presentation intent | Make relationships and ordering meaning understandable together, with accessible non-pointer interaction. |

## Essential Constraints

- Validate exact ID, skill/path, planner, gap, goal, edge, return coverage, artifact support, state target, and runtime availability.
- Keep registered type, surface, modality, and capability boundaries unchanged; do not broaden eligibility.
- Preserve `chain_id` and `iai_binding.reason` unchanged in `iai.chain_id` and `iai.reason`.
- Preserve `source_nodes`, `maps_to_edge`, and `target_node` unchanged; pending input is not a settled structure.
- Require the edge source in `source_nodes` and its destination in `target_node`; `state_update_target` identifies that destination.
- Preserve stable node IDs, content, provenance, and links except the relationships explicitly changed by permitted user operations.
- Reject duplicate identities, dangling references, inconsistent links, or silent node loss; retain all required nodes.
- For a hierarchy, enforce acyclicity and consistent parent/child links with the applicable root and parent rules.
- Do not impose tree restrictions on a nonhierarchical relationship model without semantic justification.
- Derive structural constraints from the represented model; substantive precedence or relationship choices remain with the user.
- Distinguish display/storage order from semantic order; never infer priority from an arbitrary initial arrangement.
- Do not resolve image layout through this skill or a text form; reject incompatible selection without choosing a substitute.
- Ground facts, actual nodes, source assets, and stable references; fabricate no options, uploads, or outcomes.
- Choose concrete return keys and types from L2's `expected_return`; define lossless structural serialization.
- Use one primary submission; no approval checkbox, forced rearrangement, or second confirmation step.
- Do not impose fixed controls or stages, generate final content, render, execute tasks, or embed implementation code.

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

Check source references, node preservation, relationship semantics, validity constraints, and complete serialization.
Then load `l4-widget-renderer`; L4 implements the specified structure operations rather than designing their semantics.
On invalid selection or missing indispensable evidence/capability, return `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, a nonempty deterministic `validation_errors` array identifying failed checks, and `return_to: l1-router`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 Router owns canonical workflow state and may choose Completion or emit `decision: end`.
Every widget return or failure returns to `l1-router`; a submitted structure is nonterminal.
L1 maps returned values into canonical state at the preserved destination; L3 never declares workflow completion.
