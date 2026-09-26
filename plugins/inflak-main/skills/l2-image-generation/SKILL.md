---
name: l2-image-generation
description: "Use when: Layer 1 selects image-generation to derive the current image interaction paradigm and material per-edge gap, or plan justified image generation."
---

# L2 Planner — Image Generation

## Workflow End Authority

Only L1 Router owns canonical workflow state and decides Completion with `decision: "end"`. L2 Planner never presents local completion as final. Eligible gaps enter L3 Designer on Interaction Pathway; `instruction_ready` directly invokes the selected executor on Execution Pathway without L3 or L4. Every result or failure returns directly to `l1-router`.

## Layer & Role

L2 Planner diagnoses gaps, selects interactions, and plans and directly invokes justified execution; it does not design widget semantics or render. For `image-generation` in the `image` task family, interpret the IAI information flow, select the governing paradigm and diagnose exactly one material per-edge gap if present, then filter and rank candidates and select one exact `selected_widget_id`; otherwise emit `instruction_ready` and directly invoke the selected registered image executor. L2 preserves revision-bound evidence; L3 Designer authors only the selected interaction's semantic contract.

## IAI Domain Binding

| Node | Meaning |
| --- | --- |
| H | Image requester retaining or delegating visual decisions |
| T | Current image request and content-bearing visual vocabulary |
| I | User's task-specific constraint, visual choice, or spatial drawing |
| Aug | Image instruction compiled from current evidence and justified visual latitude |
| A | Layout evidence and generated image |
| G | Configured image generator/editor |

## Interaction Chains

| Chain ID | Paradigm / function | Ordered edges |
| --- | --- | --- |
| image-direct | Generate from sufficient intent or delegated visual choices | `H→T, T→Aug, Aug→G, G→A` |
| image-constraints | Incorporate a user-owned image constraint (`image_settings_gap`) | `H→I, I→Aug, Aug→G, G→A` |
| image-vocabulary | Express subject or visual direction in prompt language (`image_keyword_gap`) | `H→I, I→T, T→Aug, Aug→G, G→A` |
| image-spatial | Externalize spatial intent as an actual layout artifact (`image_layout_gap`) | `H→I, I→A, A→Aug, Aug→G, G→A` |

`H→T` supplies intent and `H→I` a retained decision; `I→Aug` incorporates constraints, `I→T` supplies visual vocabulary, and `T→Aug` compiles it with justified latitude. In spatial work, `I→A` creates real sketch/region evidence and `A→Aug` grounds the instruction in it. `Aug→G` is L2's direct invocation of the selected registered executor; `G→A` returns a persisted image, distinct from the earlier layout A and linked to its source.

## Diagnosis

Read state before/after a GenAI invocation and with prompt-only/artifact-grounded resources; a returned sketch is revision-bound grounding evidence. Use intent, current evidence, prior returns and scoped delegation to derive the material missing transfer BEFORE choosing a widget.

Prioritize gap detection and resolution. Assess every registered gap category against current evidence. Silence is not delegation. Known facts, submitted decisions, or explicit scoped user delegation may close a gap; record the evidence and scope, and identify applicability from material information needs rather than field presence. Resolve applicable open gaps through interaction before final artifact execution. After each return, re-enter Layer 1 and reassess remaining gaps. Reserve `instruction_ready` for evidence-backed closure across all relevant categories, or bounded prerequisite preparation that returns to Layer 1 without closing an unresolved user choice or executing the final artifact. Category assessment records applicability, missing material information and closure evidence; widget selection follows the next applicable open gap.

Cover `image_settings_gap` (use, output constraints and exclusions), `image_keyword_gap` (subject and visual treatment), and `image_layout_gap` (placement, composition and actual spatial evidence), checking material ambiguity and the scope of supplied constraints or delegation even when the user has not reserved a choice.

When the image involves spatial relationships or layout decisions, treat unresolved placement, relative size, visual hierarchy, overlap, whitespace or text regions as `image_layout_gap`. Do not add a separate drawing-necessity test: the unresolved spatial decision itself triggers the interaction. Format, style, subject lists and source narrative do not establish spatial closure; assistant-invented composition is not user evidence. Close only the relationships actually settled by current user-supplied sketch/regions, precise spatial instructions or explicit scoped composition delegation; assess the remaining relationships independently. Record that evidence and its scope in `iai_binding.reason` or `execution_instruction.purpose` before declaring readiness.

| gap_type | Condition | Edge | Interaction goal |
| --- | --- | --- | --- |
| `image_settings_gap` | Aug lacks an output-controlling constraint because the user's material choice remains unresolved by evidence or delegation. | `I→Aug` | `refine_image_settings` — supply the unresolved image constraint. |
| `image_keyword_gap` | T lacks material subject or treatment language unresolved by current evidence. | `I→T` | `select_image_keywords` — choose fragments expressing the intended visual content. |
| `image_layout_gap` | The image involves spatial relationships or layout decisions that remain unresolved by current user-supplied sketch/regions, precise spatial instructions or explicit scoped composition delegation, leaving A without settled layout evidence. | `I→A` | `draw_image_layout` — establish the unresolved spatial relationships through actual sketch or region interaction. |
| `instruction_ready` | All applicable gaps are resolved with evidence-backed settings, visual content and spatial closure, including required actual grounding; alternatively, bounded prerequisite preparation returns to Layer 1 with user choices still open and no final image execution. | `Aug→G` then `G→A` | Use generate_image for prompt-only creation or supported edit_image for grounded generation or bounded preparation; return real output. |

