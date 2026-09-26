(function () {
  const form = document.querySelector('.ire');
  if (!form) return;
  const stage = form.querySelector('.ire-stage');
  const image = form.querySelector('.ire-image');
  const mask = form.querySelector('.ire-mask');
  const boxLayer = form.querySelector('.ire-box-layer');
  const loading = form.querySelector('.ire-loading');
  const help = form.querySelector('[data-ire-help]');
  const prompt = form.querySelector('[data-ire-prompt]');
  const note = form.querySelector('[data-ire-note]');
  const error = form.querySelector('[data-ire-error]');
  const brushSize = form.querySelector('[data-ire-brush-size]');
  const brushControls = form.querySelector('.ire-brush-controls');
  const eraser = form.querySelector('[data-ire-eraser]');
  const undo = form.querySelector('[data-ire-undo]');
  const imageRef = window.widgetDisplay && typeof window.widgetDisplay.image_ref === 'object'
    ? window.widgetDisplay.image_ref
    : {};
  const fileId = typeof imageRef.fileId === 'string' ? imageRef.fileId : '';
  const modes = Array.from(form.querySelectorAll('[data-ire-mode]'));
  let mode = 'box';
  let naturalWidth = 0;
  let naturalHeight = 0;
  let boxes = [];
  let dragStart = null;
  let movingBox = null;
  let activePointerId = null;
  let draftBox = null;
  let brushActive = false;
  let lastPoint = null;
  let eraseMode = false;
  let brushActions = [];

  function showError(message) { error.textContent = message; error.hidden = !message; }
  function normalized(value) { return Math.max(0, Math.min(1, value)); }
  function noteValue() { return note ? note.value.trim() : ''; }
  function activeCanvasContext() { return mask.getContext('2d'); }
  function readEditState() {
    const serialized = form.dataset.ireEditState;
    if (!serialized) return {};
    try {
      const state = JSON.parse(serialized);
      return state && typeof state === 'object' ? state : {};
    } catch (_) {
      return {};
    }
  }
  function validPoint(point) {
    return point && Number.isFinite(point.x) && Number.isFinite(point.y);
  }
  function restoreEditState() {
    const state = readEditState();
    const restoredBoxes = Array.isArray(state.boxes) ? state.boxes : [];
    const restoredActions = Array.isArray(state.brush_actions) ? state.brush_actions : [];
    boxes = restoredBoxes.filter((box) => box && Number.isFinite(box.x) && Number.isFinite(box.y)
      && Number.isFinite(box.width) && Number.isFinite(box.height));
    brushActions = restoredActions.filter((action) => action && (action.kind === 'paint' || action.kind === 'erase')
      && Number.isFinite(action.size) && Array.isArray(action.points) && action.points.every(validPoint));
    if (typeof state.edit_prompt === 'string') prompt.value = state.edit_prompt;
    if (note && typeof state.freeform_note === 'string') note.value = state.freeform_note;
    if (Number.isFinite(state.brush_size)) brushSize.value = String(state.brush_size);
    eraseMode = Boolean(state.erase_mode);
    eraser.classList.toggle('selected', eraseMode);
    eraser.setAttribute('aria-pressed', eraseMode ? 'true' : 'false');
    eraser.textContent = eraseMode ? 'Paint region' : 'Eraser';
    renderBoxes();
    redrawBrushPreview();
    setMode(state.mode === 'brush' ? 'brush' : 'box');
  }
  function buildEditState() {
    return {
      mode,
      boxes,
      brush_actions: brushActions,
      brush_size: Number(brushSize.value || 42),
      erase_mode: eraseMode,
      edit_prompt: prompt.value,
      freeform_note: note ? note.value : ''
    };
  }
  function canvasPoint(event) {
    const rect = image.getBoundingClientRect();
    return { x: normalized((event.clientX - rect.left) / rect.width), y: normalized((event.clientY - rect.top) / rect.height) };
  }
  function boxFromPoints(start, end) {
    return {
      x: Math.min(start.x, end.x),
      y: Math.min(start.y, end.y),
      width: Math.abs(end.x - start.x),
      height: Math.abs(end.y - start.y)
    };
  }
  function renderDraftBox(box) {
    if (!draftBox) {
      draftBox = document.createElement('div');
      draftBox.className = 'ire-box ire-box-draft';
      boxLayer.append(draftBox);
    }
    draftBox.style.left = (box.x * 100) + '%';
    draftBox.style.top = (box.y * 100) + '%';
    draftBox.style.width = (box.width * 100) + '%';
    draftBox.style.height = (box.height * 100) + '%';
  }
  function clearPointerInteraction(event) {
    dragStart = null;
    movingBox = null;
    activePointerId = null;
    draftBox?.remove();
    draftBox = null;
    boxLayer.querySelector('.is-moving')?.classList.remove('is-moving');
    if (stage.hasPointerCapture(event.pointerId)) stage.releasePointerCapture(event.pointerId);
  }
  function setMode(nextMode) {
    mode = nextMode;
    const brushEnabled = mode === 'brush';
    form.classList.toggle('is-brush', brushEnabled);
    // The browser's [hidden] rule keeps a canvas out of hit testing even when
    // CSS otherwise makes the Brush mode visible.
    mask.hidden = !brushEnabled;
    brushControls.hidden = !brushEnabled;
    modes.forEach((button) => {
      const active = button.dataset.ireMode === mode;
      button.classList.toggle('selected', active);
      button.setAttribute('aria-pressed', active ? 'true' : 'false');
    });
    help.textContent = mode === 'brush'
      ? 'Paint the exact area to regenerate. Painted strokes are the editable, transparent part of the exported mask.'
      : 'Drag on the image to add a box, or drag an existing box to move it.';
    showError('');
  }
  function renderBoxes() {
    boxLayer.replaceChildren();
    boxes.forEach((box, index) => {
      const element = document.createElement('div');
      element.className = 'ire-box';
      element.style.left = (box.x * 100) + '%';
      element.style.top = (box.y * 100) + '%';
      element.style.width = (box.width * 100) + '%';
      element.style.height = (box.height * 100) + '%';
      element.dataset.ireBox = String(index);
      element.tabIndex = 0;
      element.setAttribute('role', 'group');
      element.setAttribute('aria-label', 'Editable region ' + (index + 1) + '. Drag to move.');
      element.addEventListener('pointerdown', (event) => {
        if (event.target.closest('[data-ire-remove-box]')) return;
        if (event.button !== 0 || activePointerId !== null) return;
        event.preventDefault();
        event.stopPropagation();
        const point = canvasPoint(event);
        movingBox = { index, offsetX: point.x - box.x, offsetY: point.y - box.y };
        activePointerId = event.pointerId;
        stage.setPointerCapture(event.pointerId);
        element.classList.add('is-moving');
      });
      element.addEventListener('keydown', (event) => {
        const step = event.shiftKey ? 0.025 : 0.005;
        const delta = {
          ArrowLeft: [-step, 0], ArrowRight: [step, 0], ArrowUp: [0, -step], ArrowDown: [0, step]
        }[event.key];
        if (!delta) return;
        event.preventDefault();
        box.x = Math.max(0, Math.min(1 - box.width, box.x + delta[0]));
        box.y = Math.max(0, Math.min(1 - box.height, box.y + delta[1]));
        renderBoxes();
        boxLayer.querySelector(`[data-ire-box="${index}"]`)?.focus();
      });
      const remove = document.createElement('button');
      remove.type = 'button';
      remove.dataset.ireRemoveBox = String(index);
      remove.textContent = 'x';
      remove.setAttribute('aria-label', 'Remove selected region');
      remove.addEventListener('pointerdown', (event) => {
        event.preventDefault();
        event.stopPropagation();
        boxes.splice(index, 1);
        renderBoxes();
      });
      element.append(remove);
      boxLayer.append(element);
    });
  }
  function actionWidth(action) { return action.size * naturalWidth / Math.max(1, mask.clientWidth); }
  function drawAction(ctx, action, style) {
    const toPixels = (point) => ({ x: point.x * naturalWidth, y: point.y * naturalHeight });
    const first = toPixels(action.points[0]);
    ctx.save();
    ctx.globalCompositeOperation = style.composite;
    ctx.strokeStyle = style.color;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.lineWidth = actionWidth(action);
    if (action.points.length === 1) {
      ctx.beginPath();
      ctx.arc(first.x, first.y, ctx.lineWidth / 2, 0, Math.PI * 2);
      ctx.fillStyle = style.color;
      ctx.fill();
    } else {
      ctx.beginPath();
      ctx.moveTo(first.x, first.y);
      action.points.slice(1).forEach((point) => { const next = toPixels(point); ctx.lineTo(next.x, next.y); });
      ctx.stroke();
    }
    ctx.restore();
  }
  function redrawBrushPreview() {
    const ctx = activeCanvasContext();
    ctx.clearRect(0, 0, naturalWidth, naturalHeight);
    brushActions.forEach((action) => drawAction(ctx, action, action.kind === 'erase'
      ? { composite: 'destination-out', color: '#000000' }
      : { composite: 'source-over', color: 'rgba(23, 105, 209, 0.58)' }));
    undo.disabled = brushActions.length === 0;
  }
  function initializeBrushCanvas() {
    mask.width = naturalWidth; mask.height = naturalHeight;
    redrawBrushPreview();
  }
  function hasPaintedArea() {
    return brushActions.some((action) => action.kind === 'paint' && action.points.length > 0);
  }
  function createMaskBlob() {
    const output = document.createElement('canvas');
    output.width = naturalWidth;
    output.height = naturalHeight;
    const ctx = output.getContext('2d');
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, naturalWidth, naturalHeight);
    brushActions.forEach((action) => drawAction(ctx, action, action.kind === 'erase'
      ? { composite: 'source-over', color: '#ffffff' }
      : { composite: 'destination-out', color: '#000000' }));
    return new Promise((resolve) => output.toBlob(resolve, 'image/png'));
  }
  async function uploadMask() {
    const blob = await createMaskBlob();
    if (!blob) throw new Error('The brush mask could not be created.');
    const file = new File([blob], 'inpaint-mask.png', { type: 'image/png' });
    return window.uploadWidgetFile(file);
  }

  modes.forEach((button) => button.addEventListener('click', () => setMode(button.dataset.ireMode)));
  form.querySelector('[data-ire-clear-boxes]').addEventListener('click', () => { boxes = []; renderBoxes(); });
  form.querySelector('[data-ire-clear]').addEventListener('click', () => { brushActions = []; redrawBrushPreview(); });
  undo.addEventListener('click', () => { brushActions.pop(); redrawBrushPreview(); });
  eraser.addEventListener('click', () => {
    eraseMode = !eraseMode;
    eraser.classList.toggle('selected', eraseMode);
    eraser.setAttribute('aria-pressed', eraseMode ? 'true' : 'false');
    eraser.textContent = eraseMode ? 'Paint region' : 'Eraser';
  });
  mask.addEventListener('pointerdown', (event) => {
    if (mode !== 'brush' || !naturalWidth) return;
    event.preventDefault();
    mask.setPointerCapture(event.pointerId);
    brushActive = true;
    lastPoint = canvasPoint(event);
    brushActions.push({ kind: eraseMode ? 'erase' : 'paint', size: Number(brushSize.value || 42), points: [lastPoint] });
    redrawBrushPreview();
  });
  mask.addEventListener('pointermove', (event) => {
    if (!brushActive || mode !== 'brush') return;
    event.preventDefault();
    const point = canvasPoint(event);
    const action = brushActions[brushActions.length - 1];
    if (!action) return;
    action.points.push(point);
    lastPoint = point;
    redrawBrushPreview();
  });
  function finishBrush(event) {
    if (!brushActive) return;
    brushActive = false;
    lastPoint = null;
    if (mask.hasPointerCapture(event.pointerId)) mask.releasePointerCapture(event.pointerId);
  }
  mask.addEventListener('pointerup', finishBrush);
  mask.addEventListener('pointercancel', finishBrush);
  stage.addEventListener('pointerdown', (event) => {
    if (!naturalWidth || event.button !== 0 || activePointerId !== null) return;
    if (event.target.closest('[data-ire-remove-box]')) return;
    if (mode !== 'box') return;
    event.preventDefault();
    stage.setPointerCapture(event.pointerId);
    activePointerId = event.pointerId;
    dragStart = canvasPoint(event);
    renderDraftBox(boxFromPoints(dragStart, dragStart));
  });
  stage.addEventListener('pointermove', (event) => {
    if (event.pointerId !== activePointerId) return;
    event.preventDefault();
    if (dragStart) {
      renderDraftBox(boxFromPoints(dragStart, canvasPoint(event)));
      return;
    }
    if (!movingBox) return;
    const point = canvasPoint(event);
    const box = boxes[movingBox.index];
    if (!box) return;
    box.x = Math.max(0, Math.min(1 - box.width, point.x - movingBox.offsetX));
    box.y = Math.max(0, Math.min(1 - box.height, point.y - movingBox.offsetY));
    const element = boxLayer.querySelector(`[data-ire-box="${movingBox.index}"]`);
    if (element) {
      element.style.left = (box.x * 100) + '%';
      element.style.top = (box.y * 100) + '%';
    }
  });
  function finishPointer(event) {
    if (event.pointerId !== activePointerId) return;
    if (movingBox) {
      clearPointerInteraction(event);
      return;
    }
    if (mode === 'box' && dragStart) {
      const box = boxFromPoints(dragStart, canvasPoint(event));
      if (box.width > 0.01 && box.height > 0.01) boxes.push({ id: 'region-' + Date.now(), ...box });
      clearPointerInteraction(event);
      renderBoxes();
      return;
    }
    clearPointerInteraction(event);
  }
  stage.addEventListener('pointerup', finishPointer);
  stage.addEventListener('pointercancel', clearPointerInteraction);
  form.addEventListener('submit', async (event) => {
    event.preventDefault(); showError('');
    const editPrompt = prompt.value.trim();
    if (!editPrompt) { showError('Describe what should appear in the selected area.'); prompt.focus(); return; }
    if (!fileId || !naturalWidth) { showError('The source image is unavailable. Cancel and choose the image again.'); return; }
    let maskRef = {};
    if (mode === 'box' && !boxes.length) { showError('Draw at least one box over the image.'); return; }
    if (mode === 'brush') {
      if (!hasPaintedArea()) { showError('Paint at least one area to edit.'); return; }
      try { form.querySelector('[data-ire-submit]').disabled = true; maskRef = await uploadMask(); }
      catch (uploadError) { showError(uploadError.message || 'The mask upload failed.'); return; }
      finally { form.querySelector('[data-ire-submit]').disabled = false; }
    }
    window.submitWidget({ mode, image_ref: { fileId }, regions: mode === 'box' ? boxes : [], mask_ref: maskRef, edit_prompt: editPrompt, freeform_note: noteValue(), edit_state: buildEditState() });
  });
  form.querySelector('[data-ire-dismiss]').addEventListener('click', () => window.dismissWidget(noteValue()));
  image.addEventListener('load', () => {
    naturalWidth = image.naturalWidth; naturalHeight = image.naturalHeight;
    stage.style.setProperty('--ire-image-aspect', naturalWidth + ' / ' + naturalHeight);
    initializeBrushCanvas(); loading.hidden = true;
    restoreEditState();
  });
  image.addEventListener('error', () => { loading.textContent = 'The source image could not be loaded.'; showError('The source image could not be loaded.'); });
  if (fileId) image.src = window.widgetAssetUrl(fileId); else { loading.textContent = 'No source image was provided.'; }
  setMode('box');
})();
