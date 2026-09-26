---
name: l4-pN6-widget-renderer
description: "Use when: rendering a P6 traceable prompt structure, cell map, or Story Brief as a generated conversation widget and returning structured author input to Layer 1."
---

# Layer 4 - P6 Widget Renderer

## Workflow End Boundary

After any widget return or renderer failure, immediately load `l1-pN6-core-module` with the structured result. Layer 4 never decides workflow completion, produces the final response, or continues directly to a planner or executor.

## Shared Style and Layout Policy

Use this local baseline without reading main or authoring contracts. Match host typography, neutral surfaces, spacing, borders, focus and control density using host `--iai-*` tokens/classes. Remain usable at 266px iframe width and desktop widths, use `minmax(0, 1fr)` and `min-width: 0` on shrinkable children, and prevent page-level `overflow-x` without clipping information. Confine necessary scrolling to an explicit region; keep labels/status/errors clear of controls. Avoid nested decorative cards or marketing copy.

Use native labeled controls, keyboard navigation, accessible icon names/tooltips and visible focus. Keep persistent submit/dismiss/reset actions reachable in `.iai-actions`; no confirmation checkbox, and checkboxes only for genuine multi-value boolean settings. Implement truthful disabled/loading/error/submitted states. No parent DOM, storage, local files, secrets, undeclared network, remote code or modal APIs; use only approved available capabilities/libraries and the local reliability rules below.

## Role

Render a validated P6 Layer 3 semantic contract as one sandboxed widget in the conversation. Generate HTML, CSS, and JavaScript from the contract, then call exactly one render tool, `render_html_widget`, with `render_mode: "generated"`. This skill is reached only through a fresh `L1 -> L2 -> L3` widget handoff. It never writes a story or calls a task tool.

Only Interaction Pathway enters L4 Renderer: user/return → L1 → L2 gap + selection → L3 Designer → L4 render → L1. Execution Pathway directly invokes active main_model from L2 without L3/L4. Host Agent Return and Completion do not enter L4; only L1 emits `decision: "end"`.

## Accepted Widget Types

- `prompt_structure_tree`
- `prompt_cell_map`
- `story_brief_review`

Registry state_update_targets names business storage prompt_structure/prompt_components/augmented_instruction. Validate those paths through L3 merge_strategy; semantic state_update_target is T for organization or Aug for Brief review, not a literal storage path. Preserve both meanings without changing registry paths.

## Inputs (self-contained)

Validate locally; no external schema read or success `handoff_type`:

- Identity: nonempty strings `selected_widget_id`, `widget_id`, `widget_type`, `surface`, `planner_id`, `purpose`, `interaction_goal`; preserve exact L2 selection/goal and local registry eligibility/type/surface.
- `iai`: unchanged L2 `chain_id`, `gap_type`, binding `reason`, `maps_to_edge`, `source_nodes`, `target_node`; require named chain, meaningful reason, edge source in `source_nodes`, destination equal to `target_node` and allowed `state_update_target`, deterministic `merge_strategy`, and `next_planner_action: "re-enter Layer 1"`. Do not merge canonical state.
- `display`: actual task values, source references, current values and unresolved status; every profile content source resolves. Preserve authorship/provenance and never invent fragments, defaults, approvals or outcomes.
- `controls`: unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty `return_keys` limited to declared keys, and applicable `constraints` enforcing types, limits and source/edit rules.
- `presentation.profile`: nonempty `archetype`/`summary`, nonempty `content` records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`), nonempty supported `interaction.actions`/`feedback`, and `submission` with nonempty `label`, `preconditions`, `return_mapping`. Require nonempty semantic `appearance` and `signature_features` without new stages.
- `expected_return`: exactly L2 keys/types, with exactly the same keys in `presentation.profile.interaction.submission.return_mapping`; each mapping specifies actual source/serialization and declared optional/empty handling. Validate before submission; derived metadata needs mappings, not artificial controls.
- `widget_requirements`: four nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`; implement every item consistently with profile, controls and mappings.
- `safety`: `allow_html: false`, `allow_script: false` in L3 input; only L4 writes code. Optional `runtime` uses available approved capabilities/version-pinned libraries. Optional `reference_assets` are plugin-relative design-time principles, never runtime assets.

Missing/inconsistent semantics, unsafe input or unsupported capability returns structured renderer failure to `l1-pN6-core-module` before rendering without semantic repair. Compile requirements into existing renderer fields, not undocumented tool arguments.

