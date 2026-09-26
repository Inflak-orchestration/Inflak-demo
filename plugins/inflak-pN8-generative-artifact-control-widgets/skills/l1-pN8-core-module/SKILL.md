---
name: l1-pN8-core-module
description: "Use when: entering P8 or receiving any collage result, widget return, patch, or failure."
---

# L1 Router — P8

## Layer & Role

Read [root documentation](../../SKILL.md) before first routing. This is the sole callable entry. Reconstruct canonical state on initial requests and every L2 routing/execution failure, L3 validation failure, L4 result/failure, executor result, and host patch. Only L1 merges state and emits `decision: end`; never diagnose gaps, choose widgets, plan assets, render or execute here.

## Four Pathways

| Pathway | Flow |
| --- | --- |
| Interaction Pathway | user/return → L1 → L2 gap + registry selection → L3 design → L4 render → L1 |
| Execution Pathway | user/return → L1 → L2 ready plan → exec-pN8-collage-authoring (tool/main_model) → L1; no L3/L4 |
| Host Agent Return | user → L1 → host agent; `bypass` or `direct_answer` |
| Completion | user/return → L1 → Completion; only L1 emits `decision: end` |

## State and Re-entry

Preserve `user_text`, `source_prompt`, `asset_plan`, `cutout_assets`, `authoring_preparation_queue`, `prepared_authoring_results`, `collage_artifact`, `collage_scene`, `authoring_bundle`, `active_style_preset_id`, `control_opportunities`, `selected_object_ids`, `prior_returns`, `generation_state`, `comparison_state`, `acceptance_state`. Use only current session references and stable IDs.

For successful `patch_result`, merge its actual attachment/scene/revision; for `svg_document_patched`, use the canonical returned attachment and scene. Host-committed operations must not be executed again. Preserve unapplied authoring options and real candidate provenance. Revision conflict retains intent, invalidates stale bindings/previews and returns to planning. Never treat an error or old revision as authoritative success.

## Routing

Route exactly `pN8-collage-control` → `l2-pN8-collage-control` for creation, prepared authoring, object edits or unresolved current collage work. Pure explanation without creation/change may use Host Agent Return. L2, not L1, decides the next gap or tool.

## Output

Emit `core_handoff` with `decision: route_to_planner`, `selected_planner: pN8-collage-control`, and the newest declared `state_snapshot`; otherwise preserve machine `bypass`/`direct_answer` or L1-only `end`. Do not invent defaults or missing artifacts in the snapshot.

## Must / Must Not

Re-enter on every result/failure, preserve source/asset/object/revision/approval evidence, and route once. A patch, preset, or candidate selection is not a request for AI regeneration or completion. Completion requires the current collage and valid acceptance with no remaining action; explicit dismissal is cancellation, never successful production. No stale merges, fabricated success, or lower-layer completion.

## Next

Load `l2-pN8-collage-control` only after routing. Every downstream outcome returns here before another action.