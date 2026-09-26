# L2 Planner Skill Contract

Authoring-only documentation for generating or reviewing task-specific L2 Planner skills from an Add task pack JSON specification. This contract is not a callable skill, is not part of SDK skill discovery, and is not a runtime prerequisite. Runtime planners use their own operational skills and locally defined handoffs, not a load of this document.

## Layer & Role

Defines the invariant structure and semantics of every generated L2 Planner skill. The task-pack JSON supplies domain-specific bindings, chains, gaps, tools, and guardrails; a routing projection of `registry/widgets.json` supplies eligible widget candidates. The generator supplies no additional task assumptions.

The cross-layer ownership rules and interface summaries are defined in [CONTRACT.md](CONTRACT.md). This detailed contract specializes them for generated L2 documents. Compatibility readers may accept legacy shapes outside the ready bundle during migration, but new authoring emits the selected-widget routing shape defined here.

**Purpose — L2 Planner owns interaction-paradigm planning, widget routing, and execution planning and invocation.** Reading the task state along the two IAI axes — *interaction timing* (before vs. after a GenAI invocation) and *user resources* (prompt-only vs. artifact-grounded) — together with intent and prior returns, it selects the **atomic interaction paradigm** for this pass and diagnoses exactly one open per-edge gap. For that gap it filters and ranks the provided widget registry candidates by planner, gap, interaction goal, IAI edge, expected-return coverage, artifact context, and runtime availability, then selects one eligible entry and emits its exact registry `id` as `gap_requests[0].selected_widget_id`. A `gap` remains the per-edge decomposition of the paradigm; the selected ID is the routing decision for realizing that gap.

When the augmented instruction is ready, L2 Planner emits an execution plan and directly calls its selected executor: `executor.kind: main_model` uses the active main model; `executor.kind: tool` uses a real registered callable allowed for the planner. It preserves the complete parameters, purpose, and business fields and returns actual results or failures to L1 Router. A skill id is not itself a backend function. L2 does not author the selected widget's semantic contract or render UI.

**Main-specific scope.** The proactive all-category assessment, evidence-backed closure, and bounded-preparation rules in the diagnosis method apply to all five `inflak-main` planners. Every pass classifies every registered category as `not applicable`, `resolved`, or `open`, with task-grounded applicability, missing material information, and closure evidence. One selected gap limits the current handoff, not assessment coverage. Other plugins retain their task-specific diagnosis behavior and runtime APIs; these rules must not impose main's categories or a new workflow on them.

## Workflow End Authority

Only L1 Router owns the canonical workflow state and decides Completion. L2 Planner plans the current pass, routes an eligible gap to L3 Designer or directly invokes its selected executor, and never presents planner-local completion as final. Results return through the actual plugin L1, which reconstructs the newest state and chooses the next planner route, Host Agent Return, or Completion.

## Layer Routing

The four pathways are Interaction Pathway, Execution Pathway, Host Agent Return, and Completion. The layers are L1 Router, L2 Planner, L3 Designer, and L4 Renderer.

L2 Planner decides whether the current pass needs user interaction, main-model work, one or more registered tools, inspection, preparation, or execution. The Interaction Pathway sends the exact selected gap through L3 Designer and L4 Renderer before returning to L1. The Execution Pathway is `user/return -> L1 -> L2 plan -> execute/realize -> L1`: L2 directly invokes the selected executor. L2 never renders UI, produces the final workflow response, or decides Completion. L2 routing and execution failures return directly to L1.

## Input Contract

The generator receives one validated task-pack JSON object with these fields:

```json
{
  "pack_slug": "string",
  "title": "string",
  "description": "string",
  "task_family": "string",
  "node_bindings": {
    "H": "string",
    "T": "string",
    "I": "string",
    "Aug": "string",
    "A": "string",
    "G": "string"
  },
  "chains": [
    {
      "id": "string",
      "name": "string",
      "function": "string",
      "edges": [{"type": "H→T", "explanation": "string"}]
    }
  ],
  "gaps": [
    {
      "name": "string",
      "chain_id": "string",
      "edge": "I→Aug",
      "goal": "string",
      "problem": "string",
      "cause": "string"
    }
  ],
  "tools": ["string"],
  "guardrails": ["string"],
  "widget_registry_candidates": [
    {
      "id": "string",
      "compatible_planners": ["string"],
      "gap_categories": ["string"],
      "interaction_goals": ["string"],
      "iai_edges": ["I→Aug"],
      "expected_return_types": ["string"],
      "return_mode": "schema|agent_interpreted",
      "supported_artifact_types": ["string"],
      "runtime_capabilities": ["string"],
      "external_libraries": ["string"],
      "runtime_available": true
    }
  ]
}
```

