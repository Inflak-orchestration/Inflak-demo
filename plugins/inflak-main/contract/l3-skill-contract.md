# L3 Designer Skill Contract

Authoring-only documentation for generating or reviewing reusable and task-specific L3 Designer widget skills. This contract is not a callable skill, is not part of SDK skill discovery, and is not a runtime prerequisite. Operational L3 skills define their complete handoff locally, without requiring this document or another contract document at runtime.

## Layer & Role

Defines profile authoring guidance for the six reusable main L3 widget skills and generated L3 skills. In the Interaction Pathway, L2 Planner diagnoses one gap and selects one registry entry; L3 Designer validates that exact selection and designs its semantic interaction contract; L4 Renderer implements and renders it. L1 Router owns canonical state and Completion. Cross-layer ownership and all four pathways (Interaction Pathway, Execution Pathway, Host Agent Return, and Completion) are described in [CONTRACT.md](CONTRACT.md) for authoring/static review only; operational fields, validation, and handoff rules belong in the skills themselves.

**Skill document versus runtime contract.** A skill document teaches reusable design rules, not a prefilled task or fixed UI. Examples are optional; neither JSON examples nor case-specific examples are required. At runtime, however, L3 must produce the complete canonical contract; concise documentation never permits omitted runtime fields or an older reduced shape.

Generated skills MUST include the self-contained compact handoff below in their own `Output and Handoff`, alongside local primitive guidance and validation. Do not replace it with external schema references or a runtime document-loading instruction. Emit one Markdown document whose frontmatter `name` equals the selected entry's `skill` and directory name and whose `description` identifies its selection and gap scope. This detailed contract itself is pure Markdown without frontmatter, not a generated skill.

Main retains six concrete conversation-widget entries and matching reusable skills: `settings-form`, `option-selector`, `content-editor`, `structure-editor`, `canvas-editor`, and `parameter-controls`. Their descriptions independently state applicability and mismatch conditions so the exact selected skill can validate the handoff without rerouting. Do not introduce new widget capabilities or a runtime dependency on this contract.

## Required Sections

- `Layer & Role`
- `Inputs`
- `Widget Profile Design`
- `Essential Constraints`
- `Output and Handoff`
- `Workflow End Authority`

These are semantic blocks, not mandatory literal headings for legacy skills. `Layer & Role` states primitive applicability, capability boundaries, and mismatch conditions; `Inputs` states the selected handoff, registry entry, evidence, and IAI interpretation. `Widget Profile Design` teaches the reusable method below (a compact design table is optional). `Essential Constraints` makes selection, evidence, provenance, return, and validation invariants explicit. `Output and Handoff` supplies complete local fields, validation, success, and failure rules without an external read. `Workflow End Authority` reserves canonical merging, subsequent routing, and completion to L1. A heading alone does not satisfy a block.

## Inputs

| Source | Required context |
| --- | --- |
| L2 planner handoff | `planner_id`, `selected_widget_id`, `gap_type`, registered `interaction_goal`, `chain_id`, `iai_binding`, `expected_return`, task/artifact context, runtime context, and exact L1 `return_to`. |
| Selected registry entry | Resolve `selected_registry_entry` by exact ID from the same plugin `registry/widgets.json` used by L2; retain skill/path, type, surface, modality, eligibility, return coverage, and runtime declarations. |
| Authoring context, when supplied | `planner_slug`, `return_to_l1`, `gap`, and `realization_definition`; align planner, return target, gap goal, display fields, and typed `return_shape` with the handoff. |
| Task evidence | Intent, source material, current values, known or delegated decisions, unresolved constraints, provenance, and actual capability/library availability. |

L2 supplies diagnosis and required returns, not a pre-designed UI. L3 derives labels, controls, grouping, feedback, and design rules from intent and evidence within the selected primitive. Realization material does not change eligibility; runtime declarations are metadata, not executable code or parent-DOM access.

