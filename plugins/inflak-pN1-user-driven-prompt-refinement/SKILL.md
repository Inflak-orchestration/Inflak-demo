---
name: inflak-pN1-user-driven-prompt-refinement
description: "Use when: iteratively refining an image prompt through user-selected object and style keywords, then generating from the confirmed prompt."
---

# P1 — User-Driven Prompt Refinement

A four-layer co-creation plugin for evolving image prompt text through keyword selection and prompt review, then generating from the confirmed prompt. Every request enters L1 Router, including direct questions.

This is local root documentation, not a callable alias. Preserve the existing runtime entry `l1-pN1-core-module`, skill names, paths and registry IDs; add no aliases.

## Four-Layer Contract

1. **L1 Router** reconstructs canonical state and chooses Host Agent Return, Completion, or the single `image-prompt-refinement` planner.
2. **L2 Planner** binds H/T/I/Aug/A/G, locates before/after GenAI and prompt-only/artifact-grounded state, assesses every registered gap, and selects the next material per-edge gap by dependencies. It selects one eligible widget or emits `instruction_ready` and directly invokes the registered executor or active main model.
3. **L3 Designer** validates the exact selected registry entry and designs semantic information, controls, feedback and submission mappings only. It never substitutes widgets, implements UI or executes tasks.
4. **L4 Renderer** implements the validated semantic profile as sandboxed HTML/CSS/JS, calls `render_html_widget`, and returns the structured result to L1.

Only L1 owns canonical state and emits `decision: "end"`. Every downstream result or failure is nonterminal evidence for a fresh L1 decision.

## Four Pathways

| Pathway | Control flow |
| --- | --- |
| Interaction Pathway | user/return → L1 → L2 gap + selection → L3 interaction design → L4 render → L1 |
| Execution Pathway | user/return → L1 → L2 plan → execute/realize → L1; L2 directly invokes its executor or active main model without L3 or L4. |
| Host Agent Return | user → L1 → host agent; preserve `decision: "bypass"` or `decision: "direct_answer"`. |
| Completion | user/return → L1 → Completion; only L1 emits `decision: "end"`. |

L2 routing failures (including `no_eligible_widget`) return directly to L1 without L3. L3 validation failures bypass L4. Widget submissions/dismissals, renderer failures and executor results/failures all re-enter `l1-pN1-core-module` before any next action.

## Domain and Gap Policy

H owns image intent; T is the evolving prompt; I is keyword choice, manual edit or review; Aug is not a separate P1 brief; A is the actual generated image; G is the active text model or separately the image generator. Refinement acts on `I→T`; confirmed image generation uses `T→G, G→A`.

Assess extension, steering, style and current prompt confirmation as `open`, `resolved` or `not applicable`, with evidence and the consequence of guessing in existing `iai_binding.reason` or `execution_instruction.purpose`. Silence is not delegation; scoped delegation closes only its dimensions. Preserve settled choices and reopen them only after dependent changes. Choose one next material gap by dependencies, not a fixed widget sequence or generic approval checkbox.

`prompt-keyword-grid` preserves the distinct `extend_object`, `steer_object` and `style` selected/custom keyword groups. `prompt-review` preserves the exact current prompt and accept/refine/edit decision. Prompt changes invalidate earlier acceptance. Current prompt-review acceptance is required for final generation; keyword submission alone does not authorize it.

## Handoffs and Execution

L1 emits `core_handoff`; L2 emits `planner_handoff` with either one selected gap or an `execution_instruction`. A gap preserves named `chain_id`, gap/goal, source/edge/target/`reason`, grounded `display_context`, exact typed `expected_return`, order/dependency and local L1 `return_to`. Filter and rank the local registry before selecting one exact ID; do not copy registry skill/path/type metadata into the gap or invent an eligible entry.

Each local L3 `Output and Handoff` contains all eight semantic obligations, including control-to-return mappings and complete `presentation.profile`; local L4 `Inputs` validates them. No runtime main/authoring document read, success `handoff_type`, or implementation code is needed in L3 output.

After `instruction_ready`, L2 directly invokes `generate_image` with the actual confirmed prompt and supported parameters. Bounded active-`main_model` preparation may draft a prompt, prepare candidate phrases or incorporate actual keyword choices; it returns through L1 with acceptance still open and never generates the final image. No separate executor skill is loaded. Never fabricate text acceptance, uploads or successful results.

## Registry and Next

Local `registry/planners.json`, `registry/widgets.json` and `registry/tools.json` remain canonical. Tool registration metadata is not execution authority: L2 owns task execution and L4 alone owns rendering. L4 submits through `window.submitWidget(values)`, dismisses through `window.dismissWidget(note)`, and resolves actual assets through `window.widgetAssetUrl(ref)`.

Load `l1-pN1-core-module` initially and after every return/failure. Continue through a freshly chosen pathway; escape missing/refused indispensable input or unavailable capability honestly to L1. Complete only on L1's evidence-backed `decision: "end"`, never from a downstream acceptance or timeout alone.
