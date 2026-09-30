# figma_desktop

## Overview

The **figma_desktop** MCP server bridges an AI coding agent to the locally
running **Figma desktop application** (Dev Mode MCP server). It lets the agent
pull structured design information straight out of an open Figma file so it can
turn designs into code with high fidelity.

The tools cover the full "design → code" loop:

- **Generate UI code** from a selected node or FigJam board
  (`get_design_context`, `get_figjam`).
- **Inspect structure** of a page or node tree — layer names, IDs, types,
  positions, sizes (`get_metadata`).
- **Capture screenshots** of a node for visual reference
  (`get_screenshot`).
- **Read design tokens / variables** (colors, spacing, typography, etc.) so
  generated code uses the real design-system values (`get_variable_defs`).
- **Map Figma components to existing code components** via a two-step strategy
  request/response flow (`get_strategy_for_mapping`,
  `send_get_strategy_response`).
- **Bootstrap design-system rules** for the current repo
  (`create_design_system_rules`).

Typical use cases: "Build this Figma frame as a React component," "What are the
design variables used in this node?," "Show me the structure of this page,"
"Convert this FigJam sketch to code," and "Link these Figma components to our
codebase components."

Most tools accept a `nodeId`. When it is omitted, the tools operate on the
**currently selected node** in the Figma desktop app. When a Figma URL is given,
the node ID can be extracted from it (format `123:456` or `123-456`).

## Authentication

There is **no API key or token** for this server. Access is granted by a local
connection:

- The **Figma desktop application** must be **running** on the same machine, with
  the target design file open.
- The desktop app's **Dev Mode MCP server** must be enabled/available (this is
  the local endpoint the tools talk to). Dev Mode is a Figma seat/feature
  prerequisite; the user must be signed into their Figma account in the desktop
  app.

All calls are served by that local Figma desktop instance. No secrets are
printed or handled by these tools.

## Tools

Most tools share three optional context parameters that describe the caller's
tech stack so returned code matches it:

- `clientFrameworks` — string — optional — comma-separated list of frameworks in
  use (e.g. `react,next`).
- `clientLanguages` — string — optional — comma-separated list of programming
  languages in use (e.g. `typescript,css`).

These are noted per tool below where they apply.

### get_design_context

**What it does:** Generates UI code for a given node (or the currently selected
node) in the Figma desktop app. This is the primary "turn this design into code"
tool.

**Details:** If no `nodeId` is provided, the currently selected node in Figma is
used. If a Figma URL is provided, the node ID is extracted from the URL. The
`taskType`, `artifactType`, and `forceCode` hints steer what and how output is
produced; `clientFrameworks`/`clientLanguages` tailor the generated code to the
caller's stack.

**Key parameters:**
- `nodeId` — string — optional — ID of the node to generate code for, e.g.
  `123:456` or `123-456`. Omit to use the current selection.
- `clientFrameworks` — string — optional — comma-separated frameworks used by the
  client.
- `clientLanguages` — string — optional — comma-separated languages used by the
  client.
- `artifactType` — string — optional — the type of artifact the user is creating
  or modifying.
- `taskType` — string — optional — the type of task being performed.
- `forceCode` — boolean — optional — whether code should always be returned.

**Example usage:**
```json
{
  "nodeId": "123:456",
  "clientFrameworks": "react",
  "clientLanguages": "typescript",
  "forceCode": true
}
```

### get_figjam

**What it does:** Generates UI code for a given FigJam node (or the currently
selected FigJam node). Only works for FigJam files.

**Details:** FigJam-specific counterpart to `get_design_context`. If no `nodeId`
is given, the current FigJam selection is used. Can optionally include rendered
images of nodes in the response.

**Key parameters:**
- `nodeId` — string — optional — ID of the FigJam node in the document. Omit to
  use the current selection.
- `clientFrameworks` — string — optional — comma-separated frameworks.
- `clientLanguages` — string — optional — comma-separated languages.
- `includeImagesOfNodes` — boolean — optional — whether to include images of
  nodes in the response (default `true`).

**Example usage:**
```json
{
  "nodeId": "10:20",
  "clientFrameworks": "vue",
  "clientLanguages": "javascript",
  "includeImagesOfNodes": true
}
```

### get_metadata

**What it does:** Returns metadata for a node or page in XML format — a compact
overview of the structure with node IDs, layer types, names, positions, and
sizes.

**Details:** Use this to understand the layout hierarchy before generating or
mapping code (e.g. to find the right child `nodeId` to feed into
`get_design_context`). Output is XML rather than full code, keeping it lightweight
for large trees.

