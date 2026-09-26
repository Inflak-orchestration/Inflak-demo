---
name: l3-inflak-artifact-flow-map
description: "Use when: Author selects artifact/state lifecycle review grounded in confirmed workflow stages."
---

# L3 Designer — Artifact and State Flow Map

## Layer & Role

Interaction Pathway only: L1 → L2 selection → L3 design → L4 render → L1. Validate `inflak-artifact-flow-map` for `inflak-authoring`, `artifact_flow_gap`, `review_artifact_state_flow`, `G→I`. Design registered `artifact_state_flow_map` on `conversation_widget`; no diagnosis, substitution, execution or rendering.

## Inputs

Read `planner_id`, `selected_widget_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, exact `expected_return`, `return_to`, actual runtime/local registry and grounded context. Consume current revision, approved stage reads/writes, stable nodes/edges, visibility, retention, revision binding and invalidation. IDs remain metadata; show meaningful artifact names. L2 need not supply UI schema.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Review what enters, changes, remains visible, becomes stale and is delivered. |
| Presented information | Ground input/intermediate/decision/status/final nodes and dependencies in approved stages. |
| Supported interaction | Inspect/edit lifecycle properties, relationships and meaningful intermediate artifacts. |
| Feedback and constraints | Show invalid endpoints, revision-loop meaning and downstream invalidation; distinguish final artifacts. |
| Submission and return | Serialize full nodes/edges and explicit visibility changes with decision/note. |
| Presentation intent | Connected lifecycle graph and focused inspector with a readable narrow-width alternative. |

## Essential Constraints

- Validate ID, skill/path, planner/gap/goal/edge, returns, artifacts and runtime. Preserve chain/reason/source/edge/target; G in sources, I target and allowed `state_update_target`. L1 maps I to `artifact_model`/decision and derives canonical state, not L3.
- Fixed returns: `decision`, `freeform_note` strings; `artifact_nodes`, `artifact_edges`, `state_visibility_changes` arrays. Approval requires input/final artifact, meaningful intermediate/status for multistage work, valid endpoints and lifecycle metadata per node. Cycles require explicit revision-loop meaning.
- Preserve stable IDs/revision, never invent lineage or ask authors for variable names. One primary submit; no approval checkbox/second confirmation. No target-widget choice, HTML/CSS/JavaScript, local runtime paths, task calls or rendering.

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

Validate graph consistency, source references and exact mappings; send to `l4-inflak-author-renderer`. Invalid selection or missing indispensable evidence/capability returns `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, `return_to: l1-inflak-author-core`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 owns canonical merging and Completion or `decision: end`. Every return/failure re-enters `l1-inflak-author-core`; graph approval is nonterminal.
