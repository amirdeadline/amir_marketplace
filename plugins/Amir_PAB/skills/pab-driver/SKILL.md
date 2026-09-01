---
name: pab-driver
description: How to find, attach to, and drive the Prisma Access Browser (PAB) desktop app on Windows using the cua computer-use driver, under a strict read-only security gate. Use this skill WHENEVER a task involves PAB, "Prisma Browser", the Prisma Access Browser, or any web portal running INSIDE it (SCM / Strata Cloud Manager, Cloud Identity Engine, Customer Support Portal, or any lab/tenant UI) — even if the user only says "check something in the lab", "look at the tenant", or "validate this against the portal". Also use it before ANY mouse/keyboard action against a PAB window.
---

# Driving the Prisma Access Browser (PAB) with the cua driver

PAB (`PrismaAccessBrowser.exe`) is Palo Alto Networks' standalone secure browser for
Windows. It is a Chromium-based desktop app — but it is NOT Chrome: a Chrome
extension/DevTools-based browser tool cannot see or control it. The only way to drive it
is OS-level desktop control (the `cua-computer-use` MCP tools). This skill records the
proven access pattern and the non-negotiable security gate.

## THE SECURITY GATE (read this first, apply always)

The PAB usually holds live, authenticated sessions to production or lab tenants.
The gate exists so that observation can never silently turn into change.

**Allowed WITHOUT the owner's approval (read-only):**
- Navigate between pages, menus, submenus, tabs inside a page
- Open dashboards; view configuration pages and details of existing objects
- Expand/collapse sections; scroll; hover; zoom; take screenshots
- Non-destructive search and filtering
- Close a view-only dialog with Cancel or X (never with OK/Save)

**Requires the owner's explicit approval in chat BEFORE acting:**
- Anything that creates, deletes, or modifies objects, settings, or policies
- Save, Commit, Push, Apply, Submit, Enable, Disable, Acknowledge, Clear, Start, Run
- Submitting any form that changes state; uploads; starting jobs or upgrades
- Logging in, logging out, or switching tenants/accounts (this changes session context)
- Anything you are not sure about — **when uncertain, treat it as state-changing and stop**

When a workflow reaches a state-changing step: stop, report what was verified so far,
name the exact button/action that comes next, and wait for approval. Never make a change
just to test whether a procedure works.

## Access pattern (proven on Windows 11)

1. **Load the tools in bulk** (one ToolSearch call): `list_windows`, `get_window_state`,
   `click`, `press_key`, `hotkey`, `type_text`, `scroll`, `zoom`, `bring_to_front`,
   `start_session`, `get_desktop_state`.
2. **Revive the session if needed.** If any call returns "this session has ended", call
   `start_session` with no arguments (revives the implicit session), then retry.
3. **Find PAB — reuse, never launch new.** `list_windows` and look for
   `app_name: "PrismaAccessBrowser.exe"`. Example observed title:
   "Palo Alto Networks - Sign In - Prisma Browser". The window title reflects the active
   tab, so match on `app_name`, not title. If the owner said a PAB tab is prepared,
   that exact window/tab is the one to use — do not open another, do not re-authenticate,
   do not switch tenants.
4. **Snapshot before acting.** `get_window_state(pid, window_id)` returns a UIA
   (accessibility) tree AND a screenshot. Chromium apps often return a lazy or empty
   tree (`ax_tree_empty` / very few elements). When that happens the screenshot is the
   ground truth — act by pixel coordinates from that screenshot (they are in the
   screenshot's own pixel space; the driver maps them back to the real window).
5. **Input ladder — always in this order:**
   - element click (`element_token` from the snapshot) when the tree has the element;
   - pixel click with default `delivery_mode: "background"`;
   - escalate the SAME action to `delivery_mode: "foreground"` ONLY if the driver says
     background is unavailable or the action verifiably did nothing. Chromium content
     frequently drops background/synthetic input — a real foreground click is what
     finally lands. `bring_to_front` first when a flow needs sustained focus.
6. **Typing:** `hotkey` for shortcuts, `type_text` (foreground/desktop scope) for text.
   Never type into a field unless the gate allows it (search boxes are fine; config
   fields are not).
7. **Verify every step.** After each action take a fresh `get_window_state` screenshot
   and confirm the expected result actually happened before continuing. "Unverifiable"
   effect results from the driver are not success.
8. **Read small text** with `zoom` on a region instead of guessing.

## Known traps

- The owner works on the same machine. Do not fight over focus; keep foreground
  escalation brief, and coordinate in chat when the machine is busy.
- The clipboard is shared with the owner — never assume clipboard content survived.
- Coordinates go stale the moment the page scrolls or a panel opens: re-screenshot.
- One in-app browser tab's title ≠ the window's title; PAB shows multiple tabs.

## Learn-as-you-go protocol

This skill is a living knowledge base. After ANY session that used PAB:
1. Append newly verified facts to [references/learned.md](references/learned.md) with
   the date and how it was verified (screenshot, successful action, owner statement).
2. Only promote a fact into this SKILL.md once it has held true more than once.
3. Never record credentials, tokens, cookies, or tenant secrets anywhere in this plugin.
4. Portal-specific knowledge (SCM, CIE, CSP) belongs in its own plugin
   (Amir_PAB_SCM / Amir_PAB_CIE / Amir_PAB_CSP), not here.
