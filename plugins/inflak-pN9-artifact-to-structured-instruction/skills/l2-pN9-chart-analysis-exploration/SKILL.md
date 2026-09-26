---
name: l2-pN9-chart-analysis-exploration
description: "Use when: P9 must extract visible evidence, assess chartable data, gather a confirmed analysis and report plan, and have the Host Agent generate a structured report."
---

# Layer 2 - P9 Chart Analysis Exploration

## Layer & Role

L2 diagnoses and plans exactly one evidence-grounded P9 pass. Select one eligible interaction for an open material gap, or emit `instruction_ready` for execution by exec-pN9-report-generation using the active `main_model` Host Agent. Execution Pathway never enters L3/L4 and never invokes a P9 task tool. Return every actual result/failure to `l1-pN9-core-module`; do not render UI or decide Completion. Load the [execution skill](../exec-pN9-report-generation/SKILL.md) for actual execution requirements.

Source interpretation, evidence extraction and report-spec synthesis are bounded model work, not L3 execution or invented user gaps. Missing sources/capabilities are failures to L1, not fabricated readiness.

## Widget Routing

For a widget-path gap, query the plugin-local `registry/widgets.json` after diagnosis. Filter entries by `compatible_planners`, `gap_categories`, `interaction_goals`, `iai_edges`, expected-return coverage, and required artifact, runtime, and renderer availability. Select one eligible widget registry entry and write only its `id` to `gap_requests[0].selected_widget_id`; do not copy registry-derived concrete metadata into the handoff. Layer 3 validates and realizes the selected entry; it does not select or replace it. This layer does not author the semantic widget contract or render UI.

## Inputs

Read the selected `core_handoff.state_snapshot`. Require `user_text` and `source_artifact_ref`; optionally read `artifact_profile`, `data_inventory`, `analysis_suggestions`, `selection_state`, `analysis_brief`, `report_plan`, `compiled_instruction`, `generated_report`, `report_review_state`, and `prior_returns`. Bind every derived state to the current source artifact.

## IAI Binding

| Node | P9 binding |
| --- | --- |
| `H` | Analyst who owns objective, evidence-policy and report acceptance decisions. |
| `A` | Uploaded source visualization and the generated structured report as the resulting artifact. |
| `G` | GenAI evidence interpretation, grounded suggestions, instruction compilation, and Host Agent report generation. |
| `I` | User selection, progressive narrowing, brief/report editing, final preview, and explicit confirmation. |
| `T` | User-readable analysis prompt synthesized from selected directions and brief fields. |
| `Aug` | Evidence-aware structured analysis instruction that joins artifact context and confirmed constraints. |

## Interaction Chains

| Chain ID | Function | Ordered edges |
| --- | --- | --- |
| chart-evidence | Interpret the source and present grounded directions | `A→G, G→I` |
| chart-analysis | Select and narrow the analysis, then confirm its brief | `G→I, I→T, T→Aug` |
| chart-report | Resolve data policy, compose the plan, and generate a structured report | `T→Aug, Aug→G, G→A` |
| chart-review | Review the actual Host Agent report and accept or revise it | `G→I, I→A, A→G` |

## Artifact Profile

Before suggestions, extract only what is visible or explicitly supplied. Record every field as `confirmed_from_artifact`, `suggested_by_genai`, `selected_by_user`, or `missing_or_uncertain`.

```json
{
  "artifact_type": "chart|dashboard-screenshot|analytical-report|data-visualization|tabular-data|csv|spreadsheet",
  "chart_types": [],
  "metrics": [],
  "dimensions": [],
  "time_range": {"value": "", "status": "confirmed_from_artifact"},
  "units": [],
  "categories_or_series": [],
  "filters": [],
  "visible_trends": [],
  "visible_comparisons": [],
  "visible_anomalies": [],
  "unreadable_or_uncertain": []
}
```

An extracted field is not a semantic fact when its meaning cannot be read from the artifact. For example, a plotted line may be observed as declining, but its cause, the meaning of an unlabeled metric, and a value obscured in a screenshot remain uncertain.

## Data Inventory

Before proposing a derived chart, record whether its rows and fields are actually available:

```json
{
  "mode": "machine_readable|visually_extracted|image_only",
  "datasets": [],
  "confirmed_fields": [],
  "confirmed_rows": [],
  "uncertain_values": [],
  "chart_generation_capability": "full|limited|none"
}
```

