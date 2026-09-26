---
name: l3-pN1-prompt-keyword-grid
description: "Use when: P1 selects prompt-keyword-grid for source-grounded object extension, steering, or style keywords."
---

# L3 Designer — Prompt Keyword Grid

## Layer & Role

Design only L2's exact `prompt-keyword-grid` selection for `image-prompt-refinement` on `I→T`. Preserve the selected extension, steering, or style gap and registered goal. L3 Designer owns semantic interaction design; L4 Renderer implements it. Do not rewrite the prompt, select another gap/widget, or execute a task.

Only Interaction Pathway enters L3: L1 → L2 gap + selection → L3 Designer → L4 Renderer → L1. Execution Pathway directly invokes the selected executor/main_model from L2 without L3/L4. Host Agent Return and Completion stay with L1 and do not enter this skill.

## Inputs

Read `planner_id`, `selected_widget_id`, primary `gap_type`, `included_keyword_gaps`, `interaction_goal`, `chain_id`, `iai_binding`, `expected_return`, `return_to` and `display_context` from L2. Resolve the selected local registry entry and runtime capabilities. Consume actual `current_prompt` and prepared candidate keywords, with stable IDs, dimensions and optional hints. Candidates are model proposals, not user selections; missing candidates cannot be invented here.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Supply the selected prompt-refinement decision without adding unrelated dimensions. |
| Presented information | Keep current prompt visible beside one separate row per included open keyword dimension: a style-keyword row for `style_gap`, an object-description extension row for `extend_object_gap`, and an object-attribute/relation/direction steering row for `steer_object_gap`. A widget may contain multiple such rows. |
| Supported interaction | Toggle multiple keywords and optionally add custom text per evidenced dimension. |
| Feedback and constraints | Keep selected cells identifiable without color alone; distinguish suggested and user-added phrases. |
| Submission and return | Serialize keyword strings and custom text grouped by dimension, preserving unchanged values. |
| Presentation intent | A scannable matrix with labeled rows and accessible wrapping, not a generic form. |

## Essential Constraints

- Validate exact ID, skill/path, planner, gap, goal, edge, return coverage, artifact support, state destination and runtime availability. Preserve `prompt_keyword_grid`, `conversation_widget`, modality and capabilities.
- Preserve `chain_id`, binding `reason`, `source_nodes`, `maps_to_edge` and `target_node`; require the edge source in `source_nodes` and destination/state_update_target `T`.
- Preserve L2's nonempty ordered `included_keyword_gaps` records exactly, including each `gap_type`, `interaction_goal`, `dimension` and `reason`; require unique dimensions and the primary `gap_type` first. Build one distinct `display.rows` entry for every included record: `style_gap` → `style` row for visual style descriptors; `extend_object_gap` → `extend_object` row for descriptions that expand the named object or related content; `steer_object_gap` → `steer_object` row for attributes, counts, relations, or directions that redirect the named object. A single widget may therefore have two or three rows when those dimensions are simultaneously open. Never combine candidates from different dimensions into one row; each row has its own dimension label, candidate cells and custom-text control. Do not add resolved or not-applicable dimensions merely to fill the grid.
- Preserve candidate `id`, `keyword`, optional `hint`, dimension and current prompt. Return `selected_keywords` as dimension-keyed arrays of keyword strings, `custom_keywords` as dimension-keyed strings, and `freeform_note` as a string. Supported dimensions remain `extend_object`, `steer_object`, `style`; keep declared empty entries without turning them into required controls.
- Do not replace dimension-keyed objects with flat lists or fold selections into text in L3. L1 retains the exact return; subsequent L2 model preparation incorporates selected/custom phrases without inventing unselected content.
- One primary apply action; no approval checkbox, forced selection in every row, or second confirmation. No HTML, CSS, JavaScript, rendering or task calls. A local image reference may inform matrix design only, never runtime display.

## Output and Handoff

Pass a complete semantic contract using this local definition; no success `handoff_type` or external document read:

- Identity: nonempty strings `selected_widget_id` (exact L2 selection), `widget_id` (instance identity), `widget_type` and `surface` (exact registry values), `planner_id` (owning L2), `purpose` (contextual), and unchanged `interaction_goal`.
- `iai`: copy L2's `chain_id`, `gap_type`, and binding `reason`, `maps_to_edge`, `source_nodes`, `target_node` unchanged; require a named chain and meaningful reason, edge source in `source_nodes`, and destination equal to `target_node` and allowed `state_update_target`. Include a deterministic `merge_strategy` for L1 and `next_planner_action: "re-enter Layer 1"`.
- `display`: grounded task values, source references, current values, and unresolved status; for this widget include `current_prompt` and ordered `rows` with exactly one row per `included_keyword_gaps` record. Every row has the matching `dimension`, a dimension-specific `label`, only that dimension's candidate cells, and its own custom-text control. No invented evidence, defaults, uploads, previews, or outcomes.
- `controls`: array of records with `id`, `kind`, `label`, `purpose`, `required`, `return_keys`, `constraints`; IDs are unique/nonempty, kinds supported, labels/purposes nonempty, `required` boolean, and `return_keys` a nonempty list of declared return keys. State applicable limits, types, and source/edit rules in `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`, a nonempty `content` array of records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`); every source resolves. Include `interaction` with nonempty `actions`/`feedback` lists and `submission` (nonempty `label`, nonempty `preconditions`, `return_mapping`), plus nonempty semantic `appearance` and a nonempty `signature_features` list describing relevant behavior, not implementation or invented steps.
- `expected_return`: deterministic object with exactly L2's keys and types; `presentation.profile.interaction.submission.return_mapping` has exactly the same keys, each specifying its actual source and serialization. Preserve declared optional/empty semantics; derived returns need mappings, not artificial controls.
- `widget_requirements`: four nonempty string arrays, `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`; state minimal meaningful obligations consistent with the profile, not additional interaction gates.
- `safety`: `allow_html: false`, `allow_script: false`. Optional `runtime` declares only available approved capabilities and version-pinned libraries; optional `reference_assets` are plugin-relative design-time references and extracted principles only, never runtime assets.

Check candidate identity, dimensions and lossless serialization, then load `l4-pN1-widget-renderer`. On invalid selection or missing indispensable evidence/capability, return `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, a nonempty deterministic `validation_errors` array identifying failed checks, and `return_to: l1-pN1-core-module`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 Router owns canonical merging and emits `decision: end`. Every widget return/failure re-enters `l1-pN1-core-module`; selected keywords are nonterminal evidence, not a refined prompt or generated image.
