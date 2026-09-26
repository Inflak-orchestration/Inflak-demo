---
name: inflak-pN9-artifact-to-structured-instruction
description: "Use when: an uploaded visualization or tabular dataset needs evidence-aware analysis and a grounded structured report."
---

# P9 — Artifact to Structured Instruction

Root documentation read by sole callable entry `l1-pN9-core-module`. The source visualization or tabular dataset remains immutable while the active Host Agent realizes the user-confirmed structured analysis report.

## Four-Layer Contract

L1 Router owns state/routing/Completion. L2 Planner assesses gaps, selects one eligible widget or emits instruction_ready for execution by exec-pN9-report-generation using the active `main_model` Host Agent. L3 Designer validates exact selection and designs semantics only. L4 renders conversation_widget through render_html_widget.

## Four Pathways

| Pathway | Flow |
| --- | --- |
| Interaction Pathway | user/return → L1 → L2 gap + registry selection → L3 design → L4 render → L1 |
| Execution Pathway | user/return → L1 → L2 ready plan → exec-pN9-report-generation (main_model) → L1; no L3/L4 |
| Host Agent Return | user → L1 → host agent; bypass or direct_answer |
| Completion | user/return → L1 → Completion; only L1 emits decision: end |

Every result, failure, dismissal and routing error re-enters L1 before further action.

## Evidence and Authorization

Legible labels/marks/filters/units/values and supplied CSV cells are observations; hidden data, unreadable values, denominators, metric meaning and causality remain uncertain. Distinguish artifact facts, model suggestions, user selections and missing evidence. Never invent rows, fields, sources, comparisons, or successful generation.

Ask only about unresolved material choices. The default flow is grounded direction selection followed by report delivery, not brief approval followed by plan approval followed by acceptance. Reuse supplied preferences, selections and source facts. Brief and composer are optional for real ambiguity or requested customization; model-chosen sections/charts remain suggestions, not user approvals. The Host Agent emits a self-contained structured report grounded only in confirmed evidence. It may describe chart specifications as data, but never emits executable HTML, scripts, remote data URLs, invented rows, or claims unsupported by the source. L2 reads [execution skill](skills/exec-pN9-report-generation/SKILL.md) as needed.

The host saves a static HTML report and supplies the frontend preview/open/download links from actual persisted files. Report delivery is nonblocking. Review is optional for a user-requested revision or explicit approval workflow. Revisions invalidate the affected generated report state, not immutable source evidence.

## Registry and Handoffs

Local registries are authoritative. Each L3 has complete local eight-part output; L4 has local Inputs and the 266px baseline. No main skill, authoring contract, plugin-local MCP server, or task tool is a runtime prerequisite.

## Next

Enter `l1-pN9-core-module`; only L1 finishes after delivery of the current Host Agent report with no material action outstanding, or records cancellation. Explicit approval is required only when the user requested it.
