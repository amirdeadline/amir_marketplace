# 06 — Issues we hit, why, what was fixed, and where

Each row: symptom → root cause → fix and where it lives → status on **2026-10-27**.
"Repo only" means the fix is in the donor tree but not yet in the shared bucket (so live VMs
do not get it). Evidence = CHG ids in `.ai/changes/`.

## A. Boot, network, startup (the current pain)

### I-01 — VM loses `10.0.0.0/8` route, lab unreachable from corp (lab7, 2026-10-27)

- **Symptom:** nic1 SSH / labapp HTTPS time out from the corp network; VM is RUNNING; IAP works.
- **Root cause (proved on lab7):** the route is added with `ip route replace` (by
  `nic1-route-10.service` from Terraform and by the startup `all/host_routes.json`).
  systemd-networkd owns nic1 and deletes "foreign" routes whenever it restarts.
  `unattended-upgrades` runs daily (~06:10–06:45 UTC) and package upgrades restart networkd
  (lab7: libvirt/nginx upgrade at 06:30 UTC 2026-10-27; new networkd PID at 06:31 / 06:10 on
  gns3-2). Nothing puts the route back: `nic1-route-10.service` is a oneshot that already
  ran; its dhclient hook never fires (Ubuntu 22.04 uses networkd, not dhclient); the startup
  runner only runs at boot. The owner re-added it by hand at 17:05 UTC.
- **History:** 2026-10-20 TF route + boot-race fix (CHG-20261020-153700/-145500, release
  8c6550c); 2026-10-22 fleet audit fixed 17 VMs (CHG-20261022-181500); lab12 10-23 —
  all treated the route as a boot problem. It is a **runtime** problem.
- **Fix:** put the route into networkd config so networkd itself re-adds it:
  drop-in `/etc/systemd/network/<10-netplan-IF>.network.d/60-corp-10-8.conf`
  (`[Route] Destination=10.0.0.0/8 Gateway=10.95.98.129 GatewayOnLink=yes Metric=100`).
  Tool: `$LE/scripts/fix_route10_persistent.sh` (dry-run default, `--apply`).
  Permanent product fix still to do: write the same drop-in from
  `terraform/…/scripts/nic1-route-10-install.sh` and from the startup `hostnet` code, then
  publish. Also decide on unattended-upgrades on lab VMs (I-09).
- **Status:** OPEN. Not applied on any VM. Every running pod can lose the route at the next
  upgrade. Interim: a host check that re-adds it (or run the script with `--apply`).

### I-02 — Boot orchestrator (`sase-startup`) does not run on most VMs

- **Symptom:** workers have no `sase-startup.service` at all (lab7 gns3-2: unit missing);
  gns3-1 has an **old-style** unit that calls `labs/scripts/startup.py` directly; launcher
  `/usr/local/sbin/sase-startup-launch.sh` missing everywhere except lab3's new gold.
- **Root cause:** the new mechanism (17 commits on branch `agent/host-bootstrap-startup`,
  CHG-20261022-192500) makes the frozen boot hook
  `terraform/…/scripts/apply-terraform-booking-lab-status.sh` call
  `labs/scripts/startup/bootstrap_host.sh` (commit `d8652ba`). **That branch was never
  published** (publish needed `gcloud auth login`). The bucket hook is still the 2026-10-20
  copy with **no** bootstrap call (checked 2026-10-27: `grep -c bootstrap_host` = 0).
  Only lab3 got it, by a manual `bootstrap_host.sh` run on 2026-10-26, baked into the
  lab3 gold (CHG-20261026-145800 / -154900).
- **Fix:** publish the branch (after review) with
  `python labs/scripts/publish_labapp_release.py --ref agent/host-bootstrap-startup --apply`
  (L2, affects every lab on next boot), prove on dev first, then promote to SDWAN_LAB.
  Per-lab stopgap: run `bash /opt/gns3/shared/lab/labs/scripts/startup/bootstrap_host.sh`
  on all four VMs, then `systemctl enable --now sase-startup`.
- **Status:** OPEN (repo only).

### I-03 — Shared bucket is a mix of releases

`RELEASE.json` says SDWAN_LAB `8c6550c` (2026-10-20), but `labs/scripts/startup/` was
rsynced by hand on 2026-10-26 (VERSION `2026.10.22-1`) and the Terraform `scripts/` folder
is the 10-20 copy. Nobody can say exactly what code a VM runs. **Fix:** one clean publish of a
known ref; never hand-rsync. Status OPEN.

### I-04 — CRLF line endings break boot scripts

