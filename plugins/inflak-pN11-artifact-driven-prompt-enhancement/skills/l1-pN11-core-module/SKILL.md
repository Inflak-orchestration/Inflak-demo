---
name: l1-pN11-core-module
description: "Use when: P11 receives a prompt and SVG or any grounding, approval, execution, validation, or failure returns."
---

# L1 Router — P11

## Layer & Role

Read [root documentation](../../SKILL.md). Sole callable entry and canonical state/Completion owner. Never inspect markup, diagnose gaps, extract prompt units, select widgets, compile operations, render or execute.

## Four Pathways

| Pathway | Flow |
| --- | --- |
| Interaction Pathway | user/return → L1 → L2 gap + registry selection → L3 design → L4 render → L1 |
| Execution Pathway | user/return → L1 → L2 ready plan → exec-pN11-prompt-refinement (tool/main_model) → L1; no L3/L4 |
| Host Agent Return | user → L1 → host agent; `bypass` or `direct_answer` |
| Completion | user/return → L1 → Completion; only L1 emits `decision: end` |

## State and Re-entry

Preserve exact `source_prompt`, `source_artifact_ref`, `artifact_scene`, `artifact_analysis`, `prompt_units`, `object_bindings`, `reference_resolutions`, `action_refinements`, `active_object_id`, `augmented_prompt`, `review_state`, `candidate_assets`, `execution_state`, `prior_returns`. Merge by stable prompt-unit ID and candidate action-refinement ID; preserve exact source spans and object-valued constraints. Retain executed refinement IDs and returned revisions to prevent replay.

Own successful patches advance authoritative revision while preserving approved enhancement provenance and progress. External source/prompt changes invalidate dependent analysis, units, bindings, resolutions, refinements, Aug, approval, candidates and pending execution. Changed targets, parameters or constraints invalidate affected approval. Never merge different source prompts or source revisions.

Every widget/executor result or failure and L2/L3/L4 failure enters here before another action. Approval authorizes only its matching target-bound action; candidate generation is not completion. Preserve real errors and do not retry stale patches.

## Routing

Route `pN11-svg-prompt-enhancement` → `l2-pN11-svg-prompt-enhancement` for one nonempty prompt plus one safe SVG, or active P11 continuation with those stored inputs. An empty return-turn text does not erase the source prompt. Missing initial input, unrelated answers or raw source editing follow blocked/Host Agent Return behavior.

## Output

Emit `core_handoff`, `decision: route_to_planner`, `selected_planner: pN11-svg-prompt-enhancement`, newest declared `state_snapshot`; preserve machine `bypass`/`direct_answer` or L1-only `end`.

## Must / Must Not

After all target-bound action approvals, continue Host semantic checks → execution → SVG validation without another aggregate review. Only L1 may conclude once approved work has produced the actual validated current SVG and no action remains; no revision-acceptance widget is required for P11. Explicit dismissal cancels, never fabricates success. Do not infer approval from prefilling/editing or stop at instruction synthesis.

## Next

Load `l2-pN11-svg-prompt-enhancement` after routing; all downstream outcomes return here.---