`widget_registry_candidates` is the L2 routing projection of entries supplied from the plugin's `registry/widgets.json`; `runtime_available` is the host's current availability annotation. Optional arrays may be empty when the registry policy does not require them. This projection omits contract-construction and renderer implementation details. A read-only registry projection may display existing `skill` mappings and canonical paths for audit/discovery; that is not permission to hard-code a new L2-to-L3 map or copy widget-skill names into a handoff. Registry-declared return policies, capabilities, and renderer availability remain authoritative even when omitted from this illustrative projection.

Runtime input is the selected `core_handoff`, including `selected_planner` and `state_snapshot`, plus that routing projection and actual availability context. Consume `user_text`, relevant `prior_returns`, and only domain fields declared in planner `required_state`/`optional_state`; consume an existing `artifact` when the task requires it. Artifact identity is a stable session reference such as `fileId`, not a local path, filename, or display URL. Assess material needs even when their storage fields are optional; field presence and artifact labels do not establish semantic closure.

## Required Sections

- `Workflow End Authority`

  State that only L1 Router owns the canonical workflow state and decides Completion. Explicitly prohibit L2 Planner from presenting local completion as final. Require eligible gaps to enter L3 Designer, instruction-ready work to use the selected executor directly, and every result or failure to return to the actual plugin L1.

- `Layer & Role`

  State that this is L2 Planner for the configured `task_family`. Explain that it diagnoses the interaction paradigm, identifies exactly one open per-edge gap, filters and ranks the supplied widget registry candidates, selects one eligible entry, and emits a `planner_handoff` whose first gap contains `selected_widget_id`. Explicitly delimit ownership: L2 selects the registry entry and directly invokes selected executors for instruction-ready work, but does not author semantic widget contracts or render UI. Derive task wording from `title`, `description`, and `task_family`; do not add capabilities absent from the input. Whether the pack creates a new artifact or refines an existing one is inferred from its chains and state snapshot.

- `IAI Domain Binding`

  Show a two-column table with all six canonical nodes (`H`, `T`, `I`, `Aug`, `A`, `G`) and their task-specific meanings from `node_bindings`. Every node must appear exactly once. Preserve the supplied meanings rather than replacing them with generic definitions; a generic label is acceptable only when that binding is empty.

- `Interaction Chains`

  Show one summary row per item in `chains`, including its ID, task-level function, and ordered edge sequence. Each chain is a task-level **interaction paradigm**: preserve identity, edge order and repeated edges across chains. Associate registered gap names with their chains in the function cell or one short mapping sentence. Explain domain-specific edge meanings concisely; an explanation may be shared by chains when its meaning is identical, but distinguish repeated G/A roles when they differ. Do not require a paragraph repeating the whole sequence for every chain, or collapse chains into an unordered edge list.

- `Diagnosis`

  Use the compact four-column format specified in `L2 Diagnosis Authoring Method` below: `gap_type | Condition | Edge | Interaction goal`. Write one short state-reading paragraph, one diagnosis table, and at most a short routing/exception note. Include every registered gap and one final `instruction_ready` row. The table locates the gap and explains when it exists; do not add a second node-location table, a parallel gap schema or lengthy contrast examples. Preserve concrete source/target evidence in the runtime handoff rather than repeating it throughout the skill.

- `Widget Registry Routing`

  Define a deterministic two-stage route. First, filter candidates by all hard constraints: the active planner is compatible; the diagnosed gap category, interaction goal, and atomic IAI edge are declared; the candidate covers every required return key or explicitly uses agent-interpreted return semantics; the current artifact type is supported; and required runtime capabilities and libraries are available. Second, rank eligible entries by exact semantic coverage, artifact specificity, return coverage, and runtime fitness, with stable registry order and then registry `id` as deterministic tie-breakers. Select exactly one eligible entry and preserve its exact `id`. If none is eligible, return a structured routing failure directly to L1 Router rather than inventing an ID or weakening a hard constraint.

