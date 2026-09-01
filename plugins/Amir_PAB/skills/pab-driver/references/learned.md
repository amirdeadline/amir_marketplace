# PAB — verified observations log

Append new entries at the top. Format: date · fact · how verified.

- 2026-09-01 · PAB runs as `PrismaAccessBrowser.exe`; observed window
  "Palo Alto Networks - Sign In - Prisma Browser" (title = active tab) ·
  seen via cua `list_windows` on AMIR-PC1.
- 2026-09-01 · The Chrome extension browser tools cannot see PAB at all;
  only desktop control (cua driver) can · confirmed by tool inventory and
  window enumeration during the Day 2 doc project.
- 2026-09-01 · Chromium-based app windows frequently return an empty/lazy UIA tree
  (`ax_tree_empty`), so pixel actions from the window screenshot are the reliable
  path; synthetic background clicks are often dropped and need foreground
  escalation · proven while driving Chrome and Google Docs sidebars with the
  same driver on the same machine.
