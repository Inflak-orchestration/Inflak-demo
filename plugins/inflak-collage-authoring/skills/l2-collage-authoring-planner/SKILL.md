---
name: l2-collage-authoring-planner
description: "Use when: Layer 1 has routed one create, analyze, ground_prompt, or refine Collage authoring state."
---

# Layer 2 - Unified Collage Authoring Planner

## Layer & Role

Assess all registered categories as resolved, open, or not applicable from source evidence and scoped delegation, recording findings in `iai_binding.reason` or `execution_instruction.purpose`. Silence is not delegation. Choose one next material gap by dependencies or emit `instruction_ready` and load exec-collage-authoring to invoke one registered executor or active `main_model`. Never render or author the semantic widget contract. Execution Pathway bypasses L3/L4; all actual results/failures return to `l1-collage-authoring-core`, which alone merges canonical state and emits `decision: end`.

## Widget Routing

For a widget-path gap, query the plugin-local `registry/widgets.json` after diagnosis. Filter entries by `compatible_planners`, `gap_categories`, `interaction_goals`, `iai_edges`, expected-return coverage, and required artifact, runtime, and renderer availability. Select one eligible widget registry entry and write only its `id` to `gap_requests[0].selected_widget_id`; do not copy registry-derived concrete metadata into the handoff. Layer 3 validates and realizes the selected entry; it does not select or replace it. This layer does not author the semantic widget contract or render UI.

## Inputs

Read the selected `core_handoff.state_snapshot`. Require `entry_mode` and `source_intent`; optionally read `asset_plan`, `artifact`, `analysis`, `proposals`, `interaction_specs`, `active_interaction_id`, `preview_state`, `interaction_returns`, `decisions`, `augmented_intent`, `candidate_assets`, `authoring_bundle`, `pending_operations`, `execution`, `acceptance`, and `prior_returns`. Use the newest canonical artifact revision and return for the active mode.

## IAI Binding

| Node | Binding |
| --- | --- |
| `H` | User who supplies intent and confirms proposals or revisions. |
| `T` | Exact creation prompt, existing prompt, analysis intent, or refinement goal. |
| `I` | Mode choice, object/relation/action decisions, candidate choices, overrides, and acceptance. |
| `Aug` | Optional confirmed creation brief, artifact-first plan, or grounded prompt. |
| `A` | Canonical SVG revision, transparent assets, authoring bundle, and scene. |
| `G` | Model analysis, proposal generation, semantic compilation, candidate preparation, and validation interpretation. |

## Mode Profiles

- `create`: complete intent, prepare primary transparent assets and bounded authoring options, compose, then direct authoring.
- `analyze`: inspect, generate 3-6 artifact-first proposals, formally decide every proposal, compile optional Aug, execute.
- `ground_prompt`: inspect, preserve exact prompt units, resolve references/actions, compile optional Aug, execute.
- `refine`: inspect, synthesize one prompt-specific artifact-grounded interaction with a reversible default preview, collect Apply/Adjust/Regenerate/Correct/Reject, and commit only Apply without mandatory Aug.

## Interaction Chains

| Chain ID | Function | Ordered edges |
| --- | --- | --- |
| collage-mode | Resolve materially ambiguous entry | `H→I` |
| collage-create | Complete evidenced intent and prepare real composition | `H→T, I→Aug, Aug→G, G→A` |
| collage-analyze | Ground and decide artifact-first proposals | `A→G, G→I, I→Aug, Aug→G, G→A` |
| svg-ground-prompt | Preserve prompt and bind actionable units | `H→T, T→G, A→G, G→I, I→Aug, Aug→G, G→A` |
| svg-augmentation | Compile confirmed prompt and artifact context without inventing decisions | `T→Aug, A→Aug, Aug→G, G→A` |
| collage-refine | Prepare reversible artifact-grounded interaction and commit Apply | `T→G, A→G, G→I, I→A` |
| svg-review | Compare and accept actual revised artifact | `G→A, I→A` |

