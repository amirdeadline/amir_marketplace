// Host adapter for the webview (SRS Appendix F). The VS Code webview API is the only
// host today; the Windows app will provide the same two functions.

import type { HostToWebview, WebviewToHost } from '../shared/messages';

interface VsCodeApi {
  postMessage(msg: unknown): void;
}

declare const acquireVsCodeApi: () => VsCodeApi;

const api = acquireVsCodeApi();

export const host = {
  post(msg: WebviewToHost): void {
    api.postMessage(msg);
  },
  onMessage(fn: (msg: HostToWebview) => void): void {
    window.addEventListener('message', (e: MessageEvent) => {
      const data = e.data as HostToWebview | undefined;
      if (data && typeof data === 'object' && typeof data.type === 'string') fn(data);
    });
  },
};
