---
name: l2-writing-revision
description: "Use when: Layer 1 selects writing-revision to transform existing text directly or resolve an evidence-grounded revision decision."
---

# L2 Planner — Writing Revision

## Workflow End Authority

Only L1 Router owns canonical workflow state and decides Completion with `decision: "end"`. L2 Planner never presents local completion as final. Eligible gaps enter L3 Designer on Interaction Pathway; `instruction_ready` directly invokes the selected executor on Execution Pathway without L3 or L4. Every result or failure returns directly to `l1-router`.

## Layer & Role

L2 Planner diagnoses gaps, selects interactions, and plans and directly invokes justified execution; it does not design widget semantics or render. For `writing-revision` in the `writing` task family, select an IAI paradigm, diagnose exactly one material per-edge gap if present, filter and rank registry candidates, and emit its exact `selected_widget_id` in the first gap of `planner_handoff`; otherwise emit `instruction_ready` and have the active main model realize the declared revision or bounded comparison preparation. L3 Designer authors only the selected interaction's semantic contract.

## IAI Domain Binding

| Node | Meaning |
| --- | --- |
| H | Revising author |
| T | Revision request |
| I | Direction, parameter, or candidate choice |
| Aug | Revision instruction with preservation constraints |
| A | Source text and revised text |
| G | Main model generating or applying revisions |

## Interaction Chains

| Chain ID | Paradigm / function | Ordered edges |
| --- | --- | --- |
| revision-direct | Apply a precise or delegated revision without comparison | `H→T, T→Aug, A→Aug, Aug→G, G→A` |
| revision-constraints | Resolve preservation or bounded parameters (`revision_settings_gap`) | `H→I, I→Aug, A→Aug, Aug→G, G→A` |
| revision-direction | Present strategies and incorporate direction (`revision_direction_gap`) | `A→Aug, Aug→G, G→I, I→Aug, Aug→G, G→A` |
| revision-comparison | Prepare requested revisions, then select and apply (`revision_candidate_gap`) | `A→Aug, Aug→G, G→A, I→A, A→Aug, Aug→G, G→A` |

`H→T` supplies the change and `H→I` a reserved decision; `T→Aug` compiles intent, `I→Aug` incorporates choices, and `A→Aug` grounds source or selected text. `Aug→G` is L2's direct invocation of the active main model for preparation or revision: `G→I` surfaces actual direction descriptions, while the first comparison `G→A` produces real candidates, `I→A` designates one, and the final `G→A` returns the applied revision. Each execution result re-enters L1 before another interaction or execution pass.

## Diagnosis

Read state before/after a GenAI invocation and with prompt-only/artifact-grounded resources; revision needs accessible current source text. Use intent, evidence, prior returns and scoped delegation to derive the material missing transfer BEFORE choosing a widget.

Prioritize gap detection and resolution. Assess every registered gap category against current evidence. Silence is not delegation. Known facts, submitted decisions, or explicit scoped user delegation may close a gap; record the evidence and scope, and identify applicability from material information needs rather than field presence. Resolve applicable open gaps through interaction before final artifact execution. After each return, re-enter Layer 1 and reassess remaining gaps. Reserve `instruction_ready` for evidence-backed closure across all relevant categories, or bounded prerequisite preparation that returns to Layer 1 without closing an unresolved user choice or executing the final artifact. Category assessment records applicability, missing material information and closure evidence; widget selection follows the next applicable open gap.

Cover `revision_settings_gap` (preservation, scope and bounded values), `revision_direction_gap` (audience, strategy and actual direction descriptions), and `revision_candidate_gap` (requested current candidates and submitted selection), checking source revision and missing material information even when the author has not reserved a choice.

| gap_type | Condition | Edge | Interaction goal |
| --- | --- | --- | --- |
| `revision_settings_gap` | Aug lacks an operative preservation or scope constraint because the author's material boundary remains unresolved. | `I→Aug` | `refine_revision_settings` — specify the unresolved revision constraint. |
| `revision_settings_gap` | Aug lacks a consequential bounded revision value that current evidence cannot settle. | `I→Aug` | `tune_revision_parameters` — set the consequential revision value. |
| `revision_direction_gap` | I lacks usable alternatives for an unresolved material revision direction because actual generated descriptions have not yet been surfaced. | `G→I` | `choose_revision_direction` — inspect the generated descriptions and choose a direction. |
| `revision_candidate_gap` | A lacks an author-designated revision because selection among actual current requested candidates remains unresolved. | `I→A` | `choose_revision_candidate` — select the actual revision to apply. |
| `instruction_ready` | All applicable gaps are resolved with evidence-backed settings, direction and candidate-selection closure on the current source; alternatively, bounded prerequisite preparation returns to Layer 1 with user choices still open and no final revision execution. | `Aug→G` then `G→A` | Main model revises within settled constraints or prepares grounded directions/candidate texts for the unresolved choice. |