CSV, JSON, spreadsheet, or explicitly supplied records may support `full` chart generation. Legible values extracted from an image may support only `limited` charts and must retain `confirmed_from_artifact` provenance. A visual trend without readable values is not a dataset. When capability is `none`, embed the source artifact or produce narrative only; never estimate rows for Vega-Lite.

## Suggestion Rules

Generate **3 to 6** suggestions that are specifically supported by the current profile. Candidate lenses include trend analysis, group comparison, anomaly investigation, ranking, distribution, composition, metric decomposition, relationship exploration, change-driver analysis, and forecast preparation. Omit lenses unsupported by the artifact.

Every suggestion contains `id`, short `title`, one-sentence `objective`, concise `rationale`, `support: strong|partial`, `additional_data: none|may_be_required|required`, `data_availability: confirmed|partial|unavailable`, and an optional grounded chart proposal. A recommended item may be marked `recommended: true`, but it is never selected automatically. Avoid generic suggestions unrelated to visible metrics, dimensions, or trends.

## Material Gap Diagnosis

Locate before/after-generation timing and prompt/artifact resources. Assess every registered category as `resolved`, `open`, or `not applicable` using actual evidence, submitted returns and explicit scoped delegation. Record the missing transformation, its cause and consequence of guessing in `iai_binding.reason` or execution purpose. Silence is not delegation. Resolve one next dependency-ready material gap, reusing valid decisions rather than adding mandatory stages or generic approval checkboxes.

| Gap | Condition | Edge | Interaction goal |
| --- | --- | --- | --- |
| `data_availability_gap` | A requested derived chart lacks confirmed rows and no no-invention fallback is selected. | `T→Aug` | `confirm_chart_data_policy` |
| `analysis_direction_gap` | No user-selected primary objective exists. | `G→I` | `select_analysis_objective` |
| `progressive_narrowing_gap` | Scope, comparison, depth or output materially alters the chosen objective. | `I→T` | `narrow_analysis_scope` |
| `brief_completion_or_confirmation_gap` | An unresolved objective, scope, comparison, or metric meaning would materially change the analysis; absence of a confirmation click is not a gap. | `T→Aug` | `complete_analysis_brief` |
| `report_composition_gap` | The user requests report customization, or conflicting output requirements require a user decision; ordinary section/chart selection is model work. | `T→Aug` | `compose_chart_report` |
| `report_review_gap` | The user explicitly requests an approval workflow or a scoped revision of the actual current report; ordinary delivery never requires acceptance. | `G→I` | `review_chart_report` |
| `instruction_ready` | All relevant final-work choices are closed, or bounded evidence preparation has its own sources/permission. | `A→G`, `Aug→G`, or `G→A` | Direct Host Agent interpretation or report generation, then L1. |

Acceptance of the current generated report is nonterminal evidence to L1, not a planner completion action.

Default flow: one grounded direction selection (unless already supplied), then analysis and report delivery with optional revision. Collect dependency-compatible material questions in that same interaction. Brief and composer are optional alternatives, not sequential approval gates. Build `analysis_brief` and `report_plan` from actual selections and source facts; retain model-chosen sections/charts as `suggested_by_genai`, never as user-approved facts. A request to analyze authorizes ordinary read-only calculations, evidence-safe reporting and HTML delivery, not invented objectives or ambiguous metric semantics. Use confirmed rows only; lack of extra data normally becomes a disclosed limitation or narrative fallback, not a policy approval form. Ask about additional data only when the requested result cannot be supported without it.

Diagnose the following only when they alter the analysis: analysis intent gap, scope gap, comparison gap, metric-semantic gap, evidence gap, and output/audience gap. Do not ask the user to reconfirm facts clearly visible in the artifact.

Progressive narrowing must be conditional. For example, after “Investigate August decline,” offer artifact-appropriate choices such as comparison with earlier months, comparison with other regions, revenue decomposition into order volume and average order value, or testing whether the decline is isolated. Do not reuse the broad initial suggestion set.

## Semantic Handoffs

Every request requires a named `chain_id`, registered gap/goal, atomic edge with source membership and destination target, preserved meaningful `reason`, grounded context, exact typed returns, selected registry ID, `order: 1`, and boolean `depends_on_previous`. Filter/rank by semantic coverage, artifact specificity, return coverage, runtime fitness, registry order and ID. No eligible entry returns `reason: no_eligible_widget`, planner ID, `diagnosed_gap` (chain/evidence/edge/goal/returns), `rejected_candidates` and exact L1 `return_to`, without L3 or false readiness.

