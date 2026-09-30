# chrome_devtools

## Overview

The **chrome_devtools** MCP server drives a Chrome browser instance over the Chrome DevTools Protocol, exposed through the MCP gateway. It lets an agent open and switch between pages (tabs), inspect page structure via snapshots, interact with elements (click, hover, drag), run JavaScript in the page context, read console output, and handle native browser dialogs. Typical use cases include automated UI testing, scraping rendered content, reproducing and debugging web app behavior, and multi-step browser workflows against a real Chromium engine.

## Authentication

chrome_devtools does **not** use API tokens, keys, or passwords. It connects to a local (or gateway-hosted) Chrome/Chromium instance through the DevTools Protocol; access is governed by the MCP gateway and the browser process it controls, not by credential material. The only "connection requirement" is a reachable Chrome instance that the DevTools endpoint can attach to. No secrets need to be supplied to any of these tools.

Note on element references: most interaction tools require a `uid` (element reference) that comes from a prior **page content snapshot**. Snapshots are produced by the browser session, so tools that act on an element depend on having an up-to-date snapshot rather than on any authentication step.

## Tools

### click

Full name: `mcp__mcp-gateway__chrome_devtools__click`.

**What it does:** Clicks a specific element on the current page, optionally as a double-click.

**Details:** Targets an element by its `uid` from the latest page content snapshot. Supports single or double clicks. Button choice is not exposed here (use the default primary/left click behavior of the element).

**Key parameters:**
- `uid` — string — required — the element reference from the page content snapshot.
- `dblClick` — boolean — optional (default false) — set true to perform a double click.

**Example usage:** After taking a snapshot and finding the submit button's `uid`, call `click` with that `uid` to submit a form; pass `dblClick: true` to open an item that requires a double click.

### drag

Full name: `mcp__mcp-gateway__chrome_devtools__drag`.

**What it does:** Performs a drag-and-drop from one element onto another.

**Details:** Both endpoints are identified by `uid` values from the page snapshot. Useful for reordering list items, moving cards between columns, or drag-to-target UI interactions.

**Key parameters:**
- `from_uid` — string — required — the element to drag.
- `to_uid` — string — required — the element to drop onto.

**Example usage:** Drag a Kanban card from the "To Do" column element onto the "In Progress" column element by passing their two `uid`s.

### evaluate_script

Full name: `mcp__mcp-gateway__chrome_devtools__evaluate_script`.

**What it does:** Executes a JavaScript function inside the currently selected page and returns its JSON-serializable result.

**Details:** You provide a JavaScript function declaration (arrow or async function). It can run with no arguments (e.g. read `document.title` or `await fetch(...)`) or with arguments that are element references. Return values must be JSON-serializable. Optional `args` pass page elements (by `uid`) into the function so the script can operate on specific DOM nodes.

**Key parameters:**
- `function` — string — required — a JavaScript function declaration to execute, e.g. `() => document.title` or `(el) => el.innerText`.
- `args` — array of objects — optional — list of arguments; each entry is `{ uid }` referencing an element from the page snapshot, passed into the function in order.

**Example usage:** Run `() => window.location.href` to read the current URL, or pass an element `uid` in `args` and use `(el) => el.getBoundingClientRect()` to measure a node.

### get_console_message

Full name: `mcp__mcp-gateway__chrome_devtools__get_console_message`.

**What it does:** Retrieves a single browser console message by its numeric ID.

**Details:** Console messages are enumerated elsewhere in the session (the full list is obtained by listing console messages); this tool fetches the details of one specific entry using its `msgid`.

**Key parameters:**
- `msgid` — number — required — the ID of the console message to fetch (from the listed console messages).

**Example usage:** After noticing an error count, call `get_console_message` with the offending message's `msgid` to read its full text and stack context.

### handle_dialog

Full name: `mcp__mcp-gateway__chrome_devtools__handle_dialog`.

**What it does:** Accepts or dismisses a native browser dialog (alert, confirm, prompt, beforeunload) that has been opened.

**Details:** Use this when a page triggers a JavaScript dialog that blocks further interaction. You choose to accept or dismiss it, and may supply text for prompt dialogs.

**Key parameters:**
- `action` — string (`accept` | `dismiss`) — required — whether to accept or dismiss the dialog.
- `promptText` — string — optional — text to enter into a prompt dialog before accepting.

**Example usage:** When a `confirm()` dialog appears, call `handle_dialog` with `action: "accept"`; for a `prompt()`, pass `promptText` plus `action: "accept"`.

### hover

Full name: `mcp__mcp-gateway__chrome_devtools__hover`.

**What it does:** Moves the pointer over a specified element to trigger hover states.

**Details:** Targets an element by `uid` from the page snapshot. Useful for revealing dropdown menus, tooltips, or hover-only controls before clicking them.

**Key parameters:**
- `uid` — string — required — the element reference from the page content snapshot.

**Example usage:** Hover over a navigation menu item's `uid` to expand its submenu, then take a new snapshot and click the revealed link.

### list_pages

Full name: `mcp__mcp-gateway__chrome_devtools__list_pages`.

**What it does:** Lists the pages (tabs) currently open in the browser.

**Details:** Returns the open pages with their indexes, which are used by `select_page` and `resize_page`/`close`-style operations. Takes no parameters.

**Key parameters:**
- _(none)_

**Example usage:** Call `list_pages` to discover how many tabs are open and their indexes before selecting the correct one to act on.

### new_page

Full name: `mcp__mcp-gateway__chrome_devtools__new_page`.

**What it does:** Opens a new page (tab) and navigates it to a given URL.

**Details:** Creates a fresh page loading the specified URL. An optional timeout controls how long to wait for the load; `0` uses the default timeout.

**Key parameters:**
- `url` — string — required — the URL to load in the new page.
- `timeout` — integer — optional — maximum wait time in milliseconds; `0` means use the default timeout.

**Example usage:** Call `new_page` with `url: "https://example.com"` to open the site in a new tab for inspection.

### resize_page

Full name: `mcp__mcp-gateway__chrome_devtools__resize_page`.

**What it does:** Resizes the selected page's window so the page has the specified dimensions.

**Details:** Sets the viewport/window size, useful for testing responsive layouts or ensuring elements are within view before interacting.

**Key parameters:**
- `width` — number — required — target page width.
- `height` — number — required — target page height.

**Example usage:** Call `resize_page` with `width: 375, height: 812` to emulate a mobile viewport before taking a snapshot.

### select_page

Full name: `mcp__mcp-gateway__chrome_devtools__select_page`.

**What it does:** Selects which open page (tab) becomes the context for subsequent tool calls.

**Details:** Uses the page index from `list_pages`. After selecting, interaction, evaluation, and resize tools act on that page.

**Key parameters:**
- `pageIdx` — number — required — the index of the page to select (from `list_pages`).

**Example usage:** After `list_pages` shows a second tab at index 1, call `select_page` with `pageIdx: 1` to make it active.

### wait_for

Full name: `mcp__mcp-gateway__chrome_devtools__wait_for`.

**What it does:** Waits for specified text to appear on the selected page.

**Details:** Blocks until the given text is present, up to a timeout. Useful for synchronizing with asynchronous page updates before continuing. A timeout of `0` uses the default.

**Key parameters:**
- `text` — string — required — the text to wait for on the page.
- `timeout` — integer — optional — maximum wait time in milliseconds; `0` uses the default timeout.

**Example usage:** After submitting a form, call `wait_for` with `text: "Thank you"` to block until the confirmation message renders.
