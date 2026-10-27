# 01 — Architecture of the Prisma SASE lab platform

Facts checked against code, `labs/labs.json` and live hosts on **2026-10-27**. Where a fact
was not checked live, it says so. Live systems always win over this file.

## 1. What the platform is

Bookable Prisma SASE training labs on Google Cloud. A student books a lab in **Lab Hub**
(App Engine, owned by another team). Hub runs Terraform from this platform at the start
time, the lab builds itself, the student works in it, and at the end time it is cleaned
and destroyed.

One **lab pod** is:

| Piece | Count | Name pattern |
|---|---|---|
| GNS3 server VMs | 4 | `lab-N-gns3-1..4` (dev: `dev-gns3-1..4`) |
| Lab VPC (nic0 underlay) | 1 | `lab-N-gns3-lab-vpc` |
| SCM tenant (TSG) | 1 | `COE-SASE-LAB-PLATFORM-NN` (dev: `-dev`) |
| Terraform workspace | 1 | `lab-N` (dev: `dev`) |
| Golden snapshots | 4 | `gns3-{1..4}-lab{N}-snapshot` (dev = `lab0`) |
| labapp (student web app + lifecycle API) | 1 | Docker `sase-labapp` on gns3-1 |

`labs/labs.json` holds 26 entries: `dev` (lab_id 0) and `lab1`..`lab25`. Lab Hub books
**lab1–lab10** (decision D-038). `dev` is for development. lab11+ are extra pods (some have
TSGs, none are Hub-bookable today).

## 2. Big picture

```text
Student / operator (corp network 10.0.0.0/8, VPN)
        |  HTTPS / SSH to nic1 (10.95.98.x)  — needs the 10/8 route on every VM
        v
+--------------------------- one lab pod (GCP sase-lab-sdwan, us-west2) --------------------------+
|  gns3-1 (hub)                     gns3-2            gns3-3                 gns3-4               |
|  - GNS3 controller + DC1 nodes    DC2 nodes         Boston + Internet      Dallas + Atlanta     |
|  - labapp (Docker, host net)                                                                     |
|    nginx :443 -> uvicorn :8082                                                                   |
|  - br-lab11 10.10.0.1/30 -> GCP cloud node -> GCP-Router 10.10.99.1 -> OOB 10.10.99.0/24        |
|  nic0 10.100.20.11  ------------- 10.100.20.12 ----- 10.100.20.13 -------- 10.100.20.14         |
|        VXLAN overlay 172.31.255.0/24, hub-and-spoke from gns3-1 (GNS3 L2 links between hosts)   |
+-------------------------------------------------------------------------------------------------+
        |  gcsfuse on every VM: gs://sase-lab-sdwan-gns3-shared  ->  /opt/gns3/shared
        |  Secret Manager (sase-lab-sdwan) -> labapp-env-sync.sh -> /etc/labapp/labapp.env
        |  SCM APIs (Prisma SD-WAN / Prisma Access / CSP) from labapp container
        v
Strata Cloud Manager tenant (one TSG per lab, child of parent TSG 1479602777)
```

## 3. Three networks — never mix them

| Plane | Addresses | Purpose | Reachable from your PC? |
|---|---|---|---|
| **nic0** | `10.100.20.11..14` (same in every lab) | underlay between the 4 VMs of ONE pod, GNS3 API between them, VXLAN | No |
| **nic1** | `10.95.98.x`, unique per VM (`labs.json`), subnet `10.95.98.128/25`, gateway `10.95.98.129` | labapp HTTPS, GNS3 API/consoles for students, SSH from operators, DNAT to devices | Yes, **only if the VM has `10.0.0.0/8 via 10.95.98.129` on nic1** |
| **OOB** | `10.10.99.0/24` (device management inside the topology) | NGFW / ION / VyOS / hosts management | No. Only from that pod's gns3-1 (or labapp container) |

Also on gns3-1: `br-lab11` `10.10.0.1/30` (bridge to the GNS3 "cloud" node), VXLAN
`172.31.255.1/24` (`vx-g2..4`). Workers: `172.31.255.2..4`, `vx-g1`.

NIC names: N2 machines show nic0 = `ens4`, nic1 = `ens5`. **dev runs on C3
(`c3-standard-22`, zone `us-west2-c`) where nic0 = `eth0` and nic1 = `ens4`.** Never assume
the interface name; find the one holding the `10.95.98.x` address.

## 4. GCP and Terraform

