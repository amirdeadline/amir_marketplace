// Fast heading outline from raw Markdown (no markdown-it / ProseMirror).
// Used for the navigation pane on large documents where a full doc walk is too costly.

export interface ScannedHeading {
  level: number;
  text: string;
  /** Byte offset in the source string where the heading line starts. */
  offset: number;
  key: string;
}

const ATX = /^(#{1,6})(?:\s|$)(.*)$/;

/** Scan ATX headings, skipping fenced code blocks. */
export function scanHeadings(text: string): ScannedHeading[] {
  const out: ScannedHeading[] = [];
  const seen = new Map<string, number>();
  let inFence: string | null = null;
  const re = /[^\n]*(?:\n|$)/g;
  let m: RegExpExecArray | null;
  let offset = 0;
  while ((m = re.exec(text))) {
    const line = m[0];
    const lineStart = offset;
    offset += line.length;
    const content = line.replace(/\r?\n$/, '');

    const fence = content.match(/^(`{3,}|~{3,})(.*)$/);
    if (fence) {
      const open = fence[1];
      if (inFence === open) inFence = null;
      else if (!inFence) inFence = open;
      continue;
    }
    if (inFence) continue;

    const trimmed = content.trimStart();
    const lead = content.length - trimmed.length;
    const hm = ATX.exec(trimmed);
    if (!hm) continue;
    const level = hm[1].length;
    const raw = hm[2].replace(/\s+#+\s*$/, '').trim();
    const textClean = raw.replace(/\s+/g, ' ').trim();
    const base = `${level}|${textClean}`;
    const n = seen.get(base) ?? 0;
    seen.set(base, n + 1);
    out.push({ level, text: textClean, offset: lineStart + lead, key: `${base}|${n}` });
  }
  return out;
}
