---
name: l3-option-selector
description: "Use when: Layer 2 selected option-selector for a direction, alternative, or generated candidate decision."
---

# L3 Designer — Option Selector

## Layer & Role

L3 Designer handles interaction design only on Interaction Pathway: L2 gap + selection → L3 interaction design → L4 render → L1. Design L2's exact `selected_widget_id: option-selector` as a task-specific semantic widget profile.
Specialize the supplied goal and task context; never diagnose another gap or select another widget.
L3 designs how actual choices are understood and selected; L4 implements the interaction.

## Inputs

- Read `planner_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `expected_return`, and `return_to` from L2.
- Resolve the exact widget registry entry, planner eligibility, and available runtime capabilities.
- Read actual options, stable IDs, source content, provenance, known selections, and any selection limits.
- Preserve supplied descriptions, keyword dimensions, content-bearing fragments, and real preview references.
- Derive supported controls, labels, grouping, and cardinality from intent and evidence; L2 need not design the UI.
- Distinguish missing candidate evidence from presentation choices that L3 can legitimately make.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Explain the choice the user is making and how it serves the already diagnosed goal. |
| Presented information | Present actual choices, relevant consequences, provenance, and real previews when available. |
| Supported interaction | Choose single-select, multi-select, or ranking by selection semantics, not a universal gallery pattern. |
| Feedback and constraints | Expose selection state, cardinality, and meaningful ranking scope; explain invalid choices without auto-selecting. |
| Submission and return | Map selected stable IDs and any permitted ordering to exactly the return keys and types chosen by L2. |
| Presentation intent | Keep each option's meaning associated with its selection state; make comparison and ordering accessible. |

## Essential Constraints

- Validate exact ID, skill/path, planner, gap, goal, edge, return coverage, artifact support, state target, and runtime availability.
- Preserve registered type, surface, modality, and capability boundaries without broadening eligibility.
- Preserve `chain_id` and `iai_binding.reason` unchanged in `iai.chain_id` and `iai.reason`.
- Preserve `source_nodes`, `maps_to_edge`, and `target_node` unchanged; pending input is not a recorded choice.
- Require the edge source in `source_nodes` and its destination in `target_node`; `state_update_target` identifies that destination.
- Use stable IDs for actual choices, never labels or display positions as replacement identities.
- Do not generate candidates, fabricate alternatives, invent outcomes, or silently select a material choice.
- Use multi-select for `select_writing_topic_keywords` and `select_image_keywords`; grouping does not force one choice per group.
- Preserve supplied selection limits; derive only structural validity rules when the goal already establishes their meaning.
- Enable ranking only when priority is meaningful; display order alone is not user preference.
- A single actual option needs no invented competitor or ranking exercise; dismissal is not adoption.
- Ground domain facts, source assets, and stable references; use only real previews and uploads.
- Take concrete return keys and types from L2's `expected_return`; map inactive optional returns without artificial controls.
- Use one primary submission of current choices; no approval checkbox or second confirmation step.
- Do not impose fixed controls or follow-on stages, produce implementation code, render, or execute the task.

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

Check display references, supported operations, selection constraints, and valid serialization before handoff.
Then load `l4-widget-renderer`; L4 implements the design rather than inventing missing selection semantics.
On invalid selection or missing indispensable evidence/capability, return `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, a nonempty deterministic `validation_errors` array identifying failed checks, and `return_to: l1-router`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 Router owns canonical workflow state and may choose Completion or emit `decision: end`.
Every widget return or failure returns to `l1-router`; a submitted choice is nonterminal.
L1 maps returned values into canonical state at the preserved destination; L3 never declares workflow completion.
