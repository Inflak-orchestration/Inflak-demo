---
name: l3-pN7-composition-allocation
description: "Use when: P7 selects composition-allocation for approximate relative frame shares among confirmed entities."
---

# L3 Designer — Composition Allocation

## Layer & Role

Design only `composition-allocation` for `image-prompt-control`, `composition_allocation_gap`, `allocate_composition` or declared `resolve_fine_grained_prompt_control`, on `I→Aug`. L3 Designer handles semantic frame share, not pixel coordinates, entity choice, hierarchy, weights, final review, execution or rendering. Mismatch returns to L1 without substitution.

Only Interaction Pathway enters L3: L1 → L2 gap + selection → L3 Designer → L4 Renderer → L1. Execution Pathway directly invokes the selected executor/main_model from L2 without L3/L4. Host Agent Return and Completion stay with L1 and do not enter this skill.

Registry `state_update_targets` names business paths under `control_spec`, not a literal IAI-node allowlist. Preserve the selected entry's paths in `merge_strategy`; semantic `state_update_target` is Aug, the I→Aug destination. Never rename paths or store IAI node fields as business state.

## Inputs

Read L2 `planner_id`, `selected_widget_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `expected_return`, `return_to`, and `display_context`; resolve local registry/runtime. Require prompt_document.text and confirmed entity parameters with stable IDs, exact spans and numeric domain schemas. Consume negative_space only when supplied; no invented entity or default allocation.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Balance the intended relative frame share of actual entities. |
| Presented information | Show each complete source phrase with a relative frame-share slider, readable less/more endpoints, its current value and live allocation feedback. Values express approximate intended frame share, not percentages of a fixed budget or image-generation attention weights. Preserve a readable prompt preview without inventing geometry or provider syntax. |
| Supported interaction | Use keyboard-accessible sliders as the primary inline controls, not numeric-input-only editing; retain supplied IDs, bounds, steps and values. Adjust each supplied parameter independently; never redistribute other values or require a total of 100. |
| Feedback and constraints | Update the selected value and allocation feedback immediately while dragging or using the keyboard. Validate finite values, individual bounds and steps only; no total-based error or submission gate, silent normalization or automatic rebalancing. Keep phrases, sliders, values and previews readable without overlap or clipping at 266px and desktop widths; wrap locally with content-driven height. Keep parameter groups unframed, with visible focus only on the active control. Carry these requirements into presentation.profile and widget_requirements for Layer 4. |
| Submission and return | Serialize actual relative allocation values by stable ID with changed IDs, preview and note; never convert them into normalized percentages. |
| Presentation intent | Prompt-anchored relative-share sliders, not a mandatory 100-percent budget, attention-weight editor or spatial layout canvas. |

## Essential Constraints

- Validate exact ID, skill/path, planner, gap, goal, edge, returns, artifacts, state target and runtime. Preserve `inline_prompt_parameter_editor`, `conversation_widget`, modality/capabilities.
- Preserve `chain_id`, binding `reason`, source/edge/target; source includes `I`, destination/state_update_target is `Aug`. L1 merges control_spec.composition and inline_parameters deterministically.
- Values are finite relative frame-share numbers within supplied min/max/step. A supplied 0..100 range is a slider scale, not a percentage budget; there is no required sum. Never rebalance, normalize, reject or block submission based on the combined total. Conflicting scene intent returns for L1/L2 reasoning rather than a fabricated fallback.
- Preserve negative_space only when declared. Relative frame shares express approximate composition intent, not exact boxes, pixel guarantees, patches or attention weights. L2 supplies slider-compatible numeric schemas with relative-share units, not percent units or fixed-total constraints; inconsistent schemas return to L1 rather than being silently reinterpreted. Preserve parameter control type/label/min/max/step/unit/compile_mode.
- UTF-16 source spans must exactly slice parameter.text; preserve stable IDs, complete phrases, ordered nonoverlapping spans and source provenance. Stale/ambiguous anchors fail.
- Return exactly `parameter_values` (object), `changed_parameter_ids` (array), `compiled_prompt` (string), `freeform_note` (string). IDs belong to supplied parameters and changed IDs occur in values. Preview is not canonical Aug→T conversion or provider-specific compilation.
- One primary submit, no confirmation checkbox or second approval. No HTML, CSS, JavaScript, rendering or task calls.

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

Check spans, individual numeric bounds/steps and exact mappings; load `l4-pN7-widget-renderer`. On invalid selection or missing indispensable evidence/capability, return `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, a nonempty deterministic `validation_errors` array identifying failed checks, and `return_to: l1-pN7-core-module`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 Router merges canonical state and emits `decision: end`. Every return/failure re-enters `l1-pN7-core-module`; allocations are nonterminal evidence, not generated geometry.
