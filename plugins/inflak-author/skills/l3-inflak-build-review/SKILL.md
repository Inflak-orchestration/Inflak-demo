---
name: l3-inflak-build-review
description: "Use when: Author selects actual immutable preview hash/readiness/risk review or required scenario failure review."
---

# L3 Designer — Plugin Build Review

## Layer & Role

Interaction Pathway only: L1 → L2 selection → L3 design → L4 render → L1. Validate `inflak-build-review` for `inflak-authoring`, `build_review_gap`, `review_plugin_build`, `G→I`; design registered `plugin_build_review` on `conversation_widget`. No publication, execution, diagnosis, substitution or rendering.

## Inputs

Read `planner_id`, `selected_widget_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, exact `expected_return`, `return_to`, actual runtime/local registry and context. Require actual current immutable preview ID/hash/revision, full approved-design traceability, validation/reference hashes, readiness, warnings/files/examples/cases and actual scenario case/run/failed-check/report/session evidence where present. Failed installed scenarios are not successful ready builds.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Authorize only the exact reviewed bundle, request changes or cancel after inspecting risk. |
| Presented information | Approved workflow/interactions/state/final presentation first; actual identity, risks/readiness/cases/scenario status visible. |
| Supported interaction | Inspect traceability, explicitly acknowledge required warning IDs, choose publish/changes/cancel; only actual host-provided scenario affordances. |
| Feedback and constraints | Block stale/failed/incomplete publication and show missing acknowledgements/first failed phase. |
| Submission and return | Derive unchanged preview ID/hash/revision from actual display; exact decision, warnings and changes. |
| Presentation intent | Compact release review, visible immutable identity/risk, collapsed technical detail; no marketing. |

## Essential Constraints

- Validate ID, skill/path, planner/gap/goal/edge, returns, artifacts/runtime. Preserve chain/reason/source/edge/target; G in sources, I target and allowed `state_update_target`. L1 maps I to exact `build_approval` or change/cancel evidence.
- Fixed returns: `decision`, `preview_id`, `preview_hash` strings; `approved_revision` integer; `change_requests`, `acknowledged_warnings` arrays. Publish requires exact displayed identity/revision, complete design traceability and all required warning acknowledgements. Never reconstruct hashes from text; blocking validation/risk remains blocking even when acknowledged.
- Changes need a nonempty request; cancel publishes nothing. Failed required scenario never authorizes the same hash again. Preserve actual case/run/report/session and planned status for L1/L2 revision, not a fabricated good preview.
- Required warnings use explicit accessible actions/selection tied to actual IDs, not approval checkboxes. One primary submit expresses chosen decision/identity without generic second confirmation. No scenario/task/publish calls, hidden warning, staged mutation, invented readiness, HTML/CSS/JavaScript or local runtime paths.

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

Validate actual identity, risks/constraints and exact mappings; send to `l4-inflak-author-renderer`. Invalid selection or missing indispensable evidence/capability returns `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, `return_to: l1-inflak-author-core`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 owns canonical state/merging and Completion or `decision: end`. Every result/failure re-enters `l1-inflak-author-core`; hash approval is nonterminal authorization for a fresh L2 publication pass, not publication itself.
