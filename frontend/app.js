import { addArtifactCanvasArtifacts, applyArtifactCanvasWidgetValues, closeArtifactCanvas, commandArtifactCanvasLayoutDraft, completeArtifactCanvasWidgets, currentArtifactCanvasSvg, focusArtifactCanvasBinding, initArtifactCanvas, isArtifactCanvasPlugin, mergeArtifactCanvasLayoutDraft, mountArtifactCanvasWidget, openArtifactCanvas, previewArtifactCanvasLayoutDraft, resolveArtifactCanvasWidget, setArtifactCanvasBusy } from "/artifact-canvas.js?v=20260920-no-collage-flash-3";

const DEFAULT_MODEL = "gpt-5.5";
const MAX_SKILL_TRACE_ITEMS = 100;
const P10_PLUGIN_ID = "inflak-pN10-artifact-to-multimodal-instruction";
const P11_PLUGIN_ID = "inflak-pN11-artifact-driven-prompt-enhancement";
const P12_PLUGIN_ID = "inflak-pN12-interactive-artifact-refinement";
const COLLAGE_AUTHORING_PLUGIN_ID = "inflak-collage-authoring";
const SESSION_PLUGIN_TASK_LABELS = {
  "inflak-main": "General co-creation",
  "inflak-author": "Plugin authoring",
  "inflak-pN1-user-driven-prompt-refinement": "User-driven prompt refinement",
  "inflak-pN2-user-driven-prompt-organization": "User-driven prompt organization",
  "inflak-pN3-interaction-as-part-of-instruction": "Interaction as part of instruction",
  "inflak-pN4-referenced-artifact-as-instruction": "Referenced artifact as instruction",
  "inflak-pN5-ai-driven-prompt-suggestion": "AI-driven prompt suggestion",
  "inflak-pN6-ai-driven-prompt-decomposition": "AI-driven prompt decomposition",
  "inflak-pN7-generative-prompt-control-widgets": "Generative prompt control widgets",
  "inflak-pN8-generative-artifact-control-widgets": "Generative artifact control widgets",
  "inflak-pN9-artifact-to-structured-instruction": "Artifact to structured instruction",
  [P10_PLUGIN_ID]: "Artifact to multimodal instruction",
  [P11_PLUGIN_ID]: "Artifact-driven prompt enhancement",
  [P12_PLUGIN_ID]: "Interactive artifact refinement",
  [COLLAGE_AUTHORING_PLUGIN_ID]: "Collage authoring",
  "inflak-pN13-ai-proactively-initiated-interaction": "AI-proactively-initiated interaction",
  "inflak-daily-paper-conclusion": "Daily paper digest",
};

function normalizePluginId(pluginId) {
  return pluginId || "inflak-main";
}

const state = {
  models: [],
  plugins: [],
  sessions: [],
  sessionQuery: "",
  favoriteSessionsCollapsed: false,
  currentSessionId: null,
  socket: null,
  liveSessionId: null,
  isBusy: false,
  pendingAssistantId: null,
  pendingModal: null,
  attachments: [],
  canvasPendingArtifacts: [],
};

initArtifactCanvas({
  onUpload: uploadCanvasArtifacts,
  onAnalyze: analyzeCanvasArtifact,
  onError: showToast,
  onWidgetStale: handleStaleArtifactCanvasWidget,
  onComparisonDecision: handleArtifactComparisonDecision,
  onArtifactPatch: (attachment) => {
    const session = currentSession();
    if (session) session.updatedAt = new Date().toISOString();
    addArtifactCanvasArtifacts([attachment]);
  },
});

function handleArtifactComparisonDecision({ widgetId, widget, action, fileId, beforeRevision, afterRevision }) {
  const session = currentSession();
  if (!session) return false;
  const message = session.messages.findLast((item) => item.role === "widget"
    && item.status === "pending"
    && (item.widgetId || item.widget?.widget_id) === widgetId);
  if (!message) return false;
  const values = {
    action,
    file_id: fileId,
    before_revision: beforeRevision,
    after_revision: afterRevision,
  };
  const sent = sendSocket({
    type: "widget_return",
    widgetId,
    plannerId: widget.planner_id,
    action: "accept",
    values,
    freeformNote: "",
    timestamp: new Date().toISOString(),
  });
  if (!sent) return false;
  message.status = "submitted";
  message.returnValues = values;
  renderMessages();
  return true;
}

function handleStaleArtifactCanvasWidget({ sessionId, widgetId, widget, artifactId, baseRevision, currentRevision }) {
  const session = currentSession();
  if (!session || session.id !== sessionId) return false;
  const message = session.messages.findLast((item) =>
    item.role === "widget"
    && item.status === "pending"
    && (item.widgetId || item.widget?.widget_id) === widgetId);
  const values = {
    reason: "artifact_revision_changed",
    artifact_id: artifactId,
    base_revision: baseRevision,
    current_revision: currentRevision,
    action: "interrupted",
  };
  const sent = sendSocket({
    type: "widget_return",
    widgetId,
    plannerId: widget?.planner_id,
    action: "interrupted",
    values,
    freeformNote: `Artifact advanced from revision ${baseRevision} to ${currentRevision}; rebuild this interaction against the current revision.`,
    timestamp: new Date().toISOString(),
  });
  if (!sent) return false;
  if (message) {
    message.status = "interrupted";
    message.returnValues = values;
    message.freeformNote = `Artifact updated to revision ${currentRevision}. Rebuilding the interaction.`;
    renderMessages();
  }
  return true;
}

const elements = {
  status: document.querySelector("#connection-status"),
  modelSelect: document.querySelector("#model-select"),
  pluginSelect: document.querySelector("#plugin-select"),
  approveAll: document.querySelector("#approve-all"),
  newChat: document.querySelector("#new-chat"),
  sessionMenuButton: document.querySelector("#session-menu-button"),
  sidebar: document.querySelector(".sidebar"),
  sessionSearch: document.querySelector("#session-search"),
  sessionSearchClear: document.querySelector("#session-search-clear"),
  sessionSearchCount: document.querySelector("#session-search-count"),
  sessionList: document.querySelector("#session-list"),
  messages: document.querySelector("#messages"),
  skillTraceCount: document.querySelector("#skill-trace-count"),
  skillTraceClear: document.querySelector("#skill-trace-clear"),
  skillTraceList: document.querySelector("#skill-trace-list"),
  composer: document.querySelector("#composer"),
  input: document.querySelector("#message-input"),
  send: document.querySelector("#send-button"),
  attachButton: document.querySelector("#attach-button"),
  fileInput: document.querySelector("#file-input"),
  composerAttachments: document.querySelector("#composer-attachments"),
  modalBackdrop: document.querySelector("#modal-backdrop"),
  modal: document.querySelector("#modal-backdrop .modal"),
  modalTitle: document.querySelector("#modal-title"),
  modalDescription: document.querySelector("#modal-description"),
  modalDetails: document.querySelector("#modal-details"),
  modalApprove: document.querySelector("#modal-approve"),
  modalReject: document.querySelector("#modal-reject"),
  userInputRow: document.querySelector("#user-input-row"),
  userInputAnswer: document.querySelector("#user-input-answer"),
  imagePreview: document.querySelector("#image-preview"),
  imagePreviewContent: document.querySelector("#image-preview-content"),
  imagePreviewClose: document.querySelector("#image-preview-close"),
  toast: document.querySelector("#toast"),
};

let imagePreviewPreviousFocus = null;

function openImagePreview(image) {
  const source = image.currentSrc || image.src;
  if (!source) return;
  imagePreviewPreviousFocus = document.activeElement;
  elements.imagePreviewContent.src = source;
  elements.imagePreviewContent.alt = image.alt || "Previewed image";
  elements.imagePreview.classList.remove("hidden");
  elements.imagePreviewClose.focus();
}

function closeImagePreview() {
  if (elements.imagePreview.classList.contains("hidden")) return;
  elements.imagePreview.classList.add("hidden");
  elements.imagePreviewContent.removeAttribute("src");
  elements.imagePreviewContent.alt = "";
  imagePreviewPreviousFocus?.focus?.();
  imagePreviewPreviousFocus = null;
}

function setStatus(text, kind = "", title = "") {
  elements.status.textContent = text;
  elements.status.className = `status ${kind}`.trim();
  elements.status.title = title;
}

function setConnectedStatus(session) {
  const actualModel = String(session?.actualModel || "").trim();
  if (actualModel) {
    const source = session.actualModelSource ? ` from SDK ${session.actualModelSource}` : " from SDK response metadata";
    setStatus(`Connected · ${actualModel}`, "ready", `Actual response model${source}.`);
    return;
  }
  const selectedModel = session?.selectedModel || session?.model || "auto";
  setStatus(
    "Connected · Awaiting model response",
    "ready",
    `Configured model: ${selectedModel}. The model name appears after the SDK reports the response model.`,
  );
}

function showToast(message) {
  elements.toast.textContent = message;
  elements.toast.classList.remove("hidden");
  window.setTimeout(() => elements.toast.classList.add("hidden"), 6000);
}

function currentSession() {
  return state.sessions.find((session) => session.id === state.currentSessionId) || null;
}

async function renderPrimarySurface() {
  elements.composer.classList.remove("hidden");
  const pluginId = normalizePluginId(elements.pluginSelect?.value || currentSession()?.defaultPluginId || "inflak-main");
  if (pluginId === P10_PLUGIN_ID) elements.composer.classList.add("hidden");
  if (isArtifactCanvasPlugin(pluginId)) {
    elements.messages.classList.add("hidden");
    await openArtifactCanvas({ pluginId, sessionId: state.currentSessionId });
    restoreStoredArtifactCanvasWidget();
  } else {
    closeArtifactCanvas();
    elements.messages.classList.remove("hidden");
  }
}

function restoreStoredArtifactCanvasWidget() {
  const messages = currentSession()?.messages || [];
  const candidates = messages.filter((item) => {
    if (item.role !== "widget" || !item.isStored) return false;
    const widget = item.widget || {};
    const widgetType = widget.semantic_widget_type || widget.widget_type;
    if (widgetType === "svg_revision_comparison") return false;
    return widget.surface === "artifact_canvas_widget"
      || widget.widget_type === "svg_proposal_review"
      || Boolean(widget.artifact_binding || widget.display?.artifact_ref || widget.placement?.mode);
  });
  const message = candidates.findLast((item) => {
    const widget = item.widget || {};
    const widgetType = widget.semantic_widget_type || widget.widget_type;
    return widget.placement?.mode !== "canvas_overlay" || widgetType === "svg_collage_layout_board";
  }) || candidates.at(-1);
  if (!message) return;
  const widgetType = message.widget.semantic_widget_type || message.widget.widget_type;
  const interactiveLayoutHistory = widgetType === "svg_collage_layout_board";
  mountArtifactCanvasWidget(
    message.widget,
    message.widgetId,
    buildHtmlWidgetSrcdoc(message.widget, {
      readOnly: true,
      allowLayoutManipulation: interactiveLayoutHistory,
      interactions: message.interactionHistory || [],
      values: message.returnValues || {},
      controlState: message.controlState || [],
    }),
    message.widget.height,
    {
      historical: true,
      interactiveLayoutHistory,
      layoutValues: message.returnValues || {},
    },
  );
}

function makeSessionTitle(content) {
  const trimmed = content.trim().replace(/\s+/g, " ");
  if (!trimmed) return "New chat";
  return trimmed.length > 34 ? `${trimmed.slice(0, 34)}...` : trimmed;
}

function makeSessionPreview(content) {
  const trimmed = content.trim().replace(/\s+/g, " ");
  return trimmed.length > 160 ? `${trimmed.slice(0, 160)}...` : trimmed;
}

function sessionPluginIcon(pluginId) {
  const normalizedId = normalizePluginId(pluginId || "inflak-main").toLowerCase();
  if (normalizedId === "inflak-main") return "sparkles";
  if (normalizedId.includes("author")) return "blocks";
  if (normalizedId.includes("svg")) return "shapes";
  if (normalizedId.includes("chart") || normalizedId.includes("pn9")) return "chart-bar";
  if (normalizedId.includes("research")) return "search";
  if (normalizedId.includes("paper")) return "book-open";
  if (normalizedId.includes("writing") || normalizedId.includes("story")) return "pen-line";
  if (["image", "sketch", "collage", "cutout"].some((token) => normalizedId.includes(token))) return "image";
  return "plug";
}

function sessionPluginTaskLabel(pluginId, pluginLabel) {
  const normalizedId = normalizePluginId(pluginId || "inflak-main");
  if (SESSION_PLUGIN_TASK_LABELS[normalizedId]) return SESSION_PLUGIN_TASK_LABELS[normalizedId];
  return String(pluginLabel || normalizedId)
    .replace(/^inflak\s+/i, "")
    .replace(/^P\d+\s+/i, "")
    .replace(/\s+(Assistant|Coach)$/i, "")
    .trim() || "Plugin task";
}

function normalizeSessionSearch(value) {
  return String(value || "").normalize("NFKC").toLocaleLowerCase().replace(/\s+/g, " ").trim();
}

function sessionMatchesSearch(session, query) {
  if (!query) return true;
  const pluginId = normalizePluginId(session.defaultPluginId || "inflak-main");
  const plugin = state.plugins.find((item) => item.id === pluginId);
  const haystack = normalizeSessionSearch([
    session.title,
    session.preview,
    session.id,
    pluginId,
    plugin?.label,
    sessionPluginTaskLabel(pluginId, plugin?.label),
  ].filter(Boolean).join(" "));
  return query.split(" ").filter(Boolean).every((term) => haystack.includes(term));
}

function clearSessionSearch({ focus = false, render = true } = {}) {
  state.sessionQuery = "";
  if (elements.sessionSearch) elements.sessionSearch.value = "";
  if (render) renderSessions();
  if (focus) elements.sessionSearch?.focus();
}

function hasSelectedTextWithin(element) {
  const selection = window.getSelection();
  if (!selection || selection.isCollapsed) return false;
  return [selection.anchorNode, selection.focusNode].some((node) => node && element.contains(node));
}

function renderSessions() {
  elements.sessionList.replaceChildren();
  const query = normalizeSessionSearch(state.sessionQuery);
  const matchingSessions = state.sessions.filter((session) => sessionMatchesSearch(session, query));
  const favoriteSessions = matchingSessions.filter((session) => session.favorite);
  const recentSessions = matchingSessions.filter((session) => !session.favorite);
  elements.sessionSearchClear?.classList.toggle("hidden", !query);
  if (elements.sessionSearchCount) {
    elements.sessionSearchCount.textContent = query ? `${matchingSessions.length} / ${state.sessions.length}` : String(state.sessions.length);
  }
  if (query && matchingSessions.length === 0) {
    const empty = document.createElement("div");
    empty.className = "session-search-empty";
    empty.setAttribute("role", "status");
    empty.textContent = "No matching sessions";
    elements.sessionList.append(empty);
  }
  appendSessionGroup("Favorites", favoriteSessions, "folder", { collapsible: true });
  appendSessionGroup("Recent", recentSessions, "history");
  window.lucide?.createIcons();
}

function appendSessionGroup(label, sessions, icon, { collapsible = false } = {}) {
  if (sessions.length === 0) return;
  const collapsed = collapsible && state.favoriteSessionsCollapsed;
  const heading = document.createElement(collapsible ? "button" : "div");
  heading.className = "session-group-heading";
  if (collapsible) {
    heading.type = "button";
    heading.classList.add("collapsible");
    heading.setAttribute("aria-expanded", String(!collapsed));
    heading.title = `${collapsed ? "Expand" : "Collapse"} ${label}`;
    heading.addEventListener("click", () => {
      state.favoriteSessionsCollapsed = !state.favoriteSessionsCollapsed;
      renderSessions();
    });
  }
  const glyph = document.createElement("i");
  glyph.setAttribute("data-lucide", icon);
  glyph.setAttribute("aria-hidden", "true");
  const text = document.createElement("span");
  text.textContent = label;
  const count = document.createElement("span");
  count.className = "session-group-count";
  count.textContent = String(sessions.length);
  heading.append(glyph, text, count);
  if (collapsible) {
    const chevron = document.createElement("i");
    chevron.className = "session-group-chevron";
    chevron.setAttribute("data-lucide", "chevron-down");
    chevron.setAttribute("aria-hidden", "true");
    heading.append(chevron);
  }
  elements.sessionList.append(heading);
  if (collapsed) return;
  for (const session of sessions) appendSessionItem(session);
}

function appendSessionItem(session) {
    const item = document.createElement("div");
    item.className = `session-item ${session.id === state.currentSessionId ? "active" : ""} ${session.favorite ? "favorite" : ""}`;
    const openLink = document.createElement("a");
    openLink.className = "session-item-open";
    openLink.href = `?session=${encodeURIComponent(session.id)}`;
    openLink.draggable = false;
    const title = document.createElement("span");
    title.className = "session-item-title";
    title.textContent = session.title;
    openLink.append(title);

    const pluginRow = document.createElement("span");
    pluginRow.className = "session-item-plugin-row";
    const pluginId = normalizePluginId(session.defaultPluginId || "inflak-main");
    const plugin = state.plugins.find((item) => item.id === pluginId);
    const pluginIcon = document.createElement("span");
    pluginIcon.className = "session-item-plugin-icon";
    pluginIcon.title = `${plugin?.label || pluginId} plugin`;
    pluginIcon.setAttribute("aria-label", pluginIcon.title);
    const glyph = document.createElement("i");
    glyph.setAttribute("data-lucide", sessionPluginIcon(pluginId));
    glyph.setAttribute("aria-hidden", "true");
    pluginIcon.append(glyph);
    const pluginTask = document.createElement("span");
    pluginTask.className = "session-item-plugin-task";
    pluginTask.textContent = sessionPluginTaskLabel(pluginId, plugin?.label);
    pluginRow.append(pluginIcon, pluginTask);
    const backendId = document.createElement("span");
    backendId.className = "session-item-backend-id";
    const backendIdValue = document.createElement("code");
    backendIdValue.textContent = session.id;
    backendId.append(backendIdValue);
    openLink.append(pluginRow, backendId);
    openLink.addEventListener("click", (event) => {
      event.preventDefault();
      if (event.detail > 0 && hasSelectedTextWithin(openLink)) return;
      switchSession(session.id);
    });
    const favoriteButton = document.createElement("button");
    favoriteButton.type = "button";
    favoriteButton.className = "session-item-favorite";
    favoriteButton.title = session.favorite ? "Remove from favorites" : "Add to favorites";
    favoriteButton.setAttribute("aria-label", `${favoriteButton.title}: ${session.title}`);
    favoriteButton.setAttribute("aria-pressed", String(Boolean(session.favorite)));
    const favoriteIcon = document.createElement("i");
    favoriteIcon.setAttribute("data-lucide", "star");
    favoriteIcon.setAttribute("aria-hidden", "true");
    favoriteButton.append(favoriteIcon);
    favoriteButton.addEventListener("click", () => toggleSessionFavorite(session));
    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.className = "session-item-delete";
    deleteButton.title = "Delete session";
    deleteButton.setAttribute("aria-label", `Delete session: ${session.title}`);
    const deleteIcon = document.createElement("i");
    deleteIcon.setAttribute("data-lucide", "trash-2");
    deleteIcon.setAttribute("aria-hidden", "true");
    deleteButton.append(deleteIcon);
    deleteButton.addEventListener("click", () => openDeleteSessionModal(session));
    item.append(openLink, favoriteButton, deleteButton);
    elements.sessionList.append(item);
}

async function toggleSessionFavorite(session) {
  const nextFavorite = !session.favorite;
  session.favorite = nextFavorite;
  renderSessions();
  try {
    const response = await fetch(`/api/sessions/${encodeURIComponent(session.id)}/favorite`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ favorite: nextFavorite }),
    });
    if (!response.ok) throw new Error(await response.text());
  } catch (error) {
    session.favorite = !nextFavorite;
    renderSessions();
    showToast(`Failed to update favorite: ${error.message}`);
  }
}

function renderMessages() {
  const session = currentSession();
  elements.messages.replaceChildren();
  if (!session || session.messages.length === 0) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.innerHTML = '<div class="empty-state-kicker">InFlak Plugin Studio</div><h1>Collaborate with InFlak</h1><p>Interactive plugins for human-AI collaboration.</p>';
    elements.messages.append(empty);
    return;
  }

  for (const message of session.messages) {
    elements.messages.append(createMessageNode(message));
  }
  scrollToBottomAfterLayout();
}

function skillTraceKey(item) {
  return item.toolCallId || item.recordId;
}

function handleSkillEvent(event) {
  const session = currentSession();
  if (!session) return;
  if (!Array.isArray(session.debugEvents)) session.debugEvents = [];

  const recordId = event.toolCallId || event.recordId || crypto.randomUUID();
  const next = normalizeSkillEvent(event, recordId);
  const existingIndex = session.debugEvents.findIndex((item) => skillTraceKey(item) === skillTraceKey(next));
  if (existingIndex >= 0) {
    const existing = session.debugEvents[existingIndex];
    session.debugEvents[existingIndex] = {
      ...existing,
      ...next,
      preview: Object.keys(next.preview || {}).length > 0 ? next.preview : existing.preview,
      firstTimestamp: existing.firstTimestamp || existing.timestamp,
    };
  } else {
    session.debugEvents.push(next);
  }

  if (session.debugEvents.length > MAX_SKILL_TRACE_ITEMS) {
    session.debugEvents.splice(0, session.debugEvents.length - MAX_SKILL_TRACE_ITEMS);
  }
  renderSkillTrace();
}

function normalizeSkillEvent(event, recordId) {
  const displayName = event.displayName || event.name || event.toolName || "Unknown call";
  return {
    recordId,
    toolCallId: event.toolCallId || "",
    category: event.category || "tool",
    name: event.name || displayName,
    displayName,
    layer: event.layer || "",
    status: event.status || "event",
    eventType: event.eventType || "",
    turnId: event.turnId || "",
    timestamp: event.timestamp || new Date().toISOString(),
    durationMs: Number.isFinite(Number(event.durationMs)) ? Number(event.durationMs) : null,
    success: event.success,
    error: event.error || "",
    toolName: event.toolName || "",
    pluginName: event.pluginName || "",
    preview: event.preview && typeof event.preview === "object" ? event.preview : {},
  };
}

function renderSkillTrace() {
  if (!elements.skillTraceList) return;
  const session = currentSession();
  const events = session?.debugEvents || [];
  if (elements.skillTraceCount) elements.skillTraceCount.textContent = String(events.length);
  elements.skillTraceList.replaceChildren();

  if (!session) {
    elements.skillTraceList.append(createSkillTraceEmpty("No active session."));
    return;
  }
  if (events.length === 0) {
    elements.skillTraceList.append(createSkillTraceEmpty("No skill calls yet."));
    return;
  }

  for (const item of events.slice(-50)) {
    elements.skillTraceList.append(createSkillTraceNode(item));
  }
  elements.skillTraceList.scrollTop = elements.skillTraceList.scrollHeight;
}

function createSkillTraceEmpty(text) {
  const empty = document.createElement("div");
  empty.className = "skill-trace-empty";
  empty.textContent = text;
  return empty;
}

function createSkillTraceNode(item) {
  const wrapper = document.createElement("article");
  const waitingForInput = isWaitingForInteractiveReturn(item);
  const interactionEnded = isEndedInteractiveReturn(item);
  wrapper.className = `skill-trace-item ${waitingForInput ? "waiting" : (interactionEnded ? "expired" : (item.status || "event"))}`;

  const header = document.createElement("div");
  header.className = "skill-trace-item-header";

  const status = document.createElement("span");
  status.className = "skill-trace-status";
  status.textContent = waitingForInput ? "Waiting for input" : (interactionEnded ? "Interaction ended" : skillStatusText(item.status));

  const title = document.createElement("div");
  title.className = "skill-trace-title";
  title.textContent = item.displayName || item.name;

  header.append(status, title);

  const meta = document.createElement("div");
  meta.className = "skill-trace-meta";
  meta.textContent = skillTraceMeta(item);

  wrapper.append(header, meta);

  const preview = formatSkillPreview(item.preview);
  if (preview) {
    const previewNode = document.createElement("div");
    previewNode.className = "skill-trace-preview";
    previewNode.textContent = preview;
    wrapper.append(previewNode);
  }

  if (item.error) {
    const error = document.createElement("div");
    error.className = "skill-trace-error";
    error.textContent = String(item.error);
    wrapper.append(error);
  }

  return wrapper;
}

