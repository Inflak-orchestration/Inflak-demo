---
name: l3-inflak-workflow-step-designer
description: "Use when: Author selects one stable stage's agency, work, checkpoint, progress and transition review."
---

# L3 Designer — Workflow Step Designer

## Layer & Role

Interaction Pathway only: L1 → L2 selection → L3 design → L4 render → L1. Validate `inflak-workflow-step-designer` for `inflak-authoring`, `workflow_substep_gap`, `review_workflow_substep`, `G→I`. Design registered `workflow_step_designer` on `conversation_widget`; no diagnosis, substitution, execution or rendering.

## Inputs

Read `planner_id`, `selected_widget_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, exact `expected_return`, `return_to`, actual runtime and local registry. Require one stable stage/current revision, purpose, entry/dependencies, user information/work, AI work, autonomy/checkpoint, progress, intermediate artifacts/state, completion, next/failure path. L2 supplies domain intent, not controls.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Resolve the supplied uncertainty for exactly one stage, not the whole workflow. |
| Presented information | Actual stage progress/context, user/AI/shared work, checkpoint and artifact roles. |
| Supported interaction | Edit that stage's information/work/autonomy/checkpoint and progress/artifacts; approve, revise or clarify. |
| Feedback and constraints | Mark changed lane items and checkpoint consequences while preserving identity/dependencies. |
| Submission and return | Same stable stage ID, patch, decision, checkpoint policy, artifact changes and note. |
| Presentation intent | One readable swimlane stage with artifact/transition anchors and narrow-width stacking. |

## Essential Constraints

- Validate exact ID, skill/path, planner/gap/goal/edge, returns, artifacts and runtime. Preserve chain/reason/source/edge/target; G in sources, I target and allowed `state_update_target`. L1 merges only matching stage/current-revision decision.
- Fixed returns: `stage_id`, `decision`, `freeform_note` strings; `stage_patch`, `checkpoint_policy` objects; `artifact_changes` array. Approval requires purpose, actor/work, entry, completion, next/failure and explicit checkpoint policy. `needs_clarification` requires one focused ambiguity. Changes never approve other stages.
- Preserve reads/writes, IDs and local edits until submit. One primary action; no approval checkbox/second confirmation. No whole-workflow redesign, HTML/CSS/JavaScript, local runtime paths, invented evidence, task calls or rendering.

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

Validate evidence, controls and exact producible mappings; send to `l4-inflak-author-renderer`. Invalid selection or missing indispensable evidence/capability returns `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, `return_to: l1-inflak-author-core`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 owns canonical merging/invalidation and Completion or `decision: end`. Every return/failure re-enters `l1-inflak-author-core`; stage approval is nonterminal.
