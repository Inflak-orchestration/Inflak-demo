---
name: l1-daily-paper-conclusion-core
description: "Use when: entering or re-entering daily-paper work after any user, widget, execution, partial-failure or failure event."
---

# L1 Router — Daily Paper Conclusion

## Layer & Role

Read this plugin's root and local registries. L1 alone owns canonical state, validates and merges evidence, chooses pathways and may emit `decision: "end"`. All initial messages and L2/L3/L4/executor returns, routing/validation/render/tool failures and partial results first enter here. Downstream instruction_ready, completion_candidate, acceptance or execution success is nonterminal until checked here.

## Four Pathways

- **Interaction Pathway:** user/return → L1 → L2 gap + exact selection → L3 semantic design → L4 render → L1.
- **Execution Pathway:** user/return → L1 → L2 plan → selected executor/current active main_model → L1; no L3/L4 or separate executor skill.
- **Host Agent Return:** L1 → host with existing `bypass` or `direct_answer` when appropriate, not disguised daily collection/synthesis execution.
- **Completion:** only L1 emits `decision: "end"` for verified current outcome; cancellation is explicitly cancelled, never successful digest completion.

## Canonical State and Lifecycle

Required user_text/conversation_context retain actual types; omit absent optional fields, never fabricate empty strings for every state. L1 is sole writer; proposals are not user decisions. Preserve objects/arrays and evidence revisions.

| State | Evidence / merge and visibility | Invalidation / retention |
| --- | --- | --- |
| task_frame, daily_scope, scope_decision, collection_readiness_status | Actual public arXiv source/range/limit/focus/output and scope-bound permission; visible scope/readiness. | Material change advances revision_marker and invalidates affected downstream state; validation is not network success. |
| candidate_list, collection_status, skipped_entry_log | Actual collected stable arXiv identities, dedup/filter and partial/failure status. | Retain successes and skipped/duplicate reasons; new scope marks incompatible entries stale. |
| paper_evidence_cards, inspection_warnings, inclusion_decisions | Actual abstract/detail/listing-only evidence and bounded inclusion choices. | Preserve evidence boundaries and exclusions; changed inclusion invalidates themes/digest. |
| theme_map, synthesis_direction, coverage_notes | Grounded theme-to-paper support, priorities and uncertainty. | Changed evidence/direction invalidates derived digest, not raw evidence. |
| draft_digest, reviewed_digest, revision_requests, accepted_digest, export_status, final_acceptance | Actual digest revisions and current user acceptance; real export state. | Scope/evidence/revision changes invalidate acceptance/export; copy/export alone is not acceptance. |
| revision_marker, prior_returns | Current dependency revision and append-only original event envelopes. | Retain history and stable IDs; deduplicate replays without repeating side effects. |

## Return Reconstruction and Merge

Validate planner/widget/executor identity, pending operation, exact keys/types and source/revision before applying. Stale/invalid returns remain historical evidence with deterministic errors, not current acceptance. Preserve all auxiliary fields in prior_returns and their declared semantics; IAI T/Aug/A/I destinations are not business field names.

- Scope: merge daily_scope/scope_decision/collection_readiness_status, distinguish approve from request_changes, invalidate changed dependencies.
- Collection: apply candidate_decisions by real arXiv identity to candidate_list; retain collection_status/skipped_entry_log and next_action in history. A supported retry record requests future work, never asserts fetched data; stop is not success.
- Inspection: paper_decisions → inclusion_decisions; retain inspection_warnings and paper_evidence_cards, route next_action for reinspect/scope repair. Notes inside declared records cannot become fabricated top-level fields.
- Synthesis: approved_direction and theme_priorities → synthesis_direction; revision_request → revision_requests. Retain theme_map/coverage_notes and invalidate affected digest.
- Digest: decision/revision_requests/accepted_digest → exact-revision final_acceptance and accepted_digest only for accept. Preserve actual reviewed_digest; export updates only actual export_status, reopen_scope invalidates downstream state.
- Execution: merge actual collection/evidence/theme/digest outputs only, preserving per-paper access failure and successful partial evidence. Missing abstracts never become source-supported conclusions.

Newest valid explicit user decision applies only to its scope. Failure never overwrites success, authorizes unsupported browsing or silently accepts weak evidence; avoid unmodified retry loops.

## Routing and core_handoff

Select exactly `daily-paper-conclusion` using `skills/l2-daily-paper-conclusion-planner/SKILL.md`, checking registry/required state. Emit handoff_type core_handoff, decision route, selected_planner daily-paper-conclusion, actual typed state_snapshot and `return_to: l1-daily-paper-conclusion-core`. Include required and available optional state/prior_returns, actual source/revision and runtime limits, not fabricated defaults. L2 assesses all gap categories and selects by real dependencies; L1 does not preselect widgets or execute tasks.

## Completion and Final Presentation

Success requires the current evidence-linked digest for authorized scope, visible coverage/omissions, paper links, highlights/themes and a clearly labeled **1-2 sentence critical review** grounded in actual available evidence. Critical review identifies a supported limitation, assumption, evidence gap or implication, labels inference and abstract/metadata-only boundaries; no invented criticism. Missing/unsupported critical review needs L2 repair before acceptance. Require exact-current user acceptance and no unresolved revision. Show conclusion/critical review first, scope and paper evidence, caveats and actual export availability. Copy/export does not equal acceptance; future acceptance before a digest exists does not block bounded preparation. Explicitly cancelled/host outcomes are not success.

## Next

Choose one pathway only from reconstructed current evidence; every subsequent result/failure returns here before any action or Completion.
