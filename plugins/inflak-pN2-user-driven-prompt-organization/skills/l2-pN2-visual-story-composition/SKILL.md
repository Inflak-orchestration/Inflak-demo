---
name: l2-pN2-visual-story-composition
description: "Use when: P2 routes input-grounded structure editing, deterministic instruction review or confirmed image generation."
---

# L2 Planner — Input-Grounded Visual Instruction

## Workflow End Authority

Only L1 Router owns canonical state and emits `decision: end`. L2 Planner selects an eligible interaction or directly invokes its ready executor; every result/failure returns to `l1-pN2-core-module`. Execution Pathway loads neither L3 nor L4; L3 Designer never executes.

## Layer & Role

Plan one `visual-story-composition` pass. Preserve interaction-first user authorship, diagnose every registered category, select one gap by dependencies and one exact eligible entry, or directly call registered generate_image after current preview acceptance. Do not render or design semantic UI fields.

Interaction Pathway sends one gap through L3 Designer → L4 Renderer → L1. Execution Pathway directly realizes the ready plan through L2's executor → L1. Host Agent Return and Completion belong to L1 and do not enter L2; a routing failure returns directly to L1 without L3.

## IAI Domain Binding

| Node | Meaning |
| --- | --- |
| H | User who owns source wording and organization |
| T | Source text and confirmed groups/units/order/scope/lock state |
| I | Source-and-structure editing and review decisions |
| Aug | Deterministically compiled visual instruction |
| A | Actual generated image or multi-panel storyboard |
| G | Image generator invoked only after separate preview confirmation |

## Interaction Chains

| Chain ID | Paradigm / function | Ordered edges |
| --- | --- | --- |
| p2-source-organization | Enter editor, supply source and organize user-owned units | `H→I, H→T, I→T` |
| p2-structure-confirmation | User confirms the current structured T | `H→I, I→T` |
| p2-instruction-preview | Compile confirmed T and obtain review of its exact Aug | `T→Aug, H→I` |
| p2-visual-generation | Generate only the reviewed current instruction | `Aug→G, G→A` |

First task effect is render_html_widget through L1/L2/L3/L4. No GenAI call or generative preparation precedes explicit compiled-preview confirmation; deterministic segmentation/compilation is not model invention.

## Diagnosis

Position before/after GenAI and prompt-only/artifact-grounded state. Assess every category as open/resolved/not applicable from actual source, returns and current versions. Record status, source evidence and missing transfer in existing reason/purpose fields, not new state. Silence is not delegation. Select one next material gap by dependencies, not the first row mechanically; a future preview is blocked by invalid structure, not falsely resolved.

| gap_type | Condition | Edge | Interaction goal |
| --- | --- | --- | --- |
| `prompt_structure_entry_gap` | No user-editable source structure has been entered. | `H→I` | `organize_prompt_structure` — enter source-grounded organization. |
| `prompt_source_gap` | Source and user-added units lack usable authored content. | `H→T` | `add_source_content` — supply real text. |
| `prompt_structure_gap` | Current units/groups violate structural or source invariants. | `I→T` | `repair_prompt_structure` — repair explicit errors. |
| `prompt_confirmation_gap` | A valid current structure remains unconfirmed. | `I→T` | `review_prompt_structure` — confirm or revise current units. |
| `instruction_preview_gap` | Confirmed structure has an exact compiled instruction but no current preview acceptance. | `T→Aug` | `review_compiled_instruction` — confirm exact compiled meaning or revise. |
| `instruction_ready` | Current structure and exact preview are explicitly confirmed and all applicable gaps are closed. | `Aug→G` then `G→A` | L2 directly invokes generate_image and returns the actual artifact. |

Preserve real source → valid structure → explicit structure confirmation → deterministic compilation → separate preview confirmation dependencies. Changed source/units invalidate compiled_instruction and preview acceptance. Revise returns to structure; no missing input, empty confirmed status or generic checkbox closes a gap.

## Widget Registry Routing

All entry/source/repair/structure-confirmation gaps use eligible `storyboard-block-composer`; preview uses eligible `structured-instruction-preview`. Filter local registry by exact planner/gap/goal/atomic edge, all returns, artifact support and actual capability/library/renderer availability; rank semantic coverage, artifact specificity, return coverage, runtime fitness, stable registry order, then ID. Preserve one exact selected_widget_id and no copied type/skill/path/profile metadata.

No match returns directly to L1 without L3: reason no_eligible_widget, planner_id, diagnosed_gap (chain/evidence/edge/goal/returns), rejected_candidates with failed constraints, return_to. Missing capability is not false readiness.

## Structure and Compilation Constraints

Version is `pN2-prompt-structure-v2`. Return keys are exactly schema_version/source_text/mode/groups/units/submission_status. Mode is single_image or multi_scene; status draft or confirmed. Groups preserve id/label/order/scope (global/local); units preserve id/raw_text/source_span/group_id/order/active/locked/user_owned/provenance. IDs are unique, orders contiguous within group, references valid and confirmation requires at least one active nonempty unit.

