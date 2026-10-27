# 07 — What is left to do (2026-10-27)

Ordered by impact. Each item names the issue in `06-issues-and-fixes.md`.

| # | Work | Why | Who decides | Issue |
|---|---|---|---|---|
| 1 | Make the 10/8 route persistent in networkd on every running VM, then in `nic1-route-10-install.sh` + startup `hostnet`, then publish | Any running lab can drop off the corp network at the next daily upgrade (lab7 today) | owner (live L2) | I-01 |
| 2 | Decide the unattended-upgrades policy on lab VMs | Upgrades restart networkd, libvirt, nginx during bookings | owner | I-09 |
| 3 | Review + publish `agent/host-bootstrap-startup` (prove on dev, then one worker, then a fresh lab), promote to SDWAN_LAB | Boot orchestrator runs nowhere except lab3's gold | owner (L2/L3) | I-02 |
| 4 | One clean publish of a known ref to the bucket (`publish_labapp_release.py`) | Bucket is a mix (8c6550c + hand rsync) | owner | I-03, I-06 |
| 5 | Fix the `mount-shared.sh` comment interpolation (`$${…}`) | Fragile boot script; "command not found" in every boot log | code change + publish | I-05 |
| 6 | Re-cut golds lab by lab with `references/playbooks/gold-snapshot-rebuild.md` once 1, 3, 4 are published | Golds older than 2026-10-26 lack the startup mechanism and the route fix | owner per lab | I-02, I-13 |
| 7 | Fix the lab3 first-boot `npm run build` failure in the shared labapp tree | Pods silently run an old labapp image | code | I-06 |
| 8 | Prove and publish `agent/robust-lab-wipe` (on dev local disk only today) | ION retire / wipe failures block cleanup | owner | I-30 |
| 9 | Correct `labs.json`: real nic1 IPs for lab19–25, SC FQDNs for lab5/6/7/9, stale enabled/status, dev zone, release_profile | Wrong values reach builds, Day1 and the dashboard | owner | I-50 |
| 10 | Admin dashboard GCP access: own VM with `lab-admin-dashboard-sa` attached + ADC support in the credential resolver; then Terraform build/destroy from the dashboard | Org blocks SA keys; dashboard has no GCP view | owner + code | I-53 |
| 11 | Investigate failed units on dev (`nic1-policy-routing`, `lab-tls-ensure`, `sase-pod-bootstrap`) and dev `DAY0_FAILED` | dev is the proving ground | agent (read-only first) | I-07, I-24 |
| 12 | Asana issue tracker go-live (bot token, secret, env-sync, labapp redeploy) | Students cannot report issues | owner | I-52 |
| 13 | Lab3 ION seat leak and leftover Prisma Access objects on old labs | Licenses / tenant hygiene | owner (L3) | I-31, I-33 |
| 14 | Promote tested work to SDWAN_LAB and push (GitLab) | Product repo behind the donor tree | owner | I-54 |
| 15 | Day1 remaining: Mobile Users, Explicit Proxy, ADEM, SASE-Connectivity Remote Networks, DC CPE IPsec/BGP (`lab_start.md` §8.9) | Scenario 13 completeness | owner | — |
