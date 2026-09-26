---
name: l1-inflak-author-core
description: "Use when: entering inflak Author or re-entering after any authoring question, review, resource inspection, preview, validation, or publish result."
---

# Layer 1 - inflak Author Core

## Layer & Role

Read [the root contract](../../SKILL.md) as documentation on entry. This is the existing sole-L1 compatibility entry. Only L1 Router owns canonical state, return merging and Completion with `decision: end`. Reconstruct state on every initial request, L2 routing failure, L3 validation failure, L4 widget/renderer return and executor result/failure before choosing a new pathway. Downstream results are nonterminal evidence, never permission to skip L1.

## Four Pathways

| Pathway | Flow |
| --- | --- |
| Interaction Pathway | user/return → L1 → L2 gap + selection → L3 design → L4 render → L1 |
| Execution Pathway | user/return → L1 → L2 plan → exec-plugin-authoring → execute/realize → L1; exec-plugin-authoring executes the L2 plan and invokes the selected executor without L3/L4. |
| Host Agent Return | user → L1 → host agent; retain `decision: bypass` for an informational answer. |
| Completion | user/return → L1 → Completion; only L1 emits `decision: end`. |

Reconstruct one canonical authoring state and route it to the sole authoring planner. Do not diagnose missing experience decisions, draft the target plugin, choose an interaction, render UI, inspect files, or invoke authoring tools.

## State Reconstruction

Read the newest user text, conversation context, attachment metadata, prior structured returns, and authoring tool results. Maintain:

- `authoring_id`, `revision`, `question_count`, and `user_text`;
- `authoring_phase`: one of `task_framing`, `workflow_design`, `artifact_design`, `widget_design`, `experience_review`, `compile`, `build_review`, or `complete`;
- `intent_brief`, `task_frame`, and `task_frame_decision`;
- `workflow_design`, `workflow_stage_order`, `active_stage_id`, and `workflow_stage_decisions` keyed by stable stage id;
- `artifact_model`, `artifact_model_decision`, and `state_model`;
- `interaction_inventory`, `active_interaction_id`, and `widget_designs` keyed by stable interaction id;
- `experience_blueprint`, `validation_cases`, and `phase_history` recording each accepted or reopened substep;
- `assumptions` with explicit, inferred, confirmed, or conflicted status;
- `execution_resources` using a declared execution preference, an optional registered image-tool name, and stable `fileId` references only;
- `blueprint_approval`, `target_spec`, `preview_result`, `build_approval`, `publish_result`, and `scenario_validation`;
- `failed_scenario_handoff` with plugin id, case id, run id, failed checks, report URL, and session id when a required real-session case fails;
- `prior_returns` in chronological order.

The newest valid explicit author decision is authoritative. Any material change to intent, agency, checkpoints, execution resources, or generated behavior increments `revision` and invalidates an older blueprint approval, preview hash, or build approval. Tool diagnostics never override an explicit user decision. Preserve compatible unchanged stage/interaction approvals with their provenance; do not silently reapprove changed dependents.

Every Author interaction is G→I: G is the source and I is both target and registered `state_update_target`. L1 applies the preserved merge at I to the corresponding canonical field: frame→`task_frame`/decision, stage→`workflow_design`/stage decisions, artifact flow→`artifact_model`/decision, design→`widget_designs`, dialogue→`intent_brief`, resource→`execution_resources`, experience→`blueprint_approval`, build→`build_approval`. These domain fields are not replacement IAI nodes. Preserve exact declared values, stable IDs, revision, chain/reason and actual source lineage; no inference from a pending widget or label becomes approval.

## Routing

Route to `inflak-authoring` whenever the user is creating or revising a plugin, answering an authoring question, supplying a resource, reviewing a blueprint, reviewing a build, or approving publication. Bypass only for a pure informational question that does not create or change an authoring session.

```json
{
  "handoff_type": "core_handoff",
  "decision": "route_to_planner",
  "selected_planner": "inflak-authoring",
  "state_snapshot": {
    "user_text": "Create an automatic research assistant",
    "conversation_context": [],
    "attachment_refs": [],
    "authoring_id": "authoring-session-id",
    "revision": 1,
    "question_count": 0,
    "authoring_phase": "task_framing",
    "intent_brief": {},
    "task_frame": {},
    "task_frame_decision": {},
    "workflow_design": {},
    "workflow_stage_order": [],
    "active_stage_id": "",
    "workflow_stage_decisions": {},
    "artifact_model": {},
    "artifact_model_decision": {},
    "state_model": [],
    "interaction_inventory": [],
    "active_interaction_id": "",
    "widget_designs": {},
    "experience_blueprint": {},
    "validation_cases": [],
    "phase_history": [],
    "assumptions": [],
    "execution_resources": [],
    "blueprint_approval": {},
    "target_spec": {},
    "preview_result": {},
    "build_approval": {},
    "publish_result": {},
    "scenario_validation": {},
    "failed_scenario_handoff": {},
    "prior_returns": []
  }
}
```

```json
{
  "handoff_type": "core_handoff",
  "decision": "bypass",
  "state_snapshot": {
    "user_text": "What is an inflak plugin?"
  }
}
```

## Lifecycle

- After any Author interaction return, merge only declared return fields and re-route from the current revision.
- A task-frame approval advances to `workflow_design`; a change request keeps `task_framing` active.
- A workflow-stage approval is stored under its stable stage id and advances the cursor to the next unresolved stage. A change request reopens only that stage and invalidates artifact/widget designs that depend on it.
- Artifact-flow approval advances to `widget_design`. Any artifact/state change invalidates affected widget designs.
- A widget-design approval is stored under its interaction id and advances to the next unresolved interaction. It must include a complete `return_outcomes` table mapping exact raw `values` matches to canonical state targets, merge rules, workflow effects, next stages, and terminal flags. A requested alternative keeps that interaction active.
- Enter `experience_review` only when the task frame, every workflow stage, artifact/state flow, and every required widget design are confirmed.
- After a resource inspection, preview, publication, or scenario result, record it and re-route; do not summarize as though the workflow were complete.
- A failed required scenario invalidates ready completion. Preserve the failure handoff, reopen the affected design phase, and set `target_spec.replace_existing_plugin: true` plus `target_spec.source_scenario_run_id` before compiling a replacement of that exact `planned` plugin.
- Emit `decision: "end"` and stop only when publication and the required scenario succeeded, the author explicitly cancelled, or canonical state confirms that an indispensable resource cannot be supplied and no faithful host fallback exists.
- Never reuse an approval whose revision or preview hash differs from the current state.

## Prohibitions

- Do not ask authoring questions in Layer 1.
- Do not infer a target plugin contract in Layer 1.
- Do not select a Layer 3 skill or executor.
- Do not expose filesystem paths or secret values in state.

## Next

Load the exact local registry-selected `l2-inflak-authoring-planner` with the complete `core_handoff`, one `selected_planner: inflak-authoring` and a snapshot limited to declared required/optional fields plus universal user text/returns. All downstream success/failure paths return here before another action; only this layer decides Completion.