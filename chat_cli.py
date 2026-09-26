from __future__ import annotations

import argparse
import asyncio
import os
import shutil
import subprocess
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from copilot import CopilotClient, RuntimeConnection
from copilot.rpc import PermissionDecisionApproveOnce, PermissionDecisionReject
from copilot.session import PermissionHandler

try:
    import readline  # noqa: F401
except ImportError:
    pass


PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_WORKSPACE = PROJECT_DIR
DEFAULT_MODEL = os.getenv("COPILOT_MODEL", "gpt-5.5")


class AuthSetupError(RuntimeError):
    pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Interactive terminal chat frontend for the GitHub Copilot SDK.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Copilot model to use. Defaults to COPILOT_MODEL or {DEFAULT_MODEL}.",
    )
    parser.add_argument(
        "--cwd",
        default=str(DEFAULT_WORKSPACE),
        help=f"Working directory exposed to the Copilot runtime. Defaults to {DEFAULT_WORKSPACE}.",
    )
    parser.add_argument(
        "--auth",
        choices=["github", "runtime"],
        default="github",
        help=(
            "Authentication mode. 'github' uses your GitHub account via gh auth token; "
            "'runtime' relies on credentials already stored by the Copilot runtime."
        ),
    )
    parser.add_argument(
        "--cli-url",
        help="Connect to an already running Copilot CLI server, for example localhost:4321.",
    )
    parser.add_argument(
        "--base-directory",
        help="Directory for Copilot session state. Leave unset to use the normal ~/.copilot location.",
    )
    parser.add_argument(
        "--log-level",
        default="warning",
        choices=["none", "error", "warning", "info", "debug", "all"],
        help="Copilot runtime log level.",
    )
    parser.add_argument(
        "--approve-all",
        action="store_true",
        default=True,
        help="Approve every Copilot tool request automatically. Use only in trusted workspaces.",
    )
    parser.add_argument(
        "--no-approve-all",
        action="store_false",
        dest="approve_all",
        help="Ask before approving Copilot tool requests.",
    )
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="Print complete assistant messages instead of streaming deltas.",
    )
    parser.add_argument(
        "--system",
        help="Additional system instruction appended to the Copilot session.",
    )
    parser.add_argument(
        "--no-infinite-sessions",
        action="store_true",
        help="Disable Copilot SDK infinite-session persistence/compaction.",
    )
    return parser


