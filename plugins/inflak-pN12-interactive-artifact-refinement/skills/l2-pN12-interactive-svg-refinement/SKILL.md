---
name: l2-pN12-interactive-svg-refinement
description: "Use when: P12 must derive a task-specific interaction from a refinement prompt and current SVG revision, collect its typed return, and commit the result."
---

# Layer 2 - P12 Interactive Artifact Refinement Planner

## Layer & Role

Assess every registered gap as resolved, open, or not applicable using current evidence and scoped delegation; record that evidence in `iai_binding.reason` or `execution_instruction.purpose`. Silence is not delegation. Choose one next material gap by dependencies, not a mandatory stage checklist. L2 selects an exact eligible interaction or emits `instruction_ready` and loads exec-pN12-artifact-refinement to invoke one registered tool or active `main_model`. Execution Pathway bypasses L3/L4 and returns actual results/failures to `l1-pN12-core-module`. Never render or write SVG markup here.

## Widget Routing

For a widget-path gap, query the plugin-local `registry/widgets.json` after diagnosis. Filter entries by `compatible_planners`, `gap_categories`, `interaction_goals`, `iai_edges`, expected-return coverage, and required artifact, runtime, and renderer availability. Select one eligible widget registry entry and write only its `id` to `gap_requests[0].selected_widget_id`; do not copy registry-derived concrete metadata into the handoff. Layer 3 validates and realizes the selected entry; it does not select or replace it. This layer does not author the semantic widget contract or render UI.

## Inputs

Read the selected `core_handoff.state_snapshot`. Require `source_prompt` and `source_artifact_ref`; optionally read `artifact_scene`, `artifact_analysis`, `interaction_specs`, `active_interaction_id`, `preview_state`, `refinement_candidates`, `candidate_assets`, `interaction_returns`, `active_object_ids`, `patch_state`, `revision_history`, `acceptance_state`, and `prior_returns`. Reject stale artifact revisions and use the newest typed interaction return.

## IAI Binding

| Node | P12 binding |
| --- | --- |
| `H` | User who supplies a high-level goal, then manipulates the GenAI-authored interaction and its artifact preview. |
| `T` | Exact refinement prompt and constraints. |
| `I` | A GenAI-authored, artifact-grounded interaction specialized to the exact prompt, current scene, stable targets, and declared capabilities; the human manipulates its reversible preview and may apply, regenerate, correct, or reject it. |
| `Aug` | Unused. P12 never creates an augmented instruction or prompt. |
| `A` | Current canonical SVG document, stable scene objects, capabilities, candidate assets, and committed revisions. |
| `G` | GenAI that jointly analyzes the prompt and current revision, authors the task-specific interaction spec, materializes required semantic candidates, and validates the result. |

## Interaction Chains

| Paradigm | Ordered edges | Function |
| --- | --- | --- |
| `scene-grounding` | `A→G` | Inspect and analyze the exact current revision. |
| `interaction-synthesis` | `T→G`, `A→G`, `G→I` | Generate one bounded interaction spec whose archetype, controls, target bindings, evidence, and preview operations are specialized to the prompt and current scene. |
| `preview-preparation` | `G→A` | Materialize any semantic asset required for the generated interaction and prepare one reversible artifact preview before asking the user to decide. |
| `post-generation-interaction` | `G→I` | Let the user directly manipulate the generated artifact-grounded interaction; never require target discovery from scratch or approval of an unseen result. |
| `artifact-commit` | `I→A` | Commit one confirmed revisioned operation set. |
| `iterative-validation` | `A→G`, `G→I`, `I→A` | Validate the resulting revision and accept it or continue refinement. |

## Diagnosis

Locate timing (before/after generation), artifact and capability evidence first. Inspection, model analysis, interaction-spec/preview preparation, regeneration, candidate materialization, patch compilation and validation are bounded execution, not user gaps. Bounded work requires its own inputs and permission and cannot authorize final mutation while material choices remain open. Source/capability failure returns directly to L1.

| gap_type | Condition | Edge | Interaction goal |
| --- | --- | --- | --- |
| `interaction_execution_gap` | A complete, current-revision preview awaits a meaningful typed human decision or adjustment. | `G→I` | `run_adaptive_refinement_interaction`, `correct_interaction_target`, `adjust_object_color`, `harmonize_object_colors`, `adjust_svg_collage_layout`, or `assign_objects_to_layout_regions`, matching exact selected entry. |
| `artifact_comparison_gap` | The validated revision has not been compared with the immediately preceding SVG revision. | `I→A` | `compare_svg_revisions` |
| `artifact_acceptance_gap` | The latest validated revision has not been accepted or routed into another bounded pass. | `I→A` | `review_refined_artifact` |
| `instruction_ready` | Relevant choices are closed for approved work, or one bounded prerequisite has independent evidence and permission. | `A→G`, `T→G`, `G→A`, or `I→A`, according to work | Direct registered inspect/materialize/apply/validate or main-model analysis/spec compilation; return actual results to L1. |

