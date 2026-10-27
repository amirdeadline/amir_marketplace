# Playbook — Rebuild the gold snapshot of one lab

Trigger: the owner says "redo the gold for labN" (or similar). That request approves the
live steps below **for labN only** (08-rules). Reference run: lab3 on 2026-10-26
(CHG-20261026-142516 → -145800 → -154900 → -162200).

Fixed booking for every gold build:

| Key | Value |
|---|---|
| Scenario | `13` |
| Reservation user | `amirr@gatech.edu` |
| Reservation id | `local-labN-gold-<UTCSTAMP>` |
| Start / end | now / now + 24 h (ISO-8601 UTC, `Z`) |
| Build mode | `semi-auto` (Day0 and Day1 must NOT run) |
| Release profile | `version1.0` |

Evidence folder: `discovery/runs/<UTC>-labN-gold-rebuild/` — save every command output
there (no secret values). Keep a running log; it becomes the CHG record.

Timing seen: apply 5–15 min, boot + labapp 5–10 min, snapshot recut ~17 min (4 in
parallel), destroy ~5 min. Whole run ~1.5–3 h with fixes.

---

## Phase 0 — Preflight (read-only). Stop on any ✗.

1. **Mapping.** `python $LE/scripts/lab_facts.py labN` and
   `--all-checks`. ✗ if TSG null, nic1 invalid, or the lab is lab24/25.
   Save `lab_facts.py labN --json > facts.json` in the evidence folder.
2. **Bookings.** Read `/opt/gns3/shared/lab/labs/bookings.json` (via any running VM, or
   `gcloud storage cat gs://sase-lab-sdwan-gns3-shared/lab/labs/bookings.json`).
   ✗ if labN has a non-cancelled booking that is active now or starts in the next 4 h.
3. **Existing VMs.** `gcloud compute instances list --project sase-lab-sdwan --filter="name~'^lab-N-gns3-'"`.
   ✗ if any exist → stop and ask (an apply over a live pod replaces it; a booked pod must
   never be touched). If the owner says go: cleanup first if Day0 ever ran.
4. **Goldens.** `gcloud compute snapshots list --filter="name~'labN-snapshot'"` → four
   `gns3-{1..4}-labN-snapshot` READY. If missing: ask which donor lab to boot from
   (`--snapshot-lab-id`) — that turns this into a **convert** and Phase 3 must run the full
   `lab-convert-checklist.md`.
5. **Quota.** N2 CPUs free ≥ 96 in `us-west2` (32+32+16+16).
6. **Auth.** `gcloud auth print-access-token --impersonate-service-account=gns3-terraform-runner@sase-lab-sdwan.iam.gserviceaccount.com`
   works. If "Reauthentication failed" → ask the owner for `gcloud auth login`.
7. **What the bucket will give the new VMs** (read on any running VM):
   `RELEASE.json`, `labs/scripts/startup/VERSION`, and
   `grep -c bootstrap_host …/scripts/apply-terraform-booking-lab-status.sh`.
   Record it. If the bootstrap call is missing (0 today), Phase 3 F-4 installs the
   orchestrator by hand so it is baked into the gold.
8. **SCM baseline (read-only).** Note the tenant state before the build (admin dashboard
   IONs page, or a dry-run SD-WAN inventory). A gold build claims nothing; if the tenant
   already has claimed IONs or sites from an older booking, report it — do not wipe.
9. Tell the owner the plan in 3 lines (target, booking, what happens at the end) and go.

## Phase 1 — Terraform build (L3)

