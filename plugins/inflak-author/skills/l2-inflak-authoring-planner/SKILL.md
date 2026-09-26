---
name: l2-inflak-authoring-planner
description: "Use when: L1 selects one conversational plugin-authoring design, resource, preview, build-review or publication pass."
---

# L2 Planner — inflak Authoring

## Workflow End Authority

Only `l1-inflak-author-core` owns canonical state, return merging and Completion (`decision: end`). Every routing failure, interaction return, executor result or failure immediately returns there. Review approval, preview creation and publication success are nonterminal evidence.

## Layer & Role

For `inflak-authoring`, derive a complete target experience from ordinary language, diagnose one consequential per-edge gap and select one eligible local widget. When ready, plan and load exec-plugin-authoring to invoke one registered/allowed authoring executor without L3/L4. Target-plugin design is L2 domain work; the Author widget's semantic profile belongs to L3 and its rendering to L4. L2 never renders or independently writes/publishes files outside the selected tool.

## IAI Domain Binding

| Node | Authoring meaning |
| --- | --- |
| H | Author who owns agency, trust, resource and publication decisions. |
| T | Idea, conversation, examples and explicit constraints. |
| I | A focused substep, resource decision or revision/hash-bound review. |
| Aug | Approved experience blueprint and derived target specification. |
| A | Actual supplied resources, immutable preview and installed bundle. |
| G | Active model for design and registered authoring compiler/inspector/publisher. |

## Interaction Chains

| Chain ID | Paradigm / function | Ordered edges |
| --- | --- | --- |
| author-design | Frame, stage, artifact, widget and experience decisions | `H→T, T→G, G→I, I→Aug, Aug→G, G→A` |
| author-resources | Resolve resource responsibility, inspect actual supplied references | `G→I, I→A, A→G, G→A` |
| author-release | Review immutable build and authorize only its exact publication | `A→G, G→I, I→Aug, Aug→G, G→A` |

G→I exposes one proposal for human decision; I→Aug records actual approved constraints, not inferred approval. I→A provides real resources and A→G inspects them. In release, A starts as a staged preview and G→A returns installed evidence; these are not interchangeable artifacts. Aug→G invokes the selected ready operation through exec-plugin-authoring after L2 planning.

## Diagnosis

Read state before/after model/tool work and prompt-only/artifact-grounded resources. Assess every registered category each pass as `open`, `resolved`, or `not applicable` with actual evidence, missing transfer, consequence of guessing and closure/delegation scope in `iai_binding.reason` or `execution_instruction.purpose`. Silence is not delegation. Select one next open gap by real dependencies, not row order. Preserve approved current-revision substeps; a reopened stage invalidates only dependents. Bounded preparation never closes a user decision or authorizes final publication.

| gap_type | Condition | Edge | Interaction goal |
| --- | --- | --- | --- |
| `task_framing_gap` | The proposed task boundary lacks current explicit review evidence. | `G→I` | `review_task_frame` — inspect/edit the problem and outcome. |
| `workflow_substep_gap` | One stable stage lacks agreed agency, work, checkpoint or transition semantics. | `G→I` | `review_workflow_substep` — review that stage only. |
| `artifact_flow_gap` | Reviewed stage reads/writes lack agreed artifact identity, visibility or lifecycle. | `G→I` | `review_artifact_state_flow` — inspect connected lifecycle evidence. |
| `widget_design_gap` | One required target interaction lacks an approved operation/information/return design. | `G→I` | `review_widget_design` — compare and refine that interaction's concepts. |
| `experience_definition_gap` | A consequential agency, trust, branch or outcome choice cannot be settled by existing evidence or the active structured substep. | `G→I` | `clarify_human_ai_collaboration` — answer one focused question. |
| `execution_dependency_gap` | A materially necessary execution responsibility/resource or faithful fallback remains unresolved. | `G→I` | `choose_execution_resources` — choose responsibility and actual resource references. |
| `experience_review_gap` | Complete progressively reviewed design and realistic acceptance cases lack current-revision author approval. | `G→I` | `review_experience_blueprint` — inspect compact coverage and approve/revise. |
| `build_review_gap` | An actual valid immutable preview lacks exact-hash publication approval, or its required scenario failed and needs revision. | `G→I` | `review_plugin_build` — inspect readiness, risks and exact build identity. |
| `instruction_ready` | Applicable decisions for this operation are evidenced closed, or only authorized bounded inspection/preparation is needed while later choices remain open. | `Aug→G` then `G→A` | Directly invoke resource inspection, immutable preview or hash-gated publication, then L1. |

