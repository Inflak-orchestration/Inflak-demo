---
name: l3-pN1-prompt-review
description: "Use when: P1 selects prompt-review to confirm, re-refine, or edit the current image prompt."
---

# L3 Designer — Prompt Review

## Layer & Role

Design only L2's exact `prompt-review` selection for `image-prompt-refinement`, `prompt_confirmation_gap`, `confirm_prompt`, on `I→T`. Interaction Pathway is L2 selection → L3 Designer → L4 Renderer → L1 Router. An unrelated gap fails validation; never substitute a widget, rewrite the prompt, or execute generation.

Only Interaction Pathway enters L3: L1 → L2 gap + selection → L3 Designer → L4 Renderer → L1. Execution Pathway directly invokes the selected executor/main_model from L2 without L3/L4. Host Agent Return and Completion stay with L1 and do not enter this skill.

## Inputs

Read L2 `planner_id`, `selected_widget_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `expected_return`, `display_context`, and exact `return_to`. Resolve the selected local registry entry and actual runtime capabilities. Require exact current prompt text and review context; consume optional previous prompt and grounded change summary. Missing text is not a ready review.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Accept the current prompt, request refinement, or supply a manual edit. |
| Presented information | Prioritize exact current text; compare previous text only when provided. |
| Supported interaction | Select accept, refine, or edit; expose editing within supplied scope. |
| Feedback and constraints | Make outcome clear; require nonempty edited text for edit. |
| Submission and return | Serialize decision, conditional edited text, and note without generating. |
| Presentation intent | Keep prompt and decision together with accessible comparison/edit state. |

## Essential Constraints

- Validate exact ID, skill/path, planner, gap, goal, edge, return coverage, artifact support, state destination and runtime availability. Preserve registered type `prompt_review`, surface `conversation_widget`, modality and capabilities.
- Preserve `chain_id`, binding `reason`, `source_nodes`, `maps_to_edge` and `target_node`; edge source belongs to `source_nodes`, destination and `state_update_target` are `T`.
- Return exactly `action` (accept/refine/edit), `edited_prompt` (string), `freeform_note` (string). Keep empty edited text outside edit; never omit declared keys or invent acceptance.
- Acceptance binds to displayed current text. Edits invalidate stale acceptance; refinement retains text as context. L1 merges evidence before a new L2 preparation/execution pass.
- One primary submit action; no confirmation checkbox, forced edit, second approval step, HTML, CSS, JavaScript, rendering, or task calls. Dismiss via the existing envelope.

## Output and Handoff

Pass a complete semantic contract using this local definition; no success `handoff_type` or external document read:

- Identity: nonempty strings `selected_widget_id` (exact L2 selection), `widget_id` (instance identity), `widget_type` and `surface` (exact registry values), `planner_id` (owning L2), `purpose` (contextual), and unchanged `interaction_goal`.
- `iai`: copy L2's `chain_id`, `gap_type`, and binding `reason`, `maps_to_edge`, `source_nodes`, `target_node` unchanged; require a named chain and meaningful reason, edge source in `source_nodes`, and destination equal to `target_node` and allowed `state_update_target`. Include a deterministic `merge_strategy` for L1 and `next_planner_action: "re-enter Layer 1"`.
- `display`: grounded task values, source references, current values, and unresolved status; no invented evidence, defaults, uploads, previews, or outcomes.
- `controls`: array of records with `id`, `kind`, `label`, `purpose`, `required`, `return_keys`, `constraints`; IDs are unique/nonempty, kinds supported, labels/purposes nonempty, `required` boolean, and `return_keys` a nonempty list of declared return keys. State applicable limits, types, and source/edit rules in `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`, a nonempty `content` array of records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`); every source resolves. Include `interaction` with nonempty `actions`/`feedback` lists and `submission` (nonempty `label`, nonempty `preconditions`, `return_mapping`), plus nonempty semantic `appearance` and a nonempty `signature_features` list describing relevant behavior, not implementation or invented steps.
- `expected_return`: deterministic object with exactly L2's keys and types; `presentation.profile.interaction.submission.return_mapping` has exactly the same keys, each specifying its actual source and serialization. Preserve declared optional/empty semantics; derived returns need mappings, not artificial controls.
- `widget_requirements`: four nonempty string arrays, `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`; state minimal meaningful obligations consistent with the profile, not additional interaction gates.
- `safety`: `allow_html: false`, `allow_script: false`. Optional `runtime` declares only available approved capabilities and version-pinned libraries; optional `reference_assets` are plugin-relative design-time references and extracted principles only, never runtime assets.

Validate current text, conditional serialization and profile sources, then load `l4-pN1-widget-renderer`. On invalid selection or missing indispensable evidence/capability, return `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, a nonempty deterministic `validation_errors` array identifying failed checks, and `return_to: l1-pN1-core-module`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 Router owns canonical state and emits `decision: end`. Every widget return or failure re-enters `l1-pN1-core-module`. Prompt acceptance is nonterminal evidence, not generation or Completion.
