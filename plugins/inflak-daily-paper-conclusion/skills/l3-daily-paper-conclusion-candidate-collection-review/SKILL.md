---
name: l3-daily-paper-conclusion-candidate-collection-review
description: "Use when: L2 selects daily-paper-conclusion-candidate-collection-review for candidate_collection_review_gap."
---

# L3 Designer — Collection Status Timeline

## Layer & Role

Design only `daily-paper-conclusion-candidate-collection-review` / `collection_status_timeline`, planner `daily-paper-conclusion`, gap `candidate_collection_review_gap`, goal `progress_inspector`. L3 designs inspection semantics, not collection, retry execution, routing or HTML/CSS/JavaScript.

## Inputs

Read L2 `selected_widget_id`, `planner_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `display_context`, `expected_return`, `return_to`, local registry/runtime, current scope, real fetch/extract/filter/deduplicate status, candidates, skipped-entry log and warnings.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Obtain an informed decision when empty or partial coverage affects the digest. |
| Presented information | Actual timeline and active/failed operation, scope recap, candidate count, skipped or duplicate entries and public listing provenance. |
| Supported interaction | Expand evidence, inspect candidates, choose continuation with partial data, scope repair or stop; request retry only through declared decision data. |
| Feedback and constraints | Distinguish unknown, failed, empty and partially successful collection; do not animate invented progress or clear warnings by acknowledgement. |
| Submission and return | `candidate_decisions`: array; `collection_status`: object; `next_action`: continue/revise_scope/stop. Carry any supported retry request inside declared decision records, never invent a top-level retry field or enum. |
| Presentation intent | Timeline explains where coverage was lost; retain successful candidates beside failures and visible recovery choices. |

## Essential Constraints

Validate exact ID, skill/path, planner/gap/goal/edge, returns, artifact support, state destination and capabilities. Preserve `A→I`, `state_update_target: I`, chain/reason. L1 applies candidate decisions by stable arXiv identity to `candidate_list`, records `collection_status`, preserves `skipped_entry_log`, and routes next_action from history. A stop request is not successful digest completion. One primary submission; no confirmation checkbox or new runtime API.

## Output and Handoff

Complete local contract; no success `handoff_type` or external read:

- Identity: nonempty exact `selected_widget_id`, instance `widget_id`, registry `widget_type`/`surface`, `planner_id`, contextual `purpose`, unchanged `interaction_goal`.
- `iai`: unchanged named `chain_id`, `gap_type`, meaningful binding `reason`, `source_nodes`, `maps_to_edge`, `target_node`; source belongs to `source_nodes`, edge destination equals `target_node` and allowed `state_update_target`; deterministic L1 `merge_strategy`, `next_planner_action: "re-enter Layer 1"`.
- `display`: grounded values, actual references, current/unresolved status; no invented facts, defaults, uploads, previews or outcomes.
- `controls`: unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty declared `return_keys`, applicable type/limit/source/edit `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`, nonempty `content` array of resolvable `source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose` records; `interaction` with nonempty `actions`/`feedback`, `submission` with nonempty `label`/`preconditions` and exact `return_mapping`; nonempty semantic `appearance` and `signature_features` list.
- `expected_return`: exactly L2 keys/types; `presentation.profile.interaction.submission.return_mapping` has exactly the same keys, each actual source and serialization including optional/empty handling. Derived fields need mappings, not artificial controls.
- `widget_requirements`: four nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`, consistent with profile and without extra gates.
- `safety`: `allow_html: false`, `allow_script: false`; optional `runtime` limited to available approved capabilities/version-pinned libraries; optional `reference_assets` plugin-relative design-time references/principles, never runtime assets.

Validate sources, constraints and producible mappings; send to `l4-daily-paper-conclusion-renderer`. Invalid selection or indispensable missing evidence/capability returns `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, `return_to: l1-daily-paper-conclusion-core`; no L4 or substitution.

## Workflow End Authority

Only L1 owns canonical state, merges returns and may emit `decision: "end"`. Every return/failure goes to `l1-daily-paper-conclusion-core`; partial-data continuation is nonterminal.