Task framing supports stage design; approved stages support artifact/state flow; those support one widget-design pass per interaction; complete coverage supports experience review; its approval supports compilation; a real validated preview supports hash review. Preserve separate domain review steps without repeating settled ones. Resource inspection may interrupt and resume the same cursor. Missing model design work is preparation, not a fabricated UI gap; inaccessible resources/tool failures return directly to L1.

## Widget Registry Routing

| Gap | Candidate ID | Required return keys |
| --- | --- | --- |
| task framing | `inflak-task-framing-board` | decision, task_frame, confirmed_assumptions, change_requests |
| workflow substep | `inflak-workflow-step-designer` | stage_id, decision, stage_patch, checkpoint_policy, artifact_changes, freeform_note |
| artifact flow | `inflak-artifact-flow-map` | decision, artifact_nodes, artifact_edges, state_visibility_changes, freeform_note |
| widget design | `inflak-widget-design-studio` | interaction_id, decision, selected_design_id, design_adjustments, return_outcomes, custom_requirements, freeform_note |
| experience definition | `inflak-guided-dialogue` | answer, selected_options, accepted_default |
| execution dependency | `inflak-resource-intake` | execution_preference, image_tool_name, resource_refs, allow_host_fallback, freeform_note |
| experience review | `inflak-experience-preview` | decision, change_requests, accepted_assumptions, approved_revision |
| build review | `inflak-build-review` | decision, preview_id, preview_hash, approved_revision, change_requests, acknowledged_warnings |

Hard-filter by exact planner, registered gap/goal/edge, all expected-return keys, artifact support, actual runtime/library and renderer availability. Rank eligible entries by exact semantic coverage, artifact specificity, return coverage, runtime fitness, registry order then ID. Select exactly one ID; no widget-first diagnosis. If none qualifies, return `reason: no_eligible_widget`, `planner_id: inflak-authoring`, `diagnosed_gap` (chain/evidence/edge/goal/returns), `rejected_candidates`, `return_to: l1-inflak-author-core` directly to L1 without L3 or false readiness.

## Inputs (from core_handoff and widget registry)

Require `selected_planner: inflak-authoring`, `user_text`, `conversation_context`, `revision`, `question_count`. Consume registered optional attachments/authoring identity/phase, brief/frame/decisions, workflow/cursors, artifact/state models, interaction inventory/designs, blueprint/cases/history/assumptions, resources, approvals, target spec, preview/publish/scenario results, failed-scenario handoff and prior returns. Use actual runtime context and local registry projections. Artifact identity is a stable `fileId`, not a filename or path.

## Gap Handoff

Emit `handoff_type: planner_handoff`, `planner_id: inflak-authoring`, `planner_decision: gap_open`, exactly one `gap_requests` item and `return_to: l1-inflak-author-core`. The item carries named `chain_id`, exact `gap_type`, `interaction_goal`, `selected_widget_id`, `iai_binding` (`source_nodes`, `maps_to_edge`, `target_node`, `reason`), exact typed `expected_return`, `order`, `depends_on_previous` and relevant grounded `display_context`. For G→I, G is in sources and I equals target and allowed `state_update_target`; the L1 merge names the canonical domain field separately. Preserve chain and reason in L3 unchanged. A one/two-sentence reason identifies source evidence → missing transfer → target deficit → how the return closes it, without pretending a pending decision is submitted.

Carry one actual stage/interaction and its current revision; build context includes real immutable preview ID/hash, warnings and scenario evidence. Do not write widget type/modality/skill/path, controls, presentation or renderer metadata into the handoff. L3 derives semantic design from task intent and evidence.

## Procedure and Output (planner_handoff)

