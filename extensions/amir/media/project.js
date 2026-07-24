(function () {
  const vscode = acquireVsCodeApi();
  document.addEventListener('click', (e) => {
    const t = e.target;
    if (!(t instanceof HTMLElement)) return;
    const el = t.closest('[data-cmd]');
    if (!el) return;
    e.preventDefault();
    vscode.postMessage({
      command: el.getAttribute('data-cmd'),
      id: el.getAttribute('data-id') || undefined,
      approvalId: el.getAttribute('data-approval') || undefined,
    });
  });
})();
