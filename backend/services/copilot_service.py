from __future__ import annotations

import asyncio
import contextlib
import dataclasses
import os
import time
import uuid
from pathlib import Path
from typing import Any

from copilot import CopilotClient, RuntimeConnection, SessionHooks
from copilot.rpc import PermissionDecisionApproveOnce, PermissionDecisionReject
from copilot.session import PermissionHandler

from chat_cli import (
    AuthSetupError,
    DEFAULT_MODEL,
    DEFAULT_WORKSPACE,
    event_delta_content,
    event_message_content,
    event_type,
    get_github_token_from_gh,
    permission_request_to_dict,
)
from backend.services import chat_store
from backend.services.inflak_plugins import (
    DEFAULT_PLUGIN_ID,
    PluginRegistryError,
    plugin_entry,
    ready_plugin_dirs,
)
from backend.services.plugin_tools.image.tools import build_image_tools
from backend.services.plugin_tools.reporting import reports as p9_reports
from backend.services.plugin_tools.shared.layer_order import EFFECT_TOOL_NAMES, RENDER_TOOL_NAMES, LayerOrderTracker
from backend.services.plugin_tools.shared.tools import build_iai_tools


RENDERER_TOOL_NAMES = {"render_html_widget", "render_interactive_widget", "render_canvas_workspace"}

IAI_SYSTEM_MESSAGE = (
    "The 'inflak-main' plugin provides dialogue-first image and text-writing co-creation. "
    "Enter the chain when the user asks to create or revise an artifact, choose among options, "
    "or provide structured input; otherwise answer directly without a widget. "
    "Once you enter, follow the plugin's root SKILL.md and the selected pathway's layer order, "
    "re-entering Layer 1 on every pass (after every widget return or tool result). "
    "The layer names are L1 Router, L2 Planner, L3 Designer, and L4 Renderer. "
    "The four pathways are Interaction Pathway, Execution Pathway, Host Agent Return, and Completion. "
    "Interaction Pathway: user/return -> L1 -> L2 -> L3 -> L4 -> L1. "
    "Execution Pathway: user/return -> L1 -> L2 plan -> execute/realize -> L1. When the selected planner declares execution_skill and execution_skill_path, load that exec-* skill with the ready execution_instruction; otherwise invoke the selected executor or active main model directly. "
    "Host Agent Return: L1 returns an out-of-scope request to the host agent. Completion: only L1 decides the current intent is complete. "
    "Layer 1 (l1-router) reconstructs state and routes to one eligible planner, returns to the host agent, or ends; only Layer 1 decides completion. "
    "Layer 2 resolves its descriptive skill name from the selected plugin's current registry/planners.json; do not use retired or numbered main-plugin skill names. "
    "Main has exactly five planners: writing-draft, writing-revision, prompt-enhancement, image-generation, and image-edit. "
    "Layer 2 follows its L2 contract: position current state on the before/after GenAI invocation and prompt-only/artifact-grounded axes, bind the six IAI nodes, assess registered gap categories, and select the next material open gap by dependencies and its interaction chain. Derive the missing per-edge transformation from actual evidence before assigning a registered category or choosing a widget. Explain why current facts or explicit scoped delegation cannot resolve it and the user-visible consequence of guessing. "
    "For all five inflak-main L2 planners: Prioritize gap detection and resolution. Assess every registered gap category against current evidence. Resolve applicable open gaps through interaction before final artifact execution. On every pass, assess each category registered to the selected planner as not applicable, resolved, or open: justify non-applicability from the current task, resolution from actual facts, prior submitted returns or explicit scoped user delegation, and open gaps from missing material information and the consequence of guessing. Assess material information needs, including dimensions stored in optional fields; neither field presence nor artifact labels replace this assessment. "
    "Silence is not delegation. A generic creation request does not authorize every missing audience, setting or core topic. Detect and resolve material choices even when the user has not explicitly reserved them. Delegation closes only its corresponding dimensions; ordinary elaboration must stay within an evidenced direction, and being able to invent an artifact does not establish closure. Keep assessment and closure evidence in existing iai_binding.reason or execution_instruction.purpose, not new handoff or runtime state fields. "
    "Select one next material open gap per pass by dependencies, then its eligible widget. After every return, re-enter Layer 1, reassess all categories against the newest evidence, and continue until applicable gaps are resolved or a genuine escape is reported. Do not repeat settled questions unless relevant dependent evidence changes, and do not replace semantic resolution with a generic approval checkbox. "
    "Reserve instruction_ready for evidence-backed closure across all relevant gaps, with other categories justified as not applicable, or bounded prerequisite preparation meeting its own source, capability and consent requirements. Preparation returns to Layer 1 with unresolved user choices still open and must not execute the final artifact. Never invent delegation or treat an unsupported gap as readiness. Source/tool/capability failures, unsupported indispensable transfers, and gap routing failures including no_eligible_widget return directly to Layer 1 as actual nonterminal failures, without Layer 3 entry or fabricated semantic gaps. These proactive assessment and closure rules apply to inflak-main; other plugins retain their own task-specific behavior and runtime APIs. "
    "Preserve topic/visual keyword selection through option-selector when that semantic decision is genuinely open. A diagnosed spatial-drawing gap uses canvas-editor with actual sketch evidence, not a text form; an existing current sketch needs no confirmation pass. Image-edit owns edit intent, style transfer, inpaint, and deterministic adjustments. Every return goes through Layer 1 for fresh diagnosis. "
    "Main does not route to SVG editing, collage composition, or daily-paper digests. "
    "Layer 2 diagnoses gaps and selects an eligible widget for interaction, or hands a ready plan to its declared execution skill for execution. Execution skills are capabilities of the same Host, parallel to L3 interaction design, not numbered layers or new agents. They preserve executor kind/name, parameters, purpose and authorization; they never replan, render or decide completion. "
    "Only an eligible selected-widget gap enters Layer 3. Layer 3 designs the semantic interaction contract using the selected l3-* skill; it never executes task work. Layer 3 errors return directly to Layer 1 without Layer 4 entry. "
    "For inflak-main, Layer 4 (l4-widget-renderer) renders only conversation_widget with render_html_widget. "
    "Image previews, sketches and masks stay inside the dialogue widget; main never opens a persistent Canvas or uses document-selection/patch state. "
    "Other plugins may use render_canvas_workspace only when their own registered contract requests canvas_workspace. Every return goes to Layer 1. "
    "Do not skip layers: the backend enforces layer order and refuses registered rendering tools unless the pass reached them through L1 -> L2 -> L3, and refuses the image tools "
    "(including generate_image, edit_image, restyle_image, outpaint_image, remove_background, replace_background, generate_variations, transform_image, adjust_image, apply_filter) unless the pass reached them through L1 -> L2. "
    "On an instruction-ready pass, load the planner's declared execution skill before realizing its selected tool/main_model plan, without Layer 3 or Layer 4. Plugins without an execution skill, including main, retain direct execution. An execution skill is not a tool name or a replacement executor.kind. Inpaint masks use transparent pixels for edit regions and opaque pixels for preserved regions. "
    "Layer 2 freely plans user interaction, main-model work, or one or more registered tools for the current pass. Only eligible interaction design enters Layer 3; execution preserves the selected executor, parameters, and purpose. "
    "Every interaction or execution result or failure returns to the Layer 1 skill named by the selected planner's loop_return_to. Only Layer 1 decides workflow completion. "
    "When reading workspace files, use search results and small bounded ranges. Never reuse stale line ranges after a file changes. "
    "If a file read reports 'view_range out of bounds', immediately retry once with a smaller range starting at a known valid line; treat it as end-of-file rather than ending the task or exposing the tool failure to the user. "
    "For other plugins that explicitly use an artifact Canvas widget return containing patch_result, treat patch_result.attachment and patch_result.scene as the authoritative newest artifact state, re-enter Layer 1, and continue to the next prepared authoring control or review. Do not stop after merely acknowledging applied_revision. "
    "Routing, drafting, rewriting, and claim work are your own reasoning under the skills."
)


