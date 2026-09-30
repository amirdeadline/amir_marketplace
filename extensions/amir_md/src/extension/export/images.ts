// Local image lookup and size reading for export (FR-EXPORT-03, FR-EXPORT-04).

import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';

export type ImageKind = 'png' | 'jpg' | 'gif' | 'bmp' | 'svg' | 'webp';

const MIME: Record<ImageKind, string> = {
  png: 'image/png', jpg: 'image/jpeg', gif: 'image/gif', bmp: 'image/bmp', svg: 'image/svg+xml', webp: 'image/webp',
};

function safeDecode(s: string): string {
  try { return decodeURI(s); } catch { return s; }
}

/** Absolute path of a document image, or null when it is remote or missing. */
export function resolveLocalImage(src: string, docDir: string | null): string | null {
  const clean = src.trim().replace(/[?#].*$/, '');
  if (!clean) return null;
  if (/^file:/i.test(clean)) {
    try { return fs.existsSync(fileURLToPath(clean)) ? fileURLToPath(clean) : null; } catch { return null; }
  }
  if (/^[a-z][a-z0-9+.-]*:/i.test(clean) && !/^[a-z]:[\\/]/i.test(clean)) return null; // http:, data:, etc.
  for (const candidate of new Set([clean, safeDecode(clean)])) {
    const p = path.isAbsolute(candidate) ? candidate : docDir ? path.resolve(docDir, candidate) : null;
    if (p && fs.existsSync(p) && fs.statSync(p).isFile()) return p;
  }
  return null;
}

export function kindOf(file: string): ImageKind | null {
  const ext = path.extname(file).toLowerCase().slice(1);
  if (ext === 'jpeg' || ext === 'jpg') return 'jpg';
  return (['png', 'gif', 'bmp', 'svg', 'webp'] as const).find((k) => k === ext) ?? null;
}

export function dataUri(file: string): string | null {
  const kind = kindOf(file);
  if (!kind) return null;
  return `data:${MIME[kind]};base64,${fs.readFileSync(file).toString('base64')}`;
}

/** Pixel size of PNG, JPEG, GIF, and BMP data; null for anything else. */
export function imageSize(data: Buffer): { width: number; height: number } | null {
  if (data.length >= 24 && data.readUInt32BE(0) === 0x89504e47) {
    return { width: data.readUInt32BE(16), height: data.readUInt32BE(20) };
  }
  if (data.length >= 10 && data.toString('ascii', 0, 3) === 'GIF') {
    return { width: data.readUInt16LE(6), height: data.readUInt16LE(8) };
  }
  if (data.length >= 26 && data.toString('ascii', 0, 2) === 'BM') {
    return { width: Math.abs(data.readInt32LE(18)), height: Math.abs(data.readInt32LE(22)) };
  }
  if (data.length >= 4 && data[0] === 0xff && data[1] === 0xd8) {
    let i = 2;
    while (i + 9 < data.length) {
      if (data[i] !== 0xff) { i++; continue; }
      const marker = data[i + 1];
      const len = data.readUInt16BE(i + 2);
      const isSof = marker >= 0xc0 && marker <= 0xcf && marker !== 0xc4 && marker !== 0xc8 && marker !== 0xcc;
      if (isSof) return { height: data.readUInt16BE(i + 5), width: data.readUInt16BE(i + 7) };
      i += 2 + len;
    }
  }
  return null;
}

/** Remove YAML or TOML front matter; exports do not print it. */
export function stripFrontMatter(md: string): string {
  return md.replace(/^(?:---|\+\+\+)[ \t]*\r?\n[\s\S]*?\r?\n(?:---|\.\.\.|\+\+\+)[ \t]*(?:\r?\n|$)/, '');
}