- `Gap Handoff`

  Explain how one open gap becomes a selected-widget request to Layer 3, and include one valid JSON example. The example must contain `gap_type`, `interaction_goal`, `iai_binding` with source node(s), mapped edge, target node, and reason, `expected_return`, and `selected_widget_id` copied exactly from one eligible candidate. When the gap collects inputs for a specific executor, it may also carry optional `target_tool`; gaps with no executor omit it. The handoff carries only the registry ID for widget routing and does not duplicate registry-derived contract, renderer, type, modality, skill-name, or path details.

  For `X→Y`, `source_nodes` must include X and `target_node` must equal Y. `iai_binding.reason` must name the located edge and explain source evidence → missing transfer → missing target state → how the expected return closes it, including why guessing is not justified. A pending interaction source is not a claim that input was already submitted. Keep the existing fields: do not introduce a parallel location schema. Layer 3 must preserve `chain_id` and `reason` alongside the binding in its `iai` object without re-diagnosis.

  Keep the reason to one or two task-specific sentences. Normally provide one widget handoff and one execution handoff per skill; explain other registered goal/return variants briefly in prose rather than duplicating full envelopes. The table's readable goal and the handoff's exact registry goal must agree.

- `Inputs (from core_handoff and widget registry)`

  List the fields Layer 2 consumes from Layer 1. Always include `selected_planner` with the generated planner id and a `state_snapshot`. The planner requires `user_text` and may consume `prior_returns`; when the task operates on an existing artifact, it also consumes that `artifact`. Separately list the routing projection supplied from `registry/widgets.json` and the runtime availability context used to filter it. Do not claim task inputs absent from the task-pack specification.

- `Procedure`

  Give an ordered operational sequence: inspect the core handoff; diagnose the active chain and exactly one gap; filter and rank registry candidates; select one eligible `selected_widget_id`; emit one selected-widget gap request to L3 Designer; or, when instruction-ready, plan and directly invoke the selected declared executor. Every collected result returns through L1 Router. Do not include semantic-contract construction or rendering steps.

- `Output (planner_handoff)`

  Include one valid JSON object in exactly one mode. The widget mode contains `handoff_type`, `planner_id`, `planner_decision: "gap_open"`, exactly one item in `gap_requests`, and the actual plugin L1 skill in `return_to`. That gap preserves `gap_type`, `interaction_goal`, `iai_binding`, `expected_return`, `selected_widget_id`, order, dependency, optional `display_context`, optional `target_tool`, and optional `chain_id`. The execution mode preserves the plugin's existing `execution_instruction` business format with its explicit `executor`. L3 Designer receives the selected gap unchanged; L2 Planner directly invokes the selected executor with the complete execution plan. Do not emit empty legacy placeholders or duplicate registry-derived widget metadata.

- `Must`

  State positive invariants that every execution must satisfy. Require grounding in user intent and collected constraints, selection of exactly one entry that passes every hard routing constraint, exact preservation of its registry ID, deterministic ranking, and direct invocation of only the selected ready executor with unchanged parameters and purpose. Then include each string from `guardrails` as a separate rule. Do not invent policy or domain requirements beyond supplied guardrails.

- `Must Not`

  State layer-boundary prohibitions for the generated planner: do not author widget-contract fields, render UI, invoke an undeclared or unready executor, bypass L3 Designer for an open gap, invent a registry ID, or relax a hard eligibility constraint. The generated Layer 2 handoff must not directly write `widget_type`, `interaction_modality`, or an `l3-*` widget-skill name; it routes only by `selected_widget_id`. These prohibitions do not ban an existing skill mapping in a read-only registry projection. This authoring contract names the forbidden tokens to define the rule and is not itself a generated planner.

- `Tools`

  Identify which layer may use which tools. Always explain that L4 Renderer owns `render_html_widget`, and that L2 Planner directly invokes the task tool selected in `execution_instruction.executor`. If `tools` is non-empty, list exactly those task tools as executors L2 may select and invoke once its instruction is ready. If `tools` is empty, emit `executor.kind: "main_model"` and use the active main model directly. Do not introduce or invoke undeclared tools.

- `Stop / Continue / Escape`

  Define three observable control conditions. Continue when a widget or execution result supplies state needed for another L1 Router pass; return current state directly to L1 when L2 has no further local action; escape through L1 when an indispensable input is refused or cannot be safely inferred. Never define L2 Stop as Completion. Tailor the wording to the task without changing ownership of the decision.

