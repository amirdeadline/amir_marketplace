# 04 — Lab lifecycle: build, boot, Day0, Day1, cleanup, destroy

## 1. Life of one booking

```text
Lab Hub booking (lab1..10)  -> Cloud Task at START_TIME
  -> Terraform apply workspace lab-N (4 VMs from gns3-*-labN-snapshot)      ~5–15 min
  -> boot chain (01-architecture §7): mount, routes, sase-startup, labapp
  -> first-time boot (FTB): TLS names, GNS3 computes on THIS lab's nic1, leftover STATUS wipe
  -> STATUS=START
  -> Day0: open GNS3 project, start nodes, mint CloudGenix token, license NGFW + 9 IONs,
           grant the student SCM login                                     -> DAY0_FINISHED
  -> Day1: scenario 11 = nothing; scenario 13 = full SD-WAN config          -> DAY1_FINISHED, READY=True
  -> student works
  -> END_TIME: cleanup (labapp, on gns3-1) -> STATUS=DELETED
  -> Terraform destroy (VMs + VPC gone, goldens stay)
```

Terraform apply finished ≠ student ready. Students wait for `READY=True`.

## 2. Build a pod (Hub stand-in)

```powershell
cd E:\PC3_Shared\Palo\COE\Prisma_SASE_LAB\PaloAlto_SASE_LAB
$env:GOOGLE_OAUTH_ACCESS_TOKEN = (gcloud auth print-access-token --impersonate-service-account=gns3-terraform-runner@sase-lab-sdwan.iam.gserviceaccount.com)
python labs/scripts/build_lab.py --lab lab7 --scenario-id 13 `
  --reservation-user amirr@gatech.edu --reservation-id local-lab7-amirr-<UTCSTAMP> `
  --start-time <now ISO Z> --end-time <+24h ISO Z> --build-mode semi-auto `
  --release-profile version1.0 --print-only          # 1) show the command
#  ... --plan                                          # 2) terraform plan (default)
#  ... --apply --yes                                   # 3) LIVE apply
```

Flags: `--snapshot-lab-id <id>` (boot from another lab's goldens = convert),
`--vm1-type … --vm4-type`, `--labapp-code-revision <sha>`, `--labs-json <path>`.
Booking vars land in `tfvars/lab-N.tfvars` (gitignored) and in the bucket booking `.env`.
Put `tsg_id` in the tfvars (lab12 convert lesson; dev shows it empty today).

## 3. Build modes (D-040)

| Mode | Booking keys | After FTB |
|---|---|---|
| `semi-auto` (Hub default) | `LABAPP_BUILD_MODE=semi-auto`, `LABAPP_AUTO_DAY0=false`, `LABAPP_AUTO_DAY1=false` | waits; someone POSTs `/lab/day0` then `/lab/day1` |
| `auto` | `LABAPP_BUILD_MODE=auto`, auto flags true | labapp chains Day0 → Day1 |

**Gold snapshots must be cut in semi-auto with STATUS=START** so the next booking does not
inherit a finished or failed lifecycle.

## 4. STATUS values (Hub contract D-041, uppercase)

| Phase | Values |
|---|---|
| Build | `START` → `DAY0_FINISHED` / `DAY0_FAILED` → `DAY1_FINISHED` / `DAY1_FAILED` |
| Cleanup | `DELETING` → `DELETED` |
| Other | `INITIATING`, `RESTORING`, `ERROR`, `STOPPED`, `UNAVAILABLE` |

Lowercase legacy values are accepted on read. `READY=True` ⇔ mainly `DAY1_FINISHED`.

## 5. Scenarios (D-039)

| ID | Name | Day1 |
|---|---|---|
| 11 | Prisma SD-WAN Basic | no-op (student configures) |
| 13 | Prisma SASE Basic Complete | full SD-WAN site snapshot import DC1 → DC2 → Boston → Dallas → Atlanta (additive), then trims branch firewalls / stops PEs |
| 10 | Prisma SASE Basic | disabled |
| 12 | Prisma Access Basic | not a product |

## 6. Day0 / Day1

Code: `labs/lab_automation/src/lab_automation/workflows/day0_config.py`,
`workflows/day1_config.py`, `labs/designs/prisma-sase-basic/scenarios/complete/day1.py`,
`ops/scm/sdwan_site_push.py`. Day1 YAML is read from the shared tree (edit once, all labs).
`POST /lab/day1` starts Day0 first if Day0 was not pushed.

Must-knows: VFF token must bind to the lab's own TSG (fresh mint per LAB_ID); extra ION
nodes stall Day0; vION VFF idle timeout drops to a login prompt
(`.ai/knowledge/vion-vff-idle-behavior.md`); after a cross-lab snapshot (convert) the IONs
must be recreated (`recreate_ions.py`); never close/reopen the GNS3 project to "help".

## 7. Cleanup (labapp, not Terraform)

`POST https://<gns3-1>/lab/destroy` (alias `/lab/cleanup`) runs
`cleanup/lab_cleanup.py` → `workflows/cleanup_lab.py` **inside labapp on that pod**.
V1 profile (`version1.0`): SD-WAN wipe toward Day0 → vION delicense → GNS3 teardown →
revoke student SCM access → `STATUS=DELETED`. Skips Prisma Access, CIE, NGFW delicense.
Container env `RELEASE_PROFILE=full` overrides `labs.json` unless the CLI passes
`--release-profile version1.0`. Never run cleanup from the workstation (no OOB).