## Adaptive Interaction Model

Every interaction spec contains `interaction_id`, exact `prompt_span`, `interaction_goal`, `archetype`, `target_hypotheses`, `default_target_ids`, `artifact_evidence`, `confidence`, `controls`, `preview_operations`, `return_schema`, `annotation`, and field provenance. Each target hypothesis contains `rank`, stable `object_ids`, numeric `confidence`, and artifact-grounded evidence. The selected archetype and every control must exist in the selected widget registry entry; every operation must be supported by the bound objects' inspected capabilities.

Generate exactly one active interaction for the first unresolved user goal. The default state is the generated result on the artifact, not an abstract recommendation or empty form. Prefer the narrowest useful modality: direct manipulation and alignment for transforms, swatches and scoped mappings for color, text controls for copy, layer controls for order, and materialized variant comparison for semantic add or replacement. Include target alternatives only when evidence is materially ambiguous. Free selection is available only when the interaction declares target correction and the user rejects all grounded alternatives.

The annotation contains only `object_ids`, a concise `label`, and an `explanation`. The preview contains typed operations and host bindings but is transient UI state and must never be submitted as SVG markup. `Adjust` updates that preview locally through declared controls. `Regenerate` returns to GenAI. Only `Apply` makes the current typed preview eligible for `I→A` commit.

## Interaction Archetype Selection

Choose the narrowest registry archetype that lets the user express the exact prompt more faithfully than a generic form. This choice is part of GenAI's `G→I` output and must be grounded in both prompt semantics and inspected object capabilities.

| Prompt and artifact condition | Required selected widget | Generated interaction |
| --- | --- | --- |
| The prompt changes fill, stroke, text color, palette, warmth, saturation, contrast, or color harmony for one or more stable objects with presentation capabilities. | `object-color-palette` | Bind the named targets, current colors, supported channels, artifact-aware swatches, custom color input, and reversible `set_object_style` preview. |
| The prompt changes overall composition, multiple object placements, spatial regions, alignment relationships, or asks the user to specify what belongs where. | `svg-collage-layout-board` | Bind the full relevant scene, stable item ids, transforms, locks, capabilities, object list, guides, optional semantic regions, and reversible layout preview. |
| The prompt changes one already-grounded object's position, size, rotation, text, or layer order. | `refinement-control` | Bind only the necessary direct manipulation and typed controls. |
| The prompt adds or replaces semantic visual content. | `semantic-variant-review` after materialization | Bind materialized variants and only the supported placement controls. |
| The task primarily requires inspecting evidence or correcting an uncertain target before a specialized control is possible. | `refinement-recommendation-inspector` | Bind the ranked targets and the smallest generated correction interaction. |

Do not select `refinement-control` for a color request that can use visible swatches. Do not reduce a multi-object layout request to independent numeric fields. Do not open `svg-collage-layout-board` for a single precise transform unless the user asks for broader spatial composition.

Deterministic operations are `set_transform`, `set_order`, `add_text`, and `update_text`. Semantic operations are `add_cutout`, `replace_cutout_asset`, and `remove_object`. Every operation must be executable and previewable before opening the interaction: `update_text` and `add_text` require the actual non-empty user-visible `text`; `set_transform` requires at least one explicit translate, rotate, or scale value; `set_order` requires `direction`; and semantic add or replacement requires a materialized same-session raster `asset_file_id`. Never use an operation name such as `update_text` as a user-visible result label, and never ask the user to apply a placeholder, omitted value, or implementation token. Describe the concrete result in plain language while preserving the typed operation as the patch source of truth. Replacement preserves the stable target id, transform, and z-order. Never accept raw SVG, XML, CSS, selectors, scripts, path data, external URLs, or data URIs.

## Handoffs