Dependencies determine which open gap to resolve next: ground compilation through `A→Aug` in the actual current sketch and reassess its validity when dependent content changes. Technical/grounding failures, unsupported indispensable decisions, or intent to edit an existing output return directly to L1 Router without L3 rather than becoming semantic gaps.

## Widget Registry Routing

| Diagnosed gap | Selected widget ID / L3 skill | Interaction goal | Edge | Required return keys |
| --- | --- | --- | --- | --- |
| `image_settings_gap` | `settings-form` / `l3-settings-form` | `refine_image_settings` | `I→Aug` | `values`, `freeform_note` |
| `image_keyword_gap` | `option-selector` / `l3-option-selector` | `select_image_keywords` | `I→T` | `selected_ids`, `ranking`, `freeform_note` |
| `image_layout_gap` | `canvas-editor` / `l3-canvas-editor` | `draw_image_layout` | `I→A` | `artifact_ref`, `regions`, `mask_ref`, `freeform_note` |

| Routing rule | Requirement |
| --- | --- |
| Eligibility | Hard-filter by exact planner, gap, goal, atomic edge, all required return keys, current artifact support, and available runtime capabilities/libraries. Agent-interpreted semantics must cover the return; `planner_declared` cannot authorize unsupported fields. |
| Selection | Choose one eligible exact ID for the diagnosed gap, not a sequence of widgets. Rank by semantic coverage, artifact specificity, return coverage, runtime fitness, stable registry order, then registry `id`. |
| Spatial evidence | An empty drawing surface is valid for a new sketch; never invent a source image reference. Artifact-grounded work requires actual current evidence. |
| No eligible entry | Return a nonterminal failure directly to L1 without L3: `reason: no_eligible_widget`, `planner_id: image-generation`, `diagnosed_gap` (chain/evidence/edge/goal/returns), `rejected_candidates` (IDs and failed constraints), `return_to: l1-router`. Never substitute another widget or fake readiness. |

## Gap Handoff

Emit one request; the edge source must occur in `source_nodes` and its destination must equal `target_node`. Pending I is not submitted input. Layer 3 preserves `chain_id` and `reason`: source/transfer/target/closure evidence and why guessing is unjustified; copy no contract or renderer metadata. This example assumes the user reserved the two displayed garden treatments and delegated other details:

```json
{
  "handoff_type": "planner_handoff",
  "planner_id": "image-generation",
  "planner_decision": "gap_open",
  "gap_requests": [{
    "chain_id": "image-vocabulary",
    "gap_type": "image_keyword_gap",
    "interaction_goal": "select_image_keywords",
    "iai_binding": {"source_nodes": ["I"], "maps_to_edge": "I→T", "target_node": "T", "reason": "On I→T, I lacks the reserved botanical-versus-photographic selection, leaving T without chosen treatment language; guessing exceeds delegation and changes the intended appearance. Returned selected_ids resolve to the displayed prompt fragments and supply that missing language to T."},
    "display_context": {"selection_mode": "multi", "current_prompt": "Let me choose botanical illustration or garden photography; you decide the rest.", "options": [{"id": "botanical", "label": "Botanical illustration", "dimension": "subject_treatment", "prompt_fragment": "an illustrated botanical garden with carefully drawn plants", "impact": "Emphasizes drawn botanical detail."}, {"id": "photographic", "label": "Garden photography", "dimension": "subject_treatment", "prompt_fragment": "a photographic garden scene with natural textures", "impact": "Emphasizes photographic realism."}]},
    "expected_return": {"selected_ids": [], "ranking": [], "freeform_note": ""},
    "selected_widget_id": "option-selector",
    "order": 1,
    "depends_on_previous": false
  }],
  "return_to": "l1-router"
}
```

For `refine_image_settings`, `settings-form` returns `values: {}`, `freeform_note: ""`. For `draw_image_layout`, use `image-spatial` and `canvas-editor` on `I→A`, returning `artifact_ref: ""`, `regions: []`, `mask_ref: ""`, `freeform_note: ""` as real revision-bound sketch/region evidence, not a text form; include `target_tool: edit_image` only if already identified. Keyword returns preserve multi-selection, stable `id`, `label`, `dimension`, `prompt_fragment` and selected IDs without requiring every dimension.

## Output (planner_handoff)

`instruction_ready` is a planner decision, never a registered gap or workflow completion. This example assumes the user actually supplied: "Generate a square watercolor garden image with no text for a decorative card. You may choose the garden details, composition and lighting." The intended use, square format, text exclusion, subject and treatment are supplied; delegation is limited to garden details, composition and lighting:

```json
{
  "handoff_type": "planner_handoff",
  "planner_id": "image-generation",
  "planner_decision": "instruction_ready",
  "execution_instruction": {
    "executor": {"kind": "tool", "name": "generate_image"},
    "parameters": {"prompt": "A square watercolor garden image with no text for a decorative card. Choose garden details, a harmonious composition and lighting within the user's explicit delegation; preserve the supplied subject, treatment, format and text exclusion."},
    "purpose": "Settings are closed by the user-supplied decorative-card use, square format and no-text constraint; visual content is closed by the supplied watercolor garden direction and explicit garden-detail delegation; layout is closed by explicit composition delegation, with lighting also delegated. Generate within that scope and return actual persisted artifact references to Layer 1."
  },
  "return_to": "l1-router"
}
```

For submitted sketch-layout grounding, select supported `edit_image` with the actual sketch reference, compiled instruction and any required region/mask inputs under its current schema. Never claim text-only generation consumed the sketch or invent references; unavailable grounding capability returns to Layer 1.

## Inputs (from core_handoff and widget registry)

- `selected_planner: image-generation` and `state_snapshot.user_text` are required.
- Consume optional `image_settings`, `image_keywords`, `image_layout`, `generated_image`, and `prior_returns` from `state_snapshot`. Read actual layout/output artifacts through their current references; no standalone source image is required for prompt-only creation.
- Consume the routing projection from `registry/widgets.json`: candidate IDs, planner/gap/goal/edge declarations, supported returns and semantics, artifact support, capability and library requirements, plus current host runtime availability.
- Validate executor availability and actual grounding inputs against the current planner/tool registries.

## Procedure

1. Inspect `core_handoff`, intent, current returns and delegation; position both axes and assess every registered category for applicability, missing material information and closure evidence.
2. Select the next applicable open gap by dependencies, then its chain; trace source to target and the consequence of guessing. Bound prerequisite preparation while preserving unresolved choices; distinguish technical failures from semantic gaps.
3. For the selected gap, filter/rank and emit one exact selected-widget request with `chain_id`, or return a structured failure directly to L1 without L3. Emit `instruction_ready` with an allowed executor only for evidence-backed closure across relevant categories or bounded prerequisite preparation, validating real grounding inputs; open gaps prohibit final generation.
4. Interaction Pathway sends an eligible selected gap to L3 Designer then L4 Renderer. Execution Pathway has L2 directly invoke the selected registered tool with the declared `execution_instruction`, without L3 or L4. Every widget return, actual tool result, partial failure or failure immediately re-enters L1 to reassess all categories before another action.

## Must

- Ground the selected paradigm and gap in user intent, current evidence and justified inference; use delegated invention only within its actual scope.
- Preserve submitted settings, keyword IDs/dimensions/prompt fragments, exact text and real layout references in the compiled prompt, with their evidence and delegation scope.
- Route every material `image_layout_gap` to `canvas-editor`; never use `settings-form`, `content-editor`, or `structure-editor` as a layout substitute.
- For an open layout gap, emit `gap_open` with `selected_widget_id: canvas-editor`, `chain_id: image-spatial`, `interaction_goal: draw_image_layout` and edge `I→A`; load `l3-canvas-editor` to design the interaction, then let L4 render it. Return the submitted spatial evidence to L1 before reassessment and grounded execution; do not call `generate_image` while that gap remains open.
- Select exactly one entry passing all hard constraints, preserve its exact ID and use deterministic ranking; when instruction-ready, directly invoke the selected registered executor with the declared instruction.

## Must Not

- Do not generate from settings alone when a consequential subject decision is neither supplied nor delegated.
- Do not add a generic approval checkbox or invent redundant gaps; preserve evidence-backed settled decisions unless relevant dependent evidence changes.
- Do not fabricate file identifiers, images, references or tool success; do not execute before `instruction_ready`, render, or decide Completion.
- Do not reuse stale layout evidence after dependent content changes.

## Tools

L2 Planner may select and directly invoke only registered `generate_image` or `edit_image` with current planner permission, available runtime and supported inputs after `instruction_ready`. Execute the declared `execution_instruction.executor` with its parameters and purpose, returning actual results or failures directly to L1. These tools remain session-registered; registration does not make them L3 operations or Host Agent Return. L4 Renderer alone owns `render_html_widget`; L2 never invokes rendering tools.

## Stop / Continue / Escape

- **Stop:** End this local pass after handing an eligible gap to L3 or returning an actual execution result or failure directly to L1; only L1 decides Completion.
- **Continue:** A widget or execution return supplies current evidence; Layer 1 reconstructs it before another pass.
- **Escape:** Required grounding is unavailable, a tool fails, or an indispensable decision is refused; return the actual failure directly to L1 without L3, not a fake gap or invented readiness.

## Next

Interaction Pathway: send an eligible open gap with `selected_widget_id` to L3 Designer for validation and interaction design, then L4 Renderer. Execution Pathway: after `instruction_ready`, L2 directly invokes the selected executor with the declared instruction, without L3, L4, or a separate executor skill. Routing failures return directly to L1 without L3. All actual results and failures return to `l1-router`, not directly to this planner; only L1 decides Completion.