**Key parameters:**
- `nodeId` — string — optional — ID of the node/page in the document. Omit to use
  the current selection.
- `clientFrameworks` — string — optional — comma-separated frameworks.
- `clientLanguages` — string — optional — comma-separated languages.

**Example usage:**
```json
{ "nodeId": "123:456" }
```

### get_screenshot

**What it does:** Generates a screenshot (rendered image) of a given node or the
currently selected node in the Figma desktop app.

**Details:** Provides a visual reference of the design for comparison against
generated code or for the agent's own inspection. Uses the current selection when
`nodeId` is omitted.

**Key parameters:**
- `nodeId` — string — optional — ID of the node to screenshot. Omit to use the
  current selection.
- `clientFrameworks` — string — optional — comma-separated frameworks.
- `clientLanguages` — string — optional — comma-separated languages.

**Example usage:**
```json
{ "nodeId": "123-456" }
```

### get_variable_defs

**What it does:** Returns the variable definitions used by a given node. Variables
are reusable values (design tokens) that can be applied to all kinds of design
properties (colors, spacing, typography, radii, etc.).

**Details:** Lets generated code reference the real design-system tokens instead
of hard-coded values. `nodeId` is required here — supply the node whose variables
you want.

**Key parameters:**
- `nodeId` — string — required — ID of the node in the document whose variables
  should be returned.
- `clientFrameworks` — string — optional — comma-separated frameworks.
- `clientLanguages` — string — optional — comma-separated languages.

**Example usage:**
```json
{
  "nodeId": "123:456",
  "clientFrameworks": "react",
  "clientLanguages": "typescript,css"
}
```

### get_strategy_for_mapping

**What it does:** Returns the strategy for linking a given node (or the currently
selected node) to code components — i.e. how the agent should go about mapping
Figma components to existing components in the codebase.

**Details:** First step of the two-part code-connect / component-mapping flow.
The agent calls this to receive guidance, then performs the mapping work and
reports results back with `send_get_strategy_response`.

**Key parameters:**
- `nodeId` — string — optional — ID of the node to map. Omit to use the current
  selection.
- `clientFrameworks` — string — optional — comma-separated frameworks.
- `clientLanguages` — string — optional — comma-separated languages.

**Example usage:**
```json
{ "nodeId": "123:456", "clientFrameworks": "react" }
```

### send_get_strategy_response

**What it does:** Sends the agent's response back for the "get strategy for
mapping" request — i.e. reports the Figma-node-to-code-component mappings the
agent has resolved.

**Details:** Second step of the component-mapping flow that pairs with
`get_strategy_for_mapping`. The `mappings` array is required; each entry ties a
Figma `nodeId` to a code component (by name, source file, and framework label).

**Key parameters:**
- `mappings` — array — required — list of mapping objects. Each object contains:
  - `nodeId` — string — required — the Figma node being mapped.
  - `componentName` — string — required — the code component's name.
  - `source` — string — required — the source location (e.g. file path) of the
    component.
  - `label` — string (enum) — required — the target framework/format. One of:
    `React`, `Web Components`, `Vue`, `Svelte`, `Storybook`, `Javascript`,
    `Swift UIKit`, `Objective-C UIKit`, `SwiftUI`, `Compose`, `Java`, `Kotlin`,
    `Android XML Layout`, `Flutter`, `Markdown`.
- `nodeId` — string — optional — the node the strategy request was for. Omit to
  use the current selection.
- `clientFrameworks` — string — optional — comma-separated frameworks.
- `clientLanguages` — string — optional — comma-separated languages.

**Example usage:**
```json
{
  "nodeId": "123:456",
  "mappings": [
    {
      "nodeId": "123:456",
      "componentName": "PrimaryButton",
      "source": "src/components/PrimaryButton.tsx",
      "label": "React"
    }
  ]
}
```

### create_design_system_rules

**What it does:** Provides a prompt used to generate design-system rules for the
current repository, based on the client's frameworks and languages.

**Details:** Helps bootstrap a set of rules/conventions so that code generated
from Figma stays consistent with the repo's design system and stack. Both
parameters are optional context hints.

**Key parameters:**
- `clientFrameworks` — string — optional — comma-separated list of frameworks.
- `clientLanguages` — string — optional — comma-separated list of programming
  languages.

**Example usage:**
```json
{ "clientFrameworks": "react,next", "clientLanguages": "typescript" }
```