For `analysis_direction_gap` or `progressive_narrowing_gap`, emit one semantic `gap_request`. When `data_inventory.mode` is `machine_readable`, or confirmed rows have stable `row_id` values and field names, select `data-anchored-analysis-table`; otherwise select `analysis-lens-chips`. Never route a screenshot-only trend or unstructured report to the table widget. The table display context contains a bounded view rather than the entire file: stable `dataset_id`, ordered columns, rows with stable `row_id`, total and visible row counts, active filters, and 3–6 grounded recommendations. Every recommendation binds to existing `row_ids` and `fields` and states its evidence boundary. Group non-table options as `analysis_focus`, `scope`, `analysis_depth`, and `output_format`.

```json
{
  "handoff_type": "planner_handoff",
  "planner_id": "chart-analysis-instruction",
  "planner_decision": "gap_open",
  "gap_requests": [
    {
      "chain_id": "chart-analysis",
      "gap_type": "analysis_direction_gap",
      "selected_widget_id": "analysis-lens-chips",
      "interaction_goal": "select_analysis_objective",
      "iai_binding": {
        "source_nodes": ["G"],
        "maps_to_edge": "G→I",
        "target_node": "I",
        "reason": "GenAI has artifact-grounded analysis suggestions, but the analyst has not selected a primary objective."
      },
      "display_context": {
        "source_artifact_ref": "",
        "artifact_profile": {},
        "suggestion_groups": {}
      },
      "expected_return": {
        "primary_objective_id": "",
        "secondary_lens_ids": [],
        "scope_ids": [],
        "depth_id": "",
        "output_format_id": "",
        "custom_direction": "",
        "removed_or_edited_suggestions": [],
        "action": "continue|edit_selection|start_over|dismiss",
        "freeform_note": ""
      },
      "order": 1,
      "depends_on_previous": false
    }
  ],
  "return_to": "l1-pN9-core-module"
}
```

For a CSV-backed table selection, replace the example's selected widget and return contract with:

```json
{
  "selected_widget_id": "data-anchored-analysis-table",
  "display_context": {
    "source_artifact_ref": "<csv artifact ref>",
    "dataset_id": "<stable dataset id>",
    "columns": [{"field": "", "label": "", "data_type": "string|number|date", "provenance": "confirmed_from_artifact"}],
    "rows": [{"row_id": "<stable row id>"}],
    "total_row_count": 0,
    "visible_row_count": 0,
    "filter_state": {},
    "recommendations": [{
      "recommendation_id": "",
      "label": "",
      "objective": "",
      "rationale": "",
      "support": "strong|partial",
      "additional_data": "none|may_be_required|required",
      "evidence_bindings": [{"dataset_id": "", "row_ids": [], "fields": [], "evidence_boundary": ""}]
    }]
  },
  "expected_return": {
    "primary_recommendation_id": "",
    "secondary_recommendation_ids": [],
    "selected_row_ids": [],
    "selected_fields": [],
    "filter_state": {},
    "comparison_groups": [],
    "custom_direction": "",
    "recommendation_edits": [],
    "action": "continue|edit_recommendations|start_over|dismiss",
    "freeform_note": ""
  }
}
```

Rows must come from the supplied artifact, use deterministic identities derived from source rows rather than visible indexes, and remain bounded to the columns and records needed to evaluate the recommendations. Sorting or filtering changes presentation only; it never rewrites recommendation evidence bindings.

For `brief_completion_or_confirmation_gap`, emit one semantic `gap_request`, populated with the profile, selected directions, field statuses, warnings, a draft instruction preview, and the selected registry ID. Include only unresolved material warnings. Layer 3 validates and realizes the selected entry.

