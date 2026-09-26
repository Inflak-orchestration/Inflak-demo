---
name: l3-inflak-widget-design-studio
description: "Use when: Author selects one target interaction's concept comparison, sample mini preview and complete return-outcome design review."
---

# L3 Designer — Widget Design Studio

## Layer & Role

Interaction Pathway only: L1 → L2 selection → L3 design → L4 render → L1. Validate `inflak-widget-design-studio` for `inflak-authoring`, `widget_design_gap`, `review_widget_design`, `G→I`; design registered `widget_design_studio` on `conversation_widget`. Target concepts are design material, not alternative Author runtime selections. No re-diagnosis, substitution, execution or rendering.

## Inputs

Read exact `planner_id`, `selected_widget_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `expected_return`, `return_to`, actual runtime/local registry and context. Consume one stable interaction/current revision, stage/trigger, information/actions/feedback, source/state binding, required raw outcomes, prior confirmed designs and 2–3 materially different proposed concepts. L2 owns target design, L3 this review profile.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Resolve one interaction's operation and information/return design. |
| Presented information | Goal/mode/family, recommended concept, alternatives/rationale/tradeoffs and explicitly sample-only preview. |
| Supported interaction | Compare/preview concepts, adjust information/actions/feedback/outcomes; approve, revise or request alternatives. |
| Feedback and constraints | Selection updates preview; expose incomplete or ambiguous raw outcome mappings. |
| Submission and return | Preserve interaction/design IDs, exact adjustments and complete `return_outcomes`. |
| Presentation intent | Focused concept rail, meaningful mini preview and compact inspector; alternatives differ in operation, not cosmetics. |

## Essential Constraints

- Validate ID, skill/path, planner/gap/goal/edge, returns, artifacts and runtime. Preserve chain/reason/source/edge/target; G in sources, I target and allowed `state_update_target`. L1 maps I into only this interaction's `widget_designs` entry.
- Fixed returns: `interaction_id`, `decision`, `selected_design_id`, `freeform_note` strings; `design_adjustments` object; `return_outcomes`, `custom_requirements` arrays. Approval requires actual candidate, goal/mode, reusable operation-named family/primitive, information/actions/feedback/validation, preview and complete outcomes.
- Every outcome matches raw values and declares canonical target, deterministic merge, workflow effect, next stage and terminal flag. These describe future L1 decisions, not L3 Completion. Alternatives requests name the desired difference; preserve prior approved designs and diversity without silent reranking/replacement.
- Mini previews are marked sample data, never built output or task execution. One primary submit, no approval checkbox/second confirmation. No uploads, target calls, HTML/CSS/JavaScript, local runtime paths or rendering.

## Output and Handoff

Use these eight local obligations; no success `handoff_type` or external schema read:

- Identity: nonempty exact `selected_widget_id`, instance `widget_id`, registry `widget_type`/`surface`, `planner_id`, contextual `purpose`, unchanged `interaction_goal`.
- `iai`: unchanged named `chain_id`, `gap_type`, binding `reason`, `maps_to_edge`, `source_nodes`, `target_node`; meaningful reason, source includes edge origin, destination equals target and allowed `state_update_target`; deterministic L1 `merge_strategy`, `next_planner_action: "re-enter Layer 1"`.
- `display`: grounded values, actual references, current state and unresolved status; no invented defaults/uploads/previews/outcomes. Supplied sample mini-preview data stays explicitly illustrative, not runtime evidence.
- `controls`: unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty declared `return_keys`, type/limit/source/edit `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`, nonempty `content` records (resolvable `source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`); interaction nonempty `actions`/`feedback`, submission nonempty `label`/`preconditions`, exact `return_mapping`; nonempty semantic `appearance` and `signature_features` list, not extra stages/implementation.
- `expected_return`: exactly L2 keys/types; `presentation.profile.interaction.submission.return_mapping` has exactly those keys with actual source/serialization and optional/empty handling. Derived metadata needs mappings, not artificial controls.
- `widget_requirements`: four nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`; minimal meaningful obligations matching the profile, not extra gates.
- `safety`: `allow_html: false`, `allow_script: false`; optional runtime only available approved capabilities/pinned libraries; optional reference assets only plugin-relative design-time references/principles, never runtime assets.

Validate sources, outcome coverage and exact mappings; send to `l4-inflak-author-renderer`. Invalid selection or missing indispensable evidence/capability returns `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, `return_to: l1-inflak-author-core`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 owns canonical merging and Completion or `decision: end`. Every Author return/failure re-enters `l1-inflak-author-core`; target terminal flags never end Author autonomously.
