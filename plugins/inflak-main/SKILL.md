---
name: inflak
description: "Use when: interactively creating or revising writing, enhancing a prompt, generating an image, or editing an existing image."
---

# inflak

A four-layer interactive co-creation plugin with five task planners and six concrete widgets. Every request enters L1 Router; factual questions and direct explanations can use Host Agent Return without entering L2–L4.

This file is shared root documentation, not a callable skill alias. The runtime entry for plugin `inflak-main` is `l1-router`; no `skills/inflak` or `skills/inflak-main` copy is needed.

## Four-Layer Contract

1. **L1 Router** (`l1-router`) reconstructs state, chooses Host Agent Return or Completion when justified, or routes exactly one task: `writing-draft`, `writing-revision`, `prompt-enhancement`, `image-generation`, or `image-edit`.
2. **L2 Planner** loads the selected `l2-*` planner, locates current state on both IAI axes, assesses every registered gap category, and selects the next material gap by dependencies. It derives that gap's missing per-edge transformation before assigning its category or selecting a widget. It emits one eligible `selected_widget_id` for L3 Designer, or an `instruction_ready` plan justified by closure across relevant gaps or bounded prerequisite preparation and directly invokes its selected registered executor or active main model.
3. **L3 Designer** validates the exact selected entry and designs only a task-specific semantic widget profile: interaction purpose, presented information, supported operations/feedback, and submission-to-return mapping, without implementing the interface or executing tasks.
4. **L4 Renderer** (`l4-widget-renderer`) converts a valid semantic contract into sandboxed UI, calls `render_html_widget`, and returns the structured result to L1 Router.

Only Layer 1 owns canonical workflow state and may emit `decision: "end"`. After every widget return, execution result, or failure, re-enter Layer 1 before any further action.

## Four Pathways

| Pathway | Control flow |
| --- | --- |
| Interaction Pathway | user/return → L1 → L2 gap + selection → L3 interaction design → L4 render → L1 |
| Execution Pathway | user/return → L1 → L2 plan → execute/realize → L1; L2 directly invokes the selected executor or active main model, without L3 or L4. |
| Host Agent Return | user → L1 → host agent; preserve the machine `decision: "bypass"` or `decision: "direct_answer"` for a direct answer. |
| Completion | user/return → L1 → Completion; only L1 may emit `decision: "end"`. |

L2 routing failures, including `no_eligible_widget`, return directly to L1 without L3. Every downstream return is nonterminal evidence for a new L1 decision, not permission to resume the previous layer.

## Tasks

| task | intended transformation |
| --- | --- |
| `writing-draft` | Create new writing from intent and justified creative latitude. |
| `writing-revision` | Transform existing text directly or through a requested comparison. |
| `prompt-enhancement` | Improve the prompt itself while preserving its intent. |
| `image-generation` | Create an image from prompt-only or actual layout resources. |
| `image-edit` | Change an existing image with a supported operation and preserved lineage. |

These are task scopes, not interaction sequences. L2 binds H/T/I/Aug/A/G, reads before/after GenAI invocation and prompt-only/artifact-grounded state, and traces the selected chain's ordered transformations. A gap needs current evidence of a missing material decision or representation, its cause and the consequence of guessing. Assess material information needs, including dimensions stored in optional fields; neither field presence nor an artifact label substitutes for this assessment. Preserve topic/visual keyword choice and actual spatial drawing for the applicable open semantic gap.

Prioritize gap detection and resolution. Assess every registered gap category against current evidence. Resolve applicable open gaps through interaction before final artifact execution. This policy applies to all five L2 planners. On every pass, assess each category registered to the selected planner as `not applicable`, `resolved`, or `open`: justify non-applicability from the current task, resolution from actual facts, prior submitted returns or explicit scoped user delegation, and an open gap from missing material information and the consequence of guessing. Keep this evidence in existing reasoning fields (`iai_binding.reason` or `execution_instruction.purpose`), not new handoff or runtime state fields.

Select one next material open gap per pass by dependencies, then its chain and eligible widget. After every return, re-enter L1, reassess all categories against the newest evidence, and continue until applicable gaps are resolved or a genuine escape is reported. `instruction_ready` permits final artifact execution only when every relevant gap is closed with evidence and other categories are justified as not applicable. Alternatively, it may authorize bounded prerequisite preparation that meets its own source, capability and consent requirements, returns to L1, and leaves unresolved user choices open; it must not execute the final artifact. Do not repeat settled questions unless relevant dependent evidence changes, and do not replace semantic gap resolution with a generic approval checkbox.

## Widgets

Silence is not delegation. A request to create does not itself authorize agent choice of every missing audience, setting or core topic. L2 distinguishes substantive intent from ordinary elaboration and actively detects and resolves material deficits even if the user did not explicitly reserve a choice. Explicit delegation closes only its corresponding dimensions; ordinary elaboration stays within evidenced intent. The ability to invent a plausible artifact is not sufficient evidence of closure.

