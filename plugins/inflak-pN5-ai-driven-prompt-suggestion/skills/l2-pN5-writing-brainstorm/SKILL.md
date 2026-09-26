---
name: l2-pN5-writing-brainstorm
description: "Use when: P5 Layer 1 routed a writing idea for GenAI-assisted divergence, writer selection, focused prompt assembly, and final text generation."
---

# Layer 2 - Writing Brainstorm Planner

## Layer & Role

L2 Planner assesses every registered gap and selects one next interaction by real dependencies, or directly invokes the active main_model for a ready bounded preparation or final-writing instruction. Do not render or design widget semantics. L3 Designer never executes; Execution Pathway bypasses L3/L4. Every preparation, artifact, partial result or failure returns to `l1-pN5-core-module`; only L1 Router owns canonical merging and `decision: end`.

Interaction Pathway sends one gap through L3 Designer → L4 Renderer → L1. Execution Pathway directly realizes the ready plan through L2's active main_model → L1. Host Agent Return and Completion belong to L1 and do not enter L2; routing failure returns directly to L1 without L3. Locate each pass on before/after GenAI invocation and prompt-only/artifact-grounded axes before diagnosing its missing per-edge transformation.

Registry state_update_targets are business storage paths (`selected_directions`, `writing_constraints`, `confirmed_prompt`), not literal IAI nodes. Preserve them in L1 merge strategy; semantic state_update_target is the selected edge destination I for G→I or T for H→T/I→T. Presentation does not imply adoption.

## Widget Routing

For a widget-path gap, query the plugin-local `registry/widgets.json` after diagnosis. Filter entries by `compatible_planners`, `gap_categories`, `interaction_goals`, `iai_edges`, expected-return coverage, and required artifact, runtime, and renderer availability. Select one eligible widget registry entry and write only its `id` to `gap_requests[0].selected_widget_id`; do not copy registry-derived concrete metadata into the handoff. Layer 3 validates and realizes the selected entry; it does not select or replace it. This layer does not author the semantic widget contract or render UI.

Rank eligible entries by semantic coverage, artifact specificity, return coverage, runtime fitness, stable registry order then ID. No match returns nonterminal `reason: no_eligible_widget`, planner_id, diagnosed_gap with evidence/chain/edge/goal/returns, rejected_candidates with failed checks, and exact L1 return_to; do not send an invalid selection to L3.

## Inputs

Read the selected `core_handoff.state_snapshot`. Require `user_text`; optionally read `seed_prompt`, `brainstorm_candidates`, `selected_directions`, `writing_constraints`, `confirmed_prompt`, `prior_returns`, and `generated_artifact`. Treat the newest explicit author selection or confirmation as authoritative.

## IAI Binding

| Node | Domain binding |
| --- | --- |
| H | Writer owning seed and creative choices |
| T | Evolving writer-owned seed and focused prompt |
| I | Actual candidate presentation and explicit adoption/facet returns |
| Aug | Confirmed prompt compiled into writing instructions |
| A | Actual generated writing artifact |
| G | Active main model, with separate divergence and final-writing roles |

| Chain ID | Function | Ordered edges |
| --- | --- | --- |
| p5-seed | Collect actual writing intent | `H→T` |
| p5-divergence | Prepare and expose real alternatives | `T→G, G→I` |
| p5-focus | Writer adopts and develops a direction | `I→T` |
| p5-writing | Realize the confirmed prompt | `T→Aug, Aug→G, G→A` |

P5 first uses the ordered path `T→G→I`: GenAI extends the writer's seed prompt into distinct narrative directions, then the suggestions are exposed to the writer through `G→I`. The writer's selection or adoption updates `T` through `I→T`. Only after the writer confirms a focused prompt does P5 compile `Aug` and use the ordered execution path `T→Aug→G→A` for final writing.

## Candidate Generation

For a usable seed prompt, bounded instruction_ready preparation directly invokes active main_model to produce 4 to 6 clearly differentiated candidates and returns them to L1 before any interaction selection. Every candidate must include:

```json
{
  "id": "direction-...",
  "title": "",
  "logline": "",
  "narrative_lens": "",
  "form_or_structure": "",
  "emotional_tone": "",
  "creative_hook": "",
  "tradeoff": ""
}
```

Vary the underlying narrative strategy, not only wording. Candidate sets may vary point of view, temporal frame, form, scene focus, evidence source, emotional register, or central question. Do not present a candidate as selected until the writer selects it.

## Diagnosis

Assess every registered category as `open`, `resolved` or `not applicable` using current evidence, user returns and explicit scoped delegation. Record category statuses and the missing transfer/consequence in existing `iai_binding.reason` or `execution_instruction.purpose`, not invented mandatory fields. Silence is not delegation and missing input never counts as resolved. Emit one next material gap by dependency, not table order; distinguish preparation readiness from final-writing readiness.

