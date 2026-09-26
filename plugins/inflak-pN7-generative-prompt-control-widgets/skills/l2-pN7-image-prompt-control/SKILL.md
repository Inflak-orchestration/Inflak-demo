---
name: l2-pN7-image-prompt-control
description: "Use when: P7 must identify one high-impact, controllable image-prompt gap, collect a structured adjustment, prepare generation parameters, or request image generation."
---

# Layer 2 - Image Prompt Control Planner

## Layer & Role

L2 Planner assesses every registered gap, chooses one next material gap by dependencies and one eligible widget, or directly invokes the ready executor/main_model. It does not design semantic UI or render. Execution Pathway bypasses L3/L4. Every preparation, generated result or failure returns to `l1-pN7-core-module`; only L1 Router merges canonical state and emits `decision: end`.

Interaction Pathway sends one gap through L3 Designer → L4 Renderer → L1. Execution Pathway directly realizes the ready plan through L2's executor/main_model → L1. Host Agent Return and Completion belong to L1 and do not enter L2; routing failure returns directly to L1 without L3. Locate each pass on before/after GenAI invocation and prompt-only/artifact-grounded axes before diagnosing its missing per-edge transformation.

Registry state_update_targets are existing business paths under control_spec, not literal IAI nodes. Preserve the selected entry's paths for L1 merge; semantic state_update_target is Aug, matching I→Aug. Do not rename paths or invent canonical IAI state fields.

## Widget Routing

For a widget-path gap, query the plugin-local `registry/widgets.json` after diagnosis. Filter entries by `compatible_planners`, `gap_categories`, `interaction_goals`, `iai_edges`, expected-return coverage, and required artifact, runtime, and renderer availability. Select one eligible widget registry entry and write only its `id` to `gap_requests[0].selected_widget_id`; do not copy registry-derived concrete metadata into the handoff. Layer 3 validates and realizes the selected entry; it does not select or replace it. This layer does not author the semantic widget contract or render UI.

Rank semantic coverage, artifact specificity, return coverage, runtime fitness, stable registry order then ID. No eligible match returns nonterminal reason no_eligible_widget, planner_id, diagnosed_gap (chain/evidence/edge/goal/returns), rejected_candidates with failed checks and exact L1 return_to; bypass L3 without substitution.

## Inputs

Read the selected `core_handoff.state_snapshot`. Require `user_text`; optionally read `source_prompt`, `current_prompt`, `control_spec`, `provider_capabilities`, `prior_returns`, `last_image`, and `image_feedback`. Preserve stable control ids across the newest valid prompt and widget returns.

## P7 State Model

| Node | Domain binding |
| --- | --- |
| H | User controlling image intent and feedback |
| T | Actual readable source prompt, not overwritten by a preview |
| I | Exposed exact-span parameters and actual user adjustments |
| Aug | Canonical structured control_spec with current acceptance |
| A | Actual generated image and referenced feedback evidence |
| G | Main-model control analysis or the separate configured image generator |

| Chain ID | Function | Ordered edges |
| --- | --- | --- |
| p7-control-analysis | Expose traceable parameters from actual text | `T→G, G→I` |
| p7-control-update | User-owned structured control changes | `I→Aug` |
| p7-image-execution | Generate from currently confirmed controls | `Aug→G, G→A` |

`T` is the readable source prompt. `Aug` is `control_spec`, the canonical structured state. P7 uses `T→G→I` to generate controllable inline parameters, `I→Aug` to merge user control returns, and a separate `Aug→G→A` execution path to render the confirmed image. The returned `compiled_prompt` is a live preview for user review, not a structured-state-to-text state transition. Do not treat a raw prompt edit as a hidden control return: retain it as prompt text and re-analyze it through `T→G→I`.

Each parameter is derived from a planner-supplied prompt unit and contains a stable `id`, exact source `span`, readable `text`, and one control schema. Preserve those IDs across turns when their semantic unit survives. When a changed parameter replaces text, recompute later spans before opening the next editor.

## Capability Policy

Read `provider_capabilities` before offering numerical controls.

- When `weighted_prompt_syntax` is true, represent weights using the provider's documented syntax in the generation prompt preview.
- Otherwise, encode the desired priority as unambiguous natural-language composition and emphasis clauses. Call it `semantic_priority`, never model attention.
- Offer attention-evidence feedback only when `attention_visualization` is true. Otherwise use the user's described artifact mismatch as evidence.

## Gap Diagnosis

