---
name: l3-inflak-task-framing-board
description: "Use when: Author selects current-revision review of the inferred task boundary."
---

# L3 Designer — Task Framing Board

## Layer & Role

Interaction Pathway only: L1 → L2 selection → L3 design → L4 render → L1. Validate exact `inflak-task-framing-board` for `inflak-authoring`, `task_framing_gap`, `review_task_frame`, `G→I`. Design registered `task_framing_board` on `conversation_widget`; no diagnosis, substitution, execution or rendering.

## Inputs

Read `planner_id`, `selected_widget_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, exact `expected_return`, `return_to`, grounded context and actual runtime; resolve local registry. Consume current revision, target user, problem, starting input, outcome, success signals, exclusions, trust boundary and explicit/inferred assumptions. L2 supplies intent/evidence, not UI schema.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Inspect/edit the inferred task boundary before dependent workflow expansion. |
| Presented information | Prioritize problem/outcome, grounded input→collaboration→output and assumption provenance. |
| Supported interaction | Edit frame fields; approve or request meaningful changes without technical questions. |
| Feedback and constraints | Mark changes and unresolved substantive information without inventing approval. |
| Submission and return | Exact decision, complete edited frame, explicit assumption choices and changes. |
| Presentation intent | Compact framing board and meaningful flow/current phase, not a questionnaire. |

## Essential Constraints

- Validate ID, skill/path, planner/gap/goal/edge, returns, artifacts and runtime. Preserve chain/reason/source/edge/target; G is in sources, I is target and allowed `state_update_target`. L1 maps I to only the current frame/decision.
- Fixed returns: `decision` string, `task_frame` object, `confirmed_assumptions` array, `change_requests` array. Approval requires target user, problem, starting input, outcome and success signal. Request changes needs an edited field or nonempty request. Only explicit assumption choices count.
- Preserve revision and supplied evidence; no dependent-stage design or inferred approval. One primary submit, no approval checkbox/second confirmation. No HTML/CSS/JavaScript, local runtime paths, invented evidence, task calls or rendering.

## Output and Handoff

Use these eight local obligations; no success `handoff_type` or external schema read:

- Identity: nonempty exact `selected_widget_id`, instance `widget_id`, registry `widget_type`/`surface`, `planner_id`, contextual `purpose`, unchanged `interaction_goal`.
- `iai`: unchanged named `chain_id`, `gap_type`, binding `reason`, `maps_to_edge`, `source_nodes`, `target_node`; meaningful reason, source includes edge origin, destination equals target and allowed `state_update_target`; deterministic L1 `merge_strategy`, `next_planner_action: "re-enter Layer 1"`.
- `display`: grounded values, actual references, current state and unresolved status; no invented defaults/uploads/previews/outcomes.
- `controls`: unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty declared `return_keys`, type/limit/source/edit `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`, nonempty `content` records (resolvable `source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`); interaction nonempty `actions`/`feedback`, submission nonempty `label`/`preconditions`, exact `return_mapping`; nonempty semantic `appearance` and `signature_features` list, not extra stages/implementation.
- `expected_return`: exactly L2 keys/types; `presentation.profile.interaction.submission.return_mapping` has exactly those keys with actual source/serialization and optional/empty handling. Derived metadata needs mappings, not artificial controls.
- `widget_requirements`: four nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`; minimal meaningful obligations matching the profile, not extra gates.
- `safety`: `allow_html: false`, `allow_script: false`; optional runtime only available approved capabilities/pinned libraries; optional reference assets only plugin-relative design-time references/principles, never runtime assets.

Validate sources, constraints and producible exact mappings; send to `l4-inflak-author-renderer`. Invalid selection or missing indispensable evidence/capability returns `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, `return_to: l1-inflak-author-core`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 owns canonical merging and Completion or `decision: end`. Every return/failure re-enters `l1-inflak-author-core`; frame approval is nonterminal.
