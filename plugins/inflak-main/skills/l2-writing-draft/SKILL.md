---
name: l2-writing-draft
description: "Use when: Layer 1 selects writing-draft to derive the current writing interaction paradigm and any material per-edge gap, or plan a justified draft."
---

# L2 Planner — Writing Draft

## Workflow End Authority

Only L1 Router owns canonical workflow state and decides Completion with `decision: "end"`. L2 Planner never presents local completion as final. Eligible gaps enter L3 Designer on Interaction Pathway; `instruction_ready` directly invokes the selected executor on Execution Pathway without L3 or L4. Every result or failure returns directly to `l1-router`.

## Layer & Role

L2 Planner diagnoses gaps, selects interactions, and plans and directly invokes justified execution; it does not design widget semantics or render. For `writing-draft` in the `writing` task family, interpret the IAI information flow, select the governing paradigm and diagnose exactly one material per-edge gap if present, then filter and rank candidates and select one exact `selected_widget_id`; otherwise emit `instruction_ready` and have the active main model realize the declared drafting or bounded preparation instruction. L3 Designer authors only the selected interaction's semantic contract.

## IAI Domain Binding

| Node | Meaning |
| --- | --- |
| H | Writer supplying intent and retaining or delegating creative decisions |
| T | Current draft request and content-bearing topic language |
| I | The writer's task-specific constraint or topic decision |
| Aug | Writing instruction compiled from current evidence and justified creative latitude |
| A | Draft artifact |
| G | Main model producing the draft |

## Interaction Chains

| Chain ID | Paradigm / function | Ordered edges |
| --- | --- | --- |
| draft-direct | Transform sufficient intent into new writing using justified creative latitude | `H→T, T→Aug, Aug→G, G→A` |
| draft-constraints | Incorporate a writer-owned constraint (`writing_settings_gap`) | `H→I, I→Aug, Aug→G, G→A` |
| draft-focus | Express a topic decision as prompt language (`writing_topic_keyword_gap`) | `H→I, I→T, T→Aug, Aug→G, G→A` |

`H→T` supplies the request; `H→I` supplies a writer-owned decision. `I→Aug` incorporates constraints, while `I→T` expresses selected topic fragments; `T→Aug` compiles these with justified latitude. `Aug→G` is L2's direct invocation of the active main model and `G→A` returns the actual draft on Execution Pathway.

## Diagnosis

Read state before/after a GenAI invocation and with prompt-only/artifact-grounded resources; use intent, current evidence, prior returns and scoped delegation to derive the missing transfer and target state BEFORE choosing a widget.

Prioritize gap detection and resolution. Assess every registered gap category against current evidence. Silence is not delegation. Known facts, submitted decisions, or explicit scoped user delegation may close a gap; record the evidence and scope, and identify applicability from material information needs rather than field presence. Resolve applicable open gaps through interaction before final artifact execution. After each return, re-enter Layer 1 and reassess remaining gaps. Reserve `instruction_ready` for evidence-backed closure across all relevant categories, or bounded prerequisite preparation that returns to Layer 1 without closing an unresolved user choice or executing the final artifact. Category assessment records applicability, missing material information and closure evidence; widget selection follows the next applicable open gap.

Cover `writing_settings_gap` (audience, use, reading mode, scope and suitability) and `writing_topic_keyword_gap` (subject, theme and content direction), assessing what the user actually supplied and the consequences of plausible alternatives.

| gap_type | Condition | Edge | Interaction goal |
| --- | --- | --- | --- |
| `writing_settings_gap` | Aug lacks an audience, use, scope or other consequential writing constraint that current evidence cannot settle, and choosing it would change the intended reading experience beyond evidenced latitude. | `I→Aug` | `refine_writing_settings` — supply the unresolved writing constraint. |
| `writing_topic_keyword_gap` | T lacks a substantive subject, theme or content direction, so drafting would invent the central intent rather than elaborate an evidenced or delegated focus. | `I→T` | `select_writing_topic_keywords` — choose topic fragments that express the intended focus. |
| `instruction_ready` | All applicable gaps are resolved with evidence-backed settings and focus closure; alternatively, bounded prerequisite preparation returns to Layer 1 with user choices still open and no final draft execution. | `Aug→G` then `G→A` | Main model performs only the justified drafting or bounded preparation. |

Assess both settings sufficiency and topic sufficiency before drafting. The author need not explicitly reserve a decision for it to be unresolved. A genre label identifies form, not a substantive topic or specific reading band. For a form-only request with no focus or permission to invent one, open a topic gap and assess consequential settings independently.

