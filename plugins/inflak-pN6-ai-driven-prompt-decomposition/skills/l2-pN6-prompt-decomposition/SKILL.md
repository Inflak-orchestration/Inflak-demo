---
name: l2-pN6-prompt-decomposition
description: "Use when: P6 Layer 1 routed a source prompt for AI-driven, traceable decomposition into editable components before generating a story."
---

# Layer 2 - Prompt Decomposition Planner

## Layer & Role

L2 Planner assesses every registered category, chooses one next gap by dependencies, and selects one eligible widget or directly invokes the active main_model under a ready preparation/final-story instruction. Do not render or design semantic UI. Execution Pathway bypasses L3/L4. Every result, partial failure or failure returns to `l1-pN6-core-module`; only L1 Router merges canonical state and emits `decision: end`.

Interaction Pathway sends one gap through L3 Designer → L4 Renderer → L1. Execution Pathway directly realizes the ready plan through L2's active main_model → L1. Host Agent Return and Completion belong to L1 and do not enter L2; routing failure returns directly to L1 without L3. Locate each pass on before/after GenAI invocation and prompt-only/artifact-grounded axes before diagnosing its missing per-edge transformation.

Registry state_update_targets are business storage paths (`prompt_structure`, `prompt_components`, `augmented_instruction`), not literal IAI nodes. Preserve them in L1 merge strategy; semantic state_update_target is T for organization or Aug for Brief review, matching the selected edge. Never rename storage to IAI node fields.

## Widget Routing

For a widget-path gap, query the plugin-local `registry/widgets.json` after diagnosis. Filter entries by `compatible_planners`, `gap_categories`, `interaction_goals`, `iai_edges`, expected-return coverage, and required artifact, runtime, and renderer availability. Select one eligible widget registry entry and write only its `id` to `gap_requests[0].selected_widget_id`; do not copy registry-derived concrete metadata into the handoff. Layer 3 validates and realizes the selected entry; it does not select or replace it. This layer does not author the semantic widget contract or render UI.

Rank semantic coverage, artifact specificity, return coverage, runtime fitness, stable registry order then ID. No eligible match returns directly to L1 with reason no_eligible_widget, planner_id, diagnosed_gap (chain/evidence/edge/goal/returns), rejected_candidates and failed checks, return_to. source_material_gap has no local collector; do not invent a goal or open a blank structure widget as if sources existed.

## Inputs

Read the selected `core_handoff.state_snapshot`. Require `user_text`; optionally read `source_prompts`, `prompt_components`, `prompt_structure`, `augmented_instruction`, `prior_returns`, and `generated_story`. Use the newest valid structure or Story Brief return without discarding source provenance.

## IAI Binding

| Node | Domain binding |
| --- | --- |
| H | Author supplying prompts and organization decisions |
| T | Actual source prompts and traceable, evolving components |
| I | Exposed components, tree/cell edits and Brief decisions |
| Aug | Author-reviewed and explicitly approved Story Brief |
| A | Actual generated story |
| G | Active main model: distinct decomposition and story-writing roles |

| Chain ID | Function | Ordered edges |
| --- | --- | --- |
| p6-source | Supply actual source material | `H→T` |
| p6-decomposition | Prepare traceable components for inspection | `T→G, G→I` |
| p6-organization | Author owns organization and component changes | `I→T` |
| p6-brief | Review compiled Story Brief | `I→Aug` |
| p6-story | Generate from approved Brief | `Aug→G, G→A` |

`T` is the evolving collection of source prompts and components. P6 first uses the ordered AI-driven decomposition path `T→G→I`: in that pass, `G` has one role, extracting traceable components and surfacing them for author inspection. The author then updates the intermediate structure with `I→T`, or reviews the compiled Story Brief through `I→Aug`. Only an explicitly approved brief proceeds through the separate ordered execution path `Aug→G→A` for main-model story generation; do not reuse the decomposition `G` role for story writing in the same atomic graph.

## Fragment Extraction

For each prompt `{id, text}`, extract concise components:

```json
{
  "id": "fragment-...",
  "kind": "intent|audience|context|input|constraint|tone|process|output|format|evaluation",
  "text": "",
  "source_prompt_ids": ["prompt-..."]
}
```

