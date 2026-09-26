(function () {
  const form = document.querySelector('.iic');
  if (!form) return;
  const choices = Array.from(form.querySelectorAll('[data-iic-choice]'));
  const revision = form.querySelector('.iic-revision');
  const revisionInput = form.querySelector('[data-iic-revision]');
  const note = form.querySelector('[data-iic-note]');
  const error = form.querySelector('[data-iic-error]');
  const compare = form.querySelector('[data-iic-compare]');
  const range = form.querySelector('[data-iic-range]');
  let decision = 'after';
  function noteValue() { return note ? note.value.trim() : ''; }
  function setComparePosition(value) {
    const position = Math.max(0, Math.min(100, Number(value) || 0));
    compare.style.setProperty('--iic-compare-position', position + '%');
    range.value = String(position);
    range.setAttribute('aria-valuetext', position + ' percent inpaint result visible');
  }
  function positionFromPointer(event) {
    const rect = compare.getBoundingClientRect();
    return ((event.clientX - rect.left) / Math.max(1, rect.width)) * 100;
  }
  function choose(value) {
    decision = value;
    choices.forEach((button) => {
      const active = button.dataset.iicChoice === value;
      button.classList.toggle('selected', active);
      button.setAttribute('aria-pressed', active ? 'true' : 'false');
    });
    revision.hidden = value !== 'none';
    error.hidden = true;
  }
  choices.forEach((button) => button.addEventListener('click', () => choose(button.dataset.iicChoice)));
  form.querySelectorAll('img[data-iic-before-file-id], img[data-iic-after-file-id]').forEach((image) => {
    const fileId = image.dataset.iicBeforeFileId || image.dataset.iicAfterFileId || '';
    if (fileId) image.src = window.widgetAssetUrl(fileId);
  });
  range.addEventListener('input', () => setComparePosition(range.value));
  compare.addEventListener('pointerdown', (event) => {
    if (event.target === range) return;
    compare.setPointerCapture(event.pointerId);
    setComparePosition(positionFromPointer(event));
  });
  compare.addEventListener('pointermove', (event) => {
    if (compare.hasPointerCapture(event.pointerId)) setComparePosition(positionFromPointer(event));
  });
  function finishComparePointer(event) {
    if (compare.hasPointerCapture(event.pointerId)) compare.releasePointerCapture(event.pointerId);
  }
  compare.addEventListener('pointerup', finishComparePointer);
  compare.addEventListener('pointercancel', finishComparePointer);
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const request = decision === 'none' ? revisionInput.value.trim() : '';
    if (decision === 'none' && !request) { error.textContent = 'Describe the revision you want.'; error.hidden = false; revisionInput.focus(); return; }
    window.submitWidget({ accepted_version: decision, revision_request: request, freeform_note: noteValue() });
  });
  form.querySelector('[data-iic-dismiss]').addEventListener('click', () => window.dismissWidget(noteValue()));
  setComparePosition(range.value);
  choose('after');
})();