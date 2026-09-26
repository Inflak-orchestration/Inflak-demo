const P10_PLUGIN_ID = 'inflak-pN10-artifact-to-multimodal-instruction';
const P11_PLUGIN_ID = 'inflak-pN11-artifact-driven-prompt-enhancement';
const P12_PLUGIN_ID = 'inflak-pN12-interactive-artifact-refinement';
const COLLAGE_AUTHORING_PLUGIN_ID = 'inflak-collage-authoring';
const GROUNDED_SVG_PLUGINS = new Set([P10_PLUGIN_ID, P11_PLUGIN_ID, P12_PLUGIN_ID, COLLAGE_AUTHORING_PLUGIN_ID]);
const CANVAS_PLUGINS = new Set(['inflak-pN8-generative-artifact-control-widgets', ...GROUNDED_SVG_PLUGINS]);
const READ_ONLY_SVG_PLUGINS = new Set([P10_PLUGIN_ID, P11_PLUGIN_ID]);

let host = null;
let callbacks = {};
let active = null;

export function isArtifactCanvasPlugin(pluginId) {
  return CANVAS_PLUGINS.has(pluginId);
}

export function initArtifactCanvas(options = {}) {
  callbacks = options;
  host = document.querySelector('#artifact-canvas');
  if (!host) return;
  host.querySelector('[data-artifact-upload]').addEventListener('click', () => host.querySelector('[data-artifact-input]').click());
  host.querySelector('[data-artifact-input]').addEventListener('change', handleFileSelection);
  host.querySelector('[data-artifact-zoom-in]').addEventListener('click', () => setZoom((active?.zoom || 1) + 0.1));
  host.querySelector('[data-artifact-zoom-out]').addEventListener('click', () => setZoom((active?.zoom || 1) - 0.1));
  host.querySelector('[data-artifact-reset]').addEventListener('click', resetView);
  host.querySelector('[data-p10-analyze]').addEventListener('click', analyzeP10Artifact);
  host.querySelector('[data-artifact-export]').addEventListener('click', exportCurrentSvg);
  window.addEventListener('resize', () => {
    if (active?.collage?.readOnly && active.collage.editingId) anchorP10WidgetToObject(active.collage.editingId);
  });
  window.addEventListener('artifact-widget-resize', (event) => {
    const popover = host?.querySelector(`[data-p10-anchored-widget] iframe[data-widget-id="${CSS.escape(String(event.detail?.widgetId || ''))}"]`)?.closest('[data-p10-anchored-widget]');
    if (!popover || !active?.p10Widget) return;
    const widget = active.p10Widget.widget;
    const objectIds = [
      active.collage?.editingId,
      ...(widget.placement?.anchor?.object_ids || []),
      ...(widget.artifact_binding?.object_ids || []),
    ].filter(Boolean);
    const object = objectIds.map(findP10Object).find(Boolean);
    const surface = host.querySelector('[data-p10-collage-surface]');
    if (object && surface) positionP10Popover(popover, object, surface, widget.placement?.anchor?.preferred_side);
  });
  const stage = host.querySelector('[data-artifact-stage]');
  stage.addEventListener('dragover', (event) => {
    event.preventDefault();
    stage.classList.add('dragover');
  });
  stage.addEventListener('dragleave', () => stage.classList.remove('dragover'));
  stage.addEventListener('drop', handleDrop);
}

export async function openArtifactCanvas({ pluginId, sessionId }) {
  if (!host || !isArtifactCanvasPlugin(pluginId)) return;
  clearSvgRevisionComparison();
  active = { pluginId, sessionId, artifacts: [], zoom: 1, verifiedWidgetBindings: new Map() };
  host.classList.remove('hidden');
  host.classList.remove('artifact-canvas-busy', 'has-live-artifact-widget');
  host.dataset.pluginId = pluginId;
  host.querySelector('[data-artifact-paradigm]').textContent = pluginId === COLLAGE_AUTHORING_PLUGIN_ID ? 'SVG' : pluginId === 'inflak-pN8-generative-artifact-control-widgets' ? 'P8' : pluginId === P10_PLUGIN_ID ? 'P10' : pluginId === P11_PLUGIN_ID ? 'P11' : 'P12';
  host.querySelector('[data-artifact-title]').textContent = pluginId === COLLAGE_AUTHORING_PLUGIN_ID ? 'Collage authoring' : pluginId === 'inflak-pN8-generative-artifact-control-widgets' ? 'Generative artifact control widgets' : pluginId === P10_PLUGIN_ID ? 'Artifact to multimodal instruction' : pluginId === P11_PLUGIN_ID ? 'Artifact-driven prompt enhancement' : 'Interactive artifact refinement';
  host.querySelector('[data-p10-analyze]').classList.toggle('hidden', pluginId !== P10_PLUGIN_ID && pluginId !== COLLAGE_AUTHORING_PLUGIN_ID);
  render();
  if (!sessionId) return;
  try {
    const response = await fetch(`/api/sessions/${encodeURIComponent(sessionId)}/uploads`);
    if (!response.ok) throw new Error(await response.text());
    const data = await response.json();
    if (active?.sessionId === sessionId && active.pluginId === pluginId) addArtifactCanvasArtifacts(data.attachments || []);
  } catch (error) {
    callbacks.onError?.(`Failed to restore artifacts: ${error.message}`);
  }
}

export function closeArtifactCanvas() {
  clearSvgRevisionComparison();
  active = null;
  host?.classList.remove('artifact-canvas-busy', 'has-live-artifact-widget');
  host?.classList.add('hidden');
}

export function addArtifactCanvasArtifacts(artifacts) {
  if (!active || !Array.isArray(artifacts)) return;
  for (const artifact of artifacts) {
    if (!artifact?.fileId) continue;
    retireStaleArtifactWidget(artifact);
    const existingIndex = active.artifacts.findIndex((item) => item.fileId === artifact.fileId);
    if (existingIndex >= 0) {
      const existing = active.artifacts[existingIndex];
      const existingRevision = Number(existing.revision || existing.scene?.revision || 0);
      const nextRevision = Number(artifact.revision || artifact.scene?.revision || 0);
      if (nextRevision > existingRevision) captureSvgRevisionComparison(existing, artifact);
      if (nextRevision >= existingRevision) active.artifacts[existingIndex] = { ...existing, ...artifact };
    } else {
      active.artifacts.push(artifact);
    }
  }
  render();
}

function captureSvgRevisionComparison(beforeArtifact, afterArtifact) {
  const afterRevision = Number(afterArtifact.revision || afterArtifact.scene?.revision || 0);
  if (active?.svgComparison?.fileId === String(afterArtifact.fileId || '')) {
    active.svgComparison.afterRevision = afterRevision;
    active.svgComparison.afterUrl = `${afterArtifact.url || artifactUrl(afterArtifact.fileId)}?revision=${encodeURIComponent(afterRevision || Date.now())}`;
    return;
  }
  if (!active?.collage || String(active.collage.artifact?.fileId || '') !== String(beforeArtifact.fileId || '')) return;
  const svg = host?.querySelector('[data-p10-collage-surface] > svg.p8-editable-svg, .p8-collage-surface > svg.p8-editable-svg');
  if (!svg) return;
  const serialized = new XMLSerializer().serializeToString(svg.cloneNode(true));
  if (!/<svg[\s>]/i.test(serialized)) return;
  clearSvgRevisionComparison();
  const beforeUrl = URL.createObjectURL(new Blob([serialized], { type: 'image/svg+xml;charset=utf-8' }));
  active.svgComparison = {
    fileId: String(afterArtifact.fileId || beforeArtifact.fileId || ''),
    beforeRevision: Number(beforeArtifact.revision || beforeArtifact.scene?.revision || active.collage.scene?.revision || 0),
    afterRevision,
    beforeUrl,
    afterUrl: `${afterArtifact.url || artifactUrl(afterArtifact.fileId)}?revision=${encodeURIComponent(afterRevision || Date.now())}`,
  };
}

function clearSvgRevisionComparison() {
  if (active?.svgComparison?.beforeUrl) URL.revokeObjectURL(active.svgComparison.beforeUrl);
  if (active) delete active.svgComparison;
}

function renderSvgRevisionComparison(board, comparison) {
  board.replaceChildren();
  board.style.transform = '';
  board.className = 'artifact-board svg-revision-comparison-board';
  const comparisonView = document.createElement('section');
  comparisonView.className = 'svg-revision-comparison';
  comparisonView.setAttribute('aria-label', 'SVG collage revision comparison');
  const pane = (label, revision, url) => {
    const figure = document.createElement('figure');
    figure.className = 'svg-comparison-pane';
    const caption = document.createElement('figcaption');
    caption.innerHTML = `<strong>${label}</strong><span>Revision ${revision || 'unknown'}</span>`;
    const image = document.createElement('img');
    image.src = url;
    image.alt = `${label} SVG collage revision ${revision || ''}`.trim();
    figure.append(caption, image);
    return figure;
  };
  comparisonView.append(
    pane('Before', comparison.beforeRevision, comparison.beforeUrl),
    pane('After', comparison.afterRevision, comparison.afterUrl),
  );
  const actions = document.createElement('div');
  actions.className = 'svg-comparison-actions';
  const finishComparison = async (action) => {
    const widgetState = active?.comparisonWidget;
    if (widgetState) {
      const accepted = await callbacks.onComparisonDecision?.({
        widgetId: widgetState.widgetId,
        widget: widgetState.widget,
        action,
        fileId: comparison.fileId,
        beforeRevision: comparison.beforeRevision,
        afterRevision: comparison.afterRevision,
      });
      if (accepted === false) return;
      delete active.comparisonWidget;
    }
    clearSvgRevisionComparison();
    render();
  };
  if (active?.comparisonWidget) {
    const editButton = document.createElement('button');
    editButton.type = 'button';
    editButton.className = 'secondary';
    editButton.textContent = 'Continue editing';
    editButton.addEventListener('click', () => finishComparison('continue_editing'));
    const acceptButton = document.createElement('button');
    acceptButton.type = 'button';
    acceptButton.textContent = 'Accept revision';
    acceptButton.addEventListener('click', () => finishComparison('accept_revision'));
    actions.append(editButton, acceptButton);
  } else {
    const continueButton = document.createElement('button');
    continueButton.type = 'button';
    continueButton.textContent = 'Continue with revised SVG';
    continueButton.addEventListener('click', () => finishComparison('continue_editing'));
    actions.append(continueButton);
  }
  board.append(comparisonView, actions);
}

function retireStaleArtifactWidget(artifact) {
  if (!active?.p10Widget?.widget || !artifact?.fileId) return;
  const binding = active.p10Widget.widget.artifact_binding || {};
  const boundArtifactId = String(binding.artifact_id || binding.fileId || '').split('/').pop();
  const boundRevision = Number(binding.base_revision ?? binding.revision);
  const nextRevision = Number(artifact.revision || artifact.scene?.revision || 0);
  if (!boundArtifactId || boundArtifactId !== String(artifact.fileId)
    || !Number.isFinite(boundRevision) || nextRevision <= boundRevision) return;
  const staleWidgetId = active.p10Widget.widgetId;
  if (active.applyingWidgetId === staleWidgetId) return;
  callbacks.onWidgetStale?.({
    sessionId: active.sessionId,
    widgetId: staleWidgetId,
    widget: active.p10Widget.widget,
    artifactId: artifact.fileId,
    baseRevision: boundRevision,
    currentRevision: nextRevision,
  });
  if (active.pendingWidget?.widgetId === staleWidgetId) delete active.pendingWidget;
  active.verifiedWidgetBindings?.delete(String(staleWidgetId || ''));
  delete active.p10Widget;
  host?.querySelector(`[data-p10-anchored-widget] iframe[data-widget-id="${CSS.escape(String(staleWidgetId))}"]`)?.closest('[data-p10-anchored-widget]')?.remove();
  host?.querySelector(`[data-p10-review-widget] iframe[data-widget-id="${CSS.escape(String(staleWidgetId))}"]`)?.closest('[data-p10-review-widget]')?.remove();
  host?.querySelector(`[data-p10-widget-slot] iframe[data-widget-id="${CSS.escape(String(staleWidgetId))}"]`)?.remove();
  host?.classList.remove('has-live-artifact-widget');
  setAnchoredWidgetLayout(false);
}

export function setArtifactCanvasBusy(busy) {
  if (!active) return;
  active.isBusy = Boolean(busy);
  host?.classList.toggle('artifact-canvas-busy', active.isBusy);
  updateP10AnalyzeState();
  updateSvgExportState();
}

export function currentArtifactCanvasSvg() {
  if (!active || !GROUNDED_SVG_PLUGINS.has(active.pluginId)) return null;
  if (active.pluginId === P12_PLUGIN_ID || active.pluginId === COLLAGE_AUTHORING_PLUGIN_ID) {
    return ['svg-document', 'svg-collage'].includes(active.collage?.scene?.artifact_type) ? active.collage.artifact : null;
  }
  return [...active.artifacts].reverse().find((artifact) => artifact.artifactType === 'svg-collage'
    || artifact.artifactType === 'svg-figure'
    || artifact.mime === 'image/svg+xml'
    || String(artifact.name || '').toLowerCase().endsWith('.svg')) || null;
}