- `Next`

  Emit exactly one `## Next` and one `## Layer & Role` in a generated planner; do not add a separate Layer Routing heading. The role states that L2 Planner plans the current pass for user interaction, main-model work, or one or more registered tools, directly invokes the selected executor for instruction-ready work, and never renders. Next distinguishes Interaction Pathway and Execution Pathway: an eligible open gap carries `selected_widget_id` to L3 Designer for validation and interaction design before L4 Renderer; instruction-ready work calls the selected executor directly with the complete plan. Results and failures return to the plugin's L1 Router, not directly to this planner. L2 never produces the final workflow response or decides Completion.

## L2 Diagnosis Authoring Method

This guide contains the full authoring reasoning rules; the generated skill contains their concise, task-specific application. A short table must retain semantic diagnosis, not become a stage checklist.

### 1. Read state and select the paradigm

Position the current task on both IAI axes: before/after a GenAI invocation, and prompt-only/artifact-grounded resources. Use intent, current artifacts, prior returns and delegated choices to select a declared chain. Trace which information is already available and which transformation is needed next. Do not choose a widget first and invent a gap to justify it.

### 2. Derive a material per-edge gap

Prioritize gap detection and resolution. Assess every registered gap category against current evidence. For each category identify whether it is applicable, which source-to-target transfer is missing, and whether actual evidence closes it. Resolve applicable open gaps through interaction before final artifact execution. After each return, re-enter Layer 1 and reassess remaining gaps. A short prompt warrants active inspection of missing settings, content and representations, not immediate invention of a finished artifact.

Silence is not delegation. Separate supplied facts, explicit scoped user delegation, ordinary low-impact elaboration, and unresolved substantive choices. A user need not explicitly reserve a choice for it to require interaction. If plausible alternatives change the audience, use, core subject or intended outcome and the context does not settle them, diagnose the material target deficit rather than assume unrestricted creative freedom. The ability to generate a plausible artifact is not evidence that its controlling intent is ready. Record each category as open, resolved, or not applicable with its evidence; preserve resolved information and reopen it only when relevant evidence changes.

If only model synthesis or incorporation of existing evidence is missing, L2 Planner plans and directly invokes that work through the selected executor. For example, missing user drawing is `I→A`; failure to incorporate an existing drawing is `A→Aug`, not another drawing request. A failed tool or inaccessible artifact is a failure to return through L1 Router, not a fabricated interaction gap.

### 3. Write one readable diagnosis table

Use exactly these columns in generated L2 skills:

| gap_type | Condition | Edge | Interaction goal |
| --- | --- | --- | --- |
| `<registered_gap>` | Current target information is missing because the relevant user decision or representation remains unresolved. | `<X→Y>` | `<registered_goal>` — the user operation that supplies the missing information. |
| `instruction_ready` | All applicable gaps are resolved with evidence; alternatively, bounded prerequisite preparation returns to L1 with user choices still open and without final artifact execution. | `Aug→G` then `G→A` | Describe the executor directly invoked by L2 Planner, bounded scope and actual result. |

- **gap_type:** Copy the registered semantic category exactly. One row represents one distinguishable condition/edge/goal. The same category may have multiple rows for different registered goals; do not merge goals with a pipe or invent a category for prose convenience.
- **Condition:** One task-specific sentence explaining the missing state and its cause. Name the destination node when that clarifies the meaning, but avoid restating all six node definitions. Describe a general semantic condition, not a single hard-coded scenario, a UI action, or a mandatory earlier stage. Combine `problem` and `cause` here instead of separate repetitive columns.
- **Edge:** One registered atomic edge for an interaction gap, matching its chain. Its direction names the source and target nodes. Do not put a whole workflow in this cell. Only the `instruction_ready` decision row may describe an ordered execution sequence, using the task's declared chain rather than copying this example indiscriminately.
- **Interaction goal:** A short user operation, with the exact registered goal in backticks followed by a readable explanation. Do not put widget IDs, renderer names or executor decisions into interaction-gap rows. For `instruction_ready`, describe main-model/tool execution and the requested result, not an interaction.
- **Chain association:** Keep it in the existing chain table or a short mapping sentence; runtime gap requests preserve `chain_id`. Do not add another diagnosis column merely to duplicate the chain table.
- **instruction_ready:** This is a planner decision, never a registered gap category, never a `gap_request`, and never workflow completion. Final execution requires evidence-backed closure across every applicable gap. It may instead authorize bounded preparation needed to expose a choice (such as producing actual candidates); that choice remains open and must be revisited through L1 before final execution.