The complete widget inventory is:

- `settings-form`
- `option-selector`
- `content-editor`
- `structure-editor`
- `canvas-editor`
- `parameter-controls`

Only after diagnosis, Layer 2 filters `registry/widgets.json` for planner, gap, goal, atomic edge, all required returns, artifact support, and available runtime capabilities/libraries. Rank eligible entries by semantic coverage, artifact specificity, return coverage, runtime fitness, stable registry order, then ID. If none qualifies, return a structured nonterminal routing failure directly to L1 Router without L3, never an invented ID or false readiness. L3 Designer validates but never replaces the selection.

## Handoffs

Layer 1 output:

```json
{"handoff_type":"core_handoff","decision":"route_to_planner","selected_planner":"writing-draft","confidence":0.9,"matched_triggers":[],"state_snapshot":{}}
```

L2 Planner output for Interaction Pathway:

```json
{"handoff_type":"planner_handoff","planner_id":"writing-draft","planner_decision":"gap_open","gap_requests":[{"chain_id":"draft-constraints","gap_type":"writing_settings_gap","interaction_goal":"refine_writing_settings","iai_binding":{"source_nodes":["I"],"maps_to_edge":"I→Aug","target_node":"Aug","reason":"Current class context does not resolve preschool read-aloud versus older independent reading, and the choice is not delegated; guessing changes vocabulary and length."},"expected_return":{"values":{},"freeform_note":""},"selected_widget_id":"settings-form","order":1,"depends_on_previous":false}],"return_to":"l1-router"}
```

L2 Planner output for Execution Pathway (assuming the user supplied an approximately 400-word story for ages 6–8 about friends restoring a garden and learning cooperation, delegating names and events only):

```json
{"handoff_type":"planner_handoff","planner_id":"writing-draft","planner_decision":"instruction_ready","execution_instruction":{"executor":{"kind":"main_model"},"purpose":"Settings are resolved by the supplied ages 6–8 and approximately 400-word scope; topic is resolved by garden restoration and cooperation. Delegation covers names and events only. Generate within this evidenced closure and return the actual draft to Layer 1."},"return_to":"l1-router"}
```

Each selected operational L3 skill's `Output and Handoff` defines the complete semantic output locally: identity, preserved IAI diagnosis and merge destination, grounded display, controls, presentation profile, exact L2 returns and mappings, widget requirements, and safety. Optional runtime and design-time references stay within declared capabilities. Use that local definition and the [L4 skill](skills/l4-widget-renderer/SKILL.md)'s inline `Inputs` rules; no extra contract or authoring document is required during this handoff. L3 preserves L2's registered goal and gap and emits no HTML, CSS, JavaScript, or success `handoff_type`; L4 implements rather than invents the semantics.

Layer 4 submits exactly the declared values through `window.submitWidget(values)` or dismisses through `window.dismissWidget(note)`. Runtime asset references use `window.widgetAssetUrl(ref)`.

## Execution Pathway

After emitting `instruction_ready`, L2 Planner directly invokes the selected `execution_instruction.executor` with its declared parameters and purpose. Main-model text work is realized by the active session model; image work uses only the registered operation selected by L2: `generate_image`, layout-grounded `edit_image`, or image-edit operations. This pathway loads neither L3 nor L4 nor a separate executor skill. Return every actual result, partial failure, or failure directly to L1 Router before further action or Completion. Never invent generated content, image file IDs, uploads, approvals, or successful tool results.

Missing or inaccessible sources, tool/capability failures, and unsupported indispensable decisions return directly from L2 or the executor to L1 as actual failures, not fabricated semantic gaps or false readiness.

Inpaint masks use transparent-edit/opaque-preserve semantics. Preserve actual source alignment and the user's edit constraints.

## Registry

`registry/planners.json`, `registry/widgets.json`, and `registry/tools.json` are canonical. Skill prose must not create an unregistered planner, widget, gap, goal, edge, return field, or executor.

Tool `layer: "session"` describes actual host registration, not a workflow layer or Host Agent Return. L2 invokes registered task executors on Execution Pathway; L4 alone invokes rendering tools on Interaction Pathway.

## Authoring Only

The [cross-layer contract](contract/CONTRACT.md), [L2 detailed contract](contract/l2-skill-contract.md), and [L3 detailed contract](contract/l3-skill-contract.md) support skill generation and review only. They live outside discovered skills, have no skill frontmatter, are not callable, and are not runtime prerequisites. Do not load them as part of an L1–L4 pass.

## Stop / Continue / Escape

- Continue through Interaction Pathway or Execution Pathway, with every result returning to L1 Router.
- Use Host Agent Return for a direct host-agent answer without entering L2–L4.
- Enter Completion only when L1 Router reconstructs current state and emits `decision: "end"`.
- Escape to L1 when indispensable input is refused, capability is unavailable, or selection validation fails; L2 failures do not enter L3.

## Next

Load `l1-router`. After every downstream return, load it again.
