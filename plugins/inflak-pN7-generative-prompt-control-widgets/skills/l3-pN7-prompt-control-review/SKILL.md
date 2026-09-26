---
name: l3-pN7-prompt-control-review
description: "Use when: P7 selects prompt-control-review for the current controlled prompt, parameter edits or one targeted reopening."
---

# L3 Designer — Prompt Control Review

## Layer & Role

Design only `prompt-control-review` for `image-prompt-control`, `prompt_confirmation_gap`, `review_controlled_generation_prompt` or declared `resolve_fine_grained_prompt_control`, on `I→Aug`. L3 Designer exposes the accepted controls and compiled preview; unresolved atomic choices fail back to L1 rather than selecting another widget. Never render, compile missing provider semantics or generate an image.

Only Interaction Pathway enters L3: L1 → L2 gap + selection → L3 Designer → L4 Renderer → L1. Execution Pathway directly invokes the selected executor/main_model from L2 without L3/L4. Host Agent Return and Completion stay with L1 and do not enter this skill.

Registry `state_update_targets: [control_spec]` names business storage, not a literal IAI-node allowlist. Preserve that path in `merge_strategy`; semantic `state_update_target` is Aug, the I→Aug destination. Never rename paths or store IAI node fields as business state.

## Inputs

Read L2 `planner_id`, `selected_widget_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `expected_return`, `return_to`, and `display_context`; resolve local registry/runtime. Require actual compiled_prompt, control_summary, provider_note and current confirmed prompt_document parameters. Preserve the exact reviewed control version and source provenance; missing evidence is not readiness.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Accept the current generation prompt, edit supplied parameters, or reopen one category. |
| Presented information | Keep compiled prompt, accepted controls and provider limitations visible. |
| Supported interaction | Accept, edit, or reopen_control; choose a valid category only for reopening. |
| Feedback and constraints | Make current review/edited state and required category clear; invalidate stale acceptance. |
| Submission and return | Serialize all six declared fields without invoking image generation. |
| Presentation intent | Prompt-led inline review; accepted controls remain inspectable and source-bound. |

## Essential Constraints

- Validate exact ID, skill/path, planner, gap, goal, edge, returns, artifacts, state target and runtime. Preserve `inline_prompt_parameter_editor`, `conversation_widget`, modality/capabilities.
- Preserve `chain_id`, binding `reason`, source/edge/target; source includes `I`, destination/state_update_target is `Aug`. L1 deterministically merges review evidence into control_spec; no direct executor continuation.
- Return exactly `action` (accept/edit/reopen_control), `parameter_values` (object), `changed_parameter_ids` (array), `compiled_prompt` (string), `control_category` (string), `freeform_note` (string).
- Reopen requires exactly one known P7 control category; control_category is empty otherwise. Parameter values and changed IDs refer only to displayed confirmed parameters, with changed IDs also in values. Preserve nested schemas, stable IDs, bounds, options and exact UTF-16 source anchors.
- Current preview must reflect submitted edits deterministically. Accept applies to that exact reviewed version; edits or source changes invalidate old acceptance. Unstructured raw text edits are not hidden accepted control returns: L1/L2 re-analyze them before execution.
- One primary submit/Generate image-labeled decision is allowed but does not call generation. No approval checkbox or second confirmation, automatic acceptance, HTML, CSS, JavaScript, rendering or task calls.

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

Check current review evidence, parameter domains, conditional fields and mappings; load `l4-pN7-widget-renderer`. On invalid selection or missing indispensable evidence/capability, return `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, a nonempty deterministic `validation_errors` array identifying failed checks, and `return_to: l1-pN7-core-module`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 Router merges canonical state and emits `decision: end`. Every return/failure re-enters `l1-pN7-core-module`; acceptance is nonterminal evidence for a fresh L2 execution pass.