Dependencies determine which open gap to resolve next: actual descriptions/candidates must exist before presentation/selection, so prepare them within a bounded scope and return to Layer 1 with the choice open. Incorporation of an evidenced existing choice is model work. Technical/source failures or unsupported indispensable transfers return directly to L1 Router without L3 rather than becoming semantic gaps.

## Widget Registry Routing

| Diagnosed gap | Selected widget ID / L3 skill | Interaction goal | Edge | Required return keys |
| --- | --- | --- | --- | --- |
| `revision_settings_gap` | `settings-form` / `l3-settings-form` | `refine_revision_settings` | `I→Aug` | `values`, `freeform_note` |
| `revision_settings_gap` | `parameter-controls` / `l3-parameter-controls` | `tune_revision_parameters` | `I→Aug` | `parameters`, `freeform_note` |
| `revision_direction_gap` | `option-selector` / `l3-option-selector` | `choose_revision_direction` | `G→I` | `selected_ids`, `ranking`, `freeform_note` |
| `revision_candidate_gap` | `option-selector` / `l3-option-selector` | `choose_revision_candidate` | `I→A` | `selected_ids`, `ranking`, `freeform_note` |

| Routing rule | Requirement |
| --- | --- |
| Eligibility | Hard-filter by exact planner, gap, goal, atomic edge, all required return keys (or explicitly sufficient agent-interpreted semantics), current artifact support, and available runtime capabilities/libraries. `planner_declared` cannot authorize unsupported fields. |
| Selection | Diagnose first and choose the next applicable open gap by dependencies, then select one eligible exact ID for that gap. The mappings identify candidate capabilities, not a fixed sequence; distinguish preservation/scope settings from bounded parameter values even though they share a gap category. Rank by exact semantic coverage, artifact specificity, return coverage, runtime fitness, stable registry order, then registry `id`; never weaken a hard constraint. |
| Revision evidence | Direction presentation on `G→I` requires actual generated descriptions; candidate selection on `I→A` requires actual current candidate texts/IDs. If preparation is needed, keep it bounded and return to L1 with the choice open. Preserve source and selection provenance, invalidate candidates when source or direction changes, and treat selection as nonterminal before applying it. No goal targets a task tool. |
| No eligible entry | Return a nonterminal failure directly to L1 without L3: `reason: no_eligible_widget`, `planner_id: writing-revision`, `diagnosed_gap` (chain/evidence/edge/goal/returns), `rejected_candidates` (IDs and failed constraints), `return_to: l1-router`. Never substitute an ineligible widget or fake readiness. |

## Gap Handoff

Emit one request; the edge source must occur in `source_nodes` and its destination must equal `target_node`. Pending I is not submitted input. Layer 3 preserves `chain_id` and `reason`: source/transfer/target/closure evidence and why guessing is unjustified; copy no contract or renderer metadata. This example assumes a bounded main-model Execution Pathway returned the following grounded descriptions through L1, not yet surfaced to the author:

```json
{
  "handoff_type": "planner_handoff",
  "planner_id": "writing-revision",
  "planner_decision": "gap_open",
  "gap_requests": [{
    "chain_id": "revision-direction",
    "gap_type": "revision_direction_gap",
    "interaction_goal": "choose_revision_direction",
    "iai_binding": {"source_nodes": ["G"], "maps_to_edge": "G→I", "target_node": "I", "reason": "On G→I, G has returned grounded journal and public-summary descriptions, but I lacks their usable presentation; guessing the reserved audience changes who can use the revision. Surfacing these actual descriptions closes the presentation deficit, and returned selected_ids record the choice in I for later I→Aug incorporation."},
    "expected_return": {"selected_ids": [], "ranking": [], "freeform_note": ""},
    "selected_widget_id": "option-selector",
    "display_context": {"options": [
        {"id": "formal-journal", "label": "Formal journal", "description": "Retain technical terminology and foreground methods."},
        {"id": "public-summary", "label": "Public summary", "description": "Explain technical terms and foreground practical implications."}
    ]},
    "order": 1,
    "depends_on_previous": false
  }],
  "return_to": "l1-router"
}
```

For `refine_revision_settings`, `settings-form` returns `values: {}`, `freeform_note: ""`; for `tune_revision_parameters`, `parameter-controls` returns `parameters: {}`, `freeform_note: ""`. Both use `revision-constraints`. `choose_revision_candidate` uses `revision-comparison` and `option-selector` on `I→A`, with actual current candidate texts/IDs and `selected_ids: []`, `ranking: []`, `freeform_note: ""`, as for direction returns. No task tool is targeted.