Carry supplied `display_context` candidates, fragments, profiles, actual artifacts, warnings, and defaults into grounded design rather than inventing replacements. Optional `target_tool` only informs parameter-collection semantics for that registered executor; it never selects a different widget or authorizes execution during widget realization. Preserve applicable `chain_id`, order/dependency, and exact return target from the L2 request. Canonical planner fields and conditional input rules are detailed in [l2-skill-contract.md](l2-skill-contract.md), for authoring review only.

## Widget Profile Authoring Method

Answer **why the user interacts, what they need to understand, what they can do, and what their return resolves**. Teach these six design steps after selected-entry validation; they are authoring guidance, not mandatory user stages or a runtime guide-loading sequence.

1. **Purpose:** specialize `purpose` and profile `summary` around the supplied gap and expected contribution; keep the registered `interaction_goal` and L2 diagnosis unchanged.
2. **Information:** place relevant grounded values and source references in `display`; distinguish read-only evidence, editable material, and unresolved state. Assign each profile content item a resolvable source, role, and purpose.
3. **Operations:** choose only supported controls needed for the intent; derive meaningful labels, requiredness, constraints, and feedback. Preserve substantive user limits without making missing domain decisions for them.
4. **Return:** map current values and derived evidence to exactly `expected_return`; specify source, serialization, types, optional/empty handling, and applicable stable IDs or provenance. Derived fields do not require artificial controls.
5. **Profile:** organize information hierarchy, actions, feedback, submission, appearance, and distinguishing behavior into a coherent design. Record minimal grounded acceptance requirements, not a copy of all task data.
6. **Completeness:** verify references, controls, mappings, validity, and requirements agree. Resolve design choices in L3; return missing indispensable evidence or capabilities to L1 rather than asking L4 to invent semantics.

Do not mandate arbitrary numbers of controls, content sections, features, or workflow stages, or expose every possible control. Nonemptiness requirements do not justify extra behavior: describe the minimal relevant operation and validity condition. If no special behavior is needed, do not invent steps merely to fill the shape.

## Essential Constraints

- Registry declarations are factual capability boundaries: preserve type, surface, modality, eligibility, return coverage, capabilities, and library names; never broaden them or search, rank, reroute to, or substitute another widget.
- Preserve L2's named chain, reason, gap, source/edge/target, goal, and supplied problem/cause. A gap is one missing transfer and destination deficit; pending input is not existing evidence. Never repair provenance by inventing a diagnosis.
- Ground domain facts, defaults, actual candidates, artifacts, uploads, revisions, and source references in evidence. Unknown values remain unresolved; missing generated outcomes, previews, file IDs, or results must not be invented.
- Stylistic and interaction-design decisions remain agent-owned within capability and user constraints; missing facts do not require L2 to author controls or justify every label and hierarchy choice.
- Preserve applicable artifact, coordinate, mask, and upload protocols exactly; require only evidence and completed artifacts needed by the declared return. Do not invent a universal artifact count or interaction sequence.
- Use one primary submit action for current values, with no approval checkbox or second confirmation step. Dismissal uses the existing renderer envelope, not an invented return flag; optional free text exists only if declared.
- Produce no HTML, CSS, JavaScript, iframe code, scripts, event handlers, CDN URLs, remote implementation assets, rendering calls, or task-executor calls. L4 Renderer chooses accessible implementation without changing information, operations, or return semantics.
- `widget_type` names the registered reusable user operation, not a task or tool. Selection identity is preserved, not a source of new UI semantics. Do not prescribe next stages, final responses, or completion decisions.
- Preserve exact declared return keys/types and applicable fixed, planner-declared, or agent-interpreted policies in [CONTRACT.md](CONTRACT.md). Map every required return to its actual source and serialization; never add undeclared fields or capabilities. Agent interpretation does not waive planner-required fields. Artifact mutation remains a separate executor boundary with a validated input schema.
- Use stable session artifact identities such as `fileId`; a filename, local path, or display URL is not identity. In main, drawing and mask editing remain local to the dialogue iframe. Inpainting is transparent-edit/opaque-preserve. Preserve actual source alignment and never invent runtime outputs.

## Validation

