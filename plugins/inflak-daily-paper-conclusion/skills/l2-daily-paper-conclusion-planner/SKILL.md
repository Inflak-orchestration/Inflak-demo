---
name: l2-daily-paper-conclusion-planner
description: "Use when: L1 selects daily-paper-conclusion for evidence-grounded arXiv scope, coverage, synthesis or justified execution."
---

# L2 Planner — Daily Paper Conclusion

## Workflow End Authority

Only `l1-daily-paper-conclusion-core` owns canonical state, merges returns and may emit `decision: "end"`. L2 selects one eligible interaction or directly realizes an `instruction_ready` execution with the active `main_model`. Every result, partial result or failure immediately returns to L1; Execution never enters L3/L4.

## Layer & Role

Diagnose information-transfer gaps and select the exact widget before semantic design, or plan and execute justified public arXiv collection, evidence inspection, digest synthesis/revision. Never render, design controls or replace substantive evidence decisions with approval rituals.

## IAI Domain Binding

| Node | Meaning |
| --- | --- |
| H | Reader retaining/delegating scope, inclusion and emphasis |
| T | Daily cs.HC topic, source/range/focus and desired conclusion |
| I | Reader's current scope, inclusion, theme or digest decision |
| Aug | Authorized collection/inspection/synthesis instruction |
| A | Actual arXiv metadata/abstract evidence, theme map and digest revision |
| G | Active session model with only actually available source capabilities |

## Interaction Chains

| Chain ID | Paradigm / function | Ordered edges |
| --- | --- | --- |
| daily-direct | Bounded preparation or authorized collection/synthesis | `H→T, T→Aug, Aug→G, G→A` |
| daily-scope | Supply source/range/focus constraints | `H→I, I→Aug, Aug→G, G→A` |
| daily-evidence | Inspect actual coverage and resolve inclusion or emphasis | `G→A, A→I, I→Aug, Aug→G, G→A` |
| daily-review | Review digest and request bounded revision | `G→A, A→I, I→Aug, Aug→G, G→A` |

`I→Aug` incorporates user constraints/judgment, `A→I` exposes actual coverage or digest; `Aug→G` is L2 direct execution, `G→A` creates evidence, never user approval.

## Diagnosis

Assess **every registered gap** as `open`, `resolved` or `not applicable` each pass using pre/post-execution and prompt-only/source-grounded evidence. Record missing transfer, applicability, closure evidence and delegation scope in `iai_binding.reason` or `execution_instruction.purpose`. Silence is not delegation. Supplied explicit scope authorization settles that choice; no repeated widget solely because a stage name exists. Select the next applicable open gap by dependencies; future acceptance is not applicable before a current digest exists and is reassessed on return.

| gap_type | Condition | Edge | Interaction goal |
| --- | --- | --- | --- |
| `scope_setup_gap` | Public source/date-range or paper limit/focus/output has a material unresolved constraint or collection authorization. | `I→Aug` | `structured_input` |
| `candidate_collection_review_gap` | Actual empty/partial/failed collection has a material coverage choice or requested inspection. | `A→I` | `progress_inspector` |
| `paper_inspection_resolution_gap` | Actual inaccessible/borderline/weak-evidence papers require a reader-owned inclusion or caveat decision. | `I→Aug` | `decision_review` |
| `synthesis_direction_review_gap` | Actual theme/evidence proposals contain an unresolved headline/emphasis/claim-strength decision. | `I→Aug` | `decision_review` |
| `digest_acceptance_review_gap` | A current evidence-linked digest needs final review, revision, scope reopening or export choice. | `A→I` | `result_review` |
| `instruction_ready` | Relevant input gaps are evidence-resolved, or bounded prerequisite preparation preserves open user choices and returns L1 without unauthorized final synthesis. | `Aug→G` then `G→A` | Execute scoped collection/inspection/preparation/synthesis/revision and return actual evidence. |

Dependencies: authorized real public arXiv cs.HC source/scope → actual listing collection/filter/dedup → evidence card or explicit inaccessible/skipped record for each included paper → supported themes → digest with critical review → current acceptance. Preparing a theme map does not invent reader approval. Warnings already settled by evidence need no ritual interaction; genuinely unresolved coverage affects subsequent synthesis. Scope changes invalidate affected downstream revisions. Network/access failure is technical evidence, not a fabricated gap or fake listing.

## Widget Registry Routing

