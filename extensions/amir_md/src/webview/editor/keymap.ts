// Keyboard shortcuts (SRS Appendix C). The same keys are bound to amir_md.noop in
// package.json so VS Code does not also run its own command for them.

import type { Command, Plugin } from 'prosemirror-state';
import { keymap } from 'prosemirror-keymap';
import { baseKeymap, chainCommands, exitCode } from 'prosemirror-commands';
import { redo, undo } from 'prosemirror-history';
import { splitListItem } from 'prosemirror-schema-list';
import { goToNextCell } from 'prosemirror-tables';
import { schema } from '../codec/schema';
import { clearFormatting, indentList, outdentList, setBlockStyle, toggle, toggleList, BlockStyle } from './commands';
import { foldAtCursor } from './foldPlugin';

export function buildKeymaps(openLinkDialog: () => void): Plugin[] {
  const hardBreak = chainCommands(exitCode, (state, dispatch) => {
    if (dispatch) dispatch(state.tr.replaceSelectionWith(schema.nodes.hard_break.create()).scrollIntoView());
    return true;
  });
  const keys: Record<string, Command> = {
    'Mod-z': undo,
    'Mod-y': redo,
    'Mod-Shift-z': redo,
    'Mod-b': toggle.strong,
    'Mod-i': toggle.em,
    'Mod-u': toggle.underline,
    'Alt-Shift-5': toggle.strikethrough,
    'Mod-k': () => { openLinkDialog(); return true; },
    'Mod-Shift-8': toggleList('bullet'),
    'Mod-Shift-7': toggleList('ordered'),
    'Mod-Space': clearFormatting,
    'Alt-Shift--': foldAtCursor(true),
    'Alt-Shift-=': foldAtCursor(false),
    'Enter': splitListItem(schema.nodes.list_item),
    'Tab': chainCommands(goToNextCell(1), indentList),
    'Shift-Tab': chainCommands(goToNextCell(-1), outdentList),
    'Shift-Enter': hardBreak,
    'Mod-Enter': hardBreak,
    'Mod-Alt-0': setBlockStyle('paragraph'),
  };
  for (let l = 1; l <= 6; l++) keys[`Mod-Alt-${l}`] = setBlockStyle(`h${l}` as BlockStyle);
  return [keymap(keys), keymap(baseKeymap)];
}
