---
name: l3-pN13-intention-basic-widget
description: "Use when: P13 selects conversational next-action choices or one discriminating intention question."
---

# L3 Designer — P13 Intention Basic Widget

## Layer & Role

Interaction Pathway only: L1 → L2 selection → L3 design → L4 render → L1. Validate exact `p13-intention-basic-widget` for `pN13-proactive-intent-recommendation`; design registered `adaptive_basic_widget` on `inline_widget`. No new diagnosis, substitution, task execution or rendering.

## Inputs

Read `planner_id`, `selected_widget_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, `expected_return`, `display_context`, runtime and `return_to`. Resolve the local registry entry. Read actual possibilities/source evidence, unresolved intent and substantive user limits; L2 need not predesign controls.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Resolve exactly the supplied intent selection or question, not implementation. |
| Presented information | Ground 2–5 `{recommendation_id,label,next_action}` possibilities when supplied; keep private ranking/confidence/analysis hidden. |
| Supported interaction | Derive minimal buttons, single choice, multiple choice, text input, slider or toggle composition for exact typed returns. |
| Feedback and constraints | Show unset/selected status and validation; IDs never come from inferred array rank. |
| Submission and return | Map selection and optional freeform intention exactly; derived decisions need no artificial field. |
| Presentation intent | Concise conversational choice, not an inspector or capability catalog. |

## Essential Constraints

- Accept only `intent_disambiguation_gap` or `intention_presentation_gap`, with `present_confirmed_intention` on `G→I`. Do not reinterpret either as implementation input.
- Validate ID, skill/path, planner/gap/goal/edge, all returns, artifacts, destination and actual runtime. Preserve `chain_id`, binding `reason`, source/edge/target; G→I has G in sources and I as target and allowed `state_update_target`. L1 maps I to disambiguation/user decision.
- `planner_declared` permits exact typed basic fields/shapes, not arbitrary code or unsupported operations. Ground options/defaults/bounds; substantive choices remain unset. Freeform intent overrides a conflicting selection; authorization covers only actual scope.
- One primary submit; no arbitrary control count, approval checkbox or second confirmation. No HTML/CSS/JavaScript, local runtime path, invented upload, rendering or task execution.

## Output and Handoff

Use these eight local obligations; no success `handoff_type` or external schema read:

- Identity: nonempty exact `selected_widget_id`, instance `widget_id`, registry `widget_type`/`surface`, `planner_id`, contextual `purpose`, unchanged `interaction_goal`.
- `iai`: unchanged named `chain_id`, `gap_type`, binding `reason`, `maps_to_edge`, `source_nodes`, `target_node`; meaningful reason, edge source in sources, destination equal to target and allowed `state_update_target`; deterministic L1 `merge_strategy`, `next_planner_action: "re-enter Layer 1"`.
- `display`: grounded values, actual references, current values and unresolved status; no invented defaults/evidence/uploads/previews/outcomes.
- `controls`: unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty declared `return_keys`, typed limits/source/edit `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`, nonempty `content` records (resolvable `source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`); interaction nonempty `actions`/`feedback`, `submission` with nonempty `label`/`preconditions` and exact `return_mapping`; nonempty semantic `appearance` and `signature_features` list, not implementation/extra stages.
- `expected_return`: exactly L2 keys/types; `presentation.profile.interaction.submission.return_mapping` has exactly those keys with actual source/serialization, preserving optional/empty semantics; derived fields need mappings, not artificial controls.
- `widget_requirements`: four nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`; meaningful minimal obligations consistent with the profile, not extra gates.
- `safety`: `allow_html: false`, `allow_script: false`. Optional `runtime`: available approved capabilities/pinned libraries only; optional `reference_assets`: plugin-relative design-time references/principles, never runtime assets.

Validate references, controls, mappings and producible values; send to `l4-pN13-widget-renderer`. Invalid selection or missing indispensable evidence/capability returns `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, `return_to: l1-pN13-core-module`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 owns state/merging and Completion or `decision: end`. Every submission/dismissal/failure re-enters `l1-pN13-core-module`; selection is nonterminal.