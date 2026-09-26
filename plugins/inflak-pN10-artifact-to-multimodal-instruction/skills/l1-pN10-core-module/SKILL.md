---
name: l1-pN10-core-module
description: "Use when: Analyze starts P10 or any scene, suggestion, instruction, patch, comparison, or failure returns."
---

# L1 Router — P10

## Layer & Role

Read [root documentation](../../SKILL.md) before first routing. Sole callable entry, canonical state owner and Completion authority. Never inspect SVG, diagnose gaps, generate suggestions, select widgets, plan operations, render or execute.

## Four Pathways

| Pathway | Flow |
| --- | --- |
| Interaction Pathway | user/return → L1 → L2 gap + registry selection → L3 design → L4 render → L1 |
| Execution Pathway | user/return → L1 → L2 ready plan → exec-pN10-svg-instruction (tool/main_model) → L1; no L3/L4 |
| Host Agent Return | user → L1 → host agent; `bypass` or `direct_answer` |
| Completion | user/return → L1 → Completion; only L1 emits `decision: end` |

## State and Re-entry

Preserve `source_artifact_ref`, `artifact_scene`, `artifact_analysis`, `genai_suggestions`, `suggestion_decisions`, `active_object_id`, `augmented_instruction`, `review_state`, `candidate_assets`, `execution_state`, `comparison_state`, `prior_returns`. Merge decisions by suggestion ID and candidates by operation ID. Exact `fileId`, revision, confirmed instruction and originating interaction bind every result. Retain executed operation IDs and returned revisions to prevent replay.

Own successful execution revisions preserve original Aug approval provenance and execution progress. External source/revision change invalidates dependent analysis, suggestions, decisions, Aug, review, candidate assets and pending execution. Changed targets, parameters or constraints invalidate affected approval. Do not merge across revisions or interpret failed/stale results as success.

Every L2 routing failure, L3 validation failure, L4 return/failure, tool/main-model result or revision conflict re-enters here immediately. Proposal decisions, Aug confirmation, candidate generation, patch, validation and `continue_editing` comparison are nonterminal: route again in the same response without an intervening completion summary.

## Routing

Route exactly `pN10-collage-instruction` → `l2-pN10-collage-instruction` when explicit Analyze supplies one supported safe SVG or P10 has pending work. User text is not required. Unsupported/missing inputs or out-of-scope direct-source requests use the applicable blocked/Host Agent Return behavior, never invented artifacts.

## Output

Emit `core_handoff`, `decision: route_to_planner`, `selected_planner: pN10-collage-instruction`, newest declared `state_snapshot`. Preserve `bypass`/`direct_answer`; only this layer emits `end`.

## Must / Must Not

Preserve explicit per-suggestion decisions and final Aug authorization. Patch success is not completion. Finish only after actual applied changes, validation, acceptance of the source-versus-revised comparison, and visible updated artifact; explicit dismissal cancels without claiming success. Never execute, select gaps or silently revive stale authorization here.

## Next

Load `l2-pN10-collage-instruction` after routing; every downstream outcome returns here first.---