Both pathways require `handoff_type: planner_handoff`, `planner_id: pN12-interactive-svg-refinement`, `planner_decision`, and `return_to: l1-pN12-core-module`. For `gap_open`, emit exactly one `gap_requests` record with `gap_type`, `interaction_goal`, `selected_widget_id`, grounded `display_context`, and `iai_binding: {source_nodes, maps_to_edge, target_node, reason}`. Its atomic edge must occur in its named chain and match the diagnosis and selected registry entry; nonempty `source_nodes` includes that edge's origin and `target_node` equals its destination and allowed `state_update_target`. Use `post-generation-interaction` for generated interaction returns and `iterative-validation` for comparison/acceptance. For `instruction_ready`, omit `gap_requests` and widget identity; require `execution_instruction` with `executor` (`kind: tool` and allowed registered `name`, or `kind: main_model`), object `parameters`, nonempty evidence-backed `purpose`, and existing result/interaction bindings. Ground the plan in the applicable named chain, current source/revision and actual permission without adding tool API fields.

Every interaction request includes a named `chain_id`, `order: 1`, `depends_on_previous`, and exact typed `expected_return`; examples below omit no obligation. Preserve source/edge/target and meaningful `reason`; edge destination is the allowed IAI state target, while L1 deterministically merges domain records by interaction ID and revision. Rank eligible entries by semantic coverage, artifact specificity, return coverage, runtime fitness, registry order then ID. No eligible entry returns `reason: no_eligible_widget`, `planner_id`, `diagnosed_gap` (chain, evidence, edge, goal, returns), `rejected_candidates`, and `return_to: l1-pN12-core-module`, bypassing L3.

Schema routing preserves the selected entry's existing return policy. Fixed returns use exactly the listed keys; planner-declared returns retain the actual spec's typed schema, not a union of fields from other widgets. These are the existing local return shapes, not new required controls:

| Selected widget | Return keys and types |
| --- | --- |
| refinement-recommendation-inspector | `interaction_id: string`, `action: string enum apply/adjust/regenerate/correct/reject/dismiss`, `target_object_ids: string[]`, `operations: object[]`, `control_values: object`, `selected_alternative_rank: integer`, `new_constraint: string` |
| refinement-control | `interaction_id: string`, `artifact_id: string`, `base_revision: positive integer`, `operations: object[]`, `control_values: object`, `action: string enum apply/adjust/regenerate/reject/dismiss` |
| object-color-palette | `interaction_id: string`, `artifact_id: string`, `base_revision: positive integer`, `target_colors: object[]` with string `object_id`, `channel`, `value`, `operations: object[]`, `action: string enum apply/reset/regenerate/reject/dismiss` |
| svg-collage-layout-board | `interaction_id: string`, `action: string`, host-bound `artifact_id: string`, `base_revision: positive integer`, `operations: object[]`; preserve the selected spec and host-owned serialization below |
| semantic-variant-review | `interaction_id: string`, `candidate_id: string`, `variant_id: string`, `artifact_id: string`, `base_revision: positive integer`, `operations: object[]`, `control_values: object`, `action: string enum apply/regenerate/reject/dismiss` |
| refined-artifact-review | `revision: positive integer`, `decision: string enum accept/continue/revise/dismiss`, `selected_issue_id: string`, `revision_request: string`, `freeform_note: string` |
| svg-revision-comparison | `action: string enum accept_revision/continue_editing` |

L3 maps source/interaction/revision metadata from the actual bound display/spec, user values from declared controls, and actions from explicit commands. Serialize JSON types unchanged; preserve optional/empty follow-up values without fabricating evidence or adding metadata controls. Preview/reset/adjust are nonterminal; only Apply can authorize complete current-revision operations. Review decisions only supply revision-bound evidence to L1.

Load the [execution skill](../exec-pN12-artifact-refinement/SKILL.md) for ready execution. Host-committed `patch_result` is already an effect: return to L1 and never replay it. Layout host owns geometry: `artifact-layout-draft` supplies `event.detail.activeObjectId`, `itemTransforms`, `baseRevision`; Reset uses `window.resetArtifactLayoutDraft()`, Apply sends only `window.submitWidget({action:"apply",interaction_id})`, and host injects authoritative operations.

Open the generated adaptive interaction:

```json
{"handoff_type":"planner_handoff","planner_id":"pN12-interactive-svg-refinement","planner_decision":"gap_open","gap_requests":[{"chain_id":"post-generation-interaction","order":1,"depends_on_previous":false,"gap_type":"interaction_execution_gap","selected_widget_id":"refinement-recommendation-inspector","interaction_goal":"run_adaptive_refinement_interaction","iai_binding":{"source_nodes":["G"],"maps_to_edge":"G→I","target_node":"I","reason":"The prompt-specific preview exists but still needs the user's adjustment or Apply decision; guessing would commit an unapproved change."},"display_context":{"artifact_ref":{"fileId":"","revision":1},"interaction_spec":{"interaction_id":"","prompt_span":"","archetype":"","default_target_ids":[],"target_hypotheses":[],"controls":[],"preview_operations":[],"annotation":{}}},"expected_return":{"interaction_id":"","action":"apply|adjust|regenerate|correct|reject|dismiss","target_object_ids":[],"operations":[],"control_values":{},"selected_alternative_rank":1,"new_constraint":""},"merge_strategy":"replace_interaction_return_by_interaction_id","next_planner_action":"re-enter Layer 1"}],"return_to":"l1-pN12-core-module"}
```

