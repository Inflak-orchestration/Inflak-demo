---
name: l4-pN2-widget-renderer
description: "Use when: rendering P2's input-grounded visual instruction structure editor in chat."
---

# Layer 4 - P2 Structure Editor Renderer

## Workflow End Boundary

After any widget return or renderer failure, immediately load `l1-pN2-core-module` with the structured result. Layer 4 never decides workflow completion, produces the final response, or continues directly to a planner or executor.

## Shared Render Contract

L4 Renderer validates locally, with no main skill or authoring-contract read. Pass selected_widget_id, display, controls, planner_id, interaction_goal and expected_return unchanged to render_html_widget; selected ID is trace metadata, never permission to substitute. Only Interaction Pathway enters L4; L2 Planner directly executes on Execution Pathway, and only L1 Router emits decision end.

Host Agent Return and Completion belong to L1 and never enter this renderer. Registry state_update_targets names business storage: prompt_structure for the editor and instruction_preview_status for preview. Validate those paths through L3 merge_strategy; semantic state_update_target equals the selected edge destination I/T/Aug, not the storage path. Preserve both unchanged.

## Inputs

- Identity: nonempty selected_widget_id, widget_id, widget_type, surface, planner_id, purpose, interaction_goal; exact L2 selection/goal and registry type/surface/eligibility.
- `iai`: unchanged chain_id, gap_type, reason, maps_to_edge, source_nodes, target_node; named chain and meaningful reason, edge source in source_nodes, destination equals target_node and allowed state_update_target; deterministic merge_strategy and next_planner_action "re-enter Layer 1". No canonical merge here.
- `display`: actual source/groups/units or compiled instruction, current values and unresolved status; every profile source resolves, no invented evidence/defaults.
- `controls`: unique nonempty id, supported kind, nonempty label/purpose, boolean required, nonempty declared return_keys, applicable constraints for type/limits/source rules.
- `presentation.profile`: nonempty archetype/summary; nonempty content array of records with source "display.<path>", role primary|context|status and meaningful purpose; interaction has nonempty actions/feedback and submission label/preconditions/return_mapping; nonempty semantic appearance and signature_features.
- `expected_return`: exactly L2 keys/types and exactly the same return_mapping keys, with actual source/serialization and optional/empty handling. Derived metadata needs mappings, not artificial controls; validate before submit.
- `widget_requirements`: four nonempty string arrays visible_information, required_controls, required_behavior, submission_requirements; implement all consistently with profile/controls/mappings.
- `safety`: allow_html false, allow_script false in semantic input. Optional runtime uses available approved capabilities/version-pinned libraries; optional reference_assets are plugin-relative design-time principles, never runtime assets.

No success handoff_type. Invalid/missing semantics or unsupported capability returns structured failure to l1-pN2-core-module without rendering, substitution or semantic repair. Compile requirements into existing render fields, not undocumented tool arguments.

## Universal Style and Layout Baseline

Match host typography, neutral surfaces, border/spacing/focus treatment and control density through host --iai-* tokens/classes. Require usable 266px and desktop widths, minmax(0, 1fr) tracks and min-width: 0 on shrinkable children; prevent page-level overflow-x without hiding required information. Scroll only in designated semantic regions. Keep labels, values and validation messages unobscured. Native controls, accessible labels/tooltips, keyboard alternatives to drag, visible focus and truthful disabled/loading/error/submission states are required. Persistent actions remain reachable in .iai-actions. Never use a confirmation checkbox; only genuine multi-value boolean settings may use checkboxes. Avoid decorative nested cards and marketing copy.

Initialize local state from window.widgetDisplay; guard DOM/data/event lookups and show inline errors rather than blank frames. Use window.submitWidget(values) / window.dismissWidget(note). Any real asset URL comes only from window.widgetAssetUrl(ref) using the complete supplied reference; show unavailable state, never guessed paths/URLs/IDs. No parent DOM, secrets, storage/local files, undeclared network/remote code or browser modal APIs. Validate these obligations for the available template; fail through L1 if unsupported, never edit template implementation.

Render only the widget selected and validated through a fresh `L1 -> L2 -> L3` path. For `storyboard_prompt_block_composer`, render source text and grounded units rather than a curated prompt menu. For `structured_instruction_preview`, render the exact compiled instruction as a read-only generation checkpoint. Call exactly one `render_html_widget` in template mode with Layer 3 display, controls, planner id, goal, and expected return.

## Required Experience

- Show the verbatim source input in an editable source panel.
- Derive initial units from that source and preserve exact `source_span` offsets.
- Offer clear editable category groups plus one local `Unsorted` group, and place every initial source-derived unit in `Unsorted`; do not infer category assignments before user interaction.
- Highlight the corresponding source span when a unit receives focus.
- Let users edit, activate, lock, add, remove, regroup, and reorder units.
- Keep group labels editable and do not require fixed visual categories.
- Default to single-image mode; expose multi-scene mode without forcing scene count.
- Clearly distinguish `source_text`, `user_edited`, and `user_added` provenance.
- Preserve schema pN2-prompt-structure-v2 and full groups {id,label,order,scope:global|local}, units {id,raw_text,source_span,group_id,order,active,locked,user_owned,provenance}. Initial raw_text equals its half-open source slice; editing a unit preserves original spans with provenance user_edited; user-added units have null spans and provenance user_added. Source-panel edits must invalidate and explicitly reconcile affected units; never silently reassign them.
- Show a structural preview assembled from active unit wording.
- Label the editor confirmation action `Review instruction`; it must return to L1 rather than imply or invoke generation.

## Structured Instruction Preview

- Display the exact `compiled_instruction`, output mode, schema version, and provenance note.
- Provide only `Back to structure` and `Confirm & generate` decisions.
- Return `preview_status: "revise"` or `preview_status: "confirmed"` through Layer 1.
- Do not edit the instruction or call generation from the widget.

## Local Validation

Disable confirmation unless at least one active non-empty unit exists, every unit belongs to a group, ids are unique, orders are contiguous, and source spans are in bounds. Never require a fixed subject, action, shot, category, or minimum scene count.

## Editor Return

The submit handler calls `window.submitWidget(values)` with:

```json
{
  "schema_version": "pN2-prompt-structure-v2",
  "source_text": "",
  "mode": "single_image|multi_scene",
  "groups": [],
  "units": [],
  "submission_status": "draft|confirmed"
}
```

Do not compile `Aug`, call generation, or add text absent from the user's confirmed structure. Return control to `l1-pN2-core-module` after submit or dismiss.

## Preview Return

The structured instruction preview calls `window.submitWidget(values)` with exactly one decision:

```json
{"preview_status": "confirmed|revise"}
```

The preview never invokes `generate_image` directly. Return control to `l1-pN2-core-module`; Layer 2 may issue generation only after a valid `confirmed` preview return.

## Immediate Tool Call

Call `render_html_widget` as soon as validation succeeds. If the template is unavailable, return a renderer capability error through `l1-pN2-core-module`.