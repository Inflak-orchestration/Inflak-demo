# Inflak L1-L4 Contract

Status: canonical cross-layer authoring and validation contract for ready, newly generated, and regenerated Inflak task packs.

## Scope and References

This contract defines shared pathways, ownership, interfaces, registry/return policies, publication, and acceptance. Domain invariants may strengthen validation but must not transfer layer responsibilities or conflict with handoff fields. Main-specific rules below apply only to `inflak-main`; other plugins retain their task-specific behavior and runtime APIs.

Detailed authoring rules live in [L2 Planner Skill Contract](l2-skill-contract.md) and [L3 Designer Skill Contract](l3-skill-contract.md). Both retain their `Required Sections` lists and generation methods. They are Authoring-only documentation, have no frontmatter, and each is not a callable skill and not a runtime prerequisite. Examples are optional where the detailed contract permits; complete runtime payloads are not optional. Operational L3 skills define their handoff locally, and L4 validates through its own inline `Inputs`, without an extra contract read.

## Skill Document Structure

Every operational `SKILL.md` begins with exactly one YAML frontmatter block containing one `name` and a selection-oriented `description` (for example, `description: "Use when: ..."`), and has exactly one primary H1. Its `name` equals its skill directory and every registry `skill` reference. One file contains one coherent contract, never concatenated legacy and regenerated documents.

A new or regenerated independent plugin has a canonical root `SKILL.md` and a byte-identical SDK-discoverable alias at `skills/<manifest-plugin-id>/SKILL.md`; a missing or divergent alias blocks ready publication. Older plugins may use their sole registered L1 as a compatibility entry.

**Main exception:** manifest id `inflak-main` enters directly through its sole L1 `l1-router`. Do not create or retain `skills/inflak/` or `skills/inflak-main/`. Its root `SKILL.md` (`name: inflak`) is documentation read by L1, not a second callable entry. Registry-backed layer skills still require exact directory/frontmatter/registry identity. Do not change other plugins' entry policies.

Required sections are semantic blocks rather than mandatory literal headings. Established aliases (`Role` / `Layer & Role`, `Inputs` / `Inputs (from planner_handoff)`, `Contract` / `Output and Handoff`) and combined related blocks are acceptable when ownership, inputs, outputs, validation, lifecycle, and prohibitions stay explicit and independently auditable. A heading alone does not satisfy a block or weaken a machine-checkable invariant.

## Protocol Invariants

One pass follows exactly one of four pathways:

```text
Interaction Pathway: user/return -> L1 -> L2 gap_request + widget selection -> L3 interaction design -> L4 render -> L1
Execution Pathway:   user/return -> L1 -> L2 plan -> execute/realize -> L1
Host Agent Return:   user request -> L1 -> host agent
Completion:          user/return -> L1 -> Completion
```

1. Every widget render is preceded by `L1 -> L2 -> L3` in the current pass.
2. L2 plans interaction, main-model work, inspection, preparation, or one or more registered tools. In the Execution Pathway it directly calls the selected executor with the complete plan; it never renders or independently produces a final workflow response.
3. In the Interaction Pathway, L3 receives the exact L2-selected gap request. L3 preserves the diagnosis, widget, goal, state-update meaning, and return fields while designing the interaction; it does not replan or substitute.
4. Every executor result/failure, L2 routing failure, L3 validation failure, and L4 widget return/renderer failure immediately re-enters the exact plugin L1.
5. L2 selects one eligible widget by `selected_widget_id`; metadata remains registry-derived. L3 designs semantics within that primitive; L4 implements them without changing task meaning or return keys.
6. Registry metadata enables discovery and matching; the selected skill is the behavioral contract. Both must agree.

Host Agent Return hands a request outside the interaction/execution scope back to the host agent for a direct response. Completion is the L1 decision that the current workflow is finished. These pathway names do not change existing `bypass` or `end` decision values.

## Workflow End Authority

Only L1 Router owns canonical workflow state, return merging, and Completion authority. On every initial request, executor result, or downstream return/failure, it reconstructs the newest state and chooses one eligible planner, Host Agent Return, or Completion (`decision: end`). L2 Planner, L3 Designer, L4 Renderer, executors, and the host cannot independently decide completion. Their results are nonterminal until L1 decides otherwise.

## Layer Ownership

