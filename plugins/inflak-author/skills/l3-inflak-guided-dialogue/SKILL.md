---
name: l3-inflak-guided-dialogue
description: "Use when: Author selects one consequential plain-language collaboration question."
---

# L3 Designer — Guided Authoring Dialogue

## Layer & Role

Interaction Pathway only: L1 → L2 selection → L3 design → L4 render → L1. Validate `inflak-guided-dialogue` for `inflak-authoring`, `experience_definition_gap`, `clarify_human_ai_collaboration`, `G→I`; design registered `guided_authoring_dialogue` on `conversation_widget`. No new question/diagnosis, substitution, execution or rendering.

## Inputs

Read `planner_id`, `selected_widget_id`, `gap_type`, `interaction_goal`, `chain_id`, `iai_binding`, exact `expected_return`, `return_to`, actual runtime/local registry and grounded context. Consume one question, consequence, current understanding, actual options and supported recommendation. L2 supplies intent/evidence, not UI schema.

## Widget Profile Design

| Design aspect | Design guidance |
| --- | --- |
| Interaction purpose | Resolve the supplied material agency/trust/experience choice. |
| Presented information | One ordinary-language question, relevant consequence/context and visible recommendation. |
| Supported interaction | Select an actual option, use recommendation by action, or provide free text. |
| Feedback and constraints | Show response status and empty/conflicting-value feedback without inventing consent. |
| Submission and return | Exact answer, stable option IDs and explicit default-acceptance metadata. |
| Presentation intent | Low-effort conversational choice, not an implementation interview. |

## Essential Constraints

- Validate ID, skill/path, planner/gap/goal/edge, returns, artifacts/runtime. Preserve chain/reason/source/edge/target; G in sources, I target and allowed `state_update_target`. L1 maps only answered meanings at I into `intent_brief`.
- Fixed returns: `answer` string, `selected_options` array, `accepted_default` boolean. Require nonempty answer, valid selected option or explicitly chosen default; derive the boolean from actual action, not a checkbox. Free text overrides conflicting selection; default acceptance covers only its represented meaning.
- Reject multiple dependent questions, technical vocabulary or unsupported defaults. One primary submission; no approval checkbox/second confirmation. No HTML/CSS/JavaScript, local runtime paths, invented evidence, task calls or rendering.

## Output and Handoff

Use these eight local obligations; no success `handoff_type` or external schema read:

- Identity: nonempty exact `selected_widget_id`, instance `widget_id`, registry `widget_type`/`surface`, `planner_id`, contextual `purpose`, unchanged `interaction_goal`.
- `iai`: unchanged named `chain_id`, `gap_type`, binding `reason`, `maps_to_edge`, `source_nodes`, `target_node`; meaningful reason, source includes edge origin, destination equals target and allowed `state_update_target`; deterministic L1 `merge_strategy`, `next_planner_action: "re-enter Layer 1"`.
- `display`: grounded values, actual references, current state and unresolved status; no invented defaults/uploads/previews/outcomes.
- `controls`: unique nonempty `id`, supported `kind`, nonempty `label`/`purpose`, boolean `required`, nonempty declared `return_keys`, type/limit/source/edit `constraints`.
- `presentation.profile`: nonempty `archetype`/`summary`, nonempty `content` records (resolvable `source: "display.<path>"`, `role: primary|context|status`, meaningful `purpose`); interaction nonempty `actions`/`feedback`, submission nonempty `label`/`preconditions`, exact `return_mapping`; nonempty semantic `appearance` and `signature_features` list, not extra stages/implementation.
- `expected_return`: exactly L2 keys/types; `presentation.profile.interaction.submission.return_mapping` has exactly those keys with actual source/serialization and optional/empty handling. Derived metadata needs mappings, not artificial controls.
- `widget_requirements`: four nonempty string arrays `visible_information`, `required_controls`, `required_behavior`, `submission_requirements`; minimal meaningful obligations matching the profile, not extra gates.
- `safety`: `allow_html: false`, `allow_script: false`; optional runtime only available approved capabilities/pinned libraries; optional reference assets only plugin-relative design-time references/principles, never runtime assets.

Validate sources, constraints and exact mappings; send to `l4-inflak-author-renderer`. Invalid selection or missing indispensable evidence/capability returns `handoff_type: selected_widget_invalid`, copied `planner_id`, `selected_widget_id`, `gap_type`, nonempty deterministic `validation_errors`, `return_to: l1-inflak-author-core`; bypass L4 without substitution or re-diagnosis.

## Workflow End Authority

Only L1 owns canonical merging and Completion or `decision: end`. Every result/failure re-enters `l1-inflak-author-core`; answering is nonterminal.
