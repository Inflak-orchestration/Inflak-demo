---
name: l3-pN4-inpaint-review
description: "Use when: P4 selects inpaint-image-compare to accept, retain, or revise a real inpaint candidate."
---

# L3 Designer — Inpaint Review

## Layer & Role

Design only `inpaint-image-compare` for `artifact-inpaint`, `inpaint_acceptance_gap`, `review_inpaint_candidate`. L3 Designer exposes attributable source/candidate comparison, not an executor or completion decision. Never select another widget, alter the images, compile a new edit or render.

Only Interaction Pathway enters L3: L1 → L2 gap + selection → L3 Designer → L4 Renderer → L1. Execution Pathway directly invokes the selected executor from L2 without L3/L4. Host Agent Return and Completion stay with L1 and do not enter this skill.

## Inputs

Read L2 `planner_id`, `selected_widget_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `expected_return`, `return_to`, and `display_context`. Resolve local registry and available runtime. Require real `before_ref`, `after_ref`, corresponding source/candidate identities and revisions; consume the actual applied prompt or rationale. Missing output is failure, not permission to show a fabricated preview.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Judge whether the scoped inpaint should be kept or revised. |
| Presented information | Show source and candidate pixel-aligned at the same fixed viewport size, clearly attributed to the applied local change. |
| Supported interaction | Before/after reveal and after/before/none decision with revision text. |
| Feedback and constraints | Left-to-right movement changes only the candidate clipping boundary over the source; it never resizes, zooms, reflows or transforms either image. Selected outcome and revision errors remain visible. |
| Submission and return | Return the decision and note exactly; no asset mutation or tool invocation. |
| Presentation intent | Image-led comparison with accessible keyboard reveal and inspectable source/candidate views. |

## Essential Constraints

- Validate exact ID, skill/path, planner, gap, goal, atomic edge, return coverage, artifact support, state target and runtime. Preserve `inpaint_image_compare`, `conversation_widget`, modality and capabilities.
- Preserve `chain_id`, binding `reason`, source/edge/target; edge source belongs to `source_nodes`, destination equals `state_update_target` (`A` for I→A acceptance, `Aug` for a selected I→Aug revision interpretation).
- Keep real source/candidate lineage, source aspect and current review context; no invented reference, outcome or acceptance. The comparison must not obscure unedited areas whose preservation matters.
- Require a true split reveal in one shared viewport: render the source and candidate as perfectly overlapping, equally sized layers with identical aspect ratio, object fit and object position. At 50%, the left half shows one version and the right half shows the other at the same scale and coordinates. The slider changes only a straight clipping boundary; it must not change either image's rendered width, height, scale, zoom, transform or layout.
- Return exactly `accepted_version` (after/before/none), `revision_request` (string), `freeform_note` (string). After accepts the candidate; before retains the actual original; none requires nonempty bounded revision text. L1 performs the merge and chooses subsequent routing.
- One primary submit action; no approval checkbox, automatic acceptance or second confirmation. Dismissal uses the existing envelope.
- No HTML, CSS, JavaScript, rendering, image tools or new revision planning inside L3.

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

Check actual references, reveal meaning and conditional serialization; load `l4-pN4-widget-renderer`. On invalid selection or missing indispensable evidence/capability, return `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, a nonempty deterministic `validation_errors` array identifying failed checks, and `return_to: l1-pN4-core-module`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 Router owns canonical state and emits `decision: end`. Every review return/failure re-enters `l1-pN4-core-module`; even accepted candidates remain nonterminal until L1 decides Completion.
