# amir marketplace

Cross-host plugin marketplace for **amir** (project-execution harness) and
**amir-asana** (Asana MCP + skills).

One catalog. Three native marketplace formats.

| Host | Marketplace file | Install |
|------|------------------|---------|
| **Claude Code** | `.claude-plugin/marketplace.json` | `/plugin marketplace add …` then `/plugin install <name>@amir-marketplace` |
| **Cursor** | `.cursor-plugin/marketplace.json` | Local junctions under `~/.cursor/plugins/local/`, Team Marketplace, or [cursor.com/marketplace/publish](https://cursor.com/marketplace/publish) |
| **Codex / ChatGPT Work** | `.agents/plugins/marketplace.json` | `codex plugin marketplace add …` then `codex plugin add <name>` |
| **Other Agent Skills hosts** | `catalog/hosts.json` | Copy skills + package roots as needed |

| Plugin | Packed path | Source of truth |
|--------|-------------|-----------------|
| **amir** | `plugins/amir/` | [`../Amir`](../Amir) |
| **amir-asana** | `plugins/amir-asana/` | [`../asana/Amir_Asana_Claude`](../asana/Amir_Asana_Claude) |

## Layout

```text
amir_marketplace/
  .claude-plugin/marketplace.json
  .cursor-plugin/marketplace.json
  .agents/plugins/marketplace.json
  catalog/hosts.json
  scripts/pack-amir.js
  scripts/pack-amir-asana.js
  scripts/verify-marketplace.js
  scripts/install-cursor-local.ps1
  plugins/amir/
  plugins/amir-asana/
  VERSION
  README.md
```

## Quickstart — local

### 1. Pack plugins

```bash
node scripts/pack-amir.js
node scripts/pack-amir-asana.js
node scripts/verify-marketplace.js
```

Requires **Node.js >= 18**. Asana also needs its Python `.venv` (created in the
source tree; pack junctions it into `plugins/amir-asana` when present).

### 2. Add the marketplace (pick your host)

**Claude Code**

```text
/plugin marketplace add E:/PC3_Shared/Plugins/amir_marketplace
/plugin install amir@amir-marketplace
/plugin install amir-asana@amir-marketplace
```

**Cursor (local — recommended on this machine)**

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install-cursor-local.ps1
```

Then **Developer: Reload Window**. Plugins appear under Customize → Plugins
as local installs (`amir`, `amir-asana`).

Team / public listing: submit the repo at [cursor.com/marketplace/publish](https://cursor.com/marketplace/publish).

**Codex CLI / ChatGPT desktop**

```bash
codex plugin marketplace add E:/PC3_Shared/Plugins/amir_marketplace
codex plugin add amir
codex plugin add amir-asana
```

**Other hosts (Windsurf, Continue, Gemini CLI, custom)**

1. Pack plugins as above
2. Copy skills into the host skills directory
3. For Asana MCP: `node plugins/amir-asana/scripts/run-mcp.js` (stdio)

See `catalog/hosts.json` for the support matrix.

## What installs

### amir

- Full skill catalog (project lifecycle, design/plan, build/QA, git, docs, system/user maintenance)
- JSON state layer + Node tools
- Host adapters: Claude agents/hooks, Cursor commands/rules (includes `/btw`), Codex `AGENTS.md` + skills

### amir-asana

- FastMCP stdio server (17 Asana tools)
- Nine skills: priorities today, review, standup, triage, sync-from-report, backlog update, create/update/complete
- Credentials via `.env` (`ASANA_ACCESS_TOKEN`) — never committed

Claude Code does **not** register `/btw` (documented intentional absence). Cursor and Codex do.

## Developing

| Plugin | Edit | Re-pack |
|--------|------|---------|
| amir | [`../Amir`](../Amir) | `node scripts/pack-amir.js` |
| amir-asana | [`../asana/Amir_Asana_Claude`](../asana/Amir_Asana_Claude) | `node scripts/pack-amir-asana.js` |

Do not hand-edit packed files under `plugins/` — they are generated.

## Version

See [`VERSION`](VERSION). Keep `amir` aligned with `../Amir/VERSION`. `amir-asana` version lives in its pack script / plugin manifests (`0.2.0`).

## License

Same as the individual plugin packages. No warranty.
