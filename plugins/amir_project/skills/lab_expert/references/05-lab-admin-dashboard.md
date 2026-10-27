# 05 — Lab admin dashboard (saselab-admin): complete guide

One page per question: what it is, how to use it, how to run and fix it. State as of
**2026-10-27, version 202610271650**.

## 1. What it is

A fleet dashboard for every lab in `labs.json`. It shows which pods exist, whether each VM
answers, where each lab is in its lifecycle, bookings, SD-WAN IONs per tenant, open issues
and logs. It can run a few recovery actions on one lab at a time.

| Item | Value |
|---|---|
| URL | `https://srv1.dev.saselab.paloaltonetworks.com/labs/` |
| Login | the labapp admin password (`ADMIN_PASS`, same value as on dev's labapp) |
| Runs on | **dev-gns3-1** (10.95.98.171), Docker container `saselab-admin`, `127.0.0.1:8095`, host network |
| Front door | dev's `sase-labapp-nginx` proxies `/labs/` → `127.0.0.1:8095` (one nginx, ADR-001) |
| Code | `docker/lab-admin/` on branch `feature/admin-dashboard` (worktree `.claude/worktrees/compassionate-northcutt-37b611`), never pushed; product repo GitLab `code.pan.run/arashidi/saselab-admin` (`main` = 13c0f16) |
| Stack | Node 24, Fastify, React 19 + Vite, Tailwind 4, TanStack Query, zod, SQLite (node:sqlite), Vitest |
| Design record | `.ai/0lead/docs/lab-admin/` (MASTER_PROMPT_v2, DECISIONS ADR-001..016, GLOSSARY) |

## 2. Pages

| Page | What you see / do |
|---|---|
| **Fleet** | one row per provisioned lab. Columns: key, Enabled, fleet status (Good / Error / Stopped / Destroyed / Unknown), **Lifecycle** chips `Boot · Day0 · Day1 · Del`, **VMs** (numbered squares), golden snapshot, labapp, STATUS / READY, scenario, **Booked**, Start Time, End Time, TSG, TenantID, **Actions ⋮**. Click a row for the lab drawer. Labs with no TSG (lab24, lab25 and any null) sit in a collapsed **Unprovisioned** table and are never probed |
| **Lab drawer** | recovery actions, lifecycle table (phase, state, time, error, source, "open log"), registry card + guard result, full `/lab/status` card, phase table of every `last*` key, licensing tables (`panos[]`, `ions[]`), cleanup request, VM table (nic0, nic1, IAP, snapshot), recent jobs, **log viewer** |
| **Bookings** | Lab Hub's `bookings.json` as Month / Week / List; lab picker; click a bar for the full record |
| **IONs** | every Prisma SD-WAN machine per lab tenant, read **from SCM only** (claimed / unclaimed / free / connected, serial, site, element). Refresh one lab or scan all. **Retire** one ION (dry-run plan first) |
| **Issues** | derived problems, one row per `lab|kind|subject`, auto-resolve when the condition clears; History keeps resolved ones |
| **Jobs** | every action run with state, params, transcript (secrets redacted) |
| **Audit** | append-only log of logins, actions, settings and labs.json writes |
| **Settings** | GCP credential, impersonation target, check intervals, thresholds, webhook, saved table views |

### Colours

- **VM square** green = answers (ICMP on nic1 or labapp replied); red = exists but silent /
  stopped / error; grey = does not exist or nothing observed; dashed grey = never built.
- **Fleet status**: Good needs network evidence; all four silent and no booking = Stopped;
  all four silent during a booking = Error; Destroyed = every instance gone or STATUS=DELETED.
- **Lifecycle chip**: green ok, red failed (hover for error + source + time), amber running,
  grey not started / unknown. A newer `ERROR`/`Traceback` line in that phase's log also turns
  it red (source `log:<file>`).

## 3. Using the tables

- **⋮ in the Actions column**: Retry Day0, Retry Day1, Flag Lab ready, then (red) Retry Delete
  and Wipe SDWAN, then Details. Greyed out when the lab has no gns3-1 nic1 in `labs.json`.
- **Columns** button: show/hide each column and pick **Clip** (one line, cut at the edge) or
  **Wrap** (row grows to show all) per column. Lifecycle and VMs wrap by default.
- Header menu ⋮ per column: move left/right, hide, auto width, Wrap text / Clip text.
- Drag a header to reorder, drag its right edge to resize, one filter box per column.
- **Reset view** returns order, widths, filters, hidden columns and wrap to defaults.
- Views are saved per table on the server (`settings.enc`) and in your browser.

## 4. Actions and their gates

Every action passes the TSG guard first: parent TSG `1479602777` refused, only the lab's own
registry TSG, null TSG refused. Every dialog opens with a **target box** (lab key, lab_id,
name, TSG ID/name, tenant, gns3-1 nic1, what will be sent). One running job per lab.

| Action | What it does | Gate |
|---|---|---|
| Retry Day0 | `POST /lab/day0` on the pod, follows STATUS (409 = pod busy) | confirm dialog |
| Retry Day1 | `POST /lab/day1 {scenario}`; scenario prefilled from pod / booking; follows to `DAY1_FINISHED` (60 min) | confirm |
| Flag Lab ready | `PUT /lab/admin/status` (DAY1_FINISHED, READY, HEALTHY, admin_override) → verify → writes `labs.json` `enabled=true`, `status=active`, every `vms.*.status=ok` (backup first, tmp + rename) | confirm |
| Retry Delete | labapp cleanup: dry-run first; apply needs a successful dry-run in the last 24 h **and** the lab key typed. Terraform destroy stays manual | dry-run + typed key |
| Wipe SDWAN | runs `python3 -m lab_automation scm-cleanup --lab <key> --product sdwan` **inside the admin container** (shared-drive code, SCM creds from labapp env); dry-run then apply | dry-run ≤ 24 h + typed key; product `sdwan` only |
| Retire ION (IONs page) | `ion_ops.py retire`: unassign element → put back → return → retire; dry-run plan first | typed key |
| VM start / stop | GCP Compute | needs a GCP credential |
| Rebuild / reimage | visible, disabled (403 "requires owner approval (L3)") | `SASELAB_ADMIN_ENABLE_L3=false` |

The owner clicks these. An agent may **read** the dashboard; it must not trigger an action
unless the owner asked for that exact action on that exact lab.

## 5. How it checks the fleet

Three loops (Settings, no restart needed): **full check** every 10 min (re-read labs.json +
bookings.json → GCP inventory → API + ICMP → deep sweep `/lab/licensing`, `/lab/day0`,
`/lab/day1`, `/lab/destroy` → log scan → lifecycle → issues), **ICMP** every 30 s,
**labapp API** (`GET /lab/status`) every 30 s. **Refresh now** = full check.

Issue kinds: `credential_missing`, `labapp_unreachable`, `admin_pass_mismatch`,
`probe_failed`, `vm_not_running`, `vm_stopped_idle`, `vm_missing`, `not_ready_after_start`
(30 min grace), `lifecycle_failed`, `status_error`, `booking_failed`, `booking_overrun`,
`job_failed`, `job_stuck`, `guard_refused`, `registry_inconsistent`, `audit_fallback`.

## 6. GCP credential (open problem)

Without a GCP credential the header says "GCP credential missing": power state and golden
snapshot columns are unknown, VM colours come from ICMP only, VM start/stop is off.

Original plan (ADR-006): paste a service-account key for the Terraform runner in
Settings. **The org blocks service-account key creation**
(`constraints/iam.managed.disableServiceAccountKeyCreation`). On 2026-10-27 Roberto
created `lab-admin-dashboard-sa@sase-lab-sdwan.iam.gserviceaccount.com` with
`roles/logging.viewer` on the project, plus `roles/iam.serviceAccountTokenCreator` and
`roles/iam.serviceAccountUser` on `gns3-terraform-runner` only.

Without a key, the dashboard can only sign in as the service account **attached to the
machine it runs on**, then swap that for a runner token. dev-gns3-1 runs as `gns3-lab-sa`,
which every lab VM shares, so the new account cannot be used there. Options:

1. **Move the dashboard to its own small VM** with `lab-admin-dashboard-sa` attached
   (recommended). It also needs read/write on the shared bucket, `secretAccessor` on
   `admin-pass`, `scm-client-id`, `scm-client-secret`, `cloudgenix-auth-token`, and a nic on
   the `10.95.98.128/25` network. Installer supports it: `SASELAB_ADMIN_ANY_HOST=1 SRC=<clone> bash scripts/install-dev.sh`.
2. Code change still needed either way: the credential resolver knows env token → stored key
   → none. It must learn **ADC from the metadata server** (then impersonate the runner;
   read Cloud Logging as the dashboard account itself, because the runner has no logging role).
3. Short-term: the owner can paste a short-lived token (`GOOGLE_OAUTH_ACCESS_TOKEN`) — expires in 1 h.

## 7. Operate it (on dev-gns3-1)

| Task | Command |
|---|---|
| Health | `curl -k https://127.0.0.1/labs/health` or `curl http://127.0.0.1:8095/health` |
| Service | `systemctl status saselab-admin` (oneshot, `active (exited)` when healthy) |
| Container | `docker ps --filter name=saselab-admin`; `docker logs -f saselab-admin` |
| Env | `/run/saselab-admin/saselab-admin.env` (0600) written by `scripts/env-sync.sh` from `/run/labapp/labapp.env` (fallback Secret Manager / `override.env`) |
| State | `/var/lib/saselab-admin/`: `jobs.db`, `issues.db`, `settings.enc` (AES-256-GCM), `ions/<lab>.json`, `audit-fallback/` |
| Audit | `/opt/gns3/shared/lab/labs/logs/fleet/audit/audit-YYYY-MM-DD.jsonl` |
| labs.json backups | `/opt/gns3/shared/lab/labs/logs/fleet/registry-backups/` |
| Smoke | `cd /etc/saselab-admin/docker/lab-admin && BASE=https://127.0.0.1 bash scripts/smoke.sh` |
| Rollback | `bash /etc/saselab-admin/docker/lab-admin/scripts/rollback.sh` (re-tags `saselab-admin:prev`) |

### Deploy a new version (owner-approved, L2)

From the workstation, in the worktree:

```bash
cd .claude/worktrees/compassionate-northcutt-37b611
(cd docker/lab-admin && npm test && npm run typecheck && npm run build)     # must pass
git archive HEAD docker/lab-admin | ssh -i ~/.ssh/sdwan root@10.95.98.171 \
  'rm -rf /opt/gns3/shared/lab/docker/lab-admin && tar -x -C /opt/gns3/shared/lab'
ssh -i ~/.ssh/sdwan root@10.95.98.171 \
  'nohup bash /opt/gns3/shared/lab/docker/lab-admin/scripts/install-dev.sh > /tmp/install-admin.log 2>&1 &'
# wait, then smoke (above). Detach ONLY the installer: backgrounding the rm+tar chain once deleted the copy.
```

The installer copies to `/etc/saselab-admin/docker/lab-admin`, tags the old image `prev`,
builds `saselab-admin:dev` with `--network host` (bridge containers on dev-gns3-1 cannot
reach the metadata DNS, 2026-10-27), installs the unit, runs env-sync, restarts.

Publish to GitLab after a tested change:

```bash
git branch -D lab-admin-main; git subtree split --prefix=docker/lab-admin -b lab-admin-main
git push lab-admin lab-admin-main:main      # retry on "connection refused"
```

### Develop / test locally

```bash
cd docker/lab-admin && npm install && npm test && npm run typecheck && npm run build
ADMIN_PASS=<throwaway> LABS_CONFIG_PATH=<fixture with TEST-NET 192.0.2.x IPs> \
SASELAB_ADMIN_STATE_DIR=/tmp/sa SASELAB_ADMIN_COOKIE_SECURE=false SASELAB_ADMIN_WEB_DIST=web/dist \
node server/dist/main.js        # http://127.0.0.1:8095/
```

Never point a local test at real pod IPs (an early test pinged the real dev pod).

## 8. Troubleshoot the dashboard

| Symptom | Check |
|---|---|
| Page 502 / blank | `docker ps` (container up?), `curl 127.0.0.1:8095/health`, nginx `/labs/` location in dev labapp nginx |
| Login fails | `ADMIN_PASS` in `/run/saselab-admin/saselab-admin.env` must equal labapp's; re-run `scripts/env-sync.sh` (quoting bug fixed 2026-10-21) |
| Every lab grey / "probe_failed" | dev-gns3-1 lost its 10/8 route or nic1 policy routing (`ip route show 10.0.0.0/8`) |
| GCP columns unknown | expected until §6 is solved |
| Wipe SDWAN fails at start | SCM creds missing in the admin env; shared-drive `lab_automation` changed; read the job transcript |
| Image build fails "DNS: transient error" | build must use `--network host` (installer does since 2026-10-27) |
| Issues never resolve | check the full-check age in the header; a stuck loop shows `running` for long |

## 9. API (for scripts; cookie or `X-Admin-Password`)

`GET /labs/api/fleet`, `POST /labs/api/fleet/refresh`, `GET /labs/api/labs/:key/logs[/stream|/download]`,
`GET /labs/api/bookings`, `GET /labs/api/issues[?status=open]`, `GET /labs/api/issues/summary`,
`GET /labs/api/jobs[?type=]`, `POST /labs/api/jobs`, `GET /labs/api/ions`, `GET /labs/api/ions/:lab`,
`GET/PUT /labs/api/settings`, `GET /labs/api/views`, `PUT /labs/api/views/:tableId`, `GET /labs/health`.
Mutating routes need the CSRF header when using the cookie.