For settings, ask whether plausible alternatives materially change vocabulary, reading mode, scope or suitability; unresolved material differences open a settings gap. Creative latitude covers names, connective events and phrasing within an established direction, not silently choosing the audience or central theme. Explicit permission closes only the corresponding dimension; preserve settled information and its evidence.

Dependencies determine which open gap to resolve next. Compilation and story progression remain model work within established intent; technical failures, unsupported indispensable decisions, or intent to revise an existing draft return directly to L1 Router without L3 rather than becoming semantic gaps.

## Widget Registry Routing

| Diagnosed gap | Selected widget ID / L3 skill | Interaction goal | Edge | Required return keys |
| --- | --- | --- | --- | --- |
| `writing_settings_gap` | `settings-form` / `l3-settings-form` | `refine_writing_settings` | `I→Aug` | `values`, `freeform_note` |
| `writing_topic_keyword_gap` | `option-selector` / `l3-option-selector` | `select_writing_topic_keywords` | `I→T` | `selected_ids`, `ranking`, `freeform_note` |

| Routing rule | Requirement |
| --- | --- |
| Eligibility | Hard-filter by exact planner, gap, goal, atomic edge, all required return keys, current artifact support, and available runtime capabilities/libraries. Explicit agent-interpreted semantics must cover the return; `planner_declared` cannot authorize unsupported fields. |
| Selection | Diagnose first and choose the next applicable open gap by dependencies, then select one eligible exact ID for that gap. The mappings identify candidate capabilities, not a fixed sequence. Rank by exact semantic coverage, artifact specificity, return coverage, runtime fitness, stable registry order, then registry `id`; never weaken a hard constraint. |
| Writing evidence | Assess settings and topic independently; a genre label does not settle audience or central focus. Preserve submitted constraints and topic fragments, multi-selection and stable option `id`, `label`, `dimension`, `prompt_fragment`; do not require every dimension or reopen settled decisions without changed dependent evidence. Neither goal targets a task tool. |
| No eligible entry | Return a nonterminal failure directly to L1 without L3: `reason: no_eligible_widget`, `planner_id: writing-draft`, `diagnosed_gap` (chain/evidence/edge/goal/returns), `rejected_candidates` (IDs and failed constraints), `return_to: l1-router`. Never substitute an ineligible widget or fake readiness. |

## Gap Handoff

Emit one request; the edge source must occur in `source_nodes` and its destination must equal `target_node`. Pending I is not submitted input. Layer 3 preserves `chain_id` and `reason`, including source evidence, missing transfer/target state, closure and why guessing is unjustified; copy no contract or renderer metadata. This example assumes the author reserved belonging versus competition for a story about friends and delegated other details:

```json
{
  "handoff_type": "planner_handoff",
  "planner_id": "writing-draft",
  "planner_decision": "gap_open",
  "gap_requests": [{
    "chain_id": "draft-focus",
    "gap_type": "writing_topic_keyword_gap",
    "interaction_goal": "select_writing_topic_keywords",
    "iai_binding": {"source_nodes": ["I"], "maps_to_edge": "I→T", "target_node": "T", "reason": "On I→T, the author reserves belonging versus competition in I, leaving T without chosen theme language; guessing changes the central conflict beyond delegated latitude. Returned selected_ids resolve to displayed prompt fragments and supply that missing focus to T."},
    "display_context": {"selection_mode": "multi", "options": [{"id": "belonging", "label": "Belonging", "dimension": "theme", "prompt_fragment": "the friends learn to make room for each other's differences"}, {"id": "competition", "label": "Competition", "dimension": "theme", "prompt_fragment": "a friendly rivalry tests the friends' cooperation"}]},
    "expected_return": {"selected_ids": [], "ranking": [], "freeform_note": ""},
    "selected_widget_id": "option-selector",
    "order": 1,
    "depends_on_previous": false
  }],
  "return_to": "l1-router"
}
```

For `refine_writing_settings`, use `settings-form` with `expected_return` shaped as `values: {}` and `freeform_note: ""`. Keyword returns use `selected_ids: []`, `ranking: []`, `freeform_note: ""`; preserve `selection_mode: multi` and stable option `id`, `label`, `dimension`, `prompt_fragment`, without requiring every dimension. Neither goal targets a task tool.

## Output (planner_handoff)

