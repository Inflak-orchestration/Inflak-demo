"""Runtime layer-order enforcement for the inflak plugin.

The roles are L1 Router, L2 Planner, L3 Designer, and L4 Renderer:

    Interaction Pathway: user/return -> L1 -> L2 -> L3 -> L4 -> widget
    Execution Pathway: user/return -> L1 -> L2 plan -> execute/realize -> L1
    Host Agent Return: user -> L1 -> host agent
    Completion: L1 decides to end after reviewing the current state

L2 directly invokes the executor; L3 owns interaction design only, not task
execution. Every widget return or tool result re-enters L1 for reassessment.
Skill loads (L1..L4) happen inside the Copilot SDK plugin subprocess. The
session pre-tool hook rejects every non-L1 skill and ordinary tool while an
initial entry or result re-entry is pending, before that tool starts. The
backend also gates the two effects that it owns:

  * widget rendering (``render_html_widget`` / ``render_interactive_widget``), and
  * task tools (``generate_image``, ``edit_image``, ``adjust_image``, ...).

This tracker observes the sequence of layer skill loads within the current pass
(fed from the skill-load events) and lets the effect tools check that the pass
reached the required layer through ``L1 -> L2`` (task tool) or ``L1 -> L2 -> L3``
(widget render). Widget returns and task-tool results close the pass and require
the next started skill to be L1.

Enforcement can be disabled with ``IAI_ENFORCE_LAYER_ORDER=0``.
"""

from __future__ import annotations

import os
import threading

_LAYER_TO_INT = {"L1": 1, "L2": 2, "L3": 3, "L4": 4}

RENDER_TOOL_NAMES = frozenset({"render_html_widget", "render_interactive_widget", "render_canvas_workspace"})
IMAGE_TOOL_NAMES = frozenset(
    {
        "generate_image",
        "edit_image",
        "restyle_image",
        "outpaint_image",
        "remove_background",
        "extract_collage_cutouts",
        "replace_background",
        "generate_variations",
        "transform_image",
        "adjust_image",
        "apply_filter",
        "compose_collage",
        "compose_svg_collage",
    }
)
WORKFLOW_TOOL_NAMES = frozenset({"export_prompt_tree"})
SVG_ACCESSIBILITY_TOOL_NAMES = frozenset({"inspect_svg_accessibility", "patch_svg_accessibility"})
COLLAGE_INSTRUCTION_TOOL_NAMES = frozenset({"inspect_svg_collage"})
SVG_DOCUMENT_TOOL_NAMES = frozenset({"manage_svg_document", "inspect_svg_scene", "apply_svg_presentation", "apply_svg_layout", "apply_svg_structure"})
EFFECT_TOOL_NAMES = RENDER_TOOL_NAMES | IMAGE_TOOL_NAMES | WORKFLOW_TOOL_NAMES | SVG_ACCESSIBILITY_TOOL_NAMES | COLLAGE_INSTRUCTION_TOOL_NAMES | SVG_DOCUMENT_TOOL_NAMES

# Classification is descriptive; it does not relax the existing layer-order guard.
TOOL_EFFECT_KINDS = {
    **{name: "mutation" for name in EFFECT_TOOL_NAMES},
    **{name: "interaction" for name in RENDER_TOOL_NAMES},
    "inspect_svg_accessibility": "observation",
    "inspect_svg_collage": "observation",
    "inspect_svg_scene": "observation",
}


def enforcement_enabled() -> bool:
    return os.getenv("IAI_ENFORCE_LAYER_ORDER", "1") != "0"


def _is_ordered_subsequence(needle: list[int], haystack: list[int]) -> bool:
    """True if ``needle`` appears as an ordered (not necessarily contiguous)
    subsequence of ``haystack``."""
    it = iter(haystack)
    return all(any(item == want for item in it) for want in needle)


