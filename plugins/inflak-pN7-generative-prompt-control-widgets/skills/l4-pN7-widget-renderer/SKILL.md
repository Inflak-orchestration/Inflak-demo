---
name: l4-pN7-widget-renderer
description: "Use when: rendering a semantic P7 image-prompt-control widget contract and returning structured user values to Layer 1."
---

# Layer 4 - P7 Widget Renderer

## Workflow End Boundary

After any widget return or renderer failure, immediately load `l1-pN7-core-module` with the structured result. Layer 4 never decides workflow completion, produces the final response, or continues directly to a planner or executor.

## Shared Style and Layout Policy

Use this local baseline without reading main or authoring contracts. Match host typography, neutral surfaces, spacing, borders, focus and control density using host `--iai-*` tokens/classes. Remain usable at 266px iframe width and desktop widths, use `minmax(0, 1fr)` and `min-width: 0` on shrinkable children, and prevent page-level `overflow-x` without clipping information. Confine necessary scrolling to an explicit region; keep labels/status/errors clear of controls. Avoid nested decorative cards or marketing copy.

Use native labeled controls, keyboard navigation, accessible icon names/tooltips and visible focus. Keep persistent submit/dismiss/reset actions reachable in `.iai-actions`; no confirmation checkbox, and checkboxes only for genuine multi-value boolean settings. Implement truthful disabled/loading/error/submitted states. Initialize from `window.widgetDisplay`, guard DOM/data lookups and current event state, and show recoverable inline errors. No parent DOM, storage, local files, secrets, undeclared network, remote code or modal APIs; use only approved available capabilities/libraries.

Render a validated P7 Layer 3 semantic contract using exactly `render_html_widget`. Copy `selected_widget_id` unchanged from Layer 3 into that renderer call; use it only for registry trace/observability, never to change widget UI semantics or select or replace a widget. P7 uses one inline prompt parameter editor, not detached cards, forms, or control panels. This is a generic generated renderer: do not load extra plugin JavaScript, templates, remote assets, or task tools.

Only Interaction Pathway enters L4 Renderer: user/return → L1 → L2 gap + selection → L3 Designer → L4 render → L1. Execution Pathway directly invokes generate_image or bounded main_model preparation from L2 without L3/L4. Host Agent Return and Completion do not enter L4; only L1 emits `decision: "end"`.

## Accepted Widget Types

- `inline_prompt_parameter_editor`

Registry state_update_targets names business paths under control_spec. Validate the selected entry's paths through L3 merge_strategy; semantic state_update_target is Aug, the I→Aug destination, not a literal storage path. Preserve both meanings without changing registry paths.

## Inputs (self-contained)

Validate locally; no external schema read or success `handoff_type`:

- Identity: nonempty strings `selected_widget_id`, `widget_id`, `widget_type`, `surface`, `planner_id`, `purpose`, `interaction_goal`; preserve exact L2 selection/goal and local registry eligibility/type/surface, including the distinction among all six P7 selections.
- `iai`: unchanged L2 `chain_id`, `gap_type`, binding `reason`, `maps_to_edge`, `source_nodes`, `target_node`; require named chain, meaningful reason, edge source in `source_nodes`, destination equal to `target_node` and allowed `state_update_target`, deterministic `merge_strategy`, and `next_planner_action: "re-enter Layer 1"`. Do not merge canonical state.
- `display`: actual prompt_document, source-anchored parameters, current values, candidate objects and unresolved status; every profile content source resolves. Never invent candidates, provider evidence, defaults or outcomes.
- `controls`: unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty `return_keys` limited to declared keys, and applicable `constraints` enforcing types, bounds and source/edit rules.
- `presentation.profile`: nonempty `archetype`/`summary`, nonempty `content` records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`), nonempty supported `interaction.actions`/`feedback`, and `submission` with nonempty `label`, `preconditions`, `return_mapping`. Require nonempty semantic `appearance` and `signature_features` without new stages.
- `expected_return`: exactly L2 keys/types, with exactly the same keys in `presentation.profile.interaction.submission.return_mapping`; each mapping specifies actual source/serialization and declared optional/empty handling. Validate before submission; derived metadata needs mappings, not artificial controls.
- `widget_requirements`: four nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`; implement every item consistently with profile, controls and mappings.
- `safety`: `allow_html: false`, `allow_script: false` in L3 input; only L4 writes code. Optional `runtime` uses available approved capabilities/version-pinned libraries. Optional `reference_assets` are plugin-relative design-time principles, never runtime assets.