| Item | Value |
|---|---|
| Project | `sase-lab-sdwan` |
| Zone | `us-west2-a` for lab1+ (dev moved to `us-west2-c` on 2026-10-21; `labs.json` still says `-a`) |
| Machine types (build_lab defaults) | gns3-1, gns3-2 `n2-standard-32`; gns3-3, gns3-4 `n2-standard-16` |
| N2 CPU quota | ~750 in region; 2026-09-28 fleet rebuild hit `N2_CPUS 736/750` (labs 5, 7, 10 half-built) |
| Terraform stack | `labs/lab_automation/terraform/gcp-eve-ng-test-instance-feature-gns3-greenfield-merge/` |
| State | `gs://sase-lab-sdwan-tfstate/gns3-lab/<workspace>.tfstate` |
| Workspaces | `dev`, `lab-1` … `lab-N`, `shared`. **Never `default`. There is no `dest`.** |
| Terraform identity | impersonate `gns3-terraform-runner@sase-lab-sdwan.iam.gserviceaccount.com` |
| VM identity | `gns3-lab-sa@…` on every lab VM (bucket + Secret Manager). Never use it for Terraform. |
| Admin dashboard identity (new 2026-10-27) | `lab-admin-dashboard-sa@…`: logging.viewer + token creator on the runner. Org blocks SA keys, so it works only where it is the attached SA (not on dev-gns3-1). |
| Wrapper | `make` / `./tf` in the stack, or `labs/scripts/build_lab.py` (Hub stand-in, calls terraform.exe with workspace + `tfvars/<ws>.tfvars`) |
| Typical apply | 49 resources (4 VMs, disks, VPC, NAT, firewall, booking object, …); destroy 48–49 |
| Goldens | not Terraform-managed; destroy keeps them on purpose |

`metadata_startup_script` (the rendered `scripts/mount-shared.sh`) is in `ignore_changes`.
A change to it reaches only **new** VMs. Every Terraform build is a new VM, so the next
build of a lab picks it up.

## 5. The shared tree (gcsfuse "NFS")

Bucket `gs://sase-lab-sdwan-gns3-shared`, mounted read-write at `/opt/gns3/shared` on every
VM (fstab line, `opt-gns3-shared.mount`). Path `/opt/gns3/shared/lab` is the **live code**:

| Path under `/opt/gns3/shared/lab` | What |
|---|---|
| `RELEASE.json` | which git commit was published (sha, subject, publisher, `repo`) |
| `docker/labapp/` | labapp source, compose, scripts (copied to `/etc/labapp` on each labapp start) |
| `docker/labapp/<workspace>/.env` | **booking env** written by Terraform (`dev/.env`, `lab-7/.env`) |
| `labs/lab_automation/src` | lifecycle Python used by labapp and the admin dashboard |
| `labs/lab_automation/terraform/…/scripts/` | host scripts, incl. the frozen boot hook `apply-terraform-booking-lab-status.sh` |
| `labs/scripts/startup/` | boot orchestrator (`run_startup.py`, `all/`, `gns3-1/`, `other_gns3/`, `bootstrap_host.sh`, `VERSION`) |
| `labs/labs.json` | runtime registry (can differ from the git copy — compare MD5) |
| `labs/bookings.json` | Lab Hub bookings (read-only for us) |
| `labs/logs/labs/<lab_id>/` | per-lab logs: `gns3/*.log`, `gns3/lab_status.json` copy, `<hostname>-startup.log` |
| `labs/logs/fleet/` | admin dashboard audit, incidents, registry backups |

The **only supported way** to update this tree is
`python labs/scripts/publish_labapp_release.py --ref <ref> [--apply]` (git archive → LF →
rsync with delete → `RELEASE.json`). Never rsync from a Windows checkout by hand: CRLF
breaks bash (`set -euo pipefail`) on the VMs.

Live state 2026-10-27: `RELEASE.json` = SDWAN_LAB `8c6550c` (2026-10-20, "permanent 10/8
route via nic1"). But `labs/scripts/startup/` was rsynced by hand on 2026-10-26 (VERSION
`2026.10.22-1`) while the Terraform `scripts/` folder (boot hook) is still the 10-20 copy.
The bucket is a **mix**; see 06-issues (I-03).

## 6. Secrets (names only — never print values)

| Group | Names | Where |
|---|---|---|
| A — long-lived secrets | `admin-pass` (ADMIN_PASS), `scm-client-id`, `scm-client-secret`, `cloudgenix-auth-token`, `csp-api-key`, `ssl-certificate` | Secret Manager |
| Per lab | `lab_{id}_pass` (USER_PASSWORD, student), `{labkey}-srv{i}-cert`, `{labkey}-srv{i}-cert-password` | Secret Manager |
| B — booking | `LAB_ID`, `SCENARIO_ID`, `RESERVATION_USER`, `RESERVATION_ID`, `START_TIME`, `END_TIME`, `LABAPP_BUILD_MODE`, `LABAPP_AUTO_DAY0/1`, `TSG_ID`, `SCM_TSG_ID`, `LAB_ADDRESS`, `RELEASE_PROFILE`, `LABAPP_RELEASE`, `LABAPP_REBUILD_IMAGE`, `LABAPP_APPLY_ID` | Terraform → booking `.env` in the bucket |

`labapp-env-sync.sh` (Terraform scripts folder) merges A + B into `/etc/labapp/labapp.env`
(0600) and `/run/labapp/labapp.env`. Secrets never go to tfstate, git, `labs.json`, logs.

## 7. Boot chain (what runs when a VM starts)

