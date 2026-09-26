---
name: l3-pN13-implementation-widget
description: "Use when: P13 selects its registered implementation widget to resolve material parameters, content, review, selection or spatial input for a confirmed recommendation."
---

# L3 Designer — P13 Implementation Widget

## Layer & Role

Interaction Pathway only: L1 → L2 gap + selection → L3 design → L4 render → L1. Design exact selection `p13-implementation-widget`, type `adaptive_implementation_widget`, surface `inline_widget`, for `pN13-proactive-intent-recommendation`. Its bounded operation modes preserve the useful copied interaction designs without loading ambiguous main skill names. This interaction gathers implementation evidence; it neither performs task execution nor promises capabilities absent from the runtime.

## Inputs

Read `planner_id`, `selected_widget_id`, `gap_type`, `interaction_goal`, named `chain_id`, `iai_binding`, exact typed `expected_return`, `return_to`, and actual runtime availability. Resolve the local registry entry. Require a confirmed recommendation and grounded `display_context` with one registered `implementation_mode`, current sources/items, revision, constraints and unresolved task need. L2 supplies intent and return fields, not a UI schema. Existing `implementation_widget_return` is evidence, not permission to reopen settled choices.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Explain how this confirmed action's missing parameter, selection, review, editable text or spatial evidence is supplied. |
| Presented information | Preserve current content, actual before/after versions, source assets, stable IDs and user/proposed/unresolved status; never invent previews. |
| Supported interaction | Specialize the single declared mode's operations; choose no new mode, task, source or execution action. |
| Feedback and constraints | Show numeric bounds, selection cardinality, source alignment, revision validity and actual local preview status. |
| Submission and return | Serialize the full declared structure, not a lossy option label; exact source-bound fields flow back as implementation evidence. |
| Presentation intent | Embody the operation with a focused editor, review, comparison, selector or spatial surface; do not reduce drawing/order/relations to generic confirmation. |

## Essential Constraints

- The goal/edge pair is exact: `refine_confirmed_implementation` uses `I→Aug`; `ground_confirmed_implementation` uses `I→A`. Never cross-combine the registry's goal and edge lists. Both resolve only `implementation_interaction_gap`.
- Validate exact selection, skill/path, planner, `implementation_interaction_gap`, registered goal/edge, all return keys, artifact support, runtime and renderer. Preserve named chain, binding reason and source/edge/target; `I→Aug` targets Aug and `I→A` targets A, also the allowed `state_update_target`. L1 alone stores declared values in `implementation_widget_return` and applies its deterministic merge.
- `planner_declared` permits exact domain fields only when the chosen registered mode can produce their types and shapes. Preserve IDs and full structures; do not add an `implementation_widget_return` wrapper to the user's values or load an archived recipe.
- Selection/review modes (`choice-cards`, `asset-selector`, `asset-review`, `claim-review`, `paper-evidence-selector`, `artifact-review`, `artifact-diff`, `image-compare`) preserve stable source/version/item IDs, selection cardinality and exclusive review decisions. Separate model relevance from user inclusion; unverified citations stay unverified. No fetching/ranking/asset creation occurs here.
- Parameter modes (`structured-form`, `rewrite-controls`, `continuous-controls`, `adjust-preview`, `color-palette`, `swatch-gallery`, `style-inspector`) preserve exact numeric values/bounds, full color lists, supported properties and serializable patches. Adjust previews are local illustrations, never baked output; swatches use grounded semantic descriptors, not remote assets or code.
- Structural modes (`draggable-board`, `order-stack`, `connection-map`, `align-distribute`) preserve complete order/group/edge sets over declared IDs; reject duplicate/lost IDs, invalid endpoints and forbidden cycles. Alignment needs at least two actual items and a bounded operation; execution computes geometry later.
- Spatial-parameter modes (`aspect-ratio-picker`, `crop-frame`, `crop-transform`, `nudge-pad`, `transform-inspector`) preserve stable source/item identity, source aspect and normalized coordinates independent of viewport. Enforce bounds, positive extents, declared rotation/flip/step/keep-aspect rules; never mutate original artifacts.
- Annotation modes (`region-annotator`, `sketch-pad`, `cutout-candidate-board`) retain source alignment and normalized regions or deterministic strokes. Actual exported refs require successful host upload; never fabricate a mask or cutout. Cutout requests are only reviewed requests, not extraction; mask semantics must match the intended operation, with transparent-edit/opaque-preserve for inpainting and no conversion to retention-mask semantics.
- Rich isolated modes (`composition-canvas`, `konva-canvas`, `gesture-surface`, `shortcut-surface`, `tldraw-canvas`) require the respective approved pinned `konva.js`, `interact.js`, `hotkeys-js`, or `tldraw` library actually available. Preserve deterministic scene patches/elements/items/commands/drawing snapshots over declared IDs; no parent document access. Require command buttons alongside shortcuts and an accessible non-drag alternative. Missing runtime fails to L1 without silent substitution.
- `rewrite-highlight-editor` returns the complete edited text, not only a diff; preserve valid selection offsets and selected text against that exact text, request scope, revision decision and local edits until submit. Do not force a new planner pass for each keystroke.
- Ground all options, versions, sources, defaults and capability claims. One primary submit, no approval checkbox or redundant confirmation; no HTML/CSS/JavaScript, remote implementation URLs, local runtime paths, task calls, artifact mutation or invented results.

## Output and Handoff

Pass a complete semantic contract using these eight local obligations; no success `handoff_type` or external schema read:

- Identity: nonempty `selected_widget_id` (exact selection), `widget_id` (instance), `widget_type`, `surface` (exact registry), `planner_id`, contextual `purpose`, unchanged `interaction_goal`.
- `iai`: copy named `chain_id`, `gap_type`, binding `reason`, `maps_to_edge`, `source_nodes`, `target_node` unchanged; require meaningful reason, edge source in sources and destination equal to target and allowed `state_update_target`. Include deterministic L1 `merge_strategy` and `next_planner_action: "re-enter Layer 1"`.
- `display`: grounded task values, actual source references, current values and unresolved status; no invented evidence, defaults, uploads, previews or outcomes.
- `controls`: records with unique nonempty `id`, supported `kind`, nonempty `label` and `purpose`, boolean `required`, nonempty declared `return_keys`, and `constraints` covering types, limits, source/edit rules.
- `presentation.profile`: nonempty `archetype`/`summary`; nonempty `content` records with resolvable `source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`; `interaction` with nonempty `actions`/`feedback` and `submission` containing nonempty `label`, nonempty `preconditions`, exact `return_mapping`; nonempty semantic `appearance` and `signature_features` list, not implementation or extra stages.
- `expected_return`: exactly L2's keys and types. `presentation.profile.interaction.submission.return_mapping` has exactly the same keys, each naming actual source and serialization; preserve optional/empty semantics and map derived metadata without artificial controls.
- `widget_requirements`: four nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`; minimal meaningful obligations consistent with the profile, not extra gates.
- `safety`: `allow_html: false`, `allow_script: false`. Optional `runtime` contains only available approved capabilities and version-pinned libraries; optional `reference_assets` are plugin-relative design-time references/principles, never runtime assets.

Validate references, mode-specific operations, controls, mappings and actual producible values, then send to `l4-pN13-widget-renderer`. Invalid selection or missing indispensable evidence/capability returns `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, and `return_to: l1-pN13-core-module`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 owns canonical state/merging and Completion or `decision: end`. All returns re-enter `l1-pN13-core-module`. Implementation input is nonterminal; L2 executes only after a fresh L1 route and evidence-backed readiness.