function currentP10SvgArtifact() {
  if (active?.pluginId !== P10_PLUGIN_ID && active?.pluginId !== COLLAGE_AUTHORING_PLUGIN_ID) return null;
  return currentArtifactCanvasSvg();
}

function currentExportableSvgArtifact() {
  if (!active) return null;
  if (active.collage?.artifact) return active.collage.artifact;
  return [...active.artifacts].reverse().find((artifact) => artifact.artifactType === 'svg-document'
    || artifact.artifactType === 'svg-collage'
    || artifact.artifactType === 'svg-figure'
    || artifact.mime === 'image/svg+xml'
    || String(artifact.name || '').toLowerCase().endsWith('.svg')) || null;
}

function updateSvgExportState() {
  const button = host?.querySelector('[data-artifact-export]');
  if (!button) return;
  button.disabled = !currentExportableSvgArtifact() || Boolean(active?.isBusy);
}

async function exportCurrentSvg() {
  const artifact = currentExportableSvgArtifact();
  if (!artifact || active?.isBusy) return;
  const button = host.querySelector('[data-artifact-export]');
  button.disabled = true;
  try {
    const revision = artifact.revision || artifact.scene?.revision || active.collage?.scene?.revision || Date.now();
    const response = await fetch(`${artifact.url || artifactUrl(artifact.fileId)}?revision=${encodeURIComponent(revision)}`);
    if (!response.ok) throw new Error(await response.text());
    const svg = await response.text();
    if (!/<svg[\s>]/i.test(svg)) throw new Error('The current artifact is not an SVG document.');
    const blob = new Blob([svg], { type: 'image/svg+xml;charset=utf-8' });
    const objectUrl = URL.createObjectURL(blob);
    const link = document.createElement('a');
    const baseName = String(artifact.name || 'inflak-artifact').replace(/\.svg$/i, '');
    link.href = objectUrl;
    link.download = `${baseName}.svg`;
    document.body.append(link);
    link.click();
    link.remove();
    window.setTimeout(() => URL.revokeObjectURL(objectUrl), 1000);
  } catch (error) {
    callbacks.onError?.(`SVG export failed: ${error.message}`);
  } finally {
    updateSvgExportState();
  }
}

function updateP10AnalyzeState() {
  const button = host?.querySelector('[data-p10-analyze]');
  if (!button) return;
  const artifact = currentP10SvgArtifact();
  button.disabled = !artifact || Boolean(active?.isBusy);
  button.classList.toggle('is-busy', Boolean(active?.isBusy));
  button.querySelector('span').textContent = active?.isBusy ? 'Analyzing' : 'Analyze';
}

async function analyzeP10Artifact() {
  const artifact = currentP10SvgArtifact();
  if (!artifact || active?.isBusy) return;
  active.isBusy = true;
  updateP10AnalyzeState();
  try {
    const started = await callbacks.onAnalyze?.(artifact);
    if (started === false) active.isBusy = false;
  } catch (error) {
    active.isBusy = false;
    callbacks.onError?.(`Analysis failed: ${error.message}`);
  }
  updateP10AnalyzeState();
}

export function mountArtifactCanvasWidget(widget, widgetId, srcdoc, height, options = {}) {
  if (!active) return false;
  if ((widget.semantic_widget_type || widget.widget_type) === 'svg_revision_comparison') {
    if (!active.svgComparison) {
      callbacks.onError?.('The SVG comparison snapshot is unavailable for this revision pair.');
      return false;
    }
    active.comparisonWidget = { widget, widgetId };
    render();
    return true;
  }
  if (active.pluginId === 'inflak-pN8-generative-artifact-control-widgets') {
    if (!active.collage) {
      active.pendingWidget = { widget, widgetId, srcdoc, height, options };
      return true;
    }
    if (options.historical) return mountHistoricalWidgetWindow(widget, widgetId, srcdoc, height);
    return mountWidgetFrame(host.querySelector('[data-p8-widget-slot]'), widget, widgetId, srcdoc, height, 'p8-canvas-widget-frame');
  }
  if (!GROUNDED_SVG_PLUGINS.has(active.pluginId)) return false;
  if (!active.collage) {
    active.pendingWidget = { widget, widgetId, srcdoc, height, options };
    return true;
  }
  const widgetState = { widget, widgetId, srcdoc, height, options };
  active.p10Widget = widgetState;
  host.querySelector('[data-p10-widget-anchor-hint]')?.remove();
  const binding = widget.artifact_binding || {};
  const activeArtifactId = String(active.collage.artifact.fileId || '');
  const bindingArtifactName = artifactFileName(binding.artifact_id || binding.fileId);
  const bindingRevision = binding.base_revision ?? binding.revision;
  const artifactIdMatches = !bindingArtifactName || artifactFileIdsMatch(bindingArtifactName, activeArtifactId);
  const activeRevision = Number(active.collage.scene.revision);
  const boundRevision = Number(bindingRevision);
  const matchingArtifact = active.artifacts.find((artifact) => String(artifact.fileId) === activeArtifactId);
  const loadingRevision = Number(matchingArtifact?.revision || matchingArtifact?.scene?.revision || 0);
  if (artifactIdMatches && bindingRevision !== undefined && boundRevision !== activeRevision
    && boundRevision > activeRevision && loadingRevision >= boundRevision) {
    active.pendingWidget = widgetState;
    return true;
  }
  if (!options.historical && ((!artifactIdMatches)
    || (bindingRevision !== undefined && boundRevision !== activeRevision))) {
    callbacks.onWidgetStale?.({
      sessionId: active.sessionId,
      widgetId,
      widget,
      artifactId: activeArtifactId,
      baseRevision: Number.isFinite(boundRevision) ? boundRevision : null,
      currentRevision: activeRevision,
    });
    if (active.p10Widget?.widgetId === widgetId) delete active.p10Widget;
    host?.classList.remove('has-live-artifact-widget');
    callbacks.onError?.('Artifact widget binding is stale. Re-enter planning with the current SVG revision.');
    return false;
  }
  if (options.historical) {
    const semanticWidgetType = widget.semantic_widget_type || widget.widget_type;
    if (options.interactiveLayoutHistory && semanticWidgetType === 'svg_collage_layout_board') {
      const returnedTransforms = Array.isArray(options.layoutValues?.item_transforms)
        ? options.layoutValues.item_transforms
        : [];
      startP12LayoutDraft(widgetId, {
        preview_operations: returnedTransforms.map((transform) => ({
          op: 'set_transform',
          ...transform,
        })),
      });
      enableP12LayoutObjectInteractions();
      host.querySelector('.p10-instruction-workspace')?.classList.add('p12-layout-board-active');
      renderP12LayoutDraft();
    }
    return mountHistoricalWidgetWindow(widget, widgetId, srcdoc, height);
  }
  active.verifiedWidgetBindings.set(String(widgetId || widget.widget_id || ''), {
    artifactId: activeArtifactId,
    revision: activeRevision,
  });
  host?.classList.add('has-live-artifact-widget');
  host.querySelector('[data-p10-anchored-widget]')?.remove();
  host.querySelector('[data-p10-review-widget]')?.remove();
  setAnchoredWidgetLayout(false);
  const sidebarSlot = host.querySelector('[data-p10-widget-slot]');
  sidebarSlot?.replaceChildren();
  const placement = widget.placement || {};
  const semanticWidgetType = widget.semantic_widget_type || widget.widget_type;
  const isP12LayoutBoard = semanticWidgetType === 'svg_collage_layout_board';
  const unifiedObjectWidget = ['svg_object_grounding', 'svg_operation_control', 'svg_candidate_selector'].includes(semanticWidgetType);
  const dynamicSuggestionReview = semanticWidgetType === 'object_suggestion_review';
  const dynamicProposalReview = semanticWidgetType === 'svg_proposal_review';
  const dynamicPromptGrounding = ['prompt_object_alignment', 'prompt_target_resolver', 'prompt_action_specificity_editor'].includes(semanticWidgetType);
  const interactionSpec = widget.display?.interaction_spec || widget.display?.recommendation || {};
  const interactionTargetIds = interactionSpec.default_target_ids || interactionSpec.recommended_target_ids || interactionSpec.annotation?.object_ids || [];
  const dynamicP12Interaction = ['adaptive_refinement_interaction', 'refinement_recommendation_inspector', 'artifact_color_palette'].includes(semanticWidgetType);
  const dynamicP12Refinement = ['refinement_control', 'semantic_variant_review'].includes(semanticWidgetType);
  const contractObjectIds = [
    ...(placement.anchor?.object_ids || []),
    ...(widget.artifact_binding?.object_ids || []),
    ...(widget.artifact_binding?.stable_object_ids || []),
  ].filter(Boolean);
  const objectIds = dynamicP12Interaction
    ? interactionTargetIds
    : dynamicPromptGrounding && contractObjectIds.length
      ? contractObjectIds
    : dynamicSuggestionReview || dynamicPromptGrounding || dynamicP12Refinement
      ? [active.collage.editingId, ...(active.collage.selectedObjectIds || [])].filter(Boolean)
    : contractObjectIds;
  if (dynamicSuggestionReview) markP10SuggestionObjects(widget);
  if (dynamicProposalReview) markSvgProposalObjects(widget);
  if (dynamicP12Interaction) {
    active.candidateObjectIds = new Set(active.collage.scene.objects.map((object) => object.id));
    markP12InteractionObjects(interactionSpec);
  }
  if (dynamicPromptGrounding || dynamicP12Refinement) active.candidateObjectIds = new Set(widget.artifact_binding?.object_ids?.length
    ? widget.artifact_binding.object_ids
    : active.collage.scene.objects.map((object) => object.id));
  if (isP12LayoutBoard) {
    startP12LayoutDraft(widgetId, interactionSpec);
    enableP12LayoutObjectInteractions();
    host.querySelector('.p10-instruction-workspace')?.classList.add('p12-layout-board-active');
    renderP12LayoutDraft();
    const mounted = mountWidgetFrame(sidebarSlot, widget, widgetId, srcdoc, Math.min(Number(height) || 520, 640), 'p10-sidebar-widget-frame');
    syncP12LayoutDraft();
    return mounted;
  }
  if (placement.mode === 'anchored' || unifiedObjectWidget || dynamicSuggestionReview || dynamicProposalReview || dynamicPromptGrounding || dynamicP12Interaction || dynamicP12Refinement) {
    setAnchoredWidgetLayout(true);
    const object = objectIds.map(findP10Object).find(Boolean);
    if (object) {
      const surface = host.querySelector('[data-p10-collage-surface]');
      const popover = document.createElement('div');
      popover.className = 'p10-anchored-widget';
      popover.dataset.p10AnchoredWidget = '';
      surface?.append(popover);
      const mounted = mountWidgetFrame(popover, widget, widgetId, srcdoc, height, 'p10-anchored-widget-frame');
      if (mounted) positionP10Popover(popover, object, surface, placement.anchor?.preferred_side);
      if (mounted && dynamicPromptGrounding && contractObjectIds.length) {
        focusArtifactCanvasBinding(widgetId, contractObjectIds, contractObjectIds[0]);
      }
      return mounted;
    }
    if (options.historical) {
      const surface = host.querySelector('[data-p10-collage-surface]');
      const popover = document.createElement('div');
      popover.className = 'p10-anchored-widget';
      popover.dataset.p10AnchoredWidget = '';
      popover.style.top = '8px';
      popover.style.right = '8px';
      surface?.append(popover);
      return mountWidgetFrame(popover, widget, widgetId, srcdoc, height, 'p10-anchored-widget-frame');
    }
    if (unifiedObjectWidget || dynamicSuggestionReview || dynamicProposalReview || dynamicPromptGrounding || dynamicP12Interaction || dynamicP12Refinement) {
      if (dynamicP12Interaction) {
        active.pendingWidget = widgetState;
        return mountWidgetFrame(sidebarSlot, widget, widgetId, srcdoc, height, 'p10-sidebar-widget-frame');
      }
      const surface = host.querySelector('[data-p10-collage-surface]');
      if (surface) {
        const hint = document.createElement('div');
        hint.className = 'p10-widget-anchor-hint';
        hint.dataset.p10WidgetAnchorHint = '';
        hint.textContent = dynamicPromptGrounding ? 'Click an object to ground this prompt.' : dynamicP12Refinement || unifiedObjectWidget ? 'Click an object to refine this artifact.' : 'Click an object to open its instruction widget.';
        surface.append(hint);
      }
      return mountWidgetFrame(sidebarSlot, widget, widgetId, srcdoc, height, 'p10-sidebar-widget-frame');
    }

  }
  if (placement.mode === 'canvas_overlay') {
    const surface = host.querySelector('[data-p10-collage-surface]');
    const overlay = document.createElement('div');
    overlay.className = 'p10-review-widget';
    overlay.dataset.p10ReviewWidget = '';
    surface?.append(overlay);
    return mountWidgetFrame(overlay, widget, widgetId, srcdoc, height, 'p10-review-widget-frame');
  }
  return mountWidgetFrame(sidebarSlot, widget, widgetId, srcdoc, height, 'p10-sidebar-widget-frame');
}

function historicalWidgetStorageKey(widgetId) {
  return `inflak:historical-widget:${active?.sessionId || 'session'}:${widgetId || 'widget'}`;
}

