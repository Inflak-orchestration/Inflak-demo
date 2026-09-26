---
name: l3-daily-paper-conclusion-synthesis-direction-review
description: "Use when: L2 selects daily-paper-conclusion-synthesis-direction-review for synthesis_direction_review_gap."
---

# L3 Designer — Theme Evidence Matrix

## Layer & Role

Interaction design only: do not execute task operations or render HTML/CSS/JavaScript; L2 owns execution and L4 owns rendering.

Design only `daily-paper-conclusion-synthesis-direction-review` / `theme_evidence_matrix`, planner `daily-paper-conclusion`, gap `synthesis_direction_review_gap`, goal `decision_review`. Design evidence comparison semantics; never synthesize a replacement digest, execute inspection, reroute or implement UI code.

## Inputs

Read L2 `selected_widget_id`, `planner_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `display_context`, `expected_return`, `return_to`, local registry/runtime, actual headline/theme proposals, paper evidence cards, focus, coverage notes and revision identity.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Resolve emphasis and claim-strength choices from actual theme-to-paper support. |
| Presented information | Headline preview, theme-by-paper matrix, support links, confidence basis and weak/contradictory evidence. |
| Supported interaction | Compare themes, prioritize, downgrade unsupported wording, request revision or return to inspection. |
| Feedback and constraints | Every headline claim needs evidence or an explicit caveat; show changed priorities and remaining uncertainty without invented counts. |
| Submission and return | `approved_direction`: object; `theme_priorities`: array; `revision_request`: string. Preserve stable theme/paper identities and order. |
| Presentation intent | Keep support and caveats adjacent to claims; retain the required evidence-grounded 1-2 sentence critical review as part of the synthesis requirements. |

## Essential Constraints

Validate exact ID, skill/path, planner/gap/goal/edge, returns, artifact support, state destination and runtime. Preserve `I→Aug`, `state_update_target: Aug`, chain/reason. L1 records `synthesis_direction` from chosen direction/priorities, maps bounded revision instructions to `revision_requests`, and invalidates affected `draft_digest`/acceptance; raw paper evidence remains intact. One primary submission; no confirmation checkbox or fabricated criticism. Missing actual analysis is returned to L1 for bounded execution, not invented here.

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

Only L1 owns canonical state, merges returns and may emit `decision: "end"`. Every return/failure goes to `l1-daily-paper-conclusion-core`; direction selection is nonterminal.

