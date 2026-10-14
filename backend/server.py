from __future__ import annotations

import os
import webbrowser
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from chat_cli import AuthSetupError, DEFAULT_MODEL, DEFAULT_WORKSPACE
from backend.services.copilot_service import SessionNotFoundError, service
from backend.services import chat_store, uploads_store
from backend.services.inflak_plugins import PluginRegistryError, public_plugins
from backend.services.plugin_tools.author import scenario_runner as plugin_scenario_runner
from backend.services.plugin_tools.collage import accessibility as svg_accessibility
from backend.services.plugin_tools.collage import document_manager as svg_document_manager
from backend.services.plugin_tools.collage import svg_collage
from backend.services.plugin_tools.reporting import reports as p9_reports


PROJECT_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = PROJECT_DIR / "frontend"
NO_CACHE_HEADERS = {"Cache-Control": "no-store"}
HTML_PREVIEW_HEADERS = {
    **NO_CACHE_HEADERS,
    "Content-Security-Policy": "sandbox; default-src 'none'; style-src 'unsafe-inline'; img-src data:; font-src data:",
    "X-Content-Type-Options": "nosniff",
}


class CreateSessionRequest(BaseModel):
    model: str = DEFAULT_MODEL
    working_directory: str | None = None
    system_message: str | None = None
    approve_all: bool = True
    default_plugin_id: str = "inflak-main"


class SessionFavoriteRequest(BaseModel):
    favorite: bool


class PluginScenarioRequest(BaseModel):
    case_id: str | None = None
    timeout_seconds: float = 120


class SvgCollagePatchRequest(BaseModel):
    base_revision: int
    operations: list[dict[str, Any]]


class SvgAccessibilityPatchRequest(BaseModel):
    base_revision: int
    operations: list[dict[str, Any]]


app = FastAPI(title="Inflak Demo", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if (FRONTEND_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")


@app.on_event("startup")
async def open_browser_on_startup() -> None:
    if os.getenv("COPILOT_OPEN_BROWSER") == "1":
        marker = os.getenv("COPILOT_BROWSER_MARKER")
        if marker:
            try:
                Path(marker).touch(exist_ok=False)
            except FileExistsError:
                return
            except OSError:
                pass
        url = os.getenv("COPILOT_WEB_URL", "http://127.0.0.1:8002")
        webbrowser.open(url)


@app.on_event("shutdown")
async def shutdown() -> None:
    await service.close()


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html", headers=NO_CACHE_HEADERS)


@app.get("/styles.css")
async def styles() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "styles.css", headers=NO_CACHE_HEADERS)


@app.get("/app.js")
async def app_js() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "app.js", headers=NO_CACHE_HEADERS)


@app.get("/artifact-canvas.js")
async def artifact_canvas_js() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "artifact-canvas.js", headers=NO_CACHE_HEADERS)


@app.get("/artifact-canvas.css")
async def artifact_canvas_css() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "artifact-canvas.css", headers=NO_CACHE_HEADERS)


@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "ok": True,
        "defaultModel": DEFAULT_MODEL,
        "workspace": str(DEFAULT_WORKSPACE),
        "projectDir": str(PROJECT_DIR),
    }


@app.get("/api/models")
async def models() -> dict[str, Any]:
    try:
        return {"models": await service.list_models()}
    except AuthSetupError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error


@app.get("/api/inflak/plugins")
async def inflak_plugins() -> dict[str, Any]:
    return {"plugins": public_plugins(), "defaultPluginId": "inflak-main"}


