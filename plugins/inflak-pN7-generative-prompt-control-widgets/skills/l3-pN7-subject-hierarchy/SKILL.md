---
name: l3-pN7-subject-hierarchy
description: "Use when: P7 selects subject-hierarchy to assign visual roles to confirmed source-anchored entities."
---

# L3 Designer — Subject Hierarchy

## Layer & Role

Design only `subject-hierarchy` for `image-prompt-control`, `subject_priority_gap`, `set_subject_hierarchy` or declared `resolve_fine_grained_prompt_control`, on `I→Aug`. L3 Designer handles roles of known entities, not content candidates, composition, weights, final review, generation or rendering. Mismatch returns to L1 without substitution.

Only Interaction Pathway enters L3: L1 → L2 gap + selection → L3 Designer → L4 Renderer → L1. Execution Pathway directly invokes the selected executor/main_model from L2 without L3/L4. Host Agent Return and Completion stay with L1 and do not enter this skill.

Registry `state_update_targets` names business paths under `control_spec`, not a literal IAI-node allowlist. Preserve the selected entry's paths in `merge_strategy`; semantic `state_update_target` is Aug, the I→Aug destination. Never rename paths or store IAI node fields as business state.

## Inputs

Read L2 `planner_id`, `selected_widget_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `expected_return`, `return_to`, and `display_context`; resolve local registry/runtime. Require actual prompt_document.text and stable entity parameters with exact source spans and supplied role-control schemas. Preserve confirmed entity evidence; do not assign prominence in the user's absence.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Establish the primary subject and supporting/environmental context. |
| Presented information | Keep the complete fluent prompt and each full entity phrase visible. |
| Supported interaction | Assign exactly one role per supplied entity through its inline selector. |
| Feedback and constraints | Show primary status and block conflicting committed hierarchies. |
| Submission and return | Serialize roles by stable parameter ID with changed IDs, preview and note. |
| Presentation intent | Treat the entity phrase and attached control as one inline wrapping unit. |

## Essential Constraints

- Validate exact ID, skill/path, planner, gap, goal, edge, return coverage, artifact support, state target and runtime. Preserve `inline_prompt_parameter_editor`, `conversation_widget`, modality/capabilities.
- Preserve `chain_id`, binding `reason`, source/edge/target; source includes `I`, destination/state_update_target is `Aug`. L1's deterministic merge updates control_spec.subject_hierarchy and inline_parameters without changing other categories.
- Role values are primary/supporting/environment, one per entity. A committed hierarchy has exactly one primary; preserve only an explicitly supplied, evidenced single-entity primary default, never infer other values.
- UTF-16 span offsets must exactly slice parameter.text; spans are ordered, nonoverlapping and complete phrases. Repeated text must identify the intended occurrence. Preserve untouched prompt characters and source IDs; missing/stale ambiguous anchors fail.
- Keep complete original prompt fluent. Full entity phrase and its selector remain an atomic inline unit; never prescribe a detached table, list or role card. Preserve nested parameter control schema and compile_mode.
- Return exactly `parameter_values` (object), `changed_parameter_ids` (array), `compiled_prompt` (string), `freeform_note` (string). Values and changed IDs refer only to displayed supplied entities; changed IDs occur in values. Preview expresses current values but does not promise pixels or rewrite canonical T.
- One primary submit, no approval checkbox or second confirmation. No HTML, CSS, JavaScript, rendering, task calls or unsupported inferred roles.

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

Check entity spans, role cardinality and exact mappings; load `l4-pN7-widget-renderer`. On invalid selection or missing indispensable evidence/capability, return `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, a nonempty deterministic `validation_errors` array identifying failed checks, and `return_to: l1-pN7-core-module`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 Router merges canonical state and emits `decision: end`. Every return/failure re-enters `l1-pN7-core-module`; role choices are nonterminal evidence.