function mountHistoricalWidgetWindow(widget, widgetId, srcdoc, height) {
  const surface = host?.querySelector('.p8-collage-surface');
  if (!surface) return false;
  surface.querySelector('[data-historical-widget-window]')?.remove();
  const windowElement = document.createElement('section');
  windowElement.className = 'historical-widget-window';
  windowElement.dataset.historicalWidgetWindow = '';
  windowElement.setAttribute('aria-label', widget.title || widget.display?.title || 'Historical widget');
  const handle = document.createElement('div');
  handle.className = 'historical-widget-handle';
  handle.title = 'Drag widget';
  const grip = document.createElement('i');
  grip.setAttribute('data-lucide', 'grip-horizontal');
  grip.setAttribute('aria-hidden', 'true');
  const title = document.createElement('span');
  title.textContent = widget.title || widget.display?.title || 'Widget history';
  const hide = document.createElement('button');
  hide.type = 'button';
  hide.title = 'Hide widget';
  hide.setAttribute('aria-label', hide.title);
  const hideIcon = document.createElement('i');
  hideIcon.setAttribute('data-lucide', 'eye-off');
  hideIcon.setAttribute('aria-hidden', 'true');
  hide.append(hideIcon);
  const reset = document.createElement('button');
  reset.type = 'button';
  reset.title = 'Reset widget size and position';
  reset.setAttribute('aria-label', reset.title);
  const resetIcon = document.createElement('i');
  resetIcon.setAttribute('data-lucide', 'rotate-ccw');
  resetIcon.setAttribute('aria-hidden', 'true');
  reset.append(resetIcon);
  handle.append(grip, title, hide, reset);
  const body = document.createElement('div');
  body.className = 'historical-widget-body';
  windowElement.append(handle, body);
  const show = document.createElement('button');
  show.type = 'button';
  show.className = 'historical-widget-show hidden';
  show.title = 'Show widget';
  show.setAttribute('aria-label', show.title);
  const showIcon = document.createElement('i');
  showIcon.setAttribute('data-lucide', 'eye');
  showIcon.setAttribute('aria-hidden', 'true');
  show.append(showIcon, document.createTextNode(' Show widget'));
  surface.append(windowElement);
  surface.append(show);

  const storageKey = historicalWidgetStorageKey(widgetId);
  const defaultWidth = Math.min(520, Math.max(300, surface.clientWidth - 32));
  const defaultHeight = Math.min(560, Math.max(300, surface.clientHeight - 32));
  const defaultLayout = () => ({
    width: defaultWidth,
    height: defaultHeight,
    left: Math.max(8, surface.clientWidth - defaultWidth - 8),
    top: 8,
  });
  let savedLayout = null;
  try {
    savedLayout = JSON.parse(localStorage.getItem(storageKey) || 'null');
  } catch {
    savedLayout = null;
  }
  const applyLayout = (layout) => {
    const width = Math.min(Math.max(Number(layout?.width) || defaultWidth, 160), Math.max(160, surface.clientWidth - 16));
    const heightValue = Math.min(Math.max(Number(layout?.height) || defaultHeight, 96), Math.max(96, surface.clientHeight - 16));
    const left = Math.max(8, Math.min(Number(layout?.left) || 0, surface.clientWidth - width - 8));
    const top = Math.max(8, Math.min(Number(layout?.top) || 0, surface.clientHeight - heightValue - 8));
    Object.assign(windowElement.style, { width: `${width}px`, height: `${heightValue}px`, left: `${left}px`, top: `${top}px` });
  };
  let hidden = Boolean(savedLayout?.hidden);
  const saveLayout = (hiddenValue = hidden) => {
    const layout = {
      width: windowElement.offsetWidth,
      height: windowElement.offsetHeight,
      left: windowElement.offsetLeft,
      top: windowElement.offsetTop,
      hidden: hiddenValue,
    };
    localStorage.setItem(storageKey, JSON.stringify(layout));
  };
  const setHidden = (nextHidden, persist = true) => {
    if (persist && nextHidden) saveLayout(true);
    hidden = nextHidden;
    windowElement.classList.toggle('hidden', hidden);
    show.classList.toggle('hidden', !hidden);
    if (persist && !nextHidden) saveLayout(false);
  };
  applyLayout(savedLayout || defaultLayout());
  setHidden(hidden, false);
  hide.addEventListener('click', () => setHidden(true));
  show.addEventListener('click', () => setHidden(false));
  reset.addEventListener('click', () => {
    localStorage.removeItem(storageKey);
    applyLayout(defaultLayout());
    setHidden(false, false);
  });
  handle.addEventListener('pointerdown', (event) => {
    if (event.target.closest('button')) return;
    event.preventDefault();
    const startX = event.clientX;
    const startY = event.clientY;
    const startLeft = windowElement.offsetLeft;
    const startTop = windowElement.offsetTop;
    handle.setPointerCapture(event.pointerId);
    const move = (moveEvent) => {
      const maxLeft = Math.max(8, surface.clientWidth - windowElement.offsetWidth - 8);
      const maxTop = Math.max(8, surface.clientHeight - windowElement.offsetHeight - 8);
      windowElement.style.left = `${Math.max(8, Math.min(startLeft + moveEvent.clientX - startX, maxLeft))}px`;
      windowElement.style.top = `${Math.max(8, Math.min(startTop + moveEvent.clientY - startY, maxTop))}px`;
    };
    const end = () => {
      handle.removeEventListener('pointermove', move);
      handle.removeEventListener('pointerup', end);
      handle.removeEventListener('pointercancel', end);
      saveLayout();
    };
    handle.addEventListener('pointermove', move);
    handle.addEventListener('pointerup', end);
    handle.addEventListener('pointercancel', end);
  });
  if (window.ResizeObserver) new ResizeObserver(() => {
    if (!hidden) saveLayout();
  }).observe(windowElement);
  const mounted = mountWidgetFrame(body, widget, widgetId, srcdoc, height, 'historical-widget-frame');
  window.lucide?.createIcons();
  return mounted;
}

export function focusArtifactCanvasBinding(widgetId, objectIds = [], primaryObjectId = '') {
  if (!active?.collage || String(active.p10Widget?.widgetId || '') !== String(widgetId || '')) return false;
  const sceneObjectIds = new Set(active.collage.scene?.objects?.map((object) => object.id) || []);
  const validObjectIds = [...new Set(objectIds.map(String).filter((objectId) => sceneObjectIds.has(objectId)))];
  const primary = sceneObjectIds.has(String(primaryObjectId || ''))
    ? String(primaryObjectId)
    : validObjectIds[0] || '';
  if (!primary) return false;
  if (!validObjectIds.includes(primary)) validObjectIds.unshift(primary);
  active.collage.editingId = primary;
  active.collage.highlightedId = primary;
  active.collage.selectedObjectIds = validObjectIds;
  const svg = host?.querySelector('[data-p10-collage-surface] > svg.p8-editable-svg, .p8-collage-surface > svg.p8-editable-svg');
  const inspector = host?.querySelector('.p8-collage-inspector');
  if (svg) {
    for (const element of svg.querySelectorAll('.p8-collage-object')) {
      element.classList.toggle('selected', validObjectIds.includes(element.id));
    }
  }
  if (inspector) renderCollageInspector(inspector, active.collage.readOnly);
  anchorP10WidgetToObject(primary);
  syncP10CanvasSelection(validObjectIds);
  return true;
}

function markP12InteractionObjects(interactionSpec) {
  const targetIds = new Set(interactionSpec.default_target_ids || interactionSpec.recommended_target_ids || interactionSpec.annotation?.object_ids || []);
  const label = interactionSpec.annotation?.label || interactionSpec.interaction_goal || interactionSpec.title || 'Generated interaction';
  for (const element of host.querySelectorAll('[data-collage-object="true"]')) {
    const recommended = targetIds.has(element.id);
    element.classList.toggle('p12-recommended-target', recommended);
    if (recommended) {
      element.setAttribute('aria-label', `${element.id}: ${label}`);
      element.dataset.p12Recommendation = label;
    } else {
      delete element.dataset.p12Recommendation;
    }
  }
  active.recommendedTargetIds = [...targetIds];
}

function markP10SuggestionObjects(widget) {
  const suggestions = Array.isArray(widget.display?.suggestions) ? widget.display.suggestions : [];
  const decisions = new Map((widget.display?.current_decisions || []).map((record) => [record.suggestion_id, record.decision]));
  const candidateIds = new Set(suggestions.flatMap((suggestion) => suggestion.object_ids || []));
  if (candidateIds.size === 0) {
    for (const objectId of widget.artifact_binding?.object_ids || []) candidateIds.add(objectId);
  }
  active.candidateObjectIds = candidateIds;
  for (const element of host.querySelectorAll('[data-collage-object="true"]')) {
    const hasSuggestion = candidateIds.has(element.id);
    const objectDecisions = suggestions
      .filter((suggestion) => (suggestion.object_ids || []).includes(element.id))
      .map((suggestion) => decisions.get(suggestion.suggestion_id) || 'pending');
    const decisionState = objectDecisions.includes('pending') ? 'pending'
      : objectDecisions.includes('edited') ? 'edited'
        : objectDecisions.includes('accepted') ? 'accepted' : objectDecisions[0] || '';
    element.classList.toggle('p10-has-suggestion', hasSuggestion);
    for (const state of ['pending', 'accepted', 'edited', 'rejected']) {
      element.classList.toggle(`p10-suggestion-${state}`, hasSuggestion && decisionState === state);
    }
    if (hasSuggestion) element.setAttribute('aria-label', `${element.id}: GenAI suggestion ${decisionState}`);
  }
}

function markSvgProposalObjects(widget) {
  const proposals = Array.isArray(widget.display?.proposals) ? widget.display.proposals : [];
  const candidateIds = new Set(proposals.flatMap((proposal) => [
    ...(proposal.target_object_ids || []),
    ...(proposal.targets || []),
    ...(proposal.selected_stable_ids || []),
    ...(proposal.target_hypotheses || []).map((target) => target.object_id).filter(Boolean),
  ]));
  active.candidateObjectIds = candidateIds;
  for (const element of host.querySelectorAll('[data-collage-object="true"]')) {
    const proposed = candidateIds.has(element.id);
    element.classList.toggle('p10-has-suggestion', proposed);
    element.classList.toggle('p10-suggestion-pending', proposed);
    if (proposed) element.setAttribute('aria-label', `${element.id}: related analysis proposal`);
  }
}

function mountWidgetFrame(slot, widget, widgetId, srcdoc, height, className) {
  if (!slot) return false;
  slot.replaceChildren();
  const frame = document.createElement('iframe');
  frame.className = `html-widget-frame ${className}`;
  frame.setAttribute('sandbox', 'allow-scripts allow-forms');
  frame.setAttribute('scrolling', 'auto');
  frame.dataset.widgetId = widgetId || widget.widget_id || '';
  frame.style.height = `${Math.max(Number(height) || 320, 180)}px`;
  frame.srcdoc = srcdoc;
  if (className === 'historical-widget-frame') {
    let bridgedPointerId = null;
    const sendPointer = (event, phase) => {
      const rect = frame.getBoundingClientRect();
      frame.contentWindow?.postMessage({
        type: 'artifact_widget_pointer_sequence',
        widgetId: frame.dataset.widgetId,
        phase,
        pointerId: event.pointerId,
        x: event.clientX - rect.left,
        y: event.clientY - rect.top,
      }, '*');
    };
    frame.addEventListener('pointerdown', (event) => {
      bridgedPointerId = event.pointerId;
      frame.setPointerCapture(event.pointerId);
      sendPointer(event, 'down');
    });
    frame.addEventListener('pointermove', (event) => {
      if (bridgedPointerId === event.pointerId) sendPointer(event, 'move');
    });
    const finishPointer = (event) => {
      if (bridgedPointerId !== event.pointerId) return;
      sendPointer(event, event.type === 'pointercancel' ? 'cancel' : 'up');
      bridgedPointerId = null;
    };
    frame.addEventListener('pointerup', finishPointer);
    frame.addEventListener('pointercancel', finishPointer);
  }
  frame.addEventListener('click', (event) => {
    frame.contentWindow?.postMessage({
      type: 'artifact_widget_pointer',
      widgetId: frame.dataset.widgetId,
      x: event.offsetX,
      y: event.offsetY,
      timestamp: Date.now(),
    }, '*');
  });
  frame.addEventListener('wheel', (event) => {
    event.preventDefault();
    frame.contentWindow?.postMessage({
      type: 'artifact_widget_wheel',
      widgetId: frame.dataset.widgetId,
      deltaX: event.deltaX,
      deltaY: event.deltaY,
    }, '*');
  }, { passive: false });
  slot.append(frame);
  if (GROUNDED_SVG_PLUGINS.has(active?.pluginId)) {
    frame.addEventListener('load', () => {
      syncP10CanvasSelection(active?.collage?.selectedObjectIds || []);
      syncP12LayoutDraft();
    }, { once: true });
  }
  return true;
}

