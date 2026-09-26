---
name: l4-pN1-widget-renderer
description: "Use when: rendering a P1 Layer 3 widget contract (prompt_keyword_grid or prompt_review) to the frontend and waiting for the structured user return that resumes the planner."
---

# Layer 4 — Widget Renderer

## Workflow End Boundary

After any widget return or renderer failure, immediately load `l1-pN1-core-module` with the structured result. Layer 4 never decides workflow completion, produces the final response, or continues directly to a planner or executor.

## Shared Style and Layout Policy

Use this local baseline; no main skill or authoring-contract read is needed. Match host typography, neutral surfaces, spacing, borders, focus and control density using host `--iai-*` tokens/classes. Remain usable at 266px and desktop widths, use `minmax(0, 1fr)` tracks and `min-width: 0` on shrinkable children, and prevent page-level `overflow-x` without clipping information. Any necessary scrolling is confined to an explicitly designated region. Keep labels/status/errors clear of controls; avoid decorative nested cards or marketing copy.

Use native controls, accessible labels and icon tooltips, keyboard navigation, visible focus, and truthful disabled/loading/error/submitted states. Persistent submit/dismiss/reset actions belong in `.iai-actions` and remain reachable. No confirmation checkbox; checkboxes are only for genuine multi-value boolean settings. Initialize local state from `window.widgetDisplay`, guard DOM/data lookups and current event state, and show inline recoverable errors. No parent DOM, storage, local files, secrets, undeclared network/remote code or browser modal APIs. Only approved available runtime capabilities/libraries are allowed.

## Layer & Role

L4 Renderer implements one validated L3 Designer contract as sandboxed HTML/CSS/JS, calls render_html_widget and returns structured evidence to L1 Router. Only Interaction Pathway enters L4. Execution Pathway directly invokes generate_image from L2 Planner, without L3/L4; only L1 emits decision end.

Host Agent Return and Completion belong to L1 and never enter this renderer.

Layer 3 describes a reusable interaction primitive. Layer 4 owns concrete appearance, controls, event wiring, validation, and the tool call. A widget type identifies the user interaction, not the planner task; task-specific semantics arrive through the gap, display data, controls, and expected return.

You are only reachable through a fresh `L1 → L2 planner → L3` handoff on the **current** pass. If you were reached any other way, stop and re-enter Layer 1 instead of rendering.

## Inputs (widget contract from Layer 3)

- Identity: nonempty selected_widget_id, widget_id, widget_type, surface, planner_id, purpose, interaction_goal; preserve exact L2 selection/goal and local registry type/surface/eligibility. Types are prompt_keyword_grid or prompt_review.
- `iai`: unchanged chain_id, gap_type, binding reason, maps_to_edge, source_nodes, target_node; named chain, meaningful reason, edge source in source_nodes, destination equals target_node and allowed state_update_target. Require deterministic merge_strategy and next_planner_action "re-enter Layer 1"; L4 never merges canonical state.
- `display`: actual current prompt, rows or supplied previous_prompt/change_summary; preserve unresolved status, actual references and every resolvable profile source. Do not invent evidence/defaults.
- `controls`: records with unique nonempty id, supported kind, nonempty label/purpose, boolean required, nonempty return_keys limited to declared keys, applicable constraints for types/limits/source rules.
- `presentation.profile`: nonempty archetype/summary; nonempty content array of records with source "display.<path>", role primary|context|status and meaningful purpose; every source resolves. interaction has nonempty actions/feedback and submission with nonempty label/preconditions and return_mapping. Require nonempty semantic appearance and signature_features.
- `expected_return`: exactly L2 keys/types and exactly the same return_mapping keys, each with actual source/serialization and declared optional/empty handling. Validate before submit; derived metadata requires mappings, not artificial controls.
- `widget_requirements`: four nonempty string arrays visible_information, required_controls, required_behavior, submission_requirements; implement every item consistently with profile/controls/mappings.
- `safety`: allow_html false and allow_script false in L3 input; only L4 writes code. Optional runtime uses available approved capabilities and version-pinned libraries. Optional reference_assets are plugin-relative design-time principles, never runtime assets.