@app.get("/api/inflak/plugins/{plugin_id}/scenarios")
async def plugin_scenarios(plugin_id: str) -> dict[str, Any]:
    try:
        return {
            "plugin_id": plugin_id,
            "cases": plugin_scenario_runner.installed_cases(plugin_id),
            "runs": plugin_scenario_runner.list_runs(plugin_id),
        }
    except (PluginRegistryError, plugin_scenario_runner.PluginScenarioError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/inflak/plugins/{plugin_id}/scenarios/probe")
async def run_plugin_probe(plugin_id: str, request: PluginScenarioRequest) -> dict[str, Any]:
    if request.timeout_seconds < 5 or request.timeout_seconds > 600:
        raise HTTPException(status_code=400, detail="timeout_seconds must be between 5 and 600.")
    try:
        run = await plugin_scenario_runner.run_probe_case(
            service,
            plugin_id,
            case_id=request.case_id,
            timeout_seconds=request.timeout_seconds,
        )
    except (PluginRegistryError, plugin_scenario_runner.PluginScenarioError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except AuthSetupError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error
    return {**run, "session_url": f"/?session={run['session_id']}", "report_url": f"/api/inflak/plugins/{plugin_id}/scenario-runs/{run['run_id']}/report"}


@app.post("/api/inflak/plugins/{plugin_id}/scenarios/interactive")
async def start_interactive_plugin_scenario(plugin_id: str, request: PluginScenarioRequest) -> dict[str, Any]:
    try:
        run = await plugin_scenario_runner.start_interactive_case(service, plugin_id, case_id=request.case_id)
    except (PluginRegistryError, plugin_scenario_runner.PluginScenarioError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except AuthSetupError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error
    return {**run, "session_url": f"/?session={run['session_id']}", "report_url": f"/api/inflak/plugins/{plugin_id}/scenario-runs/{run['run_id']}/report"}


@app.get("/api/inflak/plugins/{plugin_id}/scenario-runs")
async def plugin_scenario_runs(plugin_id: str) -> dict[str, Any]:
    return {"plugin_id": plugin_id, "runs": plugin_scenario_runner.list_runs(plugin_id)}


@app.get("/api/inflak/plugins/{plugin_id}/scenario-runs/{run_id}")
async def plugin_scenario_run(plugin_id: str, run_id: str) -> dict[str, Any]:
    try:
        return plugin_scenario_runner.refresh_run(plugin_id, run_id)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail="Scenario run not found") from error


@app.get("/api/inflak/plugins/{plugin_id}/scenario-runs/{run_id}/report")
async def plugin_scenario_report(plugin_id: str, run_id: str) -> FileResponse:
    try:
        run = plugin_scenario_runner.load_run(plugin_id, run_id)
        path = plugin_scenario_runner.report_path(plugin_id, run_id)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail="Scenario run not found") from error
    return FileResponse(path, media_type="text/markdown", filename=f"{run_id}-SCENARIO-REPORT.md", headers=NO_CACHE_HEADERS)


@app.post("/api/sessions")
async def create_session(request: CreateSessionRequest) -> dict[str, Any]:
    try:
        session = await service.create_session(
            model=request.model,
            working_directory=request.working_directory,
            system_message=request.system_message,
            approve_all=request.approve_all,
            default_plugin_id=request.default_plugin_id,
        )
    except AuthSetupError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error
    except PluginRegistryError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(error)) from error

    return {
        "sessionId": session.session_id,
        "model": session.model,
        "actualModel": session.actual_model,
        "workingDirectory": session.working_directory,
        "defaultPluginId": session.default_plugin_id,
    }


@app.get("/api/sessions")
async def list_sessions() -> dict[str, Any]:
    return {"sessions": service.list_stored_sessions()}


@app.get("/api/sessions/{session_id}")
async def get_session_record(session_id: str) -> dict[str, Any]:
    try:
        return service.get_stored_session(session_id)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail="Session not found") from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.patch("/api/sessions/{session_id}/favorite")
async def update_session_favorite(session_id: str, request: SessionFavoriteRequest) -> dict[str, Any]:
    try:
        record = chat_store.set_session_favorite(session_id, request.favorite)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail="Session not found") from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {"sessionId": record["sessionId"], "favorite": bool(record.get("favorite", False))}


@app.delete("/api/sessions/{session_id}")
async def delete_stored_session(session_id: str) -> dict[str, Any]:
    try:
        chat_store.load_session(session_id)
        await service.delete_session(session_id)
        deletion = chat_store.delete_session_record(session_id)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail="Session not found") from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(error)) from error
    return {**deletion, "deleted": True}


@app.get("/api/sessions/{session_id}/messages")
def get_session_messages(session_id: str) -> dict[str, Any]:
    try:
        messages = service.get_stored_messages(session_id)
        record = chat_store.load_session(session_id)
        messages = [
            p9_reports.prepare_message(session_id, message)
            if (message.get("metadata") or {}).get("pluginId", record.get("defaultPluginId")) == p9_reports.PLUGIN_ID
            else message
            for message in messages
        ]
        return {"messages": messages}
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail="Session not found") from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/sessions/{session_id}/resume")
async def resume_session(session_id: str) -> dict[str, Any]:
    try:
        session = await service.resume_session(session_id)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail="Session not found") from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(error)) from error

    return {
        "sessionId": session.session_id,
        "model": session.model,
        "actualModel": session.actual_model,
        "workingDirectory": session.working_directory,
        "resumed": True,
    }