## Procedure

1. Verify the widget type is `prompt_structure_tree`, `prompt_cell_map`, or `story_brief_review`. Preserve every supplied component, fragment, provenance record, missing component, selected item, expanded item, unresolved item, and approval state.
2. For `prompt_structure_tree`, generate a responsive, accessible hierarchy editor. Render the `Traceable fragments` panel below the hierarchy and synchronize it to the selected node: it shows only fragments named by that node's `fragment_ids`, in their existing order, and re-renders immediately after node selection or fragment assignment changes. For example, when `Mira` is selected, show only the character and role fragments assigned to `Mira`; do not show fragments owned by other branches. Preserve the established fragment card presentation: bordered card, kind/id-to-branch heading, editable textarea, Unassign, Split, Merge, and Delete actions, and provenance line. Show an explicit selected-branch empty state when the selected node has no fragments. Render a linked selected-node detail. Make drag-to-reparent and sibling reordering work, but also provide working keyboard-accessible move controls. Support node create, rename, delete, confirmation state, fragment assignment/edit/create/delete, fragment split, fragment merge, and provenance inspection. Do not use a canvas, spatial coordinates, directed edges, or React Flow.
  For layout, treat the node label as primary content. A node's first row contains only its expand/collapse control, label, and status; render Up/Down/Out/In as icon buttons with tooltips in a second row or one compact actions menu. Never place all movement controls in the same grid track as the label. Use `minmax(0, 1fr)` for the label track, give the label at least 120px when controls are visible, set `min-width: 0`, and use single-line ellipsis with the full label available through an accessible name or tooltip; never wrap a label character by character. Use a two-column hierarchy/detail layout only when the hierarchy can remain at least 280px and detail at least 320px; otherwise stack the panes vertically. At 266px iframe width, use one column and move secondary actions below content. Pane scrolling must be vertical and independent, with no horizontal scrollbar or overlap.
3. For `prompt_cell_map`, generate a responsive, accessible topic-grouping editor. It must make cell creation, rename, deletion, drag-to-reorder, drag-to-assign/remove fragments, and inline content editing available. Each cell must expose an explicit expand/collapse control whose expanded detail permits editing the cell label and assigned fragment text, while showing active grouped fragments separately from unassigned suggested fragments. Do not imply directed relationships or synthesize hierarchy.
4. For `story_brief_review`, generate a responsive, accessible editable brief. Show each brief section with its status and provenance, support selection, expand/collapse, inline edits, and confirmed/unresolved status changes, and expose working Approve Brief and Return to Structure actions. Story generation is never an action inside the widget.
5. Compile `presentation.profile.content` into visible hierarchy, `interaction` into controls and feedback, `appearance` into responsive grouping, and `signature_features` into implementation acceptance criteria. Keep selection, affected content before deletion, provenance, status, and approval state unambiguous.
6. Make every visible button, control, and exposed function work. Bind each to a real event handler; it must update the widget's local state, visible feedback, or structured return. Verify drag, move controls, expand/collapse, edit, create, delete, split, merge, assignment, status, approval, submit, and dismiss interactions before rendering. Never render decorative, disabled, placeholder, or no-op controls.
7. Use `window.submitWidget(values)` only after validating tree, cell, or brief invariants, as applicable. Use `window.dismissWidget(note)` when the author dismisses the widget. Preserve the exact `expected_return` shape.
8. Read all runtime contract data from the host-injected read-only `window.widgetDisplay`, including `tree_nodes`, `root_ids`, `fragments`, `cells`, `unassigned_fragment_ids`, `brief_sections`, selected ids, expanded ids, unresolved ids, and approval state. Do not generate placeholders such as `__DISPLAY__`, `${DISPLAY}`, or `{{display}}`; the host does not interpolate generated code.
9. Apply the runtime reliability requirements below before rendering the iframe.
10. Call `render_html_widget` once with the generated `html`, `css`, and `js`; pass through `widget_type`, `selected_widget_id`, `display`, `controls`, `planner_id`, `interaction_goal`, and `expected_return` unchanged. Use `selected_widget_id` only for registry trace/observability; it must not change widget UI semantics or select or replace a widget.
11. Return the structured result to `l1-pN6-core-module`. Story generation cannot start directly from Layer 4.

## Runtime Reliability Requirements

