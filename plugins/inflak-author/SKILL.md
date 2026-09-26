---
name: inflak-author
description: "Use when: a person wants to conversationally design, preview, validate, and publish a new inflak plugin without authoring IAI graphs, contracts, registries, or runtime adapters by hand."
---

# inflak Author

Turn a plain-language idea for a human-AI workflow into a complete, independently loadable four-layer inflak plugin. Interview the author about the desired experience, not the implementation vocabulary. Infer the IAI model, state, gaps, interaction contracts, registries, and execution policy internally.

This root is documentation read by the existing sole-L1 compatibility entry `l1-inflak-author-core`; it is not an extra callable alias. Target-plugin generation retains its own required entry policy.

## Four Pathways and Ownership

| Pathway | Control flow |
| --- | --- |
| Interaction Pathway | user/return → L1 → L2 gap + selection → L3 interaction design → L4 render → L1 |
| Execution Pathway | user/return → L1 → L2 plan → exec-plugin-authoring → execute/realize → L1; exec-plugin-authoring executes the L2 plan and invokes the selected executor without L3/L4. |
| Host Agent Return | user → L1 → host agent; retain `decision: bypass` for a direct informational answer. |
| Completion | user/return → L1 → Completion; only L1 emits `decision: end`. |

L1 alone reconstructs/merges canonical state. L2 owns six-node domain reasoning, named chains, every registered category's evidence-backed `open`/`resolved`/`not applicable` assessment and one dependency-selected next gap or direct ready execution. L3 designs only the exact selected interaction using its complete local handoff; L4 validates through self-contained Inputs and implements it. Every downstream result, cancellation or failure returns immediately to L1, including L2 routing failures and L3 validation failures.

## Authoring Experience

- Start from the author's own description and reuse every detail already supplied.
- Advance through one visible design substep per pass: task framing, one workflow stage, artifact/state flow, one target interaction design, then final review.
- Ask at most one consequential clarification per pass and normally no more than four unstructured clarification questions in total. Structured substep reviews do not count as extra questioning.
- Ask only about outcomes, AI initiative, human agency, checkpoints, process visibility, revision, trust, or genuinely required execution resources.
- Offer a recommended default and accept "use the recommendation" without further interrogation.
- Never ask the author to define IAI nodes, edges, gap schemas, tool schemas, registries, or skill file structure. The widget-design substep may show plain-language interaction goals, modes, widget families, and visual concepts for review; the system authors their contracts.
- Infer reversible low-risk details and expose them inside the relevant substep instead of saving all assumptions for one large final screen.

## Progressive Design Sequence

1. **Frame the task.** Show a compact problem-framing board with target user, starting information, intended outcome, success signals, and exclusions. The author confirms or edits the inferred frame.
2. **Design the workflow one stage at a time.** For one candidate stage, show user work, AI work, required information, autonomy boundary, checkpoint, visible progress, intermediate artifact, completion, branch, and failure path. Define which raw interaction outcomes continue, loop, complete, cancel, or escape the workflow. Reopen the same stage if materially unclear.
3. **Review artifact and state flow.** Show inputs, intermediate artifacts, decisions/status, final artifact, visibility, revision binding, and invalidation as a connected flow rather than a prose inventory.
4. **Design one target interaction at a time.** For each confirmed input/checkpoint/review need, show the interaction goal, interaction mode, recommended widget family, displayed information, controls/actions, feedback, alternatives, and a small non-executing preview. For every meaningful return outcome, define the exact raw-value match, canonical state target, merge rule, workflow effect, next stage, and whether it is terminal. Prefer task-fitting and materially varied widgets over repeated forms/cards.
5. **Confirm a real example.** Include at least one realistic acceptance case with its starting request, intended human checkpoint, and observable successful outcome. Keep contract assertions in implementation details.
6. **Review and build.** Show a compact progressive summary with phase sections collapsed by default, then compile and review the immutable build.

Do not skip an earlier phase because the model can infer its contents. Inference prepares the candidate; the corresponding visual substep lets the author inspect it without answering implementation questions.

## Execution Resources

Default to the host agent when it can faithfully perform the task. Ask about files only when the author mentions or clearly requires an existing skill, script, model service, API description, template, or domain resource. Let the author upload those files through the resource-intake interaction; uploaded resources use stable `fileId` references. Do not request API keys, tokens, passwords, or other secrets in chat or uploads.

An uploaded resource is inspected before it can influence a generated runtime. Python is treated as untrusted source for static inspection and adapter planning, never executed during authoring. Missing custom runtime implementation keeps the generated plugin in `planned` status. Host fallback is allowed only when it preserves the promised behavior.

## Mandatory Layer Loop

1. Load `l1-inflak-author-core` on the first turn and after every interaction or tool result.
2. Layer 1 reconstructs the authoring revision and selects `l2-inflak-authoring-planner`.
3. Layer 2 diagnoses one semantic authoring gap, filters and ranks `registry/widgets.json` candidates against the planner, gap, interaction goal, IAI edge, expected return, artifact context, and runtime availability, and emits one eligible entry's exact registry ID as `gap_requests[0].selected_widget_id`. When authoring is ready to advance, Layer 2 instead selects one registered executor.
4. On an interaction path, Layer 3 resolves `selected_widget_id`, validates that selected entry against the same planner, gap, goal, edge, return, artifact, and runtime constraints, and realizes its semantic contract without searching for, rerouting to, or substituting another widget. `l4-inflak-author-renderer` renders that contract in the conversation.
5. On Execution Pathway, Layer 2 hands its ready plan to exec-plugin-authoring, which invokes exactly the selected registered executor with complete parameters and purpose; it loads neither L3 nor L4. Necessary operation rules live in the [execution skill](skills/exec-plugin-authoring/SKILL.md), loaded as exec-plugin-authoring.
6. Every return re-enters Layer 1 unchanged. Layer 1 interprets the raw return using the selected interaction's approved outcome semantics; the host never converts widget values into plugin workflow state. Publishing requires approval of the exact current preview hash.
7. A ready publication also requires one real-session acceptance probe. A failed probe leaves the installed plugin `planned` and returns its run, trace, failed checks, widget contracts/returns, tool results, and artifacts to Author for revision.

## User-Facing Reviews

Each design phase is reviewed when it is created, so the final experience review is a compact coverage summary rather than the first time the author sees everything. It shows confirmed phase counts, unresolved assumptions, key transitions, interaction diversity, final presentation, and at least one realistic acceptance case; details remain available in collapsed phase sections. After approval, compile a staging bundle and show a build review that traces the approved workflow, state model, interaction methods, and final presentation into generated skills and registries, alongside examples, assumptions, limitations, runtime readiness, validation results, scenario controls, and file summary. Keep IAI and registry diagnostics collapsed as implementation details.

## Registries

`registry/planners.json`, `registry/widgets.json`, and `registry/tools.json` are the machine-readable contract for this plugin.

Task tools have session registration and L2 invocation responsibility; L4 alone renders. Preserve all eight Author-specific widgets rather than replacing them with main's six primitives. All registered IAI state targets match the diagnosed edge destination; L1's merge rules map returned decisions to existing domain state fields. No generic approval checkbox replaces domain risk decisions, progressive review or exact-hash publication consent.