## 8. Destroy (Terraform)

```powershell
$env:GOOGLE_OAUTH_ACCESS_TOKEN = (gcloud auth print-access-token --impersonate-service-account=gns3-terraform-runner@sase-lab-sdwan.iam.gserviceaccount.com)
cd labs/lab_automation/terraform/gcp-eve-ng-test-instance-feature-gns3-greenfield-merge
$env:TF_WORKSPACE = "lab-7"
terraform plan -destroy -var-file=tfvars/lab-7.tfvars     # expect ~48-49 to destroy, nothing else
terraform destroy -var-file=tfvars/lab-7.tfvars -auto-approve
Remove-Item Env:TF_WORKSPACE
```

(`scripts/tf_destroy.py` and `scripts/tf_build_lab.py` exist but are **empty** files.
On Linux/WSL the `./tf` / `make destroy-lab-7` wrappers do the same.)

Gate: `STATUS=DELETED` first (licenses are not freed by deleting VMs — lab3 leaked 9 ION
seats). Exception: a pod where Day0 never ran (semi-auto gold build) holds no licenses;
destroy directly (lab3, CHG-20261026-162200). Known trap: `snapshot_lab_id` null →
re-run with `TF_VAR_snapshot_lab_id=<id>`.

## 9. Convert (build lab B from lab A's goldens)

`build_lab.py --lab B --snapshot-lab-id A --build-mode semi-auto --apply --yes`, then the
full identity heal in `labs/lab_docs/admin_guide/lab-convert-checklist.md` (TLS, vault,
computes, nft names, /etc/hosts, booking TSG, status scrub, workers, edge-authz off,
nic1 routes/policy routing, underlay/VXLAN peers, IONs recreate). Skill:
`.cursor/skills/lab-convert/`. A same-lab rebuild (A = B) needs far less, but the deep
review still checks every item.

## 10. Golden snapshots

- Names fixed: `gns3-{1..4}-lab{id}-snapshot`. `tfvars` snapshot strings are ignored.
- Replace = copy each to `old-<UTC>-gns3-<i>-lab<id>-snapshot`, delete the original, recut
  from the live boot disks: `PYTHONPATH=labs/lab_automation/src python -m lab_automation.ops.gcp.snapshot_lab --lab <id> --name-prefix lab<id> -v`
  (skill `.cursor/skills/sase_lab_snapshot_replace/`). Alternative: `python scripts/gold_snapshot.py --lab <id> --backup`.
- Preflight (read-only): `python .cursor/skills/lab-gold-check/scripts/lab_gold_check_live.py --lab <key>` → `.ai/lab_qa/gold_check_<key>_<UTC>/REPORT.md`, verdict GO / NO-GO.
- Full procedure: `references/playbooks/gold-snapshot-rebuild.md`.
