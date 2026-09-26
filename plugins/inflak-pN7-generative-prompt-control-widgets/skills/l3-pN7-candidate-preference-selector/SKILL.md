---
name: l3-pN7-candidate-preference-selector
description: "Use when: P7 selects candidate-preference-selector for similar and dissimilar choices among concrete prepared directions."
---

# L3 Designer — Candidate Preference Selector

## Layer & Role

Design only `candidate-preference-selector` for `image-prompt-control`, `candidate_preference_gap`, `compare_candidate_directions` or declared `resolve_fine_grained_prompt_control`, on `I→Aug`. L3 Designer exposes candidates for one unresolved dimension; it never generates new candidates, substitutes a widget, writes negative prompt syntax, renders or executes.

Only Interaction Pathway enters L3: L1 → L2 gap + selection → L3 Designer → L4 Renderer → L1. Execution Pathway directly invokes the selected executor/main_model from L2 without L3/L4. Host Agent Return and Completion stay with L1 and do not enter this skill.

Registry `state_update_targets` names business paths under `control_spec`, not a literal IAI-node allowlist. Preserve the selected entry's paths in `merge_strategy`; semantic `state_update_target` is Aug, the I→Aug destination. Never rename paths or store IAI node fields as business state.

## Inputs

Read L2 `planner_id`, `selected_widget_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `expected_return`, `return_to`, and `display_context`; resolve local registry/runtime. Require actual prompt_document and stable anchored parameters with options/optional dissimilar_options. Each of the 3–6 prepared candidates has stable id, concise visible label and concrete one-sentence description. Missing, ID-only, generic Candidate 1, role-only or indistinguishable candidates fail validation.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Express which concrete direction is closer to or farther from the intended image. |
| Presented information | Keep all candidate labels/descriptions available alongside the source phrase and dimension. |
| Supported interaction | Select similar, dissimilar or unselected states within the supplied candidate domain. |
| Feedback and constraints | Prevent the same candidate being both similar and dissimilar; show current choices. |
| Submission and return | Serialize candidate identities in parameter values, changed IDs, preview and note. |
| Presentation intent | Inline chooser with bounded attached detail, not an ID-only select or detached card workflow. |

## Essential Constraints

- Validate exact ID, skill/path, planner, gap, goal, edge, returns, artifacts, state destination and runtime. Preserve `inline_prompt_parameter_editor`, `conversation_widget`, modality/capabilities.
- Preserve `chain_id`, binding `reason`, source/edge/target; source includes `I`, destination/state_update_target is `Aug`. L1 merges control_spec.candidate_preferences and inline_parameters by stable ID.
- Preserve candidate IDs, labels, descriptions and dimension exactly. Candidate ID must come from supplied options/dissimilar_options; similar and dissimilar sets are disjoint. Negative preferences are not positive prompt additions.
- Keep one unresolved dimension in scope. Preserve nested parameter controls and exact UTF-16 source spans; source slice equals parameter.text, with ordered/nonoverlapping complete phrase anchors. Missing/ambiguous anchors fail.
- Return exactly `parameter_values` (object), `changed_parameter_ids` (array), `compiled_prompt` (string), `freeform_note` (string). Only supplied affected parameter IDs may occur in changed IDs and they must occur in values. Return candidate IDs as identity, not labels substituted as IDs.
- Preview is deterministic review context, not a final provider prompt or canonical Aug→T transition. No fabricated images or attention evidence.
- One primary submit; no approval checkbox or second confirmation. No HTML, CSS, JavaScript, rendering or task calls.

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

Check candidate content, mutually exclusive states, spans and mappings; load `l4-pN7-widget-renderer`. On invalid selection or missing indispensable evidence/capability, return `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, a nonempty deterministic `validation_errors` array identifying failed checks, and `return_to: l1-pN7-core-module`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 Router merges canonical state and emits `decision: end`. Every return/failure re-enters `l1-pN7-core-module`; preferences are nonterminal input.