def get_github_token_from_gh() -> str:
    if shutil.which("gh") is None:
        raise AuthSetupError(
            "GitHub account login requires the GitHub CLI, but 'gh' was not found.\n"
            "Install it with:\n"
            "  brew install gh\n"
            "Then sign in with:\n"
            "  gh auth login --hostname github.com --web"
        )

    status = subprocess.run(
        ["gh", "auth", "status", "--hostname", "github.com"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    if status.returncode != 0:
        raise AuthSetupError(
            "GitHub account login is required before starting the chat UI.\n"
            "Run:\n"
            "  gh auth login --hostname github.com --web\n"
            "Then start this app again."
        )

    token = subprocess.run(
        ["gh", "auth", "token", "--hostname", "github.com"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if token.returncode != 0:
        token = subprocess.run(
            ["gh", "config", "get", "oauth_token", "--host", "github.com"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
    if token.returncode != 0 or not token.stdout.strip():
        raise AuthSetupError(
            "Could not read a GitHub token from gh. Run 'gh auth login --hostname github.com --web' again."
        )

    return token.stdout.strip()


async def async_input(prompt: str) -> str:
    return await asyncio.to_thread(input, prompt)


def permission_request_to_dict(request: Any) -> dict[str, Any]:
    if isinstance(request, dict):
        return request
    if is_dataclass(request):
        return asdict(request)

    interesting_fields = (
        "kind",
        "tool_name",
        "toolName",
        "file_name",
        "fileName",
        "full_command_text",
        "fullCommandText",
        "url",
        "domain",
        "path",
        "command",
        "arguments",
        "memory_action",
        "memoryAction",
    )
    data = {
        field: getattr(request, field)
        for field in interesting_fields
        if hasattr(request, field)
    }
    if data:
        return data

    try:
        return vars(request)
    except TypeError:
        return {"request": repr(request)}


def format_permission_request(request: Any) -> str:
    request_type = type(request).__name__
    fields = permission_request_to_dict(request)
    lines = [f"Permission request: {request_type}"]
    for key, value in fields.items():
        if value is None or key.startswith("_"):
            continue
        text = str(value)
        if len(text) > 500:
            text = text[:497] + "..."
        lines.append(f"  {key}: {text}")
    return "\n".join(lines)


async def prompt_for_permission(request: Any, invocation: dict[str, Any]) -> Any:
    print("\n" + format_permission_request(request), file=sys.stderr)
    while True:
        answer = (await async_input("Allow this tool request once? [y/N] ")).strip().lower()
        if answer in {"y", "yes"}:
            return PermissionDecisionApproveOnce()
        if answer in {"", "n", "no"}:
            return PermissionDecisionReject(feedback="The user rejected this tool request.")
        print("Please answer y or n.", file=sys.stderr)


async def prompt_for_user_input(request: Any, invocation: dict[str, Any]) -> dict[str, Any]:
    if isinstance(request, dict):
        question = request.get("question", "Copilot asks for input")
        choices = request.get("choices") or []
    else:
        question = getattr(request, "question", "Copilot asks for input")
        choices = getattr(request, "choices", None) or []

    print(f"\nCopilot asks: {question}", file=sys.stderr)
    if choices:
        for index, choice in enumerate(choices, start=1):
            print(f"  {index}. {choice}", file=sys.stderr)

    answer = await async_input("Your answer: ")
    return {"answer": answer, "wasFreeform": True}


def event_delta_content(event: Any) -> str:
    data = getattr(event, "data", None)
    return (
        getattr(data, "delta_content", None)
        or getattr(data, "deltaContent", None)
        or ""
    )


def event_message_content(event: Any) -> str:
    data = getattr(event, "data", None)
    return getattr(data, "content", None) or ""


def event_type(event: Any) -> str:
    raw_type = getattr(event, "type", "") or getattr(event, "event_type", "")
    return str(getattr(raw_type, "value", raw_type) or "")


def print_help() -> None:
    print(
        "Commands:\n"
        "  /help      Show this help\n"
        "  /session   Show the current Copilot session id\n"
        "  /exit      Quit\n"
        "\n"
        "Everything else is sent to Copilot as a chat turn."
    )


async def run_chat(args: argparse.Namespace) -> None:
    github_token = get_github_token_from_gh() if args.auth == "github" else None

    client_kwargs: dict[str, Any] = {
        "working_directory": str(Path(args.cwd).expanduser().resolve()),
        "log_level": args.log_level,
    }
    if github_token:
        client_kwargs["github_token"] = github_token
        client_kwargs["use_logged_in_user"] = False
    elif args.auth == "runtime":
        client_kwargs["use_logged_in_user"] = True
    if args.base_directory:
        client_kwargs["base_directory"] = str(Path(args.base_directory).expanduser().resolve())
    if args.cli_url:
        client_kwargs["connection"] = RuntimeConnection.for_uri(args.cli_url)

    session_kwargs: dict[str, Any] = {
        "model": args.model,
        "streaming": not args.no_stream,
        "on_user_input_request": prompt_for_user_input,
    }
    if github_token:
        session_kwargs["github_token"] = github_token
    if args.approve_all:
        session_kwargs["on_permission_request"] = PermissionHandler.approve_all
    else:
        session_kwargs["on_permission_request"] = prompt_for_permission
    if args.system:
        session_kwargs["system_message"] = {"content": args.system}
    if args.no_infinite_sessions:
        session_kwargs["infinite_sessions"] = {"enabled": False}

    async with CopilotClient(**client_kwargs) as client:
        async with await client.create_session(**session_kwargs) as session:
            turn_state = {"streamed": False}

            def on_event(event: Any) -> None:
                kind = event_type(event)
                if kind in {"assistant.message_delta", "assistant.reasoning_delta"}:
                    delta = event_delta_content(event)
                    if delta:
                        turn_state["streamed"] = True
                        print(delta, end="", flush=True)

            session.on(on_event)

            print("Copilot SDK Chat CLI")
            print(f"model: {args.model}")
            print(f"auth: {args.auth}")
            print(f"cwd: {client_kwargs['working_directory']}")
            print("type /help for commands, /exit to quit\n")

            while True:
                try:
                    user_input = (await async_input("You: ")).strip()
                except (EOFError, KeyboardInterrupt):
                    print()
                    break

                if not user_input:
                    continue

                command = user_input.lower()
                if command in {"/exit", "/quit", "exit", "quit"}:
                    break
                if command == "/help":
                    print_help()
                    continue
                if command == "/session":
                    print(f"session id: {session.session_id}")
                    continue

                turn_state["streamed"] = False
                print("Copilot: ", end="", flush=True)
                response = await session.send_and_wait(user_input, timeout=None)
                if not turn_state["streamed"] and response is not None:
                    content = event_message_content(response)
                    if content:
                        print(content, end="", flush=True)
                print("\n")


def main() -> None:
    args = build_parser().parse_args()
    try:
        asyncio.run(run_chat(args))
    except AuthSetupError as error:
        print(f"\nAuthentication setup needed:\n{error}\n", file=sys.stderr)
        raise SystemExit(2) from error
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()