export function resolveArtifactCanvasWidget(widgetId, action = 'accept') {
  const frame = [...(host?.querySelectorAll('iframe[data-widget-id]') || [])]
    .find((candidate) => candidate.dataset.widgetId === String(widgetId || ''));
  if (!frame) return false;
  const status = document.createElement('div');
  status.className = 'artifact-widget-status';
  status.dataset.state = 'submitted';
  status.dataset.widgetId = String(widgetId || '');
  status.setAttribute('role', 'status');
  status.innerHTML = `<strong>${action === 'dismiss' ? 'Dismissed' : 'Submitted'}</strong><span>Continuing the SVG workflow...</span>`;
  frame.replaceWith(status);
  active?.verifiedWidgetBindings?.delete(String(widgetId || ''));
  clearP12LayoutDraft(action !== 'apply' && action !== 'accept');
  host?.classList.remove('has-live-artifact-widget');
  setAnchoredWidgetLayout(false);
  return true;
}

export function completeArtifactCanvasWidgets() {
  const completedWidgetIds = new Set();
  for (const status of host?.querySelectorAll('.artifact-widget-status[data-state="submitted"]') || []) {
    completedWidgetIds.add(status.dataset.widgetId || '');
    const transientContainer = status.closest('[data-p10-review-widget], [data-p10-anchored-widget]');
    if (transientContainer) transientContainer.remove();
    else status.remove();
  }
  if (active?.p10Widget && completedWidgetIds.has(String(active.p10Widget.widgetId || ''))) delete active.p10Widget;
  if (active?.pendingWidget && completedWidgetIds.has(String(active.pendingWidget.widgetId || ''))) delete active.pendingWidget;
  for (const widgetId of completedWidgetIds) active?.verifiedWidgetBindings?.delete(String(widgetId || ''));
  host?.classList.remove('has-live-artifact-widget');
  clearP12LayoutDraft(false);
  setAnchoredWidgetLayout(false);
  if (completedWidgetIds.size > 0) void render();
}

export async function applyArtifactCanvasWidgetValues(values, widgetId = '') {
  if (READ_ONLY_SVG_PLUGINS.has(active?.pluginId)) throw new Error('Prompt and instruction widgets cannot patch the source SVG.');
  const collage = active?.collage;
  const operations = values?.operations;
  if (!collage || !Array.isArray(operations) || operations.length === 0) return null;
  const verifiedBinding = active.verifiedWidgetBindings?.get(String(widgetId || ''));
  if (!verifiedBinding) throw new Error('Widget artifact binding is unavailable. Reopen this interaction.');
  const currentArtifactId = artifactFileName(collage.artifact.fileId);
  if (!artifactFileIdsMatch(verifiedBinding.artifactId, currentArtifactId)) {
    throw new Error('Widget artifact binding is stale.');
  }
  if (Number(verifiedBinding.revision) !== Number(collage.scene.revision)) {
    throw new Error('Widget revision is stale.');
  }
  values.artifact_id = collage.artifact.fileId;
  values.base_revision = Number(collage.scene.revision);
  active.applyingWidgetId = String(widgetId || active.p10Widget?.widgetId || '');
  try {
    return await commitCollageOperations(operations);
  } finally {
    delete active.applyingWidgetId;
  }
}