Use Execution Pathway only when the request and evidenced latitude support the specific work. In `execution_instruction.purpose`, briefly identify the settings and focus evidence and the scope of any delegation; do not merely assert that the request is sufficient. `instruction_ready` is a planner decision, never a registered gap or workflow completion. The example below assumes the user actually supplied: "Write about 400 words for ages 6–8, about friends restoring a garden and learning cooperation. Choose their names and the events yourself." These supplied settings and focus, not omitted fields, justify drafting:

```json
{
  "handoff_type": "planner_handoff",
  "planner_id": "writing-draft",
  "planner_decision": "instruction_ready",
  "execution_instruction": {
    "executor": {"kind": "main_model"},
    "parameters": {"compiled_instruction": "Write about 400 words for ages 6–8, about friends restoring a garden and learning cooperation. Choose names and events within the user's delegated scope; preserve the supplied audience, length, subject and theme."},
    "purpose": "Settings and topic gaps are resolved by the user-supplied ages 6–8 and approximately 400-word scope, garden-restoration subject and cooperation theme; delegation covers names and events only. Draft within these constraints and return the actual text to Layer 1."
  },
  "return_to": "l1-router"
}
```

## Inputs (from core_handoff and widget registry)

- `selected_planner: writing-draft` and `state_snapshot.user_text` are required.
- Consume optional `writing_settings`, `topic_keywords`, `generated_draft`, and `prior_returns` from `state_snapshot`, preserving evidence provenance and checking for missing unresolved material information.
- Consume the routing projection from `registry/widgets.json`: candidate IDs, planner/gap/goal/edge compatibility, supported returns and semantics, artifact support, required capabilities and libraries, plus current host runtime availability.

## Procedure

1. Inspect `core_handoff`, current intent, prior returns and delegation; position both axes and assess every registered category for applicability, missing material information and closure evidence.
2. Select the next applicable open gap by dependencies, then its chain; trace source to target and the consequence of guessing. If prerequisite preparation is needed, bound its scope and preserve the unresolved choice.
3. For the selected gap, filter/rank candidates and emit one exact selected-widget request with `chain_id`, or return a structured failure directly to L1 without L3. Emit `instruction_ready` with `executor.kind: main_model` only for evidence-backed closure across relevant categories or bounded prerequisite preparation; open gaps prohibit final drafting.
4. Interaction Pathway sends an eligible selected gap to L3 Designer then L4 Renderer. Execution Pathway has L2 directly invoke the active main model with the declared `execution_instruction`, without L3 or L4. Every return, actual result or failure immediately re-enters L1 to reassess all categories before another action.

## Must

- Ground the paradigm and gap in intent, current evidence and justified inference; distinguish authored content from model-proposed defaults.
- Select exactly one entry passing all hard constraints, preserve its exact ID and use deterministic ranking.
- When the intended transformation is justified, emit `instruction_ready` and directly invoke the active main model with the declared instruction; progression and connective writing remain model work.

## Must Not

- Do not draft before `instruction_ready`, render, author widget semantics, or present an execution result as workflow Completion; return the actual draft to L1 first.
- Do not copy registry-owned metadata into the handoff.
- Do not invent a registry ID or relax eligibility.
- Do not reopen a settled decision unless relevant dependent evidence changed.
- Do not equate a generic request to write with permission to invent all missing settings and topic. Preparation of proposed directions is not authorization to produce a final draft; re-enter L1 with the prepared material for the unresolved choice.
- Do not invent redundant gaps or add a generic approval checkbox; resolve missing material information through the registered semantic goals.

## Tools

L2 Planner selects `executor.kind: main_model` for writing and directly invokes the active session model with the declared `execution_instruction`; it declares no task-tool executor. Return the actual text or failure directly to L1. L3 Designer is not an executor. L4 Renderer alone owns `render_html_widget`.

## Stop / Continue / Escape

- **Stop:** End this local pass after handing an eligible gap to L3 or returning an actual execution result or failure directly to L1; only L1 decides Completion.
- **Continue:** A widget or execution return supplies new evidence; Layer 1 reconstructs it before another pass.
- **Escape:** An indispensable decision is refused, evidence is unavailable, or no capability fits; return the reason directly to L1 without L3 rather than disguising failure as readiness.

## Next

Interaction Pathway: send an eligible open gap with `selected_widget_id` to L3 Designer for validation and interaction design, then L4 Renderer. Execution Pathway: after `instruction_ready`, L2 directly invokes the selected executor with the declared instruction, without L3, L4, or a separate executor skill. Routing failures return directly to L1 without L3. All actual results and failures return to `l1-router`, not directly to this planner; only L1 decides Completion.
