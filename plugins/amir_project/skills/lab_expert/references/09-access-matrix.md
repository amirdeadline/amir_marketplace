# 09 — Access matrix: how to reach every layer of every lab

One table per layer: from where, how, which identity, what can go wrong. Applies to every
pod (`dev`, `lab1`…`lab25`). Get the pod's numbers with `python $LE/scripts/lab_facts.py <lab>`.
Credentials are named here, never quoted. Read values only inside a VM or container and
never echo them.

```text
L0 workstation (Windows jumpbox, Git Bash/PowerShell, gcloud, terraform.exe, python 3.12)
 ├─ L1 GCP control plane (gcloud as you; Terraform/snapshots as gns3-terraform-runner)
 ├─ L2 GNS3 host VMs  gns3-1..4    nic1 SSH :22  | IAP 127.0.0.1:<port> | serial console
 │    ├─ L3 inside the pod: nic0 10.100.20.11-14, VXLAN 172.31.255.0/24, gcsfuse /opt/gns3/shared
 │    ├─ L4 GNS3 API + consoles (https://<nic1>:3080/v2, telnet/vnc console ports)
 │    ├─ L5 GNS3 overlay nodes (devices) on OOB 10.10.99.0/24 behind GCP-Router 10.10.99.1
 │    └─ L6 labapp (gns3-1 :443) + containers; admin dashboard (dev-gns3-1 /labs/)
 └─ L7 SCM tenants (one TSG per lab) via api.sase.paloaltonetworks.com
```

## L0 — Workstation

| Item | Value |
|---|---|
| Repo | `E:\PC3_Shared\Palo\COE\Prisma_SASE_LAB\PaloAlto_SASE_LAB` (donor). Official product repo `SDWAN_LAB/` |
| SSH key | `C:\Users\amir\.ssh\sdwan` (Git Bash `/c/Users/amir/.ssh/sdwan`), user `root` |
| Reaches | nic1 `10.95.98.128/25` (only while each VM has its 10/8 route), GCP APIs, SCM APIs |
| Cannot reach | nic0 `10.100.20.x`, OOB `10.10.99.x` — go through a GNS3 host |
| Python | `python` = 3.12 (Windows); force `PYTHONIOENCODING=utf-8` for CLIs that print arrows |

## L1 — GCP

| Action | How | Identity |
|---|---|---|
| List / describe VMs, disks, snapshots, quota, logs | `gcloud compute … --project sase-lab-sdwan` | owner's login (`gcloud auth login`) |
| Terraform plan/apply/destroy, snapshot create/delete | `GOOGLE_OAUTH_ACCESS_TOKEN=$(gcloud auth print-access-token --impersonate-service-account=gns3-terraform-runner@sase-lab-sdwan.iam.gserviceaccount.com)` | runner SA |
| VM console when SSH is dead | `gcloud compute instances get-serial-port-output <vm> --zone <z>` | owner |
| Secrets (names) | `gcloud secrets list --project sase-lab-sdwan` — never `versions access` to the screen | owner |