class SessionNotFoundError(KeyError):
    pass


def to_jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [to_jsonable(item) for item in value]
    if dataclasses.is_dataclass(value):
        return to_jsonable(dataclasses.asdict(value))
    if hasattr(value, "to_dict"):
        with contextlib.suppress(Exception):
            return to_jsonable(value.to_dict())
    if hasattr(value, "__dict__"):
        return {
            key: to_jsonable(item)
            for key, item in vars(value).items()
            if not key.startswith("_")
        }
    return repr(value)


def build_sdk_attachments(attachments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Map uploaded-file metadata to Copilot SDK file attachments.

    Each upload was persisted under data/uploads, so we reference it by absolute
    path; the model reads images and documents directly from disk.
    """
    sdk_attachments: list[dict[str, Any]] = []
    for item in attachments:
        path = item.get("path")
        if not path:
            continue
        attachment: dict[str, Any] = {
            "type": "file",
            "path": path,
            "displayName": item.get("name") or Path(path).name,
        }
        if item.get("mime"):
            attachment["mimeType"] = item["mime"]
        sdk_attachments.append(attachment)
    return sdk_attachments


def compact_debug_value(value: Any, limit: int = 160) -> Any:
    if value is None or isinstance(value, (int, float, bool)):
        return value
    text = str(value).strip()
    if len(text) <= limit:
        return text
    return f"{text[:limit].rstrip()}..."


def infer_iai_layer(skill_name: str | None) -> str | None:
    if not skill_name:
        return None
    normalized = skill_name.removeprefix("iai-")
    layer, separator, suffix = normalized.partition("-")
    if separator and suffix and layer in {"l1", "l2", "l3", "l4"}:
        return layer.upper()
    return None


def hook_skill_name(tool_name: str, tool_args: Any) -> str | None:
    if tool_name != "skill" or not isinstance(tool_args, dict):
        return None
    value = tool_args.get("skill") or tool_args.get("name") or tool_args.get("skillName")
    return str(value) if value else None


def renderer_tool_display_name(tool_name: str) -> str:
    if tool_name == "render_html_widget":
        return "HTML widget renderer"
    if tool_name == "render_interactive_widget":
        return "Schema widget renderer"
    if tool_name == "render_canvas_workspace":
        return "Canvas workspace renderer"
    return tool_name.replace("_", " ")


def compact_tool_preview(tool_name: str | None, arguments: Any) -> dict[str, Any]:
    if tool_name not in RENDERER_TOOL_NAMES or not isinstance(arguments, dict):
        return {}

    preview: dict[str, Any] = {}
    for key in ("widget_id", "widget_type", "planner_id", "interaction_goal", "title", "height"):
        value = arguments.get(key)
        if value not in (None, ""):
            preview[key] = compact_debug_value(value)

    display = arguments.get("display")
    if isinstance(display, dict) and "title" not in preview and display.get("title"):
        preview["title"] = compact_debug_value(display.get("title"))

    controls = arguments.get("controls")
    if isinstance(controls, list):
        preview["control_count"] = len(controls)

    expected_return = arguments.get("expected_return")
    if isinstance(expected_return, dict):
        preview["expected_return_keys"] = list(expected_return)[:8]

    return preview


class WebCopilotSession:
    def __init__(
        self,
        *,
        session: Any,
        model: str,
        working_directory: str,
        approve_all: bool,
        default_plugin_id: str = DEFAULT_PLUGIN_ID,
        enforce_layer_order: bool | None = None,
    ) -> None:
        self.session = session
        self.session_id = session.session_id
        self.model = model
        self.actual_model: str | None = None
        self.actual_model_source: str | None = None
        self.working_directory = working_directory
        self.approve_all = approve_all
        self.default_plugin_id = default_plugin_id
        self.current_plugin_id = default_plugin_id
        self.strict_layer_harness = enforce_layer_order is True
        self.outgoing: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self.event_subscribers: set[asyncio.Queue[dict[str, Any]]] = set()
        self.pending_permissions: dict[str, asyncio.Future[bool]] = {}
        self.pending_user_inputs: dict[str, asyncio.Future[str]] = {}
        self.pending_widgets: dict[str, asyncio.Future[dict[str, Any]]] = {}
        self.pending_widget_contracts: dict[str, dict[str, Any]] = {}
        self.pending_workspaces: dict[str, asyncio.Future[dict[str, Any]]] = {}
        self.workspace_states: dict[str, dict[str, Any]] = {}
        self.active_debug_calls: dict[str, dict[str, Any]] = {}
        self.layer_order = LayerOrderTracker(
            enforce_initial_l1=enforce_layer_order,
            enforce_transitions=enforce_layer_order,
        )
        self.widget_returns: list[dict[str, Any]] = []
        self.connected = False
        self.busy = False
        self._assistant_buffer: list[str] = []

    def ensure_stored(self) -> None:
        chat_store.ensure_session_record(
            session_id=self.session_id,
            model=self.model,
            working_directory=self.working_directory,
            approve_all=self.approve_all,
            default_plugin_id=self.default_plugin_id,
        )

    async def emit(self, event: dict[str, Any]) -> None:
        await self.outgoing.put(event)
        for queue in tuple(self.event_subscribers):
            await queue.put(event)

    def emit_nowait(self, event: dict[str, Any]) -> None:
        self.outgoing.put_nowait(event)
        for queue in tuple(self.event_subscribers):
            queue.put_nowait(event)

    def subscribe_events(self) -> asyncio.Queue[dict[str, Any]]:
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self.event_subscribers.add(queue)
        return queue

    def unsubscribe_events(self, queue: asyncio.Queue[dict[str, Any]]) -> None:
        self.event_subscribers.discard(queue)

    async def handle_permission_request(self, request: Any, invocation: dict[str, Any]) -> Any:
        request_payload = permission_request_to_dict(request)
        if self.approve_all:
            chat_store.append_message(
                session_id=self.session_id,
                role="permission_response",
                content="Auto-approved tool request.",
                metadata={
                    "requestType": type(request).__name__,
                    "request": request_payload,
                    "approved": True,
                    "autoApproved": True,
                    "invocation": to_jsonable(invocation),
                },
            )
            return PermissionDecisionApproveOnce()

        request_id = str(uuid.uuid4())
        loop = asyncio.get_running_loop()
        future: asyncio.Future[bool] = loop.create_future()
        self.pending_permissions[request_id] = future

        chat_store.append_message(
            session_id=self.session_id,
            role="permission_request",
            content=f"Permission request: {type(request).__name__}",
            metadata={
                "requestId": request_id,
                "requestType": type(request).__name__,
                "request": request_payload,
                "invocation": to_jsonable(invocation),
            },
        )

        await self.emit(
            {
                "type": "permission_request",
                "requestId": request_id,
                "requestType": type(request).__name__,
                "request": request_payload,
                "invocation": to_jsonable(invocation),
            }
        )

        try:
            approved = await future
        finally:
            self.pending_permissions.pop(request_id, None)

        chat_store.append_message(
            session_id=self.session_id,
            role="permission_response",
            content="Approved tool request." if approved else "Rejected tool request.",
            metadata={"requestId": request_id, "approved": approved},
        )

        if approved:
            return PermissionDecisionApproveOnce()
        return PermissionDecisionReject(feedback="The user rejected this tool request in the web UI.")

    async def handle_user_input_request(self, request: Any, invocation: dict[str, Any]) -> dict[str, Any]:
        request_id = str(uuid.uuid4())
        loop = asyncio.get_running_loop()
        future: asyncio.Future[str] = loop.create_future()
        self.pending_user_inputs[request_id] = future

        if isinstance(request, dict):
            question = request.get("question", "Copilot asks for input")
            choices = request.get("choices") or []
        else:
            question = getattr(request, "question", "Copilot asks for input")
            choices = getattr(request, "choices", None) or []

        chat_store.append_message(
            session_id=self.session_id,
            role="user_input_request",
            content=str(question),
            metadata={
                "requestId": request_id,
                "choices": to_jsonable(choices),
                "invocation": to_jsonable(invocation),
            },
        )

        await self.emit(
            {
                "type": "user_input_request",
                "requestId": request_id,
                "question": question,
                "choices": choices,
                "invocation": to_jsonable(invocation),
            }
        )

        try:
            answer = await future
        finally:
            self.pending_user_inputs.pop(request_id, None)

        chat_store.append_message(
            session_id=self.session_id,
            role="user_input_response",
            content=answer,
            metadata={"requestId": request_id, "wasFreeform": True},
        )

        return {"answer": answer, "wasFreeform": True}

    async def send_message(
        self,
        content: str,
        *,
        attachments: list[dict[str, Any]] | None = None,
        plugin_id: str | None = None,
    ) -> None:
        if self.busy:
            await self.emit({"type": "error", "message": "A response is already in progress."})
            return

        self.busy = True
        self._assistant_buffer = []
        self.active_debug_calls.clear()
        self.ensure_stored()
        selected_plugin_id = plugin_id or self.default_plugin_id
        try:
            selected_plugin = plugin_entry(selected_plugin_id)
        except PluginRegistryError as error:
            await self.emit({"type": "error", "message": str(error)})
            self.busy = False
            return
        self.current_plugin_id = selected_plugin_id
        sdk_attachments = build_sdk_attachments(attachments or [])
        metadata: dict[str, Any] = {"pluginId": selected_plugin_id}
        if attachments:
            metadata["attachments"] = attachments
        chat_store.append_message(
            session_id=self.session_id,
            role="user",
            content=content,
            metadata=metadata,
        )
        self.layer_order.begin_turn()
        await self.emit({"type": "message_started"})
        try:
            if self.strict_layer_harness:
                await self.session.send_and_wait(
                    (
                        f"[Runtime harness entry phase for {selected_plugin_id}: load the selected "
                        "plugin's Layer 1 skill now. Do not inspect artifacts, call any task tool, "
                        "load a downstream layer, answer the task, or render an interaction. This "
                        "phase only establishes the mandatory Layer 1 entry; the user request follows.]"
                    ),
                    timeout=None,
                )
                entry_block = self.layer_order.block_completion()
                if entry_block is not None:
                    chat_store.append_message(
                        session_id=self.session_id,
                        role="error",
                        content=entry_block["message"],
                        metadata={
                            "errorType": entry_block["error"],
                            "pluginId": selected_plugin_id,
                            "harnessPhase": "initial_l1",
                        },
                    )
                    await self.emit({"type": "error", **entry_block})
                    return
                self._assistant_buffer = []
            response = await self.session.send_and_wait(
                (
                    f"[Use the selected independent inflak plugin: {selected_plugin_id}. "
                    f"Plugin role: {selected_plugin['description']} Load and follow its root SKILL.md "
                    "and then its own Layer 1 through Layer 4 skills before acting on this turn.]\n\n"
                    + content
                ),
                attachments=sdk_attachments or None,
                timeout=None,
            )
            completion_block = self.layer_order.block_completion()
            if completion_block is not None:
                self.layer_order.begin_l1_reentry()
                self._assistant_buffer = []
                response = await self.session.send_and_wait(
                    (
                        "[Runtime guard: downstream layer work cannot complete the workflow. "
                        "Load the selected plugin's Layer 1 skill now. Do not load another layer, "
                        "call a task tool, or render a widget first. Layer 1 must reconstruct the "
                        "newest state and decide whether to continue or end.]"
                    ),
                    timeout=None,
                )
                completion_block = self.layer_order.block_completion()
            if completion_block is not None:
                chat_store.append_message(
                    session_id=self.session_id,
                    role="error",
                    content=completion_block["message"],
                    metadata={
                        "errorType": completion_block["error"],
                        "pluginId": selected_plugin_id,
                    },
                )
                await self.emit({"type": "error", **completion_block})
                return
            final_content = event_message_content(response) if response is not None else ""
            if not final_content:
                final_content = "".join(self._assistant_buffer)
            delivery = {"role": "assistant", "content": final_content, "metadata": {"pluginId": selected_plugin_id}}
            if final_content and selected_plugin_id == p9_reports.PLUGIN_ID:
                delivery = await asyncio.to_thread(p9_reports.prepare_message, self.session_id, delivery)
            if final_content:
                chat_store.append_message(
                    session_id=self.session_id,
                    role="assistant",
                    content=final_content,
                    metadata=delivery["metadata"],
                )
            await self.emit({
                "type": "assistant_complete", "content": delivery["content"],
                "report": delivery["metadata"].get("report"),
                "reportError": delivery["metadata"].get("reportError"),
            })
        except Exception as error:  # noqa: BLE001
            partial_content = "".join(self._assistant_buffer).strip()
            if partial_content:
                chat_store.append_message(
                    session_id=self.session_id,
                    role="assistant",
                    content=partial_content,
                    metadata={
                        "partial": True,
                        "interruptedBy": type(error).__name__,
                        "pluginId": selected_plugin_id,
                    },
                )
            chat_store.append_message(
                session_id=self.session_id,
                role="error",
                content=str(error),
                metadata={"errorType": type(error).__name__, "pluginId": selected_plugin_id},
            )
            await self.emit({"type": "error", "message": str(error)})
        finally:
            self.clear_pending_requests()
            self.busy = False
            await self.emit({"type": "session_idle"})

    def clear_pending_requests(self) -> None:
        for future in self.pending_permissions.values():
            if not future.done():
                future.set_result(False)
        for future in self.pending_user_inputs.values():
            if not future.done():
                future.set_result("")
        for future in self.pending_widgets.values():
            if not future.done():
                future.set_result({"action": "dismiss", "values": {}, "freeform_note": "Request ended."})
        for future in self.pending_workspaces.values():
            if not future.done():
                future.set_result({"action": "dismiss", "values": {}, "freeform_note": "Request ended."})
        self.pending_permissions.clear()
        self.pending_user_inputs.clear()
        self.pending_widgets.clear()
        self.pending_widget_contracts.clear()
        self.pending_workspaces.clear()

    def resolve_permission(self, request_id: str, approved: bool) -> bool:
        future = self.pending_permissions.get(request_id)
        if future is None or future.done():
            return False
        future.set_result(approved)
        return True

    def resolve_user_input(self, request_id: str, answer: str) -> bool:
        future = self.pending_user_inputs.get(request_id)
        if future is None or future.done():
            return False
        future.set_result(answer)
        return True

    async def render_widget(self, widget_contract: dict[str, Any]) -> dict[str, Any]:
        widget_id = str(widget_contract.get("widget_id") or uuid.uuid4())
        widget_contract["widget_id"] = widget_id
        loop = asyncio.get_running_loop()
        future: asyncio.Future[dict[str, Any]] = loop.create_future()
        self.pending_widgets[widget_id] = future
        self.pending_widget_contracts[widget_id] = dict(widget_contract)
        chat_store.append_message(
            session_id=self.session_id,
            role="widget_request",
            content=str(
                widget_contract.get("interaction_goal")
                or widget_contract.get("display", {}).get("title")
                or widget_contract.get("widget_type")
                or "Interactive widget"
            ),
            metadata={"widgetId": widget_id, "widget": widget_contract},
        )
        await self.emit({"type": "widget_render", "widgetId": widget_id, "widget": widget_contract})
        try:
            result = await future
        finally:
            self.pending_widgets.pop(widget_id, None)
            self.pending_widget_contracts.pop(widget_id, None)
        self.widget_returns.append(result)
        chat_store.append_message(
            session_id=self.session_id,
            role="widget_return",
            content=str(result.get("action") or "return"),
            metadata={"widgetId": widget_id, "result": result},
        )
        self.layer_order.begin_l1_reentry()
        return {
            **result,
            "_inflak_runtime": {
                "boundary": "widget_return",
                "required_next_layer": "L1",
                "instruction": (
                    "This external return closes the L4 pass. Load the selected plugin's "
                    "Layer 1 next so it can reconstruct state and decide whether to continue or end."
                ),
            },
        }

    async def render_workspace(self, workspace: dict[str, Any]) -> dict[str, Any]:
        workspace_id = str(workspace.get("workspace_id") or uuid.uuid4())
        workspace["workspace_id"] = workspace_id
        loop = asyncio.get_running_loop()
        future: asyncio.Future[dict[str, Any]] = loop.create_future()
        self.pending_workspaces[workspace_id] = future
        self.workspace_states[workspace_id] = dict(workspace.get("initial_state") or {})
        chat_store.append_message(
            session_id=self.session_id,
            role="workspace_request",
            content=str(workspace.get("interaction_goal") or workspace.get("workspace_type") or "Canvas workspace"),
            metadata={"workspaceId": workspace_id, "workspace": workspace},
        )
        await self.emit({"type": "workspace_open", "workspaceId": workspace_id, "workspace": workspace})
        try:
            result = await future
        finally:
            self.pending_workspaces.pop(workspace_id, None)
        chat_store.append_message(
            session_id=self.session_id,
            role="workspace_return",
            content=str(result.get("action") or "return"),
            metadata={"workspaceId": workspace_id, "result": result},
        )
        await self.emit({"type": "workspace_close", "workspaceId": workspace_id, "result": result})
        self.layer_order.begin_l1_reentry()
        return {
            **result,
            "_inflak_runtime": {
                "boundary": "workspace_return",
                "required_next_layer": "L1",
                "instruction": (
                    "This external return closes the L4 pass. Load the selected plugin's "
                    "Layer 1 next so it can reconstruct state and decide whether to continue or end."
                ),
            },
        }

    def resolve_widget(self, widget_id: str, result: dict[str, Any]) -> bool:
        future = self.pending_widgets.get(widget_id)
        if future is None or future.done():
            return False
        future.set_result(result)
        return True

    async def update_workspace(self, workspace_id: str, state: dict[str, Any]) -> bool:
        if workspace_id not in self.pending_workspaces:
            return False
        self.workspace_states[workspace_id] = dict(state)
        await self.emit({"type": "workspace_state", "workspaceId": workspace_id, "state": state})
        return True

    def resolve_workspace(self, workspace_id: str, result: dict[str, Any]) -> bool:
        future = self.pending_workspaces.get(workspace_id)
        if future is None or future.done():
            return False
        future.set_result(result)
        return True


class CopilotWebService:
    def __init__(self) -> None:
        self.client: CopilotClient | None = None
        self.github_token: str | None = None
        self.sessions: dict[str, WebCopilotSession] = {}
        self._client_lock = asyncio.Lock()

    async def ensure_client(self) -> CopilotClient:
        async with self._client_lock:
            if self.client is not None:
                return self.client

            self.github_token = get_github_token_from_gh()
            working_directory = str(Path(os.getenv("COPILOT_WORKSPACE", str(DEFAULT_WORKSPACE))).resolve())
            cli_url = os.getenv("COPILOT_CLI_URL")
            kwargs: dict[str, Any] = {
                "github_token": self.github_token,
                "use_logged_in_user": False,
                "working_directory": working_directory,
                "log_level": os.getenv("COPILOT_LOG_LEVEL", "warning"),
            }
            if cli_url:
                kwargs["connection"] = RuntimeConnection.for_uri(cli_url)
            elif os.getenv("IAI_PLUGIN_ENABLED", "1") != "0":
                plugin_args = tuple(
                    argument
                    for plugin_path in ready_plugin_dirs()
                    for argument in ("--plugin-dir", str(plugin_path))
                )
                kwargs["connection"] = RuntimeConnection.for_stdio(
                    args=plugin_args
                )

            self.client = CopilotClient(**kwargs)
            await self.client.start()
            return self.client

    async def list_models(self) -> list[dict[str, Any]]:
        client = await self.ensure_client()
        models = await client.list_models()
        return [to_jsonable(model) for model in models]

    async def create_session(
        self,
        *,
        model: str = DEFAULT_MODEL,
        working_directory: str | None = None,
        system_message: str | None = None,
        approve_all: bool = True,
        default_plugin_id: str = DEFAULT_PLUGIN_ID,
        allow_planned_plugin: bool = False,
        enforce_layer_order: bool | None = None,
    ) -> WebCopilotSession:
        client = await self.ensure_client()
        plugin_entry(default_plugin_id, require_ready=not allow_planned_plugin)
        cwd = str(Path(working_directory or DEFAULT_WORKSPACE).expanduser().resolve())
        placeholder: dict[str, WebCopilotSession] = {}

        async def on_permission_request(request: Any, invocation: dict[str, Any]) -> Any:
            return await placeholder["session"].handle_permission_request(request, invocation)

        async def on_user_input_request(request: Any, invocation: dict[str, Any]) -> dict[str, Any]:
            return await placeholder["session"].handle_user_input_request(request, invocation)

        async def on_pre_tool_use(input_data: dict[str, Any], invocation: dict[str, str]) -> dict[str, Any] | None:
            tool_name = str(input_data.get("toolName") or "")
            skill_name = hook_skill_name(tool_name, input_data.get("toolArgs"))
            blocked = placeholder["session"].layer_order.block_pre_tool(
                tool_name,
                infer_iai_layer(skill_name),
            )
            if blocked is None:
                return None
            return {
                "permissionDecision": "deny",
                "permissionDecisionReason": blocked["message"],
                "additionalContext": blocked["message"],
            }

        async def on_task_tool_result(input_data: dict[str, Any], invocation: dict[str, str]) -> None:
            tool_name = str(input_data.get("toolName") or "")
            if tool_name in EFFECT_TOOL_NAMES - RENDER_TOOL_NAMES:
                placeholder["session"].layer_order.begin_l1_reentry()

        session_kwargs: dict[str, Any] = {
            "model": model,
            "streaming": True,
            "working_directory": cwd,
            "github_token": self.github_token,
            "on_user_input_request": on_user_input_request,
            "hooks": SessionHooks(
                on_pre_tool_use=on_pre_tool_use,
                on_post_tool_use=on_task_tool_result,
                on_post_tool_use_failure=on_task_tool_result,
            ),
            "tools": build_iai_tools(placeholder) + build_image_tools(placeholder),
        }
        if approve_all:
            session_kwargs["on_permission_request"] = PermissionHandler.approve_all
        else:
            session_kwargs["on_permission_request"] = on_permission_request
        iai_system_message = IAI_SYSTEM_MESSAGE
        session_kwargs["system_message"] = {
            "content": f"{iai_system_message}\n\n{system_message}" if system_message else iai_system_message
        }

        copilot_session = await client.create_session(**session_kwargs)
        web_session = WebCopilotSession(
            session=copilot_session,
            model=model,
            working_directory=cwd,
            approve_all=approve_all,
            default_plugin_id=default_plugin_id,
            enforce_layer_order=enforce_layer_order,
        )
        placeholder["session"] = web_session
        copilot_session.on(lambda event: self._handle_session_event(web_session, event))
        self.sessions[web_session.session_id] = web_session
        web_session.ensure_stored()
        return web_session

    async def resume_session(self, session_id: str) -> WebCopilotSession:
        if session_id in self.sessions:
            return self.sessions[session_id]

        record = chat_store.load_session(session_id)
        client = await self.ensure_client()
        placeholder: dict[str, WebCopilotSession] = {}

        async def on_permission_request(request: Any, invocation: dict[str, Any]) -> Any:
            return await placeholder["session"].handle_permission_request(request, invocation)

        async def on_user_input_request(request: Any, invocation: dict[str, Any]) -> dict[str, Any]:
            return await placeholder["session"].handle_user_input_request(request, invocation)

        async def on_pre_tool_use(input_data: dict[str, Any], invocation: dict[str, str]) -> dict[str, Any] | None:
            tool_name = str(input_data.get("toolName") or "")
            skill_name = hook_skill_name(tool_name, input_data.get("toolArgs"))
            blocked = placeholder["session"].layer_order.block_pre_tool(
                tool_name,
                infer_iai_layer(skill_name),
            )
            if blocked is None:
                return None
            return {
                "permissionDecision": "deny",
                "permissionDecisionReason": blocked["message"],
                "additionalContext": blocked["message"],
            }

        async def on_task_tool_result(input_data: dict[str, Any], invocation: dict[str, str]) -> None:
            tool_name = str(input_data.get("toolName") or "")
            if tool_name in EFFECT_TOOL_NAMES - RENDER_TOOL_NAMES:
                placeholder["session"].layer_order.begin_l1_reentry()

        model = record.get("model") or DEFAULT_MODEL
        cwd = record.get("workingDirectory") or str(DEFAULT_WORKSPACE)
        approve_all = bool(record.get("approveAll", False))
        default_plugin_id = str(record.get("defaultPluginId") or DEFAULT_PLUGIN_ID)
        plugin_entry(default_plugin_id)
        iai_system_message = IAI_SYSTEM_MESSAGE
        session_kwargs: dict[str, Any] = {
            "model": model,
            "streaming": True,
            "working_directory": cwd,
            "github_token": self.github_token,
            "on_user_input_request": on_user_input_request,
            "hooks": SessionHooks(
                on_pre_tool_use=on_pre_tool_use,
                on_post_tool_use=on_task_tool_result,
                on_post_tool_use_failure=on_task_tool_result,
            ),
            "tools": build_iai_tools(placeholder) + build_image_tools(placeholder),
            "system_message": {"content": iai_system_message},
        }
        if approve_all:
            session_kwargs["on_permission_request"] = PermissionHandler.approve_all
        else:
            session_kwargs["on_permission_request"] = on_permission_request

        copilot_session = await client.resume_session(session_id, **session_kwargs)
        web_session = WebCopilotSession(
            session=copilot_session,
            model=model,
            working_directory=cwd,
            approve_all=approve_all,
            default_plugin_id=default_plugin_id,
        )
        placeholder["session"] = web_session
        copilot_session.on(lambda event: self._handle_session_event(web_session, event))
        self.sessions[web_session.session_id] = web_session
        return web_session

    def list_stored_sessions(self) -> list[dict[str, Any]]:
        return chat_store.list_sessions()

    def get_stored_session(self, session_id: str) -> dict[str, Any]:
        return chat_store.load_session(session_id)

    def get_stored_messages(self, session_id: str) -> list[dict[str, Any]]:
        return chat_store.get_messages(session_id)

    def get_session(self, session_id: str) -> WebCopilotSession:
        try:
            return self.sessions[session_id]
        except KeyError as error:
            raise SessionNotFoundError(session_id) from error

    async def recover_interrupted_widget(self, session_id: str) -> dict[str, Any]:
        pending = chat_store.pending_widget_request(session_id)
        if pending is None:
            return {"recovered": False}

        metadata = pending.get("metadata") or {}
        widget = metadata.get("widget") or {}
        widget_id = str(metadata.get("widgetId") or widget.get("widget_id") or "")
        if not widget_id:
            raise ValueError("Stored widget request is missing its widget id")

        result = {
            "widget_id": widget_id,
            "action": "dismiss",
            "values": {},
            "freeform_note": "The previous interaction was interrupted.",
        }
        chat_store.append_message(
            session_id=session_id,
            role="widget_return",
            content="dismiss",
            metadata={"widgetId": widget_id, "result": result},
        )
        return {"recovered": True, "widgetId": widget_id}

    async def delete_session(self, session_id: str) -> None:
        session = self.sessions.pop(session_id, None)
        if session is not None:
            await session.session.disconnect()

    async def close(self) -> None:
        for session_id in list(self.sessions):
            with contextlib.suppress(Exception):
                await self.delete_session(session_id)
        if self.client is not None:
            await self.client.stop()
            self.client = None

    def _build_skill_event(
        self,
        web_session: WebCopilotSession,
        kind: str,
        event_payload: dict[str, Any],
    ) -> dict[str, Any] | None:
        data = event_payload.get("data") if isinstance(event_payload, dict) else None
        if not isinstance(data, dict):
            return None

        call_id = data.get("tool_call_id") or data.get("toolCallId")
        call_key = str(call_id) if call_id else ""
        active_call = web_session.active_debug_calls.get(call_key) if call_key else None
        arguments = data.get("arguments") if isinstance(data.get("arguments"), dict) else {}
        tool_name = data.get("tool_name") or data.get("toolName")

        telemetry = data.get("tool_telemetry") if isinstance(data.get("tool_telemetry"), dict) else {}
        restricted = telemetry.get("restrictedProperties") if isinstance(telemetry.get("restrictedProperties"), dict) else {}
        skill_name = arguments.get("skill") if isinstance(arguments.get("skill"), str) else None
        skill_name = skill_name or restricted.get("skillName")
        plugin_name = restricted.get("pluginName")

        category: str | None = None
        name: str | None = None
        display_name: str | None = None
        layer: str | None = None
        preview: dict[str, Any] = {}

        if skill_name or tool_name == "skill":
            category = "skill"
            name = skill_name or (active_call.get("name") if active_call else "skill")
            display_name = name
            layer = infer_iai_layer(name)
            tool_name = "skill"
        elif tool_name in RENDERER_TOOL_NAMES:
            category = "tool"
            name = tool_name
            display_name = renderer_tool_display_name(tool_name)
            layer = "L4"
            preview = compact_tool_preview(tool_name, arguments)
        elif tool_name:
            # Any other tool (generate_image, edit_image, ...) still belongs in
            # the Skill Trace so the chat transcript stays free of tool activity.
            category = "tool"
            name = tool_name
            display_name = tool_name.replace("_", " ")

        if active_call:
            category = category or active_call.get("category")
            name = name or active_call.get("name")
            display_name = display_name or active_call.get("displayName")
            layer = layer or active_call.get("layer")
            tool_name = tool_name or active_call.get("toolName")
            plugin_name = plugin_name or active_call.get("pluginName")
            preview = preview or active_call.get("preview") or {}

        if not category or not name:
            return None

        tracker = getattr(web_session, "layer_order", None)
        if tracker is not None:
            if kind == "tool.execution_start" and category == "skill" and layer:
                tracker.on_skill_load(layer)

        if kind == "tool.execution_start":
            status = "started"
        elif kind == "tool.execution_complete":
            status = "completed" if data.get("success") is not False else "failed"
        else:
            status = kind.rsplit(".", 1)[-1]

        duration_ms: int | None = None
        if kind == "tool.execution_start" and call_key:
            web_session.active_debug_calls[call_key] = {
                "category": category,
                "name": name,
                "displayName": display_name,
                "layer": layer,
                "toolName": tool_name,
                "pluginName": plugin_name,
                "preview": preview,
                "turnId": data.get("turn_id") or data.get("turnId"),
                "parentToolCallId": data.get("parent_tool_call_id") or data.get("parentToolCallId"),
                "startedAt": time.perf_counter(),
            }
        elif kind == "tool.execution_complete" and active_call:
            started_at = active_call.get("startedAt")
            if isinstance(started_at, (int, float)):
                duration_ms = max(0, round((time.perf_counter() - started_at) * 1000))
            if call_key:
                web_session.active_debug_calls.pop(call_key, None)

        error = data.get("error")
        event: dict[str, Any] = {
            "type": "skill_event",
            "eventType": kind,
            "recordId": call_key or str(event_payload.get("id") or uuid.uuid4()),
            "toolCallId": call_key or None,
            "category": category,
            "name": name,
            "displayName": display_name or name,
            "layer": layer,
            "role": "executor" if category == "skill" and name.removeprefix("iai-").startswith("exec-") else None,
            "status": status,
            "timestamp": chat_store.now_iso(),
            "turnId": data.get("turn_id") or data.get("turnId") or (active_call or {}).get("turnId"),
            "parentToolCallId": data.get("parent_tool_call_id") or data.get("parentToolCallId") or (active_call or {}).get("parentToolCallId"),
            "durationMs": duration_ms,
            "success": data.get("success"),
            "error": compact_debug_value(to_jsonable(error)) if error else None,
            "toolName": tool_name,
            "pluginName": plugin_name,
            "preview": preview,
        }
        return {key: value for key, value in event.items() if value is not None}

    def _handle_session_event(self, web_session: WebCopilotSession, event: Any) -> None:
        kind = event_type(event)
        if kind == "assistant.message_delta":
            delta = event_delta_content(event)
            if delta:
                web_session._assistant_buffer.append(delta)
                web_session.emit_nowait({"type": "assistant_delta", "content": delta, "sourceType": kind})
            return

        if kind == "assistant.reasoning_delta":
            return

        if kind == "assistant.message":
            content = event_message_content(event)
            web_session.emit_nowait({"type": "assistant_message", "content": content})
            return

        if kind == "session.idle":
            web_session.emit_nowait({"type": "sdk_session_idle"})
            return

        if kind.startswith("tool.") or kind.startswith("permission."):
            event_payload = to_jsonable(event)
            if kind.startswith("tool."):
                tool_name = event_payload.get("data", {}).get("toolName") or event_payload.get("data", {}).get("tool_name") or kind
                chat_store.append_message(
                    session_id=web_session.session_id,
                    role="tool_event",
                    content=f"{kind}: {tool_name}",
                    metadata={"eventType": kind, "event": event_payload},
                )
                skill_event = self._build_skill_event(web_session, kind, event_payload)
                if skill_event:
                    web_session.emit_nowait(skill_event)
            web_session.emit_nowait(
                {
                    "type": "tool_event",
                    "eventType": kind,
                    "event": event_payload,
                }
            )


service = CopilotWebService()