Ready patch:

```json
{"handoff_type":"planner_handoff","planner_id":"pN12-interactive-svg-refinement","planner_decision":"instruction_ready","execution_instruction":{"executor":{"kind":"tool","name":"apply_svg_presentation"},"parameters":{"file_id":"","base_revision":1,"operations":[]},"interaction_binding":{"interaction_id":"","interaction_goal":"commit_refinement_to_artifact","action":"apply"},"purpose":"Commit the current interaction preview after Apply; choose apply_svg_layout or apply_svg_structure when that is the homogeneous operation family."},"return_to":"l1-pN12-core-module"}
```

Ready semantic candidate:

```json
{"handoff_type":"planner_handoff","planner_id":"pN12-interactive-svg-refinement","planner_decision":"instruction_ready","execution_instruction":{"executor":{"kind":"tool","name":"generate_image"},"parameters":{"prompt":"One isolated complete object matching the generated semantic interaction and current SVG visual direction, clean silhouette, transparent background, no text, no frame","size":"1024x1024","quality":"high","background":"transparent","require_transparent_background":true},"result_binding":{"interaction_id":"","candidate_id":"","variant_id":"","state_target":"candidate_assets"},"purpose":"Materialize one safe transparent raster result before rendering its adaptive semantic interaction."},"return_to":"l1-pN12-core-module"}
```

The prompt must be compiled from the exact interaction spec, target evidence, visual constraints, and current scene direction. It must describe one isolated asset and must not contain raw SVG, selectors, implementation tokens, or unresolved placeholders. Bind the returned `fileId` to the named `interaction_id`, `candidate_id`, and `variant_id`; on re-entry, build the complete preview operation and open semantic variant review before any Apply decision.

Every generated SVG raster element requires `background: transparent` and `require_transparent_background: true`. A result without actual transparent pixels is invalid and must not be bound or patched into the SVG.

## SVG Document Manager

Use `manage_svg_document` only through an `instruction_ready` handoff naming the registered executor:

- Use `action: import` for a safe uploaded SVG not yet carrying canonical manager state. Supply exact `file_id` and optional `scene_kind_hint`.
- Use `action: adopt_generated` after an SVG generator returns a candidate intended to become the artifact. Supply exact generated `file_id`; do not pass raw generated markup.
- Use `action: inspect` whenever scene/revision/capabilities are absent or stale.
- Use exactly one matching `apply_svg_presentation`, `apply_svg_layout`, or `apply_svg_structure` tool only after the current interaction returns Apply with complete typed operations. Supply exact `file_id`, current `base_revision`, interaction binding, and returned operations unchanged.
- Use `action: validate` for a generated candidate that must be checked without persistence.

Layer 2 must filter candidates against each object's returned `capabilities`; unsupported properties remain locked instead of rejecting the whole SVG. For semantic materialization, name exactly one supported image or SVG executor. Any generated SVG result returns through Layer 1 and then requires `adopt_generated`; a raster variant remains a candidate asset referenced by a typed patch. Every executor result returns to Layer 1.

## Must Not

- Do not populate, review, or export `Aug`.
- Do not mutate without a current ready approved plan or replay a host-committed patch.
- Do not solve more than one material gap per pass.
- Do not reuse analysis, candidates, assets, or decisions after revision changes.
- Do not copy concrete registry metadata into the handoff or prescribe a renderer.

## Execution Skill Routing

For `instruction_ready`, finish the existing `execution_instruction` and load `exec-pN12-artifact-refinement`. Keep `executor.kind`, tool name when selected, parameters, purpose and Apply/result bindings unchanged. L2 plans; the execution skill performs one planned task and returns to L1. Do not invoke task tools or realize model work in the planner before this handoff, or route execution through L3/L4. Gap selection still routes to the selected L3 designer. Failures return directly to L1.

## Next

Eligible gap → selected L3 semantic design → L4 render → L1. Ready execution → direct registered executor/main_model → L1, without L3/L4. Only L1 (`l1-pN12-core-module`) merges canonical state, owns Completion and emits `decision: end`; every dismissal, failure and result re-enters that L1. A rendered preview, Apply return or successful patch is not workflow completion; L1 must first merge and assess the current validated revision, outstanding work and acceptance evidence.