Assess every registered category as open/resolved/not applicable against current nouns, relations, style, exclusions, real feedback and explicit scoped delegation. Record evidence/status/missing transfer/consequence in existing reason/purpose fields, not new mandatory state. Silence is not delegation, and missing text/candidates/acceptance never counts as resolved. Choose one next gap by real dependencies and visual impact, not table order. Concrete content exploration requires a candidate-bearing pass before role/weight controls; an explicit hierarchy/composition/weight-only request narrows that dependency, not all other checks.

| gap_type | Condition | Edge | Interaction goal |
| --- | --- | --- | --- |
| `entity_scope_gap` | Material source unit needs concrete alternatives or clarification. | `I→Aug` | `resolve_embedded_prompt_token` |
| `subject_priority_gap` | Known entities need user-owned visual roles. | `I→Aug` | `set_subject_hierarchy` |
| `composition_allocation_gap` | Frame shares or supplied empty space remain unresolved. | `I→Aug` | `allocate_composition` |
| `attention_weight_gap` | A concept needs stronger/weaker supported priority. | `I→Aug` | `adjust_semantic_priority` |
| `candidate_preference_gap` | One material dimension needs concrete preference evidence. | `I→Aug` | `compare_candidate_directions` |
| `prompt_confirmation_gap` | Sufficient controls lack explicit acceptance of the current preview. | `I→Aug` | `review_controlled_generation_prompt` |
| `instruction_ready` (decision, not gap) | Actual text supports bounded analysis, or current accepted Aug closes all applicable pre-generation gaps. | `T→G` preparation; `Aug→G, G→A` final | Direct L2 main_model preparation or registered generate_image invocation; return to L1. |

## Procedure

1. Read L1's source_prompt, using actual user_text when absent. If current semantic units/candidates are missing, plan a separate bounded instruction_ready main_model analysis and return the actual records to L1 before choosing an interaction. Preserve stable IDs and exact source spans; do not combine model preparation with widget handoff.
2. When the user asks to adjust, explore, or control concrete prompt content, first open `entity_scope_gap` for the highest-impact material units that have meaningful alternatives. Supply 3 to 5 concrete, mutually distinguishable candidate values per unit, including the exact current text as a `Keep current: …` option. Candidates must be image-ready phrases specific to that source span, not role names, generic labels, IDs, or minor paraphrases. Use `embedded-token-inspector` and do not open `subject_priority_gap` until this candidate-bearing return has been accepted or explicitly skipped. Skip this prerequisite only when the user explicitly limited the request to role hierarchy, composition, or weight.
3. For the selected gap supply prompt_document and actual parameter domains/candidates in display_context, plus exact selected_widget_id; do not author controls, widget_type or presentation. L3 designs the inline interaction. Every option has a visible label, not only an ID.
4. Consume L1's validated merge of parameter_values by stable ID into control_spec.inline_parameters; preserve accepted values unless explicitly replaced and retain changed_parameter_ids as provenance. Raw prompt edits require re-analysis, offset recomputation and invalidation of stale acceptance.
5. Diagnose the next gap. Prefer concrete entity/content candidates before subject hierarchy and numerical priority, and confirm a semantic unit before controlling its role or weight.
6. For `candidate_preference_gap`, require 3 to 6 meaningfully distinct prepared candidates for exactly one unresolved dimension. Each has a stable ID, concise visible label and one-sentence concrete image-change description. Missing candidates need a separate bounded preparation pass through L1. Never open this gap with empty, ID-only, role-only or minor-paraphrase alternatives.
7. When the specification is sufficient, prepare a generation prompt preview from `control_spec`. Preserve the requested entities and exclusions; make hierarchy, ratios, and semantic priority explicit without treating the preview as a replacement text-prompt state.
8. Select prompt-control-review for prompt_confirmation_gap. Only after acceptance of this exact revision and closure of applicable gaps emit instruction_ready and directly call registered generate_image.
9. After a generated image, use new user feedback to reopen only the relevant gap. Do not invent attention evidence.

## Gap Handoff

