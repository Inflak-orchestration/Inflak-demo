---
name: l2-prompt-enhancement
description: "Use when: Layer 1 selects prompt-enhancement to improve a prompt directly or resolve a material content, direction, or structure decision."
---

# L2 Planner — Prompt Enhancement

## Workflow End Authority

Only L1 Router owns canonical workflow state and decides Completion with `decision: "end"`. L2 Planner never presents local completion as final. Eligible gaps enter L3 Designer on Interaction Pathway; `instruction_ready` directly invokes the selected executor on Execution Pathway without L3 or L4. Every result or failure returns directly to `l1-router`.

## Layer & Role

L2 Planner diagnoses gaps, selects interactions, and plans and directly invokes justified execution; it does not design widget semantics or render. For `prompt-enhancement` in the `prompt` task family, select an IAI paradigm, diagnose exactly one material per-edge gap if present, filter and rank registry candidates, and emit its exact `selected_widget_id` in the first gap of `planner_handoff`; otherwise emit `instruction_ready` and have the active main model realize the declared prompt production or bounded preparation. L3 Designer authors only the selected interaction's semantic contract.

## IAI Domain Binding

| Node | Meaning |
| --- | --- |
| H | Prompt author |
| T | Source and edited prompt |
| I | Content or structure editing interaction |
| Aug | Current submitted enhanced-prompt specification |
| A | Final enhanced prompt artifact |
| G | Main model synthesizing the prompt |

## Interaction Chains

| Chain ID | Paradigm / function | Ordered edges |
| --- | --- | --- |
| prompt-direct | Apply an explicit or delegated prompt transformation | `H→T, T→Aug, Aug→G, G→A` |
| prompt-content | Resolve content or prompt direction (`prompt_content_gap`) | `H→I, I→T, T→Aug, Aug→G, G→A` |
| prompt-structure | Resolve hierarchy, order, grouping or relationships (`prompt_structure_gap`) | `H→I, I→T, T→Aug, Aug→G, G→A` |

`H→T` supplies the source and change; `H→I` expresses a retained decision. `I→T` incorporates edited content/direction or structural relationships without reopening settled clauses; identical edge order does not merge those functions. `T→Aug` compiles current evidence and delegated latitude, `Aug→G` is L2's direct invocation of the active main model, and `G→A` returns the enhanced prompt, not a downstream task result.

## Diagnosis

Read state before/after a GenAI invocation and with prompt-only/artifact-grounded resources; assess inline or partial source text against the intended transformation. Use intent, current evidence, prior returns and scoped delegation to derive the material missing transfer BEFORE choosing a widget.

Prioritize gap detection and resolution. Assess every registered gap category against current evidence. Silence is not delegation. Known facts, submitted decisions, or explicit scoped user delegation may close a gap; record the evidence and scope, and identify applicability from material information needs rather than field presence. Resolve applicable open gaps through interaction before final artifact execution. After each return, re-enter Layer 1 and reassess remaining gaps. Reserve `instruction_ready` for evidence-backed closure across all relevant categories, or bounded prerequisite preparation that returns to Layer 1 without closing an unresolved user choice or executing the final artifact. Category assessment records applicability, missing material information and closure evidence; widget selection follows the next applicable open gap.

Cover `prompt_content_gap` (task, target use, content units, exclusions and direction) and `prompt_structure_gap` (hierarchy, order, grouping and precedence), checking supplied clauses and unresolved material relationships even when the author has not reserved a choice.

| gap_type | Condition | Edge | Interaction goal |
| --- | --- | --- | --- |
| `prompt_content_gap` | T lacks task-controlling content because material information remains unresolved by current evidence. | `I→T` | `refine_prompt_content` — edit the content units needed for the intended prompt. |
| `prompt_content_gap` | T lacks an operative framing because materially different prompt directions remain unresolved by current evidence. | `I→T` | `choose_prompt_direction` — choose the prompt's intended direction. |
| `prompt_structure_gap` | T lacks a governing relationship among settled units because their hierarchy, order, grouping or precedence remains undecided. | `I→T` | `refine_prompt_structure` — specify the unresolved structural relationship. |
| `instruction_ready` | All applicable gaps are resolved with evidence-backed content, direction and structure closure; alternatively, bounded prerequisite preparation returns to Layer 1 with user choices still open and no final enhanced-prompt execution. | `Aug→G` then `G→A` | Main model produces the enhanced prompt or bounded preparation, without executing its downstream task. |

