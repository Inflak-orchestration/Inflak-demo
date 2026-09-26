---
name: l3-pN3-image-review
description: "Use when: P3 selects sketch-layout-image-compare to review an actual sketch-guided image candidate."
---

# L3 Designer — Sketch-Guided Image Review

## Layer & Role

Design only `sketch-layout-image-compare` for `sketch-layout-image-generation`, `generation_acceptance_gap`, `review_sketch_guided_image_candidate`. L3 Designer exposes the actual candidate for comparison; it neither commits an artifact, replans layout, renders nor executes image tools.

Only Interaction Pathway enters L3: L1 → L2 gap + selection → L3 Designer → L4 Renderer → L1. Execution Pathway directly invokes the selected executor from L2 without L3/L4. Host Agent Return and Completion stay with L1 and do not enter this skill.

## Inputs

Read L2 `planner_id`, `selected_widget_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `expected_return`, `return_to`, and `display_context`. Resolve local registry and runtime capabilities. Require real `before_ref` (sketch or prior accepted candidate), `after_ref` (current output), their lineage and current `compiled_brief`; consume actual legend/layout context. Missing generated output cannot be fabricated.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Judge whether the candidate follows the confirmed object layout. |
| Presented information | Co-present attributable sketch/prior image, candidate and brief context. |
| Supported interaction | Inspect both views; choose after, before, or none with bounded revision feedback. |
| Feedback and constraints | Make selection visible and require a revision request for none. |
| Submission and return | Return the exact decision/note fields, not a tool call or asset mutation. |
| Presentation intent | Image-led comparison with accessible alternatives to a reveal slider. |

## Essential Constraints

- Validate exact ID, skill/path, planner, gap, goal, edge, return coverage, supported artifacts, state target and runtime. Preserve `sketch_layout_image_compare`, `conversation_widget`, modality and capabilities.
- Preserve `chain_id`, binding `reason`, source/edge/target; for acceptance on `I→A`, source includes `I`, destination/state_update_target is `A`. A registered revision-focused `I→Aug` handoff retains `Aug`, never re-diagnose it.
- Preserve actual reference identities, labels, revisions and before/after lineage. Clearly distinguish a source sketch from a previously generated image; keeping a sketch is not evidence that final generation succeeded.
- Return exactly `accepted_version` (before/after/none), `revision_request` (string), `freeform_note` (string). After retains the candidate; before retains only the actual displayed prior artifact; none requires nonempty bounded layout feedback. L1 alone commits or routes.
- Do not silently change the reviewed brief or auto-select after. One primary submission, no approval checkbox or second confirmation. Dismiss uses the existing envelope.
- No HTML, CSS, JavaScript, rendering, prompt compilation, fabricated previews, or task calls.

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

Check references, lineage and conditional returns, then load `l4-pN3-widget-renderer`. On invalid selection or missing indispensable evidence/capability, return `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, a nonempty deterministic `validation_errors` array identifying failed checks, and `return_to: l1-pN3-core-module`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 Router owns canonical state and emits `decision: end`. Every review return/failure re-enters `l1-pN3-core-module`; acceptance is nonterminal until L1 decides Completion.