function artifactFileName(value) {
  return String(value || '').split(/[/?#]/).filter(Boolean).pop() || '';
}

function artifactFileIdsMatch(candidate, current) {
  const candidateName = artifactFileName(candidate);
  const currentName = artifactFileName(current);
  return candidateName === currentName
    || candidateName.startsWith(`${currentName}-`)
    || currentName.startsWith(`${candidateName}-`);
}

export function mergeArtifactCanvasLayoutDraft(values, widgetId = '') {
  const draft = active?.layoutDraft;
  if (!draft || String(draft.widgetId) !== String(widgetId || '')) return values || {};
  const action = String(values?.action || 'apply');
  if (action === 'reset') {
    resetP12LayoutDraft();
    return { ...values, operations: [], item_transforms: [] };
  }
  if (action !== 'apply') return values || {};
  const operations = [...draft.items.values()]
    .filter(({ original, current }) => JSON.stringify(original) !== JSON.stringify(current))
    .map(({ objectId, current }) => ({
      op: 'set_transform',
      object_id: objectId,
      x: current.x,
      y: current.y,
      width: current.width,
      height: current.height,
      rotation: current.rotation,
    }));
  return {
    ...values,
    artifact_id: active.collage.artifact.fileId,
    base_revision: draft.baseRevision,
    item_transforms: operations.map(({ op, object_id, ...transform }) => ({ object_id, ...transform })),
    operations,
  };
}

export function commandArtifactCanvasLayoutDraft(action, widgetId = '') {
  const draft = active?.layoutDraft;
  if (!draft || String(draft.widgetId) !== String(widgetId || '')) return false;
  if (action === 'reset') {
    resetP12LayoutDraft();
    return true;
  }
  return false;
}

export function previewArtifactCanvasLayoutDraft(itemTransforms, widgetId = '', activeObjectId = '') {
  const draft = active?.layoutDraft;
  if (!draft || String(draft.widgetId) !== String(widgetId || '') || !Array.isArray(itemTransforms)) return false;
  for (const transform of itemTransforms) {
    const item = draft.items.get(String(transform?.object_id || ''));
    if (!item) continue;
    item.current = normalizeDraftTransform({ ...item.current, ...transform });
  }
  const objectId = String(activeObjectId || '');
  const svg = host?.querySelector('[data-p10-collage-surface] > svg.p8-editable-svg');
  const inspector = host?.querySelector('.p8-collage-inspector');
  if (objectId && draft.items.has(objectId) && svg && inspector) selectCollageObject(objectId, svg, inspector);
  renderP12LayoutDraft();
  syncP12LayoutDraft();
  return true;
}

function startP12LayoutDraft(widgetId, interactionSpec = {}) {
  const items = new Map();
  for (const object of active?.collage?.scene?.objects || []) {
    const current = normalizeDraftTransform(object.transform || {});
    items.set(object.id, { objectId: object.id, original: { ...current }, current });
  }
  active.layoutDraft = {
    widgetId: String(widgetId || ''),
    baseRevision: Number(active.collage.scene.revision),
    items,
  };
  for (const operation of interactionSpec.preview_operations || []) {
    if (operation?.op !== 'set_transform') continue;
    const item = items.get(operation.object_id);
    if (item) item.current = normalizeDraftTransform({ ...item.current, ...operation });
  }
}

function enableP12LayoutObjectInteractions() {
  const svg = host?.querySelector('[data-p10-collage-surface] > svg.p8-editable-svg');
  const inspector = host?.querySelector('.p8-collage-inspector');
  if (!svg || !inspector) return;
  for (const element of svg.querySelectorAll('[data-collage-object="true"]')) {
    if (element.dataset.p12LayoutInteractive === 'true') continue;
    element.dataset.p12LayoutInteractive = 'true';
    element.addEventListener('pointerdown', (event) => beginObjectMove(event, element, svg, inspector));
  }
}

function normalizeDraftTransform(transform) {
  return {
    x: Number(transform.x) || 0,
    y: Number(transform.y) || 0,
    width: Math.max(1, Number(transform.width) || 1),
    height: Math.max(1, Number(transform.height) || 1),
    rotation: Number(transform.rotation) || 0,
  };
}

function resetP12LayoutDraft() {
  const draft = active?.layoutDraft;
  if (!draft) return;
  for (const item of draft.items.values()) item.current = { ...item.original };
  renderP12LayoutDraft();
  syncP12LayoutDraft();
}

function clearP12LayoutDraft(restore = false) {
  if (!active?.layoutDraft) return;
  if (restore) resetP12LayoutDraft();
  delete active.layoutDraft;
  host?.querySelector('.p10-instruction-workspace')?.classList.remove('p12-layout-board-active');
  host?.querySelector('[data-p12-layout-handles]')?.remove();
}

function renderP12LayoutDraft() {
  const draft = active?.layoutDraft;
  if (!draft) return;
  for (const item of draft.items.values()) {
    const element = findP10Object(item.objectId);
    const object = active.collage.scene.objects.find((record) => record.id === item.objectId);
    if (element && object) previewObjectTransform(element, object, item.current);
  }
  renderP12ResizeHandles();
}

function syncP12LayoutDraft() {
  const draft = active?.layoutDraft;
  if (!draft) return;
  for (const frame of host?.querySelectorAll(`iframe[data-widget-id="${CSS.escape(draft.widgetId)}"]`) || []) {
    frame.contentWindow?.postMessage({
      type: 'artifact_canvas_layout_draft',
      widgetId: draft.widgetId,
      baseRevision: draft.baseRevision,
      activeObjectId: active.collage.editingId || '',
      itemTransforms: [...draft.items.values()].map(({ objectId, current }) => ({ object_id: objectId, ...current })),
    }, '*');
  }
}

async function handleFileSelection(event) {
  const files = [...(event.target.files || [])];
  event.target.value = '';
  await uploadFiles(files);
}

async function handleDrop(event) {
  event.preventDefault();
  host.querySelector('[data-artifact-stage]').classList.remove('dragover');
  await uploadFiles([...(event.dataTransfer?.files || [])]);
}

async function uploadFiles(files) {
  if (!active || files.length === 0) return;
  const button = host.querySelector('[data-artifact-upload]');
  button.disabled = true;
  try {
    const artifacts = await callbacks.onUpload?.(files);
    addArtifactCanvasArtifacts(artifacts || []);
  } catch (error) {
    callbacks.onError?.(`Upload failed: ${error.message}`);
  } finally {
    button.disabled = false;
  }
}

async function render() {
  if (!active || !host) return;
  updateSvgExportState();
  const board = host.querySelector('[data-artifact-board]');
  const empty = host.querySelector('[data-artifact-empty]');
  const svgArtifact = [...active.artifacts].reverse().find((artifact) => artifact.artifactType === 'svg-document'
    || artifact.artifactType === 'svg-collage'
    || artifact.artifactType === 'svg-figure'
    || (artifact.mime === 'image/svg+xml' && (GROUNDED_SVG_PLUGINS.has(active.pluginId) || String(artifact.name || '').startsWith('collage-'))));
  if (svgArtifact) {
    updateP10AnalyzeState();
    empty.classList.add('hidden');
    if (active.svgComparison && active.svgComparison.fileId === String(svgArtifact.fileId || '')) {
      renderSvgRevisionComparison(board, active.svgComparison);
      return;
    }
    await renderCollage(
      board,
      svgArtifact,
      GROUNDED_SVG_PLUGINS.has(active.pluginId) && active.pluginId !== COLLAGE_AUTHORING_PLUGIN_ID,
      READ_ONLY_SVG_PLUGINS.has(active.pluginId),
    );
    return;
  }
  active.collage = null;
  updateP10AnalyzeState();
  board.replaceChildren();
  board.style.transform = `scale(${active.zoom})`;
  host.querySelector('[data-artifact-zoom]').textContent = `${Math.round(active.zoom * 100)}%`;
  empty.classList.toggle('hidden', active.artifacts.length > 0);
  active.artifacts.forEach((artifact, index) => board.append(createArtifactCard(artifact, index)));
}

function findP10Object(objectId) {
  if (!objectId) return null;
  return [...(host?.querySelectorAll('[data-collage-object="true"], .p8-editable-svg [id]') || [])].find((element) => element.id === objectId) || null;
}

function setAnchoredWidgetLayout(anchored) {
  const workspace = host?.querySelector('.p8-collage-workspace');
  const inspector = workspace?.querySelector('.p8-collage-inspector');
  workspace?.classList.toggle('has-anchored-widget', anchored);
  if (inspector) inspector.hidden = anchored;
}

function positionP10Popover(popover, object, surface, preferredSide = 'right') {
  if (!surface) return false;
  const objectRect = object.getBoundingClientRect();
  const surfaceRect = surface.getBoundingClientRect();
  const gap = 10;
  const popoverWidth = Math.min(340, Math.max(220, surface.clientWidth - 16));
  const availableHeight = Math.max(180, Math.min(620, surface.clientHeight - 16));
  popover.style.maxHeight = `${availableHeight}px`;
  const frame = popover.querySelector('iframe');
  if (frame) frame.style.maxHeight = `${availableHeight}px`;
  const popoverHeight = Math.min(popover.getBoundingClientRect().height || 240, availableHeight);
  const leftSpace = objectRect.left - surfaceRect.left - gap;
  const rightSpace = surfaceRect.right - objectRect.right - gap;
  const topSpace = objectRect.top - surfaceRect.top - gap;
  const bottomSpace = surfaceRect.bottom - objectRect.bottom - gap;
  const sides = [preferredSide, 'right', 'left', 'bottom', 'top'];
  const side = [...new Set(sides)].find((candidate) => (
    (candidate === 'right' && rightSpace >= popoverWidth)
    || (candidate === 'left' && leftSpace >= popoverWidth)
    || (candidate === 'bottom' && bottomSpace >= popoverHeight)
    || (candidate === 'top' && topSpace >= popoverHeight)
  )) || 'right';
  let left = side === 'left'
    ? objectRect.left - surfaceRect.left - popoverWidth - gap
    : objectRect.right - surfaceRect.left + gap;
  let top = objectRect.top - surfaceRect.top;
  if (side === 'bottom' || side === 'top') {
    left = objectRect.left - surfaceRect.left;
    top = side === 'bottom'
      ? objectRect.bottom - surfaceRect.top + gap
      : objectRect.top - surfaceRect.top - popoverHeight - gap;
  }
  left = Math.max(8, Math.min(left, surface.clientWidth - popoverWidth - 8));
  top = Math.max(8, Math.min(top, surface.clientHeight - popoverHeight - 8));
  popover.style.width = `${popoverWidth}px`;
  popover.style.left = `${left}px`;
  popover.style.top = `${top}px`;
  return true;
}

function anchorP10WidgetToObject(objectId) {
  if (!active?.p10Widget || !objectId) return;
  const semanticWidgetType = active.p10Widget.widget.semantic_widget_type || active.p10Widget.widget.widget_type;
  if (semanticWidgetType === 'svg_collage_layout_board') return;
  if (active.p10Widget.widget.placement?.mode === 'sidebar') return;
  const existing = host.querySelector('[data-p10-anchored-widget]');
  if (active.candidateObjectIds?.size && !active.candidateObjectIds.has(objectId)) {
    if (existing) existing.hidden = true;
    return;
  }
  host.querySelector('[data-p10-widget-anchor-hint]')?.remove();
  const object = findP10Object(objectId);
  const surface = host.querySelector('[data-p10-collage-surface]');
  if (!object || !surface) return;
  if (existing) {
    existing.hidden = false;
    positionP10Popover(existing, object, surface, active.p10Widget.widget.placement?.anchor?.preferred_side);
    return;
  }
  const widgetState = active.p10Widget;
  mountArtifactCanvasWidget(widgetState.widget, widgetState.widgetId, widgetState.srcdoc, widgetState.height, widgetState.options);
}

async function renderCollage(board, artifact, readOnly = false, allowGenericSvg = readOnly) {
  const editingId = active?.collage?.editingId || '';
  const usesGroundedWidgetSlot = readOnly || active?.pluginId === COLLAGE_AUTHORING_PLUGIN_ID;
  const renderToken = `${artifact.fileId}:${artifact.revision || 0}:${Date.now()}`;
  active.renderToken = renderToken;
  board.style.transform = '';
  board.className = `artifact-board p8-collage-board${readOnly ? ' p10-instruction-board' : ''}`;
  let workspace = board.querySelector('.p8-collage-workspace');
  let surface = workspace?.querySelector('.p8-collage-surface');
  let inspector = workspace?.querySelector('.p8-collage-inspector');
  const reuseWorkspace = Boolean(workspace && surface && inspector);
  if (!reuseWorkspace) {
    board.replaceChildren();
    workspace = document.createElement('div');
    workspace.className = `p8-collage-workspace${readOnly ? ' p10-instruction-workspace' : ''}`;
    surface = document.createElement('div');
    surface.className = `p8-collage-surface${usesGroundedWidgetSlot ? ' p10-instruction-surface' : ''}`;
    if (usesGroundedWidgetSlot) surface.dataset.p10CollageSurface = '';
    surface.innerHTML = '<div class="p8-collage-loading">Loading layered collage...</div>';
    inspector = document.createElement('aside');
    inspector.className = `p8-collage-inspector${readOnly ? ' p10-instruction-inspector' : ''}`;
    inspector.innerHTML = usesGroundedWidgetSlot
      ? '<div class="p8-inspector-empty">Select collage objects to ground the instruction.</div><div data-p10-widget-slot></div>'
      : '<div class="p8-inspector-empty">Select a cutout or text object to edit it.</div><div data-p8-widget-slot></div>';
    workspace.append(surface, inspector);
    board.append(workspace);
  }
  try {
    const response = await fetch(`${artifact.url || artifactUrl(artifact.fileId)}?revision=${artifact.revision || Date.now()}`);
    if (!response.ok) throw new Error(await response.text());
    const text = await response.text();
    if (!active || active.renderToken !== renderToken) return;
    const { svg, scene } = parseSafeCollageSvg(text, allowGenericSvg);
    const preservedEditingId = scene.objects.some((object) => object.id === editingId) ? editingId : '';
    const selectedObjectIds = readOnly
      ? (active?.collage?.selectedObjectIds || []).filter((objectId) => scene.objects.some((object) => object.id === objectId))
      : [];
    active.collage = { artifact: { ...artifact, revision: scene.revision, scene }, scene, editingId: preservedEditingId, highlightedId: preservedEditingId, selectedObjectIds, readOnly };
    updateP10AnalyzeState();
    const previousSvg = surface.querySelector(':scope > svg.p8-editable-svg');
    if (previousSvg) await replaceCollageSvgWithoutFlash(surface, previousSvg, svg);
    else surface.prepend(svg);
    surface.querySelector(':scope > .p8-collage-loading')?.remove();
    bindCollageObjects(svg, inspector, readOnly);
    renderCollageInspector(inspector, readOnly);
    if (readOnly && active?.p10Widget?.widget) {
      const semanticWidgetType = active.p10Widget.widget.semantic_widget_type || active.p10Widget.widget.widget_type;
      if (['adaptive_refinement_interaction', 'refinement_recommendation_inspector'].includes(semanticWidgetType)) {
        markP12InteractionObjects(active.p10Widget.widget.display?.interaction_spec || active.p10Widget.widget.display?.recommendation || {});
      }
    }
    if (active?.pendingWidget) {
      const pendingWidget = active.pendingWidget;
      delete active.pendingWidget;
      mountArtifactCanvasWidget(pendingWidget.widget, pendingWidget.widgetId, pendingWidget.srcdoc, pendingWidget.height, pendingWidget.options);
    }
  } catch (error) {
    if (!reuseWorkspace) surface.textContent = `Could not load SVG collage: ${error.message}`;
    callbacks.onError?.(`Could not load SVG collage: ${error.message}`);
  }
}

async function replaceCollageSvgWithoutFlash(surface, previousSvg, nextSvg) {
  const scrollLeft = surface.scrollLeft;
  const scrollTop = surface.scrollTop;
  nextSvg.classList.add('p8-editable-svg-pending');
  previousSvg.before(nextSvg);
  const imageSources = [...nextSvg.querySelectorAll('image')]
    .map((image) => image.getAttribute('href') || image.getAttribute('xlink:href') || '')
    .filter((source) => source.startsWith('data:image/'));
  await Promise.allSettled(imageSources.map(async (source) => {
    const image = new Image();
    image.src = source;
    if (typeof image.decode === 'function') {
      await Promise.race([
        image.decode(),
        new Promise((resolve) => setTimeout(resolve, 1500)),
      ]);
    }
  }));
  await new Promise((resolve) => {
    let settled = false;
    const finish = () => {
      if (settled) return;
      settled = true;
      resolve();
    };
    requestAnimationFrame(() => requestAnimationFrame(finish));
    setTimeout(finish, 100);
  });
  previousSvg.remove();
  nextSvg.classList.remove('p8-editable-svg-pending');
  surface.scrollLeft = scrollLeft;
  surface.scrollTop = scrollTop;
}

function parseSafeCollageSvg(text, allowGenericSvg = false) {
  const documentNode = new DOMParser().parseFromString(text, 'image/svg+xml');
  if (documentNode.querySelector('parsererror')) throw new Error('Invalid SVG document');
  const source = documentNode.documentElement;
  const metadata = source.querySelector('#inflak-collage-scene');
  const documentMetadata = source.querySelector('#inflak-svg-scene');
  let scene;
  if (metadata?.textContent) {
    scene = JSON.parse(metadata.textContent);
    if (scene.artifact_type !== 'svg-collage' || !Array.isArray(scene.objects)) throw new Error('Unsupported SVG artifact');
  } else if (documentMetadata?.textContent) {
    const canonicalScene = JSON.parse(documentMetadata.textContent);
    if (canonicalScene.artifact_type !== 'svg-document' || !Array.isArray(canonicalScene.objects)) throw new Error('Unsupported SVG document');
    const renderedScene = buildGenericSvgScene(source);
    const canonicalObjects = new Map(canonicalScene.objects.map((object) => [object.id, object]));
    scene = {
      ...renderedScene,
      ...canonicalScene,
      objects: renderedScene.objects.map((object) => ({...object, ...(canonicalObjects.get(object.id) || {})})),
    };
  } else if (allowGenericSvg) {
    scene = buildGenericSvgScene(source);
  } else {
    throw new Error('This SVG is not an editable layered collage');
  }
  for (const unsafe of source.querySelectorAll('script, foreignObject, style')) unsafe.remove();
  for (const element of source.querySelectorAll('*')) {
    for (const attribute of [...element.attributes]) {
      const name = attribute.name.toLowerCase();
      if (name.startsWith('on') || (name.endsWith('href') && !attribute.value.startsWith('data:image/') && !attribute.value.startsWith('#'))) element.removeAttribute(attribute.name);
    }
  }
  const svg = document.importNode(source, true);
  svg.classList.add('p8-editable-svg');
  svg.removeAttribute('width');
  svg.removeAttribute('height');
  return { svg, scene };
}

function buildGenericSvgScene(source) {
  const objectTags = new Set(['text', 'rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'path', 'g', 'use', 'image']);
  const usedIds = new Set();
  const objects = [];
  [source, ...source.querySelectorAll('*')].forEach((element, index) => {
    if (!objectTags.has(element.localName)) return;
    let objectId = element.id || `p10-auto-${index}`;
    if (usedIds.has(objectId)) objectId = `${objectId}-${index}`;
    usedIds.add(objectId);
    element.id = objectId;
    element.dataset.collageObject = 'true';
    const type = element.localName === 'text' ? 'text' : 'graphic';
    const text = type === 'text' ? String(element.textContent || '').trim() : '';
    objects.push({
      id: objectId,
      type,
      label: text || element.getAttribute('data-name') || element.getAttribute('class') || element.localName,
      tag: element.localName,
      z_index: index,
      visible: true,
      locked: true,
      ...(type === 'text' ? { text } : {}),
    });
  });
  const viewBox = String(source.getAttribute('viewBox') || '').trim().split(/[\s,]+/).map(Number);
  return {
    schema_version: '1.0',
    artifact_type: 'svg-figure',
    revision: Number(source.getAttribute('data-p10-revision')) || 1,
    canvas: {
      width: viewBox.length === 4 ? viewBox[2] : source.getAttribute('width') || '',
      height: viewBox.length === 4 ? viewBox[3] : source.getAttribute('height') || '',
      background: 'transparent',
    },
    objects,
  };
}

function bindCollageObjects(svg, inspector, readOnly = false) {
  for (const element of svg.querySelectorAll('[data-collage-object="true"]')) {
    element.classList.add('p8-collage-object');
    element.addEventListener('click', (event) => {
      event.stopPropagation();
      selectCollageObject(element.id, svg, inspector, readOnly && event.shiftKey);
    });
    if (!readOnly || active?.layoutDraft) element.addEventListener('pointerdown', (event) => beginObjectMove(event, element, svg, inspector));
  }
  svg.addEventListener('click', () => clearCollageHighlight(svg));
  if (active?.pluginId === 'inflak-pN8-generative-artifact-control-widgets' && !readOnly && active.collage.editingId) renderObjectTransformControls(svg, inspector, active.collage.editingId);
}

function selectCollageObject(objectId, svg, inspector, additive = false) {
  if (!active?.collage) return;
  active.collage.editingId = objectId;
  active.collage.highlightedId = objectId;
  if (active.collage.readOnly) {
    const selected = new Set(additive ? active.collage.selectedObjectIds : []);
    if (additive && selected.has(objectId)) selected.delete(objectId);
    else selected.add(objectId);
    active.collage.selectedObjectIds = [...selected];
  }
  const selectedIds = active.collage.readOnly ? active.collage.selectedObjectIds : [objectId];
  for (const element of svg.querySelectorAll('.p8-collage-object')) element.classList.toggle('selected', selectedIds.includes(element.id));
  if (active.pluginId === 'inflak-pN8-generative-artifact-control-widgets' && !active.collage.readOnly) renderObjectTransformControls(svg, inspector, objectId);
  renderCollageInspector(inspector, active.collage.readOnly);
  if (active.collage.readOnly || active.pluginId === COLLAGE_AUTHORING_PLUGIN_ID) {
    anchorP10WidgetToObject(objectId);
    syncP10CanvasSelection(selectedIds);
  }
  if (active.layoutDraft) {
    renderP12ResizeHandles();
    syncP12LayoutDraft();
  }
}

function clearCollageHighlight(svg) {
  if (!active?.collage) return;
  active.collage.highlightedId = '';
  for (const element of svg.querySelectorAll('.p8-collage-object')) element.classList.remove('selected');
  svg.querySelector('.p8-transform-controls')?.remove();
}

function renderObjectTransformControls(svg, inspector, objectId) {
  svg.querySelector('.p8-transform-controls')?.remove();
  const object = active?.collage?.scene.objects.find((item) => item.id === objectId);
  if (!object || object.locked || !object.transform) return;
  const transform = object.transform;
  const x = Number(transform.x);
  const y = Number(transform.y);
  const width = Number(transform.width);
  const height = Number(transform.height);
  if (![x, y, width, height].every(Number.isFinite) || width <= 0 || height <= 0) return;
  const namespace = 'http://www.w3.org/2000/svg';
  const controls = document.createElementNS(namespace, 'g');
  controls.classList.add('p8-transform-controls');
  controls.dataset.objectId = objectId;
  controls.setAttribute('transform', `rotate(${Number(transform.rotation) || 0} ${x + width / 2} ${y + height / 2})`);
  const outline = document.createElementNS(namespace, 'rect');
  outline.classList.add('p8-transform-outline');
  outline.setAttribute('x', x);
  outline.setAttribute('y', y);
  outline.setAttribute('width', width);
  outline.setAttribute('height', height);
  const screenScale = Math.max(0.01, Math.hypot(svg.getScreenCTM()?.a || 1, svg.getScreenCTM()?.b || 0));
  const handleRadius = 7 / screenScale;
  const rotateOffset = 28 / screenScale;
  const stem = document.createElementNS(namespace, 'line');
  stem.classList.add('p8-rotate-stem');
  stem.setAttribute('x1', x + width / 2);
  stem.setAttribute('y1', y);
  stem.setAttribute('x2', x + width / 2);
  stem.setAttribute('y2', y - rotateOffset);
  const rotateHandle = document.createElementNS(namespace, 'circle');
  rotateHandle.classList.add('p8-transform-handle', 'p8-rotate-handle');
  rotateHandle.setAttribute('cx', x + width / 2);
  rotateHandle.setAttribute('cy', y - rotateOffset);
  rotateHandle.setAttribute('r', handleRadius);
  rotateHandle.setAttribute('aria-label', 'Rotate element');
  const resizeHandle = document.createElementNS(namespace, 'circle');
  resizeHandle.classList.add('p8-transform-handle', 'p8-resize-handle');
  resizeHandle.setAttribute('cx', x + width);
  resizeHandle.setAttribute('cy', y + height);
  resizeHandle.setAttribute('r', handleRadius);
  resizeHandle.setAttribute('aria-label', 'Scale element proportionally');
  controls.append(outline, stem, rotateHandle, resizeHandle);
  svg.append(controls);
  controls.addEventListener('click', (event) => event.stopPropagation());
  resizeHandle.addEventListener('pointerdown', (event) => beginObjectScale(event, controls, object, svg, inspector));
  rotateHandle.addEventListener('pointerdown', (event) => beginObjectRotation(event, controls, object, svg, inspector));
}

function selectedSceneObject() {
  return active?.collage?.scene.objects.find((object) => object.id === active.collage.editingId) || null;
}

function renderCollageInspector(inspector, readOnly = false) {
  const usesGroundedWidgetSlot = readOnly || active?.pluginId === COLLAGE_AUTHORING_PLUGIN_ID;
  const widgetSlot = inspector.querySelector(usesGroundedWidgetSlot ? '[data-p10-widget-slot]' : '[data-p8-widget-slot]') || document.createElement('div');
  if (usesGroundedWidgetSlot) widgetSlot.dataset.p10WidgetSlot = '';
  else widgetSlot.dataset.p8WidgetSlot = '';
  const object = selectedSceneObject();
  const preserveWidgetSlot = widgetSlot.parentElement === inspector;
  if (preserveWidgetSlot) {
    for (const child of [...inspector.children]) {
      if (child !== widgetSlot) child.remove();
    }
  } else {
    inspector.replaceChildren();
  }
  const heading = document.createElement('div');
  heading.className = 'p8-inspector-heading';
  heading.innerHTML = object
    ? `<span>${escapeMarkup(readOnly ? 'Instruction object' : object.type)}</span><strong>${escapeMarkup(object.label || object.id)}</strong>`
    : `<strong>${readOnly ? 'Grounded instruction' : 'Collage controls'}</strong><span>Select an object on the canvas</span>`;
  if (preserveWidgetSlot) inspector.insertBefore(heading, widgetSlot);
  else inspector.append(heading);
  if (readOnly) {
    const hint = document.createElement('p');
    hint.className = 'p10-inspector-hint';
    hint.textContent = object ? `Bound object: ${object.id}. Continue in the instruction widget.` : `${active?.collage?.scene?.objects?.length || 0} stable objects available.`;
    inspector.insertBefore(hint, preserveWidgetSlot ? widgetSlot : null);
    if (!preserveWidgetSlot) inspector.append(widgetSlot);
    return;
  }
  if (!preserveWidgetSlot) inspector.append(widgetSlot);
  const bundle = active?.collage?.scene?.authoring_bundle;
  if (bundle) {
    inspector.append(createGenerativeAuthoringPanel(object, bundle, inspector));
  } else {
    const notice = document.createElement('p');
    notice.className = 'p8-authoring-notice';
    notice.textContent = 'This collage has no prepared generative options. Generate a new P8 collage to include styles, visual alternatives, and copy directions.';
    inspector.append(notice);
  }
  if (object?.type === 'text') inspector.append(createTextForm(object));
  inspector.append(createAdvancedControls(object));
}

function createGenerativeAuthoringPanel(object, bundle, inspector) {
  const panel = document.createElement('div');
  panel.className = 'p8-authoring-panel';
  const heading = document.createElement('div');
  heading.className = 'p8-authoring-title';
  heading.innerHTML = '<span>Generated with this collage</span><strong>Authoring directions</strong>';
  panel.append(heading);

  const stylePresets = Array.isArray(bundle.visual_style_presets) ? bundle.visual_style_presets : [];
  if (stylePresets.length) panel.append(createVisualStylePresets(stylePresets));
  const sceneObjects = active?.collage?.scene?.objects || [];
  const objectIds = new Set(sceneObjects.map((item) => item.id));
  if (!object) {
    const objectsById = new Map(sceneObjects.map((item) => [item.id, item]));
    const candidateOverview = Object.entries(bundle.asset_candidates_by_object || {})
      .flatMap(([objectId, candidates]) => alternativeAssetCandidates(objectsById.get(objectId), candidates)
        .map((candidate) => ({ ...candidate, objectId })))
      .filter((candidate) => candidate.fileId && objectIds.has(candidate.objectId))
      .slice(0, 6);
    if (candidateOverview.length) panel.append(createCandidateOverview(candidateOverview, sceneObjects, inspector));
  }
  const addableElements = (bundle.addable_elements || [])
    .filter((candidate) => candidate?.fileId && candidate.object_id && !objectIds.has(candidate.object_id));
  if (addableElements.length) panel.append(createAddableElementGallery(addableElements));
  if (['cutout', 'image'].includes(object?.type)) {
    const candidates = alternativeAssetCandidates(object, bundle.asset_candidates_by_object?.[object.id]);
    if (Array.isArray(candidates) && candidates.length) panel.append(createAssetCandidateGallery(object, candidates));
  }
  if (object?.type === 'text') {
    const options = bundle.text_authoring_options?.[object.id];
    if (options) panel.append(createTextAuthoringOptions(object, options));
  }
  if (panel.children.length === 1) {
    const hint = document.createElement('p');
    hint.className = 'p8-authoring-hint';
    hint.textContent = object ? 'No generated alternatives are bound to this object.' : 'Select an object to reveal its generated visual or editorial alternatives.';
    panel.append(hint);
  }
  return panel;
}

function alternativeAssetCandidates(object, candidates) {
  const currentFileId = object?.asset_file_id;
  const alternatives = [];
  const seenFileIds = new Set();
  for (const candidate of Array.isArray(candidates) ? candidates : []) {
    let alternative = candidate;
    if (candidate?.fileId && artifactFileIdsMatch(candidate.fileId, currentFileId)) {
      const sourceFileId = candidate.source_file_id || candidate.source_fileId;
      if (!sourceFileId || artifactFileIdsMatch(sourceFileId, currentFileId)) continue;
      alternative = {
        ...candidate,
        id: `${candidate.id || object?.id || 'candidate'}-original`,
        fileId: sourceFileId,
        label: 'Original selection',
        rationale: 'The asset originally selected for this object.',
        kind: 'generated',
      };
    }
    if (!alternative?.fileId || artifactFileIdsMatch(alternative.fileId, currentFileId)) continue;
    const fileName = artifactFileName(alternative.fileId);
    if (seenFileIds.has(fileName)) continue;
    seenFileIds.add(fileName);
    alternatives.push(alternative);
  }
  return alternatives;
}

function createVisualStylePresets(presets) {
  const section = document.createElement('section');
  section.className = 'p8-authoring-section';
  section.innerHTML = '<h3>Visual direction</h3>';
  const grid = document.createElement('div');
  grid.className = 'p8-style-grid';
  for (const preset of presets) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'p8-style-card';
    const swatches = (preset.swatches || []).map((color) => `<i style="--swatch:${escapeMarkup(color)}"></i>`).join('');
    button.innerHTML = `<span class="p8-swatches">${swatches}</span><strong>${escapeMarkup(preset.label || preset.id)}</strong><small>${escapeMarkup(preset.rationale || 'Apply this prepared visual system.')}</small>`;
    button.addEventListener('click', () => commitCollageOperations(preset.operations || []));
    grid.append(button);
  }
  section.append(grid);
  return section;
}

function createAssetCandidateGallery(object, candidates) {
  const section = document.createElement('section');
  section.className = 'p8-authoring-section';
  section.innerHTML = `<h3>Visual alternatives for ${escapeMarkup(object.label || object.id)}</h3>`;
  const gallery = document.createElement('div');
  gallery.className = 'p8-asset-gallery';
  for (const candidate of candidates) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'p8-asset-option';
    const image = document.createElement('img');
    image.src = artifactUrl(candidate.fileId);
    image.alt = candidate.label || 'Generated visual alternative';
    const copy = document.createElement('span');
    copy.innerHTML = `<em class="p8-candidate-kind" title="Prepared by ${escapeMarkup(candidate.source_tool || 'generation tool')}">${escapeMarkup(authoringKindLabel(candidate.kind))}</em><strong>${escapeMarkup(candidate.label || candidate.id)}</strong><small>${escapeMarkup(candidate.rationale || 'Generated for this object.')}</small>`;
    button.append(image, copy);
    button.addEventListener('click', () => commitCollageOperations([{
      op: object.type === 'image' ? 'replace_asset' : 'replace_cutout_asset',
      object_id: object.id, asset_file_id: candidate.fileId, label: candidate.label || object.label,
    }]));
    gallery.append(button);
  }
  section.append(gallery);
  return section;
}

function createCandidateOverview(candidates, sceneObjects, inspector) {
  const section = document.createElement('section');
  section.className = 'p8-authoring-section';
  section.innerHTML = '<h3>Generated candidates</h3>';
  const gallery = document.createElement('div');
  gallery.className = 'p8-candidate-overview';
  const objectsById = new Map(sceneObjects.map((object) => [object.id, object]));
  for (const candidate of candidates) {
    const object = objectsById.get(candidate.objectId);
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'p8-candidate-preview';
    const image = document.createElement('img');
    image.src = artifactUrl(candidate.fileId);
    image.alt = candidate.label || `Candidate for ${object?.label || candidate.objectId}`;
    const copy = document.createElement('span');
    copy.innerHTML = `<small>${escapeMarkup(object?.label || candidate.objectId)}</small><strong>${escapeMarkup(candidate.label || candidate.id)}</strong>`;
    button.append(image, copy);
    button.addEventListener('click', () => {
      const svg = inspector.closest('.p8-collage-workspace')?.querySelector('svg.p8-editable-svg');
      if (svg) selectCollageObject(candidate.objectId, svg, inspector);
    });
    gallery.append(button);
  }
  section.append(gallery);
  return section;
}

function createAddableElementGallery(elements) {
  const section = document.createElement('section');
  section.className = 'p8-authoring-section';
  section.innerHTML = '<h3>Add generated element</h3>';
  const gallery = document.createElement('div');
  gallery.className = 'p8-addable-gallery';
  for (const candidate of elements) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'p8-addable-option';
    const image = document.createElement('img');
    image.src = artifactUrl(candidate.fileId);
    image.alt = candidate.label || 'Generated addable element';
    const copy = document.createElement('span');
    copy.innerHTML = `<em class="p8-candidate-kind" title="Prepared by ${escapeMarkup(candidate.source_tool || 'generation tool')}">${escapeMarkup(authoringKindLabel(candidate.kind || 'new_element'))}</em><strong>${escapeMarkup(candidate.label || candidate.id)}</strong><small>${escapeMarkup(candidate.rationale || 'Prepared to add to this collage.')}</small>`;
    button.append(image, copy);
    button.addEventListener('click', () => {
      const transform = candidate.default_transform || {};
      return commitCollageOperations([{
        op: 'add_cutout', object_id: candidate.object_id, label: candidate.label || candidate.object_id,
        asset_file_id: candidate.fileId, x: transform.x, y: transform.y, width: transform.width,
        height: transform.height, rotation: transform.rotation,
      }]);
    });
    gallery.append(button);
  }
  section.append(gallery);
  return section;
}

function authoringKindLabel(kind) {
  return ({
    generated: 'Generated',
    restyle: 'Restyle',
    semantic_edit: 'Edit',
    outpaint: 'Expand',
    variation: 'Variation',
    background_treatment: 'Background',
    transform: 'Transform',
    appearance: 'Appearance',
    new_element: 'New element',
  })[kind] || 'Prepared';
}

function createTextAuthoringOptions(object, options) {
  const fragment = document.createDocumentFragment();
  const copyOptions = Array.isArray(options.copy_options) ? options.copy_options : [];
  if (copyOptions.length) {
    const section = document.createElement('section');
    section.className = 'p8-authoring-section';
    section.innerHTML = '<h3>Copy directions</h3>';
    const choices = document.createElement('div');
    choices.className = 'p8-copy-options';
    for (const option of copyOptions) {
      const button = document.createElement('button');
      button.type = 'button';
      button.innerHTML = `<strong>${escapeMarkup(option.label || option.id)}</strong><span>${escapeMarkup(option.text)}</span>`;
      button.addEventListener('click', () => commitCollageOperations([{
        op: 'update_text', object_id: object.id, text: option.text,
      }]));
      choices.append(button);
    }
    section.append(choices);
    fragment.append(section);
  }
  const typographyPresets = Array.isArray(options.typography_presets) ? options.typography_presets : [];
  if (typographyPresets.length) {
    const section = document.createElement('section');
    section.className = 'p8-authoring-section';
    section.innerHTML = '<h3>Typography directions</h3>';
    const choices = document.createElement('div');
    choices.className = 'p8-type-options';
    for (const option of typographyPresets) {
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = option.label || option.id;
      button.style.fontFamily = option.style?.font_family || '';
      button.style.fontWeight = option.style?.font_weight || '';
      button.style.color = safeColorInput(option.style?.fill);
      button.addEventListener('click', () => commitCollageOperations([{
        op: 'update_text', object_id: object.id, style: option.style || {},
      }]));
      choices.append(button);
    }
    section.append(choices);
    fragment.append(section);
  }
  return fragment;
}

function createAdvancedControls(object) {
  const details = document.createElement('details');
  details.className = 'p8-advanced-controls';
  const summary = document.createElement('summary');
  summary.textContent = 'Layout & properties';
  details.append(summary);
  if (object) {
    if (object.capabilities?.style) details.append(createObjectStyleForm(object));
    details.append(createTransformForm(object), createLayerControls(object), createObjectActions(object));
  }
  else details.append(createAddTextForm());
  return details;
}

function syncP10CanvasSelection(selectedObjectIds) {
  const frame = host?.querySelector('[data-p10-widget-slot] iframe, [data-p10-anchored-widget] iframe');
  const activeObjectId = active?.collage?.editingId || selectedObjectIds.at(-1) || '';
  const sceneObject = active?.collage?.scene?.objects?.find((object) => object.id === activeObjectId) || null;
  const objectElement = findP10Object(activeObjectId);
  const computedStyle = objectElement ? getComputedStyle(objectElement) : null;
  const presentation = objectElement ? {
    fill: objectElement.getAttribute('fill') || computedStyle?.fill || '',
    stroke: objectElement.getAttribute('stroke') || computedStyle?.stroke || '',
    opacity: objectElement.getAttribute('opacity') || computedStyle?.opacity || '',
    transform: objectElement.getAttribute('transform') || '',
  } : {};
  const suggestions = active?.p10Widget?.widget?.display?.suggestions || [];
  const suggestionsForObject = suggestions.filter((suggestion) => (suggestion.object_ids || []).includes(activeObjectId));
  const proposals = active?.p10Widget?.widget?.display?.proposals || [];
  const proposalsForObject = proposals.filter((proposal) => [
    ...(proposal.target_object_ids || []),
    ...(proposal.targets || []),
    ...(proposal.selected_stable_ids || []),
    ...(proposal.target_hypotheses || []).map((target) => target.object_id).filter(Boolean),
  ].includes(activeObjectId));
  frame?.contentWindow?.postMessage({
    type: 'artifact_canvas_selection',
    widgetId: frame.dataset.widgetId || '',
    selectedObjectIds,
    activeObjectId,
    object: sceneObject ? { ...sceneObject, presentation } : null,
    suggestionsForObject,
    proposalsForObject,
  }, '*');
}

function createAddTextForm() {
  const form = document.createElement('form');
  form.className = 'p8-control-section p8-text-form';
  form.innerHTML = '<h3>Add text</h3><label>Content<textarea name="text" rows="2" placeholder="Collage title"></textarea></label><div class="p8-field-grid"><label>Size<input name="font_size" type="number" min="8" max="512" value="64"></label><label>Color<input name="fill" type="color" value="#111111"></label></div><button type="submit" class="p8-apply">Add text object</button>';
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const values = new FormData(form);
    const text = String(values.get('text') || '').trim();
    if (!text) return;
    await commitCollageOperations([{
      op: 'add_text', object_id: `text-${crypto.randomUUID().slice(0, 8)}`, label: text.slice(0, 40), text,
      style: { font_size: Number(values.get('font_size')), fill: values.get('fill'), font_family: 'Arial', font_weight: 700 },
    }]);
  });
  return form;
}

