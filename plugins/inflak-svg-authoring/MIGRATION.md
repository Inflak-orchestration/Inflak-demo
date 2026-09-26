# SVG Authoring Contract Migration

This record describes the unified SVG documentation/registry migration. The subsequent P10/P11 simplification removes their independent export runtimes; shared Host SVG execution and frontend behavior remain unchanged.

- Four pathways now separate Interaction (L1 → L2 selection → L3 design → L4 → L1), Execution (L1 → L2 ready plan → exec-svg-authoring (tool/main_model) → L1), Host Agent Return and L1-only Completion.
- Duplicate external-tool and execution overview documents are consolidated into `skills/exec-svg-authoring/SKILL.md`, owned by a discoverable execution skill parallel to L3 interaction design, not another numbered layer. Tool registry entries retain actual callables/capabilities and point to this document, never an L3 executor.
- L2 retains create/analyze/ground_prompt/refine semantics, six domain nodes, named ordered chains and evidence-backed registered-gap diagnosis. Model-only preparation, compilation, validation and failures are not fake interaction gaps.
- Every L3 has six compact sections and the complete local eight-part semantic output. L4 validates locally, implements the 266px host baseline, and preserves Artifact Canvas protocols.
- Create preserves actual alpha assets and prepared options; analyze preserves formal decisions and permission; ground_prompt preserves exact spans; refine preserves actual preview and Apply. Host Agent checks replace the former instruction export prerequisite. No instruction-file exporter is currently registered.
- Host-owned hit testing, layout drafts, patch results, revision invalidation, sidebar artifact review and canonical operation schemas remain unchanged. Submitted intent and committed executor effects are distinguished to prevent duplicate patches.
- Legacy independent plugins remain separate entry points. This migration does not consolidate their runtime handlers or assert live acceptance.

## Unified Implementation Background

## Scope

This change adds `inflak-svg-authoring` as the unified implementation for SVG collage creation and SVG modification. Existing P8/P10/P11/P12 directories remain available as compatibility and experiment-condition entry points; they are not deleted or rewritten in this migration.

## Entry Mapping

| Legacy case | Unified `entry_mode` | Preserved behavior | Consolidated behavior |
| --- | --- | --- | --- |
| P8 | `create` | Transparent cutout generation, collage composition, prepared authoring bundle, direct controls | Uses shared state, grounding, operation families, review, and external executor. |
| P10 | `analyze` | Prompt-free artifact analysis, 3-6 proposals, formal decisions, provenance plan | Host Agent checks the confirmed plan; execution uses shared patch and validation tools. |
| P11 | `ground_prompt` | Exact prompt spans, concept binding, reference resolution, action specificity | Uses shared proposal, operation, asset, execution, and validation state. |
| P12 | `refine` | Prompt-specific interaction specs, artifact-grounded default preview, Apply/Adjust/Regenerate/Correct/Reject, direct revision loop | Uses shared patch vocabulary without mandatory Aug; color and multi-object layout select specialized interactions. |

## Layer 1 Changes

**Old:** four independent core skills reconstructed differently named state and routed to four planners.

**New:** `skills/l1-svg-authoring-core/SKILL.md` reconstructs one canonical state and routes to planner `svg-authoring`.

Changes:

1. Adds explicit `entry_mode: create|analyze|ground_prompt|refine`.
2. Replaces case-specific state fields with `source_intent`, `artifact`, `analysis`, `proposals`, refine-mode `interaction_specs`/`preview_state`/`interaction_returns`, `decisions`, `augmented_intent`, `candidate_assets`, `authoring_bundle`, `pending_operations`, `execution`, and `acceptance`.
3. Defines deterministic invalidation for changed `fileId`, revision, prompt hash, and revision conflicts.
4. Does not silently choose between `ground_prompt` and `refine` when intent is ambiguous.
5. Routes every widget/tool result back through L1 before another phase.

## Layer 2 Changes

**Old:** P8 generation/control, P10 artifact-first instruction, P11 prompt grounding, and P12 recommendation/refinement used separate gap tables and overlapping operation logic.

