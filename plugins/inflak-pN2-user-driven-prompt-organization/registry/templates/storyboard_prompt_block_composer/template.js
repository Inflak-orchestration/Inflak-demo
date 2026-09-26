(function () {
  const root = document.getElementById("composer-root");
  const parseData = (name, fallback) => {
    try { return JSON.parse(root.dataset[name] || "") ?? fallback; } catch { return fallback; }
  };
  const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;"
  })[character]);
  const makeId = (prefix) => `${prefix}-${crypto.randomUUID()}`;
  const sourceFromDisplay = parseData("sourceText", "");
  const seed = parseData("promptStructure", null);
  const defaultGroups = () => [
    { id: makeId("group"), label: "Subject and setting", order: 1, scope: "global" },
    { id: makeId("group"), label: "Action and detail", order: 2, scope: "local" },
    { id: makeId("group"), label: "Composition and camera", order: 3, scope: "global" },
    { id: makeId("group"), label: "Light, color, and style", order: 4, scope: "global" },
    { id: makeId("group"), label: "Unsorted", order: 5, scope: "local" }
  ];

  function segmentSource(source, groups) {
    let unsortedGroup = groups.find((group) => group.label.trim().toLowerCase() === "unsorted");
    if (!unsortedGroup) {
      unsortedGroup = { id: makeId("group"), label: "Unsorted", order: groups.length + 1, scope: "local" };
      groups.push(unsortedGroup);
    }
    const units = [];
    const matcher = /[^,;.!?]+[,;.!?]?/g;
    let match;
    while ((match = matcher.exec(source)) !== null) {
      const leading = match[0].search(/\S/);
      if (leading < 0) continue;
      const trailingText = match[0].trimEnd();
      const start = match.index + leading;
      const end = match.index + trailingText.length;
      const rawText = source.slice(start, end).trim();
      if (!rawText) continue;
      units.push({
        id: makeId("unit"), raw_text: rawText, source_span: { start, end },
        group_id: unsortedGroup.id, order: 1,
        active: true, locked: false, user_owned: true, provenance: "source_text"
      });
    }
    return units;
  }

  const initialGroups = seed?.groups?.length ? seed.groups : defaultGroups();
  const state = seed && Array.isArray(seed.units) ? seed : {
    schema_version: "pN2-prompt-structure-v2",
    source_text: sourceFromDisplay,
    mode: "single_image",
    groups: initialGroups,
    units: segmentSource(sourceFromDisplay, initialGroups),
    submission_status: "draft"
  };
  state.source_text ??= sourceFromDisplay;
  state.mode ||= "single_image";
  state.groups = Array.isArray(state.groups) && state.groups.length ? state.groups : defaultGroups();
  state.units = Array.isArray(state.units) ? state.units : [];
  let focusedUnitId = null;
  let sourceDirty = false;
  const collapsedGroupIds = new Set();
  let draggedUnitId = null;

  const sourceInput = document.getElementById("source-input");
  const groupsRoot = document.getElementById("groups");
  const localErrors = document.getElementById("local-errors");
  const confirm = document.getElementById("confirm");
  const orderedGroups = () => [...state.groups].sort((first, second) => first.order - second.order);
  const unitsFor = (groupId) => state.units.filter((unit) => unit.group_id === groupId).sort((first, second) => first.order - second.order);

  function normalizeOrder() {
    orderedGroups().forEach((group, groupIndex) => {
      group.order = groupIndex + 1;
      unitsFor(group.id).forEach((unit, unitIndex) => { unit.order = unitIndex + 1; });
    });
  }

  function renderMode() {
    document.querySelectorAll("[data-mode]").forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.mode === state.mode));
      button.onclick = () => { state.mode = button.dataset.mode; renderMode(); renderPreview(); };
    });
    document.getElementById("mode-help").textContent = state.mode === "single_image"
      ? "Groups become sections in one image instruction."
      : "Local groups may represent ordered scenes; global groups apply across them.";
    confirm.textContent = "Review instruction";
  }

  function renderSource() {
    sourceInput.value = state.source_text;
    document.getElementById("source-note").textContent = sourceDirty
      ? "Source changed. Rebuild units to restore exact source links."
      : "Select a unit to see its exact source span.";
    const unit = state.units.find((candidate) => candidate.id === focusedUnitId);
    const target = document.getElementById("source-highlight");
    if (!unit?.source_span) {
      target.innerHTML = escapeHtml(state.source_text || "No source content yet.");
      return;
    }
    const { start, end } = unit.source_span;
    target.innerHTML = `${escapeHtml(state.source_text.slice(0, start))}<mark>${escapeHtml(state.source_text.slice(start, end))}</mark>${escapeHtml(state.source_text.slice(end))}`;
  }

  function provenanceLabel(unit) {
    if (unit.provenance === "user_edited") return ["Edited", "edited"];
    if (unit.provenance === "user_added") return ["Added", "added"];
    return ["From source", "source"];
  }

  function unitMarkup(unit, groupId) {
    const [provenance, badgeClass] = provenanceLabel(unit);
    const groupOptions = orderedGroups().map((group) => `<option value="${group.id}"${group.id === groupId ? " selected" : ""}>${escapeHtml(group.label)}</option>`).join("");
    const sourceData = unit.source_span ? ` data-source-start="${unit.source_span.start}" data-source-end="${unit.source_span.end}"` : "";
    return `<article class="unit-card${unit.active ? "" : " inactive"}${unit.locked ? " locked" : ""}" data-unit="${unit.id}" role="treeitem" draggable="true" tabindex="0" aria-label="Drag to reorder ${escapeHtml(unit.raw_text)}" title="Drag to reorder unit"${sourceData}>
      <div class="unit-meta">
        <span class="badge ${badgeClass}">${provenance}</span>
        <label><input type="checkbox" data-field="active"${unit.active ? " checked" : ""}>Active</label>
        <label><input type="checkbox" data-field="locked"${unit.locked ? " checked" : ""}>Locked</label>
        <select class="unit-group" data-field="group_id" aria-label="Move unit to group">${groupOptions}</select>
      </div>
      <textarea class="unit-text" data-field="raw_text"${unit.locked ? " disabled" : ""}>${escapeHtml(unit.raw_text)}</textarea>
      <div class="unit-actions">
        <button class="icon-button danger" type="button" data-action="remove" title="Remove unit" aria-label="Remove unit"${unit.locked ? " disabled" : ""}>×</button>
      </div>
    </article>`;
  }

  function renderGroups() {
    groupsRoot.innerHTML = orderedGroups().map((group) => {
      const units = unitsFor(group.id);
      const collapsed = collapsedGroupIds.has(group.id);
      const unitListId = `unit-list-${group.id}`;
      return `<section class="group-card" data-group="${group.id}" data-collapsed="${collapsed}" role="treeitem" aria-expanded="${!collapsed}">
        <div class="group-head">
          <button class="icon-button tree-toggle" type="button" data-tree-toggle aria-expanded="${!collapsed}" aria-controls="${unitListId}" title="${collapsed ? "Expand group" : "Collapse group"}" aria-label="${collapsed ? "Expand group" : "Collapse group"}">${collapsed ? "▸" : "▾"}</button>
          <input class="group-name" value="${escapeHtml(group.label)}" aria-label="Group name">
          <select class="group-scope" aria-label="Group scope">
            <option value="global"${group.scope === "global" ? " selected" : ""}>Global</option>
            <option value="local"${group.scope === "local" ? " selected" : ""}>Local</option>
          </select>
          <div class="group-tools">
            <button class="icon-button add-unit" type="button" data-group-action="add" title="Add unit">+ unit</button>
            <button class="icon-button danger" type="button" data-group-action="remove" title="Remove empty group" aria-label="Remove empty group"${units.length ? " disabled" : ""}>×</button>
          </div>
        </div>
        <div class="unit-list" id="${unitListId}" role="group"${collapsed ? " hidden" : ""}>${units.length ? units.map((unit) => unitMarkup(unit, group.id)).join("") : '<p class="empty-group">No units in this group.</p>'}</div>
      </section>`;
    }).join("");

    groupsRoot.querySelectorAll("[data-group]").forEach((groupElement) => {
      const group = state.groups.find((candidate) => candidate.id === groupElement.dataset.group);
      const unitList = groupElement.querySelector(".unit-list");
      unitList.ondragover = (event) => {
        if (!draggedUnitId || event.target.closest("[data-unit]")) return;
        event.preventDefault();
        clearUnitDropTargets();
        unitList.classList.add("drop-into");
      };
      unitList.ondrop = (event) => {
        if (!draggedUnitId || event.target.closest("[data-unit]")) return;
        event.preventDefault();
        reorderUnit(draggedUnitId, group.id, null, true);
      };
      groupElement.querySelector("[data-tree-toggle]").onclick = () => {
        if (collapsedGroupIds.has(group.id)) collapsedGroupIds.delete(group.id);
        else collapsedGroupIds.add(group.id);
        renderGroups();
      };
      groupElement.querySelector(".group-name").onchange = (event) => { group.label = event.target.value.trim() || "Untitled group"; render(); };
      groupElement.querySelector(".group-scope").onchange = (event) => { group.scope = event.target.value; renderPreview(); };
      groupElement.querySelectorAll("[data-group-action]").forEach((button) => {
        button.onclick = () => groupAction(group.id, button.dataset.groupAction);
      });
    });

    groupsRoot.querySelectorAll("[data-unit]").forEach((unitElement) => {
      const unit = state.units.find((candidate) => candidate.id === unitElement.dataset.unit);
      unitElement.ondragstart = (event) => {
        if (event.target.closest("button, input, select, textarea")) { event.preventDefault(); return; }
        draggedUnitId = unit.id;
        unitElement.classList.add("dragging");
        event.dataTransfer.effectAllowed = "move";
        event.dataTransfer.setData("text/plain", unit.id);
      };
      unitElement.ondragover = (event) => {
        if (!draggedUnitId || draggedUnitId === unit.id) return;
        event.preventDefault();
        event.stopPropagation();
        const after = event.clientY > unitElement.getBoundingClientRect().top + unitElement.offsetHeight / 2;
        clearUnitDropTargets();
        unitElement.classList.add(after ? "drop-after" : "drop-before");
      };
      unitElement.ondrop = (event) => {
        if (!draggedUnitId || draggedUnitId === unit.id) return;
        event.preventDefault();
        event.stopPropagation();
        reorderUnit(draggedUnitId, unit.group_id, unit.id, unitElement.classList.contains("drop-after"));
      };
      unitElement.ondragend = clearUnitDrag;
      unitElement.onkeydown = (event) => {
        if (!event.altKey || !["ArrowUp", "ArrowDown"].includes(event.key)) return;
        event.preventDefault();
        const units = unitsFor(unit.group_id);
        const index = units.findIndex((candidate) => candidate.id === unit.id);
        const target = units[index + (event.key === "ArrowUp" ? -1 : 1)];
        if (target) reorderUnit(unit.id, unit.group_id, target.id, event.key === "ArrowDown");
      };
      unitElement.querySelector('[data-field="active"]').onchange = (event) => { unit.active = event.target.checked; render(); };
      unitElement.querySelector('[data-field="locked"]').onchange = (event) => { unit.locked = event.target.checked; render(); };
      unitElement.querySelector('[data-field="group_id"]').onchange = (event) => { unit.group_id = event.target.value; normalizeOrder(); render(); };
      const unitText = unitElement.querySelector('[data-field="raw_text"]');
      unitText.onchange = (event) => {
        unit.raw_text = event.target.value.trim();
        if (unit.provenance === "source_text") unit.provenance = "user_edited";
        render();
      };
      unitElement.querySelectorAll("[data-action]").forEach((button) => { button.onclick = () => unitAction(unit.id, button.dataset.action); });
    });
  }

  function clearUnitDropTargets() {
    groupsRoot.querySelectorAll(".drop-before, .drop-after, .drop-into").forEach((element) => element.classList.remove("drop-before", "drop-after", "drop-into"));
  }

  function clearUnitDrag() {
    draggedUnitId = null;
    groupsRoot.querySelectorAll(".dragging").forEach((element) => element.classList.remove("dragging"));
    clearUnitDropTargets();
  }

  function reorderUnit(sourceId, targetGroupId, targetId, after) {
    const source = state.units.find((unit) => unit.id === sourceId);
    if (!source) { clearUnitDrag(); return; }
    const sourceGroupId = source.group_id;
    const targetUnits = unitsFor(targetGroupId).filter((unit) => unit.id !== sourceId);
    const targetIndex = targetId ? targetUnits.findIndex((unit) => unit.id === targetId) : targetUnits.length;
    source.group_id = targetGroupId;
    targetUnits.splice(Math.max(0, targetIndex) + (targetId && after ? 1 : 0), 0, source);
    targetUnits.forEach((unit, index) => { unit.order = index + 1; });
    if (sourceGroupId !== targetGroupId) unitsFor(sourceGroupId).forEach((unit, index) => { unit.order = index + 1; });
    clearUnitDrag();
    render();
  }

  function groupAction(groupId, action) {
    if (action === "add") state.units.push({ id: makeId("unit"), raw_text: "", source_span: null, group_id: groupId, order: unitsFor(groupId).length + 1, active: true, locked: false, user_owned: true, provenance: "user_added" });
    if (action === "remove" && !unitsFor(groupId).length && state.groups.length > 1) state.groups = state.groups.filter((group) => group.id !== groupId);
    normalizeOrder(); render();
  }

  function unitAction(unitId, action) {
    const unit = state.units.find((candidate) => candidate.id === unitId);
    if (action === "remove" && !unit.locked) state.units = state.units.filter((candidate) => candidate.id !== unitId);
    normalizeOrder(); render();
  }

  function renderPreview() {
    const content = orderedGroups().map((group) => {
      const text = unitsFor(group.id).filter((unit) => unit.active && unit.raw_text.trim()).map((unit) => unit.raw_text.trim()).join(" ");
      return text ? `<div class="preview-group"><strong>${escapeHtml(group.label)}</strong><p>${escapeHtml(text)}</p></div>` : "";
    }).join("");
    document.getElementById("preview-content").innerHTML = content || '<p class="empty-group">Add or activate at least one unit.</p>';
  }

  function validate() {
    const errors = [];
    const groupIds = new Set(state.groups.map((group) => group.id));
    if (sourceDirty) errors.push("Rebuild units after changing the source input.");
    if (!state.units.some((unit) => unit.active && unit.raw_text.trim())) errors.push("Add or activate at least one non-empty unit.");
    state.units.forEach((unit) => {
      if (!groupIds.has(unit.group_id)) errors.push("Every unit must belong to an existing group.");
      if (unit.source_span && (unit.source_span.start < 0 || unit.source_span.end > state.source_text.length || unit.source_span.start >= unit.source_span.end)) errors.push("A source link is outside the source text.");
    });
    return [...new Set(errors)];
  }

  function updateValidation() {
    const errors = validate();
    localErrors.textContent = errors.join(" ");
    confirm.disabled = errors.length > 0;
    document.getElementById("completion-status").textContent = errors.length ? `${errors.length} item${errors.length === 1 ? "" : "s"} to resolve` : "Ready to review";
  }

  function render() { normalizeOrder(); renderMode(); renderSource(); renderGroups(); renderPreview(); updateValidation(); }
  function submit(status) { normalizeOrder(); state.schema_version = "pN2-prompt-structure-v2"; state.submission_status = status; window.submitWidget(state); }

  sourceInput.oninput = () => { state.source_text = sourceInput.value; sourceDirty = true; renderSource(); updateValidation(); };
  const focusLinkedSource = (event) => {
    const unitElement = event.target.closest?.("[data-unit]");
    if (!unitElement) return;
    focusedUnitId = unitElement.dataset.unit;
    renderSource();
  };
  groupsRoot.addEventListener("focusin", focusLinkedSource);
  groupsRoot.addEventListener("pointerdown", focusLinkedSource);
  document.getElementById("resegment").onclick = () => {
    state.units = segmentSource(state.source_text, state.groups);
    sourceDirty = false;
    focusedUnitId = state.units[0]?.id || null;
    render();
  };
  document.getElementById("add-group").onclick = () => {
    state.groups.push({ id: makeId("group"), label: state.mode === "multi_scene" ? `Scene ${state.groups.length + 1}` : "New group", order: state.groups.length + 1, scope: "local" });
    render();
  };
  document.getElementById("save-draft").onclick = () => submit("draft");
  confirm.onclick = () => { if (!validate().length) submit("confirmed"); };
  document.getElementById("dismiss").onclick = () => window.dismissWidget("Prompt organization cancelled.");
  document.getElementById("server-errors").textContent = parseData("errors", []).map((error) => typeof error === "string" ? error : error.message).filter(Boolean).join(" ");
  render();
})();