function createTransformForm(object) {
  const form = document.createElement('form');
  form.className = 'p8-control-section p8-transform-form';
  const transform = object.transform || {};
  form.innerHTML = `<h3>Transform</h3><div class="p8-field-grid">${numberField('x', transform.x)}${numberField('y', transform.y)}${numberField('width', transform.width, 1)}${numberField('height', transform.height, 1)}${numberField('rotation', transform.rotation)}</div><button type="submit" class="p8-apply">Apply transform</button>`;
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const values = new FormData(form);
    await commitCollageOperations([{
      op: 'set_transform', object_id: object.id,
      x: Number(values.get('x')), y: Number(values.get('y')),
      width: Number(values.get('width')), height: Number(values.get('height')), rotation: Number(values.get('rotation')),
    }]);
  });
  return form;
}

function createObjectStyleForm(object) {
  const form = document.createElement('form');
  form.className = 'p8-control-section p8-object-style-form';
  const presentation = object.presentation || {};
  form.innerHTML = `<h3>Element style</h3><div class="p8-field-grid"><label>Fill<input name="fill" type="color" value="${safeColorInput(presentation.fill)}"></label><label>Stroke<input name="stroke" type="color" value="${safeColorInput(presentation.stroke)}"></label><label>Stroke width<input name="stroke_width" type="number" min="0" max="1000" step="0.5" value="${Number(presentation.stroke_width) || 0}"></label><label>Opacity<input name="opacity" type="number" min="0" max="1" step="0.05" value="${Number.isFinite(Number(presentation.opacity)) ? Number(presentation.opacity) : 1}"></label></div><button type="submit" class="p8-apply">Apply element style</button>`;
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const values = new FormData(form);
    await commitCollageOperations([{
      op: 'set_object_style',
      object_id: object.id,
      style: {
        fill: values.get('fill'),
        stroke: values.get('stroke'),
        stroke_width: Number(values.get('stroke_width')),
        opacity: Number(values.get('opacity')),
      },
    }]);
  });
  return form;
}