Source spans use zero-based half-open string offsets; source-derived raw_text initially equals its exact source slice. Edited units retain original span with provenance user_edited; user_added units have null spans. On first entry show source verbatim, offer editable category groups plus one local Unsorted group and assign all initial source units there without inferred categorization. Preserve user grouping thereafter; do not impose categories or multi-scene counts.

Precise nested types: group `{id: string, label: string, order: positive integer, scope: global|local}`; unit `{id: string, raw_text: string, source_span: {start: integer, end: integer}|null, group_id: string, order: positive integer, active: boolean, locked: boolean, user_owned: boolean, provenance: source_text|user_added|user_edited}`. Span indices are JavaScript UTF-16 code units with `0 <= start < end <= source_text.length`; initially `source_text.slice(start,end) === raw_text`. Retain locked/user-owned state and explicitly reconcile source edits. Never cast booleans or orders to strings.

Registry state_update_targets are business paths (`prompt_structure`, `instruction_preview_status`), not literal IAI nodes. Preserve those paths for L1 merging; semantic state_update_target equals the selected edge destination I/T/Aug. Do not reject a valid mapping because its business path differs from the node, or rewrite paths to node names.

Compile only a valid confirmed structure: traverse groups and active units in order, preserve raw_text verbatim, use labeled sections for single_image and ordered local scenes plus global direction for multi_scene. Preserve unit-to-output provenance; never invent subjects/events/style/camera/constraints/transitions. Store the exact string in compiled_instruction for read-only preview and send that exact accepted string for generation. Compilation/review are distinct from new content generation.

## Gap Handoff

One request preserves chain_id, exact gap/goal, binding source/edge/target/reason, typed expected_return, grounded display_context, selected_widget_id, order 1 and real depends_on_previous. Edge source belongs to source_nodes and target equals destination. Pending input remains pending; L3 preserves chain_id and reason unchanged.

Example assumes an initial source request “A red boat on a lake” with no structure:

```json
{"handoff_type":"planner_handoff","planner_id":"visual-story-composition","planner_decision":"gap_open","gap_requests":[{"chain_id":"p2-source-organization","gap_type":"prompt_structure_entry_gap","interaction_goal":"organize_prompt_structure","iai_binding":{"source_nodes":["H"],"maps_to_edge":"H→I","target_node":"I","reason":"The user supplied boat-and-lake text but has not authored its organization on H→I. A source-linked editor lets the user supply structure without guessed assignments."},"expected_return":{"schema_version":"pN2-prompt-structure-v2","source_text":"","mode":"single_image","groups":[],"units":[],"submission_status":"draft"},"display_context":{"schema_version":"pN2-prompt-structure-v2","source_text":"A red boat on a lake","prompt_structure":null,"validation_errors":[]},"selected_widget_id":"storyboard-block-composer","order":1,"depends_on_previous":false}],"return_to":"l1-pN2-core-module"}
```

Repair uses the same full return plus actual errors. Preview uses p2-instruction-preview, T→Aug, review_compiled_instruction, structured-instruction-preview, and exactly `preview_status` (confirmed/revise), with actual compiled_instruction/mode/version/provenance_note. No freeform field is added.

## Output (planner_handoff)

Choose exactly one mode. Example assumes both structure and this exact preview were actually confirmed:

```json
{"handoff_type":"planner_handoff","planner_id":"visual-story-composition","planner_decision":"instruction_ready","execution_instruction":{"executor":{"kind":"tool","name":"generate_image"},"parameters":{"prompt":"A red boat on a lake"},"purpose":"The current valid user-owned structure and this exact deterministic preview are explicitly confirmed; all relevant gaps are closed. Generate only the reviewed instruction and return actual output to L1."},"return_to":"l1-pN2-core-module"}
```

## Inputs and Procedure

Consume selected_planner and required user_text/source_text/schema_version; optional prompt_structure/structure_submitted/compiled_instruction/instruction_preview_status/generated_artifacts/prior_returns and local registry/runtime context. Preserve first-turn user_text verbatim as source_text. Assess every gap, validate actual dependencies, compile only confirmed structure, route one eligible gap or execute ready generation, then return actual result/failure to L1.

## Must / Must Not / Tools

L2 alone directly invokes registered generate_image after instruction_ready, with the exact reviewed prompt and only supported supplied size/quality. Never run GenAI before preview confirmation, replace user content with curated blocks, silently categorize/rewrite/discard text, render, author L3 semantics, invent artifacts or add approval checkboxes. L4 owns rendering; no separate L3 executor.

## Stop / Continue / Escape

Stop the local pass at eligible L3 handoff or actual result/failure to L1. Continue only through L1. Refused indispensable input or unavailable template/tool returns honestly to L1, preserving the current draft.

## Next

Interaction Pathway sends the selected gap to L3 Designer then L4 Renderer. Execution Pathway has L2 directly call generate_image without L3/L4. All results and failures return to `l1-pN2-core-module`; only L1 decides Completion.