function skillStatusText(status) {
  const labels = {
    started: "Running",
    completed: "Done",
    failed: "Failed",
    interrupted: "Interrupted",
  };
  return labels[status] || status || "Event";
}

function skillTraceMeta(item) {
  const parts = [];
  if (item.layer) parts.push(item.layer);
  parts.push(item.category === "skill" ? "skill" : item.toolName || "tool");
  if (item.pluginName) parts.push(item.pluginName);
  if (item.turnId !== "") parts.push(`turn ${item.turnId}`);
  if (item.durationMs !== null && item.durationMs !== undefined) {
    parts.push(formatDuration(item.durationMs));
  } else if (isWaitingForInteractiveReturn(item)) {
    const widget = currentSession()?.messages.find((message) => message.role === "widget" && message.status === "pending" && !message.isStored)?.widget || {};
    const widgetType = widget.semantic_widget_type || widget.widget_type;
    parts.push(widgetType === "svg_proposal_review"
      ? "review the SVG revision on the Artifact Canvas"
      : widget.surface === "artifact_canvas_widget"
        ? "continue in the widget on the Artifact Canvas"
        : "continue in the open widget");
  } else if (isEndedInteractiveReturn(item)) {
    parts.push("resend the request to open a new widget");
  } else if (item.status === "started") {
    parts.push("running");
  }
  return parts.filter(Boolean).join(" · ");
}

function isWaitingForInteractiveReturn(item) {
  return isInteractiveRendererStart(item) && currentSession()?.messages.some((message) => message.role === "widget" && message.status === "pending" && !message.isStored);
}

function isEndedInteractiveReturn(item) {
  return isInteractiveRendererStart(item) && !isWaitingForInteractiveReturn(item);
}

function isInteractiveRendererStart(item) {
  return item?.status === "started" && ["render_html_widget", "render_interactive_widget", "render_canvas_workspace"].includes(item.toolName);
}

function formatDuration(durationMs) {
  if (durationMs < 1000) return `${Math.round(durationMs)} ms`;
  return `${(durationMs / 1000).toFixed(1)} s`;
}

function formatSkillPreview(preview) {
  if (!preview || typeof preview !== "object") return "";
  return Object.entries(preview)
    .filter(([, value]) => value !== null && value !== undefined && value !== "")
    .map(([key, value]) => `${formatPreviewKey(key)}: ${formatPreviewValue(value)}`)
    .join(" · ");
}

function formatPreviewKey(key) {
  return key.replace(/_/g, " ");
}

function formatPreviewValue(value) {
  if (Array.isArray(value)) return value.join(", ");
  if (value && typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function clearSkillTrace() {
  const session = currentSession();
  if (!session) return;
  session.debugEvents = [];
  renderSkillTrace();
}

const RENDERER_TOOL_NAMES = new Set(["render_html_widget", "render_interactive_widget"]);

function inferIaiLayer(skillName) {
  if (!skillName) return "";
  const match = String(skillName).match(/^(?:iai-)?(l[1-4])-.+$/);
  return match ? match[1].toUpperCase() : "";
}

function rendererToolDisplayName(toolName) {
  if (toolName === "render_html_widget") return "HTML widget renderer";
  if (toolName === "render_interactive_widget") return "Schema widget renderer";
  return String(toolName || "").replace(/_/g, " ");
}

function compactToolPreview(toolName, args) {
  if (!RENDERER_TOOL_NAMES.has(toolName) || !args || typeof args !== "object") return {};
  const preview = {};
  for (const key of ["widget_id", "widget_type", "planner_id", "interaction_goal", "title", "height"]) {
    const value = args[key];
    if (value !== null && value !== undefined && value !== "") preview[key] = value;
  }
  if (args.display && typeof args.display === "object" && !preview.title && args.display.title) {
    preview.title = args.display.title;
  }
  if (Array.isArray(args.controls)) preview.control_count = args.controls.length;
  if (args.expected_return && typeof args.expected_return === "object") {
    preview.expected_return_keys = Object.keys(args.expected_return).slice(0, 8);
  }
  return preview;
}

// Rebuild a single skill-trace event from a stored `tool_event` message.
// Mirrors the backend `_build_skill_event` so a reloaded session shows the
// same trace the live socket produced. `activeCalls` carries start-event
// context (name, layer, preview, start time) forward to its complete event.
function buildStoredSkillEvent(kind, data, message, activeCalls) {
  const callId = data.tool_call_id || data.toolCallId;
  const callKey = callId ? String(callId) : "";
  const activeCall = callKey ? activeCalls.get(callKey) : null;
  const args = data.arguments && typeof data.arguments === "object" ? data.arguments : {};
  let toolName = data.tool_name || data.toolName || "";

  const telemetry = data.tool_telemetry && typeof data.tool_telemetry === "object" ? data.tool_telemetry : {};
  const restricted = telemetry.restrictedProperties && typeof telemetry.restrictedProperties === "object"
    ? telemetry.restrictedProperties
    : {};
  let skillName = typeof args.skill === "string" ? args.skill : null;
  skillName = skillName || restricted.skillName || null;
  let pluginName = restricted.pluginName || "";

  let category = "";
  let name = "";
  let displayName = "";
  let layer = "";
  let preview = {};

  if (skillName || toolName === "skill") {
    category = "skill";
    name = skillName || (activeCall ? activeCall.name : "skill");
    displayName = name;
    layer = inferIaiLayer(name);
    toolName = "skill";
  } else if (RENDERER_TOOL_NAMES.has(toolName)) {
    category = "tool";
    name = toolName;
    displayName = rendererToolDisplayName(toolName);
    layer = "L4";
    preview = compactToolPreview(toolName, args);
  } else if (toolName) {
    // Any other tool call (generate_image, edit_image, ...) still belongs in
    // the Skill Trace, not the chat transcript.
    category = "tool";
    name = toolName;
    displayName = String(toolName).replace(/_/g, " ");
  }

  if (activeCall) {
    category = category || activeCall.category;
    name = name || activeCall.name;
    displayName = displayName || activeCall.displayName;
    layer = layer || activeCall.layer;
    toolName = toolName || activeCall.toolName;
    pluginName = pluginName || activeCall.pluginName;
    preview = Object.keys(preview).length > 0 ? preview : (activeCall.preview || {});
  }

  if (!category || !name) return null;

  let status;
  if (kind === "tool.execution_start") {
    status = "started";
  } else if (kind === "tool.execution_complete") {
    status = data.success === false ? "failed" : "completed";
  } else {
    status = kind.split(".").pop();
  }

  let durationMs = null;
  if (kind === "tool.execution_start" && callKey) {
    activeCalls.set(callKey, {
      category,
      name,
      displayName,
      layer,
      toolName,
      pluginName,
      preview,
      startedAt: message.createdAt || "",
    });
  } else if (kind === "tool.execution_complete") {
    const startedAt = activeCall?.startedAt;
    if (startedAt && message.createdAt) {
      const delta = new Date(message.createdAt).getTime() - new Date(startedAt).getTime();
      if (Number.isFinite(delta) && delta >= 0) durationMs = delta;
    }
    if (callKey) activeCalls.delete(callKey);
  }

  const error = data.error;
  return {
    eventType: kind,
    recordId: callKey || message.id || crypto.randomUUID(),
    toolCallId: callKey || "",
    category,
    name,
    displayName: displayName || name,
    layer,
    status,
    timestamp: message.createdAt || new Date().toISOString(),
    turnId: data.turn_id || data.turnId || "",
    durationMs,
    success: data.success,
    error: error ? (typeof error === "object" ? JSON.stringify(error) : String(error)) : "",
    toolName,
    pluginName,
    preview,
  };
}

// Convert all stored `tool_event` messages into a de-duplicated skill-trace
// list (start + complete merged per tool_call_id), matching the live view.
function buildStoredSkillTrace(storedMessages) {
  const events = [];
  const indexByKey = new Map();
  const activeCalls = new Map();

  for (const message of storedMessages) {
    if (message.role !== "tool_event") continue;
    const kind = message.metadata?.eventType || "";
    if (!kind.startsWith("tool.")) continue;
    const data = message.metadata?.event?.data;
    if (!data || typeof data !== "object") continue;

    const built = buildStoredSkillEvent(kind, data, message, activeCalls);
    if (!built) continue;

    const normalized = normalizeSkillEvent(built, built.recordId);
    const key = normalized.toolCallId || normalized.recordId;
    if (indexByKey.has(key)) {
      const idx = indexByKey.get(key);
      const existing = events[idx];
      events[idx] = {
        ...existing,
        ...normalized,
        preview: Object.keys(normalized.preview || {}).length > 0 ? normalized.preview : existing.preview,
        firstTimestamp: existing.firstTimestamp || existing.timestamp,
      };
    } else {
      indexByKey.set(key, events.length);
      events.push({ ...normalized, firstTimestamp: normalized.timestamp });
    }
  }

  if (events.length > MAX_SKILL_TRACE_ITEMS) {
    events.splice(0, events.length - MAX_SKILL_TRACE_ITEMS);
  }
  for (const event of events) {
    if (event.status === "started") event.status = "interrupted";
  }
  return events;
}

function createMessageNode(message) {
  const wrapper = document.createElement("article");
  const roleClass = message.role === "user" ? "user" : "assistant";
  wrapper.className = `message ${roleClass}`;
  wrapper.dataset.messageId = message.id;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  if (message.role === "user") {
    avatar.textContent = "You";
  } else {
    avatar.textContent = "IF";
    avatar.setAttribute("aria-label", "InFlak");
    avatar.title = "InFlak";
  }

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  if (message.report && (message.role !== "widget" || message.status !== "pending")) {
    bubble.classList.add("report-bubble");
    bubble.append(renderReport(message.report));
  } else if (message.role === "widget") {
    bubble.classList.add("widget-bubble");
    renderInlineWidget(bubble, message);
  } else if (message.role === "user_input") {
    bubble.classList.add("widget-bubble");
    renderInlineUserInput(bubble, message);
  } else {
    bubble.textContent = message.content;
  }
  if (message.reportError) {
    const error = document.createElement("p");
    error.className = "report-error";
    error.textContent = message.reportError;
    bubble.append(error);
  }

  if (Array.isArray(message.attachments) && message.attachments.length > 0) {
    if (message.attachments.some((att) => att.mime === "text/html" || /\.html?$/i.test(att.name || ""))) {
      bubble.classList.add("html-attachment-bubble");
    }
    bubble.append(renderAttachmentList(message.attachments, message.role));
  }

  wrapper.append(avatar, bubble);
  return wrapper;
}

function renderReport(report) {
  const container = document.createElement("section");
  container.className = "analysis-report";
  const title = document.createElement("h2");
  title.textContent = report.title;
  const actions = document.createElement("div");
  actions.className = "report-actions";
  const url = `/api/sessions/${encodeURIComponent(currentSession().id)}/uploads/${encodeURIComponent(report.fileId)}`;
  for (const [label, iconName, download] of [["Open report", "external-link", false], ["Download HTML", "download", true]]) {
    const link = document.createElement("a");
    link.href = download ? url : `${url}/preview`;
    link.title = label;
    const icon = document.createElement("i");
    icon.setAttribute("data-lucide", iconName);
    icon.setAttribute("aria-hidden", "true");
    link.append(icon, document.createTextNode(label));
    if (download) link.download = report.name;
    else { link.target = "_blank"; link.rel = "noopener noreferrer"; }
    actions.append(link);
  }
  const frame = document.createElement("iframe");
  frame.className = "report-preview";
  frame.title = report.title;
  frame.setAttribute("sandbox", "");
  frame.setAttribute("referrerpolicy", "no-referrer");
  const loading = document.createElement("p");
  loading.className = "report-loading";
  loading.setAttribute("role", "status");
  loading.textContent = "Loading report...";
  fetch(`${url}/preview`).then(async (response) => {
    if (!response.ok) throw new Error(`Report preview unavailable (${response.status})`);
    frame.srcdoc = await response.text();
    loading.remove();
  }).catch((error) => {
    loading.className = "report-error";
    loading.textContent = error.message;
    frame.remove();
  });
  container.append(loading);
  container.append(title, actions, frame);
  return container;
}

function renderAttachmentList(attachments, role) {
  const list = document.createElement("div");
  list.className = "message-attachments";
  for (const att of attachments) {
    const sid = currentSession()?.id;
    const url = att.fileId && sid ? `/api/sessions/${encodeURIComponent(sid)}/uploads/${att.fileId}` : null;
    if (url && String(att.mime || "").startsWith("image/")) {
      const img = document.createElement("img");
      img.className = "message-attachment-thumb";
      img.src = url;
      img.alt = att.name || "image";
      list.append(img);
    } else if (url && (att.mime === "text/html" || /\.html?$/i.test(att.name || ""))) {
      const preview = document.createElement("details");
      preview.className = "message-html-preview";

      const summary = document.createElement("summary");
      const icon = document.createElement("i");
      icon.setAttribute("data-lucide", "file-code-2");
      icon.setAttribute("aria-hidden", "true");
      const name = document.createElement("span");
      name.textContent = att.name || "HTML file";
      summary.append(icon, name);

      const frame = document.createElement("iframe");
      frame.className = "message-html-preview-frame";
      frame.title = `${att.name || "HTML file"} preview`;
      frame.setAttribute("sandbox", "");
      frame.setAttribute("referrerpolicy", "no-referrer");
      frame.dataset.src = `${url}/preview`;
      preview.addEventListener("toggle", () => {
        if (preview.open && !frame.src) frame.src = frame.dataset.src;
      });
      preview.append(summary, frame);
      list.append(preview);
    } else {
      const chip = document.createElement("span");
      chip.className = "message-attachment-chip";
      chip.textContent = att.name || "file";
      list.append(chip);
    }
  }
  return list;
}

function appendMessage(role, content = "", attachments = []) {
  const session = currentSession();
  if (!session) return null;
  const message = {
    id: crypto.randomUUID(),
    role,
    content,
    attachments: attachments || [],
    createdAt: Date.now(),
  };
  session.messages.push(message);
  renderMessages();
  return message;
}

function updateMessage(messageId, content) {
  const session = currentSession();
  if (!session) return;
  const message = session.messages.find((item) => item.id === messageId);
  if (!message) return;
  message.content = content;

  const node = elements.messages.querySelector(`[data-message-id="${messageId}"] .bubble`);
  if (node) {
    node.textContent = content;
  }
  scrollToBottom();
}

function appendToAssistant(content) {
  if (!state.pendingAssistantId) {
    const message = appendMessage("assistant", "");
    state.pendingAssistantId = message?.id || null;
  }
  if (!state.pendingAssistantId) return;
  const session = currentSession();
  const message = session.messages.find((item) => item.id === state.pendingAssistantId);
  message.streamContent = `${message.streamContent ?? message.content}${content}`;
  const visibleContent = session.defaultPluginId === "inflak-pN9-artifact-to-structured-instruction"
    ? message.streamContent.split("```inflak-report", 1)[0]
    : message.streamContent;
  updateMessage(state.pendingAssistantId, visibleContent);
}

function scrollToBottom() {
  elements.messages.scrollTop = elements.messages.scrollHeight;
}

function scrollToBottomAfterLayout() {
  scrollToBottom();
  window.requestAnimationFrame(scrollToBottom);
}

async function loadModels() {
  try {
    const response = await fetch("/api/models");
    if (!response.ok) throw new Error(await response.text());
    const data = await response.json();
    state.models = data.models || [];
    elements.modelSelect.replaceChildren();
    for (const model of state.models) {
      const option = document.createElement("option");
      option.value = model.id;
      const base = model.name ? `${model.name} (${model.id})` : model.id;
      option.textContent = model.capabilities?.supports?.vision === true ? `${base} · vision` : base;
      elements.modelSelect.append(option);
    }
    if ([...elements.modelSelect.options].some((option) => option.value === DEFAULT_MODEL)) {
      elements.modelSelect.value = DEFAULT_MODEL;
    } else if ([...elements.modelSelect.options].some((option) => option.value === "auto")) {
      elements.modelSelect.value = "auto";
    }
  } catch (error) {
    showToast(`Failed to load models: ${error.message}`);
  }
}

async function loadPlugins() {
  try {
    const response = await fetch("/api/inflak/plugins");
    if (!response.ok) throw new Error(await response.text());
    const data = await response.json();
    state.plugins = data.plugins || [];
    if (!elements.pluginSelect) return;
    const priorSelection = elements.pluginSelect.value;
    elements.pluginSelect.replaceChildren();
    for (const plugin of state.plugins) {
      const option = document.createElement("option");
      option.value = plugin.id;
      option.textContent = plugin.status === "ready" ? plugin.label : `${plugin.label} · planned`;
      option.disabled = plugin.status !== "ready";
      elements.pluginSelect.append(option);
    }
    elements.pluginSelect.value = [...elements.pluginSelect.options].some((option) => option.value === priorSelection)
      ? priorSelection
      : data.defaultPluginId || "inflak-main";
  } catch (error) {
    showToast(`Failed to load plugins: ${error.message}`);
  }
}

async function loadStoredSessions() {
  try {
    const response = await fetch("/api/sessions");
    if (!response.ok) throw new Error(await response.text());
    const data = await response.json();
    state.sessions = (data.sessions || []).map((session) => ({
      id: session.sessionId,
      title: session.title || "New chat",
      model: session.model,
      actualModel: null,
      actualModelSource: null,
      defaultPluginId: normalizePluginId(session.defaultPluginId || "inflak-main"),
      favorite: Boolean(session.favorite),
      messages: [],
      createdAt: session.createdAt,
      updatedAt: session.updatedAt,
      messageCount: session.messageCount || 0,
      preview: session.preview || "",
      debugEvents: [],
      isLive: false,
      isLoaded: false,
    }));
    renderSessions();
  } catch (error) {
    showToast(`Failed to load stored sessions: ${error.message}`);
  }
}

async function openRequestedSession() {
  const sessionId = new URLSearchParams(window.location.search).get("session");
  if (!sessionId) return false;
  let session = state.sessions.find((item) => item.id === sessionId);
  if (!session) {
    const response = await fetch(`/api/sessions/${encodeURIComponent(sessionId)}`);
    if (!response.ok) throw new Error(await response.text());
    const record = await response.json();
    session = {
      id: record.sessionId,
      title: record.title || "Scenario test",
      model: record.model,
      actualModel: null,
      actualModelSource: null,
      defaultPluginId: normalizePluginId(record.defaultPluginId || "inflak-main"),
      favorite: Boolean(record.favorite),
      messages: [],
      createdAt: record.createdAt,
      updatedAt: record.updatedAt,
      messageCount: (record.messages || []).length,
      preview: "Interactive plugin scenario",
      debugEvents: [],
      isLive: false,
      isLoaded: false,
    };
    state.sessions.unshift(session);
  }
  state.currentSessionId = session.id;
  await loadStoredMessages(session);
  if (elements.pluginSelect && session.defaultPluginId) {
    elements.pluginSelect.value = session.defaultPluginId;
  }
  await resumeSession(session);
  renderSessions();
  renderMessages();
  renderSkillTrace();
  await renderPrimarySurface();
  window.history.replaceState({}, "", window.location.pathname);
  return true;
}

async function loadStoredMessages(session) {
  if (session.isLoaded) return;
  const response = await fetch(`/api/sessions/${encodeURIComponent(session.id)}/messages`);
  if (!response.ok) throw new Error(await response.text());
  const data = await response.json();
  const storedMessages = data.messages || [];
  session.messages = buildStoredMessages(storedMessages);
  session.debugEvents = buildStoredSkillTrace(storedMessages);
  session.isLoaded = true;
}

function buildStoredMessages(storedMessages) {
  const messages = [];
  const widgetsById = new Map();
  const userInputsById = new Map();
  for (const message of storedMessages) {
    // Stored user turns remain server-side for SDK context restoration. Only
    // messages sent in the current browser lifetime should appear as "You".
    if (message.role === "user") continue;

    // Tool/skill activity (tool_event) and tool-permission prompts
    // (permission_request/response) live in the right-hand Skill Trace, not
    // the chat transcript. The chat only shows user turns, agent output,
    // widgets, and inline questions/answers.
    if (![
      "assistant",
      "error",
      "widget_request",
      "widget_interaction",
      "widget_return",
      "user_input_request",
      "user_input_response",
    ].includes(message.role)) {
      continue;
    }

    if (message.role === "widget_request") {
      const widgetMessage = storedWidgetMessage(message);
      widgetMessage.report = message.metadata?.report;
      widgetMessage.reportError = message.metadata?.reportError;
      messages.push(widgetMessage);
      widgetsById.set(widgetMessage.widgetId, widgetMessage);
      continue;
    }

    if (message.role === "widget_return") {
      const result = message.metadata?.result || {};
      const widgetId = String(message.metadata?.widgetId || result.widget_id || "");
      const widgetMessage = widgetsById.get(widgetId);
      if (widgetMessage) {
        applyWidgetResult(widgetMessage, result, message.createdAt);
        continue;
      }
    }

    if (message.role === "widget_interaction") {
      const widgetId = String(message.metadata?.widgetId || "");
      const widgetMessage = widgetsById.get(widgetId);
      if (widgetMessage) {
        widgetMessage.interactionHistory.push({
          sequence: message.metadata?.sequence,
          timestamp: message.createdAt,
          ...(message.metadata?.interaction || {}),
        });
        continue;
      }
    }

    if (message.role === "user_input_request") {
      const requestId = String(message.metadata?.requestId || message.id);
      const inputMessage = {
        id: message.id,
        role: "user_input",
        label: "Ask",
        content: message.content,
        question: message.content,
        choices: message.metadata?.choices || [],
        requestId,
        status: "interrupted",
        answer: "",
        createdAt: message.createdAt,
        isStored: true,
      };
      messages.push(inputMessage);
      userInputsById.set(requestId, inputMessage);
      continue;
    }

    if (message.role === "user_input_response") {
      const requestId = String(message.metadata?.requestId || "");
      const inputMessage = userInputsById.get(requestId);
      if (inputMessage) {
        inputMessage.status = message.content ? "submitted" : "cancelled";
        inputMessage.answer = message.content || "";
        continue;
      }
    }

    messages.push({
      id: message.id,
      role: message.role === "user" ? "user" : "assistant",
      label: labelForStoredRole(message.role),
      content: formatStoredMessage(message),
      attachments: message.metadata?.attachments || [],
      report: message.metadata?.report,
      reportError: message.metadata?.reportError,
      createdAt: message.createdAt,
      metadata: message.metadata || {},
    });
  }

  for (const message of messages) {
    if (message.role === "widget" && message.status === "pending") {
      message.status = "expired";
      message.freeformNote = "This stored widget is no longer active.";
    }
  }
  return messages;
}

function storedWidgetMessage(message) {
  const widget = message.metadata?.widget || {};
  const display = widget.display || {};
  const widgetId = String(message.metadata?.widgetId || widget.widget_id || message.id);
  return {
    id: message.id,
    role: "widget",
    label: "UI",
    content: display.title || widget.title || widget.interaction_goal || message.content || "Interactive widget",
    createdAt: message.createdAt,
    metadata: message.metadata || {},
    widget,
    widgetId,
    status: "pending",
    interactionHistory: [],
    isStored: true,
  };
}

function applyWidgetResult(widgetMessage, result, createdAt) {
  const action = result.action || "accept";
  widgetMessage.status = action === "interrupted" ? "interrupted" : action === "dismiss" ? "dismissed" : "submitted";
  widgetMessage.returnAction = action;
  widgetMessage.returnValues = result.values || {};
  widgetMessage.controlState = result.control_state || [];
  widgetMessage.freeformNote = result.freeform_note || "";
  widgetMessage.returnedAt = result.timestamp || createdAt;
}

function labelForStoredRole(role) {
  const labels = {
    assistant: "AI",
    error: "ERR",
    widget_request: "UI",
    widget_return: "You",
    user_input_request: "AI",
    user_input_response: "You",
    permission_request: "Perm",
    permission_response: "Perm",
    tool_event: "Tool",
  };
  return labels[role] || "AI";
}

function formatStoredMessage(message) {
  if (message.role === "error") return `Error: ${message.content}`;
  if (message.role === "widget_request") {
    const widget = message.metadata?.widget || {};
    return `Widget requested: ${message.content}\n${JSON.stringify(widget, null, 2)}`;
  }
  if (message.role === "widget_return") {
    const result = message.metadata?.result || {};
    return `Widget returned: ${message.content}\n${JSON.stringify(result, null, 2)}`;
  }
  if (message.role === "user_input_request") return `Question: ${message.content}`;
  if (message.role === "user_input_response") return `Answer: ${message.content}`;
  if (message.role === "permission_request") return `${message.content}\n${JSON.stringify(message.metadata?.request || {}, null, 2)}`;
  if (message.role === "permission_response") return message.content;
  if (message.role === "tool_event") return message.content;
  return message.content;
}

async function createSession() {
  closeSocket();
  setStatus("Creating session", "");
  const response = await fetch("/api/sessions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: elements.modelSelect.value || DEFAULT_MODEL,
      approve_all: elements.approveAll.checked !== false,
      default_plugin_id: elements.pluginSelect?.value || "inflak-main",
    }),
  });
  if (!response.ok) throw new Error(await response.text());
  const data = await response.json();
  const session = {
    id: data.sessionId,
    title: "New chat",
    preview: "",
    model: data.model,
    actualModel: data.actualModel || null,
    actualModelSource: null,
    defaultPluginId: data.defaultPluginId || elements.pluginSelect?.value || "inflak-main",
    messages: [],
    debugEvents: [],
    createdAt: Date.now(),
    isLive: true,
    isLoaded: true,
  };
  state.sessions.unshift(session);
  clearSessionSearch({ render: false });
  state.currentSessionId = session.id;
  state.liveSessionId = session.id;
  await connectSocket(session.id);
  renderSessions();
  renderMessages();
  renderSkillTrace();
  renderPrimarySurface();
  return session;
}