**New:** `skills/l2-svg-authoring-planner/SKILL.md` uses mode-specific named chains and evidence-backed dependencies. The following is an illustrative dependency outline, not mandatory phases for every pass:

```text
entry -> intent -> scene grounding -> analysis -> proposals
      -> target/relation/operation decisions -> optional Aug review
      -> candidate materialization -> operation compilation
      -> typed execution -> validation -> artifact acceptance
```

Changes:

1. Mode profiles activate only the phases required by each entry mode.
2. Uses one canonical proposal schema with origin, source span, ranked targets, semantic operation, compiled operations, candidate bindings, status, and provenance.
3. Separates semantic operations from manager operations.
4. Partitions compiled operations into presentation, layout, and structure families.
5. Makes Aug optional: formal for `analyze`/`ground_prompt`, unnecessary for normal `refine`, and a creation brief/bundle for `create`.
6. Makes export policy-driven (`optional|required|disabled`) rather than an unconditional execution dependency.
7. Emits one semantic gap or one external executor per pass; it never names an L3 interaction implementation.

## Layer 3 Changes

**Old:** interaction and executor skills were duplicated under P8/P10/P11/P12 names.

**New:** capability-oriented skills are shared across modes:

| Skill | Responsibility |
| --- | --- |
| `l3-svg-mode-choice` | Explicit mode and creation-intent completion. |
| `l3-svg-object-grounding` | Stable target selection, relation endpoints, preserve constraints. |
| `l3-svg-proposal-review` | Formal proposal decisions or lightweight ranked recommendation inspection. |
| `l3-svg-operation-control` | Capability-filtered semantic parameters, preview, typed-operation confirmation. |
| `l3-svg-object-color-palette` | Stable-object color channels, artifact-aware swatches, and reversible presentation preview. |
| `l3-svg-collage-layout-board` | Live-scene multi-object layout, regions, guides, and host-owned transform drafts. |
| `l3-svg-candidate-selector` | Selection among already persisted same-session candidate assets. |
| `l3-svg-plan-review` | Provenance-aware confirmation of optional augmented intent. |
| `l3-svg-artifact-review` | Validation/revision review and final acceptance. |
| `l3-svg-revision-comparison` | Actual source/revised artifact comparison without mutation. |

Changes:

1. Interaction names describe user actions, not legacy cases.
2. Widget contracts remain renderer-independent and contain deterministic return/merge semantics.
3. Widgets never invoke image tools or mutate SVG.
4. L2 prepares a ready plan; exec-svg-authoring validates tool/capability pairing, revision, session identity, operation family, and result binding before direct invocation.
5. One external side effect is allowed per pass.

## Layer 4 Changes

**Old:** each legacy plugin had its own renderer skill and P-number-oriented frontend branches.

**New:** `l4-svg-authoring-renderer` renders all unified contracts on `artifact_canvas_widget`.

Changes:

1. Object interactions anchor to stable SVG object bounds.
2. Proposal annotations remain transient host overlays.
3. Canvas owns hit testing, preview, patch commit, revision refresh, and stale-state handling.
4. The iframe submits only declared structured values through `window.submitWidget` or `window.dismissWidget`.
5. Renderer cannot inspect raw SVG, invoke tools, or change return keys.

## Registry Changes

- `registry/planners.json`: one planner, one state vocabulary, one gap vocabulary, all allowed tools.
- `registry/widgets.json`: ten registered semantic designers mapped to actual interaction gaps, IAI destinations and domain merge targets.
- `registry/tools.json`: lifecycle, inspection, composition, image preparation, and typed patch families; instruction exporters have been removed.
- `registry/authoring-capabilities.json`: maps semantic capabilities to allowed preparation tools, result bindings, transparency requirements, and apply operations.

## External Tool Calling

Every external call follows:

```text
L1 state -> L2 instruction_ready -> direct registered executor/main_model
         -> actual result/failure -> L1 merge/invalidate
```

### Import or inspect an SVG

