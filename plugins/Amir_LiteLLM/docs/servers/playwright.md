# playwright

## Overview

The **playwright** MCP server provides browser automation driven by [Playwright](https://playwright.dev/). Through it you can open web pages, click and type into elements, fill and submit forms, work with dropdowns and checkboxes, drag-and-drop, press keys, manage multiple tabs, resize the window, wait for content, and inspect the browser console.

The interaction model is built on the **accessibility snapshot**, not raw CSS selectors or screen coordinates. Playwright captures a structured snapshot of the page in which each interactive element is assigned a stable reference id (`ref`). Element-targeting tools therefore take two arguments together:

- `ref` — the exact reference id of the target element as it appears in the current page snapshot.
- `element` — a short human-readable description of that same element (e.g. "Sign in button"). This description is used to confirm the intended interaction and appears in permission/audit context.

Because `ref` values come from a snapshot, they are only valid for the page state in which they were captured. After a navigation or a change that re-renders the page, obtain a fresh snapshot before targeting elements again. (The page snapshot itself is typically returned by these action tools as part of their result, giving you the refs for the next step.)

Tools in this server are prefixed `mcp__mcp-gateway__playwright__` — for example `mcp__mcp-gateway__playwright__browser_navigate`. Throughout this reference each tool is introduced by its short name (e.g. `browser_navigate`).

## Authentication

**No API authentication is required.** These tools drive a browser instance rather than call an authenticated API, so there is no API token, key, or credential to configure for the server itself. Any login into a specific website is handled the same way a human would — by navigating to the site and typing credentials into its form fields with the interaction tools.

Access to the server is mediated by the **MCP gateway session** (the gateway routes tool calls and applies its own policy). No secrets are needed in the tool calls; never paste secrets into descriptions or field values beyond what a target site's own login flow requires, and never print secrets.

## Tools

### browser_navigate

Full name: `mcp__mcp-gateway__playwright__browser_navigate`.

**What it does:** Navigates the current browser page to a URL.

**Details:** This is normally the first call in any browsing session — it loads the target page so that a snapshot with element refs becomes available for subsequent interaction. Navigating replaces the current page content, so any previously captured `ref` values become stale.

**Key parameters:**
- `url` — string — required — the URL to navigate to.

**Example usage:**
```json
{
  "url": "https://example.com/login"
}
```

### browser_navigate_back

Full name: `mcp__mcp-gateway__playwright__browser_navigate_back`.

**What it does:** Goes back to the previous page in the browser history (equivalent to the browser's Back button).

**Details:** Takes no parameters. Use it to return to a prior page after following a link or submitting a form. As with any navigation, refs captured on the page you were on may no longer be valid after going back.

**Key parameters:** None.

**Example usage:**
```json
{}
```

### browser_click

**What it does:** Performs a click on an element in the page (`mcp__mcp-gateway__playwright__browser_click`).

**Details:** Targets an element by its snapshot `ref` and description. Supports left/right/middle mouse button, double-click, and holding modifier keys during the click (e.g. Control-click to open a link in a new tab).

**Key parameters:**
- `element` — string — required — human-readable description of the element (used to confirm the interaction).
- `ref` — string — required — exact target element reference from the page snapshot.
- `button` — string (`left` | `right` | `middle`) — optional — which mouse button to click; defaults to left.
- `doubleClick` — boolean — optional — set true to perform a double click instead of a single click.
- `modifiers` — array of strings (`Alt` | `Control` | `ControlOrMeta` | `Meta` | `Shift`) — optional — modifier keys to hold while clicking.

**Example usage:**
```json
{
  "element": "Submit button",
  "ref": "e42",
  "button": "left"
}
```

### browser_type

**What it does:** Types text into an editable element such as a text box (`mcp__mcp-gateway__playwright__browser_type`).

**Details:** Enters text into the referenced element. Can optionally type one character at a time (useful for pages with per-keystroke JavaScript handlers) and can optionally submit by pressing Enter after typing.

**Key parameters:**
- `element` — string — required — human-readable description of the element.
- `ref` — string — required — exact target element reference from the page snapshot.
- `text` — string — required — the text to type into the element.
- `slowly` — boolean — optional — type one character at a time to trigger key handlers; by default the whole text is filled at once.
- `submit` — boolean — optional — press Enter after typing (submits the entered text).

**Example usage:**
```json
{
  "element": "Search box",
  "ref": "e17",
  "text": "prisma sase lab",
  "submit": true
}
```

### browser_fill_form

**What it does:** Fills multiple form fields in a single call (`mcp__mcp-gateway__playwright__browser_fill_form`).

**Details:** Takes a list of field descriptors and populates each one according to its `type`. This is more efficient than a sequence of individual type/select/click calls when completing a whole form. For checkboxes the value is `"true"`/`"false"`; for comboboxes the value is the visible option text.

**Key parameters:**
- `fields` — array — required — the fields to fill. Each entry is an object with:
  - `name` — string — required — human-readable field name.
  - `type` — string (`textbox` | `checkbox` | `radio` | `combobox` | `slider`) — required — the kind of field.
  - `ref` — string — required — the field's reference from the page snapshot.
  - `value` — string — required — value to fill. For a checkbox use `"true"`/`"false"`; for a combobox use the option text.

**Example usage:**
```json
{
  "fields": [
    {"name": "Username", "type": "textbox", "ref": "e5", "value": "student1"},
    {"name": "Remember me", "type": "checkbox", "ref": "e6", "value": "true"},
    {"name": "Region", "type": "combobox", "ref": "e7", "value": "US-East"}
  ]
}
```

### browser_select_option

**What it does:** Selects one or more options in a dropdown (`mcp__mcp-gateway__playwright__browser_select_option`).

**Details:** Chooses option(s) in a `<select>`-style dropdown identified by its snapshot ref. Provide a single value for a single-select dropdown, or multiple values for a multi-select.

**Key parameters:**
- `element` — string — required — human-readable description of the dropdown.
- `ref` — string — required — exact target element reference from the page snapshot.
- `values` — array of strings — required — value(s) to select; one for single-select, multiple for multi-select.

**Example usage:**
```json
{
  "element": "Scenario dropdown",
  "ref": "e23",
  "values": ["Scenario 11 - SD-WAN Basic"]
}
```

### browser_hover

**What it does:** Hovers the mouse over an element (`mcp__mcp-gateway__playwright__browser_hover`).

**Details:** Moves the pointer over the referenced element, which can reveal hover-triggered menus, tooltips, or dynamic content. Takes only the element target.

**Key parameters:**
- `element` — string — required — human-readable description of the element.
- `ref` — string — required — exact target element reference from the page snapshot.

**Example usage:**
```json
{
  "element": "Account menu",
  "ref": "e9"
}
```

### browser_drag

**What it does:** Performs a drag-and-drop between two elements (`mcp__mcp-gateway__playwright__browser_drag`).

**Details:** Drags a source element onto a target element. Both endpoints are specified by their snapshot refs plus human-readable descriptions.

**Key parameters:**
- `startElement` — string — required — human-readable description of the source element.
- `startRef` — string — required — exact source element reference from the page snapshot.
- `endElement` — string — required — human-readable description of the target element.
- `endRef` — string — required — exact target element reference from the page snapshot.

**Example usage:**
```json
{
  "startElement": "Task card 'Deploy'",
  "startRef": "e31",
  "endElement": "In-progress column",
  "endRef": "e40"
}
```

### browser_press_key

**What it does:** Presses a single key on the keyboard (`mcp__mcp-gateway__playwright__browser_press_key`).

**Details:** Sends a keypress to the page. The key can be a named key (e.g. `ArrowLeft`, `Enter`, `Escape`, `Tab`) or a single character to generate (e.g. `a`). Useful for keyboard-driven navigation, dismissing dialogs, or triggering shortcuts.

**Key parameters:**
- `key` — string — required — name of the key to press or a character to generate, such as `ArrowLeft` or `a`.

**Example usage:**
```json
{
  "key": "Escape"
}
```

### browser_wait_for

**What it does:** Waits for text to appear or disappear, or for a fixed amount of time to pass (`mcp__mcp-gateway__playwright__browser_wait_for`).

**Details:** Synchronizes with dynamic pages. Supply `text` to wait until that text appears, `textGone` to wait until text disappears, or `time` to simply wait a number of seconds. Provide only the condition you need.

**Key parameters:**
- `text` — string — optional — text to wait for to appear.
- `textGone` — string — optional — text to wait for to disappear.
- `time` — number — optional — the time to wait, in seconds.

**Example usage:**
```json
{
  "text": "Lab is ready"
}
```

### browser_tabs

**What it does:** Lists, creates, closes, or selects browser tabs (`mcp__mcp-gateway__playwright__browser_tabs`).

**Details:** A single multi-purpose tab manager chosen by the `action` argument. Use `list` to enumerate open tabs, `new` to open a tab, `select` to switch to a tab by index, and `close` to close a tab (the current tab if no index is given). For `select` and `close`, provide the `index` of the target tab.

**Key parameters:**
- `action` — string (`list` | `new` | `close` | `select`) — required — the operation to perform.
- `index` — number — optional — tab index, used for `close`/`select`; if omitted for `close`, the current tab is closed.

**Example usage:**
```json
{
  "action": "select",
  "index": 1
}
```

### browser_resize

**What it does:** Resizes the browser window (`mcp__mcp-gateway__playwright__browser_resize`).

**Details:** Sets the browser window to explicit pixel dimensions, useful for testing responsive layouts or ensuring a consistent viewport.

**Key parameters:**
- `width` — number — required — width of the browser window.
- `height` — number — required — height of the browser window.

**Example usage:**
```json
{
  "width": 1280,
  "height": 800
}
```

### browser_console_messages

**What it does:** Returns console messages from the page (`mcp__mcp-gateway__playwright__browser_console_messages`).

**Details:** Retrieves messages logged to the browser console (logs, warnings, errors). Optionally restrict the result to error messages only — helpful for diagnosing failing pages or scripts.

**Key parameters:**
- `onlyErrors` — boolean — optional — return only error messages.

**Example usage:**
```json
{
  "onlyErrors": true
}
```

### browser_close

**What it does:** Closes the current page (`mcp__mcp-gateway__playwright__browser_close`).

**Details:** Closes the active browser page. Takes no parameters. Use it to end a browsing session or free the page when finished.

**Key parameters:** None.

**Example usage:**
```json
{}
```
