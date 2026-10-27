# Playbook — Troubleshoot any lab

Read-only until the cause is proven. Then propose the fix with its level (08-rules) and wait
for the owner unless the fix is L0/L1.

## 1. Intake (ask only what is missing)

- Lab (key or id), what the person sees (exact error / screenshot text), since when,
  who is affected (student booking? which user?), what changed recently (build, Day0,
  cleanup, upgrade, publish).

## 2. Collect evidence in this order (stop when the cause is clear)

1. **Registry:** `lab_facts.py labN` (+ `--all-checks` for registry errors on this lab).
2. **Booking:** `bookings.json` entry for labN; `/lab/status` reservation + window. A
   student is on it? Then read-only only, and say so.
3. **GCP:** instances (status, creation time, machine type), boot disk `sourceSnapshot`,
   serial console if SSH fails, quota, recent operations
   (`gcloud compute operations list --filter="targetLink~lab-N-gns3" --limit 20`).
4. **Reachability from the workstation:** `curl -ks -m 6 -o /dev/null -w '%{http_code}' https://<nic1>/health/live`
   for gns3-1, `ssh` to each nic1. Unreachable but RUNNING → go to symptom S-1.
5. **Host state:** `collect_vm_evidence.sh` on every VM (save outputs).
6. **labapp:** `/lab/status`, `/lab/licensing`, `/lab/day0`, `/lab/day1`, `/lab/destroy`
   (03-access §3); `docker logs --tail 300 sase-labapp`.
7. **Lab logs:** `/opt/gns3/shared/lab/labs/logs/labs/<id>/gns3/*.log` (newest first,
   grep ` ERROR |Traceback`), `<hostname>-startup.log`.
8. **GNS3:** project opened? nodes started (52)? computes connected on nic1?
9. **Devices:** from gns3-1 to OOB `10.10.99.x` (design.json), `qa-smoke` OOB matrix.
10. **SCM (read-only):** IONs page / dry-run inventory for this TSG only.
11. **Admin dashboard:** Issues, lifecycle chips and logs for the lab (05).

## 3. Symptom → likely cause → check → fix

| # | Symptom | Likely cause | Check | Fix (level) |
|---|---|---|---|---|
| S-1 | nic1 SSH/HTTPS times out, VM RUNNING | 10/8 route lost (I-01) after networkd restart / upgrade; or nic1 policy routing failed | via IAP: `ip route show 10.0.0.0/8`, `journalctl -u systemd-networkd --since -2d`, `/var/log/apt/history.log`, `systemctl status nic1-policy-routing` | `fix_route10_persistent.sh --apply` (L2) |
| S-2 | Everything unreachable incl. IAP | VM stopped / deleted / boot hung | `instances list`, serial port output | owner decides start / rebuild (L2/L3) |
| S-3 | labapp down after build | gcsfuse not mounted (CRLF metadata, I-04); release gate exit 1 (`LABAPP_RELEASE` ≠ `RELEASE.json`); image build failed (I-06); env-sync could not read a secret | collector sections mount / boot orchestrator / startup log; `journalctl -u sase-startup -u sase-labapp` | CRLF recovery; fix release pin; env-sync (L2) |
| S-4 | Boot orchestrator did nothing on workers | unit not installed — bucket hook lacks bootstrap call (I-02) | `systemctl cat sase-startup`, launcher file | `bootstrap_host.sh` on that VM (L2); publish (owner) |
| S-5 | Lab acts like another lab (wrong TSG, user, certs) | convert / snapshot leftovers (I-10), empty booking TSG (I-11) | `references/playbooks/deep-review.md` | convert checklist fixes (L2) |
| S-6 | Day0 fails / hangs | wrong-TSG VFF token, extra IONs, VFF idle login prompt, ION seats exhausted, GNS3 nodes not started, OOB down | `day0.log`, `vion_activate.log`, `/lab/licensing`, qa-smoke | retry Day0 after cause fixed (L2, owner) |
| S-7 | Day1 fails | ION not claimed / not connected, SD-WAN tenant not clean, YAML error | `sdwan_configure.log`, SCM IONs page | fix cause, Retry Day1 (L2, owner) |
| S-8 | Cleanup fails | ION retire 400 INVALID_OPERATION, nameless elements, `RELEASE_PROFILE=full` | `cleanup_lab.log`, `scm_cleanup.log`, `vion_delicense.log` | robust wipe branch / retire from IONs page (L3, owner) |
| S-9 | TF destroy fails validation | `snapshot_lab_id` null (I-42) | error text | `TF_VAR_snapshot_lab_id=<id>` |
| S-10 | TF apply partial / VMs missing | N2 CPU quota (I-41), zone stock-out | apply log | free quota / other family (owner) |
| S-11 | gcloud "Reauthentication failed" | token expired (I-40) | — | owner `gcloud auth login` |
| S-12 | GNS3 nodes stopped / 12 of 52 | GNS3 restart, host reboot | GNS3 API nodes list | start nodes (L2) — never close/reopen project |
| S-13 | Console/TLS warnings on :3080 / :443 | donor or expired leaf, chain issue | collector TLS section vs SM | ensure_host_tls_certs + vault (L2) |
| S-14 | Admin dashboard shows wrong state | stale `labs.json`, GCP credential missing, probes from dev-gns3-1 failing | 05 §8 | per 05 |
| S-15 | Route ok but a 10.x host still unreachable | corp-side routing / firewall | `traceroute`, test from another lab VM | network ticket |

## 4. Answer format

1. **Cause** (one line) and **confidence** (proved / likely / unknown) with the evidence that
   proves it (command + output excerpt, file:line).
2. **Fix**, its level, exactly what it changes, how to undo it.
3. **Other findings** worth knowing (registry errors, other VMs at risk).
4. Evidence paths. No secret values anywhere.