```json
{"executor":{"kind":"tool","name":"manage_svg_document"},"parameters":{"action":"import","file_id":"session-file-id","scene_kind_hint":"collage"}}
```

Subsequent grounding uses:

```json
{"executor":{"kind":"tool","name":"inspect_svg_scene"},"parameters":{"file_id":"session-file-id"}}
```

The result binds to `artifact.scene`, `artifact.revision`, and capabilities. Raw SVG never enters planner/widget state.

### Create a collage

1. L2 creates a P8-style plan of 3-6 independently editable visual objects.
2. L2 selects `initial_object_generation` and hands the plan to exec-svg-authoring, which calls `generate_image` once with `background: transparent` and `require_transparent_background: true`.
3. Result binds its real `fileId`, stable object id, and `primary|replacement_candidate` role to `candidate_assets`.
4. Repeat through L1 until at least two primaries exist and every successful primary has 1-3 distinct candidates.
5. Call `compose_svg_collage` once with `creation_mode: image_collage`, stable cutout objects, and complete `authoring_bundle`.
6. Adopt/inspect the generated SVG through `manage_svg_document` when required.

### Prepare a semantic candidate

1. L2 selects a capability from `authoring-capabilities.json`.
2. L2 names exactly one allowed tool such as `edit_image` or `restyle_image` and supplies `result_binding` with proposal/candidate/target identity.
3. L2 validates source `fileId`, capability/tool compatibility, session, and transparency requirement, then hands the plan to exec-svg-authoring to invoke the tool.
4. Tool output returns to L1 and is stored in `candidate_assets`.
5. Candidate selection occurs in a later pass; selection produces a typed structure operation but does not call the image tool again.

### Apply operations

Operations are homogeneous per call:

```json
{"executor":{"kind":"tool","name":"apply_svg_presentation"},"parameters":{"file_id":"svg-file-id","base_revision":3,"operations":[{"op":"update_text","object_id":"title","text":"New title"}]}}
```

```json
{"executor":{"kind":"tool","name":"apply_svg_layout"},"parameters":{"file_id":"svg-file-id","base_revision":4,"operations":[{"op":"set_order","object_id":"hero","direction":"front"}]}}
```

```json
{"executor":{"kind":"tool","name":"apply_svg_structure"},"parameters":{"file_id":"svg-file-id","base_revision":5,"operations":[{"op":"replace_cutout_asset","object_id":"hero","asset_file_id":"candidate-file-id"}]}}
```

Each success emits the next SVG attachment/revision. Remaining families execute in later passes against that new revision. Revision conflict returns to L1 and invalidates stale bindings.

### Validate and accept

After the final patch, L2 calls:

```json
{"executor":{"kind":"tool","name":"manage_svg_document"},"parameters":{"action":"validate","file_id":"svg-file-id"}}
```

Validation returns through L1, then `svg_artifact_review` collects acceptance. Patch success or export alone is never terminal.

### Export

- `analyze` and `ground_prompt` validate approved semantics in the Host Agent and execute through shared Host SVG tools without an export file/hash prerequisite.
- Exact approval, source revision, operation IDs and interaction history remain execution provenance.
- No instruction-file exporter is registered. Required or explicitly requested file exports return a capability failure to L1; optional export does not block execution.
- Shared tools still enforce session isolation, SVG safety, revision, object IDs and typed parameters; actual validation and acceptance remain required.

## Host Integration Changes

- `plugins/inflak-plugins.json` registers `inflak-svg-authoring` as ready.
- Runtime selection uses the canonical plugin id `inflak-svg-authoring`.
- `frontend/artifact-canvas.js` adds the plugin to Canvas and grounded-SVG routing while leaving it out of the P10/P11 direct-patch blocklist.
- `frontend/app.js` normalizes the short alias and leaves the composer visible so all four entry modes can supply intent.

## Compatibility and Removal Plan

This implementation is additive. After end-to-end parity is verified, legacy plugin IDs can become presets that set `entry_mode` and interaction depth before routing into this plugin. Only then should duplicated legacy skills/registries be deprecated. No legacy directory is removed in this change.
