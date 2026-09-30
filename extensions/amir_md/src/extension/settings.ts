// amir_md settings (FR-SET-01).

import * as vscode from 'vscode';
import type { Settings } from '../shared/messages';

export const SECTION = 'amir_md';

export function config(): vscode.WorkspaceConfiguration {
  return vscode.workspace.getConfiguration(SECTION);
}

export function readSettings(): Settings {
  const c = config();
  return {
    fontFamilies: c.get<string[]>('editor.fontFamilies', []),
    defaultFontFamily: c.get<string>('editor.defaultFontFamily', ''),
    defaultFontSize: c.get<number>('editor.defaultFontSize', 11),
    palette: c.get<string[]>('colors.palette', []),
    foldRemember: c.get<boolean>('fold.remember', true),
    navDefaultExpandLevel: c.get<number>('nav.defaultExpandLevel', 2),
    navWidth: c.get<number>('nav.width', 300),
    bulletMarker: c.get<string>('markdown.bulletMarker', '-'),
    emphasisMarker: c.get<string>('markdown.emphasisMarker', '*'),
    strongMarker: c.get<string>('markdown.strongMarker', '**'),
    // Untrusted workspaces never load remote images.
    allowRemoteImages: c.get<boolean>('images.allowRemote', true) && vscode.workspace.isTrusted,
  };
}

export interface ExportSettings {
  engine: 'builtin' | 'pandoc';
  browserPath: string;
  pandocPath: string;
  pageSize: 'Letter' | 'A4';
  marginMm: number;
  pageNumbers: boolean;
}

export function readExportSettings(): ExportSettings {
  const c = config();
  return {
    engine: c.get<'builtin' | 'pandoc'>('export.engine', 'builtin'),
    browserPath: c.get<string>('export.browserPath', ''),
    pandocPath: c.get<string>('export.pandocPath', ''),
    pageSize: c.get<'Letter' | 'A4'>('export.pdf.pageSize', 'Letter'),
    marginMm: c.get<number>('export.pdf.marginMm', 20),
    pageNumbers: c.get<boolean>('export.pdf.pageNumbers', true),
  };
}