## Diagnosis

Inspect before/after-generation timing and available prompt/artifact evidence. Inspection, analysis, plan synthesis, preview preparation, candidate generation, compilation and validation are bounded executor work, not invented user gaps. Such work requires its own complete inputs/permission and cannot authorize final execution while relevant choices remain open. Unsupported services and exhausted retries are nonterminal failures to L1.

| gap_type | Condition | Edge | Interaction goal |
| --- | --- | --- | --- |
| `entry_mode_gap` | Input supports multiple modes and none is explicit. | `H→I` | choose_collage_authoring_mode |
| `creation_intent_gap` | A material theme, copy, canvas or explicit constraint is neither evidenced nor delegated; a subject alone does not resolve all fields. | `I→Aug` | complete_creation_intent |
| `interaction_execution_gap` | The active refine interaction has no complete Apply/Adjust/Regenerate/Correct/Reject return. | `G→I` | run_adaptive_svg_interaction |
| `proposal_target_gap` | A proposal/prompt unit lacks a confirmed stable target. | `G→I` | resolve_svg_targets |
| `proposal_relation_gap` | A multi-object proposal lacks endpoints/constraints. | `I→Aug` | define_svg_relations |
| `proposal_operation_gap` | A proposal lacks a supported semantic operation or typed values. | `I→Aug` | define_svg_operation |
| `proposal_decision_gap` | Complete proposals lack required decisions. | `G→I` | review_svg_proposals |
| `augmented_intent_review_gap` | A complete combined plan still contains a genuine unapproved material choice; do not repeat accepted/edited authorization. | `I→Aug` | review_augmented_svg_intent |
| `candidate_selection_gap` | Multiple prepared assets require selection. | `G→I` | select_svg_candidate |
| `artifact_comparison_gap` | A required comparison of actual source/current revisions is missing. | `I→A` | compare_svg_revisions |
| `artifact_acceptance_gap` | Latest validated revision is not accepted. | `I→A` | review_svg_revision |
| `instruction_ready` | Relevant choices are closed for final work, or a bounded prerequisite has independent evidence and permission. | `Aug→G`, `G→A`, `A→G`, or `I→A` as applicable | Direct registered executor/main_model, then L1. |

## Proposal Schema

Every proposal contains `proposal_id`, `origin`, exact source span when applicable, `target_hypotheses`, selected stable ids, evidence, confidence, semantic operation, compiled operations, candidate bindings, status, and field provenance. `analyze` requires explicit accepted/edited/rejected status for every proposal. `refine` presents a default recommendation and ranked alternatives before free selection. `ground_prompt` keeps named concept, ambiguous reference, and action units separate. `create` stores generated opportunities in `authoring_bundle`.

## Refine Interaction Model

For `refine`, generate exactly one active interaction for the first unresolved user goal instead of opening the proposal-review sequence. Every `interaction_spec` contains `interaction_id`, exact `prompt_span`, `interaction_goal`, registry `archetype`, ranked `target_hypotheses`, `default_target_ids`, artifact evidence, confidence, capability-compatible controls, reversible `preview_operations`, declared return schema, annotation, and field provenance. The default state is a visible host-owned preview on the artifact, not an empty form. `Adjust` changes only that preview, `Regenerate` returns to synthesis, and only `Apply` copies complete allowlisted typed operations into `pending_operations`.

Choose the narrowest eligible registry archetype. Color, palette, warmth, saturation, contrast, fill, stroke, or text-color intent must use `collage-object-color-palette`. Overall composition, multiple placements, spatial regions, alignment relationships, or "what belongs where" must use `collage-layout-board`. A single grounded transform/text/order change may use `collage-operation-control`; semantic add or replacement uses `collage-candidate-selector` after materialization. Do not reduce color intent to raw text fields or multi-object layout to independent numeric fields.

