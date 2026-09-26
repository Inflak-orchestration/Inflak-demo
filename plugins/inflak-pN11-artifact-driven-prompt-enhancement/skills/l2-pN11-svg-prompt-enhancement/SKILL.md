---
name: l2-pN11-svg-prompt-enhancement
description: "Use when: L1 routes prompt/SVG grounding, target-bound action approval or ready enhancement execution."
---

# L2 Planner — P11

## Workflow End Authority

Only L1 (`l1-pN11-core-module`) owns canonical merging, Completion and `decision: end`. All results and failures return there before another action. An approved action or successful patch is not workflow completion; L1 assesses remaining work and the actual validated result.

## Layer & Role

Diagnose one next material gap, select its exact eligible widget, or emit `instruction_ready` and load exec-pN11-prompt-refinement to invoke selected registered executor or active `main_model`. No L3/L4 on Execution Pathway. L3 designs UI semantics; L2 never renders, mutates outside a ready approved plan, or independently concludes.

## Inputs

Read `core_handoff.state_snapshot` with `selected_planner: pN11-svg-prompt-enhancement`; require exact `source_prompt` and `source_artifact_ref`. Consume declared scene/analysis, units/bindings/resolutions/refinements, active object, Aug, review/candidate/execution state and prior returns. Read registries, actual capabilities and [execution skill](../exec-pN11-prompt-refinement/SKILL.md).

## IAI Domain Binding

| Node | Meaning |
| --- | --- |
| H | Prompt author retaining target/action approval |
| T | Exact original prompt with stable source-span units |
| I | User-confirmed bindings, references and target-bound action refinements |
| Aug | Enhanced prompt with structured grounding and complete history |
| A | Exact source SVG/capabilities and actual revised artifact |
| G | Grounded model interpretation/compilation and registered executors |

## Interaction Chains

| Chain ID | Function | Ordered edges |
| --- | --- | --- |
| prompt-grounding | Bind named concepts and references | `H→T, T→G, A→G, G→I` |
| prompt-action | Concretize and approve target-bound action | `G→I, I→Aug, T→Aug` |
| prompt-execution | Validate and realize approved enhancement | `T→Aug, Aug→G, G→A` |

## Diagnosis

Locate before/after generation and artifact-grounded resources. Classify every registered gap `resolved`, `open`, or `not applicable` with source evidence, missing transfer, permission and consequences in reason/purpose. Silence is not delegation. Dependency order resolves named concepts, references, then concrete action approval; preserve settled evidence instead of repeated questions. Every executable action retains P11's genuine target-bound approval requirement, not a generic checkbox. Grounding/compilation/validation are bounded model/tool work, failures return to L1, not invented gaps.

| gap_type | Condition | Edge | Interaction goal |
| --- | --- | --- | --- |
| `prompt_artifact_alignment_gap` | A named concept has multiple plausible or no supported scene counterparts. | `G→I` | `align_prompt_concepts_to_objects` |
| `prompt_missing_target_gap` | Pronoun/demonstrative/generic phrase or omitted subject lacks explicit referent. | `G→I` | `resolve_prompt_target` |
| `prompt_action_specificity_gap` | Target-bound operation/typed values are incomplete or lack their required explicit action approval. | `I→Aug` | `specify_prompt_action` |
| `instruction_ready` | All material units/actions are resolved and approved for final work, or bounded grounding/candidate/validation preparation meets its own scope and permission. | `Aug→G` then `G→A` | Direct main-model synthesis or registered inspect/generate/apply/validate; return to L1. |

## Widget Registry Routing

Filter exact planner/gap/goal/edge, all expected returns under declared policy, artifact type, capabilities/libraries and renderer availability. Rank semantic coverage, artifact specificity, return coverage, runtime fitness, stable order then ID. No match returns `reason: no_eligible_widget`, `planner_id`, `diagnosed_gap` with chain/evidence/edge/goal/returns, nonempty `rejected_candidates` records containing candidate IDs and failed checks, and `return_to: l1-pN11-core-module`; no L3 or false readiness.

## Prompt and Authorization Protocol

