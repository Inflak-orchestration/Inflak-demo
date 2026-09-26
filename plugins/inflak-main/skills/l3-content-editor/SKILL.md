---
name: l3-content-editor
description: "Use when: Layer 2 selected content-editor to refine prompt content."
---

# L3 Designer — Content Editor

## Layer & Role

L3 Designer handles interaction design only on Interaction Pathway: L2 gap + selection → L3 interaction design → L4 render → L1. Design L2's exact `selected_widget_id: content-editor` as a source-preserving semantic widget profile.
Specialize the supplied goal and task context; never diagnose another gap or select another widget.
L3 designs meaningful editing operations; L4 implements the interface without expanding their scope.

## Inputs

- Read `planner_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `expected_return`, and `return_to` from L2.
- Resolve the exact widget registry entry, planner eligibility, and actual runtime capabilities.
- Read source content, stable content-unit IDs, authored/proposed status, provenance, and unresolved information.
- Respect supplied editing permissions, protected content, and substantive task constraints.
- Derive supported controls, labels, grouping, and permitted edit scope from intent and evidence; L2 need not design fields.
- Distinguish legitimate interaction design from missing source facts that cannot be fabricated.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Explain what content the user can refine to resolve the existing goal without rewriting settled material. |
| Presented information | Show relevant source context and content units, distinguishing authored, proposed, unresolved, and user-edited state. |
| Supported interaction | Select edit, add, remove, or reorder operations dynamically within evidenced permissions and primitive capabilities. |
| Feedback and constraints | Identify changed units and invalid edits while keeping original provenance and protected content intact. |
| Submission and return | Serialize the required content units and metadata into exactly L2's return keys, preserving unchanged material. |
| Presentation intent | Focus attention on editable content while making source context, unit identity, and edit status accessible. |

## Essential Constraints

- Validate exact ID, skill/path, planner, gap, goal, edge, return coverage, artifact support, state target, and runtime availability.
- Keep registered type, surface, modality, and capabilities unchanged; do not broaden routing eligibility.
- Preserve `chain_id` and `iai_binding.reason` unchanged in `iai.chain_id` and `iai.reason`.
- Preserve `source_nodes`, `maps_to_edge`, and `target_node` unchanged; pending input is not authored content.
- Require the edge source in `source_nodes` and its destination in `target_node`; `state_update_target` identifies that destination.
- Preserve authored text verbatim unless the user edits it within the permitted scope.
- Preserve stable IDs, original authored/proposed status, and provenance independently of later user-edit state.
- Keep unchanged units and supplied metadata in the return; do not silently reduce complete units to text fragments.
- Derive only the operations needed for this goal; broader primitive capabilities do not authorize unrestricted editing.
- If addition is permitted, define unique stable identities and truthful user-added provenance without preauthoring missing facts.
- Removal or reordering must respect protected content and the meaning of unit order; never silently discard content.
- Ground domain facts, actual options, source assets, and references; fabricate no uploads, previews, or final outcomes.
- Choose concrete return keys and types from L2's `expected_return`; define source-preserving edit serialization.
- Use one primary submission of the current revision; no approval checkbox, forced edit, or second confirmation step.
- Do not impose fixed controls or stages, generate the final artifact, render, execute the task, or embed implementation code.

## Output and Handoff

Pass a complete semantic contract using this local definition; do not add a success `handoff_type` or require an external document read:

- Identity: nonempty strings `selected_widget_id` (exact L2 selection), `widget_id` (instance identity), `widget_type` and `surface` (exact registry values), `planner_id` (owning L2), `purpose` (contextual), and unchanged `interaction_goal`.
- `iai`: copy L2's `chain_id`, `gap_type`, and binding `reason`, `maps_to_edge`, `source_nodes`, `target_node` unchanged; require a named chain and meaningful reason, edge source in `source_nodes`, and destination equal to `target_node` and allowed `state_update_target`. Include a deterministic `merge_strategy` for L1 and `next_planner_action: "re-enter Layer 1"`.
- `display`: grounded task values, source references, current values, and unresolved status; no invented evidence, defaults, uploads, previews, or outcomes.
- `controls`: array of records with `id`, `kind`, `label`, `purpose`, `required`, `return_keys`, `constraints`; IDs are unique/nonempty, kinds supported, labels/purposes nonempty, `required` boolean, and `return_keys` a nonempty list of declared return keys. State applicable limits, types, and source/edit rules in `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`, a nonempty `content` array of records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`); every source resolves. Include `interaction` with nonempty `actions`/`feedback` lists and `submission` (nonempty `label`, nonempty `preconditions`, `return_mapping`), plus nonempty semantic `appearance` and a nonempty `signature_features` list describing relevant behavior, not implementation or invented steps.
- `expected_return`: deterministic object with exactly L2's keys and types; `presentation.profile.interaction.submission.return_mapping` has exactly the same keys, each specifying its actual source and serialization. Preserve declared optional/empty semantics; derived returns need mappings, not artificial controls.
- `widget_requirements`: four nonempty string arrays, `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`; state minimal meaningful obligations consistent with the profile, not additional interaction gates.
- `safety`: `allow_html: false`, `allow_script: false`. Optional `runtime` declares only available approved capabilities and version-pinned libraries; optional `reference_assets` are plugin-relative design-time references and extracted principles only, never runtime assets.

Check source references, stable IDs, edit scope, provenance preservation, and lossless serialization before handoff.
Then load `l4-widget-renderer` with the complete design; do not leave semantic editing decisions to L4.
On invalid selection or missing indispensable evidence/capability, return `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, a nonempty deterministic `validation_errors` array identifying failed checks, and `return_to: l1-router`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 Router owns canonical workflow state and may choose Completion or emit `decision: end`.
Every widget return or failure returns to `l1-router`; a submitted revision is nonterminal.
L1 maps returned values into canonical state at the preserved destination; L3 never declares workflow completion.