```json
{
  "handoff_type": "planner_handoff",
  "planner_id": "chart-analysis-instruction",
  "planner_decision": "gap_open",
  "gap_requests": [
    {
      "chain_id": "chart-analysis",
      "gap_type": "brief_completion_or_confirmation_gap",
      "selected_widget_id": "analysis-brief-builder",
      "interaction_goal": "complete_analysis_brief",
      "iai_binding": {
        "source_nodes": ["T"],
        "maps_to_edge": "T→Aug",
        "target_node": "Aug",
        "reason": "The selected analysis prompt needs an evidence-aware structured instruction before generation."
      },
      "display_context": {
        "artifact_profile": {},
        "selection_state": {},
        "field_statuses": {},
        "warnings": [],
        "instruction_preview": ""
      },
      "expected_return": {
        "brief_values": {},
        "field_provenance": {},
        "warnings": [],
        "instruction_preview": "",
        "action": "confirm|edit_selection|start_over|dismiss",
        "freeform_note": ""
      },
      "order": 1,
      "depends_on_previous": false
    }
  ],
  "return_to": "l1-pN9-core-module"
}
```

For `data_availability_gap` or `report_composition_gap`, use `chain_id: chart-report`, edge `T→Aug` and the exact diagnosed goal, with profile, inventory, selected analysis, proposed sections and dataset-backed chart proposals. Expected return is `report_plan` (object), `data_policy` (declared enum string), `action` (generate_report|edit_analysis_brief|start_over|dismiss), `freeform_note` (string). Review uses `chain_id: chart-review`, `review_chart_report`, `G→I`, the actual structured report, provenance, and limitations. Return strings are `decision`, `revision_target`, `revision_instruction`, `action`, `freeform_note`; preserve declared accept/revise action combinations. L3 validates selection and designs only semantics.

## Instruction Compilation and Execution

After material choices are resolved by supplied instructions, source evidence, submitted selections or explicit scoped delegation, compile `compiled_instruction` with these sections. Separate brief and report-plan confirmation is not required:

1. `Objective`
2. `Artifact Context`
3. `Analysis Scope`
4. `Comparison Targets`
5. `Analysis Steps`
6. `Evidence Policy`
7. `Output Requirements`
8. `Missing or Additional Data`
9. `Visualization Plan`
10. `Data Provenance`
11. `Artifact Requirements`

The Evidence Policy must label statements as visible observations, interpretations, hypotheses, or claims requiring additional evidence. It forbids invented values and causal claims from correlation alone.

Then issue one Host Agent handoff that produces structured report content, never HTML or JavaScript:

```json
{
  "handoff_type": "planner_handoff",
  "planner_id": "chart-analysis-instruction",
  "planner_decision": "instruction_ready",
  "execution_instruction": {
    "executor": {
      "kind": "main_model",
      "response_format": "structured_analysis_report"
    },
    "parameters": {
      "source_artifact": "<source_artifact_ref>",
      "artifact_profile": "<artifact_profile>",
      "data_inventory": "<data_inventory>",
      "compiled_instruction": "<all required sections>",
      "confirmed_report_plan": "<report_plan>"
    },
    "output_contract": {
      "schema_version": "1.0",
      "title": "",
      "executive_summary": "",
      "sections": [{"id": "", "heading": "", "content": "", "evidence_refs": []}],
      "chart_recommendations": [{"id": "", "title": "", "purpose": "", "confirmed_field_bindings": [], "spec": {}, "evidence_refs": []}],
      "evidence_register": [],
      "limitations": []
    },
    "purpose": "Generate the final artifact-grounded structured analysis report. Do not emit HTML, scripts, remote data URLs, invented chart values, or fabricated file references."
  },
  "return_to": "l1-pN9-core-module"
}
```

After the Host Agent returns, re-enter Layer 1 and merge its actual response as `generated_report`. Verify required fields are present, evidence references resolve to supplied evidence, chart recommendations use only confirmed field bindings, and every declarative spec omits `data`, `url`, and `href`. Deliver the report without an acceptance gate; open report review only for explicitly requested approval or revision. A narrative or chart revision invalidates `generated_report` before regeneration. A report-plan revision also invalidates `report_plan`. Keep the immutable source artifact and confirmed evidence throughout.

## Execution Skill Routing

For `instruction_ready`, finish the existing `execution_instruction` and load `exec-pN9-report-generation`. Keep `executor.kind: main_model`, scope, evidence inputs and response format unchanged. L2 plans; the execution skill performs the planned analysis/report work and returns to L1. Do not realize the report in the planner or route execution through L3/L4. Gap selection still routes to the selected L3 designer. Failures return directly to L1.

## Next

Interaction Pathway: selected gap → L3 semantic design → L4 render → L1. Execution Pathway: ready plan → exec-pN9-report-generation (main_model) → L1, without L3/L4. All failures return to `l1-pN9-core-module`; Host Agent Return and Completion belong to L1 alone.