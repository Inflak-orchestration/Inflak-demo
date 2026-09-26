---
name: inflak-pN2-user-driven-prompt-organization
description: "Use when: organizing a user's visual instruction into a traceable, editable prompt structure before generation."
---

# inflak P2 - User-Driven Prompt Organization

P2 starts with interaction over the user's own content. The widget presents the source text and an editable structural view whose units remain traceable to exact source spans. The user may regroup, reorder, edit, activate, lock, or add units. A single-image request stays a prompt structure; a multi-scene request may use ordered scene groups. The confirmed structure is compiled deterministically into a separate read-only structured instruction preview, and generation begins only after the user confirms that preview.

## Interaction-First Invariant

The first task effect must be `render_html_widget`, reached through `L1 -> L2 -> L3 -> L4`. Opening the structure editor realizes `H→I`; typing or pasting source content realizes `H→T`; manipulating its units realizes `I→T`. Existing `user_text` is shown immediately as `source_text`, not ignored and not replaced with a prefilled prompt menu. If no usable source content exists, the same widget provides the input field. Do not call GenAI before explicit confirmation of the subsequent structured instruction preview.

## IAI Binding

| IAI role | P2 binding |
| --- | --- |
| `H` | The user who authors and owns the source wording. |
| `I` | A chat-embedded source-and-structure editor. |
| `T` | Source text plus the user-confirmed groups, grounded prompt units, order, scope, and lock state. |
| `Aug` | A deterministic generation brief compiled from active units without erasing user wording. |
| `G` | The image GenAI invoked only after structure confirmation. |
| `A` | The generated image or multi-panel storyboard. |

The active graph is `Aug-G|G-A|H-I|H-T|I-T|T-Aug`. Runtime layer order remains `L1 -> L2 -> L3 -> L4` on the widget path.

## Four Pathways and Ownership

| Pathway | Control flow |
| --- | --- |
| Interaction Pathway | user/return → L1 Router → L2 Planner gap + selection → L3 Designer → L4 Renderer → L1 |
| Execution Pathway | user/return → L1 → L2 plan → execute/realize → L1; L2 directly invokes registered generate_image without L3 or L4. |
| Host Agent Return | user → L1 → host agent; retain decision bypass or direct_answer. |
| Completion | user/return → L1 → Completion; only L1 emits decision: end. |

L1 owns canonical state; L2 diagnoses every registered category as open/resolved/not applicable using current evidence, selects one next gap by real dependencies and ranks eligible entries. L3 only validates the exact selection and designs semantics; L4 implements its complete local profile. Silence is not delegation. Keep assessments in existing reason/purpose fields; invent no new mandatory state. No final execution while applicable choices remain open, and no GenAI preparation before the required P2 confirmations.

Every L2 routing failure, L3 validation failure, L4 return/failure and executor result/failure re-enters `l1-pN2-core-module` immediately. Only L1 chooses the next path; neither submission nor a downstream completion candidate ends the workflow. Local L3 handoffs and L4 Inputs are self-contained; do not load main or authoring contracts at runtime. Preserve stable IDs and existing entry policy; add no aliases.

The interface must use the user's source wording as its primary material. On first entry, offer clear editable category groups plus one local `Unsorted` group, and place every source-derived unit in `Unsorted`; the runtime must not infer semantic assignments. Users may select the offered groups or create, rename, and reorder their own, while all unit assignment remains user-authored structure created through interaction. Every source-derived unit carries `raw_text`, `source_span`, `provenance`, and `user_owned`; user edits do not overwrite the source text. Curated suggestions, when later added, are optional alternatives and must never masquerade as extracted content.

## Stop / Continue / Escape

- Continue after every widget return or generation result by re-entering L1.
- Only L1 may emit `decision: end` when the confirmed and preview-approved structure has produced an actual artifact and current evidence shows no remaining action.
- Escape on dismissal or unsupported intent while preserving the latest valid draft.