async function resumeSession(session) {
  if (session.isLive) return session;
  setStatus("Resuming stored session", "");
  const response = await fetch(`/api/sessions/${encodeURIComponent(session.id)}/resume`, {
    method: "POST",
  });
  if (!response.ok) throw new Error(await response.text());
  const data = await response.json();
  session.isLive = true;
  session.model = data.model || session.model;
  session.actualModel = data.actualModel || null;
  session.actualModelSource = null;
  state.liveSessionId = session.id;
  await connectSocket(session.id);
  setConnectedStatus(session);
  return session;
}

async function recoverInterruptedWidget(session) {
  const hasInterruptedWidget = session.messages.some((message) =>
    message.role === "widget" && message.status === "expired" && message.isStored);
  if (!hasInterruptedWidget) return false;
  setStatus("Recovering interrupted interaction", "");
  const response = await fetch(`/api/sessions/${encodeURIComponent(session.id)}/recover-interrupted-widget`, {
    method: "POST",
  });
  if (!response.ok) throw new Error(await response.text());
  const result = await response.json();
  if (!result.recovered) return false;
  session.isLoaded = false;
  await loadStoredMessages(session);
  return true;
}

function connectSocket(sessionId) {
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  const socket = new WebSocket(`${protocol}://${window.location.host}/ws/${sessionId}`);
  state.socket = socket;

  socket.addEventListener("close", () => {
    if (state.socket !== socket || state.currentSessionId !== sessionId) return;
    state.socket = null;
    setStatus("Disconnected", "error");
    expirePendingWidgets();
  });
  socket.addEventListener("error", () => {
    if (state.socket === socket && state.currentSessionId === sessionId) setStatus("Connection error", "error");
  });
  socket.addEventListener("message", (event) => {
    if (state.socket !== socket || state.currentSessionId !== sessionId) return;
    handleServerEvent(JSON.parse(event.data));
  });

  return new Promise((resolve, reject) => {
    socket.addEventListener("open", () => {
      if (state.socket !== socket || state.currentSessionId !== sessionId) return;
      setConnectedStatus(currentSession());
      resolve(socket);
    }, { once: true });
    socket.addEventListener("error", () => reject(new Error("WebSocket connection failed")), { once: true });
  });
}

function closeSocket() {
  if (state.socket) {
    state.socket.close();
    state.socket = null;
  }
}

async function deleteStoredSession(sessionId) {
  const session = state.sessions.find((item) => item.id === sessionId);
  if (!session) {
    closeModal();
    return;
  }
  elements.modalApprove.disabled = true;
  try {
    const response = await fetch(`/api/sessions/${encodeURIComponent(sessionId)}`, { method: "DELETE" });
    if (!response.ok) throw new Error(await response.text());

    const deletingCurrentSession = state.currentSessionId === sessionId;
    if (deletingCurrentSession) {
      closeSocket();
      state.currentSessionId = null;
      state.liveSessionId = null;
      state.isBusy = false;
      state.pendingAssistantId = null;
      state.attachments = [];
      state.canvasPendingArtifacts = [];
      closeArtifactCanvas();
      elements.messages.classList.remove("hidden");
      elements.composer.classList.remove("hidden");
      renderComposerAttachments();
      updateComposerState();
      setStatus("Ready", "ready");
    }
    state.sessions = state.sessions.filter((item) => item.id !== sessionId);
    renderSessions();
    if (deletingCurrentSession) {
      renderMessages();
      renderSkillTrace();
    }
    closeModal();
    showToast("Session deleted");
  } catch (error) {
    elements.modalApprove.disabled = false;
    showToast(`Failed to delete session: ${error.message}`);
  }
}

async function switchSession(sessionId) {
  if (sessionId === state.currentSessionId) return;
  state.currentSessionId = sessionId;
  const session = currentSession();
  closeSocket();
  if (session?.isLive) {
    await connectSocket(session.id);
    setConnectedStatus(session);
    elements.input.disabled = state.isBusy;
    elements.send.disabled = state.isBusy;
  } else if (session) {
    try {
      await loadStoredMessages(session);
      const hasInterruptedWidget = session.messages.some((message) => message.role === "widget" && message.status === "expired" && message.isStored);
      if (elements.pluginSelect && session.defaultPluginId) elements.pluginSelect.value = normalizePluginId(session.defaultPluginId);
      await renderPrimarySurface();
      if (hasInterruptedWidget) await recoverInterruptedWidget(session);
      if (hasInterruptedWidget) await resumeSession(session);
      else setStatus("Stored session ready", "");
      elements.input.disabled = false;
      elements.send.disabled = false;
    } catch (error) {
      showToast(`Failed to load messages: ${error.message}`);
    }
  }
  renderSessions();
  renderMessages();
  renderSkillTrace();
  if (elements.pluginSelect && session?.defaultPluginId) elements.pluginSelect.value = normalizePluginId(session.defaultPluginId);
  await renderPrimarySurface();
  closeSessionMenu();
}

function closeSessionMenu() {
  elements.sidebar?.classList.remove("sidebar-open");
  elements.sessionMenuButton?.setAttribute("aria-expanded", "false");
}

function toggleSessionMenu() {
  if (!elements.sidebar || !elements.sessionMenuButton) return;
  const isOpen = elements.sidebar.classList.toggle("sidebar-open");
  elements.sessionMenuButton.setAttribute("aria-expanded", String(isOpen));
}

function handleServerEvent(event) {
  if (event.type === "session_ready") {
    const session = currentSession();
    if (session) {
      session.model = event.configuredModel || event.model || session.model;
      session.actualModel = event.actualModel || null;
      session.actualModelSource = event.modelSource || null;
    }
    setConnectedStatus(session);
    return;
  }
  if (event.type === "model_status") {
    const session = currentSession();
    if (session) {
      session.actualModel = event.model || null;
      session.actualModelSource = event.model ? event.source || null : null;
      session.selectedModel = event.selectedModel || session.selectedModel;
    }
    setConnectedStatus(session);
    return;
  }
  if (event.type === "message_started") {
    const session = currentSession();
    if (session) {
      session.actualModel = null;
      session.actualModelSource = null;
      setConnectedStatus(session);
    }
    state.isBusy = true;
    state.pendingAssistantId = null;
    updateComposerState();
    return;
  }
  if (event.type === "assistant_delta") {
    appendToAssistant(event.content || "");
    return;
  }
  if (event.type === "assistant_complete") {
    if (event.report || event.reportError) {
      const session = currentSession();
      let message = session?.messages.find((item) => item.id === state.pendingAssistantId);
      if (!message && session) {
        message = { id: crypto.randomUUID(), role: "assistant", content: "" };
        session.messages.push(message);
      }
      if (message) {
        message.content = event.content || "";
        message.report = event.report;
        message.reportError = event.reportError;
        renderMessages();
      }
    }
    state.pendingAssistantId = null;
    return;
  }
  if (event.type === "session_idle") {
    state.isBusy = false;
    state.pendingAssistantId = null;
    updateComposerState();
    completeArtifactCanvasWidgets();
    return;
  }
  if (event.type === "plugins_updated") {
    loadPlugins().then(() => {
      renderSessions();
      renderMessages();
      showToast(event.runtimeReady
        ? `Plugin "${event.pluginId}" is installed and runtime-ready.`
        : `Plugin "${event.pluginId}" was installed as ${event.status}; check validation before use.`);
    });
    return;
  }
  if (event.type === "permission_request") {
    openPermissionModal(event);
    return;
  }
  if (event.type === "user_input_request") {
    // Close the current assistant bubble so any text streamed after this
    // prompt starts a NEW bubble below it, preserving reading order.
    state.pendingAssistantId = null;
    appendUserInputMessage(event);
    return;
  }
  if (event.type === "widget_render") {
    // Close the current assistant bubble at the widget boundary; text the
    // agent streams after the user submits must appear below the widget,
    // not back inside the pre-widget bubble above it.
    state.pendingAssistantId = null;
    appendWidgetMessage(event);
    return;
  }
  if (event.type === "image_generated") {
    appendMessage("assistant", event.caption || "Generated image", event.attachment ? [event.attachment] : []);
    return;
  }
  if (event.type === "artifact_generated") {
    if (event.attachment) addArtifactCanvasArtifacts([{ ...event.attachment, artifactType: event.artifactType, scene: event.scene }]);
    return;
  }
  if (event.type === "skill_event") {
    handleSkillEvent(event);
    return;
  }
  if (event.type === "tool_event") {
    return;
  }
  if (event.type === "error") {
    state.isBusy = false;
    closeModal();
    updateComposerState();
    showToast(event.message || "Unknown error");
  }
}

function expirePendingWidgets() {
  const session = currentSession();
  if (!session) return;
  let changed = false;
  for (const message of session.messages) {
    if (message.role === "widget" && message.status === "pending") {
      message.status = "expired";
      message.freeformNote = "This widget is no longer active.";
      changed = true;
    }
  }
  if (changed) renderMessages();
}

function updateComposerState() {
  elements.send.disabled = state.isBusy;
  elements.input.disabled = state.isBusy;
  setArtifactCanvasBusy(state.isBusy);
}

function openPermissionModal(event) {
  state.pendingModal = { kind: "permission", event };
  elements.modalTitle.textContent = "Tool permission request";
  elements.modalDescription.textContent = event.requestType || "InFlak wants to use a tool.";
  elements.modalDetails.textContent = JSON.stringify(event.request || {}, null, 2);
  elements.userInputRow.classList.add("hidden");
  elements.modalApprove.textContent = "Approve once";
  elements.modalReject.textContent = "Reject";
  elements.modalBackdrop.classList.remove("hidden");
}

function openUserInputModal(event) {
  state.pendingModal = { kind: "user_input", event };
  elements.modalTitle.textContent = "InFlak asks";
  elements.modalDescription.textContent = event.question || "InFlak asks for input.";
  elements.modalDetails.textContent = event.choices?.length ? event.choices.join("\n") : "";
  elements.userInputAnswer.value = "";
  elements.userInputRow.classList.remove("hidden");
  elements.modalApprove.textContent = "Send answer";
  elements.modalReject.textContent = "Cancel";
  elements.modalBackdrop.classList.remove("hidden");
  elements.userInputAnswer.focus();
}

function openDeleteSessionModal(session) {
  state.pendingModal = { kind: "delete_session", sessionId: session.id };
  elements.modal.classList.add("delete-session-modal");
  elements.modalTitle.textContent = "Delete session?";
  elements.modalDescription.textContent = "This permanently deletes the conversation and its session-owned files.";
  elements.modalDetails.textContent = `${session.title}\n${session.id}`;
  elements.userInputRow.classList.add("hidden");
  elements.modalApprove.textContent = "Delete";
  elements.modalApprove.classList.add("danger");
  elements.modalReject.textContent = "Cancel";
  elements.modalBackdrop.classList.remove("hidden");
  elements.modalApprove.focus();
}

function appendUserInputMessage(event) {
  const session = currentSession();
  if (!session) return;
  const existing = session.messages.find((item) =>
    item.role === "user_input" && item.requestId === event.requestId
  );
  if (existing) {
    existing.question = event.question || existing.question;
    existing.content = existing.question;
    existing.choices = event.choices || existing.choices || [];
    existing.status = "pending";
    existing.isStored = false;
    renderMessages();
    return;
  }
  const message = {
    id: event.requestId || crypto.randomUUID(),
    role: "user_input",
    label: "Ask",
    content: event.question || "InFlak asks for input.",
    createdAt: Date.now(),
    requestId: event.requestId,
    question: event.question || "InFlak asks for input.",
    choices: event.choices || [],
    status: "pending",
    answer: "",
  };
  session.messages.push(message);
  renderMessages();
}

function renderInlineUserInput(container, message) {
  const title = document.createElement("div");
  title.className = "widget-title";
  title.textContent = "InFlak asks";
  const question = document.createElement("div");
  question.className = "widget-description";
  question.textContent = message.question || message.content || "InFlak asks for input.";
  container.append(title, question);

  const body = document.createElement("div");
  body.className = "inline-widget-body";
  container.append(body);

  if (message.status !== "pending") {
    const status = document.createElement("div");
    status.className = "widget-status";
    status.textContent = message.status === "submitted"
      ? "Answered"
      : message.status === "interrupted" ? "Interrupted" : "Cancelled";
    body.append(status);
    if (message.answer) {
      const pre = document.createElement("pre");
      pre.className = "widget-return-preview";
      pre.textContent = message.answer;
      body.append(pre);
    }
    return;
  }

  const form = document.createElement("form");
  form.className = "inline-widget-form";

  if (Array.isArray(message.choices) && message.choices.length > 0) {
    const choices = document.createElement("div");
    choices.className = "choice-button-grid";
    for (const choice of message.choices) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "choice-button";
      button.textContent = choice;
      button.addEventListener("click", () => {
        input.value = choice;
      });
      choices.append(button);
    }
    form.append(choices);
  }

  const input = document.createElement("textarea");
  input.name = "answer";
  input.placeholder = "Your answer";
  input.required = false;
  form.append(input);

  const actions = document.createElement("div");
  actions.className = "inline-widget-actions";
  const cancel = document.createElement("button");
  cancel.type = "button";
  cancel.className = "secondary";
  cancel.textContent = "Cancel";
  cancel.addEventListener("click", () => submitInlineUserInput(message, ""));
  const submit = document.createElement("button");
  submit.type = "submit";
  submit.className = "primary";
  submit.textContent = "Send answer";
  actions.append(cancel, submit);
  form.append(actions);

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    submitInlineUserInput(message, input.value);
  });
  body.append(form);
}

function submitInlineUserInput(message, answer) {
  sendSocket({
    type: "user_input_response",
    requestId: message.requestId,
    answer,
  });
  message.status = answer ? "submitted" : "cancelled";
  message.answer = answer;
  renderMessages();
}

function openWidgetModal(event) {
  const widget = event.widget || {};
  const display = widget.display || {};
  state.pendingModal = { kind: "widget", event };
  elements.modalTitle.textContent = widget.title || display.title || widget.interaction_goal || "Interactive widget";
  elements.modalDescription.textContent = display.description || widget.interaction_goal || `Widget type: ${widget.widget_type || "unknown"}`;
  elements.modalDetails.replaceChildren();
  elements.userInputAnswer.value = "";
  elements.userInputAnswer.placeholder = "Optional note or JSON values";
  if (widget.widget_type === "html_widget") {
    renderHtmlWidget(widget);
    elements.userInputRow.classList.add("hidden");
  } else {
    elements.modalDetails.textContent = formatWidgetDetails(widget);
    elements.userInputRow.classList.remove("hidden");
  }
  elements.modalApprove.textContent = "Submit";
  elements.modalReject.textContent = "Dismiss";
  elements.modalBackdrop.classList.remove("hidden");
  if (widget.widget_type !== "html_widget") {
    elements.userInputAnswer.focus();
  }
}

function appendWidgetMessage(event) {
  const session = currentSession();
  if (!session) return;
  const widget = event.widget || {};
  const display = widget.display || {};
  const widgetId = event.widgetId || widget.widget_id;
  const existing = session.messages.find((item) => item.role === "widget" && item.widgetId === widgetId);
  if (existing) {
    existing.widget = widget;
    existing.content = display.title || widget.title || widget.interaction_goal || "Interactive widget";
    existing.status = "pending";
    existing.isStored = false;
    renderMessages();
    return existing;
  }
  const message = {
    id: widgetId || crypto.randomUUID(),
    role: "widget",
    label: "UI",
    content: display.title || widget.title || widget.interaction_goal || "Interactive widget",
    createdAt: Date.now(),
    widget,
    widgetId,
    status: "pending",
    interactionHistory: [],
    interactionSequence: 0,
  };
  session.messages.push(message);
  if (widget.surface === "artifact_canvas_widget" || widget.widget_type === "svg_proposal_review") {
    const mounted = mountArtifactCanvasWidget(widget, message.widgetId, buildHtmlWidgetSrcdoc(widget), widget.height);
    if (!mounted) renderMessages();
  } else {
    renderMessages();
  }
  renderSkillTrace();
  return message;
}

function renderInlineWidget(container, message) {
  const widget = message.widget || {};
  const display = widget.display || {};
  const isActive = message.status === "pending";
  const title = document.createElement("div");
  title.className = "widget-title";
  title.textContent = widget.title || display.title || widget.interaction_goal || "Interactive widget";
  const description = document.createElement("div");
  description.className = "widget-description";
  description.textContent = display.description || widget.interaction_goal || "";
  container.append(title, description);

  const body = document.createElement("div");
  body.className = "inline-widget-body";
  container.append(body);

  if (widget.widget_type === "html_widget") {
    const iframe = document.createElement("iframe");
    iframe.className = "html-widget-frame inline-html-widget-frame";
    iframe.setAttribute("sandbox", "allow-scripts allow-forms");
    iframe.setAttribute("scrolling", "no");
    iframe.dataset.widgetId = widget.widget_id || message.widgetId || "";
    iframe.style.height = initialHtmlWidgetHeight(widget);
    iframe.srcdoc = buildHtmlWidgetSrcdoc(widget, {
      readOnly: !isActive,
      interactions: message.interactionHistory || [],
      values: message.returnValues || {},
      controlState: message.controlState || [],
    });
    body.append(iframe);
  } else if (widget.widget_type !== "html_widget") {
    renderWidgetDisplay(body, display);
    body.append(renderSchemaWidgetForm(message, !isActive));
  }

  if ((widget.semantic_widget_type || widget.widget_type) === "plugin_build_review") {
    mountPluginScenarioPanel(body, message);
  }

  if (!isActive) {
    if (message.status === "expired" && !message.freeformNote) {
      message.freeformNote = "This interaction ended when the session disconnected. Resend the request to open a new widget.";
    }
    renderWidgetResult(body, message);
  }
  if (!isP6StructuredResult(message.returnValues || {})) {
    renderWidgetInteractionHistory(body, message.interactionHistory || []);
  }
}

function scenarioActionButton(label, icon, className = "secondary") {
  const button = document.createElement("button");
  button.type = "button";
  button.className = className;
  const glyph = document.createElement("i");
  glyph.setAttribute("data-lucide", icon);
  glyph.setAttribute("aria-hidden", "true");
  const text = document.createElement("span");
  text.textContent = label;
  button.append(glyph, text);
  return button;
}

function buildReviewPluginId(widget) {
  const display = widget.display || {};
  return String(display.plugin_id || display.pluginId || display.plugin_summary?.plugin_id || "").trim();
}

function buildReviewWarnings(widget) {
  return (widget.display?.warnings || []).map((warning) =>
    typeof warning === "string" ? warning : warning.message || JSON.stringify(warning));
}

function scenarioFailurePrompt(pluginId, run, regenerate) {
  const evaluation = run?.evaluation || {};
  const issues = evaluation.issues || [];
  const failedPhase = evaluation.failed_phase || "unknown phase";
  const caseId = run?.case?.id || run?.case_id || "unknown-case";
  const lines = [
    `${regenerate ? "Regenerate" : "Revise"} plugin ${pluginId} from failed acceptance case ${caseId}.`,
    `Scenario run: ${run?.run_id || "unknown"}`,
    `Failed phase: ${failedPhase}.`,
    `Failed checks: ${issues.length ? issues.join(", ") : "inspect the saved trace"}.`,
    "Reopen the smallest affected design phase, preserve unaffected approved decisions, and use the trace, widget contracts/returns, tool results, and artifacts as evidence.",
    `When compiling the corrected bundle, set replace_existing_plugin to true and source_scenario_run_id to ${run?.run_id || "the failed run id"}.`,
  ];
  return lines.join("\n");
}

function sendScenarioFailureToAuthor(pluginId, run, regenerate = false) {
  const prompt = scenarioFailurePrompt(pluginId, run, regenerate);
  if (state.isBusy || !state.socket || state.socket.readyState !== WebSocket.OPEN) {
    elements.input.value = prompt;
    autoResizeInput();
    elements.input.focus();
    showToast("The failure handoff is ready in the composer.");
    return;
  }
  const session = currentSession();
  if (session?.title === "New chat") session.title = `Revise ${pluginId}`;
  appendMessage("user", prompt, []);
  sendSocket({ type: "message", content: prompt, attachments: [], pluginId: "inflak-author" });
}

function submitBuildReviewFromPanel(message, pluginId, warnings) {
  const widget = message.widget || {};
  const display = widget.display || {};
  const values = {
    decision: "publish",
    preview_id: display.preview_id,
    preview_hash: display.preview_hash,
    approved_revision: display.revision,
    change_requests: [],
    acknowledged_warnings: warnings,
  };
  if (!values.preview_id || !values.preview_hash || !values.approved_revision) {
    showToast("This build review is missing its immutable preview identity.");
    return;
  }
  const sent = sendSocket({
    type: "widget_return",
    widgetId: message.widgetId || widget.widget_id,
    plannerId: widget.planner_id,
    action: "accept",
    values,
    freeformNote: `Apply the approved ${pluginId} bundle and run its required acceptance case.`,
    timestamp: new Date().toISOString(),
  });
  if (!sent) return;
  message.status = "submitted";
  message.returnValues = values;
  message.freeformNote = "Approved for hash-bound apply and scenario validation.";
  renderMessages();
}

function renderScenarioRunResult(panel, pluginId, run) {
  panel.latestRun = run;
  const result = panel.querySelector(".scenario-result");
  result.replaceChildren();
  const passed = run?.evaluation?.passed === true;
  const headline = document.createElement("div");
  headline.className = `scenario-result-head ${passed ? "passed" : "failed"}`;
  headline.textContent = `${passed ? "Passed" : "Needs revision"}: ${run?.case?.title || run?.case_id || "scenario"}`;
  result.append(headline);
  const checks = run?.evaluation?.checks || {};
  const checkGrid = document.createElement("div");
  checkGrid.className = "scenario-check-grid";
  for (const [name, ok] of Object.entries(checks)) {
    const check = document.createElement("span");
    check.className = ok ? "passed" : "failed";
    check.textContent = `${ok ? "Pass" : "Fail"} · ${name.replace(/_/g, " ")}`;
    checkGrid.append(check);
  }
  result.append(checkGrid);
  panel.querySelector("[data-scenario-action='inspect']").disabled = !run?.run_id;
  panel.querySelector("[data-scenario-action='return']").disabled = passed || !run?.run_id;
  panel.querySelector("[data-scenario-action='regenerate']").disabled = passed || !run?.run_id;
  const inspect = panel.querySelector("[data-scenario-action='inspect']");
  inspect.dataset.reportUrl = run?.report_url || `/api/inflak/plugins/${encodeURIComponent(pluginId)}/scenario-runs/${encodeURIComponent(run?.run_id || "")}/report`;
}