Dependencies determine which open gap to resolve next: relationships need actual content units; compilation of evidenced settled decisions on `T→Aug` is model work. Technical/source failures and unsupported artifact-selection requests return directly to L1 Router without L3 rather than becoming semantic gaps; never relabel `I→A` selection as prompt direction.

## Widget Registry Routing

| Diagnosed gap | Selected widget ID / L3 skill | Interaction goal | Edge | Required return keys |
| --- | --- | --- | --- | --- |
| `prompt_content_gap` | `content-editor` / `l3-content-editor` | `refine_prompt_content` | `I→T` | `content_units`, `freeform_note` |
| `prompt_content_gap` | `option-selector` / `l3-option-selector` | `choose_prompt_direction` | `I→T` | `selected_ids`, `ranking`, `freeform_note` |
| `prompt_structure_gap` | `structure-editor` / `l3-structure-editor` | `refine_prompt_structure` | `I→T` | `structure`, `freeform_note` |

| Routing rule | Requirement |
| --- | --- |
| Eligibility | Hard-filter by exact planner, gap, goal, atomic edge, all required return keys (or explicitly sufficient agent-interpreted semantics), current artifact support, and available runtime capabilities/libraries. `planner_declared` cannot authorize unsupported fields. |
| Selection | Diagnose first and choose the next applicable open gap by dependencies, then select one eligible exact ID for that gap. The mappings identify candidate capabilities, not a fixed sequence; content editing and direction selection remain distinct goals within `prompt_content_gap`. Rank by exact semantic coverage, artifact specificity, return coverage, runtime fitness, stable registry order, then registry `id`; never weaken a hard constraint. |
| Prompt evidence | Use grounded direction options and actual content units for structural relationships; preserve settled clauses and exclusions. All three goals target `I→T`; never relabel `I→A` artifact selection as prompt direction. No goal targets a task tool, and prompt enhancement does not execute the downstream task. |
| No eligible entry | Return a nonterminal failure directly to L1 without L3: `reason: no_eligible_widget`, `planner_id: prompt-enhancement`, `diagnosed_gap` (chain/evidence/edge/goal/returns), `rejected_candidates` (IDs and failed constraints), `return_to: l1-router`. Never substitute an ineligible widget or fake readiness. |

## Gap Handoff

Emit one request; the edge source must occur in `source_nodes` and its destination must equal `target_node`. Pending I is not submitted input. Layer 3 preserves `chain_id` and `reason`: source/transfer/target/closure evidence and why guessing is unjustified; copy no contract or renderer metadata. This example assumes the supplied source rubrics and reserved precedence decision are current:

```json
{
  "handoff_type": "planner_handoff",
  "planner_id": "prompt-enhancement",
  "planner_decision": "gap_open",
  "gap_requests": [{
    "chain_id": "prompt-structure",
    "gap_type": "prompt_structure_gap",
    "interaction_goal": "refine_prompt_structure",
    "iai_binding": {"source_nodes": ["I"], "maps_to_edge": "I→T", "target_node": "T", "reason": "On I→T, I lacks the author's reserved precedence decision, leaving T's existing Accuracy and Brevity clauses without a governing relationship; guessing changes which constraint is sacrificed. Returned structure supplies that precedence to T without reopening settled content."},
    "expected_return": {"structure": {}, "freeform_note": ""},
    "selected_widget_id": "structure-editor",
    "display_context": {
      "source_prompt": "Accuracy: retain all factual qualifications. Brevity: stay under 50 words.",
      "user_text": "Make one rubric override the other, but let me choose which."
    },
    "order": 1,
    "depends_on_previous": false
  }],
  "return_to": "l1-router"
}
```

For `refine_prompt_content`, use `content-editor` with `content_units: []`, `freeform_note: ""`; for `choose_prompt_direction`, use `option-selector` with grounded `display_context.options` and `selected_ids: []`, `ranking: []`, `freeform_note: ""`. Both use `prompt-content` and `prompt_content_gap` on `I→T`; neither targets a task tool.

## Inputs (from core_handoff and widget registry)

- `selected_planner: prompt-enhancement`; `state_snapshot` with required `user_text`.
- Consume optional `source_prompt`, `prompt_content`, `prompt_structure`, `enhanced_prompt`, and `prior_returns` from `state_snapshot`.
- When working from an existing prompt artifact, consume its actual content/reference as supplied in `source_prompt` or `enhanced_prompt`; do not invent a required standalone artifact field absent from this planner's registry.
- Consume the routing projection from `registry/widgets.json`: ID, planner/gap/goal/edge declarations, supported returns and semantics, artifact support, capability/library requirements; check current host availability and actual source context, not assumed dependencies.