- **Seen:** lab11 2026-10-13 (`set -euo pipefail` failed), dev 2026-10-20, lab3 2026-10-26
  (`nic1-route-10-install.sh` CRLF → rendered startup script failed → gcsfuse never mounted →
  no booking, no labapp).
- **Fix:** LF in the donor tree and the SDWAN_LAB copy (SDWAN_LAB not committed);
  `publish_labapp_release.py` normalises to LF; on a broken VM: fetch the metadata script,
  `tr -d '\r'`, run it again (CHG-20261026-142516). Gold-check uploads strip CR (QA-GOLD-02).
- **Status:** fixed in repo; VMs created before the fix keep the old metadata until rebuilt.

### I-05 — Template bug in `mount-shared.sh` comment

Line 22 of `terraform/…/scripts/mount-shared.sh` has `${nic1_route_10_install}` inside a
comment. `templatefile()` expands it, so the whole route fragment is injected into the
comment (runs once more) and the rest of that comment line runs as a command:
`line 73: —: command not found` in every VM's boot log. Harmless today (before
`set -euo pipefail`, exit 0) but fragile. **Fix:** write `$${nic1_route_10_install}` (and the
other two names) in comments. Status OPEN (seen on lab7 2026-10-27).

### I-06 — Lab App on a VM is not the latest

- First boot after apply rebuilds `sase-labapp:dev` (`labapp-compose.sh build --pull`) when
  `LABAPP_REBUILD_IMAGE=true`. On lab3 (2026-10-26) the frontend `npm run build` failed →
  the pod ran a 6-week-old image. On lab7 it worked.
- `LABAPP_RELEASE=current` = whatever was last published (8c6550c, 2026-10-20). Later labapp
  work in the donor tree (Asana Report Issue, robust wipe `agent/robust-lab-wipe`
  01016d1 installed on dev local disk only, CHG-20261026-143512) is **not** in the bucket.
- **Fix:** publish a tested ref; on the VM check `/var/lib/sase-startup/last_applied.json`
  (`release_sha`, `rebuilt`) and `docker images sase-labapp`. Status OPEN.

### I-07 — Failed units on dev (2026-10-27)

`nic1-policy-routing`, `lab-tls-ensure`, `sase-pod-bootstrap`, `cloud-init*`,
`gns3-docker-prune` show `failed` on dev-gns3-1. Not investigated. Policy routing failing
can break replies from nic1. Check with `journalctl -u <unit> -b`.

### I-08 — SSH host key warnings after rebuild

Every new VM has a new host key → "REMOTE HOST IDENTIFICATION HAS CHANGED". Use
`-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null`. Not a security event by itself
when the VM was just rebuilt.

### I-09 — Unattended upgrades restart services on live labs

`unattended-upgrades` and `apt-daily-upgrade.timer` are enabled on lab VMs (dev, lab7).
They upgrade libvirt, nginx, git, systemd pieces during student bookings and restart the
matching services — this is what restarted networkd on lab7 (I-01). Owner decision needed:
disable on lab VMs (and patch in golds on purpose), or keep and make every runtime setting
persistent. Status OPEN.

## B. Identity after convert or snapshot

### I-10 — Donor identity leaks into the new pod

Wrong TLS leaf / boot vault (donor CN), GNS3 computes pointing at donor nic1, nft tables
named `lab8_tap_*` / `lab11_*`, `/etc/hosts` donor blocks, worker `lab_status.json` with
donor lab id/TSG, `gns3-edge-authz` `LAB_ID=lab1/lab2`, oauth2-proxy issuer jumpbox
`10.95.98.150`, underlay/VXLAN peer from the donor, `lab_status.json.bak-*` files with donor
ids. **Fix:** `labs/lab_docs/admin_guide/lab-convert-checklist.md` (BUILD-07…30, P0/P1/P2
tables) with `ensure_host_tls_certs.sh`, `rewrite_boot_vault.sh`, `gns3-tls-materialize.sh`,
`ensure_gns3_computes_nic1.py`, `refresh_lab.py`, `temp/lab12-fix-all-gaps.sh`. Status:
procedure exists; run it every convert.

### I-11 — Booking TSG empty

`TSG_ID=` / `SCM_TSG_ID=` empty in the booking env (lab12 convert, dev today). **Fix:** set
`tsg_id` in `tfvars/<ws>.tfvars` before apply; check `docker exec sase-labapp printenv TSG_ID`.

### I-12 — VFF token minted for the wrong tenant

Fixed CHG-20260917-001226: fresh mint per `LAB_ID` → `labs.json` TSG (unless `--reuse-keys`).
Gold must have `vff_keys={}` and `vff_lab_tsg_id` = own TSG.

