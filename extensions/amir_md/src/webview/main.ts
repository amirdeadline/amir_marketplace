// Webview entry point: wait for the host's init message, then start the app.

import './style.css';
import { App } from './app';
import { host } from './host';
import type { HostToWebview } from '../shared/messages';

let app: App | null = null;
const early: HostToWebview[] = [];

host.onMessage((msg) => {
  if (msg.type === 'init') {
    if (app) return;
    const root = document.getElementById('app')!;
    void App.create(root, msg)
      .then((a) => {
        app = a;
        for (const m of early.splice(0)) app.handle(m);
      })
      .catch((err) => {
        root.textContent = `amir_md could not open this file: ${err instanceof Error ? err.message : String(err)}`;
        host.post({ type: 'log', level: 'error', message: err instanceof Error ? `${err.message}\n${err.stack ?? ''}` : String(err) });
      });
    return;
  }
  if (app) app.handle(msg);
  else early.push(msg);
});

host.post({ type: 'ready' });
