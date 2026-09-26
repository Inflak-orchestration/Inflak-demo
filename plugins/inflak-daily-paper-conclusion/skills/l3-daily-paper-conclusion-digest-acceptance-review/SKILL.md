---
name: l3-daily-paper-conclusion-digest-acceptance-review
description: "Use when: L2 selects daily-paper-conclusion-digest-acceptance-review for digest_acceptance_review_gap."
---

# L3 Designer — Evidence-linked Digest Review

## Layer & Role

Design only `daily-paper-conclusion-digest-acceptance-review` / `evidence_linked_artifact_review`, planner `daily-paper-conclusion`, gap `digest_acceptance_review_gap`, goal `result_review`. L3 designs final-review semantics, not digest generation, execution, Completion or HTML/CSS/JavaScript.

## Inputs

Read L2 `selected_widget_id`, `planner_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `display_context`, `expected_return`, `return_to`, local registry/runtime, actual draft/reviewed digest, scope/revision, evidence links, warnings, revision history and export availability.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Let the user inspect the current evidence-linked digest and accept or request bounded changes. |
| Presented information | Top conclusion and coverage first; clearly labeled 1-2 sentence critical review grounded in available abstracts/metadata; paper highlights, themes, links, caveats and stale status. |
| Supported interaction | Inspect evidence, compare actual revisions, request changes, accept, copy/export or reopen scope. |
| Feedback and constraints | Keep uncertainty adjacent to claims; missing critical review, unsupported criticism or stale scope blocks final acceptance/export until corrected through L1. |
| Submission and return | `decision`: accept/request_revision/reopen_scope/export; `revision_requests`: array; `accepted_digest`: object identifying the actual displayed revision only when accepted, otherwise the declared empty form. |
| Presentation intent | Readable digest with inspectable evidence and persistent actions; neither copy nor export silently supplies acceptance. |

## Essential Constraints

Validate exact ID, skill/path, planner/gap/goal/edge, returns, artifact support, state destination and runtime. Preserve `A→I`, `state_update_target: I`, chain/reason. L1 records exact-revision `final_acceptance` and `accepted_digest` only on accept, retains `revision_requests`, and marks export status from actual output. Do not silently repair missing critical review here; L2's main_model must produce it. One primary submission, no confirmation checkbox or second acceptance step; a successful copy is not a new paper result.

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

Only L1 owns canonical state, merges returns and may emit `decision: "end"`. Every return/failure goes to `l1-daily-paper-conclusion-core`; acceptance remains nonterminal until L1 validates the current digest.

