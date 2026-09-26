---
name: l3-pN12-refinement-control
description: "Use when: L2 selects P12 typed controls over a reversible preview."
---

# L3 Designer — Refinement Control

## Layer & Role

Design only `refinement-control` / `refinement_control` on `artifact_canvas_widget`. No diagnosis, substitution, rendering or execution.

## Inputs

L2 selection/planner/gap/goal, chain/binding, exact return; artifact/revision, interaction_spec, default or user-corrected stable targets, capabilities, preview operations and declared typed values.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Adjust a concrete generated result using compatible controls. |
| Presented information | Current preview, targets, operation summary and revision. |
| Supported interaction | Spec-declared transform/alignment/layer/text/presentation controls, Apply/adjust/regenerate/reject/dismiss. |
| Feedback and constraints | Host-owned reversible preview and typed validation. |
| Submission and return | Only Apply makes complete declared operations patch-ready. |
| Presentation intent | Contextual direct manipulation, not a fixed transform or approval form. |

## Essential Constraints

For every displayed color, populate `display.color_previews` from actual values and require L4 to render a visible swatch with an accessible label; preserve domain bindings. Raw code text (HEX/RGB) is auxiliary, never the primary or only color preview.

Preserve generated values not explicitly changed. Operations must be spec previews plus declared adjustments matching planner allowlists/schemas; no inferred missing parameters. Return exact `interaction_id`, `artifact_id`, `base_revision`, `operations`, `control_values`, `action: apply|adjust|regenerate|reject|dismiss`. Other actions never authorize mutation. Colors use `display.color_previews` `{value,label,role,interaction_id}` with visible swatches. Preserve L2 edge/state unchanged; no SVG/CSS/selectors/path/external content or iframe patch.

Fixed mapping: `interaction_id: string` from the active spec; `artifact_id: string` and `base_revision: positive integer` from its bound current artifact; `operations: object[]` from complete spec previews plus explicit declared adjustments; `control_values: object` from actual typed controls; `action: string enum apply/adjust/regenerate/reject/dismiss` from the command. Copy metadata unchanged with no extra controls; arrays/objects stay JSON arrays/objects. Preserve declared optional/empty values on non-Apply returns; Apply requires nonempty supported operations and all required values at the exact current revision. No extra return keys or inferred authorization.

## Output and Handoff

Eight local parts; no external read/success `handoff_type`:

- Identity: nonempty exact `selected_widget_id`, instance `widget_id`, registry `widget_type`/`surface`, `planner_id`, contextual `purpose`, unchanged `interaction_goal`.
- `iai`: unchanged L2 `chain_id`, `gap_type`, `reason`, `source_nodes`, `maps_to_edge`, `target_node`; named chain/meaningful reason, edge source in sources, destination=target and allowed `state_update_target`; deterministic L1 `merge_strategy`, `next_planner_action: "re-enter Layer 1"`.
- `display`: actual sources/revisions/values/unresolved status; no invented evidence/defaults/assets/previews/outcomes; preserve `artifact_binding`/`placement`.
- `controls`: unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty declared `return_keys`, typed/limit/source/edit `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`; nonempty resolvable `content` records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`); nonempty interaction `actions`/`feedback`; submission nonempty `label`/`preconditions`/exact `return_mapping`; nonempty semantic `appearance`/`signature_features`.
- `expected_return`: exactly L2 keys/types and identical mapping keys, actual source/serialization/optional-empty handling; no artificial metadata controls.
- `widget_requirements`: four nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`, consistent with profile, no extra gates.
- `safety`: `allow_html: false`, `allow_script: false`; optional `runtime` approved available capabilities/pinned libraries only; optional plugin-relative `reference_assets` design-time only.

Validate exact skill/path/planner/gap/goal/edge/returns/state/artifact/runtime. Send `l4-pN12-widget-renderer`. Failure: `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, `return_to: l1-pN12-core-module`; bypass L4 without substitution.

## Workflow End Authority

All outcomes to `l1-pN12-core-module`; only L1 merges state or emits `decision: end`.
