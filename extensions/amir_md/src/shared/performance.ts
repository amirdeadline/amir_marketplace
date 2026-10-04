// Document size tiers and parse scheduling (soft limits only — VS Code cannot cgroup the host).

export interface DocumentProfile {
  bytes: number;
  lines: number;
  /** Skip per-block HTML fidelity checks (largest parse win on big files). */
  skipFidelityCheck: boolean;
  /** Build navigation from a line scan instead of walking the ProseMirror tree. */
  navFromScan: boolean;
  /** Blocks processed before yielding to the event loop. */
  blocksPerTick: number;
  outlineDebounceMs: number;
  /** Cap DOM nodes in the nav tree; extra headings stay reachable via filter. */
  navDomCap: number;
}

const MB = 1024 * 1024;

export function profileDocument(text: string): DocumentProfile {
  const bytes = new TextEncoder().encode(text).length;
  let lines = 0;
  for (let i = 0; i < text.length; i++) if (text.charCodeAt(i) === 10) lines++;

  if (bytes >= 2 * MB || lines >= 25_000) {
    return {
      bytes,
      lines,
      skipFidelityCheck: true,
      navFromScan: true,
      blocksPerTick: 25,
      outlineDebounceMs: 800,
      navDomCap: 1200,
    };
  }
  if (bytes >= 512 * 1024 || lines >= 8_000) {
    return {
      bytes,
      lines,
      skipFidelityCheck: true,
      navFromScan: true,
      blocksPerTick: 40,
      outlineDebounceMs: 500,
      navDomCap: 2000,
    };
  }
  return {
    bytes,
    lines,
    skipFidelityCheck: false,
    navFromScan: false,
    blocksPerTick: 200,
    outlineDebounceMs: 300,
    navDomCap: 10_000,
  };
}

export function yieldToMain(): Promise<void> {
  return new Promise((resolve) => {
    if (typeof requestIdleCallback === 'function') requestIdleCallback(() => resolve(), { timeout: 50 });
    else setTimeout(resolve, 0);
  });
}