### I-13 — Stale lifecycle baked into a gold

A gold with `DAY1_FINISHED`, `lastDay0`, `ion_keys.env`, `LABAPP_BUILD_MODE=auto` makes the
next booking start in a wrong state. **Fix:** `temp/scrub-lab-status-gold.py <key> <id> <tsg> <scenario>`
on all four VMs, identical SHA-256 on all four, NFS copy updated; booking semi-auto.

## C. Day0 / Day1 / devices

- **I-20** Extra ION nodes from tests stall Day0 → skip extras (CHG-20260914-225200).
- **I-21** vION VFF idle timeout → login prompt; Day0 timing (`.ai/knowledge/vion-vff-idle-behavior.md`).
- **I-22** After a cross-lab snapshot, IONs must be recreated (`recreate_ions.py`, 9/9).
- **I-23** Day1 ION claim failure on dev C2 build (CHG-20261020-183600); `POST /lab/day1` retry.
- **I-24** dev Day0 last result `DAY0_FAILED`, `day0_config_status=partial` on disk (2026-10-26). Not analysed.
- **I-25** GNS3 restart drops consoles and can leave 12/52 nodes started → start all nodes;
  never close/reopen the project without the owner.
- **I-26** TLS chain problems on GNS3 :3080 → chain-strip + computes (CHG-20260925-160300).

## D. Cleanup / licenses / SCM

- **I-30** ION retire HTTP 400 `INVALID_OPERATION`; IONs stuck `initialization_failed`;
  nameless ION elements blocked the SD-WAN wipe apply (lab3 2026-10-21). Fix in progress:
  branch `agent/robust-lab-wipe` (`__wipe_rev__ = robust-lab-wipe-2`: deadline, refreshing
  token, final rescan, verify phase, `--skip-site-wipe`) installed on dev local disk only
  (CHG-20261026-143512). Not in the bucket.
- **I-31** License leak: TF destroy without cleanup leaves ION seats allocated (lab3 had 9).
  Retire from the admin dashboard IONs page (owner click).
- **I-32** `RELEASE_PROFILE=full` in the container overrides `labs.json` V1 → pass
  `--release-profile version1.0`.
- **I-33** V1 cleanup leaves Prisma Access SC/IKE/IPsec objects (expected).
- **I-34** SD-WAN wipe domains / DC groups / circuit categories → fixed (CHG-20261012-144500,
  2026-09-12 circuit reset).

## E. GCP / Terraform / workstation

- **I-40** `gcloud` token expires; non-interactive commands fail with "Reauthentication
  failed". Owner runs `gcloud auth login`. Blocked many runs.
- **I-41** N2 CPU quota (`N2_CPUS 736/750`) → half-built pods (2026-09-28: lab5, lab7, lab10).
  Check quota before a build. dev moved to C3 in `us-west2-c`.
- **I-42** `terraform destroy` fails validation when `snapshot_lab_id` is null → `TF_VAR_snapshot_lab_id=<id>`.
- **I-43** Windows `bash.exe` (WSL) cannot see WinGet terraform → `build_lab.py` calls terraform.exe directly.
- **I-44** IAP port formula `20{lab}2{idx}` breaks for lab ≥ 10 → `20000+100*id+20+idx`.
- **I-45** gcsfuse "too many open files" on rename, and SQLite journals on the bucket
  (`labs/logs/fleet/jobs/jobs.db-journal`) → keep databases on local disk (admin ADR-008).
- **I-46** Docker bridge containers on dev-gns3-1 cannot reach the metadata DNS
  (169.254.169.254) → admin image builds with `--network host` (2026-10-27). Host cause unknown.

## F. Registry / process

- **I-50** `labs.json` problems R-1…R-8 (`02-fleet-registry.md`), incl. invalid nic1 IPs for
  lab19–25 and duplicate SC FQDNs on lab6/7/9.
- **I-51** Lab Hub keeps its own `labs.json` → `--sync-hub` (CHG-20261007-171500).
- **I-52** Asana issue tracker built but not live (needs bot token, `asana-issues-token`
  secret, env-sync entry, labapp redeploy) — `docs/lab_issue_tracker.md`.
- **I-53** Admin dashboard GCP credential: SA keys blocked by org → see `05` §6.
- **I-54** Large uncommitted working tree in the donor repo; official repo push was blocked
  in September. Know which branch you are on before you publish.
- **I-55** dev gold 2026-10-26: `sase-labapp` was **disabled** before the cut and re-enabled
  after. A pod built from that gold may come up with labapp disabled — verify on the next dev
  build (`systemctl is-enabled sase-labapp`). For other golds: stop labapp, keep it enabled.
