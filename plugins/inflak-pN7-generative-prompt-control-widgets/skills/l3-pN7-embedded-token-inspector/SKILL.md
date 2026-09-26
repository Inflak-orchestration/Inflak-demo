---
name: l3-pN7-embedded-token-inspector
description: "Use when: P7 selects embedded-token-inspector for a concrete entity, attribute, relation, style or exclusion decision."
---

# L3 Designer — Embedded Token Inspector

## Layer & Role

Design only `embedded-token-inspector` for `image-prompt-control`, `entity_scope_gap`, `resolve_embedded_prompt_token` or the declared parent goal `resolve_fine_grained_prompt_control`, on `I→Aug`. L3 Designer designs inline parameter editing, not hierarchy/weights, new candidates, final prompt compilation, task execution or rendering. A mismatch returns to L1 without substitution.

Only Interaction Pathway enters L3: L1 → L2 gap + selection → L3 Designer → L4 Renderer → L1. Execution Pathway directly invokes the selected executor/main_model from L2 without L3/L4. Host Agent Return and Completion stay with L1 and do not enter this skill.

Registry `state_update_targets` names business paths under `control_spec`, not a literal IAI-node allowlist. Preserve the selected entry's paths in `merge_strategy`; semantic `state_update_target` is Aug, the I→Aug destination. Never rename paths or store IAI node fields as business state.

## Inputs

Read L2 `planner_id`, `selected_widget_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `expected_return`, `return_to`, and `display_context`. Resolve local registry and runtime. Require actual prompt_document.text and parameters with stable `id`, exact `span`, `text`, `kind`, and supplied domain options/constraints. Each candidate-bearing parameter has 3–5 concrete choices, including exact current text labeled Keep current. Missing candidates are not invented in L3.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Resolve a precise content/exclusion value without changing unrelated intent. |
| Presented information | Text accuracy, complete readability and a usable full prompt preview take precedence over compactness and decoration. Preserve the original source text, including punctuation and spacing, and exact phrase anchors; distinguish source text, option labels and actual replacement values. Keep controls anchored at their source phrases, but do not append replacement text or status words as if they were part of the source sentence. Show the complete selected replacement in a clearly associated local detail area below its control when it cannot fit beside it; never rely solely on a clipped select label or hover tooltip. Always show a separate, readable full prompt preview, initially and after every accepted edit or reset, deterministically rebuilt from the original source, validated spans, current values and supplied replace_template. Its text must equal submitted compiled_prompt, with no labels, status words or visual annotations serialized. |
| Supported interaction | Select supplied values or type custom text only when permitted. For color parameters with supplied concrete color values, prefer a labeled swatch palette; for supplied multi-color themes, use compact selectable theme cards showing their actual swatches and full names. Keep these choices locally anchored to the source phrase within the same embedded editor, not a different registry widget. Preserve candidate IDs, values, Keep current and return mappings. Permit a custom color picker only when the declared schema accepts custom color values. If concrete color data is absent, retain labeled text choices rather than inventing swatches. |
| Feedback and constraints | Treat missing, overlapping, obscured or clipped source/replacement/preview text and stale previews as unacceptable at both 266px and desktop widths, including the longest supplied values and multiple changed parameters. Allow source phrases, replacement details and preview text to wrap with sufficient vertical space; inline anchoring does not require a single unbroken row. Move details and status indicators below their associated control when space is insufficient; never force them onto one line, overlap neighboring content, hide overflow or shrink text to make them fit. Keep every phrase-control-detail group unframed in all states: no enclosing border, outline or box shadow, whether solid, dashed or dotted. Distinguish modified state with subtle emphasis and a compact non-color-only indicator in its own space; retain visible keyboard focus only on the active control, never the enclosing group. Swatches and theme choices need readable names, keyboard selection and a non-color-only selected indicator. Distinguish exclusions from positive content. Identify corresponding preview changes without moving focus or unexpectedly scrolling. Keep current restores that source phrase and clears its indicator without discarding other edits. Carry these readability, unframed-group, color-choice and preview acceptance requirements into presentation.profile and widget_requirements for Layer 4. |
| Submission and return | Serialize actual parameter values, changed IDs, deterministic preview and note. |
| Presentation intent | Controls stay inline at their source phrase, never detached role-only cards. |

## Essential Constraints

- Validate exact ID, skill/path, planner, gap, goal, edge, returns, artifact support, state destination and runtime. Preserve `inline_prompt_parameter_editor`, `conversation_widget`, modality/capabilities.
- Preserve `chain_id`, binding `reason`, source/edge/target; source includes `I`, destination/state_update_target is `Aug`. L1 merges entity/attribute/relation/style values into control_spec.entities and exclusions into control_spec.exclusions, retaining inline_parameters by ID.
- Span offsets are JavaScript UTF-16 indices: each source slice equals parameter.text exactly. Spans are ordered/nonoverlapping and identify complete intended phrases, including correct repeated-text occurrence. Preserve IDs and original source provenance; stale/ambiguous anchors fail, not silent rewriting.
- Preserve nested parameter control schemas (`type`, `label`, `value`, `options`, `allow_custom_value`, `replace_template`) independently of canonical top-level controls. Options have stable id, visible label and concrete value; no empty, ID-only, role-only or minor-paraphrase substitutes. Custom text is allowed only when declared.
- Return exactly `parameter_values` (object keyed by supplied IDs), `changed_parameter_ids` (array of changed supplied IDs also present in values), `compiled_prompt` (string), `freeform_note` (string). Preserve other accepted values; deterministic text replacement uses supplied replace_template. Preview is not a hidden Aug→T rewrite or final provider compilation.
- No invented current/default choice, candidate or source fact. One primary submit, no confirmation checkbox, forced edits or second approval. No HTML, CSS, JavaScript, rendering or task calls.

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

Check spans, concrete candidates, preserved domain schema and exact mappings; load `l4-pN7-widget-renderer`. On invalid selection or missing indispensable evidence/capability, return `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, a nonempty deterministic `validation_errors` array identifying failed checks, and `return_to: l1-pN7-core-module`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 Router merges canonical state and emits `decision: end`. Every return/failure re-enters `l1-pN7-core-module`; parameter submission is not generation or Completion.
