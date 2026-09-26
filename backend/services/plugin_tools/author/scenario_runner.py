"""Run and persist executable validation scenarios for installed inflak plugins."""

from __future__ import annotations

import asyncio
import contextlib
import json
import os
import uuid
from pathlib import Path
from typing import Any

from backend.services import chat_store
from backend.services.inflak_plugins import (
    canonical_runtime_tool_name,
    plugin_dir,
    plugin_entry,
    plugin_runtime_entry_skill,
)


PROJECT_DIR = Path(__file__).resolve().parents[4]
SCENARIO_RUNS_DIR = PROJECT_DIR / "data" / "plugin_scenarios"
MAX_SCENARIO_WIDGET_STEPS = 16


class PluginScenarioError(ValueError):
    """Raised when a validation scenario is missing or malformed."""


def _now() -> str:
    return chat_store.now_iso()


def _safe_id(value: str, fallback: str) -> str:
    cleaned = "".join(character if character.isalnum() or character in "_-" else "_" for character in value.strip())
    return cleaned.strip("_") or fallback


def _run_root(plugin_id: str, run_id: str) -> Path:
    return SCENARIO_RUNS_DIR / _safe_id(plugin_id, "plugin") / _safe_id(run_id, "run")


def _run_path(plugin_id: str, run_id: str) -> Path:
    return _run_root(plugin_id, run_id) / "run.json"


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _scenario_report(run: dict[str, Any]) -> str:
    evaluation = run.get("evaluation") if isinstance(run.get("evaluation"), dict) else {}
    checks = evaluation.get("checks") if isinstance(evaluation.get("checks"), dict) else {}
    lines = [
        f"# Scenario Report: {run.get('plugin_id')}",
        "",
        f"- Run: `{run.get('run_id')}`",
        f"- Case: `{run.get('case', {}).get('id')}` — {run.get('case', {}).get('title')}",
        f"- Mode: `{run.get('mode')}`",
        f"- Status: `{run.get('status')}`",
        f"- Session: `{run.get('session_id')}`",
        f"- Started: {run.get('started_at')}",
        f"- Finished: {run.get('finished_at') or 'in progress'}",
        "",
        "## Assertions",
        "",
    ]
    if checks:
        lines.extend(f"- {'PASS' if passed else 'FAIL'} — `{name}`" for name, passed in checks.items())
    else:
        lines.append("- Pending")
    issues = evaluation.get("issues") or []
    lines.extend(["", "## Failure Handoff", ""])
    if issues:
        lines.append(f"- Failed phase: `{evaluation.get('failed_phase') or 'unknown'}`")
        lines.extend(f"- `{issue}`" for issue in issues)
        lines.append("- Return this case and trace to inflak Author, revise the failed phase, regenerate, and rerun.")
    else:
        lines.append("- No failed assertions.")
    lines.extend([
        "",
        "## Evidence",
        "",
        f"- Skill events: {len([item for item in run.get('trace') or [] if item.get('type') == 'skill_event'])}",
        f"- Widget contracts: {len(run.get('widget_contracts') or [])}",
        f"- Widget returns: {len(run.get('widget_returns') or [])}",
        f"- Tool results: {len(run.get('tool_results') or [])}",
        f"- Final artifacts: {len(run.get('artifacts') or [])}",
        "",
    ])
    return "\n".join(lines)


