# 02 — Fleet registry: every lab, its TSG, tenant and IPs

Source: `labs/labs.json` in the donor tree on **2026-10-27** (schema 2.0, 26 labs).
Regenerate or check any single lab with:

```bash
python $LE/scripts/lab_facts.py lab7          # one lab, every expected value
python $LE/scripts/lab_facts.py lab7 --json   # machine-readable
python $LE/scripts/lab_facts.py --all-checks  # registry problems
```

**Two copies of labs.json exist**: git (`labs/labs.json`) and runtime
(`/opt/gns3/shared/lab/labs/labs.json` in the bucket). Lab Hub keeps a **third, separate**
copy (sync with `--sync-hub`, CHG-20261007-171500). Before trusting a value, compare MD5 of
the git and bucket copies. Never invent an IP or TSG: if it is not in `labs.json`, ask.

## Parent tenant

Parent TSG **`1479602777`** = **hard refuse** for every write, wipe or mutate. Only TSGs
mapped in `labs.json` may be touched, and only the one for the target lab.

## Mapping table

`pa_tenant_id` equals `tsg_id` for every lab. nic1 IPs are `10.95.98.<x>`.

| Key | id | TSG (= pa_tenant_id) | SCM tenant name | gns3-1 / -2 / -3 / -4 nic1 | IAP ports | Workspace | enabled / status | release_profile |
|---|---|---|---|---|---|---|---|---|
| `dev` | 0 | `1711343479` | COE-SASE-LAB-PLATFORM-dev | .171 / .169 / .172 / .170 | 20021-20024 | `dev` | True / active | - |
| `lab1` | 1 | `1749798335` | COE-SASE-LAB-PLATFORM-01 | .167 / .165 / .168 / .166 | 20121-20124 | `lab-1` | True / documentation-cook | - |
| `lab2` | 2 | `1835316130` | COE-SASE-LAB-PLATFORM-02 | .164 / .162 / .161 / .163 | 20221-20224 | `lab-2` | True / active | version1.0 |
| `lab3` | 3 | `1999182870` | COE-SASE-LAB-PLATFORM-03 | .174 / .175 / .176 / .177 | 20321-20324 | `lab-3` | True / active | version1.0 |
| `lab4` | 4 | `1855931604` | COE-SASE-LAB-PLATFORM-04 | .179 / .180 / .181 / .182 | 20421-20424 | `lab-4` | True / planned | version1.0 |
| `lab5` | 5 | `1118928420` | COE-SASE-LAB-PLATFORM-05 | .184 / .185 / .186 / .187 | 20521-20524 | `lab-5` | True / active | version1.0 |
| `lab6` | 6 | `1890995699` | COE-SASE-LAB-PLATFORM-06 | .189 / .190 / .191 / .192 | 20621-20624 | `lab-6` | True / planned | version1.0 |
| `lab7` | 7 | `1880230960` | COE-SASE-LAB-PLATFORM-07 | .194 / .195 / .196 / .197 | 20721-20724 | `lab-7` | True / planned | version1.0 |
| `lab8` | 8 | `1414435244` | COE-SASE-LAB-PLATFORM-08 | .199 / .200 / .201 / .202 | 20821-20824 | `lab-8` | True / planned | version1.0 |
| `lab9` | 9 | `1695374108` | COE-SASE-LAB-PLATFORM-09 | .204 / .205 / .206 / .207 | 20921-20924 | `lab-9` | True / planned | version1.0 |
| `lab10` | 10 | `1630390203` | COE-SASE-LAB-PLATFORM-10 | .209 / .210 / .211 / .212 | 21021-21024 | `lab-10` | True / planned | version1.0 |
| `lab11` | 11 | `1209694244` | COE-SASE-LAB-PLATFORM-11 | .214 / .215 / .216 / .217 | 21121-21124 | `lab-11` | True / planned | - |
| `lab12` | 12 | `1608497273` | COE-SASE-LAB-PLATFORM-12 | .219 / .220 / .221 / .222 | 21221-21224 | `lab-12` | False / planned | - |
| `lab13` | 13 | `1390988258` | COE-SASE-LAB-PLATFORM-13 | .224 / .225 / .226 / .227 | 21321-21324 | `lab-13` | False / planned | - |
| `lab14` | 14 | `1479378069` | COE-SASE-LAB-PLATFORM-14 | .229 / .230 / .231 / .232 | 21421-21424 | `lab-14` | False / planned | - |
| `lab15` | 15 | `1732197108` | COE-SASE-LAB-PLATFORM-15 | .234 / .235 / .236 / .237 | 21521-21524 | `lab-15` | False / planned | - |
| `lab16` | 16 | `1914259008` | COE-SASE-LAB-PLATFORM-16 | .239 / .240 / .241 / .242 | 21621-21624 | `lab-16` | False / planned | - |
| `lab17` | 17 | `1134980756` | COE-SASE-LAB-PLATFORM-17 | .244 / .245 / .246 / .247 | 21721-21724 | `lab-17` | False / planned | - |
| `lab18` | 18 | `1596169374` | COE-SASE-LAB-PLATFORM-18 | .249 / .250 / .251 / .252 | 21821-21824 | `lab-18` | False / planned | - |
| `lab19` | 19 | `1347435403` | COE-SASE-LAB-PLATFORM-19 | .254 / .255 / .256 / .257 | 21921-21924 | `lab-19` | False / planned | - |
| `lab20` | 20 | `1430967505` | COE-SASE-LAB-PLATFORM-20 | .259 / .260 / .261 / .262 | 22021-22024 | `lab-20` | False / planned | - |
| `lab21` | 21 | `1311614492` | COE-SASE-LAB-PLATFORM-21 | .264 / .265 / .266 / .267 | 22121-22124 | `lab-21` | False / planned | - |
| `lab22` | 22 | `1108931216` | COE-SASE-LAB-PLATFORM-22 | .269 / .270 / .271 / .272 | 22221-22224 | `lab-22` | False / planned | - |
| `lab23` | 23 | `1177394227` | COE-SASE-LAB-PLATFORM-23 | .274 / .275 / .276 / .277 | 22321-22324 | `lab-23` | False / planned | - |
| `lab24` | 24 | `**null**` | COE-SASE-LAB-PLATFORM-24 | .279 / .280 / .281 / .282 | 22421-22424 | `lab-24` | False / planned | - |
| `lab25` | 25 | `**null**` | COE-SASE-LAB-PLATFORM-25 | .284 / .285 / .286 / .287 | 22521-22524 | `lab-25` | False / planned | - |