@app.post("/api/sessions/{session_id}/recover-interrupted-widget")
async def recover_interrupted_widget(session_id: str) -> dict[str, Any]:
    try:
        return await service.recover_interrupted_widget(session_id)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail="Session not found") from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/sessions/{session_id}/uploads")
async def upload_files(session_id: str, files: list[UploadFile] = File(...)) -> dict[str, Any]:
    try:
        chat_store.safe_session_id(session_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    saved: list[dict[str, Any]] = []
    for upload in files:
        content = await upload.read()
        try:
            attachment = uploads_store.save_upload(
                session_id=session_id,
                filename=upload.filename or "upload.bin",
                content=content,
                mime=upload.content_type,
            )
            if Path(attachment["path"]).suffix.lower() == ".svg":
                try:
                    scene = svg_document_manager.normalize_document(
                        Path(attachment["path"]),
                        document_id=attachment["fileId"],
                        source_kind="upload",
                    )
                except svg_document_manager.SvgDocumentError:
                    Path(attachment["path"]).unlink(missing_ok=True)
                    raise
                attachment.update({"artifactType": "svg-document", "revision": scene["revision"], "scene": scene})
            saved.append(attachment)
        except uploads_store.UploadTooLargeError as error:
            raise HTTPException(status_code=413, detail=f"File too large: {error}") from error
        except uploads_store.UploadTypeNotAllowedError as error:
            raise HTTPException(status_code=415, detail=f"Unsupported file type: {error}") from error
        except svg_document_manager.SvgDocumentError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
    if saved:
        try:
            chat_store.touch_session(session_id)
        except FileNotFoundError:
            pass
    return {"attachments": saved}


@app.get("/api/sessions/{session_id}/uploads")
async def list_uploads(session_id: str) -> dict[str, Any]:
    try:
        uploads = uploads_store.list_uploads(session_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    for upload in uploads:
        upload["url"] = f"/api/sessions/{session_id}/uploads/{upload['fileId']}"
        path = uploads_store.upload_path(session_id, upload["fileId"])
        if path is not None and path.suffix.lower() == ".svg":
            try:
                scene = svg_document_manager.inspect_document(path, document_id=upload["fileId"])
            except svg_document_manager.SvgDocumentError:
                continue
            upload.update({"artifactType": "svg-document", "revision": scene["revision"], "scene": scene})
    return {"attachments": uploads}


@app.get("/api/sessions/{session_id}/uploads/{file_id}")
async def download_upload(session_id: str, file_id: str) -> FileResponse:
    try:
        chat_store.safe_session_id(session_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    path = uploads_store.upload_path(session_id, file_id)
    if path is None:
        raise HTTPException(status_code=404, detail="Upload not found")
    return FileResponse(path, headers=NO_CACHE_HEADERS)


@app.get("/api/sessions/{session_id}/uploads/{file_id}/preview")
async def preview_html_upload(session_id: str, file_id: str) -> FileResponse:
    try:
        chat_store.safe_session_id(session_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    path = uploads_store.upload_path(session_id, file_id)
    if path is None:
        raise HTTPException(status_code=404, detail="Upload not found")
    if uploads_store.infer_mime(path.name) != "text/html":
        raise HTTPException(status_code=415, detail="Only HTML uploads can be previewed")
    return FileResponse(path, media_type="text/html", headers=HTML_PREVIEW_HEADERS)


@app.get("/api/sessions/{session_id}/widget-assets/{asset_path:path}")
async def download_widget_asset(session_id: str, asset_path: str) -> FileResponse:
    try:
        path = uploads_store.runtime_image_path(session_id, asset_path)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if path is None:
        raise HTTPException(status_code=404, detail="Widget image not found")
    return FileResponse(path, headers=NO_CACHE_HEADERS)


@app.post("/api/sessions/{session_id}/svg-collages/{file_id}/patch")
async def patch_svg_collage(session_id: str, file_id: str, request: SvgCollagePatchRequest) -> dict[str, Any]:
    try:
        path = uploads_store.upload_path(session_id, file_id)
        if path is None or path.suffix.lower() != ".svg":
            raise HTTPException(status_code=404, detail="SVG collage artifact not found")
        scene = svg_collage.apply_svg_collage_patch(
            path,
            request.base_revision,
            request.operations,
            session_id=session_id,
        )
    except svg_collage.SvgCollageError as error:
        status_code = 409 if "Revision conflict" in str(error) else 400
        raise HTTPException(status_code=status_code, detail=str(error)) from error
    return {
        "attachment": {
            "fileId": file_id,
            "name": path.name.split("-", 1)[-1],
            "mime": "image/svg+xml",
            "size": path.stat().st_size,
            "artifactType": "svg-collage",
            "revision": scene["revision"],
            "scene": scene,
            "url": f"/api/sessions/{session_id}/uploads/{file_id}",
        }
    }


@app.post("/api/sessions/{session_id}/svg-documents/{file_id}/patch")
async def patch_svg_document(session_id: str, file_id: str, request: SvgCollagePatchRequest) -> dict[str, Any]:
    path = uploads_store.upload_path(session_id, file_id)
    if path is None or path.suffix.lower() != ".svg":
        raise HTTPException(status_code=404, detail="SVG document not found")
    try:
        result = svg_document_manager.patch_document(
            path,
            document_id=file_id,
            session_id=session_id,
            base_revision=request.base_revision,
            operations=request.operations,
        )
    except svg_document_manager.SvgDocumentError as error:
        status_code = 409 if "Revision conflict" in str(error) else 400
        raise HTTPException(status_code=status_code, detail=str(error)) from error
    scene = result["scene"]
    return {
        "attachment": {
            "fileId": file_id,
            "name": path.name.split("-", 1)[-1],
            "mime": "image/svg+xml",
            "size": path.stat().st_size,
            "artifactType": "svg-document",
            "revision": scene["revision"],
            "scene": scene,
            "url": f"/api/sessions/{session_id}/uploads/{file_id}",
        },
        "appliedOperations": result["applied_operations"],
    }


@app.get("/api/sessions/{session_id}/svg-figures/{file_id}/inspect")
async def inspect_svg_figure(session_id: str, file_id: str) -> dict[str, Any]:
    path = uploads_store.upload_path(session_id, file_id)
    if path is None or path.suffix.lower() != ".svg":
        raise HTTPException(status_code=404, detail="SVG figure not found")
    try:
        return {"fileId": file_id, **svg_accessibility.inspect_svg(path)}
    except svg_accessibility.SvgAccessibilityError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/sessions/{session_id}/svg-figures/{file_id}/patch")
async def patch_svg_figure(session_id: str, file_id: str, request: SvgAccessibilityPatchRequest) -> dict[str, Any]:
    path = uploads_store.upload_path(session_id, file_id)
    if path is None or path.suffix.lower() != ".svg":
        raise HTTPException(status_code=404, detail="SVG figure not found")
    try:
        result = svg_accessibility.apply_svg_patch(path, request.base_revision, request.operations)
    except svg_accessibility.SvgAccessibilityError as error:
        status_code = 409 if "Revision conflict" in str(error) else 400
        raise HTTPException(status_code=status_code, detail=str(error)) from error
    return {
        "attachment": {
            "fileId": file_id,
            "name": path.name.split("-", 1)[-1],
            "mime": "image/svg+xml",
            "size": path.stat().st_size,
            "artifactType": "svg-figure",
            "revision": result["revision"],
            "url": f"/api/sessions/{session_id}/uploads/{file_id}",
        },
        "appliedOperations": result["applied_operations"],
        "accessibilityReport": result["report"],
    }


@app.websocket("/ws/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str) -> None:
    await websocket.accept()
    try:
        session = await service.resume_session(session_id)
    except (FileNotFoundError, SessionNotFoundError):
        await websocket.send_json({"type": "error", "message": "Session not found."})
        await websocket.close(code=4404)
        return

    session.connected = True
    await websocket.send_json(
        {
            "type": "session_ready",
            "sessionId": session.session_id,
            "model": session.model,
            "configuredModel": session.model,
            "actualModel": session.actual_model,
            "modelSource": session.actual_model_source,
            "workingDirectory": session.working_directory,
            "defaultPluginId": session.default_plugin_id,
        }
    )
    for widget_id, widget in session.pending_widget_contracts.items():
        await websocket.send_json({"type": "widget_render", "widgetId": widget_id, "widget": widget})
    for request_id, request in session.pending_user_inputs.items():
        await websocket.send_json({
            "type": "user_input_request",
            "requestId": request_id,
            "question": request.get("question"),
            "choices": request.get("choices") or [],
            "invocation": request.get("invocation") or {},
        })
    event_subscription = session.subscribe_events()

    async def send_events() -> None:
        while True:
            event = await event_subscription.get()
            await websocket.send_json(event)

    import asyncio

    sender = asyncio.create_task(send_events())

    try:
        while True:
            payload = await websocket.receive_json()
            if not isinstance(payload, dict):
                await websocket.send_json({"type": "error", "message": "Invalid message payload."})
                continue

            event_type = str(payload.get("type", ""))
            request_id = payload.get("requestId") or payload.get("request_id")

            if event_type == "message":
                content = str(payload.get("content") or "").strip()
                attachments = payload.get("attachments") or []
                plugin_id = payload.get("pluginId") or payload.get("plugin_id")
                if not content and not attachments:
                    await websocket.send_json({"type": "error", "message": "Message content is empty."})
                    continue
                import asyncio

                asyncio.create_task(session.send_message(content, attachments=attachments, plugin_id=plugin_id))
            elif event_type == "permission_response":
                if not request_id:
                    await websocket.send_json({"type": "error", "message": "Missing permission request id."})
                    continue
                if not session.resolve_permission(str(request_id), bool(payload.get("approved"))):
                    await websocket.send_json({"type": "error", "message": "Permission request was not pending."})
            elif event_type == "user_input_response":
                if not request_id:
                    await websocket.send_json({"type": "error", "message": "Missing user input request id."})
                    continue
                if not session.resolve_user_input(str(request_id), str(payload.get("answer") or "")):
                    await websocket.send_json({"type": "error", "message": "User input request was not pending."})
            elif event_type == "widget_interaction":
                widget_id = payload.get("widgetId") or payload.get("widget_id")
                interaction = payload.get("interaction")
                if not widget_id or not isinstance(interaction, dict):
                    await websocket.send_json({"type": "error", "message": "Widget interaction requires an id and interaction object."})
                    continue
                if str(widget_id) not in session.pending_widget_contracts:
                    await websocket.send_json({"type": "error", "message": "Widget request was not pending."})
                    continue
                chat_store.append_message(
                    session_id=session.session_id,
                    role="widget_interaction",
                    content=str(interaction.get("type") or "interaction"),
                    metadata={
                        "widgetId": str(widget_id),
                        "sequence": payload.get("sequence"),
                        "interaction": interaction,
                    },
                )
            elif event_type in {"widget_return", "widget_dismiss"}:
                widget_id = payload.get("widgetId") or payload.get("widget_id")
                if not widget_id:
                    await websocket.send_json({"type": "error", "message": "Missing widget id."})
                    continue
                result = {
                    "widget_id": str(widget_id),
                    "planner_id": payload.get("plannerId") or payload.get("planner_id"),
                    "action": payload.get("action") or ("dismiss" if event_type == "widget_dismiss" else "accept"),
                    "values": payload.get("values") or {},
                    "control_state": payload.get("controlState") or payload.get("control_state") or [],
                    "freeform_note": payload.get("freeformNote") or payload.get("freeform_note") or "",
                    "timestamp": payload.get("timestamp"),
                }
                if not session.resolve_widget(str(widget_id), result):
                    await websocket.send_json({"type": "error", "message": "Widget request was not pending."})
            elif event_type == "workspace_patch":
                workspace_id = payload.get("workspaceId") or payload.get("workspace_id")
                state = payload.get("state") or {}
                if not workspace_id or not isinstance(state, dict):
                    await websocket.send_json({"type": "error", "message": "Workspace patch requires an id and object state."})
                    continue
                if not await session.update_workspace(str(workspace_id), state):
                    await websocket.send_json({"type": "error", "message": "Workspace request was not pending."})
            elif event_type in {"workspace_submit", "workspace_dismiss"}:
                workspace_id = payload.get("workspaceId") or payload.get("workspace_id")
                if not workspace_id:
                    await websocket.send_json({"type": "error", "message": "Missing workspace id."})
                    continue
                result = {
                    "workspace_id": str(workspace_id),
                    "planner_id": payload.get("plannerId") or payload.get("planner_id"),
                    "action": payload.get("action") or ("dismiss" if event_type == "workspace_dismiss" else "accept"),
                    "values": payload.get("values") or payload.get("state") or {},
                    "freeform_note": payload.get("freeformNote") or payload.get("freeform_note") or "",
                    "timestamp": payload.get("timestamp"),
                }
                if not session.resolve_workspace(str(workspace_id), result):
                    await websocket.send_json({"type": "error", "message": "Workspace request was not pending."})
            else:
                await websocket.send_json({"type": "error", "message": f"Unknown event type: {event_type}"})
    except WebSocketDisconnect:
        session.connected = False
    finally:
        session.unsubscribe_events(event_subscription)
        sender.cancel()
