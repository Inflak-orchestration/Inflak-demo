---
name: inflak-pN12-interactive-artifact-refinement
description: "Use when: a prompt and SVG need a grounded adaptive interaction with reversible preview and explicit Apply."
---

# P12 — Interactive Artifact Refinement

Root read by sole entry `l1-pN12-core-module`. Preserve exact nonempty source prompt and one canonical svg-document; manager normalizes safe ordinary/legacy SVGs. Persistent Canvas is active; never call render_canvas_workspace.

## Four-Layer Contract

L1 owns state/routing/Completion. L2 diagnoses/selects and loads exec-pN12-artifact-refinement to invoke ready executor/main_model; L3 only designs selected interaction_spec controls/profile; L4 implements artifact_canvas_widget. Host owns hit testing, annotations, preview, layout drafts and atomic revision commit.

## Four Pathways

| Pathway | Flow |
| --- | --- |
| Interaction Pathway | user/return → L1 → L2 gap + registry selection → L3 design → L4 render → L1 |
| Execution Pathway | user/return → L1 → L2 ready plan → direct registered executor or main_model → L1; no L3/L4 |
| Host Agent Return | user → L1 → host agent; bypass or direct_answer |
| Completion | user/return → L1 → Completion; only L1 emits decision: end |

Every result/failure re-enters L1 before further action.

## Domain Invariants

- Prompt/scene evidence grounds target hypotheses/default stable targets/confidence/capabilities. Real initial generated preview and task-specific controls, never empty picker or abstract approval.
- Color intent uses palette; multi-object composition/regions use real spatial board. L2 selects, L3 does not substitute. Free selection only after relevant grounded correction alternatives rejected.
- Preserve interaction_id, prompt span/hash, source fileId/revision, candidate/variant identity and provenance. Aug unused: no compilation/review/export.
- Adjust/Reset only transient preview; Regenerate/Correct/Reject/Dismiss no patch authorization. Only Apply authorizes complete current-revision typed operations.
- Layout host injects authoritative draft operations; iframe-local geometry is not execution evidence. If host already committed patch_result, L1 merges actual scene/revision without another execution. Otherwise approved values may enter later L2 execution.
- Required candidates are real transparent session assets before preview. Preparation never implies mutation consent. Reject stale bindings/raw SVG/XML/CSS/selectors/scripts/path data/URLs/data URIs.
- After real commit, validate/compare and collect current revision acceptance; reuse actual valid acceptance, no duplicate gate. Only L1 concludes.

## Registry and Handoffs

Local registries and [execution skill](skills/exec-pN12-artifact-refinement/SKILL.md) preserve API protocols. References noncallable. L3 local eight parts and L4 local Inputs/266px host baseline require no main skill.

## Next

Enter `l1-pN12-core-module`; all outcomes return there.