### 4. Select one action for the current pass

After assessing all categories, select the next applicable open gap using current intent and real dependencies, and route it for interaction. Continue this cycle through L1 until applicable gaps are resolved; one gap per pass limits the handoff size, not diagnosis coverage or total refinement. Use supplied facts, valid prior returns and explicit scoped permission as closure evidence. If an open gap cannot be routed, report the structured capability failure rather than silently treating it as ready. Explain closure across relevant categories in the execution purpose before final work.

### 5. Preserve concise but complete handoffs

After diagnosis, filter/rank widget candidates using the requirements below. Emit exactly one gap with `chain_id`, exact `gap_type` and `interaction_goal`, `iai_binding` (`source_nodes`, `maps_to_edge`, `target_node`, concise evidence-grounded `reason`), supported `expected_return`, exact `selected_widget_id`, order/dependency and relevant display context. For ready work, emit only `execution_instruction` with the allowed executor and actual parameters. An eligible gap enters L3 Designer unchanged; L2 Planner directly invokes the selected executor for ready work. Every result returns to L1 Router.

Use the existing `execution_instruction.purpose` to state concise evidence for readiness and the scope/source of any delegation. Do not invent delegation in a compiled instruction or example; examples must disclose the actual assumed input that supports it. Readiness for bounded preparation does not close an outstanding user choice or authorize the final artifact: identify the limited preparation and return to L1 afterward. No new handoff field or fixed stage is needed.

### 6. Keep presentation separate from workflow policy

Preserve the five planners and six widgets in inflak-main. Actively use the eligible interaction to resolve diagnosed settings, content, direction, structure, comparison, parameter and spatial gaps. Keyword selection preserves content-bearing choices; spatial drawing produces real canvas evidence. Do not add a generic confirmation checkbox or invent unsupported gaps. Keep the diagnosis table compact and avoid duplicated location tables or extended scenario sections.

## Semantic Requirements

- Derive gaps from current IAI state, not a predefined gate sequence: locate both axes, select the governing chain, trace source evidence into the intended target transformation, and identify the material missing decision or representation before assigning a registered category or selecting a widget. Explain the problem, cause/evidence, why justified inference or delegation cannot resolve it, and the consequence of guessing in `iai_binding.reason`.
- For main, evaluate every registered category and prioritize interaction to resolve all applicable open gaps. Instruction-ready final execution requires evidence-backed closure, not creative latitude. Keep assessments and closure evidence in existing `iai_binding.reason` or `execution_instruction.purpose`, never new handoff or runtime state fields. Delegation closes only its stated dimensions. Preserve settled decisions unless relevant dependent evidence changes; a generic approval checkbox is not semantic resolution.
- Bind all six IAI nodes to the task domain; preserve every declared chain, its function, edge order and domain-specific edge meaning. Shared concise explanations are allowed.
- Diagnose the interaction paradigm and exactly one next material open per-edge gap by dependencies. Preserve `chain_id` when declared by the source JSON, including named-paradigm requests and task packs with multiple named paradigms.
- Select exactly one eligible widget entry after filtering and deterministic ranking. Emit only its ID for widget routing, not registry-derived contract, renderer, type, modality, skill-name, or path details. Read-only registry projections may show existing mappings without becoming handoff fields.
- Keep semantic-contract realization in L3 and rendering in L4. L3 preserves `chain_id`, `reason`, `source_nodes`, `maps_to_edge`, and `target_node` in `iai`; its `state_update_target` is the same edge destination. L1 alone merges canonical domain state. Missing/inconsistent location returns `selected_widget_invalid` without rendering, re-diagnosis, extra widget-return fields, or new interaction stages.
- Select only declared, registered, available executors allowed for the planner. The active main model is not a host function; a tool executor must resolve to an actual host or registered MCP callable. Neither a skill name nor an authoring-only alias creates a tool binding.
- Source/tool/capability failures and unsupported indispensable transfers are actual nonterminal failures directly to the exact plugin L1, never fabricated semantic gaps or false readiness. Bounded preparation requires its own source, capability, and consent evidence, leaves unresolved choices open, returns to L1, and must not execute the final artifact.
- Return control to the actual plugin L1 (`l1-router` in main) after every collected result or failure. Never treat the end of L2 planning as workflow completion.