class LayerOrderTracker:
    """Per-session state machine over the IAI layer sequence of the current pass."""

    def __init__(
        self,
        *,
        enforce_initial_l1: bool | None = None,
        enforce_transitions: bool | None = None,
    ) -> None:
        default_enforcement = enforcement_enabled()
        self._enforce_initial_l1 = (
            default_enforcement if enforce_initial_l1 is None else enforce_initial_l1
        )
        self._enforce_transitions = (
            default_enforcement if enforce_transitions is None else enforce_transitions
        )
        self._pass: list[int] = []
        self._initial_l1_required = False
        self._needs_l1_decision = False
        self._l1_reentry_required = False
        self._lock = threading.Lock()

    # -- observation (driven by skill-load / effect-completion events) --------

    def begin_turn(self) -> None:
        """Require the first decision in a new user turn to come from Layer 1."""
        if not self._enforce_initial_l1:
            return
        with self._lock:
            self._pass = []
            self._initial_l1_required = True
            self._needs_l1_decision = False
            self._l1_reentry_required = False

    def on_skill_load(self, layer: str | None) -> None:
        """Record that a layer skill was loaded. ``L1`` starts a fresh pass."""
        n = _LAYER_TO_INT.get((layer or "").upper())
        if n is None:
            return
        with self._lock:
            if n == 1:
                self._pass = [1]
                self._initial_l1_required = False
                self._needs_l1_decision = False
                self._l1_reentry_required = False
            elif not self._pass or self._pass[-1] != n:
                self._pass.append(n)
                self._needs_l1_decision = True

    def begin_l1_reentry(self) -> None:
        """Close downstream execution until Layer 1 reviews the current state."""
        if not self._enforce_transitions:
            return
        with self._lock:
            self._l1_reentry_required = True

    def block_pre_tool(self, tool_name: str, skill_layer: str | None = None) -> dict | None:
        """Reject every tool except an L1 skill while an L1 entry is required."""
        with self._lock:
            initial_l1_required = self._initial_l1_required
            reentry_required = self._l1_reentry_required
        if not initial_l1_required and not reentry_required:
            return None
        if tool_name == "skill" and (skill_layer or "").upper() == "L1":
            return None
        error = "missing_initial_l1" if initial_l1_required else "l1_reentry_required"
        boundary = "this turn" if initial_l1_required else "the latest external result"
        return {
            "action": "error",
            "error": error,
            "message": (
                f"Refused {tool_name}: {boundary} requires Layer 1 as the first skill load. "
                "Load the selected plugin's Layer 1 skill before any other skill or tool."
            ),
        }

    def snapshot(self) -> list[int]:
        with self._lock:
            return list(self._pass)

    # -- enforcement (called from inside the effect tools) --------------------

    def _blocked(self, required: list[int], effect_label: str, tool_name: str) -> dict | None:
        with self._lock:
            initial_l1_required = self._initial_l1_required
            reentry_required = self._l1_reentry_required
            seen = list(self._pass)
        if initial_l1_required:
            return {
                "action": "error",
                "error": "missing_initial_l1",
                "message": (
                    f"Refused {tool_name}: this turn must enter the selected inflak plugin "
                    "through Layer 1 before any Host decision or downstream effect."
                ),
            }
        if not self._enforce_transitions:
            return None
        if reentry_required:
            return {
                "action": "error",
                "error": "l1_reentry_required",
                "message": (
                    f"Refused {tool_name}: downstream execution is closed until Layer 1 "
                    "reconstructs the current workflow state and decides whether to continue or end."
                ),
            }
        if _is_ordered_subsequence(required, seen):
            return None
        need = " -> ".join(f"L{n}" for n in required)
        seen_text = " -> ".join(f"L{n}" for n in seen) if seen else "(no layer loaded)"
        return {
            "action": "error",
            "error": "layer_order_violation",
            "message": (
                f"Refused {tool_name}: an IAI {effect_label} must be reached through "
                f"{need} on the current pass, but the observed layer sequence since the "
                f"last effect is {seen_text}. Re-enter Layer 1 (l1-router) and "
                f"route through the planner (and, for a widget, a Layer 3 widget skill) "
                f"before this effect."
            ),
        }

    def block_render(self, tool_name: str) -> dict | None:
        """Return an error contract if a widget render is not preceded by
        L1 -> L2 -> L3 on the current pass, else ``None``."""
        return self._blocked([1, 2, 3], "widget render", tool_name)

    def block_tool(self, tool_name: str) -> dict | None:
        """Return an error contract if a task tool is not preceded by L1 -> L2 on
        the current pass, else ``None``."""
        return self._blocked([1, 2], "task tool", tool_name)

    def block_completion(self) -> dict | None:
        """Require L1 to review downstream work before the response completes."""
        with self._lock:
            initial_l1_required = self._initial_l1_required
            needs_l1_decision = self._needs_l1_decision
            if not self._needs_l1_decision:
                if not initial_l1_required:
                    return None
            seen = list(self._pass)
        if initial_l1_required:
            return {
                "action": "error",
                "error": "missing_initial_l1",
                "message": (
                    "Refused workflow completion: this turn has not entered the selected "
                    "inflak plugin through Layer 1. Load Layer 1 before deciding whether "
                    "to answer at the Host boundary or continue downstream."
                ),
            }
        if not self._enforce_transitions or not needs_l1_decision:
            return None
        seen_text = " -> ".join(f"L{n}" for n in seen) if seen else "(no layer loaded)"
        return {
            "action": "error",
            "error": "l1_reentry_required",
            "message": (
                "Refused workflow completion: downstream layer work occurred after "
                f"the latest Layer 1 entry ({seen_text}). Re-enter Layer 1 so it can "
                "reconstruct the current state and decide whether to continue or end."
            ),
        }