## Patterns (use to spot wrong values)

| Item | Rule | Example lab7 |
|---|---|---|
| Workspace | `dev` for lab_id 0, else `lab-<id>` | `lab-7` |
| VM names | `lab-<id>-gns3-<i>` (dev: `dev-gns3-<i>`) | `lab-7-gns3-1` |
| nic1 (lab3 and up) | gns3-1 = `10.95.98.(159 + 5*id)`, gns3-i = that + (i-1) | `.194 .195 .196 .197` |
| nic1 (dev, lab1, lab2) | irregular — read `labs.json` | dev `.171/.169/.172/.170` |
| nic0 | `10.100.20.1<i>` in every lab | `10.100.20.11..14` |
| IAP SSH port | `20000 + 100*id + 20 + i` (lab10 → `21021`; lab25 → `22521`) | `20721..20724` |
| FQDN | `srv<i>.<labkey>.saselab.paloaltonetworks.com` | `srv1.lab7.saselab.paloaltonetworks.com` |
| Golden snapshot | `gns3-<i>-lab<id>-snapshot` (dev = `lab0`) | `gns3-1-lab7-snapshot` |
| Archive snapshot | `old-<YYYYMMDDHHMMSS>-gns3-<i>-lab<id>-snapshot` | |
| Booking env | `/opt/gns3/shared/lab/docker/labapp/<workspace>/.env` | `.../lab-7/.env` |
| tfvars | `<stack>/tfvars/<workspace>.tfvars` (gitignored) | `tfvars/lab-7.tfvars` |
| Logs | `/opt/gns3/shared/lab/labs/logs/labs/<id>/` | `.../labs/7/` |
| Student password secret | `lab_<id>_pass` | `lab_7_pass` |
| TLS secrets | `<labkey>-srv<i>-cert`, `<labkey>-srv<i>-cert-password` | `lab7-srv1-cert` |
| NGFW deployment profile | `LAB-<id>-NGFW-Deployment-Profile` (dev: `LAB-DEV-…`) | `LAB-7-NGFW-Deployment-Profile` |
| Domain (Windows) | `prismalab.local` | |

