# 03 — Access: SSH to any VM, and how to get data on any lab

Workstation: Windows jumpbox, repo `E:\PC3_Shared\Palo\COE\Prisma_SASE_LAB\PaloAlto_SASE_LAB`,
Git Bash + PowerShell, SSH key `C:\Users\amir\.ssh\sdwan` (Git Bash: `/c/Users/amir/.ssh/sdwan`).
Get every address with `python $LE/scripts/lab_facts.py <lab>`.

## 1. SSH to a GNS3 VM

**Path A — nic1 (try first).** User `root`, port 22, nic1 IP from `labs.json`.
Host keys change on every rebuild, so do not let `known_hosts` block you:

```bash
ssh -i /c/Users/amir/.ssh/sdwan -o IdentitiesOnly=yes -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10 root@10.95.98.194
```

Run one command without a shell: append `'<command>'`. Pipe a local script:
`ssh … root@<nic1> 'bash -s' -- <args> < script.sh`.

nic1 SSH fails when the VM has no `10.0.0.0/8 via 10.95.98.129` route (I-01), is stopped,
or does not exist. Then use:

**Path B — IAP tunnel.** Needs `gcloud auth login` (human account) on the workstation.

```bash
# one tunnel by hand (lab7 gns3-1 -> local 20721)
gcloud compute start-iap-tunnel lab-7-gns3-1 22 --local-host-port=localhost:20721 \
    --zone us-west2-a --project sase-lab-sdwan &
ssh -i /c/Users/amir/.ssh/sdwan -p 20721 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@127.0.0.1
# or all four VMs of several labs (keeps running until Ctrl+C)
python dev/scripts/start_gcp_tunnels.py --lab 7 --ssh
```

Port = `20000 + 100*lab_id + 20 + vm_index` (lab10 gns3-1 = 21021). dev uses zone
`us-west2-c`. Older docs say `20{lab}2{idx}`; that breaks for lab_id ≥ 10 — use the formula.

**Path C — GCP serial console / guest attributes** when neither SSH path works:
`gcloud compute instances get-serial-port-output lab-7-gns3-1 --zone us-west2-a --project sase-lab-sdwan | tail -200`.

**Inside a pod**: from gns3-1 you reach nic0 of the other three (`10.100.20.12..14`) and
the OOB devices `10.10.99.x`. Device IPs and credentials (names only) are in
`labs/designs/prisma-sase-basic/design.json` → `oob_management`. Never guess a device IP.

## 2. GCP auth (needed for gcloud, Terraform, snapshots)

```powershell
gcloud auth login                 # interactive, the owner does it; tokens expire ~daily
$env:GOOGLE_OAUTH_ACCESS_TOKEN = (gcloud auth print-access-token `
   --impersonate-service-account=gns3-terraform-runner@sase-lab-sdwan.iam.gserviceaccount.com)
```

If a command says "Reauthentication failed. cannot prompt during non-interactive
execution", stop and ask the owner to run `gcloud auth login`. This blocked many runs
(CHG-20261020-213000, -20261021-120000, -20260925-202500).

Read-only GCP facts:

```bash
P="--project sase-lab-sdwan"
gcloud compute instances list $P --filter="name~'^lab-7-gns3-'" \
  --format="table(name,zone.basename(),status,machineType.basename(),creationTimestamp,networkInterfaces[1].networkIP)"
gcloud compute disks list $P --filter="name~'^lab-7-gns3-'" --format="table(name,sourceSnapshot.basename(),sizeGb)"
gcloud compute snapshots list $P --filter="name~'lab7-snapshot'" --format="table(name,status,creationTimestamp,diskSizeGb)"
gcloud logging read 'resource.type="gce_instance" AND resource.labels.instance_id="<id>"' $P --limit 50 --freshness 1d
gcloud compute regions describe us-west2 $P --format="table(quotas.metric,quotas.usage,quotas.limit)" | grep -i n2_cpus
```

## 3. labapp API (per pod)

`https://<gns3-1 nic1>/…` Lifecycle endpoints need `X-Admin-Password`. **Never print the
password.** Read it on the pod and call localhost there:

```bash
ssh … root@<gns3-1 nic1> 'P=$(grep ^ADMIN_PASS= /run/labapp/labapp.env | cut -d= -f2-);
  curl -ks -H "X-Admin-Password: $P" https://127.0.0.1/lab/status | python3 -m json.tool'
```