Preview state is transient host UI keyed by `interaction_id` and bound to the exact artifact revision. Never accept preview SVG/XML, CSS, selectors, scripts, paths, URLs, or data URIs. On Apply, require the exact current `base_revision`, stable object ids, and a homogeneous operation family before execution.

## Post-Decision Execution

When all proposal decisions exist, proposal review is closed but the workflow is not complete:

1. Exclude rejected proposals from executable work and preserve them only in decision history.
2. Treat accepted semantics and user-edited semantics as confirmed only within the displayed scope. An explicit execution-authorizing submission can release a temporary review-stage "not yet" restriction; an unrelated Continue/Accept never overrides a standing prohibition.
3. Accepted/edited semantics plus an explicitly execution-authorizing `continue|accept` authorize only displayed downstream work. Open `augmented_intent_review_gap` for genuinely missing combined-plan authorization, never duplicate authorization or mandatory Aug in refine.
4. Resolve missing typed values, candidates, or operation compilation one gap per pass.
5. Emit `instruction_ready` for exactly one homogeneous operation family at the current revision. After its tool result re-enters Layer 1, execute remaining families against the new revision.
6. After no executable operations remain, plan validation through the execution skill in a ready pass; then assess comparison and concrete artifact acceptance, reusing valid acceptance evidence.

Proposal decisions update `decisions`; they never update `acceptance`. Do not emit a completion summary merely because every proposal has a decision.

## Semantic Compilation

Allowed semantic operations are `move`, `resize`, `rotate`, `reorder`, `align`, `edit_text`, `add`, `remove`, `replace`, `restyle`, `increase_prominence`, and `change_palette`. Compile only complete confirmed values:

- layout to `set_transform`, `set_order`, or `set_dom_order`;
- text/style to `set_object_style`, `set_attributes`, `set_text`, or `update_text`;
- structure to `add_cutout`, `remove_object`, `remove_element`, `replace_cutout_asset`, or `replace_asset`.

Never send semantic names to patch tools. If compilation requires inventing a target, text, color, relation, transform, or asset id, reopen the matching gap.

## External Calls

Read `registry/authoring-capabilities.json` and [execution skill](../exec-collage-authoring/SKILL.md) before ready work. Preserve real parameters, dependencies and result bindings. exec-collage-authoring executes the L2 plan and invokes one approved registered tool or main_model per pass and returns its result/failure to `l1-collage-authoring-core`. Host-committed `patch_result` must never be replayed. Export policy is `optional|required|disabled`; only required policy or an explicit export request creates a dependency, and disabled policy blocks export.

- Normalize/import/adopt/validate: `manage_svg_document`.
- Widget grounding: `inspect_svg_scene`.
- Initial collage: follow the P8 asset queue. Plan 3-6 independently editable visual objects, prepare at least two alpha-validated primary cutouts one per pass, prepare 1-3 distinct replacements for every successful primary, then call `compose_svg_collage` with `creation_mode: image_collage`, stable ids, and a complete `authoring_bundle`.
- Asset preparation: use only a capability-declared image tool; require transparent output for SVG raster elements.
- Patch: partition operations by family and call one of `apply_svg_presentation`, `apply_svg_layout`, or `apply_svg_structure` against current `base_revision`.
- Export: no instruction-file exporter is registered. Required policy or an explicit file-export request returns a capability failure to L1; do not invent a tool or file. Optional export does not block direct Host execution and validation of confirmed Aug.

For each create-mode primary or alternate, count matching preparation attempts in `prior_returns`. Permit at most two transparent-asset attempts. After a timeout, provider error, or second transparency validation failure, mark only that plan item unavailable; never retry with an opaque or white background. Continue the remaining asset queue. Composition remains blocked until at least two primary cutouts succeed and every successful primary has 1-3 distinct candidates. If fewer than two primaries can succeed, return an `asset_generation_blocked` failure directly to L1, not a gap or readiness; no vector/text-only substitute.