function createLayerControls(object) {
  const section = document.createElement('section');
  section.className = 'p8-control-section';
  section.innerHTML = '<h3>Layer order</h3>';
  const actions = document.createElement('div');
  actions.className = 'p8-layer-actions';
  for (const [direction, label] of [['front', 'To front'], ['forward', 'Forward'], ['backward', 'Backward'], ['back', 'To back']]) {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = label;
    button.addEventListener('click', () => commitCollageOperations([{ op: 'set_order', object_id: object.id, direction }]));
    actions.append(button);
  }
  section.append(actions);
  return section;
}

function createObjectActions(object) {
  const section = document.createElement('section');
  section.className = 'p8-control-section p8-object-actions';
  section.innerHTML = '<h3>Object</h3>';
  const remove = document.createElement('button');
  remove.type = 'button';
  remove.className = 'p8-remove-object';
  remove.textContent = 'Remove object';
  remove.addEventListener('click', () => {
    if (!window.confirm(`Remove ${object.label || object.id} from this collage?`)) return;
    return commitCollageOperations([{ op: 'remove_object', object_id: object.id }]);
  });
  section.append(remove);
  return section;
}

function createTextForm(object) {
  const form = document.createElement('form');
  form.className = 'p8-control-section p8-text-form';
  const currentFamily = String(object.style?.font_family || 'Arial');
  const fontOptions = ['Arial', 'Georgia', 'Verdana', 'Trebuchet MS', 'Courier New']
    .map((family) => `<option value="${family}"${family === currentFamily ? ' selected' : ''}>${family}</option>`).join('');
  form.innerHTML = `<h3>Text</h3><label>Content<textarea name="text" rows="2">${escapeMarkup(object.text || '')}</textarea></label><div class="p8-field-grid"><label>Font<select name="font_family">${fontOptions}</select></label><label>Weight<input name="font_weight" type="number" min="100" max="900" step="100" value="${Number(object.style?.font_weight) || 700}"></label><label>Size<input name="font_size" type="number" min="8" max="512" value="${Number(object.style?.font_size) || 64}"></label><label>Color<input name="fill" type="color" value="${safeColorInput(object.style?.fill)}"></label></div><button type="submit" class="p8-apply">Apply text</button>`;
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const values = new FormData(form);
    await commitCollageOperations([{ op: 'update_text', object_id: object.id, text: values.get('text'), style: { font_family: values.get('font_family'), font_weight: Number(values.get('font_weight')), font_size: Number(values.get('font_size')), fill: values.get('fill') } }]);
  });
  return form;
}

function beginObjectScale(event, controls, object, svg, inspector) {
  if (event.button !== 0 || active?.isBusy) return;
  event.preventDefault();
  event.stopPropagation();
  const transform = normalizeDraftTransform(object.transform);
  const angle = transform.rotation * Math.PI / 180;
  const cosine = Math.cos(angle);
  const sine = Math.sin(angle);
  const center = { x: transform.x + transform.width / 2, y: transform.y + transform.height / 2 };
  const anchor = {
    x: center.x - cosine * transform.width / 2 + sine * transform.height / 2,
    y: center.y - sine * transform.width / 2 - cosine * transform.height / 2,
  };
  const diagonal = {
    x: cosine * transform.width - sine * transform.height,
    y: sine * transform.width + cosine * transform.height,
  };
  const minimumScale = Math.max(8 / transform.width, 8 / transform.height);
  const element = svg.querySelector(`#${CSS.escape(object.id)}`);
  const move = (moveEvent) => {
    const point = clientToSvgPoint(svg, moveEvent.clientX, moveEvent.clientY);
    const scale = Math.max(minimumScale, ((point.x - anchor.x) * diagonal.x + (point.y - anchor.y) * diagonal.y) / (diagonal.x ** 2 + diagonal.y ** 2));
    const width = transform.width * scale;
    const height = transform.height * scale;
    const nextCenter = {
      x: anchor.x + cosine * width / 2 - sine * height / 2,
      y: anchor.y + sine * width / 2 + cosine * height / 2,
    };
    const next = { ...transform, x: nextCenter.x - width / 2, y: nextCenter.y - height / 2, width, height };
    controls.dataset.previewTransform = JSON.stringify(next);
    previewObjectTransform(element, object, next);
    previewTransformControls(svg, next);
  };
  finishCanvasTransform(event, controls, move, object, svg, inspector);
}

function beginObjectRotation(event, controls, object, svg, inspector) {
  if (event.button !== 0 || active?.isBusy) return;
  event.preventDefault();
  event.stopPropagation();
  const transform = normalizeDraftTransform(object.transform);
  const center = { x: transform.x + transform.width / 2, y: transform.y + transform.height / 2 };
  const start = clientToSvgPoint(svg, event.clientX, event.clientY);
  const startAngle = Math.atan2(start.y - center.y, start.x - center.x);
  const element = svg.querySelector(`#${CSS.escape(object.id)}`);
  const move = (moveEvent) => {
    const point = clientToSvgPoint(svg, moveEvent.clientX, moveEvent.clientY);
    const delta = (Math.atan2(point.y - center.y, point.x - center.x) - startAngle) * 180 / Math.PI;
    const next = { ...transform, rotation: Math.round((transform.rotation + delta) * 10) / 10 };
    controls.dataset.previewTransform = JSON.stringify(next);
    previewObjectTransform(element, object, next);
    previewTransformControls(svg, next);
  };
  finishCanvasTransform(event, controls, move, object, svg, inspector);
}

function finishCanvasTransform(event, controls, move, object, svg, inspector) {
  controls.setPointerCapture(event.pointerId);
  const finish = async () => {
    removeListeners();
    const transform = JSON.parse(controls.dataset.previewTransform || JSON.stringify(object.transform));
    await commitCollageOperations([{ op: 'set_transform', object_id: object.id, ...transform }]);
  };
  const cancel = () => {
    removeListeners();
    renderObjectTransformControls(svg, inspector, object.id);
  };
  const removeListeners = () => {
    controls.removeEventListener('pointermove', move);
    controls.removeEventListener('pointerup', finish);
    controls.removeEventListener('pointercancel', cancel);
  };
  controls.addEventListener('pointermove', move);
  controls.addEventListener('pointerup', finish);
  controls.addEventListener('pointercancel', cancel);
}

function clientToSvgPoint(svg, clientX, clientY) {
  const point = svg.createSVGPoint();
  point.x = clientX;
  point.y = clientY;
  return point.matrixTransform(svg.getScreenCTM().inverse());
}

