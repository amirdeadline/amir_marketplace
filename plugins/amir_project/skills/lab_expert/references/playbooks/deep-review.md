# Playbook — Deep review: every variable has the right value for this lab_id

Read-only. Goal: prove that no file, env, service or config on the four VMs carries a value
that belongs to another lab, a donor lab, or nothing (empty). Run it after a build, before
a gold cut, and when a lab "behaves like another lab".

## 1. Expected values

```bash
python $LE/scripts/lab_facts.py labN --json > facts.json
```

That sheet is the truth (from `labs.json`). First compare the git and bucket copies of
`labs.json` for this lab's entry — they must match:

```bash
ssh … root@<gns3-1> "python3 -c \"import json;print(json.dumps(json.load(open('/opt/gns3/shared/lab/labs/labs.json'))['labs']['labN'],sort_keys=True))\"" | md5sum
python -c "import json;print(json.dumps(json.load(open('labs/labs.json'))['labs']['labN'],sort_keys=True))" | md5sum
```

## 2. Where each value must appear (and nothing else)

| Variable | Expected | Places to check |
|---|---|---|
| lab key / id | `labN` / `N` | hostname `lab-N-gns3-i`; `lab_status.json` `labKey`, `labId`, `checks.labKey/labId` (all 4 VMs); booking `LAB_ID`; container `LAB_ID`; `/etc/gns3/edge-authz.env` `LAB_ID`; `/var/lib/sase-startup/last_run.json` identity |
| TSG | `facts.tsg_id` | booking `TSG_ID`, `SCM_TSG_ID`; container env; `lab_status.json` `vff_lab_tsg_id`; tfvars `tsg_id` |
| TSG name | `COE-SASE-LAB-PLATFORM-NN` | container `TSG_NAME` (never `…-dev` on a student lab) |
| nic1 IPs | `facts.vms[i].nic1` | `ip -br addr`; GNS3 `/v2/computes` hosts (gns3-1); TLS SAN; DNAT rules (`nft list ruleset` on gns3-1, target = own nic1); labapp `LAB_ADDRESS` / links |
| nic0 | `10.100.20.11..14` | `ip -br addr`; workers `gns3_controller.conf`; VXLAN `local`/`remote` in netplan; `gns3_underlay_block` peers |
| FQDN | `srv<i>.labN.saselab.paloaltonetworks.com` | TLS CN/SAN `/etc/gns3/certs/web/server.crt`; boot vault `/root/secure/tls/bundle.pem`; `LAB_ADDRESS`; DNS resolves to own nic1 |
| TLS leaf | SM `labN-srv<i>-cert` | SHA-256 fingerprint equals the on-disk leaf on each VM |
| Scenario | `13` for a gold build | booking `SCENARIO_ID`; container env |
| Build mode | `semi-auto`, auto Day0/Day1 `false` | booking + container |
| Reservation | `amirr@gatech.edu`, `local-labN-gold-*` | booking + container + `/lab/status` |
| Workspace | `lab-N` | tfvars file, TF state key |
| Golden | `gns3-<i>-labN-snapshot` | each boot disk `sourceSnapshot` (informational) |
| Release | `RELEASE.json.git_sha` | `last_applied.json release_sha`; labapp image built after apply |
| Secrets | names SET | `/run/labapp/labapp.env` (names only); student `lab_N_pass` |

## 3. Foreign-value scan (nothing from another lab)

Use `facts.foreign_tsgs`, `facts.foreign_nic1_ips`, `facts.foreign_lab_keys`:

```bash
# on each VM, excluding the shared tree and backup files
grep -rlE '<tsg1>|<tsg2>|…' /etc/labapp /etc/gns3 /etc/nftables* /etc/hosts /etc/systemd/system /usr/local/sbin 2>/dev/null
grep -rlE '10\.95\.98\.(161|162|…)\b' /etc/labapp /etc/gns3 /etc/nftables* /etc/hosts /root/secure 2>/dev/null
grep -rnE 'srv[0-9]\.(lab[0-9]+|dev)\.saselab' /etc/labapp /etc/gns3 /etc/hosts | grep -v 'labN\.'
nft list tables | grep -E 'lab[0-9]+_' | grep -v 'lab11_tap'   # lab11_tap_* names are generic in every gold (verify)
```

Collector shortcut for the TSG part: `collect_vm_evidence.sh` section "foreign TSG". The
gold-check runs the same scan (`ID-TSG-LABAPP`) via `tsg_leak_scan.sh`.

Any hit under `/etc/labapp` = NO-GO. Hits elsewhere: explain each one (some names such
as `br-lab11`, `lab11_tap_*`, `lab11-oob-policy` are historical names used in every pod —
confirm they point at this pod's addresses before accepting).

## 4. Empty values

Grep the booking and container env for keys that exist but are empty
(`grep -E '^[A-Z_]+=$' /run/labapp/labapp.env | cut -d= -f1`). `TSG_ID=` / `SCM_TSG_ID=`
empty is a defect (I-11). `USER_PASSWORD` empty on a gold build is expected only if the
secret `lab_N_pass` does not exist — report it.

## 5. Report

Table: variable | expected | found where | PASS/FAIL. List every FAIL with the fix from
`gold-snapshot-rebuild.md` Phase 3. No fix during the review itself.
