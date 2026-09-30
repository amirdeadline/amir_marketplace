// Export commands: Markdown, HTML, PDF, and Word (FR-EXPORT-01 to 08).

import * as vscode from 'vscode';
import * as fs from 'fs';
import * as os from 'os';
import * as path from 'path';
import { execFile } from 'child_process';
import type { ExportFormat } from '../shared/messages';
import { renderHtml } from './export/html';
import { findBrowser, printPdf } from './export/pdf';
import { buildDocx } from './export/docx';
import { readExportSettings, SECTION } from './settings';

const LABEL: Record<ExportFormat, string> = { pdf: 'PDF', docx: 'Word', html: 'HTML', md: 'Markdown' };
const FILTER: Record<ExportFormat, Record<string, string[]>> = {
  pdf: { PDF: ['pdf'] },
  docx: { 'Word document': ['docx'] },
  html: { 'Web page': ['html'] },
  md: { Markdown: ['md', 'markdown'] },
};

export interface ExportResult {
  ok: boolean;
  path?: string;
  error?: string;
}

function docDirOf(doc: vscode.TextDocument): string | null {
  return doc.uri.scheme === 'file' ? path.dirname(doc.uri.fsPath) : null;
}

function titleOf(doc: vscode.TextDocument): string {
  return path.basename(doc.uri.path).replace(/\.(md|markdown)$/i, '');
}

function runPandoc(pandoc: string, input: string, output: string, cwd: string | null, token: vscode.CancellationToken): Promise<void> {
  return new Promise((resolve, reject) => {
    const tmp = path.join(os.tmpdir(), `amir-md-${Date.now()}.md`);
    fs.writeFileSync(tmp, input, 'utf8');
    const child = execFile(pandoc || 'pandoc', [tmp, '-f', 'markdown+raw_html', '-o', output, '--standalone'], { cwd: cwd ?? undefined, timeout: 120_000 }, (err, _out, stderr) => {
      fs.rmSync(tmp, { force: true });
      if (err) reject(new Error(stderr?.trim() || err.message));
      else resolve();
    });
    token.onCancellationRequested(() => child.kill());
  });
}

async function noBrowser(): Promise<'html' | null> {
  const choice = await vscode.window.showErrorMessage(
    'amir_md could not find Microsoft Edge or Google Chrome to create the PDF.',
    'Set Browser Path', 'Use Pandoc', 'Export HTML Instead',
  );
  if (choice === 'Set Browser Path') await vscode.commands.executeCommand('workbench.action.openSettings', `${SECTION}.export.browserPath`);
  if (choice === 'Use Pandoc') await vscode.commands.executeCommand('workbench.action.openSettings', `${SECTION}.export.engine`);
  return choice === 'Export HTML Instead' ? 'html' : null;
}

/** Ask for a target file and export the document text (unsaved edits included, folds ignored). */
export async function exportDocument(doc: vscode.TextDocument, format: ExportFormat, log: vscode.OutputChannel): Promise<ExportResult> {
  const s = readExportSettings();
  const docDir = docDirOf(doc);
  const title = titleOf(doc);
  const ext = format === 'md' ? 'md' : format;
  const defaultUri = docDir ? vscode.Uri.file(path.join(docDir, `${title}${format === 'md' ? ' copy' : ''}.${ext}`)) : undefined;

  let fmt = format;
  let browser: string | null = null;
  if (fmt === 'pdf' && s.engine === 'builtin') {
    browser = findBrowser(s.browserPath);
    if (!browser) {
      const alt = await noBrowser();
      if (!alt) return { ok: false, error: 'No browser for PDF export.' };
      fmt = alt;
    }
  }

  const target = await vscode.window.showSaveDialog({ defaultUri, filters: FILTER[fmt], saveLabel: `Export ${LABEL[fmt]}` });
  if (!target) return { ok: false, error: 'Cancelled.' };
  const out = target.fsPath;
  const text = doc.getText();
  const pageOpts = { title, docDir, pageSize: s.pageSize, marginMm: s.marginMm, pageNumbers: s.pageNumbers };

  try {
    const notes = await vscode.window.withProgress(
      { location: vscode.ProgressLocation.Notification, title: `amir_md: exporting to ${LABEL[fmt]}`, cancellable: true },
      async (_progress, token): Promise<string[]> => {
        const messages: string[] = [];
        const usePandoc = s.engine === 'pandoc' && (fmt === 'pdf' || fmt === 'docx');
        if (usePandoc) {
          if (!vscode.workspace.isTrusted) throw new Error('Pandoc does not run in an untrusted workspace.');
          await runPandoc(s.pandocPath, text, out, docDir, token);
          return messages;
        }
        switch (fmt) {
          case 'md':
            fs.writeFileSync(out, text, 'utf8');
            break;
          case 'html': {
            const r = renderHtml(text, pageOpts);
            fs.writeFileSync(out, r.html, 'utf8');
            if (r.missingImages.length) messages.push(`${r.missingImages.length} image(s) could not be found.`);
            break;
          }
          case 'pdf': {
            const r = renderHtml(text, pageOpts);
            await printPdf(browser!, r.html, out, token);
            if (r.missingImages.length) messages.push(`${r.missingImages.length} image(s) could not be found.`);
            break;
          }
          case 'docx': {
            const r = await buildDocx(text, pageOpts);
            if (token.isCancellationRequested) throw new Error('Export cancelled.');
            fs.writeFileSync(out, r.buffer);
            if (r.sourceBlocks) messages.push(`${r.sourceBlocks} source block(s) were written as plain text.`);
            if (r.missingImages.length) messages.push(`${r.missingImages.length} image(s) could not be found.`);
            break;
          }
        }
        return messages;
      },
    );
    log.appendLine(`[export] ${LABEL[fmt]} -> ${out}${notes.length ? ` (${notes.join(' ')})` : ''}`);
    const open = format === 'md' ? 'Open in amir_md' : 'Open';
    void vscode.window.showInformationMessage(`Exported ${path.basename(out)}. ${notes.join(' ')}`.trim(), open, 'Reveal in File Explorer').then((choice) => {
      if (choice === 'Open in amir_md') void vscode.commands.executeCommand('vscode.openWith', target, 'amir_md.editor');
      else if (choice === 'Open') void vscode.env.openExternal(target);
      else if (choice === 'Reveal in File Explorer') void vscode.commands.executeCommand('revealFileInOS', target);
    });
    return { ok: true, path: out };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    log.appendLine(`[export] ${LABEL[fmt]} failed: ${msg}`);
    void vscode.window.showErrorMessage(`amir_md export failed: ${msg}`);
    return { ok: false, error: msg };
  }
}