- Preserve `original_prompt` exactly; units retain `prompt_unit_id`, `source_span` (`start`,`end`,`text`), `kind: named_concept|ambiguous_reference|action`, candidate IDs, confidence evidence, status and provenance. Keep IDs while source span/meaning survives.
- Unique clearly evidenced named concepts may close from artifact facts. References never resolve by proximity. In “make it stand out”, `it` is reference, `stand out` action; predicates never route to the target resolver.
- Actions require stable target, allowlisted operation, complete typed parameters and object-valued constraints. Vocabulary: move/resize/rotate/reorder/align/edit_text/add/remove/replace/restyle/increase_prominence/change_palette. Prefill a proposal within evidence, but never mark it approved.
- Every executable action, even an unambiguous remove/replace, needs one actual target-bound approval of its concrete instruction. Closure requires `selected_by_user` provenance and history matching unit/targets/operation/parameters/constraints, `interaction: action_specificity`, `selected_by: user`. Viewing, editing, model inference or aggregate review does not satisfy it.
- After all action approvals, compile canonical enhancement and mark confirmed; no aggregate prompt-review widget. Canonical fields: `schema_version`, `source_artifact`, `original_prompt`, `prompt_units`, `object_bindings`, `reference_resolutions`, `action_refinements`, `enhanced_prompt`, `interaction_history`, `field_provenance`, `validation`, `status`.
- The Host Agent validates `source_artifact.fileId`, positive integer revision, artifact type, exact source spans and current object membership; unit status `resolved|not_present|skipped`; object-valued parameters/constraints; every history item refers to a valid unit and every executable refinement matches its user-selected approval; `validation.unresolved_prompt_unit_ids: []` only on actual closure. Provenance: `from_original_prompt`, `confirmed_from_artifact`, `suggested_by_genai`, `selected_by_user`, `missing_or_uncertain`.
- Apply supported homogeneous families directly through shared Host tools using actual schema, real alpha candidates only where semantic content requires them. No export file or exported hash is required. Preserve exact approved refinements and interaction bindings; never replay executed refinement IDs. The execution skill preserves exact tool validation. Return each result through L1 before another family and validate actual final revision. No final revision-acceptance widget in P11.

## Handoffs and Procedure

Both pathways emit `handoff_type: planner_handoff`, `planner_id: pN11-svg-prompt-enhancement`, `planner_decision`, and `return_to: l1-pN11-core-module`.

For `planner_decision: gap_open`, emit exactly one `gap_requests` record with `chain_id`, `gap_type`, `interaction_goal`, `selected_widget_id`, integer `order: 1`, boolean `depends_on_previous`, grounded `display_context`, typed `expected_return`, and `iai_binding: {source_nodes, maps_to_edge, target_node, reason}`. Choose `prompt-grounding` for alignment/reference and `prompt-action` for action specificity. The atomic `maps_to_edge` must occur in that named chain and match the diagnosis and selected registry entry; its origin is in nonempty `source_nodes`, its destination equals `target_node` and allowed `state_update_target`. Keep a nonempty evidence-backed `reason`, deterministic `merge_strategy` by unit/source hash/revision, and `next_planner_action: re-enter Layer 1`. No L3 names/types/renderer metadata.

All P11 widgets use `return_mode: agent_interpreted`, not a fixed registry schema. `expected_return` and the L3 submission mapping describe the current interaction's producible JSON values and preserve their types. L1 interprets actual returns against the source-bound interaction before canonical merging; the following shapes are domain guidance, not mandatory transport keys. Alternative serialization never waives explicit target-bound approval or complete canonical action parameters/constraints.

| Selected widget | Typical semantic return values and types |
| --- | --- |
| prompt-object-alignment | `prompt_unit_id: string`, `object_ids: string[]`, `resolution: string enum confirmed/not_present/skip`, `action: string enum continue/dismiss` |
| prompt-target-resolver | `prompt_unit_id: string`, `resolved_object_ids: string[]`, `replacement_label: string`, `action: string enum continue/dismiss` |
| prompt-action-specificity-editor | `prompt_unit_id: string`, `target_object_ids: string[]`, `operation: string`, `parameters: object`, `constraints: object`, `action: string enum approve/edit/dismiss` |

IDs come from the current source-bound unit and stable scene objects; values come from the declared controls, never inferred targets. Preserve empty/unresolved values on edit/dismiss without treating them as closure. Only `approve` closes action permission; L1 merges by unit, source hash and revision.

For `planner_decision: instruction_ready`, omit `gap_requests` and widget identity. Require `execution_instruction` with `executor` (`kind: tool` plus registered/allowed `name`, or `kind: main_model`), object `parameters`, nonempty evidence-backed `purpose` and existing result/interaction bindings. Bind execution to the named applicable chain and exact current source/revision and approvals; do not invent tool API parameters. exec-pN11-prompt-refinement executes the L2 plan and invokes it and immediately returns actual result/failure to L1. Bounded preparation is not permission for final mutation.

## Must / Must Not

No unconfirmed/stale execution, fabricated targets/values/results, generic approval checkbox, duplicate aggregate confirmation, render calls or final response. Read references as documentation, not skills. Reopen only affected actual gaps when evidence changes.

## Execution Skill Routing

For `instruction_ready`, finish the existing `execution_instruction` and load `exec-pN11-prompt-refinement`. Keep `executor.kind`, tool name when selected, parameters, purpose and target-bound approval/result bindings unchanged. L2 plans; the execution skill performs one planned task and returns to L1. Do not invoke task tools or realize model work in the planner before this handoff, or route execution through L3/L4. Gap selection still routes to the selected L3 designer. Failures return directly to L1.

## Next

Gap → L3 design → L4 → L1. Ready plan → exec-pN11-prompt-refinement → L1. All failures → `l1-pN11-core-module`; execution skill: exec-pN11-prompt-refinement.