Do not invent sources. A fragment derived from more than one prompt lists every contributing id.

## Diagnosis

Assess every registered category as open/resolved/not applicable using current facts, valid returns and explicit scoped delegation. Record statuses, missing transfer and consequence of guessing in existing reason/purpose fields, not new required state. Silence is not delegation; missing source, fragments or approval is not resolved. Select one next gap by real dependencies, not row order.

Before widget routing or preparation, check source availability: no usable actual source exists on `H→T`. There is no registered collector, so request source through L1 using the existing no_eligible_widget diagnosis; never invent sources or open a blank structure widget as if sources existed. This remains a required source check, not a registered widget gap.

| gap_type | Condition | Edge | Interaction goal |
| --- | --- | --- | --- |
| `hierarchical_structure_gap` | Actual components require parent-child containment or ordered decomposition. | `I→T` | `organize_prompt_hierarchy` |
| `topic_grouping_gap` | Actual components require topical categories without directed relationships. | `I→T` | `organize_prompt_topics` |
| `component_gap` | Current organization lacks a material instruction component. | `I→T` | `complete_prompt_components` |
| `brief_review_gap` | Submitted organization needs a compiled, current author-reviewed Brief. | `I→Aug` | `review_story_brief` |
| `instruction_ready` (decision, not gap) | Actual source permits bounded decomposition/Brief compilation, or a complete current Brief is explicitly approved. | `T→G` preparation; `Aug→G, G→A` final | Directly invoke active main_model for the stated bounded purpose and return to L1. |

Emit exactly one semantic gap per widget pass. Describe whether the author needs hierarchy, topical grouping, component completion, or Story Brief review, then select its eligible registry entry. Layer 3 validates and realizes that selected entry. For mixed material, diagnose the first material gap: hierarchy before grouping when it is required. Do not emit both organization gaps in the same pass.

## Widget Handoff

```json
{
  "handoff_type": "planner_handoff",
  "planner_id": "prompt-decomposition",
  "planner_decision": "gap_open",
  "gap_requests": [{
    "chain_id": "p6-organization",
    "gap_type": "hierarchical_structure_gap",
    "selected_widget_id": "prompt-structure-tree",
    "interaction_goal": "organize_prompt_hierarchy",
    "iai_binding": {
      "source_nodes": ["I"],
      "maps_to_edge": "I→T",
      "target_node": "T",
      "ordered_edges": ["T→G", "G→I", "I→T"],
      "reason": "AI-decomposed components have been surfaced to the author and need an author-owned organization update."
    },
    "expected_return": {"structure_kind": "tree", "tree_nodes": [], "root_ids": [], "selected_node_id": "", "expanded_node_ids": [], "fragment_edits": [], "unresolved_ids": [], "freeform_note": ""},
    "order": 1,
    "depends_on_previous": false,
    "display_context": {"source_prompts": [], "fragments": [], "story_structure": {}, "missing_slots": []}
  }],
  "return_to": "l1-pN6-core-module"
}
```

For topic_grouping_gap use prompt-cell/organize_prompt_topics; expected_return is structure_kind "cell_map", cells array, unassigned_fragment_ids array, selected_cell_id string, fragment_edits array, freeform_note string. For component_gap use complete_prompt_components and preserve the current eligible tree or cell return shape. Never combine alternatives or silently convert topology. Both use p6-organization/I→T. The JSON above is a shape illustration; real display must contain actual traceable sources/components, not empty fabricated preparation. Tree display includes actual tree_nodes/root_ids/selected_node_id/expanded_node_ids/unresolved_ids; cell display includes actual cells/unassigned_fragment_ids/selected_cell_id. Both preserve source_prompts/fragments and existing missing-component context.

Each gap includes named chain_id, source_nodes containing edge source, maps_to_edge and matching target_node, meaningful reason preserved through L3, exact goal, all typed returns, actual display, order 1 and truthful depends_on_previous. Existing ordered_edges may retain the antecedent decomposition path; distinguish that preparation from the atomic selected I→T interaction.