Require local validation of exact selection ID, registry skill/path, planner/gap/goal/edge eligibility, return coverage, artifact support, allowed state destination, and available capabilities/libraries. All applicable checks must pass. Preserve the named chain and meaningful reason; the edge source must be in `source_nodes`, and its destination must equal `target_node` and `state_update_target`. Before L4, check grounded resolvable references, unique control IDs, compatible constraints, exact return mappings, producible typed values, and agreement with requirements. A heading or external reference is insufficient; keep these checks local without prescribing fixed cases.

`compatible_planners`, gap categories, goals, edges, return policies, artifact types, and runtime constraints are validated against the selected entry, not used to find a replacement. An explicitly supported semantic parent goal is allowed only as declared; never guess synonyms or choose a different destination from the widget's supported list. For `X→Y`, source evidence may still be pending at X, but neither its absence nor a field's optional storage status licenses a fabricated Y state. Missing or inconsistent location, or missing indispensable evidence/capability, fails immediately without rendering, re-diagnosis, or L4 entry.

L4 validates success using its own inline `Inputs` corresponding to the selected L3's local `Output and Handoff`. Neither layer requires another document read or a new renderer-tool argument. L2 routing failures return directly to L1; L3 receives only a selected-widget request and returns its own validation failures to the exact L1 without false readiness or a near-match selection.

## Output and Handoff

Include these eight bullets in every generated skill's local handoff definition, not a link to this guide:

- Identity: nonempty strings `selected_widget_id` (exact L2 selection), `widget_id` (instance identity), `widget_type` and `surface` (exact registry values), `planner_id` (owning L2), `purpose` (contextual), and unchanged `interaction_goal`.
- `iai`: copy L2's `chain_id`, `gap_type`, and binding `reason`, `maps_to_edge`, `source_nodes`, `target_node` unchanged; require a named chain and meaningful reason, edge source in `source_nodes`, and destination equal to `target_node` and allowed `state_update_target`. Include a deterministic `merge_strategy` for L1 and `next_planner_action: "re-enter Layer 1"`.
- `display`: grounded task values, source references, current values, and unresolved status; no invented evidence, defaults, uploads, previews, or outcomes.
- `controls`: array of records with `id`, `kind`, `label`, `purpose`, `required`, `return_keys`, `constraints`; IDs are unique/nonempty, kinds supported, labels/purposes nonempty, `required` boolean, and `return_keys` a nonempty list of declared return keys. State applicable limits, types, and source/edit rules in `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`, a nonempty `content` array of records (`source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`); every source resolves. Include `interaction` with nonempty `actions`/`feedback` lists and `submission` (nonempty `label`, nonempty `preconditions`, `return_mapping`), plus nonempty semantic `appearance` and a nonempty `signature_features` list describing relevant behavior, not implementation or invented steps.
- `expected_return`: deterministic object with exactly L2's keys and types; `presentation.profile.interaction.submission.return_mapping` has exactly the same keys, each specifying its actual source and serialization. Preserve declared optional/empty semantics; derived returns need mappings, not artificial controls.
- `widget_requirements`: four nonempty string arrays, `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`; state minimal meaningful obligations consistent with the profile, not additional interaction gates.
- `safety`: `allow_html: false`, `allow_script: false`. Optional `runtime` declares only available approved capabilities and version-pinned libraries; optional `reference_assets` are plugin-relative design-time references and extracted principles only, never runtime assets.

Teach success as a complete validated contract to the actual L4 renderer (`l4-widget-renderer` in main), without adding a success `handoff_type`. A profile summary or authored skill document is never the runtime payload. On invalid selection or missing indispensable evidence/capability, return `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, a nonempty deterministic `validation_errors` array identifying failed checks, and `return_to` set to the supplied exact plugin L1 (`l1-router` in main); no substitution, re-diagnosis, or L4 entry.

## Workflow End Authority

Only L1 Router owns canonical workflow state, maps and merges returned values at the preserved destination, and decides Completion or emits `decision: end`. L3 Designer's semantic contract is nonterminal: success proceeds to L4 Renderer, and validation failure returns immediately to the exact plugin L1 (`l1-router` in main). Every widget return or renderer failure also returns to L1, which reconstructs current state and chooses the next planner route, Host Agent Return, or Completion.