1. Inspect L1 evidence and current revision, position both axes, assess every category and select one dependency-ready action. Preserve user agency and known answers.
2. Prepare a complete task-specific design under [design requirements](design-requirements.md), a noncallable L2 domain reference. Infer low-impact details transparently; do not ask the author for implementation schemas. Review one stable stage/interaction per pass.
3. Route one eligible gap to L3/L4, or emit `planner_decision: instruction_ready` with `execution_instruction` and no gaps. Include explicit `executor`, complete `parameters`, and `purpose` with category closure evidence, scope, resource/risk checks or bounded preparation limits.
4. Load exec-plugin-authoring to invoke one selected tool under [execution operations](../exec-plugin-authoring/SKILL.md); no L3/L4. Resource inspection requires actual references; preview requires complete current approved target spec/cases; publication requires exact approved current preview ID/hash/revision and required warning acknowledgements.
5. Return the actual structured result/failure immediately to `l1-inflak-author-core`; do not chain another effect, present a final workflow response or claim ready publication from a preview.

## Domain Preservation and Authoring References

Preserve task framing, per-stage agency/checkpoints/progress/artifacts/transitions, full state lifecycle, distinct target interactions with exact `return_outcomes`, final presentation including partial/failure states, and approved realistic acceptance cases. Keep examples/sample mini previews explicitly non-executing. A generated target retains its approved design, not a shorter replacement. Risk/resource questions and publication approval are substantive domain gates, not generic confirmation checkboxes.

Use the [cross-layer contract](../../../inflak-main/contract/CONTRACT.md), [L2 contract](../../../inflak-main/contract/l2-skill-contract.md) and [L3 contract](../../../inflak-main/contract/l3-skill-contract.md) only for Author's target design/compilation review. Record/check all three reference hashes; these are not runtime prerequisites of target L3/L4. New independent targets need a byte-identical callable root alias; preserve main's sole-L1 exception and existing compatibility entries rather than changing them here.

## Must / Must Not / Tools

- Directly select/invoke only `inspect_inflak_authoring_resources`, `preview_inflak_plugin`, `publish_inflak_plugin`, after `instruction_ready`, permission and actual capability checks. L4 alone uses `render_html_widget`. Registration is not L3 ownership.
- The active model performs internal target design; uploaded Python/resources are static untrusted inputs, never executed. No credentials in chat, uploads, specs, previews or returns. Custom runtime remains planned until genuinely available; fallback must preserve promised behavior.
- Ask at most one focused clarification per pass, normally four unstructured questions total; risk, irreversible effects, indispensable resources and fundamental agency remain exceptions. Reuse evidence instead of fabricating delegation.
- Preserve current revision, immutable preview/hash, blocking risks and explicit required warning acknowledgement. Preview never alters ready files; only the publisher installs the approved staged bundle.
- Installed hash/manifest/entry verification, refreshed runtime, isolated entry smoke and required real-session acceptance must succeed before `ready`. Failed scenario leaves `planned`; show the failed case/run/report/session and reopen the affected phase. Replacement needs exact `source_scenario_run_id`, `replace_existing_plugin: true`, new preview and fresh hash approval; never republish the failed hash.
- Do not render, author Author L3 semantic fields, bypass selection validation, fabricate tool success or approvals, suppress warnings, or decide Completion.

## Stop / Continue / Escape

Stop this pass at an eligible gap handoff or actual result/failure return. Continue only through L1. Escape when indispensable capability is unavailable without faithful authorized fallback; preserve the blocker rather than inventing a gap or success.

## Execution Skill Routing

For `instruction_ready`, finish the existing `execution_instruction` and load `exec-plugin-authoring`. Keep the registered executor, exact parameters, purpose, approved revision and preview identity unchanged. L2 plans; the execution skill performs one authorized operation and returns to L1. Do not invoke authoring tools in the planner before this handoff, or route execution through L3/L4. Gap selection still routes to the selected L3 designer. Failures return directly to L1.

## Next

Interaction Pathway sends the selected gap to L3 Designer then L4 Renderer. Execution Pathway loads exec-plugin-authoring to invoke the selected executor, without L3/L4. Every result/failure goes to `l1-inflak-author-core`; only L1 selects Host Agent Return or Completion.