| Layer | Owns | Must not own |
| --- | --- | --- |
| L1 Router | Entry, state reconstruction/merge, planner routing, Host Agent Return, Completion | Gap diagnosis, widget selection, execution parameters, rendering |
| L2 Planner | Atomic paradigm, next material open gap by dependencies, domain reasoning, widget routing, execution planning and direct executor invocation | Semantic widget contract details, rendering, workflow completion |
| L3 Designer | Exact-selection validation and semantic interaction design | Planner decisions, widget substitution, task execution, HTML/CSS/JS, workflow completion |
| L4 Renderer | Contract validation, concrete sandboxed UI, event wiring, local validation, render call, structured return | Gap diagnosis, widget selection, task tools, changing return semantics, workflow completion |

## Pass State and Loop

L1 reconstructs state each pass from the latest user text, prior widget returns, execution results, and current artifact references. The newest valid return/result is authoritative for the state it updates. A field exists only when it affects routing or downstream planning; its name stays stable across `state_snapshot`, planner `required_state`/`optional_state`, L2 inputs, and return-merge logic.

Artifact identity uses stable session identifiers such as `fileId`, never a local path, filename, or display URL. L1 applies the selected interaction's `outcome_semantics` to returned `values`, including state, merge, workflow, and termination rules. L3's state-update destination remains the diagnosed edge destination; only L1 merges canonical domain state.

The loop ends only when L1 re-enters and finds no remaining action for the current intent. Accepting constraints normally updates state, not completion; a new or edited artifact can expose an acceptance gap on the next pass. Submit, dismiss, refusal, and capability failures do not independently authorize completion or fabricate approval.

## L1 Router Contract

L1 Router reconstructs state, chooses exactly one planner route, Host Agent Return, or Completion outcome, and emits the corresponding self-contained handoff. It does not diagnose a domain gap. Canonical route example:

```json
{
  "handoff_type": "core_handoff",
  "decision": "route_to_planner",
  "selected_planner": "<planner-id>",
  "state_snapshot": {"user_text": "", "prior_returns": []}
}
```

- `handoff_type`: `core_handoff` for the canonical handoff.
- `decision`: `route_to_planner`, `bypass`, or `end`. Existing plugin-specific bypass, direct-answer/Host, and end forms stay compatible; no new fields are required for them.
- `selected_planner`: required only for `route_to_planner`, equal to a planner registry `id`.
- `state_snapshot`: required; for routing, keys must be in the selected planner's required/optional state except universal `user_text` and `prior_returns`.
- Optional `matched_triggers` and `confidence` are observability only, not planner logic or routing correctness. Do not require them in generated skills.
- Do not add `required_tool_capabilities`; tool permission belongs to planner/tool registries.

Required L1 semantic blocks: role/ownership; state schema and re-entry; routing table sourced from `registry/planners.json`; canonical `core_handoff`; bypass/end behavior; Must / Must Not / Next. Domain-wide IAI node definitions belong in root or L2; L1 contains only the edge/state information needed to route.

## L2 Planner Contract

L2 Planner consumes `core_handoff.selected_planner` and `state_snapshot`, the widget registry routing projection, and actual runtime availability. It owns domain reasoning, atomic paradigm/gap diagnosis, dependency-based next-gap selection, widget routing, execution planning, and direct invocation of the selected executor, not semantic UI design. Main's five planners assess every registered category each pass and resolve applicable material gaps before final execution; detailed evidence, delegation, preparation, and failure rules are in [l2-skill-contract.md](l2-skill-contract.md).

Output is `planner_handoff` with `planner_id`, `planner_decision`, exact plugin L1 `return_to`, and exactly one mode: `gap_open` supplies one `gap_requests` item (`gap_type`, `interaction_goal`, `iai_binding` source/edge/target/reason, `expected_return`, `selected_widget_id`, `order`, `depends_on_previous`, and applicable `chain_id`, `display_context`, `target_tool`); `instruction_ready` supplies `execution_instruction` with explicit `executor` (`main_model` or registered/allowed `tool`), `parameters`, `purpose`, and preserved plugin-specific business fields. An eligible gap enters L3 Designer unchanged. An instruction-ready plan is executed directly by L2 Planner through its selected executor, with actual results/failures returned to L1; neither readiness nor bounded preparation is workflow completion.

