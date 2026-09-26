---
name: inflak-collage-authoring
description: "Use when: creating, analyzing, prompt-grounding or refining a canonical SVG artifact."
---

# Unified Collage Authoring

Root read by sole entry `l1-collage-authoring-core`. One canonical svg-document and state model, persistent Artifact Canvas, no second workspace activation.

## Modes

| Mode | Behavior |
| --- | --- |
| create | Creation intent without SVG; transparent cutouts, layered collage and prepared authoring bundle. |
| analyze | Explicit artifact-first proposals, formal decisions and confirmed executable intent. |
| ground_prompt | Exact prompt plus SVG; preserve source spans/concepts/references/typed actions. |
| refine | Concrete prompt plus SVG; reversible capability-grounded interaction and Apply, no mandatory Aug. |

## Four-Layer Contract

L1 owns canonical state/routing/Completion. L2 assesses gaps, selects one eligible widget or hands a ready plan to exec-collage-authoring to invoke registered ready executor/main_model. L3 validates and designs semantics only; L4 renders artifact_canvas_widget. Host owns selection, previews/drafts and atomic commit.

## Four Pathways

| Pathway | Flow |
| --- | --- |
| Interaction Pathway | user/return → L1 → L2 gap + registry selection → L3 design → L4 render → L1 |
| Execution Pathway | user/return → L1 → L2 ready plan → direct registered executor or main_model → L1; no L3/L4 |
| Host Agent Return | user → L1 → host agent; bypass or direct_answer |
| Completion | user/return → L1 → Completion; only L1 emits decision: end |

Every result/failure re-enters L1 before further action; references are not callable executor layers.

## Domain Invariants

- Exact session fileId/revision/stable object IDs/capabilities bind every decision and typed operation. External changes invalidate dependent evidence; own commits preserve progress. Never replay host-committed patches.
- Create retains 3–6 visual-object plan, at least two actual transparent primary cutouts, 1–3 distinct candidates per successful primary and complete initial authoring_bundle. Missing material choices need evidence or scoped delegation, not silence.
- Semantic intent differs from typed manager operations; only complete approved values compile. Preserve prompt spans, constraints, provenance and rejected history.
- Proposal approval authorizes displayed scope only. Explicit execution-authorizing submission may resolve 'not yet'; standing prohibitions are not automatically revoked. No redundant approval checkbox.
- Color/spatial refinement stays specialized, only Apply authorizes current preview operations. Raster assets are real transparent session results; widgets never call image tools or write markup.
- Aug is mode-dependent and checked directly by the Host Agent before shared SVG execution. No instruction-file exporter is registered. Preserve source_intent.export_policy optional|required|disabled: required or explicitly requested export is a capability failure to resolve through L1; never invent a binding or force optional export.
- Validation/patch/export alone is not completion. Only L1 concludes after actual current revision acceptance with no outstanding action. Artifact review stays sidebar, artwork visible.

## Registry and Handoffs

Local registries and [execution skill](skills/exec-collage-authoring/SKILL.md) govern actual APIs/capabilities. L3 local eight-part output and L4 local Inputs/266px baseline are self-contained; no main skill read.

## Next

Enter `l1-collage-authoring-core`; all downstream outcomes return there.
