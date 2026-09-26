---
name: l3-pN5-prompt-constellation
description: "Use when: P5 selects prompt-constellation for seed entry, focused writing facets, or current-prompt confirmation."
---

# L3 Designer — Prompt Constellation

## Layer & Role

Design only `prompt-constellation` for `writing-brainstorm`. Preserve one selected goal: `collect_writing_seed`, `focus_writing_prompt`, or `confirm_writing_prompt` with its registered seed/development/confirmation gap. L3 Designer designs grouped creative choices and prompt editing, not a new workflow, candidate generation, final writing or rendering.

Only Interaction Pathway enters L3: L1 → L2 gap + selection → L3 Designer → L4 Renderer → L1. Execution Pathway directly invokes active main_model from L2 without L3/L4. Host Agent Return and Completion stay with L1 and do not enter this skill.

The registry's `state_update_targets` lists business storage `writing_constraints`/`confirmed_prompt`, not a literal IAI-node allowlist. Preserve those paths in `merge_strategy`; semantic `state_update_target` is T, the selected H→T or I→T destination. Confirmation still requires current user evidence.

## Inputs

Read L2 `planner_id`, `selected_widget_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `expected_return`, `return_to`, and `display_context`. Resolve local registry and runtime. Consume current seed/premise, selected directions, supplied facet suggestions, existing constraints, `current_prompt_preview` and actual confirmation context. Missing seed remains visibly empty on seed entry, not model-authored content.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Supply the missing seed or creative facet, or confirm the current focused prompt. |
| Presented information | Show writer-owned premise, optional suggestions, current choices and editable prompt. |
| Supported interaction | Choose/remove chips, add custom facet text, leave a facet open deliberately, edit prompt, confirm or return to directions. |
| Feedback and constraints | Distinguish suggestions, adopted values and intentional ambiguity; show current preview. |
| Submission and return | Serialize facet objects, edits, action and note into the existing exact return. |
| Presentation intent | Premise-led grouped facet workspace; do not turn every optional facet into a required question. |

## Essential Constraints

- Validate exact ID, skill/path, planner, gap, goal, edge, returns, artifacts, state destination and runtime. Preserve `prompt_constellation`, `conversation_widget`, modality/capabilities.
- Preserve `chain_id`, binding `reason`, source/edge/target unchanged. Seed uses `H→T`; development/confirmation use `I→T`. Destination/state_update_target is `T`; L1's deterministic merge retains seed_prompt, writing_constraints or confirmed_prompt as appropriate, not a fabricated node.
- Supported facets: `artifact_type`, `audience`, `narrative_lens`, `form_or_structure`, `scope_or_setting`, `tone`, `length`, `constraints`. Include only current relevant facets and supplied proposals; preserve selected direction and writer wording.
- `leave_open` is an explicit scoped user choice, not the interpretation of silence. Do not force precision or treat absent material information as settled.
- Return exactly `selected_facets` (object), `custom_facets` (object), `prompt_edits` (string), `action` (continue/confirm/back_to_directions/dismiss), `freeform_note` (string). Keep unchanged values and empty semantics; custom text is user-owned.
- Confirmation binds the currently displayed prompt; edits invalidate old confirmation. Back to directions preserves work and returns through L1. One primary submit action, no approval checkbox or second confirmation.
- No HTML, CSS, JavaScript, rendering, final prompt synthesis on behalf of the user, or task calls.

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

Check exact goal, actual premise, intentional-open semantics and lossless mappings; load `l4-pN5-widget-renderer`. On invalid selection or missing indispensable evidence/capability, return `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, a nonempty deterministic `validation_errors` array identifying failed checks, and `return_to: l1-pN5-core-module`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 Router merges canonical state and emits `decision: end`. Every return/failure re-enters `l1-pN5-core-module`; confirmation is nonterminal evidence for later L2 execution.