Exact IDs for the five rows are `daily-paper-conclusion-scope-setup`, `daily-paper-conclusion-candidate-collection-review`, `daily-paper-conclusion-paper-inspection-resolution`, `daily-paper-conclusion-synthesis-direction-review`, `daily-paper-conclusion-digest-acceptance-review`; skills are `l3-` plus ID at each registry canonical_skill_path. Fixed keys come from registry expected_return_types and typed/enumerated returns from that L3; preserve all auxiliary status and request fields.

Hard-filter by planner, gap, goal, atomic edge/destination, complete return coverage/types, actual artifact support and available capabilities/libraries. Rank by semantic coverage, artifact specificity, return coverage, runtime fitness, registry order then ID; choose exactly one. None eligible: return `reason: no_eligible_widget`, `planner_id: daily-paper-conclusion`, `diagnosed_gap` with chain/evidence/edge/goal/returns, `rejected_candidates` with IDs/failed constraints, `return_to: l1-daily-paper-conclusion-core`, nonterminal without L3. Never substitute another widget or fake readiness.

## Gap Handoff

Emit `handoff_type: planner_handoff`, `planner_id: daily-paper-conclusion`, `planner_decision: gap_open`, exactly one record in the `gap_requests` array and `return_to: l1-daily-paper-conclusion-core`. The record carries named `chain_id`, exact `gap_type`, `interaction_goal`, `selected_widget_id`, `order: 1`, `depends_on_previous: false`, grounded `display_context`, typed `expected_return`, `iai_binding` with `source_nodes`, `maps_to_edge`, `target_node`, meaningful `reason`. Source belongs to source_nodes; destination equals target_node. Explain the missing transfer, real closure evidence, all-category assessment and consequence of guessing. Do not copy L3 presentation/control or renderer fields into L2.

## Output (planner_handoff)

Execution emits `handoff_type: planner_handoff`, `planner_id: daily-paper-conclusion`, `planner_decision: instruction_ready`, `execution_instruction` with `executor: {kind: main_model}`, actual operation/scope/evidence/revision `parameters`, evidence-backed `purpose` and `return_to: l1-daily-paper-conclusion-core`. Omit `gap_requests` and `selected_widget_id` on Execution Pathway. Directly realize the declared instruction in the active session; return actual `execution_result` evidence/failure to L1. This is not a host function call or Host Agent Return. Literal dotted-state references are not parameters.

## Inputs and Procedure

Require selected_planner and state_snapshot `user_text`/`conversation_context`; consume typed task_frame, daily_scope, scope_decision, collection_readiness_status, candidate_list, collection_status, skipped_entry_log, paper_evidence_cards, inspection_warnings, inclusion_decisions, theme_map, synthesis_direction, coverage_notes, draft_digest, reviewed_digest, revision_requests, accepted_digest, export_status, final_acceptance, revision_marker and prior_returns when present.

1. Assess all categories and dependencies; resolve the next material gap or perform only justified prerequisite preparation.
2. Collect only authorized available public sources; preserve canonical arXiv identities, URLs, actual date metadata, duplicates/skips and per-fetch/extraction/filter status.
3. Inspect actual abstracts/details; distinguish abstract evidence from listing-only metadata and unavailable full text. Preserve partial success; never invent abstracts, methods or conclusions.
4. Build grounded theme-to-paper support and a readable digest: top conclusion, paper highlights, cross-paper themes, evidence links and caveats. Include a clearly labeled **1-2 sentence critical review** naming a supported limitation, assumption, evidence gap or implication. Separate inference from source claims and disclose abstract/metadata-only boundaries; do not fabricate criticism.
5. Missing criticism or unsupported synthesis requires bounded repair before final-review selection, not L3 authoring. Return each actual result/failure to L1; acceptance binds exact digest/scope revision. Copy/export is not acceptance.

## Tools

The active `main_model` performs the declared operation with actually available authorized capabilities; no unregistered fetch or export API is implied. Unavailable access returns a truthful limitation with retained evidence. `render_html_widget` is L4-only; do not call it or task tools from L3/L4.

## Must / Must Not

Preserve source-bound evidence, explicit authorization, partial coverage and critical review. Do not force every widget, invent counts/citations/approval, turn warning acknowledgement into resolution, render, merge state, emit end or synthesize final output while applicable input gaps remain open.

## Stop / Continue / Escape

Stop this pass after one handoff or execution result/failure. Continue only after L1 reconstruction. Escape inaccessible sources, absent required capability or refused indispensable choice directly to L1 without L3, retaining actual partial evidence.

## Next

Interaction: L1 → L2 gap/selection → L3 → L4 → L1. Execution: L1 → L2 plan → active main_model → L1, without L3/L4. Only L1 selects Host Agent Return (`bypass`/`direct_answer`) or Completion.