```powershell
cd E:\PC3_Shared\Palo\COE\Prisma_SASE_LAB\PaloAlto_SASE_LAB
$env:GOOGLE_OAUTH_ACCESS_TOKEN = (gcloud auth print-access-token --impersonate-service-account=gns3-terraform-runner@sase-lab-sdwan.iam.gserviceaccount.com)
$S = (Get-Date).ToUniversalTime(); $start = $S.ToString("yyyy-MM-ddTHH:mm:ssZ"); $end = $S.AddHours(24).ToString("yyyy-MM-ddTHH:mm:ssZ")
python labs/scripts/build_lab.py --lab labN --scenario-id 13 --reservation-user amirr@gatech.edu `
  --reservation-id ("local-labN-gold-" + $S.ToString("yyyyMMddHHmmss")) --start-time $start --end-time $end `
  --build-mode semi-auto --release-profile version1.0 --print-only
# check the printed command + snapshot names, then the same line with:  --apply --yes
```

Check `tfvars/lab-N.tfvars` has `tsg_id = "<TSG>"` (I-11). ✓ = "Apply complete … 49 added",
four VMs RUNNING with the nic1 IPs from facts.json.

## Phase 2 — Boot verification (read-only), after ~10 min

Run the collector on all four VMs (03-access §4) and save each output. Check:

| ID | Check | Expected |
|---|---|---|
| B-1 | nic1 SSH works | yes (else IAP; then F-2) |
| B-2 | `/opt/gns3/shared` mounted (`fuse.gcsfuse`) | all 4 |
| B-3 | metadata script CR-lines = 0, exit status 0 | all 4 |
| B-4 | `ip route show 10.0.0.0/8` via `10.95.98.129` on nic1 | all 4 |
| B-5 | sase-startup present, launcher present, last run rc=0 | all 4 (today: gns3-1 old unit only) |
| B-6 | gns3-1 containers `sase-labapp`, `sase-labapp-nginx`, `sase-lab-assistant` healthy; `/health/live` 200 | gns3-1 |
| B-7 | booking keys: `LAB_ID=N`, `SCENARIO_ID=13`, `TSG_ID`=`SCM_TSG_ID`=TSG, `RESERVATION_USER=amirr@gatech.edu`, `LABAPP_BUILD_MODE=semi-auto`, `LABAPP_AUTO_DAY0=false`, `LABAPP_AUTO_DAY1=false`; secrets SET | gns3-1 `/run/labapp/labapp.env` + container `printenv` |
| B-8 | `/lab/status`: Day0/Day1 `not_started`, nothing running | gns3-1 |
| B-9 | `last_applied.json` `release_sha` = `RELEASE.json` sha, `rebuilt=true` without error | gns3-1 |
| B-10 | workers: `sase-labapp` inactive | gns3-2..4 |

If B-2/B-3 fail (CRLF): on that VM
`curl -s -H 'Metadata-Flavor: Google' http://169.254.169.254/computeMetadata/v1/instance/attributes/startup-script | tr -d '\r' > /tmp/boot-fix.sh && bash /tmp/boot-fix.sh`
then on gns3-1:
`bash /opt/gns3/shared/lab/labs/lab_automation/terraform/gcp-eve-ng-test-instance-feature-gns3-greenfield-merge/scripts/labapp-env-sync.sh`
and `bash /etc/labapp/docker/labapp/scripts/labapp-compose.sh up` (CHG-20261026-142516).

If Day0/Day1 started anyway (auto flags wrong): stop and tell the owner — licenses may be
claimed, and the pod then needs labapp cleanup before destroy.

## Phase 3 — Apply every known fix to this pod (L2, labN only)

Fix only what Phase 2 / Phase 4 shows broken, re-check after each fix. Never touch another
lab or the bucket here (bucket = all labs = separate owner ask).

