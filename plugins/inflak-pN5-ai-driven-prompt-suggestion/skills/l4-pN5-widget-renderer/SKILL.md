---
name: l4-pN5-widget-renderer
description: "Use when: rendering a P5 narrative_direction_cards or prompt_constellation Layer 3 contract and returning structured writer input to Layer 1."
---

# Layer 4 - P5 Widget Renderer

## Workflow End Boundary

After any widget return or renderer failure, immediately load `l1-pN5-core-module` with the structured result. Layer 4 never decides workflow completion, produces the final response, or continues directly to a planner or executor.

## Shared Style and Layout Policy

Use this local baseline without reading main or authoring contracts. Match host typography, neutral surfaces, spacing, borders, focus and control density using host `--iai-*` tokens/classes. Remain usable at 266px iframe width and desktop widths, use `minmax(0, 1fr)` and `min-width: 0` on shrinkable children, and prevent page-level `overflow-x` without clipping information. Confine necessary scrolling to an explicit region; keep labels/status/errors clear of controls. Avoid nested decorative cards or marketing copy.

Use native labeled controls, keyboard navigation, accessible icon names/tooltips and visible focus. Keep persistent submit/dismiss/reset actions reachable in `.iai-actions`; no confirmation checkbox, and checkboxes only for genuine multi-value boolean settings. Implement truthful disabled/loading/error/submitted states. Initialize from `window.widgetDisplay`, guard DOM/data lookups and current event state, and show recoverable inline errors. No parent DOM, storage, local files, secrets, undeclared network, remote code or modal APIs. Use only approved available capabilities/libraries.

## Role

Render a validated P5 Layer 3 semantic contract by generating sandboxed HTML/CSS/JS and calling exactly one render tool, `render_html_widget`. It is reached only through a fresh `L1 -> L2 -> L3` widget handoff. It never generates writing or calls task tools.

Only Interaction Pathway enters L4 Renderer: user/return → L1 → L2 gap + selection → L3 Designer → L4 render → L1. Execution Pathway directly invokes the active main model from L2 without L3/L4. Host Agent Return and Completion do not enter L4; only L1 emits `decision: "end"`.

Registry state_update_targets names business storage selected_directions/writing_constraints/confirmed_prompt. Validate those paths through L3 merge_strategy; semantic state_update_target equals I for G→I presentation or T for H→T/I→T, not a literal storage path. Preserve both meanings without changing registry paths.

## Inputs (self-contained)

Validate locally; no external schema read or success `handoff_type`:

- Identity: nonempty strings `selected_widget_id`, `widget_id`, `widget_type`, `surface`, `planner_id`, `purpose`, `interaction_goal`; preserve exact L2 selection/goal and local registry eligibility/type/surface. Type is `narrative_direction_cards` or `prompt_constellation`.
- `iai`: unchanged L2 `chain_id`, `gap_type`, binding `reason`, `maps_to_edge`, `source_nodes`, `target_node`; require named chain, meaningful reason, edge source in `source_nodes`, destination equal to `target_node` and allowed `state_update_target`, deterministic `merge_strategy`, and `next_planner_action: "re-enter Layer 1"`. Do not merge canonical state.
- `display`: actual task values, source references, current choices and unresolved status; resolve every profile content source. Never fabricate candidates, defaults, authorship or outcomes.
- `controls`: unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty `return_keys` limited to declared keys, and applicable `constraints` enforcing types, limits and source/edit rules.
- `presentation.profile`: nonempty `archetype`/`summary`, nonempty `content` records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`), nonempty supported `interaction.actions`/`feedback`, and `submission` with nonempty `label`, `preconditions`, `return_mapping`. Require nonempty semantic `appearance` and `signature_features` without new stages.
- `expected_return`: exactly L2 keys/types, with exactly the same keys in `presentation.profile.interaction.submission.return_mapping`; each mapping specifies actual source/serialization and declared optional/empty handling. Validate before submission; derived metadata needs mappings, not artificial controls.
- `widget_requirements`: four nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`; implement every item consistently with profile, controls and mappings.
- `safety`: `allow_html: false`, `allow_script: false` in L3 input; only L4 writes code. Optional `runtime` uses available approved capabilities/version-pinned libraries. Optional `reference_assets` are plugin-relative design-time principles, never runtime assets.

Missing/inconsistent semantics, unsafe input or unsupported capability returns structured renderer failure to `l1-pN5-core-module` before rendering without semantic repair. Compile requirements into existing renderer fields, not undocumented tool arguments; pass selected_widget_id, display, controls, planner_id, interaction_goal and expected_return unchanged.

## Procedure

1. Compile the Layer 3 semantic content into visible hierarchy, the interaction into controls and feedback, and the presentation profile into responsive grouping and appearance.
2. For `narrative_direction_cards`, preserve the seed prompt and all candidate fields. Enforce at most two supporting directions and require a primary choice only for `develop`.
3. For `prompt_constellation`, render only supplied facet groups; preserve `leave_open` choices, the editable prompt preview, and the action choices.
4. Use `window.submitWidget(values)` for valid returns and `window.dismissWidget(note)` for dismissal. Maintain the exact expected return shape.
5. Call `render_html_widget` once with `render_mode: "generated"`, copying `selected_widget_id` unchanged from Layer 3 into the renderer call, then return the structured result to `l1-pN5-core-module`. Use `selected_widget_id` only for registry trace/observability; it must not change widget UI semantics or select or replace a widget.

When a contract cites an image, read the complete host-supplied reference from `window.widgetDisplay` and assign only `window.widgetAssetUrl(ref)` to its image URL sink. Never use `.path` or `.url` directly, construct `file://`, or invent an asset id or remote image URL. Show an explicit unavailable state when the reference is absent.

## Stable Return Shapes

```json
{
  "narrative_direction_cards": {
    "primary_direction_id": "",
    "supporting_direction_ids": [],
    "rejected_direction_ids": [],
    "action": "develop|more_ideas|dismiss",
    "freeform_note": ""
  },
  "prompt_constellation": {
    "selected_facets": {},
    "custom_facets": {},
    "prompt_edits": "",
    "action": "continue|confirm|back_to_directions|dismiss",
    "freeform_note": ""
  }
}
```

## Must Not

- Do not call a task tool or main-model writing generation.
- Do not add a dedicated frontend template, host-page JavaScript, or external dependency.
- Do not send plugin reference assets or implementation instructions to the iframe.

## Next

After a widget return, control returns to `l1-pN5-core-module` for fresh routing.