def _save_run(run: dict[str, Any]) -> None:
    path = _run_path(str(run["plugin_id"]), str(run["run_id"]))
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_text(json.dumps(run, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary, path)
        _write_json(path.parent / "scenario-input.json", run.get("case") or {})
        _write_json(path.parent / "skill-trace.json", run.get("trace") or [])
        _write_json(path.parent / "widget-contracts.json", run.get("widget_contracts") or [])
        _write_json(path.parent / "widget-returns.json", run.get("widget_returns") or [])
        _write_json(path.parent / "tool-results.json", run.get("tool_results") or [])
        _write_json(path.parent / "final-artifacts.json", run.get("artifacts") or [])
        _write_json(path.parent / "assertions.json", run.get("evaluation") or {})
        (path.parent / "SCENARIO-REPORT.md").write_text(_scenario_report(run), encoding="utf-8")
    finally:
        temporary.unlink(missing_ok=True)


def load_run(plugin_id: str, run_id: str) -> dict[str, Any]:
    path = _run_path(plugin_id, run_id)
    if not path.is_file():
        raise FileNotFoundError(run_id)
    return json.loads(path.read_text(encoding="utf-8"))


def refresh_run(plugin_id: str, run_id: str) -> dict[str, Any]:
    run = load_run(plugin_id, run_id)
    _session_evidence(run)
    if run.get("status") in {"running", "waiting_for_user"}:
        run["evaluation"] = evaluate_run(run)
        run.setdefault("debug_handoff", {})["failed_phase"] = run["evaluation"].get("failed_phase")
    _save_run(run)
    return run


def report_path(plugin_id: str, run_id: str) -> Path:
    load_run(plugin_id, run_id)
    path = _run_root(plugin_id, run_id) / "SCENARIO-REPORT.md"
    if not path.is_file():
        raise FileNotFoundError(run_id)
    return path


def list_runs(plugin_id: str) -> list[dict[str, Any]]:
    directory = SCENARIO_RUNS_DIR / _safe_id(plugin_id, "plugin")
    if not directory.is_dir():
        return []
    runs = []
    for path in directory.glob("*/run.json"):
        try:
            run = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        runs.append({
            "run_id": run.get("run_id"),
            "plugin_id": run.get("plugin_id"),
            "case_id": run.get("case", {}).get("id"),
            "title": run.get("case", {}).get("title"),
            "mode": run.get("mode"),
            "status": run.get("status"),
            "session_id": run.get("session_id"),
            "started_at": run.get("started_at"),
            "finished_at": run.get("finished_at"),
            "passed": run.get("evaluation", {}).get("passed"),
        })
    return sorted(runs, key=lambda item: item.get("started_at") or "", reverse=True)


def _session_evidence(run: dict[str, Any]) -> None:
    session_id = str(run.get("session_id") or "")
    if not session_id:
        return
    try:
        messages = chat_store.get_messages(session_id)
    except (FileNotFoundError, ValueError):
        return
    run["widget_returns"] = [
        message.get("metadata", {}).get("result") or {}
        for message in messages
        if message.get("role") == "widget_return"
    ]
    started_tools: dict[str, str] = {}
    for message in messages:
        metadata = message.get("metadata") if isinstance(message.get("metadata"), dict) else {}
        if message.get("role") != "tool_event" or metadata.get("eventType") != "tool.execution_start":
            continue
        data = (metadata.get("event") or {}).get("data")
        if not isinstance(data, dict):
            continue
        call_id = str(data.get("tool_call_id") or data.get("toolCallId") or "")
        raw_name = str(data.get("tool_name") or data.get("toolName") or data.get("mcp_tool_name") or "")
        if call_id and raw_name:
            started_tools[call_id] = canonical_runtime_tool_name(raw_name)

    run["tool_results"] = []
    for message in messages:
        metadata = message.get("metadata") if isinstance(message.get("metadata"), dict) else {}
        if message.get("role") != "tool_event" or metadata.get("eventType") != "tool.execution_complete":
            continue
        event = metadata.get("event") if isinstance(metadata.get("event"), dict) else {}
        data = event.get("data") if isinstance(event.get("data"), dict) else {}
        call_id = str(data.get("tool_call_id") or data.get("toolCallId") or "")
        raw_name = str(data.get("tool_name") or data.get("toolName") or "")
        run["tool_results"].append({
            "event_type": metadata.get("eventType"),
            "tool_name": canonical_runtime_tool_name(raw_name) if raw_name else started_tools.get(call_id),
            "content": message.get("content"),
            "event": event,
        })
    artifacts: list[dict[str, Any]] = []
    for result in run["tool_results"]:
        data = result.get("event", {}).get("data")
        payload = data.get("result") if isinstance(data, dict) else None
        if not isinstance(payload, dict):
            continue
        structured_content = payload.get("structured_content") or payload.get("structuredContent")
        if isinstance(structured_content, dict):
            payload = structured_content
        for key in ("artifact", "preview_artifact_ref"):
            if isinstance(payload.get(key), dict):
                artifacts.append(payload[key])
        if isinstance(payload.get("artifacts"), list):
            artifacts.extend(item for item in payload["artifacts"] if isinstance(item, dict))
    run["artifacts"] = artifacts


def installed_cases(plugin_id: str) -> list[dict[str, Any]]:
    root = plugin_dir(plugin_id, require_ready=False)
    path = root / "tests" / "scenarios.json"
    if not path.is_file():
        raise PluginScenarioError(f"Plugin '{plugin_id}' has no tests/scenarios.json.")
    try:
        cases = json.loads(path.read_text(encoding="utf-8"))["cases"]
    except (KeyError, TypeError, json.JSONDecodeError) as error:
        raise PluginScenarioError(f"Plugin '{plugin_id}' has invalid scenario definitions: {error}") from error
    if not isinstance(cases, list) or not cases:
        raise PluginScenarioError(f"Plugin '{plugin_id}' requires at least one validation case.")
    return cases


def select_case(plugin_id: str, case_id: str | None = None) -> dict[str, Any]:
    cases = installed_cases(plugin_id)
    if case_id:
        case = next((item for item in cases if str(item.get("id")) == case_id), None)
        if case is None:
            raise PluginScenarioError(f"Unknown validation case '{case_id}' for plugin '{plugin_id}'.")
        return dict(case)
    return dict(cases[0])


def _compact_event(event: dict[str, Any]) -> dict[str, Any]:
    event_type = str(event.get("type") or "")
    if event_type == "skill_event":
        return {
            "type": event_type,
            "category": event.get("category"),
            "name": event.get("name"),
            "layer": event.get("layer"),
            "status": event.get("status"),
            "success": event.get("success"),
            "tool_name": event.get("toolName"),
            "error": event.get("error"),
            "turn_id": event.get("turnId"),
        }
    if event_type == "widget_render":
        widget = event.get("widget") if isinstance(event.get("widget"), dict) else {}
        return {
            "type": event_type,
            "widget_id": event.get("widgetId") or widget.get("widget_id"),
            "selected_widget_id": widget.get("selected_widget_id"),
            "widget_type": widget.get("semantic_widget_type") or widget.get("widget_type"),
            "planner_id": widget.get("planner_id"),
            "interaction_goal": widget.get("interaction_goal"),
            "expected_return": widget.get("expected_return") or {},
        }
    if event_type == "workspace_open":
        workspace = event.get("workspace") if isinstance(event.get("workspace"), dict) else {}
        return {
            "type": event_type,
            "workspace_id": event.get("workspaceId") or workspace.get("workspace_id"),
            "workspace_type": workspace.get("workspace_type"),
            "planner_id": workspace.get("planner_id"),
            "interaction_goal": workspace.get("interaction_goal"),
        }
    if event_type == "user_input_request":
        return {
            "type": event_type,
            "request_id": event.get("requestId"),
            "question": event.get("question"),
        }
    if event_type in {"assistant_complete", "error", "session_idle", "artifact_generated", "image_generated"}:
        return {
            "type": event_type,
            "content": str(event.get("content") or event.get("message") or "")[:1000],
            "artifact_type": event.get("artifactType"),
            "attachment": event.get("attachment"),
        }
    return {"type": event_type}


def evaluate_run(run: dict[str, Any]) -> dict[str, Any]:
    case = run["case"]
    assertions = case.get("assertions") if isinstance(case.get("assertions"), dict) else {}
    trace = run.get("trace") or []
    skill_events = [item for item in trace if item.get("type") == "skill_event"]
    completed_skills = [item for item in skill_events if item.get("category") == "skill" and item.get("status") == "completed"]
    failed_skills = [item for item in skill_events if item.get("category") == "skill" and item.get("status") == "failed"]
    completed_layers = [str(item.get("layer")) for item in completed_skills if item.get("layer")]
    required_layers = [str(item) for item in assertions.get("required_skill_layers") or ["L1", "L2", "L3", "L4"]]
    layer_cursor = 0
    for layer in completed_layers:
        if layer_cursor < len(required_layers) and layer == required_layers[layer_cursor]:
            layer_cursor += 1
    widget = (run.get("widget_contracts") or [None])[0]
    runtime_entry = plugin_runtime_entry_skill(str(run["plugin_id"]), require_ready=False)
    completed_names = [str(item.get("name") or "") for item in completed_skills]
    expected_skill_sequence = [str(item) for item in assertions.get("expected_skill_sequence") or []]
    skill_cursor = 0
    for name in completed_names:
        if skill_cursor < len(expected_skill_sequence) and name == expected_skill_sequence[skill_cursor]:
            skill_cursor += 1
    scenario_errors = [
        item
        for item in trace
        if item.get("type") in {"error", "scenario_timeout", "scenario_script_error", "scenario_runner_error"}
    ]
    checks = {
        "runtime_entry_loaded": any(item.get("name") == runtime_entry for item in completed_skills),
        "required_layer_order": layer_cursor == len(required_layers),
        "expected_skill_sequence": skill_cursor == len(expected_skill_sequence),
        "no_failed_skills": not failed_skills,
        "no_runtime_or_scenario_errors": not scenario_errors,
        "first_widget_rendered": widget is not None,
        "first_interaction_goal": True,
        "first_widget_type": True,
        "forbidden_tools_absent": True,
    }
    expected_goal = assertions.get("expected_first_interaction_goal")
    if expected_goal:
        checks["first_interaction_goal"] = bool(widget and widget.get("interaction_goal") == expected_goal)
    expected_type = assertions.get("expected_first_widget_type")
    if expected_type:
        checks["first_widget_type"] = bool(widget and widget.get("widget_type") == expected_type)
    forbidden_tools = {str(item) for item in assertions.get("forbidden_tools") or []}
    observed_tools = {
        str(item.get("tool_name") or item.get("name"))
        for item in skill_events
        if item.get("category") == "tool"
    }
    required_tools = {str(item) for item in assertions.get("required_tools") or []}
    checks["required_tools_called"] = required_tools <= observed_tools
    checks["forbidden_tools_absent"] = not bool(forbidden_tools & observed_tools)
    if run.get("mode") != "probe":
        checks["scripted_returns_consumed"] = int(run.get("scripted_returns_consumed") or 0) == len(case.get("scripted_returns") or [])
        expected_artifact_types = {str(item) for item in assertions.get("expected_artifact_types") or []}
        observed_artifact_types = {
            str(item.get("artifact_type") or item.get("type") or item.get("mime") or "")
            for item in run.get("artifacts") or []
        }
        checks["expected_artifacts"] = expected_artifact_types <= observed_artifact_types
        signals = [str(item).lower() for item in assertions.get("final_content_signals") or []]
        final_content = "\n".join(
            str(item.get("content") or "")
            for item in trace
            if item.get("type") in {"assistant_complete", "artifact_generated"}
        ).lower()
        checks["final_content_signals"] = all(signal in final_content for signal in signals)
    issues = [name for name, passed in checks.items() if not passed]
    failed_phase = None
    if issues:
        if not checks["runtime_entry_loaded"]:
            failed_phase = "runtime_entry"
        elif not checks["required_layer_order"]:
            failed_phase = required_layers[layer_cursor] if layer_cursor < len(required_layers) else "layer_chain"
        elif not checks["expected_skill_sequence"]:
            failed_phase = "skill_sequence"
        elif not checks["first_widget_rendered"] or not checks["first_interaction_goal"] or not checks["first_widget_type"]:
            failed_phase = "widget_contract"
        elif not checks["required_tools_called"] or not checks["forbidden_tools_absent"]:
            failed_phase = "execution"
        else:
            failed_phase = "final_result"
    return {
        "passed": not issues,
        "checks": checks,
        "issues": issues,
        "failed_phase": failed_phase,
        "completed_skill_names": [item.get("name") for item in completed_skills],
        "completed_layers": completed_layers,
        "failed_skills": failed_skills,
        "scenario_errors": scenario_errors,
        "first_widget": widget,
    }


def _scripted_result(case: dict[str, Any], index: int, interaction: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    scripted_returns = case.get("scripted_returns") or []
    if index >= len(scripted_returns):
        return None, f"No scripted return exists for interaction #{index + 1}."
    scripted = scripted_returns[index]
    match = scripted.get("match") if isinstance(scripted.get("match"), dict) else {}
    expected_widget_type = scripted.get("widget_type") or match.get("widget_type")
    if expected_widget_type and expected_widget_type != interaction.get("widget_type"):
        return None, f"Interaction #{index + 1} expected widget_type '{expected_widget_type}', got '{interaction.get('widget_type')}'."
    expected_goal = scripted.get("interaction_goal") or match.get("interaction_goal")
    if expected_goal and expected_goal != interaction.get("interaction_goal"):
        return None, f"Interaction #{index + 1} expected interaction_goal '{expected_goal}', got '{interaction.get('interaction_goal')}'."
    payload = scripted.get("result") if isinstance(scripted.get("result"), dict) else scripted
    values = payload.get("values") if isinstance(payload.get("values"), dict) else {}
    return {
        "widget_id": interaction.get("widget_id"),
        "planner_id": interaction.get("planner_id"),
        "action": str(payload.get("action") or "accept"),
        "values": values,
        "freeform_note": str(payload.get("freeform_note") or "Automated scripted acceptance response."),
        "timestamp": _now(),
    }, None


async def _collect_background_case(
    web_session: Any,
    queue: asyncio.Queue,
    task: asyncio.Task,
    run: dict[str, Any],
    timeout_seconds: float,
) -> None:
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout_seconds
    saw_widget = False
    scripted_index = 0
    needs_abort = False
    while loop.time() < deadline:
        try:
            event = await asyncio.wait_for(queue.get(), timeout=min(1.0, max(0.1, deadline - loop.time())))
        except TimeoutError:
            if task.done():
                break
            continue
        compact = _compact_event(event)
        run["trace"].append(compact)
        if compact["type"] == "widget_render":
            run["widget_contracts"].append(compact)
            if run["mode"] == "scripted":
                result, script_error = _scripted_result(run["case"], scripted_index, compact)
                if script_error:
                    run["trace"].append({"type": "scenario_script_error", "content": script_error})
                    needs_abort = True
                    break
                scripted_index += 1
            else:
                result = {
                    "widget_id": compact.get("widget_id"),
                    "planner_id": compact.get("planner_id"),
                    "action": "dismiss",
                    "values": {},
                    "freeform_note": "Automated probe completed at the first interaction.",
                    "timestamp": _now(),
                }
            web_session.resolve_widget(str(compact.get("widget_id") or ""), result)
            run["widget_returns"].append(result)
            saw_widget = True
        elif compact["type"] == "workspace_open":
            if run["mode"] == "scripted":
                run["trace"].append({
                    "type": "scenario_script_error",
                    "content": "Scripted workspace returns are not declared for this case.",
                })
                needs_abort = True
                break
            web_session.resolve_workspace(
                str(compact.get("workspace_id") or ""),
                {"action": "dismiss", "values": {}, "freeform_note": "Automated probe completed at the first interaction."},
            )
        elif compact["type"] == "user_input_request":
            if run["mode"] == "scripted":
                run["trace"].append({
                    "type": "scenario_script_error",
                    "content": "The plugin requested unstructured input instead of its scripted interaction contract.",
                })
                needs_abort = True
                break
            web_session.resolve_user_input(str(compact.get("request_id") or ""), "")
        if compact["type"] == "error":
            break
        if compact["type"] == "session_idle":
            break
        if saw_widget and len(run["widget_contracts"]) >= MAX_SCENARIO_WIDGET_STEPS:
            run["trace"].append({"type": "scenario_script_error", "content": "Interaction step limit exceeded."})
            needs_abort = True
            break
    if not task.done() and loop.time() >= deadline:
        run["trace"].append({"type": "scenario_timeout", "content": f"Exceeded {timeout_seconds:g} seconds."})
    run["scripted_returns_consumed"] = scripted_index
    if needs_abort and not task.done():
        with contextlib.suppress(Exception):
            await web_session.session.abort()
    try:
        await asyncio.wait_for(task, timeout=5)
    except TimeoutError:
        with contextlib.suppress(Exception):
            await web_session.session.abort()
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


async def run_probe_case(
    service: Any,
    plugin_id: str,
    *,
    case_id: str | None = None,
    case: dict[str, Any] | None = None,
    timeout_seconds: float = 120,
) -> dict[str, Any]:
    plugin_entry(plugin_id, require_ready=False)
    selected_case = dict(case or select_case(plugin_id, case_id))
    run_mode = "scripted" if selected_case.get("mode") == "scripted" else "probe"
    run_id = uuid.uuid4().hex
    web_session = await service.create_session(
        default_plugin_id=plugin_id,
        approve_all=True,
        allow_planned_plugin=True,
        system_message=(
            "This is an isolated validation scenario. Follow the selected plugin normally. "
            + (
                "The host will provide approved scripted widget returns; do not invent or replace them."
                if run_mode == "scripted"
                else "Do not infer that a widget dismissal is task approval. The host will stop after the first interaction."
            )
        ),
    )
    run = {
        "schema_version": "1.0",
        "run_id": run_id,
        "plugin_id": plugin_id,
        "mode": run_mode,
        "status": "running",
        "session_id": web_session.session_id,
        "case": selected_case,
        "started_at": _now(),
        "finished_at": None,
        "trace": [],
        "widget_contracts": [],
        "widget_returns": [],
        "tool_results": [],
        "artifacts": [],
        "evaluation": {},
        "debug_handoff": {
            "author_action": "reopen_author_with_failed_case",
            "plugin_id": plugin_id,
            "case_id": selected_case.get("id"),
        },
    }
    _save_run(run)
    queue = web_session.subscribe_events()
    task = asyncio.create_task(web_session.send_message(
        str(selected_case.get("user_input") or ""),
        attachments=list(selected_case.get("attachments") or []),
        plugin_id=plugin_id,
    ))
    try:
        await _collect_background_case(web_session, queue, task, run, timeout_seconds)
    except Exception as error:  # noqa: BLE001
        run["trace"].append({"type": "scenario_runner_error", "content": str(error)})
    finally:
        web_session.unsubscribe_events(queue)
    _session_evidence(run)
    run["evaluation"] = evaluate_run(run)
    run["debug_handoff"]["failed_phase"] = run["evaluation"].get("failed_phase")
    run["status"] = "passed" if run["evaluation"]["passed"] else "failed"
    run["finished_at"] = _now()
    _save_run(run)
    return run


_BACKGROUND_TASKS: set[asyncio.Task] = set()


def _track_task(task: asyncio.Task) -> None:
    _BACKGROUND_TASKS.add(task)
    task.add_done_callback(_BACKGROUND_TASKS.discard)


async def _monitor_interactive_run(web_session: Any, queue: asyncio.Queue, task: asyncio.Task, run: dict[str, Any]) -> None:
    try:
        while True:
            event = await queue.get()
            compact = _compact_event(event)
            run["trace"].append(compact)
            if compact["type"] == "widget_render":
                run["widget_contracts"].append(compact)
                run["status"] = "waiting_for_user"
            elif compact["type"] == "artifact_generated" and compact.get("attachment"):
                run["artifacts"].append(compact)
            elif compact["type"] == "error":
                run["status"] = "failed"
            elif compact["type"] == "session_idle":
                break
            _save_run(run)
        await task
    except Exception as error:  # noqa: BLE001
        run["status"] = "failed"
        run["trace"].append({"type": "monitor_error", "content": str(error)})
    finally:
        web_session.unsubscribe_events(queue)
        _session_evidence(run)
        run["evaluation"] = evaluate_run(run)
        run["debug_handoff"]["failed_phase"] = run["evaluation"].get("failed_phase")
        if run["status"] != "failed":
            run["status"] = "passed" if run["evaluation"]["passed"] else "needs_review"
        run["finished_at"] = _now()
        _save_run(run)


async def start_interactive_case(
    service: Any,
    plugin_id: str,
    *,
    case_id: str | None = None,
    case: dict[str, Any] | None = None,
) -> dict[str, Any]:
    plugin_entry(plugin_id, require_ready=False)
    selected_case = dict(case or select_case(plugin_id, case_id))
    web_session = await service.create_session(
        default_plugin_id=plugin_id,
        approve_all=True,
        allow_planned_plugin=True,
    )
    run = {
        "schema_version": "1.0",
        "run_id": uuid.uuid4().hex,
        "plugin_id": plugin_id,
        "mode": "interactive",
        "status": "running",
        "session_id": web_session.session_id,
        "case": selected_case,
        "started_at": _now(),
        "finished_at": None,
        "trace": [],
        "widget_contracts": [],
        "widget_returns": [],
        "tool_results": [],
        "artifacts": [],
        "evaluation": {},
        "debug_handoff": {
            "author_action": "reopen_author_with_failed_case",
            "plugin_id": plugin_id,
            "case_id": selected_case.get("id"),
        },
    }
    _save_run(run)
    queue = web_session.subscribe_events()
    task = asyncio.create_task(web_session.send_message(
        str(selected_case.get("user_input") or ""),
        attachments=list(selected_case.get("attachments") or []),
        plugin_id=plugin_id,
    ))
    monitor = asyncio.create_task(_monitor_interactive_run(web_session, queue, task, run))
    _track_task(task)
    _track_task(monitor)
    return run