```json
{
  "handoff_type": "planner_handoff",
  "planner_id": "image-prompt-control",
  "planner_decision": "gap_open",
  "gap_requests": [
    {
      "chain_id": "p7-control-update",
      "gap_type": "attention_weight_gap",
      "selected_widget_id": "attention-weight-control",
      "interaction_goal": "adjust_semantic_priority",
      "iai_binding": {
        "source_nodes": ["I"],
        "maps_to_edge": "I→Aug",
        "target_node": "Aug",
        "ordered_edges": ["T→G", "G→I", "I→Aug"],
        "reason": "The AI-identified prompt control needs a user-owned structured value before image generation."
      },
      "expected_return": {"parameter_values": {}, "changed_parameter_ids": [], "compiled_prompt": "", "freeform_note": ""},
      "order": 1,
      "depends_on_previous": false,
      "display_context": {
        "prompt_document": {"text": "", "parameters": []},
        "weight_mode": "provider_native|semantic_priority"
      }
    }
  ],
  "return_to": "l1-pN7-core-module"
}
```

## Ready Handoff

Gap examples are schemas, not evidence: never render empty prompt text/parameters or a literal alternative enum. All six IDs use p7-control-update/I→Aug, source_nodes contains I and target_node/state_update_target is Aug. Business control_spec paths remain deterministic L1 merge destinations. Preserve chain_id/reason through L3, truthful dependency/order, and exact typed returns. Standard returns are parameter_values object, changed_parameter_ids array, compiled_prompt string, freeform_note string. Review adds action accept|edit|reopen_control and control_category string, nonempty only for reopen_control. Select exactly one known category; edits/reopen invalidate acceptance.

Parameters preserve id, span, text, kind, control. Use ordered nonoverlapping UTF-16 half-open spans satisfying exact JS text.slice(start,end) === parameter.text; never guess offsets. Hierarchy has exactly one primary, with supporting/environment roles for known entities. Composition uses independent relative frame-share controls with type slider, explicit finite min/max/step, relative-share units and grounded current values; no invented initial allocation. A 0–100 range is only a scale, not percent units or a fixed-total budget. Do not require a sum of 100, normalize values or rebalance other parameters; negative_space only when supplied, no pixel guarantees. These values express approximate composition intent, not attention weights. Legacy percent/fixed-total schemas must be resolved through L1 before handoff, never silently relabeled. Weights use supplied bounds/step and neutral 1.0; provider_native requires documented capability, otherwise semantic_priority. Candidate preference keeps similar/dissimilar disjoint and never inserts rejected content as positive prompt text.

Precise domain schema: prompt_document is `{text: string, parameters: array}`; each parameter retains `{id: string, span: {start: integer, end: integer}, text: string, kind: string, control: object}`. Nested control preserves `type` (select/text/select_or_text/slider/number as applicable), `label`, typed `value`, optional `options`, `allow_custom_value`, `replace_template`, and supplied numeric min/max/step. Option records retain stable `id`, readable `label`, concrete `value`; candidate-preference records also retain concrete `description` and any separate dissimilar_options. Do not confuse these domain controls with L3's canonical top-level controls. parameter_values keys are supplied parameter IDs and values follow each declared domain type; changed_parameter_ids is a unique string array of actually changed supplied IDs also present in parameter_values. No new executor arguments are implied by this schema.

Missing parameter/candidate analysis may use a separate bounded instruction_ready, executor.kind main_model, actual source text and provider capabilities, purpose limited to traceable units/candidates. L2 directly invokes main_model then returns preparation to L1 before interaction; user choices remain open and no image is generated. Missing source cannot be repaired by inventing a prompt: return the blocker to L1.

```json
{
  "handoff_type": "planner_handoff",
  "planner_id": "image-prompt-control",
  "planner_decision": "instruction_ready",
  "execution_instruction": {
    "executor": {"kind": "tool", "name": "generate_image"},
    "parameters": {"prompt": "<actual currently confirmed generation prompt preview>", "size": "1024x1024", "quality": "high"},
    "purpose": "render the confirmed P7-controlled image prompt"
  },
  "return_to": "l1-pN7-core-module"
}
```

## Must Not

- Do not copy concrete registry metadata into the planner handoff; emit only the selected registry ID.
- Do not ask Layer 3 to select or replace the entry; it validates and realizes the L2 selection.
- Do not describe accepted controls as compiling `Aug` back into `T`; final rendering uses the separate `Aug→G→A` execution path.
- Do not claim a semantic priority is a measured diffusion attention value.
- Do not call generate_image before instruction_ready, render UI or discard accepted controls. Pass only tool-supported parameters; retain control_spec and ordered_edges as planning/state context, not invented tool arguments.

## Next

Interaction Pathway sends the selected gap to L3 Designer then L4 Renderer. Execution Pathway directly invokes main_model or generate_image from L2 without L3/L4. Every result/failure returns to `l1-pN7-core-module`; only L1 decides Completion.