| GET | What |
|---|---|
| `/health/live` (no auth) | labapp up? |
| `/lab/status` | STATUS, READY, HEALTHY, scenario, user, build mode, day0/day1 status, `last*` phases |
| `/lab/licensing` | NGFW (`panos[]`) and ION (`ions[]`) license state |
| `/lab/day0`, `/lab/day1`, `/lab/destroy` | last request / progress of that phase |
| `/lab/config` | booking config (START_TIME/END_TIME …) |
| `/lab/qa/smoke` | smoke QA (OOB ping matrix, GNS3 project, HTTPS) |

POST endpoints (`/lab/day0`, `/lab/day1`, `/lab/destroy`, `/lab/refresh`,
`PUT /lab/admin/status`) change the lab — only with owner approval (see 08-rules).

## 4. Data on the VM (read-only)

Fastest: run the collector, it prints identity, routes, mount, units, boot orchestrator,
booking keys (non-secret), lab_status fields, foreign-TSG leaks, containers, TLS, logs:

```bash
F=$(python $LE/scripts/lab_facts.py lab7 --json | python -c "import json,sys;print(' '.join(json.load(sys.stdin)['foreign_tsgs']))")
ssh … root@10.95.98.194 'bash -s' -- lab7 7 1880230960 "$F" < $LE/scripts/collect_vm_evidence.sh > ev-lab7-g1.txt
```

Key files on a VM:

| Path | What |
|---|---|
| `/etc/labapp/lab_status.json` | lifecycle state (all 4 VMs keep a copy; gns3-1 is the truth) |
| `/etc/labapp/labapp.env`, `/run/labapp/labapp.env` | merged env (secrets inside — grep key names only) |
| `/var/lib/sase-startup/last_run.json`, `last_applied.json` | boot orchestrator result |
| `/var/log/sase-startup/startup.log` | boot orchestrator log |
| `/var/lib/sase-labapp/lifecycle/ion_keys.env` | ION keys sidecar (must be absent in a gold) |
| `/etc/gns3/certs/web/server.crt` | GNS3/labapp TLS leaf |
| `/etc/nftables.conf`, `nft list tables` | DNAT / underlay / VXLAN rules |
| `journalctl -u sase-startup / sase-labapp / google-startup-scripts / systemd-networkd` | boot and service logs |
| `/var/log/apt/history.log` | unattended upgrades (cause of networkd restarts) |

Inside the labapp container:

```bash
docker exec sase-labapp printenv LAB_ID TSG_ID SCM_TSG_ID TSG_NAME SCENARIO_ID LABAPP_BUILD_MODE
docker exec sase-labapp python3 -m lab_automation qa-smoke --lab lab7
docker exec sase-labapp python3 -m lab_automation status --lab lab7
docker logs --tail 200 sase-labapp
```

GNS3 API (on gns3-1): `https://127.0.0.1:3080/v2/projects`, `/v2/computes`,
`/v2/projects/<id>/nodes` with Basic auth from container env `GNS3_USERNAME` / `GNS3_PASSWORD`.
Expect project `Prisma-SASE-Basic` opened, 52 nodes started, 4 computes connected on nic1.

## 5. Logs on the shared tree (no SSH to the target needed)

From any GNS3 VM that mounts the bucket (e.g. dev-gns3-1), or with `gcloud storage cat`:

```text
/opt/gns3/shared/lab/labs/logs/labs/<lab_id>/
   <hostname>-startup.log            boot orchestrator copy, per VM
   gns3/day0.log  vion_activate.log  ngfw_licencing.log  scm_day0_config.log
   gns3/sdwan_configure.log (Day1)   cleanup_lab.log  scm_cleanup.log  vion_delicense.log
   gns3/first_time_boot.log  lab_status.json (NFS copy)
gs://sase-lab-sdwan-gns3-shared/lab/labs/logs/labs/<lab_id>/...
```

Live cleanup: start the tail **before** you trigger it (`.cursor/rules/lab-cleanup-live-logs.mdc`).

## 6. SCM (read-only unless the owner says otherwise)

- Admin dashboard **IONs** page (per-lab machines, claimed/unclaimed, retire plan dry-run).
- Inside labapp / admin container: `python3 -m lab_automation scm-cleanup --lab <key> --product sdwan --dry-run`.
- Parent tenant listing: `labs/scripts/scm/list_parent_child_tsgs.py` (read-only).
- Any SCM write = owner approval. Parent TSG `1479602777` = never.

## 7. Fleet view

The admin dashboard (`https://srv1.dev.saselab.paloaltonetworks.com/labs/`) shows all labs,
VM state, lifecycle chips, logs and issues in one place — see `05-lab-admin-dashboard.md`.