Missing/inconsistent semantics, unsafe input or unsupported capability returns structured renderer failure to `l1-pN7-core-module` before rendering without semantic repair. Compile requirements into existing renderer fields, not undocumented tool arguments; pass display, controls, planner_id, interaction_goal and expected_return unchanged.

## Procedure

1. Verify the widget type, required `display.prompt_document`, `iai`, and `expected_return` fields. Reject contracts that contain executable markup from Layer 3.
2. Validate every source span before rendering. Span offsets use JavaScript UTF-16 string indices and must satisfy `prompt_document.text.slice(span.start, span.end) === parameter.text`. If an offset is stale, repair it only by an exact, non-overlapping, forward search for `parameter.text` in the prompt; reject an ambiguous or missing match instead of slicing a word or silently changing text.
3. Render the prompt as ordered text fragments and inline parameter tokens. For `subject-hierarchy`, replace each validated source span with one atomic inline editor containing the complete entity text and its select. Preserve every character before, between, and after spans so the surrounding prompt remains complete and fluent. The browser may move the whole editor to the next line, but it must not split the entity phrase or detach its control.
4. Open a token's compact editor in place: use `select` for fixed options, except for embedded color/theme options described below; use a text input for `text` or `select_or_text`, a range input plus numeric output for `slider`, and a number input for `number`. Do not place controls in a separate sidebar or a detached card grid.
5. On every `input` or `change`, update local parameter values and recompute the visible `compiled_prompt` immediately. Use `replace_template` for text replacements. For semantic-only controls such as priority or composition, show the changed parameter value in its entity row but leave provider-specific compilation to Layer 2.
6. Validate individual numeric bounds/steps and mutually exclusive candidate states before submission. Composition relative shares have no required total: never block submission based on their sum, normalize them or rebalance another parameter. Submit exactly L2's return through `window.submitWidget(values)`: `parameter_values`, `changed_parameter_ids`, `compiled_prompt`, `freeform_note`; prompt-control-review also includes declared `action` (accept/edit/reopen_control) and `control_category` (one registered category only for reopen_control, empty otherwise). Edits/reopen invalidate acceptance. Dismiss through `window.dismissWidget(note)`.
7. Return the exact expected shape to `l1-pN7-core-module`.

## P7 Visual and Responsive Requirements

