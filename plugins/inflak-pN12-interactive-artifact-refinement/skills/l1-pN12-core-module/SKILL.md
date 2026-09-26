---
name: l1-pN12-core-module
description: "Use when: entering P12 or receiving an adaptive interaction, preview, candidate, patch, review, or failure."
---

# L1 Router — P12

## Layer & Role

Read [root documentation](../../SKILL.md). Sole entry; reconstruct canonical state and route. Only L1 merges state or emits `decision: end`. Never inspect SVG, diagnose gaps, generate candidates, select widgets, render or execute.

## Four Pathways

| Pathway | Flow |
| --- | --- |
| Interaction Pathway | user/return → L1 → L2 gap + registry selection → L3 design → L4 render → L1 |
| Execution Pathway | user/return → L1 → L2 ready plan → exec-pN12-artifact-refinement (tool/main_model) → L1; no L3/L4 |
| Host Agent Return | user → L1 → host agent; `bypass` or `direct_answer` |
| Completion | user/return → L1 → Completion; only L1 emits `decision: end` |

## State and Re-entry

Preserve exact `source_prompt`, `source_artifact_ref`, `artifact_scene`, `artifact_analysis`, `interaction_specs`, `active_interaction_id`, `preview_state`, `refinement_candidates`, `candidate_assets`, `interaction_returns`, `active_object_ids`, `patch_state`, `revision_history`, `comparison_state`, `acceptance_state`, `prior_returns`.

Merge specs/returns by `interaction_id`, candidates by `candidate_id`, variants by `variant_id`. Preview is transient host-owned revision-bound state, never committed SVG. Only Apply authorizes its exact typed operation set. If the host already returned successful `patch_result`, merge actual scene/revision and do not execute those operations again.

New prompt hash/fileId clears derived state; new revision preserves history and actual own commit evidence but invalidates old scene analysis, specs, previews, uncommitted candidates/returns and pending patches. Do not reuse object IDs or authorization across revisions. All L2/L3/L4 failures, executor outcomes, submissions/dismissals and conflicts re-enter here before another action.

## Routing

Route `pN12-interactive-svg-refinement` → `l2-pN12-interactive-svg-refinement` for one nonempty stored/current goal and one supported SVG. Safe ordinary/legacy SVG routes for manager import rather than invented scene data. Bypass pure explanations/raw source editing; report absent indispensable input truthfully.

## Output

Emit `core_handoff`, `decision: route_to_planner`, `selected_planner: pN12-interactive-svg-refinement`, and newest declared `state_snapshot`; preserve `bypass`/`direct_answer` or L1-only `end`.

## Must / Must Not

Apply/Adjust/Regenerate/Correct/Reject remain distinct; only real patch success advances artifact state. Do not compile/export Aug or turn preview into completion. Only L1 may finish when the current validated concrete revision is accepted and no action remains; explicit dismissal cancels without production claims.

## Next

Load `l2-pN12-interactive-svg-refinement` after routing. Every result or failure returns here.---