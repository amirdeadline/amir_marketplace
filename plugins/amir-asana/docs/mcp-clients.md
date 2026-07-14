# Connecting other MCP clients (Gemini, generic hosts)

The Amir Asana connector is a **stdio MCP server**. Any host that supports stdio MCP
can use it with the same Python command and credentials.

## Server command

**Windows:**

```
E:\PC3_Shared\Palo\asana\Amir_Asana_Claude\.venv\Scripts\python.exe
E:\PC3_Shared\Palo\asana\Amir_Asana_Claude\src\asana_connector\server.py
```

**macOS / Linux:**

```
/path/Amir_Asana_Claude/.venv/bin/python
/path/Amir_Asana_Claude/src/asana_connector/server.py
```

## Credentials (recommended: `.env`)

Create `.env` in the project root:

```
ASANA_ACCESS_TOKEN=your-personal-access-token
```

The server calls `load_dotenv()` on startup, so **all MCP hosts** pick up the token
without duplicating it in each config file.

**Precedence:** OS environment variable → `.env` → `CLAUDE.md` paste line.

## Generic MCP config template

If your host uses JSON MCP configuration:

```json
{
  "mcpServers": {
    "amir-asana": {
      "command": "E:/PC3_Shared/Palo/asana/Amir_Asana_Claude/.venv/Scripts/python.exe",
      "args": [
        "E:/PC3_Shared/Palo/asana/Amir_Asana_Claude/src/asana_connector/server.py"
      ],
      "env": {
        "ASANA_ACCESS_TOKEN": "your-pat-here"
      }
    }
  }
}
```

Prefer leaving `env` empty when `.env` exists in the project folder — avoids duplicating
secrets. Use the `env` block only when the host cannot read `.env` from the server's
working directory.

## Cursor / Claude Code

Use the plugin marketplace (recommended):

```text
/plugin marketplace add e:\PC3_Shared\Palo\asana\Amir_Asana_Claude
/plugin install amir-asana@amir-asana-marketplace
```

The plugin bundles the MCP server **and** all nine skills.

## Gemini and other agents

1. Install Python deps (`pip install -r requirements.txt`) in the project `.venv`.
2. Set credentials via `.env` or host `env` block.
3. Register the stdio server with the command above.
4. Call tools by name, e.g. `list_priority_tasks_today` for "most important tasks today".

Skills are optional — they guide Claude/Cursor workflows. Other agents call MCP tools
directly.

## Security

- One Personal Access Token per person.
- Never commit `.env` or `CLAUDE.md` (both are git-ignored).
- Revoke leaked tokens in Asana → Developer Console immediately.
