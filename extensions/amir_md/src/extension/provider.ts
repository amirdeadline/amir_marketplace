// The amir_md custom text editor (SRS FR-OPEN, FR-SAVE). The TextDocument stays the
// source of truth: the webview sends range replacements, the host applies them as
// WorkspaceEdits, and VS Code handles save, dirty state, revert, and hot exit.

import * as vscode from 'vscode';
import * as crypto from 'crypto';
import * as path from 'path';
import type { ExportFormat, HostToWebview, TextChange, ViewState, WebviewToHost } from '../shared/messages';
import { readSettings, SECTION, config } from './settings';
import { exportDocument } from './exporter';
import { docDir, findImageFile, isUnder, pickImage, savePastedImage } from './imageHost';

export const VIEW_TYPE = 'amir_md.editor';
const EXTERNAL_DEBOUNCE_MS = 100;
const FLUSH_TIMEOUT_MS = 1500;

function applyChanges(text: string, changes: readonly TextChange[]): string {
  let out = text;
  for (const c of [...changes].sort((a, b) => b.start - a.start)) out = out.slice(0, c.start) + c.text + out.slice(c.end);
  return out;
}

function eolOf(doc: vscode.TextDocument): '\n' | '\r\n' {
  return doc.eol === vscode.EndOfLine.CRLF ? '\r\n' : '\n';
}

class Session implements vscode.Disposable {
  private disposables: vscode.Disposable[] = [];
  private applying = 0;
  private externalTimer: ReturnType<typeof setTimeout> | null = null;
  private flushWaiters: (() => void)[] = [];
  private roots: vscode.Uri[];
  private askedFolders = new Set<string>();

  constructor(
    private readonly ctx: vscode.ExtensionContext,
    readonly document: vscode.TextDocument,
    readonly panel: vscode.WebviewPanel,
    private readonly log: vscode.OutputChannel,
    private readonly onActive: (s: Session | null) => void,
  ) {
    const dir = docDir(document);
    this.roots = [
      vscode.Uri.joinPath(ctx.extensionUri, 'dist'),
      ...(dir ? [vscode.Uri.file(dir)] : []),
      ...(vscode.workspace.workspaceFolders?.map((f) => f.uri) ?? []),
    ];
    panel.webview.options = { enableScripts: true, localResourceRoots: this.roots };
    panel.webview.html = this.html();

    this.disposables.push(
      panel.webview.onDidReceiveMessage((m: WebviewToHost) => this.onMessage(m)),
      vscode.workspace.onDidChangeTextDocument((e) => {
        if (e.document.uri.toString() !== document.uri.toString() || !e.contentChanges.length) return;
        if (this.applying > 0) return; // our own edit
        this.scheduleExternal();
      }),
      vscode.workspace.onWillSaveTextDocument((e) => {
        if (e.document.uri.toString() === document.uri.toString()) e.waitUntil(this.flush());
      }),
      vscode.workspace.onDidChangeConfiguration((e) => {
        if (e.affectsConfiguration(SECTION)) this.post({ type: 'settings', settings: readSettings() });
      }),
      panel.onDidChangeViewState((e) => { if (e.webviewPanel.active) this.onActive(this); }),
    );
    if (panel.active) this.onActive(this);
  }

  private get stateKey(): string {
    return `amir_md.view:${this.document.uri.toString()}`;
  }

  post(msg: HostToWebview): void {
    void this.panel.webview.postMessage(msg);
  }