No candidate match yields a nonterminal failure directly to L1: `reason: no_eligible_widget`, `planner_id`, `diagnosed_gap`, `rejected_candidates`, `return_to`, without rendering or false readiness. Handoffs never copy registry-derived widget type, modality, skill names, paths, or renderer details; a read-only registry projection may display existing skill mappings. Complete fields, matching constraints, diagnosis method, failure details, examples, and generated-document requirements belong solely in [l2-skill-contract.md](l2-skill-contract.md).

## L3 Designer Contract

L3 Designer consumes the exact L2-selected widget request, selected registry entry, grounded task/artifact evidence, runtime context, and L1 return target. In the Interaction Pathway it validates selection and preserves diagnosis, then owns purpose, information hierarchy, operations, constraints, feedback, and return production within the reusable primitive. It never reroutes, substitutes a widget, invokes task executors, invents evidence, or emits rendering code.

Successful widget output to the actual L4 includes identity (`selected_widget_id`, `widget_id`, `widget_type`, `surface`, `planner_id`, `purpose`, `interaction_goal`), preserved `iai` diagnosis and merge destination, grounded `display`, `controls`, `presentation.profile`, exact `expected_return` and mappings, `widget_requirements`, `safety`, and applicable `runtime`/`reference_assets`. There is no new success `handoff_type`. Each operational L3 defines this complete compact handoff locally, and L4 validates locally, without an extra reference read.