### Widget eligibility and selection failure

All declared constraints must pass before ranking:

1. `compatible_planners` contains `planner_id` when that restriction is present; an explicitly restrictive list is not permission to infer compatibility.
2. `gap_categories` contains the exact `gap_type`, also declared verbatim by the planner registry.
3. `interaction_goals` contains the exact `interaction_goal`, or the skill explicitly supports a compatible semantic parent goal. Never guess synonyms.
4. `iai_edges` contains `iai_binding.maps_to_edge`.
5. Return coverage satisfies every required `expected_return` field under the fixed, planner-declared, or agent-interpreted policy in [CONTRACT.md](CONTRACT.md). Agent interpretation does not waive required planner fields.
6. `supported_artifact_types` accepts artifacts in `display_context`.
7. Required runtime capabilities, approved libraries, and renderer are actually available.

Rank remaining candidates by semantic coverage, artifact specificity, return coverage, runtime fitness, stable registry order, and finally registry `id`. Unsupported extra controls are not better semantic coverage.

If no candidate satisfies required return fields or runtime capabilities, L2 must not select a near match or claim readiness. Return a structured nonterminal routing failure directly to L1 with `reason: no_eligible_widget`, `planner_id`, `diagnosed_gap` (chain, evidence, edge, goal and required returns), `rejected_candidates` (IDs and failed constraints), and `return_to`. No widget is rendered for a routing failure. A fallback is eligible only if it is registered and passes all the same constraints. This is distinct from L3's `selected_widget_invalid` validation failure.

## Output Requirements

Produce exactly one complete Markdown skill document with YAML frontmatter:

- `name` must be `l2-{pack_slug}` and agree with the actual directory and registry identity.
- `description` must state the routing condition for this planner.
- The `planner_handoff` example must be valid JSON.
- Every configured gap must appear in the single four-column `Diagnosis` table, followed by exactly one `instruction_ready` decision row; each runtime widget-mode example emits exactly one gap request.
- Every example `selected_widget_id` must name an eligible entry from `widget_registry_candidates`.
- Do not emit commentary outside the skill document.

Examples are optional beyond the required widget and execution handoff examples for a generated L2 skill. The templates below are authoring illustrations, not live evidence or ready-to-submit payloads; replace placeholders with actual registered values and grounded inputs. This detailed contract itself is pure Markdown without frontmatter, not a generated skill.

### Canonical planner fields

| Field | Requirement |
| --- | --- |
| `handoff_type` | Always `planner_handoff` for widget and execution plans. |
| `planner_id` | Exact selected planner registry ID. |
| `planner_decision` | `gap_open` or `instruction_ready`; not workflow completion. |
| `gap_requests` | Interaction Pathway only, exactly one request for the current pass. |
| `execution_instruction` | Execution Pathway only; complete business plan with explicit `executor`, actual `parameters`, and task-level `purpose`, directly invoked by L2 Planner. |
| `return_to` | Actual plugin L1 skill name, not a generic placeholder. |

| Gap field | Requirement |
| --- | --- |
| `gap_type` | Exact registered semantic missing state. |
| `interaction_goal` | Registered user operation needed to close the gap, not a widget name. |
| `iai_binding` | Required `source_nodes`, `maps_to_edge`, `target_node`, and evidence-grounded `reason`; source includes X and target equals Y for `X→Y`. |
| `expected_return` | Semantic description or typed expectation supported by the selected entry; ready schema handoffs specify producible exact keys/types. |
| `selected_widget_id` | Exact eligible registry ID. |
| `order`, `depends_on_previous` | Required order and dependency indicators. |
| `display_context` | Include prepared candidates, fragments, profiles, actual artifacts, warnings, or grounded defaults that L3 must display; omit when not needed. It is not renderer-owned `display`. |
| `target_tool` | Only when collecting parameters for a particular registered executor; informs tool-aware realization, never selects L3. |
| `chain_id` | Preserve declared named paradigms; required when the task pack declares multiple named paradigms. Main preserves its named chain. |

### Interaction Pathway example