- Do not call browser modal APIs: `alert()`, `confirm()`, or `prompt()`. The iframe is sandboxed without `allow-modals`. For destructive actions, render an in-widget confirmation state with working Confirm and Cancel controls.
- Initialize local state from `window.widgetDisplay` before querying or rendering DOM. Treat absent arrays as `[]`, absent objects as `{}`, and absent selected ids as empty strings.
- Guard every DOM lookup and every data lookup. Before calling methods or reading properties, verify that `querySelector` / `getElementById` returned an element, a node/cell/edge id resolves to an existing item, and a map lookup is not `undefined` or `null`.
- Event handlers must read current local state and tolerate a removed or collapsed selection. Never assume a node, cell, fragment, edge, or DOM element still exists after a prior edit or delete action.
- Render a usable empty state when the graph or cell map has no items. On an unrecoverable widget-local error, show an inline error message with a working dismiss control rather than throwing an uncaught exception or leaving a blank iframe.
- Keep generated JavaScript self-contained and deterministic: establish state, render DOM, then bind events. Do not bind handlers to elements before they are rendered.
- Before a tree submit, validate that each non-root parent id resolves, no node is its own ancestor, sibling order is unique, each fragment belongs to at most one node, and every retained provenance list is preserved. Render an inline validation message and do not submit an invalid tree.
- Before a Story Brief submit with `approved: true`, validate that every required section exists and no required section remains unresolved. Editing any section resets local approval state to `false`.

## Render Request Mapping

```json
{
  "widget_type": "prompt_structure_tree",
  "selected_widget_id": "<copied-from-L3>",
  "render_mode": "generated",
  "title": "display.title or interaction_goal",
  "html": "generated sandboxed markup",
  "css": "generated sandboxed styles",
    "js": "generated sandboxed behavior that reads window.widgetDisplay and calls window.submitWidget(values)",
  "display": {"tree_nodes": [], "root_ids": [], "fragments": [], "selected_node_id": "", "expanded_node_ids": [], "unresolved_ids": []},
  "controls": [],
  "planner_id": "prompt-decomposition",
  "interaction_goal": "organize_prompt_hierarchy",
  "expected_return": {}
}
```

## Stable Return Shapes

```json
{
  "prompt_structure_tree": {
    "structure_kind": "tree",
    "tree_nodes": [],
    "root_ids": [],
    "selected_node_id": "",
    "expanded_node_ids": [],
    "fragment_edits": [],
    "unresolved_ids": [],
    "freeform_note": ""
  },
  "prompt_cell_map": {
    "structure_kind": "cell_map",
    "cells": [],
    "unassigned_fragment_ids": [],
    "selected_cell_id": "",
    "fragment_edits": [],
    "freeform_note": ""
  },
  "story_brief_review": {
    "structure_kind": "story_brief",
    "brief_sections": [],
    "selected_section_id": "",
    "unresolved_ids": [],
    "approved": false,
    "freeform_note": ""
  }
}
```

## Must

- Render only the supplied P6 semantic contract and preserve `source_prompt_ids` on tree nodes, cells, brief sections, and fragments.
- Generate and render the widget in the conversation with `render_html_widget` and `render_mode: "generated"`.
- Read runtime data from `window.widgetDisplay`; it is the only injected display-data API.
- When a contract cites an image, pass the complete host-supplied reference to `window.widgetAssetUrl(ref)` and use only its result. Never use `.path` or `.url` directly, construct `file://`, or invent an asset id or remote image URL; show an explicit unavailable state when absent.
- Ensure every visible button, control, and exposed function has working event wiring and changes state, visible feedback, or the submitted return value.
- Meet every `Runtime Reliability Requirements` rule before calling `render_html_widget`.
- Return values as a flat object matching `expected_return`, then hand control back to `l1-pN6-core-module`.

## Must Not

- Do not call `render_canvas_workspace`, host Canvas APIs, React Flow, or any task tool.
- Do not use `render_mode: "template"`, load a template, or add a fixed frontend implementation.
- Do not use `__DISPLAY__`, `${DISPLAY}`, `{{display}}`, or another unresolved data placeholder in generated HTML, CSS, or JavaScript.
- Do not render a decorative, disabled, placeholder, or no-op button, control, or exposed function.
- Do not call `alert()`, `confirm()`, or `prompt()`, or leave an unguarded DOM or data lookup that can throw in the sandboxed iframe.
- Do not access the parent DOM, network, storage, local files, cookies, tokens, secrets, or remote assets.

## Next

After every widget return, control returns to `l1-pN6-core-module` for fresh routing.