## Procedure

1. Inspect `core_handoff`, source, target use and prior returns; position both axes and assess every registered category for applicability, missing material information and closure evidence, preserving authored clauses/exclusions.
2. Select the next applicable open gap by dependencies, then its chain; trace source to target and why guessing is unjustified. Bound prerequisite preparation while preserving unresolved choices.
3. For the selected gap, filter/rank and emit one exact selected-widget request with `chain_id`, or return a structured failure directly to L1 without L3. Emit `instruction_ready` with `executor.kind: main_model` only for evidence-backed closure across relevant categories or bounded prerequisite preparation; open gaps prohibit final prompt synthesis.
4. Interaction Pathway sends an eligible selected gap to L3 Designer then L4 Renderer. Execution Pathway has L2 directly invoke the active main model with the declared `execution_instruction`, without L3 or L4. Every interaction return, actual result or failure immediately re-enters L1 to reassess all categories before another action.

## Output (planner_handoff)

`instruction_ready` is a planner decision, never a registered gap or workflow completion. This example assumes the user supplied the source "Examples: use the two supplied samples. Output: return a JSON object." and requested: "Only move Output before Examples. Preserve both clauses verbatim and choose clear headings; return the enhanced prompt, not its downstream result." Content is settled by exact preservation, structure by the specified order, and delegation covers headings only:

```json
{
  "handoff_type": "planner_handoff",
  "planner_id": "prompt-enhancement",
  "planner_decision": "instruction_ready",
  "execution_instruction": {
    "executor": {"kind": "main_model"},
    "parameters": {"source_prompt": "Examples: use the two supplied samples. Output: return a JSON object.", "compiled_instruction": "Move Output before Examples. Preserve both clauses verbatim and choose clear headings; do not execute this prompt."},
    "purpose": "Content and direction are closed by the user's supplied Examples and Output clauses and exact-preservation, reordering-only scope; structure is closed by the explicit Output-before-Examples order. Delegation covers headings only. Produce the enhanced prompt and return to Layer 1 without executing the downstream task."
  },
  "return_to": "l1-router"
}
```

## Must

- Ground the transformation in intent, current source evidence, collected constraints and delegation; preserve authored prompt material/exclusions and distinguish authored from proposed values.
- For one diagnosed gap, select exactly one entry passing every hard constraint, preserve its exact ID, and use deterministic ranking.
- When instruction-ready, directly invoke the active main model with the declared instruction to produce a usable enhanced prompt from justified current state.

## Must Not

- Do not add a generic approval checkbox or invent redundant gaps; preserve evidence-backed settled decisions unless relevant dependent evidence changes.
- Do not silently fill unresolved material information or invent task facts and user preferences.
- Do not turn prompt enhancement into downstream task execution or relabel artifact selection as direction selection.
- Do not author widget-contract fields, render UI, invoke an executor before `instruction_ready`, bypass L3 for an eligible interaction, or decide Completion.
- Do not invent registry IDs, duplicate registry-owned metadata, or relax hard eligibility constraints.

## Tools

L2 Planner selects `executor.kind: main_model` for prompt production and directly invokes the active session model with the declared `execution_instruction`; it declares no task-tool executor. Return the actual enhanced prompt or failure directly to L1 without executing its downstream task. L3 Designer is not an executor. L4 Renderer alone owns `render_html_widget`.

## Stop / Continue / Escape

- **Stop:** End this local pass after handing an eligible gap to L3 or returning an actual execution result or failure directly to L1; only L1 decides Completion.
- **Continue:** A valid widget or execution return supplies new state; Layer 1 reconstructs it before selecting another pass.
- **Escape:** A referenced source, indispensable target-use decision, or capability is unavailable or refused and cannot safely be inferred; return directly to L1 without L3. Generation/tool failures also escape, never become user interaction gaps.

## Next

Interaction Pathway: send an eligible open gap with `selected_widget_id` to L3 Designer for validation and interaction design, then L4 Renderer. Execution Pathway: after `instruction_ready`, L2 directly invokes the selected executor with the declared instruction, without L3, L4, or a separate executor skill. Routing failures return directly to L1 without L3. All actual results and failures return to `l1-router`, not directly to this planner; only L1 decides Completion.
