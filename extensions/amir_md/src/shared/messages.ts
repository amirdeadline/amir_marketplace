// Message contract between the extension host and the webview (SRS 5.3).

export interface TextChange {
  start: number;
  end: number;
  text: string;
}

export interface Settings {
  fontFamilies: string[];
  defaultFontFamily: string;
  defaultFontSize: number;
  palette: string[];
  foldRemember: boolean;
  navDefaultExpandLevel: number;
  navWidth: number;
  bulletMarker: string;
  emphasisMarker: string;
  strongMarker: string;
  allowRemoteImages: boolean;
}

export type NavLevel = 'all' | '1' | '2' | '3' | '4' | '5';

export interface ViewState {
  folds: string[];
  navOpen: Record<string, boolean>;
  navLevel: NavLevel;
  navWidth: number;
  navHidden: boolean;
  scrollTop: number;
}

export type ExportFormat = 'pdf' | 'docx' | 'html' | 'md';

export type HostToWebview =
  | {
      type: 'init';
      text: string;
      version: number;
      eol: '\n' | '\r\n';
      fileName: string;
      /** Webview URL of the document's folder, ending in "/", for resolving relative image paths. */
      baseUri: string;
      settings: Settings;
      viewState: ViewState | null;
    }
  | { type: 'externalChange'; text: string; version: number }
  | { type: 'editResult'; ok: true; version: number }
  | { type: 'editResult'; ok: false; version: number; text: string }
  | { type: 'settings'; settings: Settings }
  | { type: 'resources'; map: Record<string, string | null> }
  | { type: 'imageInserted'; requestId: number; path: string | null }
  | { type: 'command'; name: 'expandAll' | 'collapseAll' | 'toggleNav' | 'flush' | 'export'; format?: ExportFormat }
  | { type: 'exportDone'; ok: boolean; path?: string; error?: string };

export type WebviewToHost =
  | { type: 'ready' }
  | { type: 'edit'; baseVersion: number; changes: TextChange[] }
  | { type: 'resolveResources'; paths: string[] }
  | { type: 'pickImage'; requestId: number }
  | { type: 'saveImage'; requestId: number; dataBase64: string; mime: string }
  | { type: 'openLink'; href: string }
  | { type: 'saveViewState'; state: ViewState }
  | { type: 'export'; format: ExportFormat }
  | { type: 'flushed' }
  | { type: 'log'; level: 'info' | 'warn' | 'error'; message: string };