function previewTransformControls(svg, transform) {
  const controls = svg.querySelector('.p8-transform-controls');
  if (!controls) return;
  const { x, y, width, height, rotation } = normalizeDraftTransform(transform);
  const outline = controls.querySelector('.p8-transform-outline');
  outline.setAttribute('x', x);
  outline.setAttribute('y', y);
  outline.setAttribute('width', width);
  outline.setAttribute('height', height);
  const screenScale = Math.max(0.01, Math.hypot(svg.getScreenCTM()?.a || 1, svg.getScreenCTM()?.b || 0));
  const rotateOffset = 28 / screenScale;
  const stem = controls.querySelector('.p8-rotate-stem');
  stem.setAttribute('x1', x + width / 2);
  stem.setAttribute('y1', y);
  stem.setAttribute('x2', x + width / 2);
  stem.setAttribute('y2', y - rotateOffset);
  const rotateHandle = controls.querySelector('.p8-rotate-handle');
  rotateHandle.setAttribute('cx', x + width / 2);
  rotateHandle.setAttribute('cy', y - rotateOffset);
  const resizeHandle = controls.querySelector('.p8-resize-handle');
  resizeHandle.setAttribute('cx', x + width);
  resizeHandle.setAttribute('cy', y + height);
  controls.setAttribute('transform', `rotate(${rotation} ${x + width / 2} ${y + height / 2})`);
}

function beginObjectMove(event, element, svg, inspector) {
  if (event.button !== 0 || !active?.collage || (active.isBusy && !active.layoutDraft)) return;
  const object = active.collage.scene.objects.find((item) => item.id === element.id);
  if (!object || object.locked) return;
  event.preventDefault();
  event.stopPropagation();
  selectCollageObject(element.id, svg, inspector);
  const point = svg.createSVGPoint();
  const toSvgPoint = (clientX, clientY) => {
    point.x = clientX;
    point.y = clientY;
    return point.matrixTransform(svg.getScreenCTM().inverse());
  };
  const start = toSvgPoint(event.clientX, event.clientY);
  const draftItem = active.layoutDraft?.items.get(object.id);
  const sourceTransform = draftItem?.current || object.transform;
  const origin = { x: Number(sourceTransform.x), y: Number(sourceTransform.y) };
  element.setPointerCapture(event.pointerId);
  const move = (moveEvent) => {
    const current = toSvgPoint(moveEvent.clientX, moveEvent.clientY);
    const next = { ...sourceTransform, x: origin.x + current.x - start.x, y: origin.y + current.y - start.y };
    previewObjectTransform(element, object, next);
    if (active.pluginId === 'inflak-pN8-generative-artifact-control-widgets') previewTransformControls(svg, next);
  };
  const finish = async (finishEvent) => {
    element.removeEventListener('pointermove', move);
    element.removeEventListener('pointerup', finish);
    element.removeEventListener('pointercancel', cancel);
    const current = toSvgPoint(finishEvent.clientX, finishEvent.clientY);
    const nextTransform = { ...sourceTransform, x: origin.x + current.x - start.x, y: origin.y + current.y - start.y };
    if (draftItem) {
      draftItem.current = normalizeDraftTransform(nextTransform);
      renderP12LayoutDraft();
      syncP12LayoutDraft();
    } else {
      await commitCollageOperations([{ op: 'set_transform', object_id: object.id, ...object.transform, ...nextTransform }]);
    }
  };
  const cancel = () => render();
  element.addEventListener('pointermove', move);
  element.addEventListener('pointerup', finish);
  element.addEventListener('pointercancel', cancel);
}

function previewObjectTransform(element, object, transform) {
  const { x, y, width, height, rotation } = normalizeDraftTransform(transform);
  if (object.type === 'text') {
    const sourceWidth = Number(object.transform?.width) || width;
    const fontSize = Number(object.style?.font_size || 64) * width / sourceWidth;
    element.setAttribute('x', x);
    element.setAttribute('y', y + fontSize);
    element.setAttribute('font-size', fontSize);
  } else {
    element.setAttribute('x', x);
    element.setAttribute('y', y);
    element.setAttribute('width', width);
    element.setAttribute('height', height);
  }
  element.setAttribute('transform', `rotate(${rotation} ${x + width / 2} ${y + height / 2})`);
}

function renderP12ResizeHandles() {
  host?.querySelector('[data-p12-layout-handles]')?.remove();
  const draft = active?.layoutDraft;
  const objectId = active?.collage?.editingId;
  const item = draft?.items.get(objectId);
  const element = findP10Object(objectId);
  const surface = host?.querySelector('[data-p10-collage-surface]');
  if (!item || !element || !surface) return;
  const surfaceRect = surface.getBoundingClientRect();
  const elementRect = element.getBoundingClientRect();
  const overlay = document.createElement('div');
  overlay.className = 'p12-layout-handles';
  overlay.dataset.p12LayoutHandles = '';
  overlay.style.left = `${elementRect.left - surfaceRect.left}px`;
  overlay.style.top = `${elementRect.top - surfaceRect.top}px`;
  overlay.style.width = `${elementRect.width}px`;
  overlay.style.height = `${elementRect.height}px`;
  for (const corner of ['nw', 'ne', 'se', 'sw']) {
    const handle = document.createElement('button');
    handle.type = 'button';
    handle.className = `p12-layout-resize p12-layout-resize-${corner}`;
    handle.setAttribute('aria-label', `Resize ${objectId} from ${corner}`);
    handle.addEventListener('pointerdown', (event) => beginP12ObjectResize(event, corner, item));
    overlay.append(handle);
  }
  surface.append(overlay);
}

function beginP12ObjectResize(event, corner, item) {
  if (event.button !== 0 || !active?.layoutDraft) return;
  event.preventDefault();
  event.stopPropagation();
  const svg = host.querySelector('[data-p10-collage-surface] > svg.p8-editable-svg');
  const element = findP10Object(item.objectId);
  const object = active.collage.scene.objects.find((record) => record.id === item.objectId);
  if (!svg || !element || !object) return;
  const point = svg.createSVGPoint();
  const toSvgPoint = (clientX, clientY) => {
    point.x = clientX;
    point.y = clientY;
    return point.matrixTransform(svg.getScreenCTM().inverse());
  };
  const start = toSvgPoint(event.clientX, event.clientY);
  const origin = { ...item.current };
  const move = (moveEvent) => {
    const current = toSvgPoint(moveEvent.clientX, moveEvent.clientY);
    const deltaX = current.x - start.x;
    const deltaY = current.y - start.y;
    const fromWest = corner.includes('w');
    const fromNorth = corner.includes('n');
    item.current = normalizeDraftTransform({
      ...origin,
      x: fromWest ? Math.min(origin.x + deltaX, origin.x + origin.width - 8) : origin.x,
      y: fromNorth ? Math.min(origin.y + deltaY, origin.y + origin.height - 8) : origin.y,
      width: Math.max(8, origin.width + (fromWest ? -deltaX : deltaX)),
      height: Math.max(8, origin.height + (fromNorth ? -deltaY : deltaY)),
    });
    previewObjectTransform(element, object, item.current);
    renderP12ResizeHandles();
  };
  const finish = () => {
    window.removeEventListener('pointermove', move);
    syncP12LayoutDraft();
  };
  window.addEventListener('pointermove', move);
  window.addEventListener('pointerup', finish, { once: true });
}

async function commitCollageOperations(operations) {
  const canvasState = active;
  if (!canvasState?.collage) return;
  if (canvasState.isBusy && !canvasState.applyingWidgetId) {
    callbacks.onError?.('Finish the current SVG interaction before editing the artifact directly.');
    return null;
  }
  const queuedPatch = (canvasState.patchQueue || Promise.resolve()).then(async () => {
    if (active !== canvasState || !canvasState.collage) return;
    return performCollageOperations(canvasState, operations);
  });
  canvasState.patchQueue = queuedPatch.catch(() => undefined);
  return queuedPatch;
}

async function performCollageOperations(canvasState, operations) {
  const collage = canvasState.collage;
  try {
    const patchUrl = `/api/sessions/${encodeURIComponent(canvasState.sessionId)}/svg-documents/${encodeURIComponent(collage.artifact.fileId)}/patch`;
    const sendPatch = (baseRevision) => fetch(patchUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ base_revision: baseRevision, operations }),
    });
    let response = await sendPatch(collage.scene.revision);
    if (response.status === 409) {
      const conflict = await response.text();
      const currentRevision = Number(conflict.match(/current revision is (\d+)/)?.[1]);
      if (!Number.isFinite(currentRevision)) throw new Error(conflict);
      response = await sendPatch(currentRevision);
    }
    if (!response.ok) throw new Error(await response.text());
    const data = await response.json();
    const attachment = data.attachment;
    if (active !== canvasState) return attachment;
    const index = canvasState.artifacts.findIndex((item) => item.fileId === attachment.fileId);
    if (index >= 0) canvasState.artifacts[index] = attachment;
    await render();
    callbacks.onArtifactPatch?.(attachment, operations);
    return attachment;
  } catch (error) {
    callbacks.onError?.(`Collage edit failed: ${error.message}`);
    await render();
    throw error;
  }
}

function numberField(name, value, min = '') {
  return `<label>${name}<input name="${name}" type="number" step="0.1" ${min === '' ? '' : `min="${min}"`} value="${Number(value) || 0}"></label>`;
}

function escapeMarkup(value) {
  return String(value || '').replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[character]);
}

function safeColorInput(value) {
  return /^#[0-9a-f]{6}$/i.test(String(value || '')) ? value : '#111111';
}

function createArtifactCard(artifact, index) {
  const card = document.createElement('article');
  card.className = 'artifact-card';
  card.dataset.fileId = artifact.fileId;
  const position = loadPosition(artifact.fileId) || defaultPosition(index);
  card.style.left = `${position.x}px`;
  card.style.top = `${position.y}px`;
  const preview = document.createElement('div');
  preview.className = 'artifact-preview';
  if (String(artifact.mime || '').startsWith('image/')) {
    const image = document.createElement('img');
    image.src = artifact.url || artifactUrl(artifact.fileId);
    image.alt = artifact.name || 'Uploaded artifact';
    preview.append(image);
  } else {
    const type = document.createElement('span');
    type.className = 'artifact-file-type';
    type.textContent = fileTypeLabel(artifact);
    preview.append(type);
  }
  const meta = document.createElement('div');
  meta.className = 'artifact-meta';
  const name = document.createElement('strong');
  name.textContent = artifact.name || 'Untitled artifact';
  const detail = document.createElement('span');
  detail.textContent = `${fileTypeLabel(artifact)} | ${formatBytes(artifact.size)}`;
  meta.append(name, detail);
  const open = document.createElement('a');
  open.className = 'artifact-open';
  open.href = artifact.url || artifactUrl(artifact.fileId);
  open.target = '_blank';
  open.rel = 'noopener';
  open.textContent = 'Open';
  open.addEventListener('pointerdown', (event) => event.stopPropagation());
  card.append(preview, meta, open);
  card.addEventListener('pointerdown', (event) => beginDrag(event, card, artifact.fileId));
  return card;
}

function beginDrag(event, card, fileId) {
  if (event.button !== 0 || event.target.closest('a, button')) return;
  event.preventDefault();
  card.setPointerCapture(event.pointerId);
  card.classList.add('dragging');
  const startX = event.clientX;
  const startY = event.clientY;
  const originX = parseFloat(card.style.left) || 0;
  const originY = parseFloat(card.style.top) || 0;
  const move = (moveEvent) => {
    card.style.left = `${Math.max(16, originX + (moveEvent.clientX - startX) / active.zoom)}px`;
    card.style.top = `${Math.max(16, originY + (moveEvent.clientY - startY) / active.zoom)}px`;
  };
  const finish = () => {
    card.classList.remove('dragging');
    card.removeEventListener('pointermove', move);
    card.removeEventListener('pointerup', finish);
    card.removeEventListener('pointercancel', finish);
    savePosition(fileId, parseFloat(card.style.left), parseFloat(card.style.top));
  };
  card.addEventListener('pointermove', move);
  card.addEventListener('pointerup', finish);
  card.addEventListener('pointercancel', finish);
}

function defaultPosition(index) {
  return { x: 32 + (index % 3) * 244, y: 32 + Math.floor(index / 3) * 236 };
}

function storageKey(fileId) {
  return `artifact-canvas:${active?.sessionId || 'draft'}:${active?.pluginId || 'unknown'}:${fileId}`;
}

function loadPosition(fileId) {
  try {
    return JSON.parse(localStorage.getItem(storageKey(fileId)) || 'null');
  } catch {
    return null;
  }
}

function savePosition(fileId, x, y) {
  localStorage.setItem(storageKey(fileId), JSON.stringify({ x, y }));
}

function setZoom(value) {
  if (!active) return;
  active.zoom = Math.min(1.5, Math.max(0.6, value));
  render();
}

function resetView() {
  if (!active) return;
  active.zoom = 1;
  for (const artifact of active.artifacts) localStorage.removeItem(storageKey(artifact.fileId));
  render();
}

function artifactUrl(fileId) {
  return `/api/sessions/${encodeURIComponent(active.sessionId)}/uploads/${encodeURIComponent(fileId)}`;
}

function fileTypeLabel(artifact) {
  const extension = String(artifact.name || '').split('.').pop();
  if (extension && extension !== artifact.name) return extension.toUpperCase();
  return String(artifact.mime || 'FILE').split('/').pop().toUpperCase();
}

function formatBytes(value) {
  const bytes = Number(value) || 0;
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}