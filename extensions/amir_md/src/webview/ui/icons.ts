// Toolbar icons: 16x16 inline SVG drawn with currentColor so they follow the VS Code theme.

const svg = (body: string) =>
  `<svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">${body}</svg>`;

export const ICONS: Record<string, string> = {
  undo: svg('<path d="M4 6h6a3 3 0 0 1 0 6H7"/><path d="M6.5 3.5 4 6l2.5 2.5"/>'),
  redo: svg('<path d="M12 6H6a3 3 0 0 0 0 6h3"/><path d="M9.5 3.5 12 6 9.5 8.5"/>'),
  bold: '<b>B</b>',
  italic: '<i style="font-family:Georgia,serif">I</i>',
  underline: '<u>U</u>',
  strike: '<s>S</s>',
  sup: 'x<sup>2</sup>',
  sub: 'x<sub>2</sub>',
  clear: svg('<path d="M3 3h8M7 3 5 13"/><path d="m9.5 9.5 4 4m0-4-4 4"/>'),
  bullets: svg('<circle cx="3" cy="4" r=".9" fill="currentColor"/><circle cx="3" cy="8" r=".9" fill="currentColor"/><circle cx="3" cy="12" r=".9" fill="currentColor"/><path d="M6 4h8M6 8h8M6 12h8"/>'),
  numbers: svg('<path d="M2.5 2.8h1v3M2.3 5.8h2M2.2 9.2c.3-.6 1.8-.6 1.8.3 0 .8-1.8 1.3-1.8 2.2h1.9"/><path d="M6.5 4h7.5M6.5 8h7.5M6.5 12h7.5"/>'),
  tasks: svg('<rect x="1.8" y="2.3" width="3.4" height="3.4" rx=".6"/><path d="m2.4 10.6 1 1 1.6-2"/><rect x="1.8" y="9" width="3.4" height="3.4" rx=".6"/><path d="M7 4h7M7 10.7h7"/>'),
  outdent: svg('<path d="M7 4h7M7 8h7M3 12h11M4.5 5.5 2.5 7.5l2 2"/>'),
  indent: svg('<path d="M7 4h7M7 8h7M3 12h11M2.5 5.5l2 2-2 2"/>'),
  alignLeft: svg('<path d="M2 3.5h12M2 6.5h8M2 9.5h12M2 12.5h8"/>'),
  alignCenter: svg('<path d="M2 3.5h12M4 6.5h8M2 9.5h12M4 12.5h8"/>'),
  alignRight: svg('<path d="M2 3.5h12M6 6.5h8M2 9.5h12M6 12.5h8"/>'),
  link: svg('<path d="M6.8 9.2a2.6 2.6 0 0 0 3.7 0l2.2-2.2a2.6 2.6 0 0 0-3.7-3.7l-.8.8"/><path d="M9.2 6.8a2.6 2.6 0 0 0-3.7 0L3.3 9a2.6 2.6 0 0 0 3.7 3.7l.8-.8"/>'),
  image: svg('<rect x="1.8" y="2.8" width="12.4" height="10.4" rx="1.2"/><circle cx="5.5" cy="6.3" r="1.2"/><path d="m2.5 12 3.8-3.6 2.5 2.3 2-1.8 2.8 2.6"/>'),
  table: svg('<rect x="1.8" y="2.3" width="12.4" height="11.4" rx="1"/><path d="M1.8 6h12.4M1.8 9.8h12.4M6 2.3v11.4M10 2.3v11.4"/>'),
  quote: svg('<path d="M3 4.5v7M6 5h8M6 8h8M6 11h5"/>'),
  code: svg('<path d="m5.5 4.5-3.5 3.5 3.5 3.5M10.5 4.5 14 8l-3.5 3.5"/>'),
  codeBlock: svg('<rect x="1.8" y="2.3" width="12.4" height="11.4" rx="1.2"/><path d="m6 6-2 2 2 2M10 6l2 2-2 2"/>'),
  rule: svg('<path d="M2 8h12"/><path d="M2 4.5h12M2 11.5h12" stroke-opacity=".35"/>'),
  nav: svg('<rect x="1.8" y="2.3" width="12.4" height="11.4" rx="1.2"/><path d="M6 2.3v11.4M3 5h1.8M3 7.5h1.8M3 10h1.8"/>'),
  export: svg('<path d="M8 2.5v7.5M5 7l3 3 3-3"/><path d="M3 10.5V13h10v-2.5"/>'),
  caret: svg('<path d="m4.5 6.5 3.5 3.5 3.5-3.5"/>'),
  highlight: svg('<path d="m4 10.5 5.5-7 3 2.3-5.5 7H4z"/><path d="M4 10.5 2.6 12.2"/>'),
};