async function loadPluginScenarioPanel(panel, pluginId) {
  const status = panel.querySelector(".scenario-panel-status");
  const runButton = panel.querySelector("[data-scenario-action='run']");
  const interactiveButton = panel.querySelector("[data-scenario-action='interactive']");
  const caseSelect = panel.querySelector("select");
  try {
    const response = await fetch(`/api/inflak/plugins/${encodeURIComponent(pluginId)}/scenarios`);
    if (!response.ok) throw new Error(await response.text());
    const data = await response.json();
    if (!panel.isConnected) return;
    caseSelect.replaceChildren();
    for (const scenarioCase of data.cases || []) {
      const option = document.createElement("option");
      option.value = scenarioCase.id;
      option.textContent = scenarioCase.title || scenarioCase.id;
      caseSelect.append(option);
    }
    const available = caseSelect.options.length > 0;
    runButton.disabled = !available;
    interactiveButton.disabled = !available;
    status.textContent = available ? `${caseSelect.options.length} approved case${caseSelect.options.length === 1 ? "" : "s"}` : "No approved cases";
    const latest = (data.runs || [])[0];
    if (latest) {
      const runResponse = await fetch(`/api/inflak/plugins/${encodeURIComponent(pluginId)}/scenario-runs/${encodeURIComponent(latest.run_id)}`);
      if (runResponse.ok && panel.isConnected) renderScenarioRunResult(panel, pluginId, await runResponse.json());
    }
  } catch (error) {
    status.textContent = "Available after the approved files are applied";
    runButton.disabled = true;
    interactiveButton.disabled = true;
  }
}

function mountPluginScenarioPanel(body, message) {
  const widget = message.widget || {};
  const pluginId = buildReviewPluginId(widget);
  if (!pluginId) return;
  const panel = document.createElement("section");
  panel.className = "plugin-scenario-panel";
  const heading = document.createElement("div");
  heading.className = "scenario-panel-heading";
  const title = document.createElement("strong");
  title.textContent = "Acceptance run";
  const status = document.createElement("span");
  status.className = "scenario-panel-status";
  status.textContent = "Checking installed build";
  heading.append(title, status);

  const caseRow = document.createElement("div");
  caseRow.className = "scenario-case-row";
  const caseSelect = document.createElement("select");
  caseSelect.setAttribute("aria-label", "Acceptance case");
  const previewCases = widget.display?.validation_cases || widget.display?.plugin_summary?.validation_cases || [];
  for (const scenarioCase of previewCases) {
    const option = document.createElement("option");
    option.value = scenarioCase.id;
    option.textContent = scenarioCase.title || scenarioCase.id;
    caseSelect.append(option);
  }
  caseRow.append(caseSelect);

  const actions = document.createElement("div");
  actions.className = "scenario-actions";
  const run = scenarioActionButton("Run in background", "play");
  run.dataset.scenarioAction = "run";
  run.disabled = true;
  const interactive = scenarioActionButton("Open interactive", "panel-top-open");
  interactive.dataset.scenarioAction = "interactive";
  interactive.disabled = true;
  const inspect = scenarioActionButton("Inspect run", "file-search");
  inspect.dataset.scenarioAction = "inspect";
  inspect.disabled = true;
  const returnToAuthor = scenarioActionButton("Return to Author", "undo-2");
  returnToAuthor.dataset.scenarioAction = "return";
  returnToAuthor.disabled = true;
  const regenerate = scenarioActionButton("Regenerate", "refresh-cw");
  regenerate.dataset.scenarioAction = "regenerate";
  regenerate.disabled = true;
  actions.append(run, interactive, inspect, returnToAuthor, regenerate);

  const warnings = buildReviewWarnings(widget);
  if (message.status === "pending") {
    const apply = scenarioActionButton("Apply approved files", "package-check", "primary");
    apply.dataset.scenarioAction = "apply";
    if (warnings.length) {
      const acknowledgement = document.createElement("label");
      acknowledgement.className = "scenario-warning-ack";
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      const label = document.createElement("span");
      label.textContent = `I reviewed ${warnings.length} build warning${warnings.length === 1 ? "" : "s"}`;
      acknowledgement.append(checkbox, label);
      apply.disabled = true;
      checkbox.addEventListener("change", () => { apply.disabled = !checkbox.checked; });
      panel.append(acknowledgement);
    }
    apply.addEventListener("click", () => submitBuildReviewFromPanel(message, pluginId, warnings));
    actions.append(apply);
  }

  const result = document.createElement("div");
  result.className = "scenario-result";
  panel.prepend(heading, caseRow, actions);
  panel.append(result);
  body.append(panel);

  run.addEventListener("click", async () => {
    run.disabled = true;
    status.textContent = "Running real session";
    try {
      const response = await fetch(`/api/inflak/plugins/${encodeURIComponent(pluginId)}/scenarios/probe`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ case_id: caseSelect.value, timeout_seconds: 120 }),
      });
      if (!response.ok) throw new Error(await response.text());
      const scenarioRun = await response.json();
      renderScenarioRunResult(panel, pluginId, scenarioRun);
      status.textContent = scenarioRun.evaluation?.passed ? "Latest run passed" : "Latest run needs revision";
    } catch (error) {
      status.textContent = "Run failed to start";
      showToast(`Scenario run failed: ${error.message}`);
    } finally {
      run.disabled = false;
    }
  });
  interactive.addEventListener("click", async () => {
    interactive.disabled = true;
    try {
      const response = await fetch(`/api/inflak/plugins/${encodeURIComponent(pluginId)}/scenarios/interactive`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ case_id: caseSelect.value }),
      });
      if (!response.ok) throw new Error(await response.text());
      const scenarioRun = await response.json();
      const opened = window.open(scenarioRun.session_url, "_blank", "noopener");
      if (!opened) window.location.assign(scenarioRun.session_url);
    } catch (error) {
      showToast(`Interactive scenario failed: ${error.message}`);
      interactive.disabled = false;
    }
  });
  inspect.addEventListener("click", () => {
    if (inspect.dataset.reportUrl) window.open(inspect.dataset.reportUrl, "_blank", "noopener");
  });
  returnToAuthor.addEventListener("click", () => sendScenarioFailureToAuthor(pluginId, panel.latestRun, false));
  regenerate.addEventListener("click", () => sendScenarioFailureToAuthor(pluginId, panel.latestRun, true));
  window.lucide?.createIcons();
  void loadPluginScenarioPanel(panel, pluginId);
}

function renderWidgetInteractionHistory(body, interactions) {
  if (!interactions.length) return;
  const details = document.createElement("details");
  details.className = "widget-interaction-history";
  const summary = document.createElement("summary");
  summary.textContent = `Interaction history (${interactions.length})`;
  details.append(summary);
  const list = document.createElement("ol");
  for (const interaction of interactions) {
    const item = document.createElement("li");
    const target = interaction.target?.label || interaction.target?.name || interaction.target?.id || interaction.target?.selector || "widget";
    const value = interaction.value === undefined ? "" : `: ${formatWidgetValue(interaction.value)}`;
    item.textContent = `${interaction.type || "interaction"} · ${target}${value}`;
    list.append(item);
  }
  details.append(list);
  body.append(details);
}

function recordWidgetInteraction(message, interaction) {
  if (!message || message.status !== "pending") return;
  const sequence = (message.interactionSequence || 0) + 1;
  message.interactionSequence = sequence;
  const entry = { ...interaction, timestamp: new Date().toISOString(), sequence };
  const sent = sendSocket({
    type: "widget_interaction",
    widgetId: message.widgetId || message.widget?.widget_id,
    sequence,
    interaction: entry,
  });
  if (sent) message.interactionHistory.push(entry);
}

function renderWidgetResult(body, message) {
  const status = document.createElement("div");
  status.className = `widget-status ${message.status || ""}`.trim();
  const labels = {
    submitted: "Submitted",
    dismissed: "Dismissed",
    expired: "No longer active",
    interrupted: "Interrupted",
  };
  status.textContent = labels[message.status] || "Finished";
  body.append(status);

  const values = message.returnValues || {};
  const hasValues = Object.keys(values).length > 0;
  if (isP6StructuredResult(values)) {
    renderP6ResultStatus(body, values);
    return;
  }
  const hasOrganizedValues = Array.isArray(values.groups) && Array.isArray(values.units);
  if ((hasValues && !hasOrganizedValues) || message.freeformNote) {
    const summary = document.createElement("div");
    summary.className = "widget-return-summary";
    if (hasValues && !hasOrganizedValues) {
      const list = document.createElement("dl");
      for (const [key, value] of Object.entries(values)) {
        const term = document.createElement("dt");
        term.textContent = key.replace(/_/g, " ");
        const description = document.createElement("dd");
        description.textContent = formatWidgetValue(value);
        list.append(term, description);
      }
      if (list.children.length) summary.append(list);
    }
    if (message.freeformNote) {
      const note = document.createElement("div");
      note.className = "widget-return-note";
      note.textContent = message.freeformNote;
      summary.append(note);
    }
    body.append(summary);
  }
}

function isP6StructuredResult(values) {
  return Array.isArray(values.tree_nodes) || Array.isArray(values.brief_sections);
}

function renderP6ResultStatus(body, values) {
  const summary = document.createElement("div");
  summary.className = "widget-return-summary widget-return-status-line";
  const parts = [];
  if (Array.isArray(values.tree_nodes)) {
    parts.push(`${values.tree_nodes.length} branches`);
    parts.push(`${(values.fragment_edits || []).length} fragments`);
  }
  if (Array.isArray(values.brief_sections)) parts.push(`${values.brief_sections.length} sections`);
  parts.push((values.unresolved_ids || []).length ? `${values.unresolved_ids.length} unresolved` : "All resolved");
  if (Object.hasOwn(values, "approved")) parts.push(values.approved ? "Approved" : "Not approved");
  summary.textContent = parts.join(" · ");
  body.append(summary);
}

function formatWidgetValue(value) {
  if (Array.isArray(value)) return value.join(", ");
  if (value && typeof value === "object") return JSON.stringify(value, null, 2);
  if (value === true) return "Yes";
  if (value === false) return "No";
  if (value === null || value === undefined || value === "") return "-";
  return String(value);
}

function collectWidgetDisplayImageRefs(value, key = "", refs = []) {
  const imageKey = /(?:^|_)(?:image|photo|thumbnail|cutout|poster|sketch|mask)(?:_|$)|^(?:before|after|background)_ref$/i.test(key);
  if (value && typeof value === "object" && !Array.isArray(value)) {
    const mime = String(value.mime || value.mime_type || "");
    const name = String(value.filename || value.name || "");
    const hasAssetRef = ["fileId", "file_id", "asset_file_id", "source_file_id", "url", "path", "src"]
      .some((field) => value[field]);
    const imageName = /\.(?:avif|bmp|gif|jpe?g|png|svg|webp)$/i.test(name);
    if (hasAssetRef && (imageKey || mime.startsWith("image/") || imageName)) {
      refs.push({ ref: value, label: name || key.replace(/_/g, " ") || "Image" });
      return refs;
    }
    for (const [nestedKey, nestedValue] of Object.entries(value)) {
      collectWidgetDisplayImageRefs(nestedValue, nestedKey, refs);
    }
    return refs;
  }
  if (Array.isArray(value)) {
    for (const item of value) collectWidgetDisplayImageRefs(item, key, refs);
    return refs;
  }
  if (imageKey && typeof value === "string" && (
    /^(?:file:|https?:|data:image\/|blob:|\/)/i.test(value)
    || /\.(?:avif|bmp|gif|jpe?g|png|svg|webp)(?:[?#].*)?$/i.test(value)
  )) {
    refs.push({ ref: value, label: key.replace(/_/g, " ") || "Image" });
  }
  return refs;
}

function renderWidgetDisplayImages(valueEl, key, value) {
  const sessionId = currentSession()?.id || "";
  const images = new Map();
  for (const imageRef of collectWidgetDisplayImageRefs(value, key)) {
    const url = normalizeHtmlWidgetAssetUrl(imageRef.ref, sessionId);
    if (!url || images.has(url)) continue;
    images.set(url, imageRef.label);
  }
  if (images.size === 0) return false;

  const gallery = document.createElement("div");
  gallery.className = "widget-display-images";
  for (const [url, label] of images) {
    const figure = document.createElement("figure");
    figure.className = "widget-display-image";
    const status = document.createElement("div");
    status.className = "widget-display-image-status hidden";
    status.textContent = "Image unavailable";
    const renderable = /^(?:\/api\/sessions\/[^/]+\/(?:uploads|widget-assets)\/|data:image\/|blob:|https?:)/i.test(url);
    if (renderable) {
      const image = document.createElement("img");
      image.src = url;
      image.alt = label;
      image.loading = "lazy";
      image.addEventListener("error", () => {
        image.hidden = true;
        status.classList.remove("hidden");
      }, { once: true });
      figure.append(image);
    } else {
      status.classList.remove("hidden");
    }
    const caption = document.createElement("figcaption");
    caption.textContent = label;
    figure.append(status, caption);
    gallery.append(figure);
  }
  valueEl.append(gallery);
  return true;
}

const COLOR_TOKEN_PATTERN = /#[0-9a-f]{3,8}\b|rgba?\([^)]*\)|hsla?\([^)]*\)|\b(?:black|white|red|green|blue|yellow|orange|purple|pink|brown|gray|grey|teal|cyan|magenta|navy|maroon|olive|lime|aqua|fuchsia|silver|transparent)\b/gi;

function renderColorToken(color, label = "Color") {
  const preview = document.createElement("span");
  preview.className = "widget-color-preview";
  const swatch = document.createElement("span");
  swatch.className = "widget-color-swatch";
  swatch.style.setProperty("--widget-color", color);
  swatch.setAttribute("role", "img");
  swatch.setAttribute("aria-label", `${label}: ${color}`);
  swatch.title = `${label}: ${color}`;
  const value = document.createElement("span");
  value.className = "widget-color-value";
  value.textContent = color;
  preview.append(swatch, value);
  return preview;
}

function renderStringWithColorPreviews(container, text, label) {
  const source = String(text);
  const matches = [...source.matchAll(new RegExp(COLOR_TOKEN_PATTERN.source, "gi"))];
  if (!matches.length) {
    container.append(document.createTextNode(source));
    return;
  }
  let cursor = 0;
  for (const match of matches) {
    if (match.index > cursor) container.append(document.createTextNode(source.slice(cursor, match.index)));
    container.append(renderColorToken(match[0], label));
    cursor = match.index + match[0].length;
  }
  if (cursor < source.length) container.append(document.createTextNode(source.slice(cursor)));
}

function renderRichWidgetValue(container, value, label = "Value") {
  if (Array.isArray(value)) {
    const list = document.createElement("ul");
    for (const item of value) {
      const entry = document.createElement("li");
      renderRichWidgetValue(entry, item, label);
      list.append(entry);
    }
    container.append(list);
    return;
  }
  if (value && typeof value === "object") {
    const details = document.createElement("dl");
    details.className = "widget-display-structure";
    for (const [key, nestedValue] of Object.entries(value)) {
      const nestedLabel = key.replace(/_/g, " ");
      const term = document.createElement("dt");
      term.textContent = nestedLabel;
      const description = document.createElement("dd");
      renderRichWidgetValue(description, nestedValue, nestedLabel);
      details.append(term, description);
    }
    container.append(details);
    return;
  }
  if (typeof value === "string") {
    renderStringWithColorPreviews(container, value, label);
    return;
  }
  container.append(document.createTextNode(formatWidgetValue(value)));
}

function renderWidgetDisplay(body, display) {
  const skip = new Set(["title", "description"]);
  for (const [key, value] of Object.entries(display || {})) {
    if (skip.has(key) || value === null || value === undefined || value === "") continue;
    const block = document.createElement("div");
    block.className = "widget-display-field";
    const keyEl = document.createElement("div");
    keyEl.className = "widget-display-key";
    keyEl.textContent = key.replace(/_/g, " ");
    block.append(keyEl);
    const valueEl = document.createElement("div");
    valueEl.className = "widget-display-value";
    if (renderWidgetDisplayImages(valueEl, key, value)) {
      // Image references are rendered through the same host resolver as HTML widgets.
    } else {
      renderRichWidgetValue(valueEl, value, key.replace(/_/g, " "));
    }
    block.append(valueEl);
    body.append(block);
  }
}

function renderSchemaWidgetForm(message, disabled = false) {
  const widget = message.widget || {};
  const form = document.createElement("form");
  form.className = `inline-widget-form ${disabled ? "disabled-widget-form" : ""}`.trim();
  const controls = Array.isArray(widget.controls) ? widget.controls : [];
  if (controls.length === 0) {
    const pre = document.createElement("pre");
    pre.className = "widget-return-preview";
    pre.textContent = JSON.stringify(widget, null, 2);
    form.append(pre);
  }
  for (const control of controls) {
    form.append(renderWidgetControl(control));
  }
  const note = document.createElement("textarea");
  note.name = "freeform_note";
  note.placeholder = "Optional note";
  if (message.freeformNote) note.value = message.freeformNote;
  form.append(note);

  setWidgetFormValues(form, message.returnValues || {});

  if (!disabled) {
    form.addEventListener("change", (event) => {
      const field = event.target;
      if (!(field instanceof HTMLInputElement || field instanceof HTMLTextAreaElement || field instanceof HTMLSelectElement)) return;
      recordWidgetInteraction(message, {
        type: "change",
        target: { name: field.name, label: field.closest("label")?.querySelector("span")?.textContent || field.name },
        value: field.type === "checkbox" ? field.checked : field.value,
      });
    });
  }

  if (disabled) {
    for (const field of form.querySelectorAll("input, textarea, select, button")) {
      field.disabled = true;
    }
    return form;
  }

  const actions = document.createElement("div");
  actions.className = "inline-widget-actions";
  const dismiss = document.createElement("button");
  dismiss.type = "button";
  dismiss.className = "secondary";
  dismiss.textContent = "Dismiss";
  dismiss.addEventListener("click", () => submitInlineWidget(message, "dismiss", {}, note.value));
  const submit = document.createElement("button");
  submit.type = "submit";
  submit.className = "primary";
  submit.textContent = "Submit";
  actions.append(dismiss, submit);
  form.append(actions);

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    submitInlineWidget(message, "accept", collectWidgetFormValues(form), note.value);
  });
  return form;
}

function setWidgetFormValues(form, values) {
  for (const [key, value] of Object.entries(values || {})) {
    const field = form.elements[key];
    if (!field) continue;
    if (field instanceof RadioNodeList) {
      field.value = String(value);
    } else if (field.type === "checkbox") {
      field.checked = Boolean(value);
    } else {
      field.value = Array.isArray(value) ? value.join(", ") : String(value ?? "");
    }
  }
}

function renderWidgetControl(control) {
  const field = control.field || control.id || control.name || control.type || crypto.randomUUID();
  const label = control.label || field;
  const type = control.type || "text";
  const wrapper = document.createElement("label");
  wrapper.className = "widget-field";
  const labelText = document.createElement("span");
  labelText.textContent = label;
  wrapper.append(labelText);

  if (type === "textarea") {
    const textarea = document.createElement("textarea");
    textarea.name = field;
    textarea.required = Boolean(control.required);
    textarea.placeholder = control.placeholder || "";
    wrapper.append(textarea);
    return wrapper;
  }
  if (type === "select" || type === "choice_cards" || type === "single_select") {
    const select = document.createElement("select");
    select.name = field;
    select.required = Boolean(control.required);
    const options = control.options || control.choices || [];
    for (const option of options) {
      const optionEl = document.createElement("option");
      if (typeof option === "string") {
        optionEl.value = option;
        optionEl.textContent = option;
      } else {
        optionEl.value = option.value || option.id || option.label || "";
        optionEl.textContent = option.label || option.title || option.value || option.id || "Option";
      }
      select.append(optionEl);
    }
    wrapper.append(select);
    return wrapper;
  }
  const input = document.createElement("input");
  input.name = field;
  input.type = type === "number" || type === "checkbox" ? type : "text";
  input.required = Boolean(control.required);
  input.placeholder = control.placeholder || "";
  wrapper.append(input);
  return wrapper;
}

function collectWidgetFormValues(form) {
  const values = {};
  const data = new FormData(form);
  for (const [key, value] of data.entries()) {
    if (key === "freeform_note") continue;
    values[key] = value;
  }
  return values;
}

function submitInlineWidget(message, action, values, freeformNote = "") {
  if (message.status !== "pending") return;
  const widget = message.widget || {};
  const eventType = action === "dismiss" ? "widget_dismiss" : "widget_return";
  const sent = sendSocket({
    type: eventType,
    widgetId: message.widgetId || widget.widget_id,
    plannerId: widget.planner_id,
    action,
    values,
    freeformNote,
    timestamp: new Date().toISOString(),
  });
  if (!sent) return;
  message.status = action === "dismiss" ? "dismissed" : "submitted";
  message.returnValues = values;
  message.freeformNote = freeformNote;
  renderMessages();
}

function renderHtmlWidget(widget) {
  const iframe = document.createElement("iframe");
  iframe.className = "html-widget-frame";
  iframe.setAttribute("sandbox", "allow-scripts allow-forms");
  iframe.setAttribute("scrolling", "no");
  iframe.dataset.widgetId = widget.widget_id || "";
  iframe.style.height = initialHtmlWidgetHeight(widget);
  iframe.srcdoc = buildHtmlWidgetSrcdoc(widget);
  elements.modalDetails.append(iframe);
}

function initialHtmlWidgetHeight(widget) {
  return `${Math.max(Number(widget.height) || 160, 120)}px`;
}

function resizeHtmlWidgetFrames(widgetId, height) {
  if (!widgetId) return;
  const shouldKeepBottom = elements.messages.scrollHeight - elements.messages.scrollTop - elements.messages.clientHeight <= 32;
  const nextHeight = Math.max(Math.ceil(Number(height) || 0), 80);
  for (const iframe of document.querySelectorAll(".html-widget-frame")) {
    if (iframe.dataset.widgetId === widgetId) {
      const anchoredContainer = iframe.closest("[data-p10-anchored-widget]");
      const reviewContainer = iframe.closest("[data-p10-review-widget]");
      const surface = (anchoredContainer || reviewContainer)?.closest("[data-p10-collage-surface]");
      const availableHeight = surface ? Math.max(180, Math.min(620, surface.clientHeight - 16)) : nextHeight;
      iframe.style.height = `${Math.min(nextHeight, availableHeight)}px`;
      if (anchoredContainer || reviewContainer) {
        iframe.style.maxHeight = `${availableHeight}px`;
        iframe.setAttribute("scrolling", "auto");
        if (anchoredContainer) anchoredContainer.style.maxHeight = `${availableHeight}px`;
      }
    }
  }
  window.dispatchEvent(new CustomEvent("artifact-widget-resize", { detail: { widgetId } }));
  if (shouldKeepBottom) scrollToBottomAfterLayout();
}