Invalid selection or missing indispensable evidence/capability immediately returns `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, and exact L1 `return_to`, without substitution, re-diagnosis, rendering, or L4. Complete validation, profile method, eight local handoff bullets, and failure rules are in [l3-skill-contract.md](l3-skill-contract.md).

## L4 Renderer Contract

L4 validates the semantic L3 contract using its inline `Inputs`, generates sandboxed HTML/CSS/JS, invokes exactly one render tool per widget contract, and returns structured values to the actual plugin L1. No extra contract read or new renderer-tool argument is required.

Canonical render request:

```json
{
  "widget_type": "<copied-from-L3>",
  "selected_widget_id": "<copied-from-L3>",
  "render_mode": "generated",
  "title": "<display.title-or-interaction-goal>",
  "html": "<sandboxed-markup>",
  "css": "<scoped-layout-styles>",
  "js": "<event-wiring>",
  "height": 520,
  "display": {},
  "controls": [],
  "planner_id": "<copied-from-L3>",
  "interaction_goal": "<copied-from-L3>",
  "expected_return": {}
}
```

Canonical widget return:

```json
{
  "widget_id": "<widget-id>",
  "planner_id": "<planner-id>",
  "action": "accept",
  "values": {},
  "freeform_note": "",
  "timestamp": "<ISO-8601>"
}
```

- Preserve `widget_type` and task semantics. Pass `selected_widget_id`, `display`, `controls`, `planner_id`, `interaction_goal`, and `expected_return` unchanged. The selected ID is registry trace/observability metadata only, not new UI semantics.
- Initialize state from `window.widgetDisplay` before rendering or binding handlers. Guard DOM/data lookups; every visible control updates state, feedback, or return data, never a decorative no-op.
- Submit through `window.submitWidget(values)` or dismiss through `window.dismissWidget(note)`. Provide a visible dismiss action; validate return invariants before submission and show inline errors.
- `values` matches L3 `expected_return` exactly. Only host envelope normalization is permitted; never rename, infer, discard, or translate planner values. Forward the structured result to L1 for `outcome_semantics` interpretation.
- The host must not infer plugin workflow state, next stages, or completion from widget metadata, planner IDs, interaction goals, or action labels.
- Use shared `--iai-*` design tokens and `.iai-*` component classes, deterministic local state, and sandbox-safe rendering. Only approved, version-pinned external libraries declared by L3 and permitted by CSP may be used.
- Never call task tools or access parent DOM, storage, cookies, tokens, local files, or undeclared networks. Browser modal APIs are prohibited in sandboxed widgets.
- After submit, dismiss, or renderer failure, immediately load the actual plugin L1 with the structured result. Never decide completion or produce a final workflow response. A task result cannot directly trigger L4 acceptance: start a fresh L1/L2/L3 pass.

Required L4 semantic blocks: role and accepted types/registry policy; local input validation; rendering procedure; unchanged request mapping; stable return shapes and interaction-specific invariants; runtime reliability/design system; Must / Must Not / Stop-Continue-Escape / Next. Task-pack renderers reference shared [main L4 rules](../skills/l4-widget-renderer/SKILL.md) and add only accepted types and domain-specific validation/rendering invariants, not repeated generic security/CSS text.

## Registry Contract

Planner registry minimum (arrays are shape placeholders, not authorization):

```json
{
  "id": "<planner-id>",
  "skill": "<l2-skill-name>",
  "canonical_skill_path": "<path>",
  "required_state": ["user_text"],
  "optional_state": ["prior_returns"],
  "iai_edges": [],
  "gap_categories": [],
  "allowed_tools": [],
  "loop_return_to": "<actual-plugin-l1-name>"
}
```

Widget registry minimum:

```json
{
  "id": "<widget-id>",
  "skill": "<l3-skill-name>",
  "canonical_skill_path": "<path>",
  "widget_type": "<interaction-primitive>",
  "surface": "conversation_widget",
  "interaction_modality": "<user-operation>",
  "supported_artifact_types": [],
  "interaction_goals": [],
  "iai_edges": [],
  "gap_categories": [],
  "state_update_targets": [],
  "return_mode": "schema",
  "return_field_policy": "fixed",
  "expected_return_types": [],
  "widget_capabilities": [],
  "primary_renderer": "render_html_widget",
  "compatible_planners": []
}
```

Registry IDs are unique within each registry. Referenced skill paths and renderers must exist; every ready L3 is referenced by a standard or declared extension registry and is renderer-reachable. Remove or archive unreferenced L3s outside the ready plugin, or register them only after proving an independent gap, return contract, and renderer support.

A tool entry declares stable id, callable name, input schema/required parameters, result artifact type, compatible planners, and registration layer. L2 selects and directly invokes only registered tools allowed by its planner; L3 owns interaction design and cannot invoke task tools. Each callable must resolve to its actual executable host handler or registered MCP binding before a runtime-ready preview is approved. A skill registry entry is not a backend function. `main_model` means direct work by the active main model, with availability checked explicitly, not a fabricated host/MCP callable. Host and MCP tools keep their real registration/invocation boundaries; a `session` registration does not change L2's invocation responsibility.

## Return Field Policies

- **Schema / fixed (defaults):** `return_mode: "schema"` requires nonempty `expected_return_types`. Default `return_field_policy: "fixed"` requires every L2 top-level `expected_return` key in that registry list and in the L3 contract.
- **Planner declared:** reusable schema widgets may use `return_field_policy: "planner_declared"` only when their L3 skill explicitly defines dynamic controls/validation that preserve exact planner-provided top-level keys and shapes. Registry `expected_return_types` remains a nonempty stable baseline, not an exhaustive list of domain fields.
- **Agent interpreted:** `return_mode: "agent_interpreted"` may omit `expected_return_types`; L3 still names all fields required by each supported planner handoff, and all results re-enter L1 before further planning or execution.
- Artifact mutation remains a separate executor boundary with its own validated input schema. No return policy permits undeclared fields, invented provenance, or changing the planner's meaning.

## Authoring and Publication

Author from one source specification in this order: task family/state/six IAI node bindings/named atomic paradigms; semantic gap categories without widget types; ready conditions and registered executor policy; reusable L3 capabilities/match metadata; deterministic returns/merge strategies or explicit agent interpretation; L4 domain invariants using shared rules; consistent skills and registries; then the required entry alias (or main's sole-L1 exception).

Use the two detailed contracts for document generation/review only. Necessary content is explicit ownership, handoff examples where required, state/gap/matching/return/merge semantics, invalidating domain constraints, observable loops, and registry consistency. Diagnostics, design-time reference assets, capability declarations, and additional nonconflicting examples are optional. Exclude repeated generic IAI definitions, duplicate renderer rules, empty consumerless placeholders, hard-coded L2-to-L3 mappings, L1-L3 implementation code, and prose with no effect on routing, validation, state, or output.

Define and approve at least one realistic executable acceptance case in the task blueprint and store it in `tests/scenarios.json`. Publish atomically, re-read the installed bundle, verify its hash and manifest/root identity, refresh the runtime plugin directories, smoke-load the declared entry in an isolated SDK session, then run the required real-session case before retaining `ready`.

Each case has stable id/title, realistic initial input, optional attachments, mode (`probe`, `scripted`, or `interactive`), optional scripted returns, and assertions. Assertions cover the intended first goal/widget type, expected ordered skills or L1-L4 path, required/forbidden tools and side effects, final artifact types, and observable final content as applicable.

- `probe` proves root-to-widget execution and dismisses safely; dismissal is not approval.
- `scripted` uses only blueprint-approved structured returns through completion; a missing or mismatched return fails rather than guessing.
- `interactive` opens a normal browser-visible session and persists evidence as the user acts.

Every run writes `scenario-input.json`, `skill-trace.json`, `widget-contracts.json`, `widget-returns.json`, `tool-results.json`, `final-artifacts.json`, `assertions.json`, and `SCENARIO-REPORT.md`. A required background case executes through the real SDK/WebCopilotSession path, not a static substitute.

A failed required case prevents/revokes `ready`, leaves the installed plugin `planned` for inspection, and returns failed case, phase, run, report, and session to Author. Regenerating that exact plugin requires a new immutable preview, `replace_existing_plugin: true`, the source scenario run id, and new hash-bound approval. Restore the old planned directory if replacement is not atomic; prior approval cannot authorize a changed bundle.

## Validation and Acceptance

- Validate one frontmatter/name/H1 per operational skill and matching directory/frontmatter/registry identities. Validate entry policy: main's direct `l1-router` with no aliases; new independent plugins' byte-identical aliases; sole-L1 compatibility only for older plugins.
- Every L1 planner selection exists; each routed state key is declared except universal fields. Every concrete L2 gap is verbatim in its planner and an eligible widget registry entry. Goals/edges must match declared eligibility, not guessed synonyms; each concrete request names one gap/goal, never `a|b|c` alternatives.
- Widget and execution handoffs are mutually exclusive. Every selected widget is eligible; handoffs contain no duplicate widget type/modality/skill/path metadata. Existing registry projections may display mapped skills. Every executor is registered/allowed and each tool binding is executable; main-model availability is checked separately.
- Every ready L3 is registry-referenced and names a valid renderer, preserves selection/diagnosis and allowed state-update destination in the L1 state schema, provides the complete local contract and failure envelope, covers exact L2 returns under the declared policy, and contains no render code.
- Every L4 accepted type exists in registry; request/return fields are preserved and every widget return or renderer failure re-enters the actual L1. No layer assumes another layer's responsibilities.
- Re-read and hash-check the installed bundle and manifest/root identity; confirm the refreshed runtime includes its plugin directory and isolated entry loading succeeds. At least one blueprint-approved realistic case must exist and its required real-session run must pass without layer-order, widget-contract, tool-policy, or declared final-result failures.

Ready-set acceptance requires all counters below to be zero:

```text
format issues:              0
unreferenced L3 skills:      0
L2/registry gap drift:       0
unmatched L2 handoffs:       0
invalid executors:          0
invalid renderer refs:      0
invalid runtime bindings:   0
runtime entry failures:     0
required scenario failures: 0
layer-boundary violations:  0
```

## Main Runtime Scope

Main is a five-planner image/writing bundle: `writing-draft`, `writing-revision`, `prompt-enhancement`, `image-generation`, `image-edit`. Its six concrete widget entries and matching skills are `settings-form`, `option-selector`, `content-editor`, `structure-editor`, `canvas-editor`, and `parameter-controls`. It enters only through `l1-router`; L2 Planner directly calls the executor for instruction-ready work. All widget surfaces are `conversation_widget`; drawing/mask editing stays in the dialogue iframe, not a separate document workspace.

Main inpainting uses transparent-edit/opaque-preserve masks. Respect declared operation and preservation constraints; report capability failures truthfully and never invent runtime outputs. Main's proactive category assessment and closure requirements do not change other plugins' task behavior or runtime APIs.

Outside the ready runtime set, planned/non-ready packs may temporarily retain `execution_instruction.tools: ["name"]`, generic `return_to: "l1-router"`, optional empty `tool_plan`/`expected_return_types`/condition fields, or L3 contracts without `surface`, `presentation.profile`, `merge_strategy`, or `next_planner_action`. Readers may accept these only during migration; ready plugins, new authoring, and regeneration emit canonical forms. Preserve existing behavior and tests while tightening one boundary at a time, not by restoring obsolete contradictions or adding runtime document loads.
