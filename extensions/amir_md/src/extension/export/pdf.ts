// PDF export through an installed Chromium browser in headless mode (FR-EXPORT-03, 07, 08).
//
// Deviation from the SRS, recorded as the spike S3 finding: instead of puppeteer-core,
// amir_md runs the browser's own --print-to-pdf command line. That needs no extra
// package, and page size, margins, and page numbers come from CSS @page rules.
// The table of contents option in FR-EXPORT-03 is not available this way yet.

import { spawn } from 'child_process';
import * as fs from 'fs';
import * as os from 'os';
import * as path from 'path';
import { pathToFileURL } from 'url';

const TIMEOUT_MS = 120_000;

function candidates(): string[] {
  const env = process.env;
  switch (process.platform) {
    case 'win32': {
      const pf = env['ProgramFiles'] || 'C:\\Program Files';
      const pf86 = env['ProgramFiles(x86)'] || 'C:\\Program Files (x86)';
      const local = env['LOCALAPPDATA'] || '';
      return [
        path.join(pf86, 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
        path.join(pf, 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
        path.join(pf, 'Google', 'Chrome', 'Application', 'chrome.exe'),
        path.join(pf86, 'Google', 'Chrome', 'Application', 'chrome.exe'),
        local && path.join(local, 'Google', 'Chrome', 'Application', 'chrome.exe'),
      ].filter(Boolean);
    }
    case 'darwin':
      return [
        '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '/Applications/Chromium.app/Contents/MacOS/Chromium',
      ];
    default:
      return ['/usr/bin/microsoft-edge', '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser', '/snap/bin/chromium'];
  }
}

/** The configured browser if it exists, otherwise the first installed Edge or Chrome. */
export function findBrowser(configured: string): string | null {
  if (configured) return fs.existsSync(configured) ? configured : null;
  return candidates().find((p) => fs.existsSync(p)) ?? null;
}

export interface Cancel {
  isCancellationRequested: boolean;
  onCancellationRequested(listener: () => void): { dispose(): void };
}

const FILE_WAIT_MS = 60_000;
const POLL_MS = 250;

async function waitForFile(file: string, cancel?: Cancel): Promise<boolean> {
  const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));
  let last = -1;
  for (let waited = 0; waited < FILE_WAIT_MS; waited += POLL_MS) {
    if (cancel?.isCancellationRequested) return false;
    const size = fs.existsSync(file) ? fs.statSync(file).size : -1;
    if (size > 0 && size === last) return true;
    last = size;
    await sleep(POLL_MS);
  }
  return false;
}

/** Print an HTML string to `outPath`. Rejects with a readable message on failure. */
export async function printPdf(browser: string, html: string, outPath: string, cancel?: Cancel): Promise<void> {
  const work = fs.mkdtempSync(path.join(os.tmpdir(), 'amir-md-'));
  const htmlPath = path.join(work, 'document.html');
  const profile = path.join(work, 'profile');
  fs.writeFileSync(htmlPath, html, 'utf8');
  if (fs.existsSync(outPath)) fs.unlinkSync(outPath);
  const args = [
    '--headless=new',
    '--disable-gpu',
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-extensions',
    '--no-pdf-header-footer',
    // Scripts in the document are blocked by the page's CSP (default-src 'none').
    // --blink-settings=scriptEnabled=false is not used: it stops headless printing.
    `--user-data-dir=${profile}`,
    `--print-to-pdf=${outPath}`,
    pathToFileURL(htmlPath).href,
  ];
  try {
    await new Promise<void>((resolve, reject) => {
      const child = spawn(browser, args, { stdio: ['ignore', 'ignore', 'pipe'], windowsHide: true });
      let stderr = '';
      child.stderr?.on('data', (d: Buffer) => { stderr = (stderr + d.toString()).slice(-4000); });
      const timer = setTimeout(() => { child.kill(); reject(new Error('The browser did not finish printing within 2 minutes.')); }, TIMEOUT_MS);
      const sub = cancel?.onCancellationRequested(() => { child.kill(); reject(new Error('Export cancelled.')); });
      child.on('error', (err) => { clearTimeout(timer); sub?.dispose(); reject(new Error(`Could not start the browser: ${err.message}`)); });
      // The browser launcher can exit before its child process has written the file,
      // so wait for the PDF to appear and stop growing.
      child.on('exit', (code) => {
        void waitForFile(outPath, cancel).then((ok) => {
          clearTimeout(timer);
          sub?.dispose();
          if (ok) resolve();
          else reject(new Error(`The browser exited with code ${code} and wrote no PDF. ${stderr.trim().split('\n').slice(-3).join(' ')}`));
        });
      });
    });
  } finally {
    try {
      fs.rmSync(work, { recursive: true, force: true, maxRetries: 3, retryDelay: 200 });
    } catch {
      // the browser can still hold its profile folder for a moment; the OS temp cleanup removes it later
    }
  }
}
