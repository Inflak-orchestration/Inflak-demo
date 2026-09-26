---
name: l3-pN11-prompt-action-specificity-editor
description: "Use when: L2 selects a target-bound concrete P11 instruction editor."
---

# L3 Designer — Prompt Action Specificity

## Layer & Role

Design only `prompt-action-specificity-editor` / `prompt_action_specificity_editor` on `artifact_canvas_widget`. No diagnosis, substitution, rendering or execution.

## Inputs

Require L2 selection/planner/gap/goal, chain/binding, expected return, current artifact/revision, action `prompt_unit`, confirmed targets, compatible operations, current/proposed values, missing parameters and separate object-valued constraints.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Approve one complete target-bound instruction. |
| Presented information | Source action, visible target label/ID and concrete_instruction_preview. |
| Supported interaction | Edit supported operation/typed parameters/constraints; Approve instruction, edit or dismiss. |
| Feedback and constraints | Live readable preview states exactly what changes and stays preserved. |
| Submission and return | Map prompt unit, targets, operation, parameters, constraints and action. |
| Presentation intent | Automatically anchored to target without requiring a prior object click. |

## Essential Constraints

For every displayed color, populate `display.color_previews` from actual values and require L4 to render a visible swatch with an accessible label; preserve domain bindings. Raw code text (HEX/RGB) is auxiliary, never the primary or only color preview.

All proposed fields stay editable. Viewing, editing or prefill is not approval. One primary `Approve instruction` returns `selected_by_user` provenance; no aggregate prompt-enhancement review or second confirmation. Typical return values describe `prompt_unit_id`, `target_object_ids`, `operation`, `parameters`, `constraints`, `action: approve|edit|dismiss`; alternative serialization must preserve the same explicit target-bound decision evidence. Include every action/current/proposed color in `display.color_previews` as `{value,label,role,prompt_unit_id}` with swatches. Source stays read-only; no patch operations, invented values, custom code/selectors or export here.

Typical semantic return mapping (adapt keys to L2's current agent-interpreted interaction, retaining approval evidence):

| Return field | Type and source/serialization |
| --- | --- |
| prompt_unit_id | Nonempty string copied from the exact bound source action unit. |
| target_object_ids | String array of the source-bound confirmed stable targets; target corrections require L1 re-entry, not inferred replacements. |
| operation | String from the declared allowlisted operation control. |
| parameters | Object of typed values from the operation's declared controls; preserve numeric/boolean/string types, never JSON text. |
| constraints | Separate object from the declared constraint controls; `{}` only when no constraints are required. |
| action | String enum `approve`, `edit`, `dismiss` from the explicit command. |

Approve requires nonempty targets, supported operation and all required typed values. Edit/dismiss preserve declared unfinished/optional values and never grant approval. `selected_by_user` is provenance derived by L1 from the actual approve event and source-bound payload, not an extra return key or checkbox.

## Output and Handoff

Complete local contract; no external read or success `handoff_type`:

- Identity: nonempty exact `selected_widget_id`, instance `widget_id`, registry `widget_type`/`surface`, `planner_id`, contextual `purpose`, unchanged `interaction_goal`.
- `iai`: unchanged L2 `chain_id`, `gap_type`, `reason`, `source_nodes`, `maps_to_edge`, `target_node`; named chain/meaningful reason, edge source in sources, destination=target and allowed `state_update_target`; deterministic L1 `merge_strategy`; `next_planner_action: "re-enter Layer 1"`.
- `display`: actual source/revision/values/unresolved status; no invented evidence/defaults/assets/previews/outcomes; preserve `artifact_binding`/`placement`.
- `controls`: unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty declared `return_keys`, typed/limit/source/edit `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`, nonempty resolvable `content` records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`); nonempty interaction `actions`/`feedback`; submission nonempty `label`/`preconditions`/exact `return_mapping`; nonempty semantic `appearance`/`signature_features`.
- `expected_return`: under `return_mode: agent_interpreted`, preserve exactly L2 keys/types for this contextual interaction and identical mapping keys with actual source/serialization/optional-empty handling. Domain field names are guidance, not fixed registry keys; retain user evidence for L1 interpretation, no artificial metadata controls or inferred consent.
- `widget_requirements`: four nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`, consistent with profile, no extra gates.
- `safety`: `allow_html: false`, `allow_script: false`; optional `runtime` approved available capabilities/pinned libraries only; optional plugin-relative `reference_assets` design-time only.

Validate exact skill/path, planner/gap/goal/edge, returns/state/artifact/runtime. Send `l4-pN11-widget-renderer`. Failure: `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, `return_to: l1-pN11-core-module`; no L4/substitution.

## Workflow End Authority

All outcomes re-enter `l1-pN11-core-module`; only L1 merges state or emits `decision: end`. Approval returns to L1 before L2 performs Host checks and directly executes the approved action.
