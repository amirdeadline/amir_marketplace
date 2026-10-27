# 08 — Rules and approval gates (never break these)

The full rule set is `PROJECT_RULES.md`, `PROJECT_DECISIONS.md` and `.cursor/rules/*.mdc` in
the repo. Owner words in the chat win over every file. This page is the short form.

## Change levels

| Level | Examples | Needs |
|---|---|---|
| L0 read-only | read files, SSH and inspect, `gcloud … list/describe`, GET APIs, dry-runs, gold-check | nothing |
| L1 local code/docs | edit repo files, tests | owner asked for the change |
| L2 live, one lab, reversible | restart a service, install a unit, env-sync, scrub status, fix a route on one pod, publish to the bucket (affects all labs!) | owner yes for that lab / that publish |
| L3 live, destructive or costly | Terraform apply/destroy, snapshot delete/recut, SCM writes, cleanup `--apply`, license retire, anything on a booked lab | owner yes, explicit, per action |

A request like "rebuild gold for lab N" approves the L2/L3 steps of
`references/playbooks/gold-snapshot-rebuild.md` **for lab N only**. It does not approve: touching
another lab, publishing to the shared bucket, SCM writes, or acting on a lab with an active
booking. Stop and ask for those.

## Hard rules

1. **Parent TSG `1479602777`: refuse** every write. Only the target lab's own TSG from `labs.json`.
2. **No SCM writes** (wipe, retire, config push) without the owner's explicit yes. Dry-run first.
3. **Cleanup runs in labapp on that lab's gns3-1** (`POST /lab/destroy`), never from the workstation.
4. **Terraform only via `build_lab.py` / `make` / `./tf` / terraform with `TF_WORKSPACE` + `-var-file=tfvars/<ws>.tfvars`**, runner
   impersonation, never workspace `default`, never bare `terraform` without workspace + tfvars.
5. **Destroy only after cleanup reached `STATUS=DELETED`** — except a pod where Day0 never ran
   (no licenses claimed), and say so in the record.
6. **Never act on a lab with an active booking** (check `bookings.json` and `/lab/status`
   reservation user + window) unless the owner names that lab and accepts the impact.
7. **Secrets by name only.** Never print, log, or paste a value. Read secrets inside the pod.
8. **Never invent** an IP, TSG, VM name or device address. Read `labs.json` / `design.json`.
9. **No new fields in `design.json`.** Mutate existing keys only.
10. **Never close/reopen the GNS3 project, restart GNS3 or ubridge** without an owner plan
    (consoles drop, nodes stop).
11. **Do not resurrect dead features** (Guacamole, Terminal tab, Keycloak, WireGuard, gcloud
    inside cleanup) — `PROJECT_REQUIREMENTS.md` non-goals.
12. **Official repo `SDWAN_LAB`:** no files or commits unless tested and the owner asked.
13. **Never hand-rsync** a Windows checkout to the bucket (CRLF). Use `publish_labapp_release.py`.
14. **Do not undo** lab1 documentation work unless the owner asks.
15. Write every live change as `.ai/changes/CHG-<UTC>-<slug>.md` + a row in `.ai/changelogs.md`
    (template `.ai/changes/_TEMPLATE.md`). Durable findings → `.ai/agents/SHARED_MEMORY.md`.

## Before any live step, say

- the exact target (lab key, lab_id, TSG, VM names, nic1 IPs),
- what will change and how to undo it,
- why it is safe now (no booking, right workspace, gold backed up).