// Shared design system injected into EVERY iai-chain widget iframe so that all
// widgets in a chat session look consistent regardless of whether they come
// from a fixed template or are generated on the fly. Tokens mirror the host
// chat UI (see styles.css :root). Widget CSS is appended after this block and
// should only add layout — never redefine the palette, fonts, or button look.
const WIDGET_DESIGN_SYSTEM_CSS = `
    :root {
      --iai-font: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      --iai-bg: #ffffff;
      --iai-surface: #ffffff;
      --iai-surface-soft: #eef3f9;
      --iai-text: #172033;
      --iai-muted: #667085;
      --iai-line: #d9e2ef;
      --iai-accent: #1769d1;
      --iai-accent-strong: #0d4f9e;
      --iai-accent-soft: #e8f1fe;
      --iai-danger: #b42318;
      --iai-danger-soft: #f7e4e1;
      --iai-radius: 10px;
      --iai-radius-sm: 8px;
      --iai-gap: 12px;
      --iai-shadow: 0 6px 20px rgba(29, 51, 84, 0.12);
      --iai-focus: 0 0 0 3px rgba(23, 105, 209, 0.28);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      padding: 16px;
      color: var(--iai-text);
      font-family: var(--iai-font);
      font-size: 14px;
      line-height: 1.5;
      background: var(--iai-bg);
    }
    /* Base element defaults keep even class-less widgets visually consistent. */
    button, input, textarea, select { font: inherit; color: inherit; }
    button {
      cursor: pointer;
      padding: 8px 14px;
      border: 1px solid var(--iai-line);
      border-radius: var(--iai-radius-sm);
      background: var(--iai-surface);
      color: var(--iai-text);
      font-weight: 600;
      transition: background .15s, border-color .15s, box-shadow .15s;
    }
    button:hover { background: var(--iai-surface-soft); }
    button:focus-visible { outline: none; box-shadow: var(--iai-focus); }
    input[type="text"], input[type="number"], input[type="search"],
    input[type="email"], input[type="url"], input[type="password"],
    textarea, select {
      width: 100%;
      padding: 8px 10px;
      border: 1px solid var(--iai-line);
      border-radius: var(--iai-radius-sm);
      background: var(--iai-surface);
      color: var(--iai-text);
    }
    input:focus-visible, textarea:focus-visible, select:focus-visible {
      outline: none;
      border-color: var(--iai-accent);
      box-shadow: var(--iai-focus);
    }
    textarea { resize: vertical; }
    a { color: var(--iai-accent-strong); }
    /* Reusable component classes — prefer these in generated widgets. */
    .iai-widget { display: flex; flex-direction: column; gap: var(--iai-gap); }
    .iai-title { margin: 0; font-size: 16px; font-weight: 700; color: var(--iai-text); }
    .iai-summary { margin: 0; font-size: 13px; color: var(--iai-muted); }
    .iai-card {
      display: flex; flex-direction: column; gap: 4px; text-align: left;
      padding: 12px 14px; border: 1px solid var(--iai-line); border-radius: var(--iai-radius);
      background: var(--iai-surface); cursor: pointer;
      transition: border-color .15s, box-shadow .15s, background .15s;
    }
    .iai-card:hover { border-color: var(--iai-accent); }
    .iai-card.selected {
      border-color: var(--iai-accent); background: var(--iai-accent-soft);
      box-shadow: inset 0 0 0 1px var(--iai-accent);
    }
    .iai-field { display: flex; flex-direction: column; gap: 6px; }
    .iai-label { font-size: 12px; font-weight: 600; color: var(--iai-muted); }
    .iai-actions { display: flex; align-items: center; justify-content: flex-end; gap: 8px; flex-wrap: wrap; }
    .iai-spacer { flex: 1; }
    .iai-btn {
      padding: 8px 16px; border: 1px solid var(--iai-line); border-radius: var(--iai-radius-sm);
      background: var(--iai-surface); color: var(--iai-text); font-weight: 600; cursor: pointer;
      transition: background .15s, border-color .15s, box-shadow .15s;
    }
    .iai-btn:hover { background: var(--iai-surface-soft); }
    .iai-btn:focus-visible { outline: none; box-shadow: var(--iai-focus); }
    .iai-btn-primary { background: var(--iai-accent); border-color: var(--iai-accent); color: #fff; }
    .iai-btn-primary:hover { background: var(--iai-accent-strong); border-color: var(--iai-accent-strong); }
    .iai-btn-secondary { background: var(--iai-surface); color: var(--iai-text); }
    .iai-btn-ghost { background: transparent; border-color: transparent; color: var(--iai-muted); }
    .iai-btn-ghost:hover { background: var(--iai-surface-soft); }
    .iai-chip {
      display: inline-flex; align-items: center; gap: 6px; padding: 6px 10px;
      border: 1px solid var(--iai-line); border-radius: 999px; background: var(--iai-surface);
      color: var(--iai-text); cursor: pointer; font-size: 13px;
    }
    .iai-chip.selected { border-color: var(--iai-accent); background: var(--iai-accent-soft); color: var(--iai-accent-strong); }
    .widget-color-preview { display: inline-flex; align-items: center; gap: 5px; margin: 2px 4px; vertical-align: middle; white-space: nowrap; }
    .widget-color-swatch { width: 22px; height: 22px; flex: 0 0 22px; border: 1px solid rgba(31,42,34,.25); border-radius: 4px; background-color: var(--widget-color); box-shadow: inset 0 0 0 1px rgba(255,255,255,.35); }
    .widget-color-value { color: var(--iai-muted); font-size: 10px; font-variant-numeric: tabular-nums; }
    .group-head:has(> [data-widget-tree-toggle]) { grid-template-columns: 28px minmax(120px, 1fr) 92px auto; }
    .group-tools [data-group-action="up"], .group-tools [data-group-action="down"] { display: none !important; }
    .unit-card[data-widget-unit-drag-handle] { cursor: grab; }
    .unit-card[data-widget-unit-drag-handle]:active { cursor: grabbing; }
    .unit-card[data-widget-unit-drag-handle] input, .unit-card[data-widget-unit-drag-handle] select, .unit-card[data-widget-unit-drag-handle] textarea, .unit-card[data-widget-unit-drag-handle] button { cursor: auto; }
    .unit-card.widget-dragging { opacity: .48; }
    .unit-card.widget-drop-before { box-shadow: inset 0 3px 0 var(--iai-accent), 0 0 0 1px var(--iai-line); }
    .unit-card.widget-drop-after { box-shadow: inset 0 -3px 0 var(--iai-accent), 0 0 0 1px var(--iai-line); }
    .unit-list.widget-drop-into { outline: 2px dashed var(--iai-accent); outline-offset: 3px; min-height: 42px; }
    .unit-actions [data-action="up"], .unit-actions [data-action="down"] { display: none !important; }
    [data-widget-tree-toggle] { width: 28px; height: 28px; padding: 0; font-size: 14px; font-weight: 800; line-height: 1; }
`;

const WIDGET_RESPONSIVE_GUARD_CSS = `
    html, body {
      width: 100% !important;
      overflow-x: hidden !important;
    }
    body *, body *::before, body *::after {
      min-width: 0 !important;
      max-width: 100%;
    }
    p, li, dd, dt, label, a, code, pre, output, [class*="title"], [class*="label"] {
      overflow-wrap: anywhere;
      word-break: break-word;
    }
    img, svg, canvas, video, iframe, input, textarea, select, button {
      max-width: 100% !important;
    }
    pre, code { white-space: pre-wrap; }
    [class*="actions"], [class*="toolbar"] { flex-wrap: wrap !important; }
    .unit-list[hidden] { display: none !important; }
    @media (max-width: 560px) {
      body { padding: 10px !important; }
      body > main, body > section, body > form,
      .panel, .layout, .grid, .workspace, .columns, .split {
        grid-template-columns: minmax(0, 1fr) !important;
      }
    }
`;

