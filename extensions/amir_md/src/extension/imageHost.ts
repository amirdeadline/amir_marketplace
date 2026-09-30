// Host side of images: pick a file, save pasted images, and show images from other
// folders (FR-IMG-01 to 04, FR-IMG-08).

import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { config } from './settings';

const IMAGE_EXT = ['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'];
const MIME_EXT: Record<string, string> = {
  'image/png': 'png', 'image/jpeg': 'jpg', 'image/gif': 'gif', 'image/webp': 'webp', 'image/svg+xml': 'svg', 'image/bmp': 'bmp',
};
const MAX_PASTE_BYTES = 25 * 1024 * 1024;

export function docDir(doc: vscode.TextDocument): string | null {
  return doc.uri.scheme === 'file' ? path.dirname(doc.uri.fsPath) : null;
}

/** Relative path with forward slashes, or null when the file is on another drive. */
export function relativeImagePath(fromDir: string, file: string): string | null {
  const rel = path.relative(fromDir, file);
  if (!rel || path.isAbsolute(rel)) return null;
  return rel.split(path.sep).join('/');
}

function stamp(d = new Date()): string {
  const p = (n: number) => String(n).padStart(2, '0');
  return `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}-${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}`;
}

function uniqueFile(dir: string, base: string, ext: string): string {
  let file = path.join(dir, `${base}.${ext}`);
  for (let i = 2; fs.existsSync(file); i++) file = path.join(dir, `${base}-${i}.${ext}`);
  return file;
}

function imagesFolder(dir: string): string {
  const setting = config().get<string>('images.folder', 'images').trim() || 'images';
  const folder = path.resolve(dir, setting);
  fs.mkdirSync(folder, { recursive: true });
  return folder;
}

/** FR-IMG-01: choose an image; files outside the document folder are linked or copied. */
export async function pickImage(doc: vscode.TextDocument): Promise<string | null> {
  const dir = docDir(doc);
  if (!dir) {
    void vscode.window.showWarningMessage('Save the document first, so amir_md can link images relative to it.');
    return null;
  }
  const picked = await vscode.window.showOpenDialog({
    canSelectMany: false,
    defaultUri: vscode.Uri.file(dir),
    filters: { Images: IMAGE_EXT },
    openLabel: 'Insert Picture',
  });
  if (!picked?.length) return null;
  const file = picked[0].fsPath;
  const rel = relativeImagePath(dir, file);
  const inside = rel !== null && !rel.startsWith('../');
  if (inside) return rel;
  const choice = await vscode.window.showQuickPick(
    [
      ...(rel ? [{ label: 'Link with a relative path', description: rel, value: 'link' }] : []),
      { label: 'Copy into the images folder', description: config().get<string>('images.folder', 'images'), value: 'copy' },
    ],
    { placeHolder: 'The picture is outside the document folder.' },
  );
  if (!choice) return null;
  if (choice.value === 'link') return rel;
  const folder = imagesFolder(dir);
  const ext = path.extname(file).slice(1).toLowerCase();
  const target = uniqueFile(folder, path.basename(file, path.extname(file)), ext);
  fs.copyFileSync(file, target);
  return relativeImagePath(dir, target);
}

/** FR-IMG-03: save a pasted or dropped image next to the document. */
export function savePastedImage(doc: vscode.TextDocument, dataBase64: string, mime: string): string | null {
  const dir = docDir(doc);
  if (!dir) {
    void vscode.window.showWarningMessage('Save the document first, so amir_md has a folder for pasted images.');
    return null;
  }
  const ext = MIME_EXT[mime.toLowerCase()];
  if (!ext) {
    void vscode.window.showWarningMessage(`amir_md cannot save pasted images of type ${mime}.`);
    return null;
  }
  const data = Buffer.from(dataBase64, 'base64');
  if (!data.length || data.length > MAX_PASTE_BYTES) {
    void vscode.window.showWarningMessage('The pasted image is empty or larger than 25 MB.');
    return null;
  }
  const target = uniqueFile(imagesFolder(dir), `image-${stamp()}`, ext);
  fs.writeFileSync(target, data);
  return relativeImagePath(dir, target);
}

/** Absolute path for an image path written in the document, if the file exists. */
export function findImageFile(doc: vscode.TextDocument, src: string): string | null {
  const dir = docDir(doc);
  const clean = src.replace(/[?#].*$/, '');
  const decoded = (() => { try { return decodeURI(clean); } catch { return clean; } })();
  for (const c of new Set([clean, decoded])) {
    const p = path.isAbsolute(c) ? c : dir ? path.resolve(dir, c) : null;
    if (p && fs.existsSync(p) && fs.statSync(p).isFile()) return p;
  }
  return null;
}

export function isUnder(file: string, roots: readonly vscode.Uri[]): boolean {
  const f = path.resolve(file).toLowerCase();
  return roots.some((r) => {
    const root = path.resolve(r.fsPath).toLowerCase();
    return f === root || f.startsWith(root.endsWith(path.sep) ? root : root + path.sep);
  });
}