```text
GCE boot -> network (systemd-networkd; netplan generated by google-guest-agent)
  -> google-startup-scripts: metadata startup-script = rendered mount-shared.sh (fixed at VM create)
       - root SSH key, nic1-route-10 install (route + service + dhclient hook)
       - fstab gcsfuse line, mount /opt/gns3/shared
       - writes OLD-style sase-startup.service (gns3-1 only) + labapp drop-in (Requires sase-startup)
       - runs bucket hook  .../scripts/apply-terraform-booking-lab-status.sh   (frozen path)
             NEW (repo, branch agent/host-bootstrap-startup, NOT yet in bucket):
             -> labs/scripts/startup/bootstrap_host.sh -> launcher + unit on ALL 4 VMs
  -> sase-startup.service -> run_startup.py
       all/startup_all.py       routes from all/host_routes.json (corp-10-8 via nic1)
       gns3-1/startup.py        labapp release gate (LABAPP_RELEASE vs RELEASE.json) + image rebuild
       other_gns3/...           worker tasks (placeholder)
  -> sase-labapp.service (gns3-1): labapp-env-sync.sh -> labapp-compose.sh up
       containers: sase-labapp, sase-labapp-nginx, sase-lab-assistant
  -> labapp first-time boot (FTB): TLS names, GNS3 computes on nic1, leftover STATUS wipe
  -> STATUS=START; auto mode chains Day0 -> Day1; semi-auto waits for POST /lab/day0, /lab/day1
```

Kill switch: `"startup_enabled": false` at the top of the bucket `labs.json`.

## 8. labapp (per pod)

- Source `docker/labapp/` (FastAPI + React 19). Image `sase-labapp:dev`, host network.
- uvicorn `127.0.0.1:8082`; `sase-labapp-nginx` TLS on nic1 `:443` (and `:9443`).
- Student login = reservation user + `USER_PASSWORD`. Admin = `X-Admin-Password: ADMIN_PASS`.
- Tabs: Lab Detail, GNS3 Guide, Devices, Admin (+ Report Issue / Asana, not live yet).
- Lifecycle REST: `GET /lab/status`, `POST /lab/day0`, `POST /lab/day1 {scenario}`,
  `POST /lab/destroy` (= cleanup, NOT Terraform), `GET /lab/licensing`, `/lab/qa/smoke`,
  `PUT /lab/admin/status`, `POST /lab/refresh`. OpenAPI: `labs/lab_docs/lab_app_openapi.json`.
- Shells out to `python3 -m lab_automation <verb>` inside the container (`/labs` mount).
- State file: `/etc/labapp/lab_status.json` (+ NFS copy under `labs/logs/labs/<id>/gns3/`).

## 9. lab_automation (Python lifecycle)

`labs/lab_automation/src/lab_automation`. CLI `python -m lab_automation <verb>`: `status`,
`day0`, `day1`, `destroy`/`cleanup` (dry-run unless `--apply`), `scm-cleanup`,
`ions-activate`, `ngfw-activate`, `qa-smoke`, `issues`, `ion-image-upgrade`.
SCM safety: `ops/scm/guards.py` (parent TSG refuse, only registry TSGs).
Wipe baselines: `labs/day0_config/scm/`. Day1 gold YAML:
`labs/designs/prisma-sase-basic/final_config/prisma_sdwan/`.

## 10. Topology (design `prisma-sase-basic`, GNS3 project `Prisma-SASE-Basic`)

- 52 nodes when started (convert/start); 7 NGFW (PAN-OS), 9 vIONs
  (`3102v/3108v-6.5.3-b16`), VyOS routers, Windows DCs, Linux servers, webterm PCs.
- Compute placement: DC1 → gns3-1, DC2 → gns3-2, Boston + Internet → gns3-3,
  Dallas + Atlanta → gns3-4.
- Site codes: DC1=11 (NY), DC2=12 (LA), BOS=101, DAL=102, ATL=103.
- `labs/designs/prisma-sase-basic/design.json`: OOB IPs, DNAT `assigned_ports`
  (5000–5500 on gns3-1 nic1). **Never add fields to design.json.**
- Scenarios: **11** SD-WAN Basic (Day1 = no-op), **13** Complete (Day1 = full SD-WAN site
  snapshots). 10 disabled, 12 not a product.

## 11. Repos

| Tree | Role |
|---|---|
| `E:\PC3_Shared\Palo\COE\Prisma_SASE_LAB\PaloAlto_SASE_LAB` | donor / daily work (this tree). Main checkout on branch `agent/host-bootstrap-startup` (2026-10-27), large uncommitted changes |
| `SDWAN_LAB/` (GitLab `prisma-sdwan-lab`) | **official product** (D-042). Only tested work, only when the owner asks |
| `.claude/worktrees/compassionate-northcutt-37b611` branch `feature/admin-dashboard` | admin dashboard source `docker/lab-admin/` (local only, never pushed) |
| GitLab `code.pan.run/arashidi/saselab-admin` | admin dashboard repo (subtree split of `docker/lab-admin`) |
| Lab Hub | other team; not in any of these trees |