A submitted tree or cell map proceeds to the separate Story Brief review; do not generate a story before that review is explicitly approved.

## Brief Review Handoff

After the author submits a coherent organization return, use a bounded instruction_ready main_model pass if Brief compilation is needed, return the actual traceable sections to L1, then select `brief_review_gap` on a fresh routed pass. If current compiled sections already exist, select review directly. Never combine preparation execution and widget handoff or generate a story in a review pass.

```json
{
  "handoff_type": "planner_handoff",
  "planner_id": "prompt-decomposition",
  "planner_decision": "gap_open",
  "gap_requests": [{
    "chain_id": "p6-brief",
    "gap_type": "brief_review_gap",
    "selected_widget_id": "story-brief-review",
    "interaction_goal": "review_story_brief",
    "iai_binding": {
      "source_nodes": ["I"],
      "maps_to_edge": "I→Aug",
      "target_node": "Aug",
      "ordered_edges": ["I→Aug"],
      "reason": "The author-organized prompt structure must become an explicit, approved Story Brief before generation."
    },
    "expected_return": {"structure_kind": "story_brief", "brief_sections": [], "selected_section_id": "", "unresolved_ids": [], "approved": false, "freeform_note": ""},
    "order": 1,
    "depends_on_previous": false,
    "display_context": {"brief_sections": [], "unresolved_ids": []}
  }],
  "return_to": "l1-pN6-core-module"
}
```

After the author returns `approved: true` from `story_brief_review`, compile the approved sections into the execution instruction and have the main model write one complete, emotionally grounded short story. Preserve component provenance in the state record; do not expose provenance markers in the story unless the user asks.

```json
{
  "handoff_type": "planner_handoff",
  "planner_id": "prompt-decomposition",
  "planner_decision": "instruction_ready",
  "execution_instruction": {
    "executor": {"kind": "main_model"},
    "parameters": {"approved_story_brief": {}, "ordered_edges": ["Aug→G", "G→A"]},
    "purpose": "Write one complete story from the author-approved Story Brief. Preserve all approved story requirements and return the story artifact, not decomposition notes."
  },
  "return_to": "l1-pN6-core-module"
}
```

## Must

- When decomposition is needed, emit a bounded instruction_ready with executor.kind main_model and actual source_prompts, then directly produce traceable components and return them to L1. Organization/approval remain open; preparation never writes a story. Brief compilation similarly preserves submitted material and unresolved choices, returning to L1 before review. Final execution directly invokes main_model with the actual approved Brief; main_model_story_generation is descriptive no_tool_execution metadata, never a backend callable.
- Sources keep stable {id,text}; fragments keep {id,kind,text,source_prompt_ids}; multi-source fragments list every contributing source, while genuine user additions may have origin user and empty source IDs. Preserve provenance across split/merge/edit.
- Tree nodes retain id,parent_id,order,label,kind,status,fragment_ids,source_prompt_ids; require exact roots, existing parents, acyclicity, unique sibling order and at most one owner per fragment. Cells retain id,label,fragment_ids and optional source_prompt_ids; topical membership is unique, and deletion returns fragments to unassigned rather than deleting source content.
- Brief sections retain id,kind,label,text,status,source_prompt_ids; kinds are premise, protagonist, setting, conflict, tone_constraints, narrative_direction, unresolved_decision. unresolved_ids exactly matches unresolved sections. Any dependent change resets approval; true requires explicit approval of the current complete Brief. Return-to-structure preserves sections with approved false.

- Keep all user material traceable through components, structures, and `Aug`.
- Emit exactly one semantic organization gap from the diagnosed interaction need and include only the selected registry ID; Layer 3 validates and realizes it.
- Require the explicit `story_brief_review` approval return before generating the story.

## Must Not

- Do not render, write HTML or invoke an invented task tool. Use active main_model directly only for the ready instruction's bounded purpose.
- Do not silently change the author's tree or cell map; reorganization is an explicit user return.

## Next

Interaction Pathway sends the eligible gap to L3 Designer then L4 Renderer. Execution Pathway directly invokes main_model from L2 without L3/L4. Every result/failure returns to `l1-pN6-core-module`; only L1 decides Completion.