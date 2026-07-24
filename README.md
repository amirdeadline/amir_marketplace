# amir marketplace

Cross-host plugin marketplace (Claude Code / Cursor / Codex).

**Version:** see [`VERSION`](VERSION) · **Security matrix:** [`SECURITY.md`](SECURITY.md)

## Slash menu (`/` in Cursor / Claude Code)

Every marketplace plugin is named `amir` or `amir-*`, so typing **`/amir`** lists your tools:

| Example | Plugin |
|---------|--------|
| `/amir:plan`, `/amir:build_goal`, `/amir:troubleshoot`, `/amir:use_subagent` | core harness |
| `/use_subagent {prompt}` | alias recognized by the use_subagent skill (same as `/amir:use_subagent`) |
| `/amir-asana:…` | Asana |
| `/amir-aws:whoami`, `/amir-terraform:plan` | infra |
| `/amir-nmap:scan`, `/amir-ssh:run` | network |
| `/amir-prisma:ask`, `/amir-paloalto:…` | security |

## Plugins

| Name | Category |
|------|----------|
| amir | integrations |
| amir-asana | integrations |
| amir-prisma | security (internal) |
| amir-litellm | integrations |
| amir-paloalto | security |
| amir-aws | infra |
| amir-azure | infra |
| amir-terraform | infra |
| amir-docker | infra |
| amir-splunk | security |
| amir-elastic | security |
| amir-sentinel | security |
| amir-qradar | security |
| amir-cortex-xdr | security |
| amir-ssh | network |
| amir-nmap | network |
| amir-wireshark | network |

## Pack tooling batch

```powershell
cd E:\PC3_Shared\Plugins\amir_marketplace
python scripts\scaffold_tooling_batch.py
python scripts\scaffold_tooling_batch2.py
python scripts\update_marketplace_catalog.py
powershell -ExecutionPolicy Bypass -File scripts\validate-all.ps1
```

## Validate

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validate-all.ps1
# or: bash scripts/validate-all.sh
```

CI: `.github/workflows/validate-plugins.yml`

## Cursor local

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install-cursor-local.ps1
```

## Claude Code

```text
/plugin marketplace add E:/PC3_Shared/Plugins/amir_marketplace
/plugin install <name>@amir-marketplace
```

## Licensing

`amir-prisma` baked references are for **internal/personal use only** - prefer a private repo.