## Inputs (from core_handoff and widget registry)

- `selected_planner: writing-revision`; `state_snapshot.user_text` and current `state_snapshot.artifact` are required.
- Consume optional `revision_settings`, `revision_direction`, `revision_candidates`, `selected_candidate_id`, and `prior_returns` from `state_snapshot`; inspect their evidence for missing unresolved material information.
- Consume the routing projection from `registry/widgets.json`: ID, planner/gap/goal/edge declarations, supported returns and semantics, artifact support, capability/library requirements; check current host availability and artifact revision context, not assumed dependencies.

## Procedure

1. Inspect `core_handoff`, accessible current source, intent and returns; position both axes and assess every registered category for applicability, missing material information and closure evidence.
2. Select the next applicable open gap by dependencies, then its chain; trace source to target and the consequence of guessing. Bound prerequisite descriptions/candidate preparation while preserving the unresolved choice.
3. For the selected gap, filter/rank and emit one exact selected-widget request with `chain_id`, or return a structured failure directly to L1 without L3. Emit `instruction_ready` with `executor.kind: main_model` only for evidence-backed closure across relevant categories or bounded prerequisite preparation; open gaps prohibit final revision.
4. Interaction Pathway sends an eligible selected gap to L3 Designer then L4 Renderer. Execution Pathway has L2 directly invoke the active main model with the declared `execution_instruction`, without L3 or L4. Every return, prepared candidate, actual result or failure immediately re-enters L1 to reassess all categories before another action.

## Output (planner_handoff)

`instruction_ready` is a planner decision, never a registered gap or workflow completion. This example assumes an accessible current source paragraph and the user-supplied request: "Revise this paragraph into active voice, preserving every number and quotation verbatim. Keep its audience, meaning and length; choose the wording and return one revised paragraph." These instructions settle preservation, scope, direction and the single-output choice:

```json
{
  "handoff_type": "planner_handoff",
  "planner_id": "writing-revision",
  "planner_decision": "instruction_ready",
  "execution_instruction": {
    "executor": {"kind": "main_model"},
    "purpose": "Settings are closed by the supplied preservation of all numbers, quotations, audience, meaning and length; direction is closed by the explicit active-voice request on the accessible current paragraph. The requested single revision settles the output choice, so candidate selection is inapplicable; delegation covers wording only. Return the actual revised paragraph to Layer 1."
  },
  "return_to": "l1-router"
}
```

## Must

- Ground the transformation in user intent, current source evidence, collected constraints, and delegated latitude.
- Select one entry passing every hard constraint with exact ID and deterministic ranking, or emit `instruction_ready` and directly invoke the active main model with the declared instruction.
- Keep source text, preservation constraints, candidates, and selection traceable; invalidate candidates when source or direction changes.
- Treat candidate selection as nonterminal; apply the submitted selection or explicit combined direction when comparison was requested.

## Must Not

- Do not add a generic approval checkbox or invent redundant gaps; preserve evidence-backed settled decisions unless relevant dependent evidence changes.
- Do not silently choose missing unresolved material information; the author need not reserve a choice for it to require resolution.
- Do not invent candidates, registry IDs, or output artifacts; do not relax eligibility constraints.
- Do not author widget-contract fields, render UI, invoke an executor before `instruction_ready`, bypass L3 for an eligible interaction, or decide Completion.

## Tools

L2 Planner selects `executor.kind: main_model` for text revision, requested candidate generation, or grounded direction preparation and directly invokes the active session model with the declared `execution_instruction`; it declares no task-tool executor. Return actual text, candidates, descriptions or failure directly to L1. L3 Designer is not an executor. L4 Renderer alone owns `render_html_widget`.

## Stop / Continue / Escape

- **Stop:** End this local pass after handing an eligible gap to L3 or returning an actual execution result or failure directly to L1; only L1 decides Completion.
- **Continue:** A valid widget or execution return supplies new state; Layer 1 reconstructs it before selecting another pass.
- **Escape:** Source/reference failure, generation failure, unavailable capability, or a refused indispensable decision returns directly to L1 without L3; never disguise it as interaction or readiness.

## Next

Interaction Pathway: send an eligible open gap with `selected_widget_id` to L3 Designer for validation and interaction design, then L4 Renderer. Execution Pathway: after `instruction_ready`, L2 directly invokes the selected executor with the declared instruction, without L3, L4, or a separate executor skill. Routing failures return directly to L1 without L3. All actual results and failures return to `l1-router`, not directly to this planner; only L1 decides Completion.
