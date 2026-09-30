// amir_md extension entry point: registers the custom editor and its commands.

import * as vscode from 'vscode';
import { AmirMdEditorProvider, VIEW_TYPE } from './provider';
import { config, SECTION } from './settings';
import type { ExportFormat } from '../shared/messages';

const ASSOCIATION = '*.md';

function markdownUri(arg: unknown): vscode.Uri | undefined {
  if (arg instanceof vscode.Uri) return arg;
  const doc = vscode.window.activeTextEditor?.document;
  return doc && /\.(md|markdown)$/i.test(doc.uri.path) ? doc.uri : undefined;
}

/** FR-OPEN-03: make amir_md the default editor for .md files after the user confirms. */
async function syncDefaultEditor(): Promise<void> {
  const wb = vscode.workspace.getConfiguration('workbench');
  const assoc = { ...(wb.get<Record<string, string>>('editorAssociations') ?? {}) };
  const want = config().get<boolean>('defaultEditor', false);
  if (want && assoc[ASSOCIATION] !== VIEW_TYPE) {
    const ok = await vscode.window.showInformationMessage(
      'Open all .md files in amir_md by default? This sets workbench.editorAssociations in your user settings.',
      { modal: true }, 'Yes',
    );
    if (ok !== 'Yes') {
      await config().update('defaultEditor', false, vscode.ConfigurationTarget.Global);
      return;
    }
    assoc[ASSOCIATION] = VIEW_TYPE;
    await wb.update('editorAssociations', assoc, vscode.ConfigurationTarget.Global);
  } else if (!want && assoc[ASSOCIATION] === VIEW_TYPE) {
    delete assoc[ASSOCIATION];
    await wb.update('editorAssociations', assoc, vscode.ConfigurationTarget.Global);
  }
}

export function activate(ctx: vscode.ExtensionContext): void {
  const log = vscode.window.createOutputChannel('amir_md');
  const provider = new AmirMdEditorProvider(ctx, log);

  const withSession = (fn: (s: NonNullable<AmirMdEditorProvider['activeSession']>) => unknown) => () => {
    const s = provider.activeSession;
    if (!s) {
      void vscode.window.showInformationMessage('Open a Markdown file in amir_md first.');
      return;
    }
    return fn(s);
  };
  const exportCmd = (format: ExportFormat) => withSession((s) => s.export(format));

  ctx.subscriptions.push(
    log,
    vscode.window.registerCustomEditorProvider(VIEW_TYPE, provider, {
      webviewOptions: { retainContextWhenHidden: true, enableFindWidget: true },
      supportsMultipleEditorsPerDocument: false,
    }),
    vscode.commands.registerCommand('amir_md.openWith', async (arg?: unknown) => {
      const uri = markdownUri(arg);
      if (!uri) {
        void vscode.window.showInformationMessage('Select a Markdown file to open in amir_md.');
        return;
      }
      await vscode.commands.executeCommand('vscode.openWith', uri, VIEW_TYPE);
    }),
    vscode.commands.registerCommand('amir_md.openAsText', withSession((s) =>
      vscode.commands.executeCommand('vscode.openWith', s.document.uri, 'default', vscode.ViewColumn.Beside))),
    vscode.commands.registerCommand('amir_md.exportPdf', exportCmd('pdf')),
    vscode.commands.registerCommand('amir_md.exportDocx', exportCmd('docx')),
    vscode.commands.registerCommand('amir_md.exportHtml', exportCmd('html')),
    vscode.commands.registerCommand('amir_md.saveAsMarkdown', exportCmd('md')),
    vscode.commands.registerCommand('amir_md.toggleNavPane', withSession((s) => s.post({ type: 'command', name: 'toggleNav' }))),
    vscode.commands.registerCommand('amir_md.expandAllHeadings', withSession((s) => s.post({ type: 'command', name: 'expandAll' }))),
    vscode.commands.registerCommand('amir_md.collapseAllHeadings', withSession((s) => s.post({ type: 'command', name: 'collapseAll' }))),
    // Holds amir_md's shortcuts so VS Code's defaults (Ctrl+B sidebar, Ctrl+K chords) do not also run.
    vscode.commands.registerCommand('amir_md.noop', () => undefined),
    vscode.workspace.onDidChangeConfiguration((e) => {
      if (e.affectsConfiguration(`${SECTION}.defaultEditor`)) void syncDefaultEditor();
    }),
  );
}

export function deactivate(): void {
  // nothing to clean up; subscriptions are disposed by VS Code
}
