---
name: l1-pN9-core-module
description: "Use when: entering P9 or receiving any analysis widget, Host Agent, or failure return."
---

# L1 Router — P9

## Layer & Role

Read [root documentation](../../SKILL.md) before first routing. Sole callable entry; reconstruct state and route, never inspect evidence, diagnose gaps, choose widgets, compile instructions, render or execute. Only L1 owns canonical merging and `decision: end`.

## Four Pathways

| Pathway | Flow |
| --- | --- |
| Interaction Pathway | user/return → L1 → L2 gap + registry selection → L3 design → L4 render → L1 |
| Execution Pathway | user/return → L1 → L2 ready plan → exec-pN9-report-generation (main_model) → L1; no L3/L4 |
| Host Agent Return | user → L1 → host agent; `bypass` or `direct_answer` |
| Completion | user/return → L1 → Completion; only L1 emits `decision: end` |

## State and Re-entry

Preserve `user_text`, immutable `source_artifact_ref`, `artifact_profile`, `data_inventory`, `analysis_suggestions`, `selection_state`, `analysis_brief`, `report_plan`, `compiled_instruction`, `generated_report`, `report_review_state`, and `prior_returns`. Newest valid returned values are authoritative only for their declared domain destination. Node I/T/Aug/A contributions merge into these state fields; do not confuse node identity with storage keys.

Every widget/model return and L2/L3/L4 failure enters here before another action. Revision requests invalidate the affected generated report (and report plan when revised), retaining the immutable source and valid evidence. Failed generation never creates report state.

## Routing

Route `chart-analysis-instruction` → `l2-pN9-chart-analysis-exploration` for source-visualization or tabular-dataset analysis requiring material user choices, and for all active P9 continuations. A complete brief returned inside P9 remains a continuation, not an initial-request bypass. A single visible-value question, initial fully specified direct analysis, chart-design editing or unrelated factual request may use Host Agent Return. Missing source is a blocked input, never invented analysis.

## Output

Emit `core_handoff`, `decision: route_to_planner`, `selected_planner: chart-analysis-instruction`, and newest declared `state_snapshot`. Other decisions are machine `bypass`/`direct_answer` or L1-only `end`; no fabricated placeholders masquerade as facts.

## Must / Must Not

Preserve provenance, exact source references, and return values. Finish when the actual current Host Agent report is ready for delivery with no unresolved material choice or requested revision. Do not open an acceptance widget unless the user explicitly requested approval. Selection, brief or plan submission alone is not completion; explicit dismissal cancels without claiming production. Never resume L2/L3/L4 without this routing pass.

## Host Delivery Envelope

On normal Completion, the final assistant message contains a short summary and exactly one fenced `inflak-report` block. Its JSON object has `source_artifact_ref` (the original session upload path or upload URL) and `generated_report` (the complete actual report returned by the execution skill). Do not send abbreviated placeholders or an ordinary `json` fence. The host consumes this block, loads only source CSV data belonging to this session, renders valid charts using the installed Vega-Lite library, escapes narrative content, and persists a self-contained static HTML document. Preview, open and download links appear only after persistence succeeds; never invent links or claim successful export before host processing. The report has no scripts or external dependencies. Unsupported chart specifications or sources produce visible limitations, never invented charts. Other source formats still support narrative HTML delivery. Host delivery is presentation infrastructure, not a P9 task executor or an L4 interaction. The user can request changes after delivery without approving this version first.

## Next

Load `l2-pN9-chart-analysis-exploration` after routing; all downstream outcomes return here.