A complete create-mode `authoring_bundle` is an interactive editing contract, not prose. It must contain 2-4 `visual_style_presets` with swatches and typed operations; `text_authoring_options` with copy and typography presets for every authored text object; 1-3 `asset_candidates_by_object` entries for every successful primary cutout; and `addable_elements` for successful unplaced cutouts. Every candidate must have a real current-session `fileId`, differ from its primary, and retain source tool, alpha provenance, target object id, label, and rationale. Do not compose or route to artifact acceptance until this bundle is embedded in the canonical scene and the host can expose object-bound candidate thumbnails.

## Handoffs

Both pathways require `handoff_type: planner_handoff`, `planner_id: collage-authoring`, `planner_decision`, and `return_to: l1-collage-authoring-core`. For `gap_open`, emit exactly one `gap_requests` record with named `chain_id`, `gap_type`, `interaction_goal`, `selected_widget_id`, integer `order: 1`, boolean `depends_on_previous`, grounded `display_context`, exact typed `expected_return`, and `iai_binding: {source_nodes, maps_to_edge, target_node, reason}`. The atomic edge must occur in that named chain and match the diagnosis/registry; nonempty `source_nodes` includes the edge origin, and `target_node` equals its destination and allowed `state_update_target`. Preserve nonempty evidence-backed `reason`, deterministic `merge_strategy` by source hash/stable IDs/revision, and `next_planner_action: re-enter Layer 1`.

Use `collage-mode` for mode choice, `collage-create` for creation intent, `collage-refine` for adaptive interaction, `collage-analyze` or `svg-ground-prompt` for their grounded proposal decisions, and `svg-review` for comparison/acceptance. Other decisions use an applicable declared chain containing the exact diagnosis edge, never a chain selected merely because it contains similar nodes. Rank eligible widgets by semantic coverage, artifact specificity, returns, runtime, registry order and ID. No match returns `reason: no_eligible_widget`, `planner_id`, `diagnosed_gap` with chain/evidence/edge/goal/returns, nonempty `rejected_candidates` records with candidate IDs and failed checks, and `return_to: l1-collage-authoring-core`, bypassing L3. No invented source SVG in create/mode choice.

The following existing local return schemas ground registry coverage. Preserve `planner_declared` policy: L2 selects the exact typed shape for the active goal; the catalog is not permission to append unrelated fields. Fixed comparison returns only `action`.

| Selected widget | Return keys and types |
| --- | --- |
| collage-mode-choice | `entry_mode: string enum create/analyze/ground_prompt/refine`, `source_intent: object`, `action: string enum continue/dismiss` |
| collage-object-grounding | `proposal_id: string`, `target_object_ids: string[]`, `relations: object[]`, `constraints: object[]`, `resolution: string enum confirmed/not_present/skip`, `action: string enum continue/dismiss` |
| collage-proposal-review | `decisions: object[]`, `action: string enum continue/regenerate/dismiss` |
| collage-operation-control | `proposal_id: string`, `semantic_operation: object`, `artifact_id: string`, `base_revision: positive integer`, `operations: object[]`, `action: string enum continue/apply/dismiss` |
| collage-object-color-palette | `interaction_id: string`, `action: string enum apply/reset/regenerate/reject/dismiss`, `target_object_ids: string[]`, `base_revision: positive integer`, `operations: object[]`, `control_values: object` |
| collage-layout-board | `interaction_id: string`, `action: string enum apply/reset/regenerate/reject/dismiss`, `base_revision: positive integer`, `changed_object_ids: string[]`, `layout_regions: object[]`; the existing host also binds `artifact_id: string` and authoritative `operations: object[]` for Apply, never iframe-reconstructed geometry |
| collage-candidate-selector | `proposal_id: string`, `candidate_id: string`, `asset_file_id: string`, `artifact_id: string`, `base_revision: positive integer`, `operations: object[]`, `action: string enum select/reject/dismiss`; refine uses its actual declared Apply interaction schema and permission |
| collage-plan-review | `augmented_intent: object`, `review_state: object` with `status: string enum confirmed/edit/start_over`, `action: string enum confirm/edit_targets/edit_operations/start_over/dismiss` |
| collage-artifact-review | `revision: positive integer`, `decision: string enum accepted/continue/revise`, `selected_issue_id: string`, `followup_intent: string`, `action: string enum continue/dismiss` |
| collage-revision-comparison | `action: string enum accept_revision/continue_editing` |

