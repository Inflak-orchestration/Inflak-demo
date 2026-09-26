---
name: l4-widget-renderer
description: "Use when: Layer 3 produced a validated semantic contract for one of inflak-main's six conversation widgets."
---

# L4 Renderer

## Workflow End Authority

Only L1 Router owns the canonical workflow state and decides Completion with `decision: "end"`. After any widget submission, dismissal, cancellation, or renderer failure, return control to `l1-router` before any further action. L4 Renderer never decides workflow completion.

## Layer & Role

L4 Renderer implements Interaction Pathway: user/return → L1 → L2 gap + selection → L3 interaction design → L4 render → L1. Compile one validated L3 Designer semantic contract into concrete sandboxed HTML, CSS, and JavaScript, call `render_html_widget`, and collect exactly the declared structured return. L3 Designer owns information and interaction design; L4 Renderer owns concrete layout, accessible implementation and event wiring. It cannot alter planner meaning, widget selection, information purpose, permitted operations, expected return keys, or workflow state. Execution Pathway, Host Agent Return, and Completion do not enter L4.

## Inputs

Validate the supplied semantic contract using these local rules; no external contract or authoring-guide read is required, and no success `handoff_type` is added:

- Identity: require nonempty strings `selected_widget_id`, `widget_id`, `widget_type`, `surface`, `planner_id`, `purpose`, `interaction_goal`; selection and planner match L2, type/surface match the selected registry entry, and goal and eligibility remain unchanged.
- `iai`: require unchanged L2 `chain_id`, `gap_type`, binding `reason`, `maps_to_edge`, `source_nodes`, `target_node`, with a named chain and meaningful reason. The edge source belongs to `source_nodes`; its destination equals `target_node` and allowed `state_update_target`. Require deterministic `merge_strategy` for L1 and `next_planner_action: "re-enter Layer 1"`; do not merge state here.
- `display`: require grounded values and actual source references, preserving unresolved status. Resolve every profile content source against this object; never fill missing evidence or invent outcomes.
- `controls`: require records with unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty `return_keys` containing only declared keys, and applicable `constraints`; validate types, limits, and source/edit rules without changing them.
- `presentation.profile`: require nonempty `archetype`/`summary`, a nonempty `content` array of records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`), and `interaction` with nonempty supported `actions` and visible `feedback` lists plus `submission` (nonempty `label`, nonempty `preconditions`, `return_mapping`). Require nonempty semantic `appearance` and a nonempty `signature_features` list; implement relevant behavior, not extra stages.
- `expected_return`: require exactly L2's keys/types and exactly the same keys in `presentation.profile.interaction.submission.return_mapping`; each mapping specifies a producible source and serialization, including declared optional/empty handling. Validate typed values before submission; no artificial controls for derived metadata.
- `widget_requirements`: require four nonempty string arrays, `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`; they must agree with the profile, controls, and return mappings, and every item must be implemented.
- `safety`: require `allow_html: false`, `allow_script: false` in L3 input; only L4 writes implementation code. Optional `runtime` uses available approved capabilities and version-pinned libraries only; optional `reference_assets` are plugin-relative design-time references/principles, never runtime assets.

Missing or inconsistent semantics, unsupported capabilities, or unsafe input produce a structured renderer failure to `l1-router` without rendering or semantic repair. A primitive name or visual adjectives alone are not a complete profile.

## Rendering Procedure

1. Validate the complete semantic profile: resolvable content sources, labeled controls and constraints, supported actions, feedback, submission preconditions and a return mapping covering exactly `expected_return`.
2. Map information roles and semantic controls to accessible concrete layout and controls. Implement only L3's designed operations; do not invent missing options, defaults or interaction semantics.
3. Generate self-contained HTML/CSS/JS with no remote fetches or parent-document access.
4. Resolve runtime image and artifact references only through `window.widgetAssetUrl(ref)`.
5. Submit values through `window.submitWidget(values)` and dismissal through `window.dismissWidget(note)`.
6. Call `render_html_widget` with `render_mode: "generated"`.
7. Pass the unmodified widget return or renderer failure to `l1-router`.

## Universal Style and Layout Baseline

The rendered widget must match the host application's UI. Use the host's typography scale, neutral surfaces, border treatment, spacing rhythm, focus treatment, and control density; task-specific presentation must not override this host-UI consistency requirement.

- The widget must remain usable at a 266px iframe width and at desktop widths.
- Use stable responsive tracks such as `minmax(0, 1fr)` and set `min-width: 0` on shrinkable children.
- Prevent page-level `overflow-x`; scroll only inside an explicitly designated region when semantically necessary.
- Keep labels, values, status, and validation messages from overlapping controls.
- Use native buttons, inputs, selects, textareas, and radios where possible. Checkboxes are allowed only for actual multi-value boolean settings, never for confirming, approving, accepting, or submitting the widget.
- Keep persistent actions in `.iai-actions`; submit, dismiss, and reset controls remain reachable. The primary submit action confirms the current widget values.
- Use icons for familiar commands when available, with accessible names and tooltips.
- Do not nest decorative cards or add marketing copy.

## Widget Requirements

Require all four `widget_requirements` arrays and implement every item. `display` supplies actual values; `controls` defines operations and constraints; `presentation.profile.content` specifies information hierarchy and purpose; `presentation.profile.interaction` specifies actions, feedback and submission. Appearance and signature features express semantic intent, not an alternative task plan. None may replace or weaken another.

Resolve each content `source` against `display`; render its stated role without fabricating absent evidence. Preserve each control's label, purpose, required status, `return_keys` and constraints. Apply `interaction.submission.preconditions` and serialize exactly its `return_mapping`, including derived metadata or actual uploaded references. Do not add artificial controls for derived fields. If references, constraints, or mappings are missing/inconsistent, return a structured renderer failure to L1 without rendering; never repair the design by changing its semantics.

The complete semantic contract is L4's input, not additional undocumented renderer-tool arguments. Compile its requirements into the existing render request fields and sandbox behavior; do not assume the host validates the profile or return schema on L4's behalf.

Special handling:

- `canvas_editor`: preserve source aspect, coordinate system, mask protocol, actual upload state, and reachable drawing controls.
- `structure_editor` and `content_editor`: preserve stable IDs, visible authored/proposed/unresolved status, and accessible ordering.
- `option_selector`: preserve stable option IDs and required selection cardinality.
- `parameter_controls`: show current numeric values and enforce declared bounds without silently changing data.

## Output

```json
{
  "title": "Widget title",
  "html": "<main class=\"iai-widget\">...</main>",
  "css": ".iai-widget { min-width: 0; overflow-x: hidden; } .iai-layout { display: grid; grid-template-columns: minmax(0, 1fr); } .iai-actions { display: flex; flex-wrap: wrap; }",
  "js": "document.querySelector('form').addEventListener('submit', event => { event.preventDefault(); window.submitWidget(values); });",
  "height": 520,
  "planner_id": "writing-draft",
  "interaction_goal": "refine_writing_settings",
  "expected_return": {"values": {}, "freeform_note": ""}
}
```

## Must

- Render exactly the selected semantic contract.
- Implement accessible keyboard, focus, label, error, disabled, loading, and submission states.
- Validate return keys and required values before submission.
- Use only approved runtime capabilities and libraries.
- Preserve actual artifact references and mask semantics.

## Must Not

- Do not add workflow steps, fields, options, defaults, confirmation checkboxes, approval controls, or task facts.
- Do not mutate planner or IAI meaning.
- Do not access the parent DOM, use remote code, or expose local paths.
- Do not call task execution tools.
- Do not produce the final workflow response.

## Stop / Continue / Escape

Continue by returning submitted values to L1 Router. On dismissal, cancellation, or renderer failure, return structured evidence to L1. Do not resume L2 or L3 directly; only L1 may select the next pathway or Completion.

## Next

After any widget return or renderer failure, load `l1-router` with the exact return envelope.
