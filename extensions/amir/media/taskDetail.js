(function () {
  const vscode = acquireVsCodeApi();
  document.addEventListener('click', (e) => {
    const t = e.target;
    if (!(t instanceof HTMLElement)) return;
    const cmd = t.getAttribute('data-cmd') || (t.closest('[data-cmd]') && t.closest('[data-cmd]').getAttribute('data-cmd'));
    if (!cmd) return;
    e.preventDefault();
    const el = t.closest('[data-cmd]') || t;
    vscode.postMessage({
      command: cmd,
      id: el.getAttribute('data-id') || undefined,
    });
  });
})();
