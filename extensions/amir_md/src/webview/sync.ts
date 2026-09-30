// Keeps the editor and the VS Code TextDocument in step (SRS FR-SAVE-01, 05 to 08).
//
// `base` is the document text as the host last confirmed it, at `version`.
// Local edits are serialized, diffed against `base`, and sent as one range
// replacement. Only one edit is in flight at a time. If the host rejects an edit
// because the file changed first, our change is replayed on top of the new text
// when the two changes do not touch; otherwise the editor reloads from the file.

import type { Node } from 'prosemirror-model';
import { computeChange, serializeDocument, CodecMeta } from './codec/document';
import type { TextChange, WebviewToHost } from '../shared/messages';

export interface SyncDeps {
  post(msg: WebviewToHost): void;
  doc(): Node;
  meta(): CodecMeta;
  /** Replace the editor content so it matches `text`, without adding an undo step. */
  load(text: string): void;
  notify(message: string): void;
  debounceMs?: number;
}

function disjoint(a: TextChange, b: TextChange): boolean {
  return a.end < b.start || b.end < a.start;
}

/** Replay change `a` (made against the same base as `b`) on text that already has `b`. */
export function replay(theirs: string, a: TextChange, b: TextChange): string {
  if (a.end < b.start) return theirs.slice(0, a.start) + a.text + theirs.slice(a.end);
  const shift = b.text.length - (b.end - b.start);
  return theirs.slice(0, a.start + shift) + a.text + theirs.slice(a.end + shift);
}

export class DocSync {
  private inFlight: string | null = null;
  private dirty = false;
  private timer: ReturnType<typeof setTimeout> | null = null;
  private queued: { text: string; version: number } | null = null;
  private flushWaiters = 0;

  constructor(private readonly deps: SyncDeps, public base: string, public version: number) {}

  /** Call after every local document change. */
  changed(): void {
    this.dirty = true;
    if (this.timer) clearTimeout(this.timer);
    this.timer = setTimeout(() => this.flush(), this.deps.debounceMs ?? 150);
  }

  /** Send pending edits now; the host is told when everything has been applied. */
  flushNow(): void {
    this.flushWaiters++;
    this.flush();
    this.settle();
  }

  private settle(): void {
    if (this.flushWaiters && !this.inFlight && !this.dirty) {
      this.flushWaiters = 0;
      this.deps.post({ type: 'flushed' });
    }
  }

  current(): string {
    return serializeDocument(this.deps.doc(), this.deps.meta());
  }

  flush(): void {
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }
    if (this.inFlight !== null) return; // sent again after the result arrives
    this.dirty = false;
    const text = this.current();
    const change = computeChange(this.base, text);
    if (!change) return;
    this.inFlight = text;
    this.deps.post({ type: 'edit', baseVersion: this.version, changes: [change] });
  }

  editResult(ok: boolean, version: number, text?: string): void {
    const sent = this.inFlight;
    this.inFlight = null;
    if (ok && sent !== null) {
      this.base = sent;
      this.version = version;
    } else if (!ok && text !== undefined) {
      const ours = this.dirty ? this.current() : sent ?? this.current();
      this.rebase(ours, text, version);
    }
    const q = this.queued;
    this.queued = null;
    if (q) this.external(q.text, q.version);
    if (this.dirty) this.flush();
    this.settle();
  }

  /** A change made outside amir_md (text editor, Git, undo in the text editor). */
  external(text: string, version: number): void {
    if (this.inFlight !== null) {
      this.queued = { text, version };
      return;
    }
    if (version <= this.version && text === this.base) return;
    const ours = this.current();
    if (ours === this.base) {
      this.base = text;
      this.version = version;
      if (text !== ours) this.deps.load(text);
      return;
    }
    this.rebase(ours, text, version);
    if (this.dirty) this.flush();
  }

  private rebase(ours: string, theirs: string, version: number): void {
    const base = this.base;
    this.base = theirs;
    this.version = version;
    const a = computeChange(base, ours);
    const b = computeChange(base, theirs);
    if (!a) {
      this.deps.load(theirs);
      this.dirty = false;
      return;
    }
    if (!b) {
      this.dirty = true; // the host still has the old text; send our change again
      return;
    }
    if (!disjoint(a, b)) {
      this.deps.load(theirs);
      this.dirty = false;
      this.deps.notify('The file changed outside amir_md while you were editing the same place. Your last edit was not applied.');
      return;
    }
    this.deps.load(replay(theirs, a, b));
    this.dirty = true;
  }
}