```json
{
  "handoff_type": "planner_handoff",
  "planner_id": "<planner-id>",
  "planner_decision": "gap_open",
  "gap_requests": [
    {
      "chain_id": "<declared-chain-id>",
      "gap_type": "<exact-registry-gap>",
      "interaction_goal": "<registered-user-operation>",
      "iai_binding": {
        "source_nodes": ["I"],
        "maps_to_edge": "I→Aug",
        "target_node": "Aug",
        "reason": "<I→Aug: available or pending source evidence, missing target choice, why guessing is unjustified, and how the return closes it>"
      },
      "expected_return": {"<declared-key>": "<declared-type>"},
      "selected_widget_id": "<eligible-widget-registry-id>",
      "display_context": {"<relevant-context-key>": "<actual-evidence>"},
      "order": 1,
      "depends_on_previous": false
    }
  ],
  "return_to": "<actual-plugin-l1-name>"
}
```

### Execution Pathway examples

Assumption for each template: actual facts, prior returns, or explicitly scoped user delegation establish the stated readiness, or authorize only the stated bounded preparation. A placeholder purpose does not establish closure. The tool template assumes a real registered callable, valid input parameters, planner permission, source evidence, availability, and required consent.

```json
{
  "handoff_type": "planner_handoff",
  "planner_id": "<planner-id>",
  "planner_decision": "instruction_ready",
  "execution_instruction": {
    "executor": {"kind": "tool", "name": "<registered-and-allowed-callable>"},
    "parameters": {"<required-parameter>": "<actual-value>"},
    "purpose": "<task result and evidence-backed closure, or bounded preparation scope>"
  },
  "return_to": "<actual-plugin-l1-name>"
}
```

Direct main-agent generation uses the active main model, not a fabricated host/MCP tool:

```json
{
  "handoff_type": "planner_handoff",
  "planner_id": "<planner-id>",
  "planner_decision": "instruction_ready",
  "execution_instruction": {
    "executor": {"kind": "main_model"},
    "parameters": {"compiled_instruction": "<instruction grounded in actual supplied or explicitly delegated choices>"},
    "purpose": "<task result and evidence-backed closure, or bounded preparation scope>"
  },
  "return_to": "<actual-plugin-l1-name>"
}
```

Preserve existing plugin-specific execution business fields and any planned multi-tool work without creating a new runtime schema; new authoring names an explicit executor. L2 Planner directly invokes the selected executor with the complete parameters and purpose. `main_model` uses the active main model; a tool must resolve to its registered host or MCP binding. Return actual results and failures immediately to L1 Router. Do not substitute executors, invent results, or present a local result as workflow completion. Legacy `execution_instruction.tools` is readable only outside the ready bundle.

### Invalid content

- Both `gap_requests` and `execution_instruction` in one handoff, or `instruction_ready` as a gap.
- Alternative strings such as `a|b|c` in a concrete gap or goal; each request names one exact semantic value.
- Duplicated widget metadata (`target_widget`, `widget_type`, `interaction_modality`, widget-skill names or canonical paths) in the handoff, or a hard-coded replacement for registry selection. Existing registry projections may display existing mappings.
- L3-owned `display`, `controls`, `presentation`, renderer details, HTML, CSS, JavaScript, event handlers, or renderer instructions.
- Undeclared or unready task-tool invocation, widget substitution, false readiness, or bypassing L3 Designer for an interaction gap.
- Empty boilerplate such as `tool_plan: []`, `expected_return_types: []`, or empty `continue_condition`, `stop_condition`, and `escape_condition`.

## Validation

A generated skill conforms only when its semantic blocks are present, the four-column diagnosis table covers the registered gaps and distinguishes instruction-ready execution, each interaction row has a valid chain-bound atomic edge and registered goal, and every widget example selects an eligible candidate with complete supported returns. Reject contradictory node/edge bindings, unregistered IDs, invented task requirements and duplicated handoff metadata. Check meaning and parsed rows/handoffs rather than exact long prose or scenario wording. Existing heading aliases remain readable for legacy packs; new main L2s use `Diagnosis`. The generated skill need not repeat this authoring method verbatim.

Verify main's all-category closure policy without imposing it on unrelated plugins; check execution permission and real host/MCP bindings separately from main-model availability. Validate failure envelopes and exact L1 return targets as well as successful examples. Apply cross-file publication and acceptance checks from [CONTRACT.md](CONTRACT.md); this is a static authoring check, not an additional runtime load.
