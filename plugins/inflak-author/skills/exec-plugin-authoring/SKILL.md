---
name: exec-plugin-authoring
description: "Use when: Author L2 hands off an instruction-ready resource inspection, immutable preview or approved publication plan."
---

# Plugin Authoring Execution

## Role and Handoff

Execution capability of the same Host Agent, parallel to the L3 interaction branch, not a numbered layer or another agent. Load only after L1 and L2 with the current `planner_handoff` and `execution_instruction`. Preserve the selected registered tool, exact parameters, purpose and actual authorization. Execute one planned operation; do not select gaps, replan, render or infer permission. Every actual result/failure returns to `l1-inflak-author-core`. Only L1 merges state and decides Completion; no L3/L4 execution. Missing or stale input returns there without side effects.

## Permission and input checks

Require a current `planner_handoff` for `inflak-authoring`, `planner_decision: instruction_ready`, one explicit registered/allowed available executor, complete parameters and purpose. Preserve the exact selected executor; no substitution or inferred approval.

| Executor | Required input and boundary |
| --- | --- |
| `inspect_inflak_authoring_resources` | `resources`: stable uploaded `fileId` references and purposes; static inspection only, never execute uploaded code or read secrets. |
| `preview_inflak_plugin` | `target_spec`, `approved_revision`: complete approved current design, inspected dependencies, at least one approved realistic acceptance case; immutable staging, no ready-tree/manifest mutation. |
| `publish_inflak_plugin` | Only `preview_id`, `preview_hash`, `approved_revision`: exact current immutable preview identity and explicit author authorization, with required warning acknowledgements in canonical state. No arbitrary files, extra replacement content or reconstructed hash. |

Reject stale revision/hash, local runtime paths, credentials, undeclared parameters or external capability claims. A changed intent, resource or canonical authoring contract invalidates dependent preview and approval. Preserve design-time reference hashes for all three current main contract documents.

## Invocation and results

exec-plugin-authoring executes the L2 plan and invokes the one selected tool once with the complete plan. Every actual result or failure immediately returns to `l1-inflak-author-core`; never perform another operation before L1 re-entry.

- Inspection reports resource kind, capabilities, static risks, missing dependencies and execution recommendation without running code.
- Preview reports immutable ID/hash/revision, behavior summary, reference hashes, layer/registry/return validation, runtime bindings, warnings and file list. Never fabricate a successful report.
- Publication atomically installs only the approved staged bundle, re-reads it, verifies bundle hash and manifest/root identity, refreshes runtime discovery and performs an isolated entry smoke-load. A new independent target requires its byte-identical root alias; existing sole-L1 compatibility and main's direct entry are not silently rewritten.
- Required real-session acceptance uses approved realistic input/returns, persists trace/contracts/returns/tool results/artifacts/assertions, and must succeed before retaining `ready`. Background or interactive scenario actions use only actual host-provided controls; this reference does not invent a callable scenario tool.
- Failed installed/runtime/scenario validation leaves or downgrades the target to `planned`. Return plugin/case/run/report/session identity, failed checks and first failing phase. Do not republish the failed hash. Regeneration of that exact planned plugin requires `replace_existing_plugin: true`, exact `source_scenario_run_id`, a new immutable preview and new hash approval.

## Prohibitions

No rendering, uploaded Python execution, undeclared service, secret collection, hash bypass, arbitrary filesystem writes or completion decision. Only L1 may emit `decision: end`; executor success is nonterminal evidence.