Zones: `us-west2-a` for labs; **dev is `us-west2-c`** (C3). Token errors ("Reauthentication
failed") → ask the owner to log in; do not loop.

## L2 — GNS3 host VMs (all 4 of every pod)

| Path | Command | When |
|---|---|---|
| A nic1 | `ssh -i <key> -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR root@<nic1>` | first choice |
| B IAP | `gcloud compute start-iap-tunnel <vm> 22 --local-host-port=localhost:<20000+100*id+20+i> --zone <z> --project sase-lab-sdwan` then `ssh -p <port> root@127.0.0.1`; or `python dev/scripts/start_gcp_tunnels.py --lab <id> --ssh` | nic1 down (route lost, policy routing) |
| C serial | `get-serial-port-output` | VM hung / no network |
| Pipe a local script | `ssh … root@<nic1> 'bash -s' -- <args> < script.sh` | collectors, fixes |

VM names: `lab-<id>-gns3-<i>` (dev: `dev-gns3-<i>`). Host keys change each rebuild.
nic1 interface is `ens5` on N2, `ens4` on dev's C3 — find it by the `10.95.98.x` address.

## L3 — Inside a pod

| From | To | How |
|---|---|---|
| gns3-1 | gns3-2..4 | `ssh root@10.100.20.12..14` (fleet key `/root/.ssh/gns3-fleet` where installed), else jump from the workstation to each nic1 |
| any VM | shared tree | `/opt/gns3/shared/lab` (gcsfuse, read-write, same bucket for all labs!) |
| gns3-1 | OOB | `br-lab11` 10.10.0.1/30 → GNS3 cloud node → GCP-Router 10.10.99.1 |

## L4 — GNS3 API and consoles

| Item | How |
|---|---|
| API | `https://<gns3-1 nic1>:3080/v2/…` (or `https://127.0.0.1:3080/v2` on gns3-1), Basic auth: container env `GNS3_USERNAME` / `GNS3_PASSWORD` (`docker exec sase-labapp printenv GNS3_USERNAME`, password never printed) |
| Useful calls | `GET /v2/version`, `/v2/computes` (4, on own nic1), `/v2/projects` (`Prisma-SASE-Basic`), `/v2/projects/<pid>/nodes` (status, `console`, `console_host`, `console_type`) |
| Console of a node | telnet/VNC to the **hosting** server's nic1 + the **live** console port from the nodes API. `design.json` console ports can be stale |
| Start a stopped node | `POST /v2/projects/<pid>/nodes/<nid>/start` (L2). Never close/reopen the project; never restart gns3server without the owner |
| Docker nodes (webterm, toolbox) | on the hosting VM: `docker ps --filter name=GNS3.` then `docker exec -it <name> sh` |

Live pods run 52 nodes; `design.json` lists 48 (+ webterm/test extras added later).

## L5 — GNS3 overlay nodes (devices)

Same OOB plan in every pod (`design.json` → `projects["Prisma-SASE-Basic"].nodes[*].oob_management`).
Management network `10.10.99.0/24`, gateway/DNS/NTP `10.10.99.1` (GCP-Router, SNAT so devices
see you as 10.10.99.1), DHCP pool .20–.250.

| Way in | Command | Notes |
|---|---|---|
| From the workstation (DNAT) | `ssh -p <ssh_port> <user>@<gns3-1 nic1>`; NGFW GUI `https://<gns3-1 nic1>:<https_port>/`; RDP `<gns3-1 nic1>:<rdp_port>` | ports 5000–5500 on gns3-1 nic1, nft DNAT to the OOB IP; target node must be started |
| From gns3-1 | `ssh <user>@10.10.99.x` | read the password from `design.json` on the host into a variable (`sshpass -e`), never echo it |
| Console | see L4 | for devices without working mgmt (e.g. ION before VFF activation) |
| Whole matrix | `docker exec sase-labapp python3 -m lab_automation qa-smoke --lab <key>` | OOB ping-all (36), 52 nodes started, labapp :443 |

Device table (from `design.json`; same for every pod — the DNAT ports are on **that pod's**
gns3-1 nic1; users are the design defaults; passwords live in `design.json`
`oob_management.credentials` and are not copied here):

| Node | Kind | Host | Console (design, may be stale) | OOB IP | DNAT on gns3-1 nic1 (ssh / https / rdp) | User |
|---|---|---|---|---|---|---|
| GCP-Router | qemu | gns3-1 | telnet 5566 | 10.10.99.1 | 5001 / - / - | admin |
| DC1-Server2 | qemu | gns3-1 | vnc 5902 | 10.10.99.12 | 5011 / 5411 / - | labuser |
| DC1-PE | qemu | gns3-1 | telnet 5560 | 10.10.99.51 | 5003 / - / - | admin |
| DC1-SW2 | qemu | gns3-1 | telnet 5564 | 10.10.99.59 | 5009 / - / - | admin |
| DC1-FW1 | qemu | gns3-1 | telnet 5571 | 10.10.99.111 | 5004 / 5404 / - | admin |
| DC1-FW2 | qemu | gns3-1 | telnet 5573 | 10.10.99.112 | 5005 / 5405 / - | admin |
| DC1-ION1 | qemu | gns3-1 | telnet 5556 | 10.10.99.113 | 5006 / - / - | elem-admin |
| DC1-ION2 | qemu | gns3-1 | telnet 5558 | 10.10.99.114 | 5007 / - / - | elem-admin |
| DC1-SW1 | qemu | gns3-1 | telnet 5562 | 10.10.99.115 | 5008 / - / - | admin |
| DC1-Server1 | qemu | gns3-1 | vnc 5901 | 10.10.99.141 | 5010 / - / 5110 | Administrator |
| DC2-Server1 | qemu | gns3-2 | vnc 5902 | 10.10.99.21 | 5019 / - / 5119 | Administrator |
| DC2-Server2 | qemu | gns3-2 | vnc 5901 | 10.10.99.22 | 5020 / 5420 / - | labuser |
| DC2-PE | qemu | gns3-2 | telnet 5539 | 10.10.99.52 | 5012 / - / - | admin |
| DC2-FW1 | qemu | gns3-2 | telnet 5545 | 10.10.99.121 | 5013 / 5413 / - | admin |
| DC2-FW2 | qemu | gns3-2 | telnet 5547 | 10.10.99.122 | 5014 / 5414 / - | admin |
| DC2-ION1 | qemu | gns3-2 | telnet 5535 | 10.10.99.123 | 5015 / - / - | elem-admin |
| DC2-ION2 | qemu | gns3-2 | telnet 5537 | 10.10.99.124 | 5016 / - / - | elem-admin |
| DC2-SW1 | qemu | gns3-2 | telnet 5541 | 10.10.99.125 | 5017 / - / - | admin |
| DC2-SW2 | qemu | gns3-2 | telnet 5543 | 10.10.99.126 | 5018 / - / - | admin |
| BOS-PE | qemu | gns3-3 | telnet 5542 | 10.10.99.53 | 5021 / - / - | admin |
| BOS-PC | qemu | gns3-3 | vnc 5901 | 10.10.99.146 | 5026 / - / 5126 | Administrator |
| DAL-PC | docker | gns3-3 | vnc 5907 | 10.10.99.147 | - / - / - | root |
| Internet | qemu | gns3-3 | telnet 5546 | 10.10.99.201 | 5002 / - / - | admin |
| BOS-FW1 | qemu | gns3-3 | telnet 5549 | 10.10.99.211 | 5022 / 5422 / - | admin |
| BOS-ION1 | qemu | gns3-3 | telnet 5537 | 10.10.99.213 | 5023 / - / - | elem-admin |
| BOS-ION2 | qemu | gns3-3 | telnet 5540 | 10.10.99.214 | 5024 / - / - | elem-admin |
| BOS-SW1 | qemu | gns3-3 | telnet 5544 | 10.10.99.215 | 5025 / - / - | admin |
| DAL-PE | qemu | gns3-4 | telnet 5547 | 10.10.99.54 | 5027 / - / - | admin |
| ATL-PE | qemu | gns3-4 | telnet 5537 | 10.10.99.55 | 5033 / - / - | admin |
| ATL-SW1 | qemu | gns3-4 | telnet 5539 | 10.10.99.135 | 5036 / - / - | admin |
| DAL-FW1 | qemu | gns3-4 | telnet 5552 | 10.10.99.221 | 5028 / 5428 / - | admin |
| DAL-ION1 | qemu | gns3-4 | telnet 5543 | 10.10.99.223 | 5029 / - / - | elem-admin |
| DAL-ION2 | qemu | gns3-4 | telnet 5545 | 10.10.99.224 | 5030 / - / - | elem-admin |
| DAL-SW1 | qemu | gns3-4 | telnet 5549 | 10.10.99.225 | 5031 / - / - | admin |
| ATL-FW1 | qemu | gns3-4 | telnet 5554 | 10.10.99.231 | 5034 / 5434 / - | admin |
| ATL-ION1 | qemu | gns3-4 | telnet 5535 | 10.10.99.233 | 5035 / - / - | elem-admin |

Nodes without OOB (12): AT&T-MPLS, ATL-INET1-SW, BOS-INET1-SW, BOS-INET2-SW, DAL-INET1-SW, DAL-INET2-SW, DC1-INET1-SW, DC1-INET2-SW, DC2-INET1-SW, DC2-INET2-SW, GCP, MGMT

Device CLIs: PAN-OS (`admin`, `show system info`, `ping source <ip> host <ip>`), Prisma
SD-WAN ION (`elem-admin`; before Day0 the console shows the VFF "Select an ION model"
prompt; idle VFF drops to a login prompt — `.ai/knowledge/vion-vff-idle-behavior.md`),
VyOS PE / GCP-Router (`admin`, `show interfaces`, `show ip route`), Windows servers
(`Administrator`, RDP), Linux Server2 (`labuser`, Grafana/InfluxDB monitoring).

## L6 — labapp, containers, admin dashboard

| Target | How |
|---|---|
| labapp health | `curl -ks https://<gns3-1 nic1>/health/live` (no auth) |
| labapp lifecycle API | on gns3-1: `P=$(grep ^ADMIN_PASS= /run/labapp/labapp.env \| cut -d= -f2-); curl -ks -H "X-Admin-Password: $P" https://127.0.0.1/lab/status` |
| labapp shell / CLI | `docker exec -it sase-labapp bash`; `python3 -m lab_automation <verb> --lab <key>` (container has `/labs`, SCM creds, OOB reach) |
| Containers | `sase-labapp`, `sase-labapp-nginx`, `sase-lab-assistant` (gns3-1 only); workers run none |
| Admin dashboard | `https://srv1.dev.saselab.paloaltonetworks.com/labs/` (dev-gns3-1 `127.0.0.1:8095`, container `saselab-admin`); API `GET /labs/api/fleet` etc. (05) |

## L7 — SCM tenants (Prisma SD-WAN, Prisma Access, CIE)

| Item | Value |
|---|---|
| Tenant per lab | TSG `labs.json.labs.<key>.tsg_id`, name `COE-SASE-LAB-PLATFORM-NN` (`-dev`), `pa_tenant_id` = same id |
| Parent | `1479602777` — never write; listing children only (`labs/scripts/scm/list_parent_child_tsgs.py`) |
| Auth | OAuth2 client credentials, `POST https://auth.apps.paloaltonetworks.com/oauth2/access_token`, `scope=tsg_id:<TSG>`, client from secrets `scm-client-id` / `scm-client-secret` (env `SCM_CLIENT_ID` / `SCM_CLIENT_SECRET`) |
| API base | `https://api.sase.paloaltonetworks.com` |
| SD-WAN rule | every new TCP connection must `GET /sdwan/v2.1/api/profile` before id-scoped calls, else empty-body `DEF_403` |
| SD-WAN reads | machines `/sdwan/v2.5/api/machines`, elements `/sdwan/v3.2/api/elements`, sites, operator `…/profile` |
| CloudGenix token | `POST /sdwan/v2.1/api/operators/{operator_id}/authtokens` → `CLOUDGENIX_AUTH_TOKEN` (ION VFF activation), minted per lab TSG on Day0 |
| Safe client | `lab_automation.ops.scm.client.ScmClient.from_env(<lab>)` — enforces `guards.assert_lab_tsg_allowed` (registry TSG, parent refuse) |
| Where to run | inside `sase-labapp` (any pod) or the admin container on dev-gns3-1 — credentials already there; do not copy client secrets to the workstation |
| Read-only commands | `python3 -m lab_automation scm-cleanup --lab <key> --product sdwan --dry-run` (inventory + plan); admin dashboard **IONs** page; `status --lab <key>` |
| Writes (owner only) | `scm-cleanup --apply`, `ions-deactivate`, `sdwan-configure --apply`, ION retire, cleanup |
| Student access | Day0 grants the reservation user SCM roles (lab_user_basics + network admin + security admin); cleanup revokes it |
| UI | Strata Cloud Manager, pick tenant `COE-SASE-LAB-PLATFORM-NN` |