L3 maps unchanged proposal/source/interaction/revision IDs from actual bound display context, semantic values from declared controls, and action/decision from explicit commands. Serialize JSON types without stringifying objects or arrays; preserve declared optional/empty fields, rather than fabricate values or metadata controls. The selected runtime schema must remain within actual widget capabilities. Preview, selection, or dismissal alone never authorizes a patch or final completion.

Open gap example:

```json
{"handoff_type":"planner_handoff","planner_id":"collage-authoring","planner_decision":"gap_open","gap_requests":[{"chain_id":"collage-analyze","gap_type":"proposal_target_gap","selected_widget_id":"collage-object-grounding","interaction_goal":"resolve_svg_targets","iai_binding":{"source_nodes":["G"],"maps_to_edge":"G→I","target_node":"I","reason":"A grounded proposal needs a stable target decision."},"display_context":{"artifact_ref":{"fileId":"","revision":1},"proposal":{},"objects":[]},"expected_return":{"proposal_id":"","target_object_ids":[],"resolution":"confirmed|not_present|skip","action":"continue|dismiss"},"order":1,"depends_on_previous":false}],"return_to":"l1-collage-authoring-core"}
```

For `planner_decision: instruction_ready`, omit `gap_requests` and widget identity. Require `execution_instruction` with `executor` (`kind: tool` plus registered/allowed `name`, or `kind: main_model`), object `parameters`, nonempty evidence-backed `purpose`, and the existing result/interaction bindings; retain top-level `return_to`. Bind work to its applicable named chain, exact current source/revision and actual scoped authorization without inventing tool API fields. exec-collage-authoring executes the L2 plan and invokes that executor and returns the actual result/failure to L1; bounded preparation cannot authorize final mutation while relevant choices remain open.

## Execution Skill Routing

For `instruction_ready`, finish the existing `execution_instruction` and load `exec-collage-authoring`. Keep `executor.kind`, tool name when selected, parameters, purpose and authorization/result bindings unchanged. L2 plans; the execution skill performs one planned task and returns to L1. Do not invoke task tools or realize model work in the planner before this handoff, or route execution through L3/L4. Gap selection still routes to the selected L3 designer. Failures return directly to L1.

## Next

- `gap_open`: selected L3 design → L4 render → L1.
- `instruction_ready`: direct registered executor/main_model → L1; never L3/L4.
- All results, failures, cancellations and dismissals re-enter `l1-collage-authoring-core`; only L1 merges state and ends.

Asset example:

```json
{"handoff_type":"planner_handoff","planner_id":"collage-authoring","planner_decision":"instruction_ready","execution_instruction":{"executor":{"kind":"tool","name":"generate_image"},"parameters":{"prompt":"One isolated full [planned object], matching [shared visual direction], clean silhouette, transparent background, no text, no frame","size":"1024x1024","quality":"high","background":"transparent","require_transparent_background":true},"result_binding":{"object_id":"stable-object-id","candidate_id":"primary-or-alternate-id","asset_role":"primary|replacement_candidate","state_target":"candidate_assets"},"purpose":"Materialize exactly one P8-style collage asset before composition."},"return_to":"l1-collage-authoring-core"}
```

When composition becomes ready, pass `creation_mode: image_collage`. Include at least two cutout objects with real primary `asset_file_id` values, plus 1-3 different real candidate `fileId` values under `authoring_bundle.asset_candidates_by_object` for every cutout. The compiler rejects an image-collage scene below this threshold.

After each tool or widget result return to Layer 1. Stop only after validation and artifact acceptance.
An evidenced subject resolves only the subject; assess remaining material fields independently.
