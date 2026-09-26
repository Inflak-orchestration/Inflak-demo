---
name: l3-pN7-attention-weight-control
description: "Use when: P7 selects attention-weight-control for stronger or weaker visual priority on confirmed prompt units."
---

# L3 Designer — Attention Weight Control

## Layer & Role

Design only `attention-weight-control` for `image-prompt-control`, `attention_weight_gap`, `adjust_semantic_priority` or declared `resolve_fine_grained_prompt_control`, on `I→Aug`. L3 Designer collects intended visual emphasis, not measured model attention. It cannot choose entities, infer provider support, substitute widgets, compile final prompts, render or generate.

Only Interaction Pathway enters L3: L1 → L2 gap + selection → L3 Designer → L4 Renderer → L1. Execution Pathway directly invokes the selected executor/main_model from L2 without L3/L4. Host Agent Return and Completion stay with L1 and do not enter this skill.

Registry `state_update_targets` names business paths under `control_spec`, not a literal IAI-node allowlist. Preserve the selected entry's paths in `merge_strategy`; semantic `state_update_target` is Aug, the I→Aug destination. Never rename paths or store IAI node fields as business state.

## Inputs

Read L2 `planner_id`, `selected_widget_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `expected_return`, `return_to`, and `display_context`; resolve local registry/runtime. Require source-anchored confirmed parameters with supplied numeric bounds/step, current values and weight_mode. Consume actual provider capabilities and attention evidence only if supplied and available.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Express stronger/weaker emphasis for the exact confirmed unit. |
| Presented information | Keep source phrase, numeric value, neutral point, weight mode and preview visible. |
| Supported interaction | Adjust bounded slider/numeric value and restore the declared neutral value. |
| Feedback and constraints | Label provider-native versus semantic intent and validate bounds/steps. |
| Submission and return | Serialize numeric values, changed IDs, preview and note without claiming measured attention. |
| Presentation intent | Inline continuous adjustment tied to source text, never a detached technical panel. |

## Essential Constraints

- Validate exact ID, skill/path, planner, gap, goal, edge, returns, artifacts, state target and actual runtime. Preserve `inline_prompt_parameter_editor`, `conversation_widget`, modality/capabilities.
- Preserve `chain_id`, binding `reason`, source/edge/target; source includes `I`, destination/state_update_target is `Aug`. L1 merges control_spec.attention and inline_parameters by stable ID.
- Values are finite numeric values within supplied min/max/step; 1.0 is neutral. Do not impose sample bounds when none were actually supplied. Preserve weight_mode and nested control schema including compile_mode.
- `provider_native` requires documented supported weighting. Otherwise use `semantic_priority` as natural-language intent, never unsupported syntax or claims about diffusion attention. Attention visualization is available only with actual capability and evidence; do not invent measurements.
- Preserve exact UTF-16 source spans, complete phrases, ordered/nonoverlapping anchors and stable IDs; source slice equals parameter.text. Missing or ambiguous evidence fails rather than selecting a replacement.
- Return exactly `parameter_values` (object), `changed_parameter_ids` (array), `compiled_prompt` (string), `freeform_note` (string). IDs resolve to displayed parameters, changed IDs occur in values; preview reflects values without replacing canonical T or inventing provider compilation.
- One primary submit, no approval checkbox, forced adjustment or second confirmation. No HTML, CSS, JavaScript, render or task calls.

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

Check anchors, weight mode, numeric validity and exact mappings; load `l4-pN7-widget-renderer`. On invalid selection or missing indispensable evidence/capability, return `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, a nonempty deterministic `validation_errors` array identifying failed checks, and `return_to: l1-pN7-core-module`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 Router merges canonical state and emits `decision: end`. Every return/failure re-enters `l1-pN7-core-module`; weight submission is nonterminal intent, not a model result.