## Known registry problems (2026-10-27, from `lab_facts.py --all-checks`)

| # | Problem | Impact | What to do |
|---|---|---|---|
| R-1 | lab19 gns3-2..4 and **all of lab20–lab25** have nic1 `10.95.98.255`…`.287` — invalid or outside `10.95.98.128/25` | These pods cannot be built on the current nic1 subnet | Ask the owner for the real subnet/IPs before any build. Do not "fix" by guessing |
| R-2 | lab6, lab7, lab9: `scm.sc.sc2.fqdn` equals the **dc1** FQDN | Day1 / service-connection checks for DC2 would use the wrong FQDN | Read the real SC FQDN in SCM (read-only) and propose the edit to the owner |
| R-3 | lab5 sc1 FQDN equals lab4's (`onyjoc5ooy`) and sc2 is missing | Same | Same |
| R-4 | lab24, lab25 `tsg_id` null | Never target them | Leave alone |
| R-5 | `enabled` / `status` fields are stale for many labs (e.g. lab4 `planned`, lab7 `planned` while lab7 is booked and running) | Admin dashboard and Hub may show the wrong state | Flag; only Flag Lab Ready or an owner ask changes them |
| R-6 | dev `zone` says `us-west2-a`; dev VMs run in `us-west2-c` (C3) since 2026-10-21 | Tools that read the zone from labs.json look in the wrong zone for dev | Pass the zone explicitly for dev |
| R-7 | dev booking env has `TSG_ID=` and `SCM_TSG_ID=` **empty** (seen 2026-10-27) | Day0 may fall back to defaults | Set in `tfvars/dev.tfvars` (`tsg_id`) on the next dev build |
| R-8 | `release_profile` missing for dev, lab1, lab11–25 | Cleanup uses the container default (`RELEASE_PROFILE`), which may be `full` | Pass `--release-profile version1.0` when building |

## Live picture (2026-10-27, quick probe — always re-check)

| Lab | Seen | Note |
|---|---|---|
| dev | 4 VMs up (C3, us-west2-c) | `semi-auto`, sc13, user amirr@gatech.edu, Day0 last run `DAY0_FAILED` on disk; admin dashboard `saselab-admin` runs here |
| lab7 | 4 VMs up since 2026-10-26 15:02 UTC | **Booked by a student** (`tjeedigunta@…`, sc11, `auto`). 10/8 route was lost 2026-10-27 06:30 UTC (see 06-issues I-01). Do not rebuild without the owner |
| lab6 | labapp answers on nic1 | not inspected |
| lab3 | destroyed 2026-10-26 after a new gold cut (startup bootstrap baked) | goldens `gns3-*-lab3-snapshot` new; archive `old-20261026151200-*` |
| lab9 | destroyed 2026-10-26 after live cleanup | |
| lab10, lab11 | destroyed 2026-10-24 | |
| lab12 | built from lab11 gold 2026-10-23, gold cut, then status unclear | see CHG-20261023-214000 (partial) |
| others | labapp did not answer | VMs probably not built or stopped |