| gap_type | Condition | Edge | Interaction goal |
| --- | --- | --- | --- |
| `creative_seed_gap` | No usable subject, desired artifact, or creative goal exists. | `H→T` | `collect_writing_seed` |
| `divergence_gap` | A usable seed needs current directions surfaced; prepare actual candidates before widget selection. | `G→I` | `compare_narrative_directions` |
| `focus_gap` | Current directions lack author adoption or further-exploration decision. | `I→T` | `select_or_combine_narrative_directions` |
| `development_gap` | A selected direction has a material unresolved writing choice. | `I→T` | `focus_writing_prompt` |
| `prompt_confirmation_gap` | The sufficient focused prompt lacks explicit current confirmation. | `I→T` | `confirm_writing_prompt` |
| `instruction_ready` (decision, not gap) | Inputs for bounded divergence exist, or the current final prompt is explicitly confirmed with applicable gaps closed. | `T→G` preparation; `Aug→G, G→A` final | Directly invoke active main_model for that bounded purpose; return to L1. |

Prioritize a missing decision that materially changes the result: intended artifact, audience, narrative lens, form, scope, tone, or length. Preserve productive ambiguity when the writer chooses it.

## Widget Handoffs

For `divergence_gap` and `focus_gap`, emit a request using actual 4–6 candidates, never the empty example arrays below as live evidence. Divergence uses p5-divergence/G→I/compare_narrative_directions; focus uses p5-focus/I→T/select_or_combine_narrative_directions. Preserve existing ordered_edges when relevant and consistent with the named chain.

```json
{
  "handoff_type": "planner_handoff",
  "planner_id": "writing-brainstorm",
  "planner_decision": "gap_open",
  "gap_requests": [{
    "chain_id": "p5-divergence",
    "gap_type": "divergence_gap",
    "selected_widget_id": "narrative-direction-cards",
    "interaction_goal": "compare_narrative_directions",
    "iai_binding": {
      "source_nodes": ["G"],
      "maps_to_edge": "G→I",
      "target_node": "I",
      "ordered_edges": ["T→G", "G→I"],
      "reason": "Generated narrative directions exist and must be surfaced for writer judgment before any adoption changes the prompt."
    },
    "expected_return": {"primary_direction_id": "", "supporting_direction_ids": [], "rejected_direction_ids": [], "action": "develop|more_ideas|dismiss", "freeform_note": ""},
    "order": 1,
    "depends_on_previous": false,
    "display_context": {"seed_prompt": "", "candidates": [], "selection_summary": ""}
  }],
  "return_to": "l1-pN5-core-module"
}
```

For seed collection, development, and final confirmation, emit a semantic request with only current missing facets, selected direction content, existing constraints, the compiled prompt preview, and the selected registry ID. Layer 3 validates and realizes the selected entry.

Use prompt-constellation with p5-seed/H→T for seed and p5-focus/I→T for development/confirmation. Exact expected_return: selected_facets object, custom_facets object, prompt_edits string, action continue|confirm|back_to_directions|dismiss, freeform_note string. Facets are artifact_type, audience, narrative_lens, form_or_structure, scope_or_setting, tone, length, constraints; expose only material facets and allow intentional leave_open. Direction returns require primary only for develop, at most two distinct supporting IDs, and disjoint rejected IDs; more_ideas requires no selection. All references must identify actual candidates. Any adopted content or prompt edit invalidates previous confirmation; suggestions alone are not adoption.

Every gap includes chain_id, order 1, truthful depends_on_previous, exact goal and typed expected_return. Edge source belongs to source_nodes and target_node equals the selected edge destination; validate registry business paths through the explicit L1 merge mapping, not literal node/path equality. Preserve binding reason through L3.

## Execution Handoff

When the writer explicitly confirms, compile `confirmed_prompt` from their selections and wording. Preserve the chosen direction's central premise and all stated constraints. Then hand the main model an execution instruction:

```json
{
  "handoff_type": "planner_handoff",
  "planner_id": "writing-brainstorm",
  "planner_decision": "instruction_ready",
  "execution_instruction": {
    "executor": {"kind": "main_model"},
    "parameters": {"confirmed_prompt": "", "artifact_type": "", "ordered_edges": ["T→Aug", "Aug→G", "G→A"]},
    "purpose": "Create the requested writing artifact from the writer-confirmed prompt. Honor selected narrative direction, structure, tone, audience, and constraints. Return the artifact, not brainstorming notes or an explanation."
  },
  "return_to": "l1-pN5-core-module"
}
```

L2 directly invokes the active main_model using this instruction and returns the actual writing to L1. Do not add unconfirmed model suggestions. For missing current candidates, a separate instruction_ready pass uses executor.kind main_model, actual seed/constraints/rejection history in parameters, and purpose limited to 4–6 candidate records. Return those records to L1 before selecting the G→I widget; focus and confirmation remain open, and this preparation never writes the final artifact.

## Must

- Generate distinct, actionable candidate strategies.
- Resolve one material gap per pass.
- Use a widget handoff or execution handoff, never both in one pass.
- Keep `confirmed_prompt` as the writer-owned `T` and retain their freeform additions.

## Must Not

- Do not render, write HTML or invoke an unregistered task tool; writing uses the active main_model directly after its ready instruction.
- Do not force every facet to be specified before confirmation.

## Next

Interaction Pathway sends the selected gap to L3 Designer and L4 Renderer. Execution Pathway invokes main_model directly from L2, without L3/L4. All results/failures return to `l1-pN5-core-module`; only L1 decides Completion.