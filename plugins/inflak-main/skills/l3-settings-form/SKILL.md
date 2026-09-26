---
name: l3-settings-form
description: "Use when: Layer 2 selected settings-form for missing writing, revision, image-generation, or image-edit settings."
---

# L3 Designer — Settings Form

## Layer & Role

L3 Designer handles interaction design only on Interaction Pathway: L2 gap + selection → L3 interaction design → L4 render → L1. Design L2's exact `selected_widget_id: settings-form` as a task-specific semantic widget profile.
Specialize the supplied goal and task context; never diagnose another gap or select another widget.
L3 owns interaction design; L4 owns rendering and implementation.

## Inputs

- Read `planner_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `expected_return`, and `return_to` from the L2 handoff.
- Resolve the exact selected entry from the widget registry; use planner eligibility and actual runtime capabilities.
- Read task intent, source evidence, known or delegated settings, and consequential unresolved constraints.
- Preserve supplied field identities, value domains, defaults, provenance, and substantive user limits.
- L2 need not predesign fields: derive supported controls, labels, grouping, and validation from intent and evidence.
- Missing domain facts are not permission to invent values or demand a planner-authored UI schema.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Explain which consequential missing constraint this interaction contributes to the existing goal. |
| Presented information | Separate known or delegated settings from unresolved decisions; show relevant evidence and consequences. |
| Supported interaction | Derive only the typed inputs needed for those decisions, within registered capabilities and supplied limits. |
| Feedback and constraints | Distinguish unset, known, and proposed values; explain requiredness and domain errors without choosing for the user. |
| Submission and return | Map typed values to the exact L2 return keys; retain settled values only as its return policy requires. |
| Presentation intent | Prioritize unresolved decisions, keep context readable, and associate accessible labels and errors with each input. |

## Essential Constraints

- Validate exact ID, skill/path, planner, gap, goal, edge, return coverage, artifact support, state target, and runtime availability.
- Keep registered type, surface, modality, and capabilities unchanged; eligibility is not a new diagnosis.
- Preserve `chain_id` and `iai_binding.reason` unchanged in `iai.chain_id` and `iai.reason`.
- Preserve `source_nodes`, `maps_to_edge`, and `target_node` unchanged; pending input is not submitted evidence.
- Require the edge source in `source_nodes` and its destination in `target_node`; `state_update_target` must identify that destination.
- Ask only for consequential missing constraints, not every setting the primitive could represent.
- Known or delegated values do not force fields, re-entry, or confirmation; keep them as context when useful.
- Distinguish a supported default from an unresolved substantive choice; never silently fill the latter.
- Ground domain values, actual options, source assets, and stable references in evidence; fabricate no uploads or outcomes.
- Choose concrete return keys and types from L2's `expected_return`, not from the registry's entire capability list.
- Define precise serialization and optional-value handling for each declared return.
- Use one primary submission of current values; no approval checkbox or second confirmation step.
- Do not impose fixed controls, stages, or follow-on interactions; derive the smallest useful profile.
- Produce no HTML, CSS, JavaScript, rendering calls, or task execution from this widget skill.

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

Check grounded display references, control consistency, required behavior, and submission validity before handoff.
Then load `l4-widget-renderer` with that complete contract; do not delegate missing interaction design to L4.
On invalid selection or missing indispensable evidence/capability, return `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, a nonempty deterministic `validation_errors` array identifying failed checks, and `return_to: l1-router`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 Router owns canonical workflow state and may choose Completion or emit `decision: end`.
Every widget return or failure returns to `l1-router`; submission is nonterminal.
L1 maps returned values into canonical state at the preserved destination; L3 never declares the workflow complete.