| ID | Fix | How |
|---|---|---|
| F-1 | Mount / CRLF | see Phase 2 note |
| F-2 | **Persistent 10/8** | on all 4: `ssh … 'bash -s' -- --apply < $LE/scripts/fix_route10_persistent.sh`; also `systemctl enable nic1-route-10` |
| F-3 | nic1 policy routing | `systemctl restart nic1-policy-routing`; `ip rule` shows `from <nic1> lookup nic1` (gns3-1 also `lookup lab_oob`) |
| F-4 | **Boot orchestrator** | on all 4: `bash /opt/gns3/shared/lab/labs/scripts/startup/bootstrap_host.sh` (installs launcher + role unit + gns3-1 labapp drop-in, enables the unit, starts it only if not active). gns3-1 already has the old unit active, so then run `systemctl restart sase-startup` there to exercise the new launcher — this also restarts labapp; do it before the F-5 checks. ✓ launcher present, `/var/lib/sase-startup/last_run.json` rc=0, `/var/log/sase-startup/startup.log` DONE on all 4. (CRLF in the bucket copy → `sed -i 's/\r$//'` on a local copy, run that) |
| F-5 | labapp current | image rebuilt from `RELEASE.json` sha; if `npm run build` failed, read the startup log, do not deploy an ad-hoc build; report (I-06). Containers healthy, `/health/live` 200 |
| F-6 | Booking identity | wrong key → fix `tfvars/lab-N.tfvars`, re-run the Phase 1 apply (updates the booking object, VMs stay), then `labapp-env-sync.sh` + `systemctl restart sase-labapp` |
| F-7 | TLS | per VM: SM `labN-srv<i>-cert` fingerprint = `/etc/gns3/certs/web/server.crt`; else `FORCE=1 bash /opt/gns3/shared/lab/labs/scripts/tls/ensure_host_tls_certs.sh` then `bash …/tls/rewrite_boot_vault.sh` |
| F-8 | GNS3 | 2.2.60, project `Prisma-SASE-Basic` opened, 52/52 started, 4 computes on own nic1 (`APPLY=1 FORCE=1 python3 /opt/gns3/shared/lab/labs/scripts/gns3/ensure_gns3_computes_nic1.py`); start stopped nodes via GNS3 API. No project close/reopen |
| F-9 | Edge helpers | all 4: `systemctl disable --now gns3-edge-authz oauth2-proxy` (BUILD-28) |
| F-10 | nft / hosts | no foreign lab names in `nft list tables`, `/etc/nftables.conf`, `/etc/hosts`; VXLAN/underlay peers `10.100.20.11..14` |
| F-11 | Unit hygiene | `systemctl --failed` empty or explained; `sase-pod-bootstrap`, `lab-tls-ensure`, `gns3-tls-materialize`, `lab-gns3-computes-nic1` disabled after FTB as the gold-check expects |
| F-12 | IONs / NGFW | GNS3 nodes started; no ION claimed in SCM (read-only check). Do not activate or license anything |
| F-13 | qa-smoke | `docker exec sase-labapp python3 -m lab_automation qa-smoke --lab labN` → ok, OOB 36/36, 52/52, labapp https |

Owner-only items you may NOT do here: publish to the bucket, SCM wipe/retire, change
unattended-upgrades fleet policy. You may disable unattended-upgrades on this pod only if
the owner already decided that (I-09) — otherwise list it in the report.

## Phase 4 — Deep review (read-only) → must be GO

1. `references/playbooks/deep-review.md` (every expected value vs every place it lives).
2. The gold-check runner SSHes through IAP ports `127.0.0.1:<20000+100*N+20+i>`: start
   them first with `python dev/scripts/start_gcp_tunnels.py --lab N` (separate terminal),
   then `python .cursor/skills/lab-gold-check/scripts/lab_gold_check_live.py --lab labN`
   → `.ai/lab_qa/gold_check_labN_<UTC>/REPORT.md`. Verdict must be **GO** or
   **GO-WITH-WARNINGS** with warnings you can explain.
3. NO-GO → back to Phase 3 for the listed items, then a **new** gold-check. Max 3 rounds,
   then stop and report to the owner with the blockers.

## Phase 5 — Gold prep (L2): freeze the pod in a clean START state

On **gns3-1** first:

```bash
docker exec sase-labapp python3 -m lab_automation qa-smoke --lab labN > /tmp/qa-final.json   # keep
docker exec sase-labapp python3 -m lab_automation rotate-logs --lab labN --dry-run   # then without --dry-run: archive this build's logs, fresh empty .log files
bash /etc/labapp/docker/labapp/scripts/labapp-compose.sh down
systemctl stop sase-labapp            # stop only; KEEP it enabled (I-55)
```

On **all four** (copy the scrub tool first:
`ssh … root@<nic1> 'cat > /tmp/scrub.py' < temp/scrub-lab-status-gold.py`):

```bash
python3 /tmp/scrub.py labN N <TSG> 13
sha256sum /etc/labapp/lab_status.json             # must be identical on all four
mkdir -p /root/archive/labapp-status-bak && mv /etc/labapp/lab_status.json.bak-* /root/archive/labapp-status-bak/ 2>/dev/null || true
rm -f /var/lib/sase-labapp/lifecycle/ion_keys.env
sync
```

Then on gns3-1: `cp /etc/labapp/lab_status.json /opt/gns3/shared/lab/labs/logs/labs/N/gns3/lab_status.json`
(NFS copy byte-identical). Verify the gold state on each VM:
`STATUS=START`, `READY=false`, day0/day1 `not_started`, `vff_keys={}`, `ions=[]`, `panos=[]`,
`vff_lab_tsg_id=<TSG>`, no `last*` keys, booking semi-auto with auto flags false.

Run the gold-check once more (labapp stopped → APP-HEALTH / qa-smoke N/A). Must be GO.

## Phase 6 — Replace the golden snapshots (L3)

Follow `.cursor/skills/sase_lab_snapshot_replace/SKILL.md` exactly (VMs stay RUNNING):

```bash
P="--project sase-lab-sdwan"; D=$(date -u +%Y%m%d%H%M%S)
# 1. archive (copy) — stop if any archive name exists or any copy fails
for i in 1 2 3 4; do gcloud compute snapshots create old-$D-gns3-$i-labN-snapshot --source-snapshot=gns3-$i-labN-snapshot $P; done
gcloud compute snapshots list $P --filter="name~'^old-$D-'" --format="table(name,status)"   # 4x READY
# 2. delete only the originals that were archived
for i in 1 2 3 4; do gcloud compute snapshots delete gns3-$i-labN-snapshot $P --quiet; done
# 3. recut from the live boot disks (canonical tool)
PYTHONPATH=labs/lab_automation/src python -m lab_automation.ops.gcp.snapshot_lab --lab N --name-prefix labN -v
gcloud compute snapshots list $P --filter="name~'labN-snapshot'" --format="table(name,status,creationTimestamp)"
```

✓ = four new `gns3-{1..4}-labN-snapshot` READY and four `old-$D-…` READY. 3 of 4 is not a
gold set — stop and report. Never delete `old-*` archives.

## Phase 7 — Terraform destroy (L3)

Day0 never ran → no licenses. Confirm first: `/lab/status` day0/day1 `not_started` (from the
Phase 5 notes) and SCM shows no new claimed IONs for this TSG. Then destroy (04-lifecycle §8)
with `TF_WORKSPACE=lab-N`. ✓ = ~49 destroyed, no `lab-N-gns3-*` VMs, VPC gone, goldens still
READY.

## Phase 8 — Record and report

- `.ai/changes/CHG-<UTC>-labN-gold-rebuild.md` (template `_TEMPLATE.md`) + row in `.ai/changelogs.md`.
- Durable lessons → `.ai/agents/SHARED_MEMORY.md`.
- Report to the owner: table (phase | result | evidence path), fixes applied on the pod (they
  are now in the gold), fixes NOT applied and why (bucket publish, policy items), new gold
  names + archive names, time taken.

## Stop and ask when

- labN is booked, has VMs, or has claimed licenses; any value in `labs.json` looks wrong;
  quota or auth blocks; Day0/Day1 started; the same NO-GO item survives 3 rounds; a fix
  would touch the bucket, another lab or SCM; snapshot archive/copy fails.