- Use the host-injected light interface exactly as supplied: `.iai-widget`, `.iai-title`, `.iai-summary`, `.iai-field`, `.iai-label`, `.iai-actions`, `.iai-btn`, and `--iai-*` tokens. Generated CSS must not redefine `:root`, declare `color-scheme: dark`, use dark-mode media queries, gradients, literal colors, custom font stacks, or custom shadows. The sole literal-color exception is validated planner-supplied color data displayed inside embedded color/theme swatches; it must not style surrounding surfaces, text, borders or focus states. The widget background, text, borders, controls, and focus states must otherwise match the main system interface.
- Do not restyle shared classes or generic `button`, `input`, `textarea`, or `select` elements. Add only P7 layout selectors and reference `--iai-*` tokens when a layout-specific border or surface is necessary.
- For `subject-hierarchy`, reconstruct the prompt only from the original text and validated, ordered spans. Copy untouched slices byte-for-byte and replace exactly each entity slice with an inline editor; never type, summarize, normalize, or regenerate any prompt fragment.
- Make each subject-hierarchy editor an atomic `inline-flex` or `inline-grid` unit with `vertical-align: middle`, `max-width: 100%`, and normal margins. Keep the complete entity label and select together. Do not use `display: flex` or `display: grid` on the prompt text container because that would turn prose into rows.
- On widths where an entity plus its select fits, keep both on one line and use `white-space: nowrap` for the atomic unit and entity label. Allow wrapping only before or after the whole unit, never inside an entity phrase or between a partial phrase and its control.
- At `max-width: 560px`, an atomic unit that cannot fit may use a bounded two-row `inline-grid` with the complete entity label above its full-width select. It remains embedded at the entity's source position and must use `width: min(100%, 22rem)` so neither label nor control exceeds the prompt container.
- Entity labels contain `parameter.text` verbatim and remain selectable/readable. Never clip, ellipsize, split a word, or use `overflow-wrap: anywhere` / `word-break: break-word` on prompt prose, entity labels, or inline editors. Override the host's generic responsive wrapping guard for these selectors with `overflow-wrap: normal`, `word-break: normal`, and `hyphens: none`.
- Controls use a bounded width such as `clamp(8rem, 24vw, 11rem)`, plus `max-width: 100%`. Prompt prose wraps naturally only at valid text boundaries; no inline editor may cause horizontal overflow.
- For `composition-allocation`, use a labeled native range slider as each phrase's primary control with supplied min/max/step/value, readable less/more endpoints and a live numeric output without a percent suffix. Preserve native keyboard support and update only that parameter on input; reset restores supplied values. Show live relative-allocation feedback while leaving semantic-only compiled_prompt text unchanged as required by Procedure 5. Do not render a required-total meter, percent budget, normalized chart or total-based error. Keep each phrase-slider-output group unframed, preserve focus on its active control, and allow local wrapping with content-driven height so source phrases, slider labels, values and preview never overlap or clip at 266px or desktop widths.
- For `embedded-token-inspector`, populate inline choices from the complete planner-supplied candidate objects. Display the candidate `label`, use its `value` as the selected parameter value, preserve its `id` for identity, and keep the custom-value path when allowed. Never substitute role names for content candidates or show IDs as option text.
- Keep embedded phrase-control-detail wrappers unframed in every state, including changed, hover and focus-within: no enclosing border, outline or box shadow, whether solid, dashed or dotted. Use P7-scoped wrapper selectors only; do not remove the active control's host-provided keyboard focus indicator. Modification indicators occupy their own space, not an enclosing frame.
- For embedded color parameters with supplied concrete color data, render labeled swatches; for supplied multi-color themes, render compact selectable cards with actual swatches and full theme names, locally anchored to that phrase. Use accessible radio-group semantics and keyboard behavior, with a checkmark or explicit selected text independent of color. Individual choices may use restrained host-token borders, but the surrounding parameter group remains unframed. Keep current and every supplied candidate retain their original values and IDs; choosing a swatch/card uses the same parameter update, preview and submission path as a select. Use a custom color input only when the declared schema accepts its serialized color value. If concrete color data is missing or invalid, show the supplied labeled text choices instead of inferring swatches. Never replace selected_widget_id or widget_type for this presentation adaptation.
- Embedded source text, complete selected values, choice names and full prompt preview must remain readable without overlap or clipping at 266px and desktop widths. Permit natural wrapping and content-driven height; move details below their own control when needed, without forcing an unbroken row or hiding overflow. Keep the complete selected value visible outside any truncated native select. Preserve original prompt punctuation and spacing; keep annotations distinct from prose. Rebuild the full visible preview from the original source and current values on initialization, edits and reset; its text must equal submitted compiled_prompt without status labels or visual annotations.
- For `candidate-preference-selector`, keep the chooser anchored at its source phrase and render every candidate's label plus description in a bounded detail region associated with the inline control. Similar, dissimilar, and unselected states must be directly selectable; a plain select that hides descriptions or exposes only IDs is insufficient.

When a contract cites an image, read the complete host-supplied reference from `window.widgetDisplay` and assign only `window.widgetAssetUrl(ref)` to its image URL sink. Never use `.path` or `.url` directly, construct `file://`, or invent an asset id or remote image URL. Show an explicit unavailable state when the reference is absent.

## Must Not

- Do not call `generate_image`; L2 directly executes its instruction_ready plan without L3/L4.
- Do not compile prompts, infer image-model capabilities, access the parent DOM, network, files, or secrets.
- Do not add P1 templates or P1 widget behavior.
- Do not render one widget per control category or a standalone form beneath the prompt.
- Do not create a dark theme or override the host palette, even when the image prompt describes a dark scene.
- Do not convert subject-hierarchy controls into a list, table, detached form, or rows below the prompt; they remain anchored inline at their source spans.