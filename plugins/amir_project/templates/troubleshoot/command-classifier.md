# Troubleshoot — command classifier

Classify **every** proposed command before execution as exactly one of:

```text
READ_ONLY
STATE_CHANGING
UNCERTAIN
```

**Fail closed:** when uncertain, treat as `STATE_CHANGING` (requires approval).

---

## READ_ONLY

May run without approval only when **all** of the following hold:

- Does not alter local or remote state.
- Does not create, truncate, or overwrite files (including via redirection).
- Does not trigger scripts / hooks / lifecycle tools with unknown side effects.
- Does not acquire locks that materially affect the system.
- Does not restart, reload, signal, or terminate processes.
- Does not modify caches, databases, queues, or external APIs.
- Does not mutate package installs, configs, permissions, or credentials.
- Output can be redacted for secrets before display.

### Common READ_ONLY examples (still verify flags and composition)

```text
pwd, whoami, id, uname -a, date, uptime
ls, find, stat, file, cat, head, tail, less, grep, rg, awk, sed -n, cut, sort, uniq, wc
ps, top -b -n 1, df -h, du, free, mount, lsblk, lsof
ss, netstat, ip addr, ip route, ip link
docker ps, docker inspect, docker logs, docker compose ps
kubectl get, kubectl describe, kubectl logs
systemctl status, systemctl show, journalctl   (without write redirects)
git status, git diff, git log, git branch, git show
npm list, pip list, pip show, cargo metadata, go env
```

Windows equivalents that are typically READ_ONLY when used without write redirects:

```text
Get-Location, Get-Process, Get-Service, Get-Content, Select-String,
Get-NetTCPConnection, Get-Disk, Get-Volume, Get-ChildItem, systeminfo
docker / kubectl / git read subcommands as above
```

---

## STATE_CHANGING

Requires explicit plan + human approval. Includes (non-exhaustive):

- Create / edit / move / delete files.
- Install / remove packages.
- Restart / stop / kill services or processes.
- Change env vars, permissions, ownership, config.
- DB migrations or data writes.
- Infra apply / cloud mutations.
- Container create/start/stop/rm; image pull/push when it changes local or remote state meaningfully.
- Git state changes (`checkout`, `restore`, `clean`, `reset`, `commit`, `push`).
- Repair tools, cache clears, credential rotation.
- Mutating API / network writes.
- Any use of `sudo`, other users, or production availability impact.
- Output redirection to files (`>`, `>>`, `tee`).
- Creating TEMP diagnostic workspaces under `%TEMP%\troubleshoot\` (unless host already authorized).

### Never treat as automatically safe

```text
npm install, npm test, npm run, make
terraform plan, terraform apply
ansible, helm, kubectl apply, kubectl delete, kubectl rollout
docker compose up, docker restart, systemctl restart, service restart
git checkout, git restore, git clean, git reset
```

`npm test` / `npm run` / `make` execute project scripts → **UNCERTAIN** unless the script is inspected and proven read-only.

---

## Compound command inspection

Inspect the **full** string, including:

| Pattern | Effect |
|---------|--------|
| `>`, `>>`, `2>`, `tee` | File write → STATE_CHANGING |
| `xargs` + mutating cmd | STATE_CHANGING |
| `sh -c` / `bash -c` / `pwsh -c` / `cmd /c` | Inspect inner command |
| `$(...)` / backticks | Inspect substitutions |
| `;` `&&` `||` | Classify **each** segment; any STATE_CHANGING / UNCERTAIN → whole command blocked without approval |
| `eval`, `exec` | UNCERTAIN / STATE_CHANGING |
| `sudo` | STATE_CHANGING (elevated) |
| pipes to `kill`, `rm`, `dd`, etc. | STATE_CHANGING |
| remote shells / DB clients | Inspect for writes |

Examples:

```bash
cat config.yml                    # likely READ_ONLY
cat config.yml > backup.yml       # STATE_CHANGING
ps aux | grep nginx               # likely READ_ONLY
ps aux | awk '{print $2}' | xargs kill   # STATE_CHANGING
journalctl -u app > app.log       # STATE_CHANGING (file create)
journalctl -u app -n 200 --no-pager      # prefer this READ_ONLY form
```

---

## Secret exposure

Even READ_ONLY commands that dump secrets (`env`, `printenv`, full `.env` `cat`) should be **avoided** or tightly filtered. Prefer targeted greps with redaction. Never paste raw tokens into reports.