  private html(): string {
    const w = this.panel.webview;
    const nonce = crypto.randomBytes(16).toString('base64');
    const js = w.asWebviewUri(vscode.Uri.joinPath(this.ctx.extensionUri, 'dist', 'webview.js'));
    const css = w.asWebviewUri(vscode.Uri.joinPath(this.ctx.extensionUri, 'dist', 'webview.css'));
    const csp = [
      "default-src 'none'",
      `img-src ${w.cspSource} https: data: blob:`,
      `style-src ${w.cspSource} 'unsafe-inline'`,
      `font-src ${w.cspSource}`,
      `script-src 'nonce-${nonce}'`,
    ].join('; ');
    const name = path.basename(this.document.uri.path).replace(/[<>&"]/g, '');
    return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="Content-Security-Policy" content="${csp}">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="${css}" rel="stylesheet">
<title>amir_md</title>
</head>
<body>
<div id="app"><div class="amd-loading">Opening ${name}...</div></div>
<script nonce="${nonce}" src="${js}"></script>
</body>
</html>`;
  }

  // ---------------------------------------------------------------- sync

  private sendInit(): void {
    const dir = docDir(this.document);
    const base = dir ? `${this.panel.webview.asWebviewUri(vscode.Uri.file(dir)).toString()}/` : 'about:blank';
    this.post({
      type: 'init',
      text: this.document.getText(),
      version: this.document.version,
      eol: eolOf(this.document),
      fileName: path.basename(this.document.uri.path),
      baseUri: base,
      settings: readSettings(),
      viewState: this.ctx.workspaceState.get<ViewState>(this.stateKey) ?? null,
    });
  }

  private scheduleExternal(): void {
    if (this.externalTimer) clearTimeout(this.externalTimer);
    this.externalTimer = setTimeout(() => {
      this.externalTimer = null;
      this.post({ type: 'externalChange', text: this.document.getText(), version: this.document.version });
    }, EXTERNAL_DEBOUNCE_MS);
  }

  /** FR-SAVE-07: apply an edit only if the document is still at the version it was based on. */
  private async applyEdit(baseVersion: number, changes: TextChange[]): Promise<void> {
    const doc = this.document;
    if (doc.version !== baseVersion) {
      this.post({ type: 'editResult', ok: false, version: doc.version, text: doc.getText() });
      return;
    }
    const expected = applyChanges(doc.getText(), changes);
    const edit = new vscode.WorkspaceEdit();
    for (const c of changes) edit.replace(doc.uri, new vscode.Range(doc.positionAt(c.start), doc.positionAt(c.end)), c.text);
    this.applying++;
    let ok = false;
    try {
      ok = await vscode.workspace.applyEdit(edit);
    } catch (err) {
      this.log.appendLine(`[edit] applyEdit failed: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      this.applying--;
    }
    if (!ok) {
      this.post({ type: 'editResult', ok: false, version: doc.version, text: doc.getText() });
      return;
    }
    this.post({ type: 'editResult', ok: true, version: doc.version });
    // VS Code may normalize line endings; if the text differs, the webview reloads it.
    if (doc.getText() !== expected) this.post({ type: 'externalChange', text: doc.getText(), version: doc.version });
  }

  /** Ask the webview to send pending edits; resolves when it reports they are applied. */
  flush(): Promise<void> {
    return new Promise((resolve) => {
      const timer = setTimeout(() => {
        this.flushWaiters = this.flushWaiters.filter((w) => w !== done);
        resolve();
      }, FLUSH_TIMEOUT_MS);
      const done = () => { clearTimeout(timer); resolve(); };
      this.flushWaiters.push(done);
      this.post({ type: 'command', name: 'flush' });
    });
  }

  // ---------------------------------------------------------------- messages

  private async onMessage(m: WebviewToHost): Promise<void> {
    switch (m.type) {
      case 'ready':
        this.sendInit();
        break;
      case 'edit':
        await this.applyEdit(m.baseVersion, m.changes);
        break;
      case 'flushed':
        for (const w of this.flushWaiters.splice(0)) w();
        break;
      case 'saveViewState':
        await this.ctx.workspaceState.update(this.stateKey, m.state);
        break;
      case 'pickImage': {
        const p = await pickImage(this.document);
        this.post({ type: 'imageInserted', requestId: m.requestId, path: p });
        break;
      }
      case 'saveImage': {
        let p: string | null = null;
        try {
          p = savePastedImage(this.document, m.dataBase64, m.mime);
        } catch (err) {
          void vscode.window.showErrorMessage(`amir_md could not save the image: ${err instanceof Error ? err.message : String(err)}`);
        }
        this.post({ type: 'imageInserted', requestId: m.requestId, path: p });
        break;
      }
      case 'resolveResources':
        this.post({ type: 'resources', map: await this.resolveResources(m.paths) });
        break;
      case 'openLink':
        await this.openLink(m.href);
        break;
      case 'export':
        await this.export(m.format);
        break;
      case 'log':
        this.log.appendLine(`[webview ${m.level}] ${m.message}`);
        break;
      default:
        break;
    }
  }

  async export(format: ExportFormat): Promise<void> {
    await this.flush();
    const r = await exportDocument(this.document, format, this.log);
    this.post({ type: 'exportDone', ...r });
  }

  /** FR-IMG-02: images outside the allowed folders are shown after the user agrees. */
  private async resolveResources(paths: string[]): Promise<Record<string, string | null>> {
    const map: Record<string, string | null> = {};
    for (const src of paths) {
      const file = findImageFile(this.document, src);
      if (!file) { map[src] = null; continue; }
      if (!isUnder(file, this.roots)) {
        const folder = path.dirname(file);
        if (this.askedFolders.has(folder)) { map[src] = null; continue; }
        this.askedFolders.add(folder);
        const ok = await vscode.window.showInformationMessage(
          `This document shows images from ${folder}, which is outside the workspace. Allow amir_md to show them?`,
          'Allow', 'Not Now',
        );
        if (ok !== 'Allow') { map[src] = null; continue; }
        this.roots.push(vscode.Uri.file(folder));
        this.panel.webview.options = { enableScripts: true, localResourceRoots: this.roots };
      }
      map[src] = this.panel.webview.asWebviewUri(vscode.Uri.file(file)).toString();
    }
    return map;
  }

  /** FR-LINK-04 and 05: open web links outside VS Code and relative files inside it. */
  private async openLink(href: string): Promise<void> {
    const h = href.trim();
    if (/^(https?|mailto):/i.test(h)) {
      await vscode.env.openExternal(vscode.Uri.parse(h));
      return;
    }
    if (/^[a-z][a-z0-9+.-]*:/i.test(h) && !/^[a-z]:[\\/]/i.test(h)) {
      void vscode.window.showWarningMessage(`amir_md does not open ${h.split(':')[0]}: links.`);
      return;
    }
    const dir = docDir(this.document);
    const file = h.replace(/#.*$/, '');
    const decoded = (() => { try { return decodeURI(file); } catch { return file; } })();
    const abs = path.isAbsolute(decoded) ? decoded : dir ? path.resolve(dir, decoded) : null;
    if (!abs) return;
    const uri = vscode.Uri.file(abs);
    try {
      await vscode.workspace.fs.stat(uri);
    } catch {
      void vscode.window.showWarningMessage(`File not found: ${decoded}`);
      return;
    }
    if (/\.(md|markdown)$/i.test(abs)) await vscode.commands.executeCommand('vscode.openWith', uri, VIEW_TYPE);
    else await vscode.commands.executeCommand('vscode.open', uri);
  }

  dispose(): void {
    if (this.externalTimer) clearTimeout(this.externalTimer);
    for (const w of this.flushWaiters.splice(0)) w();
    for (const d of this.disposables) d.dispose();
    this.onActive(null);
  }
}

export class AmirMdEditorProvider implements vscode.CustomTextEditorProvider {
  private active: Session | null = null;

  constructor(private readonly ctx: vscode.ExtensionContext, private readonly log: vscode.OutputChannel) {}

  get activeSession(): Session | null {
    return this.active;
  }

  async resolveCustomTextEditor(document: vscode.TextDocument, panel: vscode.WebviewPanel): Promise<void> {
    // FR-OPEN-05: warn before opening very large files.
    const limitMb = config().get<number>('maxFileSizeMB', 5);
    const sizeMb = Buffer.byteLength(document.getText(), 'utf8') / (1024 * 1024);
    if (limitMb > 0 && sizeMb > limitMb) {
      const choice = await vscode.window.showWarningMessage(
        `${path.basename(document.uri.path)} is ${sizeMb.toFixed(1)} MB, larger than the amir_md limit of ${limitMb} MB. Editing may be slow.`,
        { modal: true }, 'Open Anyway', 'Open in Text Editor',
      );
      if (choice !== 'Open Anyway') {
        panel.dispose();
        if (choice === 'Open in Text Editor') await vscode.commands.executeCommand('vscode.openWith', document.uri, 'default');
        return;
      }
    }
    const session = new Session(this.ctx, document, panel, this.log, (s) => {
      if (s) this.active = s;
      else if (this.active === session) this.active = null;
    });
    panel.onDidDispose(() => session.dispose());
  }
}
