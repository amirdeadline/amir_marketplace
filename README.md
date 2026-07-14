# amir marketplace

Cross-host plugin marketplace for **amir**, **amir-asana**, **prisma** (internal),
and **litellm**.

| Plugin | Source | Notes |
|--------|--------|-------|
| **amir** | `../Amir` | Project-execution harness |
| **amir-asana** | `../asana/Amir_Asana_Claude` | Asana MCP + skills |
| **prisma** | `../prisma` | Prisma SASE/SCM corpus skills — **internal use only** |
| **litellm** | `../litellm` | Org LiteLLM session launcher + MCP |

## Licensing warning (prisma)

The `prisma` plugin bakes distilled indexes from Palo Alto Networks documentation.
**Do not publish this marketplace (or the prisma plugin) publicly** while those
baked `references/` ship. Prefer a **private** GitHub repo. The ingest script never
uploads corpus content.

## Pack + verify

```powershell
cd E:\PC3_Shared\Plugins\amir_marketplace
node scripts/pack-amir.js
node scripts/pack-amir-asana.js
# prisma: generate skills + ingest corpus first
python ..\prisma\scripts\gen_skills.py
python ..\prisma\scripts\ingest.py
node scripts/pack-plugin-copy.js --name prisma --source ../prisma
node scripts/pack-plugin-copy.js --name litellm --source ../litellm
node scripts/verify-marketplace.js
```

## Cursor local install

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install-cursor-local.ps1
```

Then **Developer: Reload Window**.

## Visual Cockpit (VS Code / Cursor extension)

Optional IDE side panel lives in [`extensions/amir`](extensions/amir) — Project / Agents / Tasks over `ai/state/*.json`. Mutations call packed `plugins/amir/tools/state.js`.

```powershell
cd extensions/amir
npm install
npm run compile
npm run package
code --install-extension amir-0.1.0.vsix
# or: cursor --install-extension amir-0.1.0.vsix
```

See [`extensions/amir/README.md`](extensions/amir/README.md).

## Claude Code

```text
/plugin marketplace add E:/PC3_Shared/Plugins/amir_marketplace
/plugin install amir@amir-marketplace
/plugin install amir-asana@amir-marketplace
/plugin install prisma@amir-marketplace
/plugin install litellm@amir-marketplace
```

## Version

See [`VERSION`](VERSION).