function normalizeHtmlWidgetAssetUrl(ref, sessionId) {
  if (!ref || !sessionId) return typeof ref === "string" ? ref : "";
  const explicitFileId = typeof ref === "object"
    ? ref.fileId || ref.file_id || ref.asset_file_id || ref.source_file_id || ""
    : "";
  const rawValue = typeof ref === "object"
    ? explicitFileId || ref.url || ref.path || ref.src || ref.filename || ref.name || ""
    : ref;
  const value = String(rawValue || "").trim();
  if (!value || /^(?:data|blob):/i.test(value)) return value;

  let pathname = value;
  try {
    if (/^(?:file|https?):/i.test(value)) pathname = new URL(value).pathname;
    pathname = decodeURIComponent(pathname.split(/[?#]/, 1)[0]);
  } catch {
    return value;
  }
  const routedWidgetAsset = pathname.match(/\/api\/sessions\/[^/]+\/widget-assets\/(.+)$/i)?.[1];
  const runtimeAsset = pathname.match(/\/\.copilot\/session-state\/([^/]+)\/files\/(.+)$/i);
  const runtimeAssetPath = routedWidgetAsset
    || (runtimeAsset && runtimeAsset[1] === sessionId ? runtimeAsset[2] : "");
  if (runtimeAssetPath) {
    const encodedPath = runtimeAssetPath.split("/").map((part) => encodeURIComponent(part)).join("/");
    return `/api/sessions/${encodeURIComponent(sessionId)}/widget-assets/${encodedPath}`;
  }
  const routedFileId = pathname.match(/\/api\/sessions\/[^/]+\/uploads\/([A-Za-z0-9]+)/i)?.[1]
    || pathname.match(/\/data\/uploads\/[^/]+\/([A-Za-z0-9]+)(?:-|\/|$)/i)?.[1];
  const bareFileId = /^[A-Za-z0-9]{16,}$/.test(value) ? value : "";
  const storedFilenameId = !/^(?:https?):/i.test(value)
    ? (pathname.split("/").pop() || "").match(/^([A-Za-z0-9]{16,})-/)?.[1]
    : "";
  const fileId = String(explicitFileId || routedFileId || bareFileId || storedFilenameId || "");
  if (fileId) return `/api/sessions/${encodeURIComponent(sessionId)}/uploads/${encodeURIComponent(fileId)}`;
  const relativeRuntimeImage = !/^(?:[a-z]+:|\/)/i.test(value)
    && /\.(?:avif|bmp|gif|jpe?g|png|svg|webp)$/i.test(pathname)
    ? pathname.replace(/^\.\//, "")
    : "";
  if (!relativeRuntimeImage) return value;
  const encodedPath = relativeRuntimeImage.split("/").map((part) => encodeURIComponent(part)).join("/");
  return `/api/sessions/${encodeURIComponent(sessionId)}/widget-assets/${encodedPath}`;
}

function normalizeHtmlWidgetAssetRefs(value, sessionId) {
  if (Array.isArray(value)) return value.map((item) => normalizeHtmlWidgetAssetRefs(item, sessionId));
  if (!value || typeof value !== "object") return value;

  const normalized = Object.fromEntries(
    Object.entries(value).map(([key, item]) => [key, normalizeHtmlWidgetAssetRefs(item, sessionId)]),
  );
  const assetKeys = ["fileId", "file_id", "asset_file_id", "source_file_id", "url", "path", "src", "filename"];
  if (!assetKeys.some((key) => Object.hasOwn(normalized, key))) return normalized;
  const url = normalizeHtmlWidgetAssetUrl(normalized, sessionId);
  if (!/^\/api\/sessions\/[^/]+\/(?:uploads|widget-assets)\//.test(url)) return normalized;
  const fileId = url.match(/\/uploads\/([A-Za-z0-9]+)/)?.[1];
  normalized.url = url;
  normalized.path = url;
  if (Object.hasOwn(normalized, "src")) normalized.src = url;
  if (fileId) normalized.fileId = fileId;
  return normalized;
}

function normalizeHtmlWidgetSrcset(source, sessionId, resolveAssetUrl = normalizeHtmlWidgetAssetUrl) {
  const value = String(source || "");
  if (!value || /(?:^|,)\s*data:/i.test(value)) return value;
  return value.split(",").map((candidate) => {
    const trimmed = candidate.trim();
    const descriptor = trimmed.match(/\s+\d+(?:\.\d+)?[wx]\s*$/i)?.[0] || "";
    const url = descriptor ? trimmed.slice(0, -descriptor.length) : trimmed;
    return `${resolveAssetUrl(url, sessionId)}${descriptor}`;
  }).join(", ");
}

function normalizeHtmlWidgetCssAssetUrls(source, sessionId, resolveAssetUrl = normalizeHtmlWidgetAssetUrl) {
  return String(source || "").replace(/url\(\s*(?:(['"])(.*?)\1|([^)]*?))\s*\)/gi, (match, quote, quotedValue, rawValue) => {
    const value = String(quotedValue ?? rawValue ?? "").trim();
    const url = resolveAssetUrl(value, sessionId);
    if (url === value) return match;
    const outputQuote = quote || '"';
    return `url(${outputQuote}${url}${outputQuote})`;
  });
}

function normalizeHtmlWidgetUploadUrls(source, sessionId) {
  if (!source || !sessionId) return String(source || "");
  return String(source)
    .replace(/(\b(?:src|poster|href|xlink:href)\s*=\s*)(["'])(.*?)\2/gi, (attribute, prefix, quote, value) => {
      const url = normalizeHtmlWidgetAssetUrl(value, sessionId);
      return url === value ? attribute : `${prefix}${quote}${url}${quote}`;
    })
    .replace(/(\bsrcset\s*=\s*)(["'])(.*?)\2/gi, (attribute, prefix, quote, value) => {
      const srcset = normalizeHtmlWidgetSrcset(value, sessionId);
      return srcset === value ? attribute : `${prefix}${quote}${srcset}${quote}`;
    })
    .replace(/(\bstyle\s*=\s*)(["'])(.*?)\2/gi, (attribute, prefix, quote, value) => {
      const style = normalizeHtmlWidgetCssAssetUrls(value, sessionId);
      return style === value ? attribute : `${prefix}${quote}${style}${quote}`;
    });
}

function injectHtmlWidgetHistoryState(source, values) {
  if (!Array.isArray(values?.groups) || !Array.isArray(values?.units)) return String(source || "");
  const documentRoot = new DOMParser().parseFromString(`<body>${String(source || "")}</body>`, "text/html");
  const promptStructureRoot = documentRoot.querySelector("[data-prompt-structure]");
  if (!promptStructureRoot) return String(source || "");
  promptStructureRoot.dataset.promptStructure = JSON.stringify(values);
  return documentRoot.body.innerHTML;
}

function enhanceLegacyInpaintBoxDragging(source) {
  const declaration = "let boxes=[];let brush=[];let drawing=false,start=null,current=null;let selected=-1;";
  const pointerEvents = "canvas.addEventListener('pointerdown',ev=>{if(!naturalW)return;canvas.setPointerCapture(ev.pointerId);drawing=true;start=npt(ev);selected=-1;if(mode==='box'){current={x:start.x,y:start.y,width:0,height:0}}else{brush.push({size:34,points:[start]})}draw()});canvas.addEventListener('pointermove',ev=>{if(!drawing)return;const p=npt(ev);if(mode==='box'){const x=Math.min(start.x,p.x),y=Math.min(start.y,p.y);current={x:clamp(x),y:clamp(y),width:clamp(Math.abs(p.x-start.x)),height:clamp(Math.abs(p.y-start.y))}}else{brush[brush.length-1].points.push({x:clamp(p.x),y:clamp(p.y)})}draw()});canvas.addEventListener('pointerup',ev=>{if(!drawing)return;drawing=false;if(mode==='box'&&current){if(current.width>.01&&current.height>.01){boxes.push({...current,id:'box_'+Date.now()});selected=boxes.length-1;setStatus(`${boxes.length} box${boxes.length===1?'':'es'} selected.`)}current=null}draw()});";
  if (!String(source || "").includes(declaration) || !String(source || "").includes(pointerEvents)) return String(source || "");
  const enhancedEvents = "canvas.addEventListener('pointerdown',ev=>{if(!naturalW)return;canvas.setPointerCapture(ev.pointerId);drawing=true;start=npt(ev);moving=null;if(mode==='box'){selected=boxes.findIndex(b=>start.x>=b.x&&start.x<=b.x+b.width&&start.y>=b.y&&start.y<=b.y+b.height);if(selected>=0){const b=boxes[selected];moving={index:selected,offsetX:start.x-b.x,offsetY:start.y-b.y};current=null}else{current={x:start.x,y:start.y,width:0,height:0}}}else{selected=-1;brush.push({size:34,points:[start]})}draw()});canvas.addEventListener('pointermove',ev=>{if(!drawing)return;const p=npt(ev);if(mode==='box'&&moving){const b=boxes[moving.index];b.x=Math.max(0,Math.min(1-b.width,p.x-moving.offsetX));b.y=Math.max(0,Math.min(1-b.height,p.y-moving.offsetY))}else if(mode==='box'){const x=Math.min(start.x,p.x),y=Math.min(start.y,p.y);current={x:clamp(x),y:clamp(y),width:clamp(Math.abs(p.x-start.x)),height:clamp(Math.abs(p.y-start.y))}}else{brush[brush.length-1].points.push({x:clamp(p.x),y:clamp(p.y)})}draw()});canvas.addEventListener('pointerup',ev=>{if(!drawing)return;drawing=false;if(moving){moving=null;setStatus('Box moved.')}else if(mode==='box'&&current){if(current.width>.01&&current.height>.01){boxes.push({...current,id:'box_'+Date.now()});selected=boxes.length-1;setStatus(`${boxes.length} box${boxes.length===1?'':'es'} selected.`)}current=null}draw()});";
  return String(source).replace(declaration, `${declaration}let moving=null;`).replace(pointerEvents, enhancedEvents);
}

function orderP6FragmentsByHierarchy(values) {
  const nodes = Array.isArray(values?.tree_nodes) ? values.tree_nodes : [];
  const fragments = Array.isArray(values?.fragment_edits) ? values.fragment_edits : [];
  if (!nodes.length || !fragments.length) return fragments;
  const nodesByParent = new Map();
  for (const node of nodes) {
    const parentId = String(node.parent_id || "");
    nodesByParent.set(parentId, [...(nodesByParent.get(parentId) || []), node]);
  }
  for (const children of nodesByParent.values()) {
    children.sort((left, right) => Number(left.order || 0) - Number(right.order || 0));
  }
  const rootsById = new Map((nodesByParent.get("") || []).map((node) => [String(node.id), node]));
  const roots = (values.root_ids || []).map((id) => rootsById.get(String(id))).filter(Boolean);
  for (const root of nodesByParent.get("") || []) {
    if (!roots.includes(root)) roots.push(root);
  }
  const fragmentById = new Map(fragments.map((fragment) => [String(fragment.id), fragment]));
  const ordered = [];
  const included = new Set();
  const visit = (node) => {
    for (const id of node.fragment_ids || []) {
      const fragment = fragmentById.get(String(id));
      if (fragment && !included.has(String(id))) {
        ordered.push(fragment);
        included.add(String(id));
      }
    }
    for (const child of nodesByParent.get(String(node.id)) || []) visit(child);
  };
  for (const root of roots) visit(root);
  for (const fragment of fragments) {
    if (!included.has(String(fragment.id))) ordered.push(fragment);
  }
  return ordered;
}

function buildHtmlWidgetSrcdoc(widget, history = {}) {
  const semanticWidgetType = widget.semantic_widget_type || widget.widget_type;
  if (semanticWidgetType === "svg_proposal_review") {
    return buildSvgProposalReviewSrcdoc(widget, history);
  }
  if (semanticWidgetType === "augmented_instruction_review" && !String(widget.html || "").trim()) {
    return buildAugmentedInstructionReviewSrcdoc(widget, history);
  }
  const widgetId = widget.widget_id;
  const sid = currentSession()?.id || "";
  const css = normalizeHtmlWidgetCssAssetUrls(widget.css, sid);
  const historyValues = history.values || {};
  const html = injectHtmlWidgetHistoryState(normalizeHtmlWidgetUploadUrls(widget.html, sid), historyValues);
  const widgetDisplayData = normalizeHtmlWidgetAssetRefs(widget.display || {}, sid);
  for (const key of ["tree_nodes", "root_ids", "selected_node_id", "expanded_node_ids", "brief_sections", "selected_section_id", "unresolved_ids", "approved"]) {
    if (Object.hasOwn(historyValues, key)) widgetDisplayData[key] = historyValues[key];
  }
  if (Array.isArray(historyValues.fragment_edits)) widgetDisplayData.fragments = orderP6FragmentsByHierarchy(historyValues);
  const widgetDisplay = JSON.stringify(widgetDisplayData)
    .replace(/</g, "\\u003c")
    .replace(/>/g, "\\u003e")
    .replace(/&/g, "\\u0026");
  // Older generated widgets used __DISPLAY__ as an unreplaced source placeholder.
  // The iframe protocol exposes the same data through window.widgetDisplay.
  const js = enhanceLegacyInpaintBoxDragging(String(widget.js || "")).replaceAll("__DISPLAY__", widgetDisplay);
  const readOnly = Boolean(history.readOnly);
  const allowLayoutManipulation = Boolean(history.allowLayoutManipulation);
  const interactions = JSON.stringify(history.interactions || []).replace(/</g, "\\u003c");
  const returnValues = JSON.stringify(history.values || {})
    .replace(/</g, "\\u003c")
    .replace(/>/g, "\\u003e")
    .replace(/&/g, "\\u0026");
  const controlState = JSON.stringify(history.controlState || [])
    .replace(/</g, "\\u003c")
    .replace(/>/g, "\\u003e")
    .replace(/&/g, "\\u0026");
  const bootstrap = `
    window.widgetDisplay = Object.freeze(${widgetDisplay});
    window.widgetReturnValues = Object.freeze(${returnValues});
    var __widgetSessionId = ${JSON.stringify(sid)};
    var __resolveWidgetAssetUrl = ${normalizeHtmlWidgetAssetUrl.toString()};
    var __resolveWidgetSrcset = ${normalizeHtmlWidgetSrcset.toString()};
    var __resolveWidgetCssUrls = ${normalizeHtmlWidgetCssAssetUrls.toString()};
    function __patchWidgetAssetProperty(prototype, property, resolver) {
      if (!prototype) return;
      var descriptor = Object.getOwnPropertyDescriptor(prototype, property);
      if (!descriptor || !descriptor.set) return;
      Object.defineProperty(prototype, property, {
        configurable: descriptor.configurable,
        enumerable: descriptor.enumerable,
        get: descriptor.get,
        set: function(value) {
          descriptor.set.call(this, resolver(value, __widgetSessionId, __resolveWidgetAssetUrl));
        }
      });
    }
    __patchWidgetAssetProperty(HTMLImageElement.prototype, 'src', __resolveWidgetAssetUrl);
    __patchWidgetAssetProperty(HTMLImageElement.prototype, 'srcset', __resolveWidgetSrcset);
    if (window.HTMLSourceElement) {
      __patchWidgetAssetProperty(HTMLSourceElement.prototype, 'src', __resolveWidgetAssetUrl);
      __patchWidgetAssetProperty(HTMLSourceElement.prototype, 'srcset', __resolveWidgetSrcset);
    }
    if (window.HTMLVideoElement) __patchWidgetAssetProperty(HTMLVideoElement.prototype, 'poster', __resolveWidgetAssetUrl);
    if (window.HTMLInputElement) __patchWidgetAssetProperty(HTMLInputElement.prototype, 'src', __resolveWidgetAssetUrl);
    var __nativeSetAttribute = Element.prototype.setAttribute;
    function __normalizedWidgetAttribute(element, name, value) {
      var attribute = String(name || '').toLowerCase();
      if (attribute === 'srcset') return __resolveWidgetSrcset(value, __widgetSessionId, __resolveWidgetAssetUrl);
      if (attribute === 'style') return __resolveWidgetCssUrls(value, __widgetSessionId, __resolveWidgetAssetUrl);
      if (attribute === 'src' || attribute === 'poster' || attribute === 'href' || attribute === 'xlink:href') {
        return __resolveWidgetAssetUrl(value, __widgetSessionId);
      }
      return value;
    }
    Element.prototype.setAttribute = function(name, value) {
      return __nativeSetAttribute.call(this, name, __normalizedWidgetAttribute(this, name, value));
    };
    function __repairWidgetAssetElement(element) {
      if (!element || element.nodeType !== 1) return;
      for (var name of ['src', 'srcset', 'poster', 'href', 'xlink:href', 'style']) {
        if (!element.hasAttribute(name)) continue;
        var current = element.getAttribute(name) || '';
        var normalized = __normalizedWidgetAttribute(element, name, current);
        if (normalized !== current) __nativeSetAttribute.call(element, name, normalized);
      }
      if (element.tagName === 'STYLE') {
        var cssText = element.textContent || '';
        var normalizedCss = __resolveWidgetCssUrls(cssText, __widgetSessionId, __resolveWidgetAssetUrl);
        if (normalizedCss !== cssText) element.textContent = normalizedCss;
      }
    }
    function __repairWidgetAssetTree(root) {
      if (!root) return;
      if (root.nodeType === 1) __repairWidgetAssetElement(root);
      if (root.querySelectorAll) {
        for (var element of root.querySelectorAll('[src], [srcset], [poster], [href], [style], style, image')) {
          __repairWidgetAssetElement(element);
        }
      }
    }
    __repairWidgetAssetTree(document);
    if (window.MutationObserver) {
      new MutationObserver(function(records) {
        for (var record of records) {
          if (record.type === 'attributes') __repairWidgetAssetElement(record.target);
          if (record.type === 'characterData') __repairWidgetAssetElement(record.target.parentElement);
          for (var node of record.addedNodes || []) __repairWidgetAssetTree(node);
        }
      }).observe(document.documentElement, { childList: true, subtree: true, attributes: true, characterData: true });
    }
    var __widgetReadOnly = ${JSON.stringify(readOnly)};
    var __widgetAllowLayoutManipulation = ${JSON.stringify(allowLayoutManipulation)};
    var __widgetInteractions = ${interactions};
    var __widgetReturnValues = window.widgetReturnValues;
    var __hasStructuredReturnState = Array.isArray(__widgetReturnValues.groups) && Array.isArray(__widgetReturnValues.units);
    var __hasAuthoritativeSelectionState = __hasStructuredReturnState
      || Object.hasOwn(__widgetReturnValues, 'primary_direction_id')
      || Object.hasOwn(__widgetReturnValues, 'primary_objective_id')
      || (__widgetReturnValues.selected_facets && typeof __widgetReturnValues.selected_facets === 'object')
      || Array.isArray(__widgetReturnValues.tree_nodes)
      || Array.isArray(__widgetReturnValues.brief_sections);
    var __widgetControlState = ${controlState};
    var __interactionSeq = 0;
    function widgetTarget(element) {
      if (!element || element === document || element === window) return { selector: 'document', label: 'widget' };
      element = element.closest && element.closest('button, input, select, textarea, [role="button"], [aria-pressed], [aria-selected]') || element;
      var selector = element.id ? '#' + CSS.escape(element.id) : '';
      if (!selector && element.name) selector = '[name="' + CSS.escape(element.name) + '"]';
      if (!selector && element.dataset) {
        var dataKey = Object.keys(element.dataset).find(function(key) { return element.dataset[key]; });
        if (dataKey) selector = '[data-' + dataKey.replace(/[A-Z]/g, function(char) { return '-' + char.toLowerCase(); }) + '="' + CSS.escape(element.dataset[dataKey]) + '"]';
      }
      if (!selector) {
        var parentElement = element.parentElement;
        var index = parentElement ? Array.prototype.indexOf.call(parentElement.children, element) + 1 : 1;
        selector = element.tagName.toLowerCase() + ':nth-child(' + index + ')';
      }
      return { selector: selector, id: element.id || '', name: element.name || '', label: (element.getAttribute('aria-label') || element.textContent || element.name || element.id || element.tagName).trim().slice(0, 120) };
    }
    function recordWidgetInteraction(type, element, value) {
      if (__widgetReadOnly) return;
      parent.postMessage({ type: 'html_widget_interaction', widgetId: ${JSON.stringify(widgetId)}, sequence: ++__interactionSeq, interaction: { type: type, target: widgetTarget(element), value: value, timestamp: new Date().toISOString() } }, '*');
    }
    function __captureWidgetControlState() {
      var elements = Array.from(document.querySelectorAll('input, select, textarea, [aria-pressed], [aria-selected], [data-selected], [data-active], [data-decision]'));
      return elements.map(function(element) {
        var state = { target: widgetTarget(element), tag: element.tagName.toLowerCase() };
        if ('type' in element) state.type = element.type || '';
        if ('value' in element) state.value = element.value;
        if ('checked' in element) state.checked = Boolean(element.checked);
        if (element instanceof HTMLSelectElement && element.multiple) {
          state.selectedValues = Array.from(element.selectedOptions).map(function(option) { return option.value; });
        }
        state.attributes = {};
        for (var name of ['aria-pressed', 'aria-selected', 'data-selected', 'data-active', 'data-decision']) {
          if (element.hasAttribute(name)) state.attributes[name] = element.getAttribute(name);
        }
        return state;
      });
    }
    document.addEventListener('change', function(event) {
      var element = event.target;
      var value = element && element.type === 'checkbox' ? element.checked : element && 'value' in element ? element.value : undefined;
      recordWidgetInteraction('change', element, value);
    }, true);
    document.addEventListener('click', function(event) {
      if (event.isTrusted) recordWidgetInteraction('click', event.target, undefined);
    }, true);
    window.submitWidget = function(values) {
      if (__widgetReadOnly) return;
      parent.postMessage({
        type: 'html_widget_return',
        widgetId: ${JSON.stringify(widgetId)},
        values: values || {},
        controlState: __captureWidgetControlState()
      }, '*');
    };
    window.dismissWidget = function(note) {
      if (__widgetReadOnly) return;
      parent.postMessage({
        type: 'html_widget_dismiss',
        widgetId: ${JSON.stringify(widgetId)},
        note: note || ''
      }, '*');
    };
    window.focusArtifactBinding = function(objectIds, primaryObjectId) {
      if (__widgetReadOnly) return;
      parent.postMessage({
        type: 'html_widget_artifact_binding',
        widgetId: ${JSON.stringify(widgetId)},
        objectIds: Array.isArray(objectIds) ? objectIds : [],
        primaryObjectId: primaryObjectId || ''
      }, '*');
    };
    window.artifactLayoutDraft = null;
    window.resetArtifactLayoutDraft = function() {
      if (__widgetReadOnly && !__widgetAllowLayoutManipulation) return;
      parent.postMessage({ type: 'html_widget_layout_command', widgetId: ${JSON.stringify(widgetId)}, action: 'reset' }, '*');
    };
    function __installHistoricalLayoutAbstractEditor() {
      if (!__widgetAllowLayoutManipulation) return;
      var canvas = window.widgetDisplay.canvas || {};
      var canvasWidth = Number(canvas.width) || 1200;
      var canvasHeight = Number(canvas.height) || 1200;
      var sourceItems = Array.isArray(window.widgetDisplay.items) ? window.widgetDisplay.items : [];
      var returnedTransforms = Array.isArray(__widgetReturnValues.item_transforms) ? __widgetReturnValues.item_transforms : [];
      var returnedById = new Map(returnedTransforms.map(function(item) { return [String(item.object_id || ''), item]; }));
      var items = sourceItems.filter(function(item) { return item && item.object_id && !item.locked; }).map(function(item) {
        var returned = returnedById.get(String(item.object_id)) || {};
        return {
          id: String(item.object_id),
          label: String(item.label || item.object_id),
          type: String(item.type || 'object'),
          transform: Object.assign({}, item.transform || {}, returned)
        };
      });
      if (!items.length) return;
      var root = document.querySelector('.wrap') || document.body;
      var editor = document.createElement('section');
      editor.className = 'historical-layout-editor';
      editor.setAttribute('aria-label', 'Abstract layout editor');
      editor.innerHTML = '<div class="historical-layout-editor-head"><strong>Layout map</strong><span>Local preview</span></div><div class="historical-layout-stage"></div>';
      var stage = editor.querySelector('.historical-layout-stage');
      var style = document.createElement('style');
      style.textContent = '.historical-layout-editor{margin:14px 0;border:1px solid #b9c3ba;border-radius:8px;background:#f8faf7;padding:10px}.historical-layout-editor-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;color:#33443a;font-size:12px}.historical-layout-editor-head span{color:#718078;font-size:10px;font-weight:700;text-transform:uppercase}.historical-layout-stage{position:relative;overflow:hidden;width:100%;aspect-ratio:'+canvasWidth+'/'+canvasHeight+';border:1px solid #97a59a;border-radius:6px;background:linear-gradient(90deg,transparent 49.8%,#7c8d8138 50%,transparent 50.2%),linear-gradient(transparent 49.8%,#7c8d8138 50%,transparent 50.2%),#e9eee8;touch-action:none}.historical-layout-block{position:absolute;display:grid;place-items:center;overflow:hidden;min-width:28px;min-height:20px;border:1px solid #315f4a;border-radius:4px;background:#dcebdd;color:#203a2e;padding:2px;box-sizing:border-box;cursor:grab;font-size:9px;font-weight:800;line-height:1.05;text-align:center;user-select:none}.historical-layout-block[data-type="text"]{border-color:#9a562f;background:#f5d9bd;color:#64351e}.historical-layout-block:focus,.historical-layout-block.is-active{outline:3px solid #e19a42;outline-offset:1px;z-index:2}.historical-layout-block:active{cursor:grabbing}';
      document.head.append(style);
      root.insertBefore(editor, root.children[1] || root.firstChild);
      var blocks = new Map();
      function renderBlock(item) {
        var block = blocks.get(item.id);
        if (!block) return;
        var transform = item.transform || {};
        var widthPercent = Math.min(58, Math.max(8, Number(transform.width || 120) / canvasWidth * 100));
        var heightPercent = Math.min(42, Math.max(7, Number(transform.height || 80) / canvasHeight * 100));
        var left = Math.min(100 - widthPercent, Math.max(0, Number(transform.x || 0) / canvasWidth * 100));
        var top = Math.min(100 - heightPercent, Math.max(0, Number(transform.y || 0) / canvasHeight * 100));
        Object.assign(block.style, { left:left+'%', top:top+'%', width:widthPercent+'%', height:heightPercent+'%' });
      }
      function sendPreview(item) {
        parent.postMessage({ type:'html_widget_layout_preview', widgetId:${JSON.stringify(widgetId)}, activeObjectId:item.id, itemTransforms:[Object.assign({object_id:item.id}, item.transform)] }, '*');
      }
      for (var item of items) {
        var block = document.createElement('div');
        block.className = 'historical-layout-block';
        block.dataset.objectId = item.id;
        block.dataset.type = item.type;
        block.tabIndex = 0;
        block.textContent = item.label;
        block.title = item.label;
        blocks.set(item.id, block);
        stage.append(block);
        renderBlock(item);
        (function(boundItem, boundBlock) {
          boundBlock.addEventListener('keydown', function(event) {
            if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(event.key)) return;
            event.preventDefault();
            var step = event.shiftKey ? 25 : 10;
            if (event.key === 'ArrowLeft') boundItem.transform.x = (Number(boundItem.transform.x) || 0) - step;
            if (event.key === 'ArrowRight') boundItem.transform.x = (Number(boundItem.transform.x) || 0) + step;
            if (event.key === 'ArrowUp') boundItem.transform.y = (Number(boundItem.transform.y) || 0) - step;
            if (event.key === 'ArrowDown') boundItem.transform.y = (Number(boundItem.transform.y) || 0) + step;
            renderBlock(boundItem);
            sendPreview(boundItem);
          });
          boundBlock.addEventListener('pointerdown', function(event) {
            event.preventDefault();
            for (var candidate of blocks.values()) candidate.classList.remove('is-active');
            boundBlock.classList.add('is-active');
            var startX = event.clientX;
            var startY = event.clientY;
            var originX = Number(boundItem.transform.x) || 0;
            var originY = Number(boundItem.transform.y) || 0;
            try { boundBlock.setPointerCapture(event.pointerId); } catch {}
            sendPreview(boundItem);
            function move(moveEvent) {
              var rect = stage.getBoundingClientRect();
              boundItem.transform.x = originX + (moveEvent.clientX - startX) * canvasWidth / rect.width;
              boundItem.transform.y = originY + (moveEvent.clientY - startY) * canvasHeight / rect.height;
              renderBlock(boundItem);
              sendPreview(boundItem);
            }
            function finish() {
              boundBlock.removeEventListener('pointermove', move);
              boundBlock.removeEventListener('pointerup', finish);
              boundBlock.removeEventListener('pointercancel', finish);
            }
            boundBlock.addEventListener('pointermove', move);
            boundBlock.addEventListener('pointerup', finish);
            boundBlock.addEventListener('pointercancel', finish);
          });
        })(item, block);
      }
      window.addEventListener('artifact-layout-draft', function(event) {
        var detail = event.detail || {};
        var updates = Array.isArray(detail.itemTransforms) ? detail.itemTransforms : [];
        for (var update of updates) {
          var item = items.find(function(candidate) { return candidate.id === String(update.object_id || ''); });
          if (!item) continue;
          item.transform = Object.assign({}, item.transform, update);
          renderBlock(item);
        }
        for (var entry of blocks.entries()) entry[1].classList.toggle('is-active', entry[0] === detail.activeObjectId);
      });
    }
    var __widgetColorPattern = /#[0-9a-f]{3,8}\\b|rgba?\\([^)]*\\)|hsla?\\([^)]*\\)/gi;
    function __widgetColorPreview(color, label) {
      var preview = document.createElement('span');
      preview.className = 'widget-color-preview';
      preview.dataset.widgetColorPreview = '';
      var swatch = document.createElement('span');
      swatch.className = 'widget-color-swatch';
      swatch.style.setProperty('--widget-color', color);
      swatch.setAttribute('role', 'img');
      swatch.setAttribute('aria-label', (label || 'Color') + ': ' + color);
      swatch.title = (label || 'Color') + ': ' + color;
      var value = document.createElement('span');
      value.className = 'widget-color-value';
      value.textContent = color;
      preview.append(swatch, value);
      return preview;
    }
    window.renderWidgetColorPreview = __widgetColorPreview;
    function __enhanceWidgetColorText(root) {
      if (!root || !document.body) return;
      var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
      var nodes = [];
      while (walker.nextNode()) nodes.push(walker.currentNode);
      for (var node of nodes) {
        var parentElement = node.parentElement;
        if (!parentElement || parentElement.closest('script, style, textarea, input, select, option, [data-widget-color-preview]')) continue;
        var text = node.nodeValue || '';
        var matches = Array.from(text.matchAll(new RegExp(__widgetColorPattern.source, 'gi')));
        if (!matches.length) continue;
        var fragment = document.createDocumentFragment();
        var cursor = 0;
        for (var match of matches) {
          if (match.index > cursor) fragment.append(document.createTextNode(text.slice(cursor, match.index)));
          fragment.append(__widgetColorPreview(match[0], parentElement.getAttribute('aria-label') || parentElement.dataset.label || 'Color'));
          cursor = match.index + match[0].length;
        }
        if (cursor < text.length) fragment.append(document.createTextNode(text.slice(cursor)));
        node.replaceWith(fragment);
      }
    }
    __enhanceWidgetColorText(document.body);
    if (window.MutationObserver) {
      new MutationObserver(function(records) {
        for (var record of records) for (var node of record.addedNodes || []) {
          if (node.nodeType === 3) __enhanceWidgetColorText(node.parentElement);
          else if (node.nodeType === 1) __enhanceWidgetColorText(node);
        }
      }).observe(document.body, { childList: true, subtree: true });
    }
    var __uploadSeq = 0;
    var __uploadResolvers = {};
    var __lastTrustedWidgetClick = 0;
    var __bridgedPointerTargets = new Map();
    document.addEventListener('click', function(event) {
      if (event.isTrusted) __lastTrustedWidgetClick = Date.now();
    }, true);
    window.addEventListener('message', function(event) {
      var msg = event.data || {};
      if (msg.type === 'artifact_widget_pointer_sequence' && (!msg.widgetId || msg.widgetId === ${JSON.stringify(widgetId)})) {
        var pointerId = Number(msg.pointerId) || 1;
        var phase = String(msg.phase || 'move');
        var target = phase === 'down'
          ? document.elementFromPoint(Number(msg.x), Number(msg.y))
          : __bridgedPointerTargets.get(pointerId);
        if (phase === 'down' && target) __bridgedPointerTargets.set(pointerId, target);
        if (target) target.dispatchEvent(new PointerEvent('pointer' + phase, {
          bubbles: true,
          cancelable: true,
          pointerId: pointerId,
          button: phase === 'down' ? 0 : -1,
          buttons: phase === 'up' || phase === 'cancel' ? 0 : 1,
          clientX: Number(msg.x),
          clientY: Number(msg.y),
        }));
        if (phase === 'up' || phase === 'cancel') __bridgedPointerTargets.delete(pointerId);
        return;
      }
      if (msg.type === 'artifact_widget_pointer' && (!msg.widgetId || msg.widgetId === ${JSON.stringify(widgetId)})) {
        if (Date.now() - __lastTrustedWidgetClick < 100) return;
        var target = document.elementFromPoint(Number(msg.x), Number(msg.y));
        recordWidgetInteraction('artifact_pointer', target, { x: Number(msg.x), y: Number(msg.y) });
        if (target && typeof target.focus === 'function') target.focus({ preventScroll: true });
        if (target && typeof target.click === 'function') target.click();
        return;
      }
      if (msg.type === 'artifact_widget_wheel' && (!msg.widgetId || msg.widgetId === ${JSON.stringify(widgetId)})) {
        window.scrollBy(Number(msg.deltaX) || 0, Number(msg.deltaY) || 0);
        return;
      }
      if (msg.type === 'artifact_canvas_selection' && (!msg.widgetId || msg.widgetId === ${JSON.stringify(widgetId)})) {
        recordWidgetInteraction('artifact_selection', document, { selected_object_ids: msg.selectedObjectIds || [], active_object_id: msg.activeObjectId || '' });
      }
      if (msg.type === 'artifact_canvas_layout_draft' && (!msg.widgetId || msg.widgetId === ${JSON.stringify(widgetId)})) {
        window.artifactLayoutDraft = msg;
        window.dispatchEvent(new CustomEvent('artifact-layout-draft', { detail: msg }));
      }
      if (msg.type === 'host_upload_result' && msg.uploadId && __uploadResolvers[msg.uploadId]) {
        var r = __uploadResolvers[msg.uploadId];
        delete __uploadResolvers[msg.uploadId];
        if (msg.error) { r.reject(new Error(msg.error)); } else { r.resolve(msg.attachment); }
      }
    });
    window.uploadWidgetFile = function(file) {
      if (__widgetReadOnly) return Promise.reject(new Error('Uploads are unavailable in widget history.'));
      return new Promise(function(resolve, reject) {
        var reader = new FileReader();
        reader.onload = function() {
          var uploadId = 'u' + (++__uploadSeq);
          __uploadResolvers[uploadId] = { resolve: resolve, reject: reject };
          parent.postMessage({
            type: 'html_widget_upload',
            widgetId: ${JSON.stringify(widgetId)},
            uploadId: uploadId,
            name: file.name,
            mime: file.type,
            dataBase64: String(reader.result).split(',')[1] || ''
          }, '*');
        };
        reader.onerror = function() { reject(new Error('read failed')); };
        reader.readAsDataURL(file);
      });
    };
    window.widgetAssetUrl = function(ref) {
      return __resolveWidgetAssetUrl(ref, __widgetSessionId);
    };
    function reportWidgetHeight() {
      var root = document.documentElement;
      var body = document.body;
      var fallbackHeight = Math.max(
        root ? root.scrollHeight : 0,
        root ? root.offsetHeight : 0,
        body ? body.scrollHeight : 0,
        body ? body.offsetHeight : 0
      );
      var contentHeight = 0;
      if (body) {
        var bodyRect = body.getBoundingClientRect();
        for (var child of body.children) {
          contentHeight = Math.max(contentHeight, child.getBoundingClientRect().bottom - bodyRect.top);
        }
        contentHeight += parseFloat(getComputedStyle(body).paddingBottom) || 0;
      }
      var height = contentHeight > 0 ? Math.ceil(contentHeight) : fallbackHeight;
      parent.postMessage({
        type: 'html_widget_resize',
        widgetId: ${JSON.stringify(widgetId)},
        height: height
      }, '*');
    }
    window.addEventListener('load', reportWidgetHeight);
    window.addEventListener('resize', reportWidgetHeight);
    if (window.ResizeObserver) {
      new ResizeObserver(reportWidgetHeight).observe(document.body);
    }
    if (window.MutationObserver) {
      new MutationObserver(reportWidgetHeight).observe(document.body, { childList: true, subtree: true, attributes: true, characterData: true });
    }
    requestAnimationFrame(reportWidgetHeight);
    setTimeout(reportWidgetHeight, 0);
    setTimeout(reportWidgetHeight, 250);
    function __restoreWidgetReturnValues() {
      for (var entry of Object.entries(__widgetReturnValues || {})) {
        var key = entry[0];
        var value = entry[1];
        var fields = Array.from(document.getElementsByName(key));
        if (!fields.length) {
          var byId = document.getElementById(key);
          if (byId) fields.push(byId);
        }
        for (var field of fields) {
          if (!field || !('value' in field || 'checked' in field)) continue;
          if (field.type === 'radio') {
            field.checked = Array.isArray(value)
              ? value.map(String).includes(String(field.value))
              : String(field.value) === String(value == null ? '' : value);
          } else if (field.type === 'checkbox') {
            field.checked = Array.isArray(value)
              ? value.map(String).includes(String(field.value))
              : typeof value === 'boolean' ? value : String(field.value) === String(value == null ? '' : value);
          } else if (field instanceof HTMLSelectElement && field.multiple) {
            var selectedValues = new Set((Array.isArray(value) ? value : [value]).map(String));
            for (var option of field.options) option.selected = selectedValues.has(String(option.value));
          } else {
            field.value = Array.isArray(value) ? value.join(', ') : String(value == null ? '' : value);
          }
          field.dispatchEvent(new Event('input', { bubbles: true }));
          field.dispatchEvent(new Event('change', { bubbles: true }));
        }
        if (value && typeof value === 'object' && !Array.isArray(value)) {
          for (var nestedEntry of Object.entries(value)) {
            var dimension = nestedEntry[0];
            var nestedValue = nestedEntry[1];
            var dimensionRoot = document.querySelector('[data-dimension="' + CSS.escape(dimension) + '"]');
            if (!dimensionRoot) continue;
            if (Array.isArray(nestedValue)) {
              var selectedValues = new Set(nestedValue.map(String));
              for (var candidate of dimensionRoot.querySelectorAll('[data-keyword], [data-value], [aria-pressed], [aria-selected]')) {
                var candidateValue = candidate.dataset.keyword || candidate.dataset.value || candidate.value || '';
                var selected = selectedValues.has(String(candidateValue));
                if (candidate.hasAttribute('aria-pressed')) candidate.setAttribute('aria-pressed', String(selected));
                if (candidate.hasAttribute('aria-selected')) candidate.setAttribute('aria-selected', String(selected));
              }
            } else {
              var nestedField = dimensionRoot.querySelector('[name="' + CSS.escape(key + '.' + dimension) + '"], [name="' + CSS.escape(key + '[' + dimension + ']') + '"], input:not([type="button"]):not([type="submit"]):not([type="reset"]), textarea, select');
              if (nestedField && 'value' in nestedField) {
                nestedField.value = String(nestedValue == null ? '' : nestedValue);
                nestedField.dispatchEvent(new Event('input', { bubbles: true }));
                nestedField.dispatchEvent(new Event('change', { bubbles: true }));
              }
            }
          }
        }
      }
      window.dispatchEvent(new CustomEvent('widget-history-restore', { detail: __widgetReturnValues }));
    }
    function __restoreWidgetControlState() {
      for (var state of __widgetControlState || []) {
        var target = state.target || {};
        var candidates = [];
        if (target.id) {
          var byId = document.getElementById(target.id);
          if (byId) candidates.push(byId);
        }
        if (!candidates.length && target.name) candidates = Array.from(document.getElementsByName(target.name));
        if (!candidates.length && target.selector) {
          var bySelector = document.querySelector(target.selector);
          if (bySelector) candidates.push(bySelector);
        }
        var element = candidates.find(function(candidate) {
          return state.type !== 'radio' && state.type !== 'checkbox' || String(candidate.value) === String(state.value);
        }) || candidates[0];
        if (!element) continue;
        if ('checked' in state && 'checked' in element) element.checked = Boolean(state.checked);
        if (Array.isArray(state.selectedValues) && element instanceof HTMLSelectElement) {
          var selectedValues = new Set(state.selectedValues.map(String));
          for (var option of element.options) option.selected = selectedValues.has(String(option.value));
        } else if ('value' in state && 'value' in element && state.type !== 'radio' && state.type !== 'checkbox') {
          element.value = state.value == null ? '' : String(state.value);
        }
        for (var attribute of Object.entries(state.attributes || {})) element.setAttribute(attribute[0], attribute[1]);
        element.dispatchEvent(new Event('input', { bubbles: true }));
        element.dispatchEvent(new Event('change', { bubbles: true }));
      }
    }
    function __restoreSemanticWidgetSelections() {
      var analysisLensGroups = [
        ['#analysis_focus', 'primary_objective_id', false],
        ['#secondary_focus', 'secondary_lens_ids', true],
        ['#scope', 'scope_ids', true],
        ['#analysis_depth', 'depth_id', false],
        ['#output_format', 'output_format_id', false]
      ];
      if (Object.hasOwn(__widgetReturnValues, 'primary_objective_id')) {
        for (var lensGroup of analysisLensGroups) {
          var lensRoot = document.querySelector(lensGroup[0]);
          if (!lensRoot) continue;
          var returnedValue = __widgetReturnValues[lensGroup[1]];
          var returnedIds = new Set((lensGroup[2] && Array.isArray(returnedValue) ? returnedValue : [returnedValue]).map(String));
          for (var lensButton of lensRoot.querySelectorAll('[data-id]')) {
            var shouldSelect = returnedIds.has(String(lensButton.dataset.id || ''));
            if (lensButton.classList.contains('selected') !== shouldSelect) lensButton.click();
          }
        }
      }

      var candidates = Array.isArray(window.widgetDisplay.candidates) ? window.widgetDisplay.candidates : [];
      var directionCards = Array.from(document.querySelectorAll('.iai-card'));
      if (candidates.length && directionCards.length === candidates.length && Object.hasOwn(__widgetReturnValues, 'primary_direction_id')) {
        var primaryId = String(__widgetReturnValues.primary_direction_id || '');
        var supportingIds = new Set((__widgetReturnValues.supporting_direction_ids || []).map(String));
        var rejectedIds = new Set((__widgetReturnValues.rejected_direction_ids || []).map(String));
        directionCards.forEach(function(card, index) {
          var candidateId = String(candidates[index] && candidates[index].id || '');
          var states = [candidateId === primaryId, supportingIds.has(candidateId), rejectedIds.has(candidateId)];
          card.classList.toggle('primary', states[0]);
          card.classList.toggle('supporting', states[1]);
          card.classList.toggle('rejected', states[2]);
          Array.from(card.querySelectorAll('.iai-card-actions button')).forEach(function(button, buttonIndex) {
            button.setAttribute('aria-pressed', String(Boolean(states[buttonIndex])));
          });
        });
      }

      var selectedFacets = __widgetReturnValues.selected_facets;
      var facets = Array.isArray(window.widgetDisplay.facets) ? window.widgetDisplay.facets : [];
      var facetSections = Array.from(document.querySelectorAll('.iai-facet'));
      if (selectedFacets && typeof selectedFacets === 'object' && facets.length === facetSections.length) {
        facetSections.forEach(function(section, index) {
          var facetId = String(facets[index] && facets[index].id || '');
          var selectedValues = new Set((selectedFacets[facetId] || []).map(String));
          for (var button of section.querySelectorAll('.iai-chip')) {
            var value = button.textContent === 'Leave open' ? 'leave_open' : button.textContent;
            button.setAttribute('aria-pressed', String(selectedValues.has(String(value))));
          }
          var customInput = section.querySelector('.iai-custom');
          if (customInput) customInput.value = String(__widgetReturnValues.custom_facets && __widgetReturnValues.custom_facets[facetId] || '');
        });
        var promptEdits = document.getElementById('promptEdits');
        if (promptEdits) promptEdits.value = String(__widgetReturnValues.prompt_edits || '');
        var freeformNote = document.getElementById('freeformNote');
        if (freeformNote) freeformNote.value = String(__widgetReturnValues.freeform_note || '');
      }
    }
    function __syncHistoricalP6FragmentsToSelection() {
      var treeNodes = Array.isArray(window.widgetDisplay.tree_nodes) ? window.widgetDisplay.tree_nodes : [];
      var fragments = Array.isArray(window.widgetDisplay.fragments) ? window.widgetDisplay.fragments : [];
      var fragmentRoot = document.getElementById('fragments');
      if (!treeNodes.length || !fragments.length || !fragmentRoot) return;
      var selectedRow = document.querySelector('#tree [role="treeitem"][aria-selected="true"][data-id]');
      var selectedId = String(selectedRow && selectedRow.dataset.id || window.widgetDisplay.selected_node_id || '');
      var selectedNode = treeNodes.find(function(node) { return String(node.id) === selectedId; });
      if (!selectedNode) return;
      var visibleIds = new Set((selectedNode.fragment_ids || []).map(String));
      var cards = Array.from(fragmentRoot.querySelectorAll('.frag'));
      cards.forEach(function(card, index) {
        var fragment = fragments[index];
        card.hidden = !fragment || !visibleIds.has(String(fragment.id));
      });
      var panel = fragmentRoot.closest('.iai-panel');
      var heading = panel && panel.querySelector('h3');
      if (heading) heading.textContent = 'Traceable fragments · ' + String(selectedNode.label || 'Selected branch');
    }
    document.addEventListener('click', function(event) {
      if (!event.target.closest('#tree .tree-label, #tree [role="treeitem"]')) return;
      setTimeout(__syncHistoricalP6FragmentsToSelection, 0);
    });
    function __restoreP7ParameterValues() {
      var parameterValues = __widgetReturnValues.parameter_values;
      var parameters = window.widgetDisplay.prompt_document && window.widgetDisplay.prompt_document.parameters;
      var tokens = Array.from(document.querySelectorAll('.p7-token'));
      if (!parameterValues || typeof parameterValues !== 'object' || !Array.isArray(parameters) || parameters.length !== tokens.length) return;
      parameters.forEach(function(parameter, index) {
        if (!Object.hasOwn(parameterValues, parameter.id)) return;
        var token = tokens[index];
        var select = token.querySelector('select');
        var customInput = token.querySelector('.p7-custom');
        if (!select) return;
        var value = String(parameterValues[parameter.id] == null ? '' : parameterValues[parameter.id]);
        var hasOption = Array.from(select.options).some(function(option) { return String(option.value) === value; });
        select.value = hasOption ? value : '__custom__';
        if (customInput) customInput.value = value;
        select.dispatchEvent(new Event('change', { bubbles: true }));
        if (!hasOption && customInput) customInput.dispatchEvent(new Event('input', { bubbles: true }));
      });
    }
    function __enhanceStructuredWidgetTree() {
      var groupsRoot = document.querySelector('.groups');
      if (groupsRoot) {
        groupsRoot.setAttribute('role', 'tree');
        groupsRoot.setAttribute('aria-label', 'Prompt structure groups');
      }
      for (let group of document.querySelectorAll('.group-card')) {
        let header = group.querySelector(':scope > .group-head');
        let unitList = group.querySelector(':scope > .unit-list');
        if (!header || !unitList || header.querySelector('[data-tree-toggle], [data-widget-tree-toggle]')) continue;
        if (!unitList.id) unitList.id = 'widget-unit-list-' + Math.random().toString(36).slice(2);
        let toggle = document.createElement('button');
        toggle.type = 'button';
        toggle.className = 'icon-button tree-toggle';
        toggle.dataset.widgetTreeToggle = '';
        toggle.setAttribute('aria-controls', unitList.id);
        group.setAttribute('role', 'treeitem');
        unitList.setAttribute('role', 'group');
        for (var unit of unitList.querySelectorAll('[data-unit]')) unit.setAttribute('role', 'treeitem');
        const setExpanded = function(expanded) {
          toggle.setAttribute('aria-expanded', String(expanded));
          group.setAttribute('aria-expanded', String(expanded));
          toggle.setAttribute('aria-label', expanded ? 'Collapse group' : 'Expand group');
          toggle.title = expanded ? 'Collapse group' : 'Expand group';
          toggle.textContent = expanded ? '▾' : '▸';
          unitList.hidden = !expanded;
          group.dataset.collapsed = String(!expanded);
        };
        setExpanded(true);
        toggle.addEventListener('click', function() {
          setExpanded(toggle.getAttribute('aria-expanded') !== 'true');
          requestAnimationFrame(reportWidgetHeight);
        });
        header.prepend(toggle);
      }
    }
    function __enhanceStructuredWidgetUnitDrag() {
      var groupsRoot = document.querySelector('.groups');
      if (!groupsRoot) return;
      var draggedUnit = null;
      function clearDragState() {
        draggedUnit = null;
        for (var element of groupsRoot.querySelectorAll('.widget-dragging, .widget-drop-before, .widget-drop-after, .widget-drop-into')) {
          element.classList.remove('widget-dragging', 'widget-drop-before', 'widget-drop-after', 'widget-drop-into');
        }
      }
      function refreshEmptyState(unitList) {
        if (!unitList) return;
        var empty = unitList.querySelector(':scope > .empty-group');
        if (unitList.querySelector(':scope > [data-unit]')) empty?.remove();
        else if (!empty) {
          empty = document.createElement('p');
          empty.className = 'empty-group';
          empty.textContent = 'No units in this group.';
          unitList.append(empty);
        }
      }
      function moveUnit(source, targetList, target, after) {
        if (!source || !targetList || source === target) { clearDragState(); return; }
        var sourceList = source.parentElement;
        targetList.querySelector(':scope > .empty-group')?.remove();
        targetList.insertBefore(source, target ? (after ? target.nextSibling : target) : null);
        var groupId = targetList.closest('[data-group]')?.dataset.group || '';
        var groupSelect = source.querySelector('[data-field="group_id"]');
        if (groupSelect && groupId) groupSelect.value = groupId;
        clearDragState();
        refreshEmptyState(sourceList);
        refreshEmptyState(targetList);
        requestAnimationFrame(reportWidgetHeight);
      }
      for (let unitList of groupsRoot.querySelectorAll('.unit-list')) {
        unitList.addEventListener('dragover', function(event) {
          if (!draggedUnit || event.target.closest('[data-unit]')) return;
          event.preventDefault();
          for (var element of groupsRoot.querySelectorAll('.widget-drop-before, .widget-drop-after, .widget-drop-into')) element.classList.remove('widget-drop-before', 'widget-drop-after', 'widget-drop-into');
          unitList.classList.add('widget-drop-into');
        });
        unitList.addEventListener('drop', function(event) {
          if (!draggedUnit || event.target.closest('[data-unit]')) return;
          event.preventDefault();
          moveUnit(draggedUnit, unitList, null, true);
        });
      }
      for (let unit of groupsRoot.querySelectorAll('[data-unit]')) {
        unit.draggable = true;
        unit.dataset.widgetUnitDragHandle = '';
        unit.tabIndex = 0;
        var text = unit.querySelector('[data-field="raw_text"]')?.value || 'unit';
        unit.setAttribute('aria-label', 'Drag to reorder ' + text);
        unit.title = 'Drag to reorder unit';
        unit.addEventListener('dragstart', function(event) {
          if (event.target.closest('button, input, select, textarea')) { event.preventDefault(); return; }
          draggedUnit = unit;
          unit.classList.add('widget-dragging');
          event.dataTransfer.effectAllowed = 'move';
          event.dataTransfer.setData('text/plain', unit.dataset.unit || 'unit');
        });
        unit.addEventListener('dragover', function(event) {
          if (!draggedUnit || draggedUnit === unit) return;
          event.preventDefault();
          event.stopPropagation();
          var after = event.clientY > unit.getBoundingClientRect().top + unit.offsetHeight / 2;
          for (var element of groupsRoot.querySelectorAll('.widget-drop-before, .widget-drop-after, .widget-drop-into')) element.classList.remove('widget-drop-before', 'widget-drop-after', 'widget-drop-into');
          unit.classList.add(after ? 'widget-drop-after' : 'widget-drop-before');
        });
        unit.addEventListener('drop', function(event) {
          if (!draggedUnit || draggedUnit === unit) return;
          event.preventDefault();
          event.stopPropagation();
          moveUnit(draggedUnit, unit.parentElement, unit, unit.classList.contains('widget-drop-after'));
        });
        unit.addEventListener('dragend', clearDragState);
        unit.addEventListener('keydown', function(event) {
          if (!event.altKey || !['ArrowUp', 'ArrowDown'].includes(event.key)) return;
          event.preventDefault();
          var sibling = event.key === 'ArrowUp' ? unit.previousElementSibling : unit.nextElementSibling;
          if (sibling?.matches('[data-unit]')) moveUnit(unit, unit.parentElement, sibling, event.key === 'ArrowDown');
          unit.focus();
        });
      }
    }
    function __resolveInteractionTarget(interaction) {
      var targetInfo = interaction && interaction.target || {};
      var target = targetInfo.selector ? document.querySelector(targetInfo.selector) : null;
      if (interaction && interaction.type === 'change' && target && target.type === 'radio') {
        var radioName = targetInfo.name || target.name;
        var candidates = radioName ? Array.from(document.getElementsByName(radioName)) : [];
        target = candidates.find(function(candidate) {
          return candidate.type === 'radio' && String(candidate.value) === String(interaction.value);
        }) || target;
      }
      return target;
    }
    window.addEventListener('load', function() {
      if (!__widgetReadOnly) return;
      __installHistoricalLayoutAbstractEditor();
      if (!__hasAuthoritativeSelectionState) {
        for (var interaction of __widgetInteractions) {
          var target = __resolveInteractionTarget(interaction);
          if (!target) continue;
          if (interaction.type === 'change' && 'value' in target) {
            if (target.type === 'checkbox') target.checked = Boolean(interaction.value);
            else if (target.type === 'radio') target.checked = true;
            else target.value = interaction.value == null ? '' : interaction.value;
            target.dispatchEvent(new Event('input', { bubbles: true }));
            target.dispatchEvent(new Event('change', { bubbles: true }));
          } else if (interaction.type === 'click' || interaction.type === 'artifact_pointer') {
            target.click();
          }
        }
      }
      __restoreWidgetReturnValues();
      __restoreWidgetControlState();
      __restoreSemanticWidgetSelections();
      __syncHistoricalP6FragmentsToSelection();
      __restoreP7ParameterValues();
      __enhanceStructuredWidgetTree();
      __enhanceStructuredWidgetUnitDrag();
      function __isHistoricalLocalControl(control) {
        if (__widgetAllowLayoutManipulation && control.matches('#reset')) return true;
        return control.matches([
          '[data-tree-toggle]',
          '[data-widget-tree-toggle]',
          '#boxBtn',
          '#brushBtn',
          '#clearBtn',
          '#slider[type="range"]',
          '.p7-widget select',
          '.p7-widget .p7-custom',
          '[data-ire-mode]',
          '[data-ire-clear-boxes]',
          '[data-ire-remove-box]'
        ].join(', '));
      }
      function __lockHistoricalWidget() {
        for (var control of document.querySelectorAll('button, input, select, textarea')) {
          control.disabled = !__isHistoricalLocalControl(control);
        }
        window.scrollTo(0, 0);
      }
      __lockHistoricalWidget();
      setTimeout(__lockHistoricalWidget, 0);
      setTimeout(__lockHistoricalWidget, 250);
      document.documentElement.dataset.history = 'true';
    });
  `;
  return `<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline' https://cdn.quilljs.com https://cdn.jsdelivr.net https://esm.sh; script-src 'unsafe-inline' https://cdn.quilljs.com https://cdn.jsdelivr.net https://esm.sh; img-src data: blob: https: ${location.origin}; frame-src ${location.origin}; font-src data:; connect-src 'none'; form-action 'none'; base-uri 'none';" />
  <style>
    ${WIDGET_DESIGN_SYSTEM_CSS}
    ${css}
    ${WIDGET_RESPONSIVE_GUARD_CSS}
  </style>
</head>
<body>
  ${html}
  <script>${bootstrap}</script>
  <script>${js}</script>
</body>
</html>`;
}

function buildAugmentedInstructionReviewSrcdoc(widget, history = {}) {
  const widgetId = JSON.stringify(widget.widget_id || "");
  const display = JSON.stringify(widget.display || {}).replace(/</g, "\\u003c");
  const readOnly = Boolean(history.readOnly);
  return `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <style>${WIDGET_DESIGN_SYSTEM_CSS}
    body{padding:16px;background:var(--iai-bg);color:var(--iai-text)}.review{display:grid;gap:14px;max-width:920px;margin:0 auto}.review-header{display:grid;gap:4px}.review-header h2{margin:0;font-size:20px}.review-header p{margin:0;color:var(--iai-muted);font-size:12px}.instruction-field{display:grid;gap:6px}.instruction-field textarea{box-sizing:border-box;width:100%;min-height:92px;resize:vertical;border:1px solid var(--iai-line);border-radius:7px;padding:10px;background:var(--iai-surface);color:var(--iai-text);font:inherit}.section{display:grid;gap:8px}.section h3{margin:0;font-size:14px}.item-list{display:grid;gap:8px}.review-item{display:grid;gap:5px;width:100%;border:1px solid var(--iai-line);border-radius:7px;padding:10px;background:var(--iai-surface);color:var(--iai-text);text-align:left;box-sizing:border-box}.review-item[data-bound="true"]{cursor:pointer}.review-item[data-bound="true"]:focus-visible{outline:2px solid var(--iai-accent);outline-offset:2px}.item-head{display:flex;align-items:center;justify-content:space-between;gap:8px}.item-head strong{font-size:13px}.status{font-size:11px;padding:2px 6px;border-radius:999px;background:var(--iai-surface-soft)}.binding{color:var(--iai-muted);font-size:11px;overflow-wrap:anywhere}.summary{font-size:12px;line-height:1.45}.empty{margin:0;color:var(--iai-muted);font-size:12px}.actions{position:sticky;bottom:0;display:flex;flex-wrap:wrap;gap:8px;padding-top:10px;background:var(--iai-bg)}.actions button{min-height:36px}.actions .primary{margin-left:auto}@media(max-width:560px){body{padding:10px}.actions button{flex:1 1 44%}.actions .primary{margin-left:0}}
  </style></head><body><main class="review" aria-labelledby="review-title"><header class="review-header"><h2 id="review-title">Review augmented instruction</h2><p id="source"></p></header><label class="instruction-field"><strong>Generated instruction</strong><textarea id="instruction"></textarea></label><section class="section"><h3>Actionable operations</h3><div class="item-list" id="operations"></div></section><section class="section"><h3>Suggestion decisions</h3><div class="item-list" id="decisions"></div></section><div class="actions"><button type="button" class="iai-btn iai-btn-ghost" data-action="start_over">Start over</button><button type="button" class="iai-btn iai-btn-secondary" data-action="regenerate">Regenerate</button><button type="button" class="iai-btn iai-btn-secondary" data-action="edit_decisions">Edit decisions</button><button type="button" class="iai-btn iai-btn-ghost" data-action="dismiss">Dismiss</button><button type="button" class="iai-btn iai-btn-primary primary" data-action="confirm">Confirm instruction</button></div></main>
  <script>
    const widgetId=${widgetId};const display=${display};const readOnly=${JSON.stringify(readOnly)};const instruction=structuredClone(display.instruction||{});const textarea=document.getElementById('instruction');
    const idsFor=value=>[...new Set([...(value?.object_ids||[]),...(value?.confirmed_object_ids||[]),...(value?.target_object_ids||[]),...(value?.target_object_id?[value.target_object_id]:[]),...(value?.object_id?[value.object_id]:[])].map(String).filter(Boolean))];
    function focusArtifactBinding(objectIds,primaryObjectId){if(readOnly||!objectIds.length)return;parent.postMessage({type:'html_widget_artifact_binding',widgetId,objectIds,primaryObjectId:primaryObjectId||objectIds[0]},'*')}window.focusArtifactBinding=focusArtifactBinding;
    function addItem(container,value,title,summary,status){const ids=idsFor(value);const row=document.createElement(ids.length?'button':'div');if(ids.length)row.type='button';row.className='review-item';row.dataset.bound=String(Boolean(ids.length));const head=document.createElement('div');head.className='item-head';const label=document.createElement('strong');label.textContent=String(title||'Item');const badge=document.createElement('span');badge.className='status';badge.textContent=String(status||'');head.append(label,badge);const detail=document.createElement('div');detail.className='summary';detail.textContent=String(summary||'');const binding=document.createElement('div');binding.className='binding';binding.textContent=ids.length?'Bound to: '+ids.join(', '):'No object binding';row.append(head,detail,binding);if(ids.length)row.addEventListener('click',()=>focusArtifactBinding(ids,String(value?.primary_object_id||value?.target_object_id||value?.object_id||ids[0])));container.append(row)}
    const source=instruction.source_artifact||{};document.getElementById('source').textContent='Source revision '+String(source.revision??'unknown')+' · '+String(source.fileId||source.file_id||'SVG artifact');textarea.value=instruction.natural_language_instruction||instruction.objective||'';textarea.readOnly=readOnly;
    const operations=document.getElementById('operations');for(const operation of instruction.operations||[]){const params=operation.parameters||{};addItem(operations,operation,operation.type||operation.op||'Operation',params.summary||params.text||params.new_text||operation.objective||JSON.stringify(params),'action')}if(!operations.children.length)operations.innerHTML='<p class="empty">No actionable operations.</p>';
    const decisions=document.getElementById('decisions');for(const decision of display.suggestion_decisions||instruction.suggestion_decisions||[]){addItem(decisions,decision,decision.title||decision.suggestion_id||'Suggestion',decision.objective||decision.edited_objective||decision.rationale||'',decision.decision||'pending')}if(!decisions.children.length)decisions.innerHTML='<p class="empty">No suggestion decisions were supplied.</p>';
    function submit(action){if(readOnly)return;if(action==='dismiss'){parent.postMessage({type:'html_widget_dismiss',widgetId,note:''},'*');return}const next=structuredClone(instruction);next.natural_language_instruction=textarea.value.trim();parent.postMessage({type:'html_widget_return',widgetId,values:{action:action,instruction:next,suggestion_decisions:display.suggestion_decisions||next.suggestion_decisions||[]}},'*')}
    for(const button of document.querySelectorAll('[data-action]')){button.disabled=readOnly;button.addEventListener('click',()=>submit(button.dataset.action))}addEventListener('load',()=>parent.postMessage({type:'html_widget_resize',widgetId,height:document.documentElement.scrollHeight},'*'));
  </script></body></html>`;
}

function buildSvgProposalReviewSrcdoc(widget, history = {}) {
  const widgetId = JSON.stringify(widget.widget_id || "");
  const display = JSON.stringify(widget.display || {}).replace(/</g, "\\u003c");
  const readOnly = Boolean(history.readOnly);
  const interactions = JSON.stringify(history.interactions || []).replace(/</g, "\\u003c");
  return `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <style>${WIDGET_DESIGN_SYSTEM_CSS}
    body{padding:12px}.proposal-list{display:grid;gap:10px}.proposal{border:1px solid var(--iai-line);border-radius:8px;padding:10px;background:var(--iai-surface)}
    .proposal.is-related{border-color:var(--iai-accent);box-shadow:var(--iai-focus)}.proposal h3{margin:0 0 4px;font-size:14px}.proposal p{margin:4px 0;color:var(--iai-muted);font-size:12px}
    .proposal-meta{display:flex;gap:6px;flex-wrap:wrap;margin:7px 0}.proposal-meta span{font-size:11px;padding:2px 6px;border-radius:999px;background:var(--iai-surface-soft)}
    .decision{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}.decision button{display:flex;align-items:center;justify-content:center;min-height:34px;border:1px solid var(--iai-line);border-radius:7px;padding:5px;background:var(--iai-surface);color:var(--iai-text);cursor:pointer;font-size:12px}.decision button[aria-pressed="true"]{border-color:var(--iai-accent);background:var(--iai-accent-soft)}.edit-note{margin-top:7px;display:none}.proposal.is-editing .edit-note{display:block}
    .actions{display:flex;gap:8px;flex-wrap:wrap;position:sticky;bottom:0;padding-top:10px;background:var(--iai-bg)}.actions button{flex:1 1 auto}.decision-progress{flex:1 0 100%;color:var(--iai-muted);font-size:12px}
  </style></head><body><main class="iai-widget"><h2 class="iai-title">Review SVG proposals</h2><p class="iai-summary">Click an SVG object to highlight related proposals, then accept, edit, or reject each proposal.</p><form id="review"><div class="proposal-list" id="proposals"></div><div class="actions"><button class="iai-btn iai-btn-primary" type="submit">Continue</button><button class="iai-btn iai-btn-secondary" type="button" id="regenerate">Regenerate</button><button class="iai-btn iai-btn-ghost" type="button" id="dismiss">Dismiss</button></div></form></main>
  <script>
    const widgetId=${widgetId};const display=${display};const readOnly=${JSON.stringify(readOnly)};const history=${interactions};const list=document.getElementById('proposals');const form=document.getElementById('review');const continueButton=form.querySelector('button[type="submit"]');const progress=document.createElement('span');progress.className='decision-progress';form.querySelector('.actions').prepend(progress);let interactionSeq=0;
    function record(type,target,value){if(!readOnly)parent.postMessage({type:'html_widget_interaction',widgetId,sequence:++interactionSeq,interaction:{type,target,value,timestamp:new Date().toISOString()}},'*')}
    function focusBinding(objectIds,primaryObjectId){if(!readOnly)parent.postMessage({type:'html_widget_artifact_binding',widgetId,objectIds,primaryObjectId:primaryObjectId||objectIds[0]||''},'*')}
    let lastTrustedWidgetClick=0;document.addEventListener('click',event=>{if(event.isTrusted)lastTrustedWidgetClick=Date.now()},true);
    const esc=value=>String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
    const proposalTargets=proposal=>[...new Set([...(proposal.target_object_ids||[]),...(proposal.targets||[]),...(proposal.selected_stable_ids||[]),...(proposal.target_hypotheses||[]).map(target=>target.object_id).filter(Boolean)])];
    function updateProgress(){const cards=[...document.querySelectorAll('.proposal')];const decided=cards.filter(card=>card.dataset.decision).length;progress.textContent=decided+' of '+cards.length+' decided';continueButton.disabled=decided!==cards.length}
    for(const proposal of display.proposals||[]){const id=String(proposal.proposal_id||'');const targets=proposalTargets(proposal);const evidence=Array.isArray(proposal.evidence)?proposal.evidence.join(' '):proposal.evidence||'';const result=proposal.concrete_result||proposal.semantic_operation?.summary||'';const card=document.createElement('section');card.className='proposal';card.tabIndex=0;card.dataset.proposalId=id;card.dataset.targets=JSON.stringify(targets);card.innerHTML='<h3>'+esc(proposal.title||id)+'</h3><p>'+esc(evidence)+'</p><div class="proposal-meta"><span>'+Math.round(Number(proposal.confidence||0)*100)+'% confidence</span><span>'+esc(targets.join(', '))+'</span></div><p><strong>Result:</strong> '+esc(result)+'</p><div class="decision">'+['accepted','edited','rejected'].map(value=>'<button type="button" data-value="'+value+'" aria-pressed="false">'+value+'</button>').join('')+'</div><textarea class="edit-note" rows="2" placeholder="Describe the corrected semantics"></textarea>';const focus=()=>focusBinding(targets,targets[0]);card.addEventListener('click',focus);card.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();focus()}});card.querySelectorAll('.decision button').forEach(button=>button.addEventListener('click',()=>{card.dataset.decision=button.dataset.value;for(const option of card.querySelectorAll('.decision button'))option.setAttribute('aria-pressed',String(option===button));card.classList.toggle('is-editing',button.dataset.value==='edited');record('proposal_decision',{selector:'[data-proposal-id="'+id+'"]',label:proposal.title||id},{proposal_id:id,status:button.dataset.value});updateProgress()}));card.querySelector('textarea').addEventListener('change',event=>record('change',{selector:'[data-proposal-id="'+id+'"] textarea',label:(proposal.title||id)+' edit'},event.target.value));list.append(card)}
    function decisions(){return [...document.querySelectorAll('.proposal')].map(card=>({proposal_id:card.dataset.proposalId,status:card.dataset.decision||'pending',edited_semantics:card.querySelector('textarea')?.value.trim()||'',target_object_ids:JSON.parse(card.dataset.targets||'[]')}))}
    function submit(action){parent.postMessage({type:'html_widget_return',widgetId,values:{decisions:decisions(),action}},'*')}
    form.addEventListener('submit',event=>{event.preventDefault();if(!readOnly&&!continueButton.disabled)submit('continue')});document.getElementById('regenerate').onclick=()=>{if(!readOnly)submit('regenerate')};document.getElementById('dismiss').onclick=()=>{if(!readOnly)parent.postMessage({type:'html_widget_dismiss',widgetId,note:''},'*')};for(const interaction of history){if(interaction.type==='proposal_decision'){const card=document.querySelector('[data-proposal-id="'+CSS.escape(interaction.value?.proposal_id||'')+'"]');card?.querySelector('[data-value="'+CSS.escape(interaction.value?.status||'')+'"]')?.click()}else if(interaction.type==='change'){const target=document.querySelector(interaction.target?.selector||'');if(target)target.value=interaction.value||''}}updateProgress();
    addEventListener('message',event=>{const message=event.data||{};if(message.type==='artifact_widget_pointer'&&(!message.widgetId||message.widgetId===widgetId)){if(Date.now()-lastTrustedWidgetClick<100)return;const target=document.elementFromPoint(Number(message.x),Number(message.y));if(target&&typeof target.focus==='function')target.focus({preventScroll:true});if(target&&typeof target.click==='function')target.click();return}if(message.type==='artifact_widget_wheel'&&(!message.widgetId||message.widgetId===widgetId)){scrollBy(Number(message.deltaX)||0,Number(message.deltaY)||0);return}if(message.type!=='artifact_canvas_selection')return;const selected=new Set(message.selectedObjectIds||[]);for(const card of document.querySelectorAll('.proposal')){const targets=JSON.parse(card.dataset.targets||'[]');card.classList.toggle('is-related',targets.some(id=>selected.has(id)))}});
    addEventListener('load',()=>parent.postMessage({type:'html_widget_resize',widgetId,height:document.documentElement.scrollHeight},'*'));
  </script></body></html>`;
}

function formatWidgetDetails(widget) {
  const details = {
    widget_id: widget.widget_id,
    widget_type: widget.widget_type,
    planner_id: widget.planner_id,
    interaction_goal: widget.interaction_goal,
    display: widget.display || {},
    controls: widget.controls || [],
    expected_return: widget.expected_return || {},
  };
  return JSON.stringify(details, null, 2);
}

function parseWidgetValues(text) {
  const trimmed = text.trim();
  if (!trimmed) return {};
  try {
    return JSON.parse(trimmed);
  } catch {
    return { note: trimmed };
  }
}

function closeModal() {
  state.pendingModal = null;
  elements.modalApprove.disabled = false;
  elements.modalApprove.classList.remove("danger");
  elements.modal.classList.remove("delete-session-modal");
  elements.modalDetails.replaceChildren();
  elements.modalBackdrop.classList.add("hidden");
}

window.addEventListener("message", async (event) => {
  const data = event.data || {};
  if (data.type === "html_widget_resize") {
    resizeHtmlWidgetFrames(data.widgetId, data.height);
    return;
  }
  const session = currentSession();
  const matchingWidgetMessages = (session?.messages || []).filter((message) =>
    message.role === "widget" && (message.widgetId || message.widget?.widget_id) === data.widgetId);
  const widgetMessage = matchingWidgetMessages.findLast((message) => message.status === "pending")
    || matchingWidgetMessages.at(-1);
  const modal = state.pendingModal;
  const modalWidget = modal?.event?.widget || {};
  const isModalWidget = modal?.kind === "widget" && data.widgetId === (modal.event.widgetId || modalWidget.widget_id);
  if (!widgetMessage && !isModalWidget) return;
  const widget = widgetMessage?.widget || modalWidget;

  if (data.type === "html_widget_artifact_binding") {
    if (widgetMessage?.status !== "pending" && !isModalWidget) return;
    const objectIds = Array.isArray(data.objectIds) ? data.objectIds.map(String) : [];
    const primaryObjectId = String(data.primaryObjectId || objectIds[0] || "");
    if (!focusArtifactCanvasBinding(data.widgetId, objectIds, primaryObjectId)) return;
    if (widgetMessage?.status === "pending") {
      recordWidgetInteraction(widgetMessage, {
        type: "instruction_focus",
        target: { selector: "", id: primaryObjectId, name: "artifact-binding", label: primaryObjectId },
        value: { selected_object_ids: objectIds, active_object_id: primaryObjectId },
        timestamp: new Date().toISOString(),
      });
    }
    return;
  }

  if (data.type === "html_widget_upload") {
    if (widgetMessage?.status !== "pending" && !isModalWidget) return;
    handleWidgetUpload(data, event.source);
    return;
  }

  if (data.type === "html_widget_interaction") {
    if (widgetMessage?.status === "pending" && data.interaction && typeof data.interaction === "object") {
      recordWidgetInteraction(widgetMessage, data.interaction);
    }
    return;
  }

  if (data.type === "html_widget_layout_command") {
    const widgetType = widget.semantic_widget_type || widget.widget_type;
    const isHistoricalLayoutReset = widgetMessage?.isStored
      && widgetType === "svg_collage_layout_board"
      && data.action === "reset";
    if (widgetMessage?.status !== "pending" && !isModalWidget && !isHistoricalLayoutReset) return;
    commandArtifactCanvasLayoutDraft(data.action, data.widgetId);
    return;
  }

  if (data.type === "html_widget_layout_preview") {
    const widgetType = widget.semantic_widget_type || widget.widget_type;
    if (!widgetMessage?.isStored || widgetType !== "svg_collage_layout_board") return;
    previewArtifactCanvasLayoutDraft(data.itemTransforms, data.widgetId, data.activeObjectId);
    return;
  }

  if (data.type === "html_widget_return") {
    if (widgetMessage && widgetMessage.status !== "pending") return;
    let values = mergeArtifactCanvasLayoutDraft(data.values || {}, data.widgetId);
    if (widget.surface === "artifact_canvas_widget" && Array.isArray(values.operations) && values.operations.length > 0) {
      try {
        const attachment = await applyArtifactCanvasWidgetValues(values, data.widgetId);
        if (!attachment?.fileId || !attachment?.scene || !attachment?.revision) {
          throw new Error("Patch response did not include a canonical artifact scene.");
        }
        values = {
          ...values,
          artifact_id: attachment.fileId,
          applied_revision: attachment.revision,
          patch_result: {
            action: "svg_document_patched",
            attachment,
            scene: attachment.scene,
            revision: attachment.revision,
          },
        };
      } catch (error) {
        showToast(`Canvas widget could not apply: ${error.message}`);
        return;
      }
    }
    const sent = sendSocket({
      type: "widget_return",
      widgetId: data.widgetId,
      plannerId: widget.planner_id,
      action: "accept",
      values,
      controlState: data.controlState || [],
      freeformNote: "",
      timestamp: new Date().toISOString(),
    });
    if (!sent) return;
    resolveArtifactCanvasWidget(data.widgetId, String(values.action || "accept"));
    if (widgetMessage) {
      widgetMessage.status = "submitted";
      widgetMessage.returnValues = values;
      widgetMessage.controlState = data.controlState || [];
      widgetMessage.freeformNote = "";
      renderMessages();
    }
    if (isModalWidget) closeModal();
  }
  if (data.type === "html_widget_dismiss") {
    if (widgetMessage && widgetMessage.status !== "pending") return;
    const sent = sendSocket({
      type: "widget_dismiss",
      widgetId: data.widgetId,
      plannerId: widget.planner_id,
      action: "dismiss",
      values: {},
      freeformNote: data.note || "",
      timestamp: new Date().toISOString(),
    });
    if (!sent) return;
    resolveArtifactCanvasWidget(data.widgetId, "dismiss");
    if (widgetMessage) {
      widgetMessage.status = "dismissed";
      widgetMessage.returnValues = {};
      widgetMessage.freeformNote = data.note || "";
      renderMessages();
    }
    if (isModalWidget) closeModal();
  }
});

function sendSocket(payload) {
  if (!state.socket || state.socket.readyState !== WebSocket.OPEN) {
    showToast("WebSocket is not connected yet.");
    return false;
  }
  state.socket.send(JSON.stringify(payload));
  return true;
}

async function handleWidgetUpload(data, source) {
  const reply = (msg) => source?.postMessage({ type: "host_upload_result", uploadId: data.uploadId, ...msg }, "*");
  const session = currentSession();
  if (!session) return reply({ error: "No active session" });
  try {
    const bytes = Uint8Array.from(atob(data.dataBase64 || ""), (c) => c.charCodeAt(0));
    const extension = String(data.name || "").split(".").pop().toLowerCase();
    const inferredMime = {
      py: "text/x-python",
      md: "text/markdown",
      txt: "text/plain",
      json: "application/json",
      yaml: "application/yaml",
      yml: "application/yaml",
    }[extension];
    const blob = new Blob([bytes], { type: data.mime || inferredMime || "application/octet-stream" });
    const form = new FormData();
    form.append("files", blob, data.name || "upload.bin");
    const response = await fetch(`/api/sessions/${encodeURIComponent(session.id)}/uploads`, { method: "POST", body: form });
    if (!response.ok) throw new Error(await response.text());
    const result = await response.json();
    reply({ attachment: (result.attachments || [])[0] || null });
  } catch (error) {
    reply({ error: error.message || "upload failed" });
  }
}

async function handleSubmit(event) {
  event.preventDefault();
  const content = elements.input.value.trim();
  const pluginId = normalizePluginId(elements.pluginSelect?.value || currentSession()?.defaultPluginId || "inflak-main");
  const requiresPromptAndSvg = pluginId === P11_PLUGIN_ID || pluginId === P12_PLUGIN_ID;
  const canvasSvgPlugin = requiresPromptAndSvg || pluginId === COLLAGE_AUTHORING_PLUGIN_ID;
  const currentCanvasSvg = canvasSvgPlugin ? currentArtifactCanvasSvg() : null;
  if (requiresPromptAndSvg && (!content || !currentCanvasSvg)) {
    showToast(pluginId === P11_PLUGIN_ID
      ? "P11 requires a prompt and an SVG artifact on the Canvas."
      : "P12 requires a prompt and an SVG artifact on the Canvas.");
    return;
  }
  if ((!content && state.attachments.length === 0 && state.canvasPendingArtifacts.length === 0) || state.isBusy) return;

  if (!currentSession()) {
    try {
      await createSession();
    } catch (error) {
      showToast(`Failed to create session: ${error.message}`);
      return;
    }
  }

  const session = currentSession();
  if (!session.isLive) {
    try {
      await recoverInterruptedWidget(session);
      await resumeSession(session);
    } catch (error) {
      showToast(`Failed to resume session: ${error.message}`);
      return;
    }
  }

  let attachments = [...state.canvasPendingArtifacts];
  if (state.attachments.length > 0) {
    try {
      attachments.push(...await uploadPendingAttachments(session.id));
    } catch (error) {
      showToast(`Upload failed: ${error.message}`);
      return;
    }
  }
  if (currentCanvasSvg) {
    attachments = attachments.filter((attachment) => attachment.fileId !== currentCanvasSvg.fileId
      && attachment.artifactType !== 'svg-collage'
      && attachment.artifactType !== 'svg-figure'
      && attachment.mime !== 'image/svg+xml'
      && !String(attachment.name || '').toLowerCase().endsWith('.svg'));
    attachments.push(currentCanvasSvg);
  }
  attachments = [...new Map(attachments.map((attachment) => [attachment.fileId, attachment])).values()];

  if (session.title === "New chat" && content) {
    session.title = makeSessionTitle(content);
    session.preview = makeSessionPreview(content);
    renderSessions();
  }
  appendMessage("user", content, attachments);
  elements.input.value = "";
  state.attachments = [];
  state.canvasPendingArtifacts = [];
  renderComposerAttachments();
  autoResizeInput();
  sendSocket({ type: "message", content, attachments, pluginId });
}

async function uploadCanvasArtifacts(files) {
  if (!currentSession()) await createSession();
  const session = currentSession();
  if (!session?.isLive) await resumeSession(session);
  const form = new FormData();
  for (const file of files) form.append("files", file, file.name);
  const response = await fetch(`/api/sessions/${encodeURIComponent(session.id)}/uploads`, { method: "POST", body: form });
  if (!response.ok) throw new Error(await response.text());
  const data = await response.json();
  const artifacts = data.attachments || [];
  const pendingIds = new Set(state.canvasPendingArtifacts.map((artifact) => artifact.fileId));
  state.canvasPendingArtifacts.push(...artifacts.filter((artifact) => !pendingIds.has(artifact.fileId)));
  addArtifactCanvasArtifacts(artifacts);
  updateComposerState();
  return artifacts;
}

async function analyzeCanvasArtifact(artifact) {
  if (!artifact) return false;
  if (state.isBusy) {
    showToast("Finish or dismiss the current SVG interaction before starting analysis.");
    return false;
  }
  if (!currentSession()) await createSession();
  const session = currentSession();
  if (!session?.isLive) await resumeSession(session);
  if (session.title === "New chat") {
    session.title = `Analyze ${artifact.name || "SVG artifact"}`;
    session.preview = "Artifact-first P10 analysis";
    renderSessions();
  }
  state.isBusy = true;
  updateComposerState();
  const analysisIntent = "Analyze this SVG artifact for concrete improvements. Do not modify it yet. Generate 3-6 artifact-grounded proposals and let me formally accept, edit, or reject each proposal.";
  appendMessage("user", analysisIntent, [artifact]);
  const sent = sendSocket({ type: "message", content: analysisIntent, attachments: [artifact], pluginId: normalizePluginId(elements.pluginSelect?.value || P10_PLUGIN_ID) });
  if (!sent) {
    state.isBusy = false;
    updateComposerState();
    return false;
  }
  state.canvasPendingArtifacts = state.canvasPendingArtifacts.filter((item) => item.fileId !== artifact.fileId);
  return true;
}

async function uploadPendingAttachments(sessionId) {
  const form = new FormData();
  for (const item of state.attachments) form.append("files", item.file, item.name);
  const response = await fetch(`/api/sessions/${encodeURIComponent(sessionId)}/uploads`, {
    method: "POST",
    body: form,
  });
  if (!response.ok) throw new Error(await response.text());
  const data = await response.json();
  return data.attachments || [];
}

function currentModelId() {
  return currentSession()?.model || elements.modelSelect.value || DEFAULT_MODEL;
}

function modelSupportsVision(modelId) {
  if (!modelId || modelId === "auto") return true; // router: don't nag
  const model = (state.models || []).find((m) => (m.id || m.name) === modelId);
  if (!model) return true; // unknown model: don't block
  return model.capabilities?.supports?.vision !== false;
}

function addPendingFiles(fileList) {
  const files = [...fileList].filter(Boolean);
  let addedImage = false;
  for (const file of files) {
    if (file.size > 10 * 1024 * 1024) {
      showToast(`"${file.name}" exceeds the 10MB limit.`);
      continue;
    }
    if (String(file.type || "").startsWith("image/")) addedImage = true;
    state.attachments.push({ file, name: file.name, mime: file.type, size: file.size });
  }
  if (addedImage && !modelSupportsVision(currentModelId())) {
    showToast(`Model "${currentModelId()}" can't read images — switch to a vision model (e.g. gpt-5.5) to use image input.`);
  }
  renderComposerAttachments();
  updateComposerState();
}

function removePendingFile(index) {
  state.attachments.splice(index, 1);
  renderComposerAttachments();
}

function renderComposerAttachments() {
  const row = elements.composerAttachments;
  row.replaceChildren();
  if (state.attachments.length === 0) {
    row.classList.add("hidden");
    return;
  }
  row.classList.remove("hidden");
  state.attachments.forEach((item, index) => {
    const chip = document.createElement("span");
    chip.className = "attachment-pill";
    if (item.mime.startsWith("image/")) {
      const img = document.createElement("img");
      img.src = URL.createObjectURL(item.file);
      img.alt = item.name;
      chip.append(img);
    }
    const label = document.createElement("span");
    label.textContent = item.name;
    const remove = document.createElement("button");
    remove.type = "button";
    remove.textContent = "×";
    remove.setAttribute("aria-label", `Remove ${item.name}`);
    remove.addEventListener("click", () => removePendingFile(index));
    chip.append(label, remove);
    row.append(chip);
  });
}

function autoResizeInput() {
  elements.input.style.height = "auto";
  elements.input.style.height = `${Math.min(elements.input.scrollHeight, 180)}px`;
}

elements.composer.addEventListener("submit", handleSubmit);
elements.messages.addEventListener("dblclick", (event) => {
  const image = event.target.closest("img");
  if (image) openImagePreview(image);
});
elements.imagePreview.addEventListener("click", (event) => {
  if (event.target === elements.imagePreview) closeImagePreview();
});
elements.imagePreviewClose.addEventListener("click", closeImagePreview);
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !elements.imagePreview.classList.contains("hidden")) {
    event.preventDefault();
    closeImagePreview();
  }
});
elements.attachButton.addEventListener("click", () => elements.fileInput.click());
elements.fileInput.addEventListener("change", () => {
  if (elements.fileInput.files?.length) addPendingFiles(elements.fileInput.files);
  elements.fileInput.value = "";
});
elements.composer.addEventListener("dragover", (event) => {
  event.preventDefault();
  elements.composer.classList.add("dragover");
});
elements.composer.addEventListener("dragleave", () => elements.composer.classList.remove("dragover"));
elements.composer.addEventListener("drop", (event) => {
  event.preventDefault();
  elements.composer.classList.remove("dragover");
  if (event.dataTransfer?.files?.length) addPendingFiles(event.dataTransfer.files);
});
elements.input.addEventListener("paste", (event) => {
  const files = [...(event.clipboardData?.files || [])];
  if (files.length) {
    event.preventDefault();
    addPendingFiles(files);
  }
});
elements.skillTraceClear?.addEventListener("click", clearSkillTrace);
elements.sessionSearch?.addEventListener("input", () => {
  state.sessionQuery = elements.sessionSearch.value;
  renderSessions();
});
elements.sessionSearch?.addEventListener("keydown", (event) => {
  if (event.key !== "Escape" || !state.sessionQuery) return;
  event.preventDefault();
  clearSessionSearch({ focus: true });
});
elements.sessionSearchClear?.addEventListener("click", () => clearSessionSearch({ focus: true }));
elements.newChat.addEventListener("click", async () => {
  try {
    await createSession();
    closeSessionMenu();
  } catch (error) {
    showToast(`Failed to create session: ${error.message}`);
  }
});

elements.pluginSelect?.addEventListener("change", async () => {
  const selectedPluginId = elements.pluginSelect.value;
  renderPrimarySurface();
  if (selectedPluginId !== currentSession()?.defaultPluginId) {
    try {
      await createSession();
    } catch (error) {
      showToast(`Failed to create session: ${error.message}`);
    }
  }
});

elements.sessionMenuButton?.addEventListener("click", toggleSessionMenu);
elements.input.addEventListener("input", autoResizeInput);
elements.input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    elements.composer.requestSubmit();
  }
});
elements.modalApprove.addEventListener("click", async () => {
  const modal = state.pendingModal;
  if (!modal) return;
  if (modal.kind === "delete_session") {
    await deleteStoredSession(modal.sessionId);
    return;
  } else if (modal.kind === "permission") {
    sendSocket({ type: "permission_response", requestId: modal.event.requestId, approved: true });
  } else if (modal.kind === "widget") {
    const widget = modal.event.widget || {};
    sendSocket({
      type: "widget_return",
      widgetId: modal.event.widgetId || widget.widget_id,
      plannerId: widget.planner_id,
      action: "accept",
      values: parseWidgetValues(elements.userInputAnswer.value),
      freeformNote: elements.userInputAnswer.value,
      timestamp: new Date().toISOString(),
    });
  } else {
    sendSocket({ type: "user_input_response", requestId: modal.event.requestId, answer: elements.userInputAnswer.value });
  }
  closeModal();
});
elements.modalReject.addEventListener("click", () => {
  const modal = state.pendingModal;
  if (!modal) return;
  if (modal.kind === "delete_session") {
    closeModal();
    return;
  } else if (modal.kind === "permission") {
    sendSocket({ type: "permission_response", requestId: modal.event.requestId, approved: false });
  } else if (modal.kind === "widget") {
    const widget = modal.event.widget || {};
    sendSocket({
      type: "widget_dismiss",
      widgetId: modal.event.widgetId || widget.widget_id,
      plannerId: widget.planner_id,
      action: "dismiss",
      values: {},
      freeformNote: elements.userInputAnswer.value,
      timestamp: new Date().toISOString(),
    });
  } else {
    sendSocket({ type: "user_input_response", requestId: modal.event.requestId, answer: "" });
  }
  closeModal();
});

setStatus("Loading models");
window.lucide?.createIcons();
await loadPlugins();
await loadModels();
await loadStoredSessions();
try {
  await openRequestedSession();
} catch (error) {
  showToast(`Failed to open scenario session: ${error.message}`);
}
setStatus("Ready", "ready");
renderMessages();
renderSkillTrace();
