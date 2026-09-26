---
name: l1-collage-authoring-core
description: "Use when: entering unified Collage authoring or receiving any interaction, asset, export, patch, validation, or failure return."
---

# L1 Router — Collage Authoring

## Layer & Role

Read [root documentation](../../SKILL.md). Sole entry and canonical state/Completion owner; determine task route and explicit mode, never diagnose gaps, compile operations, select widgets, inspect SVG, render or execute.

## Four Pathways

| Pathway | Flow |
| --- | --- |
| Interaction Pathway | user/return → L1 → L2 gap + registry selection → L3 design → L4 render → L1 |
| Execution Pathway | user/return → L1 → L2 ready plan → exec-collage-authoring (tool/main_model) → L1; no L3/L4 |
| Host Agent Return | user → L1 → host agent; `bypass` or `direct_answer` |
| Completion | user/return → L1 → Completion; only L1 emits `decision: end` |

## State and Re-entry

Preserve `entry_mode`, `source_intent` (original text/hash/objective/constraints/export policy), `asset_plan`, `artifact`, `analysis`, `proposals`, `interaction_specs`, `active_interaction_id`, `preview_state`, `interaction_returns`, `decisions`, `augmented_intent`, `candidate_assets`, `authoring_bundle`, `pending_operations`, `execution`, `comparison_state`, `acceptance`, `prior_returns`.

Merge valid decisions by proposal/prompt-unit ID and interactions by interaction ID. Proposal decisions update `decisions`, never artifact `acceptance`. Approved semantics return to L2 for compilation; L1 does not build operations. Preserve explicit permission scope: a review-stage “not yet” ends only when the displayed submit explicitly authorizes execution; a standing “do not modify” restriction is not silently revoked.

Own successful patches advance revision and preserve execution progress/provenance; if host `patch_result` already committed, never replay it. External fileId/revision/prompt changes invalidate dependent analysis, proposals, specs/previews, decisions, Aug, candidates and pending operations. Preserve revision history, user intent and actual errors; conflicts require fresh grounding, not stale retry.

## Routing

Route exactly `collage-authoring` → `l2-collage-authoring-planner`. Explicit mode wins when inputs fit: `create` has intent without source SVG; `analyze` has explicit artifact-first analysis; `ground_prompt` preserves an existing prompt for grounding; `refine` changes a concrete SVG. If mode is materially ambiguous, retain unresolved mode for L2, never silently choose. Pure explanations/raw source editing may use Host Agent Return. L2 owns material creation-intent assessment, not L1 defaults.

## Output

Emit `core_handoff`, `decision: route_to_planner`, `selected_planner: collage-authoring`, newest declared `state_snapshot`; preserve machine `bypass`/`direct_answer` or L1-only `end`.

## Must / Must Not

Every L2 routing/execution failure, L3 validation failure, L4 return/failure and tool/host result re-enters here. Continue approved work through planning without requiring a new chat prompt, while retaining actual permission constraints. Export, generated assets, proposal approval, patch and validation alone are nonterminal. Completion requires current validated revision acceptance with no remaining action; dismissal is cancellation, never success.

## Next

Load `l2-collage-authoring-planner` after routing. All outcomes return here before further work.---
