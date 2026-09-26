---
name: l3-inflak-experience-preview
description: "Use when: Author selects current-revision review of complete progressive design and realistic acceptance cases."
---

# L3 Designer — Experience Blueprint Preview

## Layer & Role

Interaction Pathway only: L1 → L2 selection → L3 design → L4 render → L1. Validate `inflak-experience-preview` for `inflak-authoring`, `experience_review_gap`, `review_experience_blueprint`, `G→I`; design registered `experience_blueprint_preview` on `conversation_widget`. No compilation, publication, diagnosis, substitution or rendering.

## Inputs

Read `planner_id`, `selected_widget_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, exact `expected_return`, `return_to`, runtime/local registry and context. Require complete current-revision blueprint, actual phase approvals/history, stage/artifact/state decisions, widget designs, final presentation, exceptions/resources/assumptions and realistic acceptance cases. Reject stale, unreviewed or implementation-only context.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Approve/revise exact experience revision and coverage before compilation. |
| Presented information | Actual phase coverage, key agency decisions, workflow path, interaction diversity, final artifact/cases. |
| Supported interaction | Inspect collapsed phase details, explicitly resolve assumptions, approve or request targeted changes. |
| Feedback and constraints | Show missing/stale coverage and blocking assumptions; never preselect approval. |
| Submission and return | Preserve exact displayed revision, decision, explicit accepted assumptions and changes. |
| Presentation intent | Compact coverage summary with separately disclosed details, not a first-time blueprint wall. |

## Essential Constraints

- Validate ID, skill/path, planner/gap/goal/edge, returns, artifacts and runtime. Preserve chain/reason/source/edge/target; G is in sources, I equals target and allowed `state_update_target`. L1 maps I to `blueprint_approval` or change/invalidation evidence.
- Fixed returns: `decision` string, `change_requests` array, `accepted_assumptions` array, `approved_revision` integer. Approval requires exact displayed revision, complete current approvals for frame/every stage/artifact flow/every design, approved realistic cases and no unresolved blocking assumption. Request changes requires a nonempty targeted change.
- Assumption acceptance must be explicit; model inference, control presence or disclosure viewing is not approval. Use substantive choice/action controls, never confirmation checkboxes. This approval is neither build approval nor publication consent.
- One primary submit, no second confirmation. Do not derive a replacement target spec, compile, publish, invent successful coverage or emit HTML/CSS/JavaScript/local runtime paths.

## Output and Handoff

Use these eight local obligations; no success `handoff_type` or external schema read:

- Identity: nonempty `selected_widget_id` (exact selection), `widget_id` (instance), registry `widget_type`/`surface`, `planner_id`, contextual `purpose`, unchanged `interaction_goal`.
- `iai`: copy named `chain_id`, `gap_type`, binding `reason`, `maps_to_edge`, `source_nodes`, `target_node` unchanged; require meaningful reason, edge source in sources and destination equal to target and allowed `state_update_target`. Include deterministic L1 `merge_strategy`, `next_planner_action: "re-enter Layer 1"`.
- `display`: grounded task values, actual source references, current values and unresolved status; no invented defaults, uploads, previews or outcomes.
- `controls`: unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty declared `return_keys`, `constraints` for types/limits/source/edit rules.
- `presentation.profile`: nonempty `archetype`/`summary`; nonempty `content` records with resolvable `source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`; `interaction` with nonempty `actions`/`feedback` and `submission` (nonempty `label`, nonempty `preconditions`, exact `return_mapping`); nonempty semantic `appearance` and `signature_features` list, not extra stages or implementation.
- `expected_return`: exactly L2 keys/types; `presentation.profile.interaction.submission.return_mapping` has exactly those keys, each naming actual source and serialization, preserving optional/empty semantics. Map derived metadata without artificial controls.
- `widget_requirements`: four nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`; minimal meaningful obligations consistent with the profile, not extra gates.
- `safety`: `allow_html: false`, `allow_script: false`. Optional `runtime` only for available approved capabilities/pinned libraries; optional `reference_assets` are plugin-relative design-time references/principles, never runtime assets.

Validate evidence, revision, controls and exact mappings, then hand to `l4-inflak-author-renderer`. Invalid selection or missing indispensable evidence/capability returns `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, `return_to: l1-inflak-author-core`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 owns canonical state/revision invalidation and Completion or `decision: end`. Every return/failure re-enters `l1-inflak-author-core`; review approval remains nonterminal.
