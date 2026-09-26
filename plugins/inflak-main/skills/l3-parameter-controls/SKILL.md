---
name: l3-parameter-controls
description: "Use when: Layer 2 selected parameter-controls for bounded revision or image-edit values."
---

# L3 Designer — Parameter Controls

## Layer & Role

L3 Designer handles interaction design only on Interaction Pathway: L2 gap + selection → L3 interaction design → L4 render → L1. Design L2's exact `selected_widget_id: parameter-controls` as a task-specific bounded-parameter profile.
Specialize the supplied goal and task context; never diagnose another gap or select another widget.
L3 designs meaningful parameter interaction and feedback; L4 implements supported controls.

## Inputs

- Read `planner_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `expected_return`, and `return_to` from L2.
- Resolve the exact widget registry entry, planner eligibility, and actual runtime capabilities.
- Read parameter meaning, stable IDs, types, domain bounds, units, increments, and applicable dependencies.
- Distinguish known values, unresolved values, and proposed defaults using source evidence and provenance.
- Derive supported controls, labels, grouping, and validation from intent and evidenced domains; L2 need not design fields.
- Establish actual preview support separately from value feedback; missing domain definitions cannot be invented.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Explain which task-controlling parameter decision contributes to the already diagnosed goal. |
| Presented information | Show relevant meaning, current values, default status, bounds, units, dependencies, and actual preview availability. |
| Supported interaction | Select needed sliders, steppers, toggles, color controls, or reset behavior within registered capabilities. |
| Feedback and constraints | Expose precise values and validation errors; distinguish value feedback from a genuinely available preview. |
| Submission and return | Serialize validated parameter values with their original types and units under exactly L2's return keys. |
| Presentation intent | Keep meaning, value, unit, and limits associated; communicate default, changed, and error states accessibly. |

## Essential Constraints

- Validate exact ID, skill/path, planner, gap, goal, edge, return coverage, artifact support, state target, and runtime availability.
- Keep registered type, surface, modality, and capabilities unchanged; do not broaden routing eligibility.
- Preserve `chain_id` and `iai_binding.reason` unchanged in `iai.chain_id` and `iai.reason`.
- Preserve `source_nodes`, `maps_to_edge`, and `target_node` unchanged; a displayed value is not automatically submitted input.
- Require the edge source in `source_nodes` and its destination in `target_node`; `state_update_target` identifies that destination.
- Ground parameter IDs, types, bounds, units, and dependencies in domain evidence; do not invent substantive parameters.
- Choose controls from parameter semantics rather than requiring planner-authored control kinds or exposing every capability.
- Validate finite numeric values, applicable increments, categorical domains, and dependencies without silent clamping or coercion.
- Preserve declared units and types through return serialization; avoid false decimal-step failures from floating-point representation.
- Keep known values distinct from proposed defaults; neither displaying nor resetting a proposal counts as user submission.
- Do not force changes away from a valid current/default value or make settled parameters into new required decisions.
- Reset, when useful and supported, restores only evidenced defaults without submitting or changing unrelated input.
- Show previews only when genuinely supported and produced; value changes alone do not prove a visual or textual outcome.
- Ground actual options, source assets, and stable references; fabricate no previews, uploads, or execution results.
- Choose concrete return keys and types from L2's `expected_return`; map each value with its declared type and unit.
- Use one primary submission of current values; no approval checkbox or second confirmation step.
- Do not impose fixed controls or stages, render, execute task operations, or embed implementation code.

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

Check grounded domains, control constraints, default provenance, preview claims, and typed serialization before handoff.
Then load `l4-widget-renderer`; L4 implements the design without inventing missing parameter semantics.
On invalid selection or missing indispensable evidence/capability, return `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, a nonempty deterministic `validation_errors` array identifying failed checks, and `return_to: l1-router`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 Router owns canonical workflow state and may choose Completion or emit `decision: end`.
Every widget return or failure returns to `l1-router`; submitted parameters are nonterminal.
L1 maps returned values into canonical state at the preserved destination; L3 never declares workflow completion.
