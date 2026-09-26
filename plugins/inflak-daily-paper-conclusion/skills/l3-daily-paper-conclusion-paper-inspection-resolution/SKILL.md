---
name: l3-daily-paper-conclusion-paper-inspection-resolution
description: "Use when: L2 selects daily-paper-conclusion-paper-inspection-resolution for paper_inspection_resolution_gap."
---

# L3 Designer — Paper Inspection Resolution

## Layer & Role

Interaction design only: do not execute task operations or render HTML/CSS/JavaScript; L2 owns execution and L4 owns rendering.

Design only `daily-paper-conclusion-paper-inspection-resolution` / `inspection_warning_dialogue`, planner `daily-paper-conclusion`, gap `paper_inspection_resolution_gap`, goal `decision_review`. No source fetching, re-diagnosis, replacement widget or implementation code.

## Inputs

Read L2 `selected_widget_id`, `planner_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `display_context`, `expected_return`, `return_to`, local registry/runtime, actual affected papers, evidence cards, inaccessible-page log, focus criteria and available listing/abstract evidence.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Resolve inclusion and evidence-boundary choices for inaccessible, borderline or low-confidence papers. |
| Presented information | Warning, affected paper identities, public detail links, evidence availability and consequences of each supported response. |
| Supported interaction | Include with caveat, exclude affected papers, request reinspection or revise scope; preserve per-paper decisions. |
| Feedback and constraints | Show coverage changes and listing-only limitations; an accepted caveat does not create missing abstract evidence. |
| Submission and return | `paper_decisions`: array; `inspection_warnings`: array; `next_action`: continue/reinspect/revise_scope. Notes belong inside declared records if supported, not a new top-level field. |
| Presentation intent | Focus on the material warning and evidence, not an arbitrary approval stage for every paper. |

## Essential Constraints

Validate exact ID, skill/path, planner/gap/goal/edge, returns, artifact support, state destination and runtime/library availability. Preserve `I→Aug`, `state_update_target: Aug`, chain/reason. L1 maps paper decisions to `inclusion_decisions`, retains actual `inspection_warnings` and evidence cards, invalidates affected themes/digest, and routes reinspection without pretending it already occurred. One primary submission; no second confirmation, fabricated papers or claims.

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

Only L1 owns canonical state, merges returns and may emit `decision: "end"`. Every return/failure goes to `l1-daily-paper-conclusion-core`; inclusion choices are nonterminal evidence.