No success handoff_type or external schema read. Inconsistent semantics, missing indispensable evidence or unsupported capability returns structured failure to l1-pN1-core-module before rendering, without semantic repair. Compile the complete contract into existing renderer arguments; do not invent tool fields.

## Procedure

1. Confirm the `widget_type` is `prompt_keyword_grid` or `prompt_review`, validate that L3 supplied semantic data only, and reject a flat-only presentation contract. Require `presentation.profile` with `archetype`, `summary`, `content`, `interaction`, `appearance`, and `signature_features`.
2. Compile `content` into visible hierarchy, `interaction` into controls and feedback, `appearance` into layout/grouping/responsive behavior, and `signature_features` into implementation acceptance criteria. Preserve the exact return schema.
3. Generate sandbox-safe `html`/`css`/`js`, call `window.submitWidget(values)` or `window.dismissWidget(note)`, and call `render_html_widget` with `widget_type`, `render_mode: "generated"`, `display`, `controls`, `interaction_goal`, and `expected_return`. Copy `selected_widget_id` unchanged from Layer 3 into that renderer call; use it only for registry trace/observability, never to change widget UI semantics or select or replace a widget.
  - `prompt_keyword_grid`: preserve `display.title`, optional `display.summary`, `display.current_prompt`, and ordered `display.rows` (each row: `dimension`, dimension-specific `label`, cells `{ id, keyword, hint }`, and its own custom-text control). Render one visually separate row per included open keyword dimension. Never merge cells from `extend_object`, `steer_object`, or `style` into a shared row or generic candidate section; return `selected_keywords` grouped by dimension plus `custom_keywords`.
  - `prompt_review`: preserve `display.title`, `display.current_prompt`, optional `display.previous_prompt` and `display.change_summary`; return `action` and `edited_prompt`.
4. Never send `reference_assets` to the renderer; session-upload artifact references explicitly supplied in `display` remain permitted.
5. Wait for the structured widget return, then hand control back to Layer 1 (`l1-pN1-core-module`) for re-evaluation — not to the planner.

## Render Request Mapping

Pass the semantic contract together with the generated markup:

```json
{
  "widget_type": "prompt_keyword_grid",
  "selected_widget_id": "<copied-from-L3>",
  "render_mode": "generated",
  "title": "display.title or interaction_goal",
  "display": { "title": "", "summary": "", "current_prompt": "", "rows": [] },
  "controls": [],
  "planner_id": "image-prompt-refinement",
  "interaction_goal": "interaction_goal",
  "expected_return": {}
}
```

The iframe host injects `window.submitWidget(values)` / `window.dismissWidget(note)`. Do not assume access to the parent DOM, storage, local files, network, cookies, tokens, or external libraries.

When a contract cites an image, read the complete host-supplied reference from `window.widgetDisplay` and assign only `window.widgetAssetUrl(ref)` to its image URL sink. Never use `.path` or `.url` directly, construct `file://`, or invent an asset id or remote image URL. Show an explicit unavailable state when the reference is absent.

## Stable Return Shapes

- `prompt_keyword_grid`: `{ "selected_keywords": { "extend_object": [], "steer_object": [], "style": [] }, "custom_keywords": { "extend_object": "", "steer_object": "", "style": "" }, "freeform_note": "" }`
- `prompt_review`: `{ "action": "accept|refine|edit", "edited_prompt": "", "freeform_note": "" }`

## Must

- Render only the supplied P1 semantic contract; keep the current prompt visible in both widgets.
- Return values in a flat `values` object matching the contract's `expected_return`.
- Hand control back to `l1-pN1-core-module` after the widget return.

## Must Not

- Do not call any task tool (including `generate_image`); Layer 4 calls only `render_html_widget`.
- Do not insert generated HTML into the parent page or request network/remote assets.

## Next

After the widget return, control returns to `l1-pN1-core-module`, which re-routes to the planner for the next pass.
