---
name: l3-daily-paper-conclusion-scope-setup
description: "Use when: L2 selects daily-paper-conclusion-scope-setup for scope_setup_gap."
---

# L3 Designer — Daily Scope Filter

## Layer & Role

Interaction design only: do not execute task operations or render HTML/CSS/JavaScript; L2 owns execution and L4 owns rendering.

Design only `daily-paper-conclusion-scope-setup` / `source_filter_panel`, planner `daily-paper-conclusion`, gap `scope_setup_gap`, goal `structured_input`. L2 selects; L3 designs semantics; L4 implements. No collection, re-diagnosis, replacement widget or HTML/CSS/JavaScript.

## Inputs

Read L2 `selected_widget_id`, `planner_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `display_context`, `expected_return`, `return_to`, local registry/runtime, current public arXiv URL, date/range or paper limit, focus criteria, output preferences and actual scope evidence/delegation.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Resolve material source/range/focus ambiguity and scope-bound collection permission. |
| Presented information | Show current URL and source preview, scope filters, output preferences, readiness and contradictory combinations. |
| Supported interaction | Edit source, date/range, count and facets; submit the chosen scope or request changes. |
| Feedback and constraints | Public arXiv URL and coherent scope are required for collection; estimates require actual evidence and are not fetched results. |
| Submission and return | `daily_scope`: object; `scope_decision`: approve/request_changes; `collection_readiness_status`: object derived from actual local validation, not an editable assertion of network access. |
| Presentation intent | Source/filter clarity before compact readiness feedback; preserve existing choices and avoid sample counts or approval checkboxes. |

## Essential Constraints

Validate exact ID, skill/path, planner/gap/goal/edge, returns, artifact support, state destination and runtime/library availability. Preserve `I→Aug`, `state_update_target: Aug`, chain and reason. L1 merges the three declared fields and advances `revision_marker` on material scope changes, invalidating candidates/evidence/synthesis/acceptance. A new scope is not collected evidence. Use one primary submit; no second confirmation or invented defaults.

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

Only L1 owns canonical state, merges returns and may emit `decision: "end"`. Every return/failure goes to `l1-daily-paper-conclusion-core`; scope submission is nonterminal.

