# Prisma SD-WAN topic map (navigation only)

This map tells you **where to look and which neighbouring topics to check**. It is not evidence.
Never quote it as a source and never state product behavior from it. Open the files it points to.

- Paths are relative to the KB root. `confluence/sd_wan/<id>_*` means "the page whose file starts with that ID".
- `SRC-000029 grep "<regex>"` means: `kbq.py grep SRC-000029 "<regex>"` (searches only inside that official PDF).
- Verify the map after KB changes: `python <skill_dir>/scripts/kbq.py check-map <skill_dir>/references/sdwan_topic_map.md`

Most Confluence `sd_wan` pages are product requirement or design notes (often "Phase 1/2", "requirements",
"enhancements"). They describe intended behavior, may never have shipped, and are INTERNAL. Corroborate them
with an official source (rank 1-4) before presenting behavior as fact.

## Cross-cutting entry points

- Product index: `palo-alto-knowledge-base/prisma-sd-wan/README.md`
- Best practices (official PDF): SRC-000036 (`SRC-000036 grep "<topic>"`)
- Best practices guide, May 2026 (unregistered local Markdown; cite by path, check against SRC-000036): `palo-alto-knowledge-base/prisma-sd-wan/Prisma SD-WAN Best Practices - May 2026.md`
- Administration guide (official PDF): SRC-000029. CLI reference: SRC-000032 (dated June 2021, see GAP-000012). Release notes 6.3-6.5: SRC-000033..SRC-000035
- Design and deployment guides Oct25: SRC-000038 (design), SRC-000037 (deployment)
- TSE playbooks hub: `palo-alto-knowledge-base/prisma-sd-wan/playbooks/README.md`
- Low-level operator playbook: `palo-alto-knowledge-base/corpus/prisma-sd-wan/playbooks-root/Prisma SD-WAN Low-Level Playbook.md`
- PAEE internal datapath set (SRC-000098..SRC-000105): `palo-alto-knowledge-base/prisma-sd-wan/troubleshooting/paee-datapath/README.md`
- Known KB gaps: `palo-alto-knowledge-base/global-gap-register.json`

## Path selection and application steering

Related: path policy, performance policy, LQM, application probes and reachability, WAN path state, circuit categories and labels, DC group / transit, QoS, VPN state.
Typical questions: "why does this app use MPLS instead of Internet", "path flapping", "app pinned to wrong circuit".

- `confluence/sd_wan/78890282_*` (path selection walk-through), `confluence/sd_wan/78890299_*` (active-backup path selection)
- `confluence/sd_wan/78890365_*` (performance management), `confluence/sd_wan/78890297_*` (application performance management)
- `confluence/sd_wan/78890384_*` (VPN on MPLS and static routing)
- `palo-alto-knowledge-base/prisma-sd-wan/playbooks/official/prisma-sd-wan-playbook-performance-troubleshooting.md`
- Official: `SRC-000029 grep "path polic"`, `SRC-000036 grep "path policy|performance policy|application probe"`

## Link quality monitoring (LQM) and circuit health

Related: WAN interfaces and circuits, probes, loss/latency/jitter, MOS, performance policy thresholds, bandwidth, auto-bandwidth QoS.

- `palo-alto-knowledge-base/prisma-sd-wan/troubleshooting/paee-datapath/lqm-uplink-pkt-loss.md` (SRC-000101, internal)
- `confluence/sd_wan/78890364_*` (LQM probes design limitations), `confluence/sd_wan/78890352_*` (probe service), `confluence/sd_wan/74187079_*` (interface selection for LQM probing)
- `confluence/sd_wan/214567940_*` (LQM NPN), `confluence/sd_wan/223052347_*` (auto bandwidth QoS on WAN circuits)
- `palo-alto-knowledge-base/prisma-sd-wan/playbooks/legacy/l3-reachability-detection-for-internet-circuit.md`
- Official: `SRC-000029 grep "LQM|link quality"`, `SRC-000036 grep "circuit"`

## ION datapath and packet processing

Related: life of packet, DPDK/FC, flow table, mbuf exhaustion, MRL, crash checks, kernel capture.

- `palo-alto-knowledge-base/prisma-sd-wan/troubleshooting/paee-datapath/life-of-packet-datapath-on-prisma-sdwan-ion.md` (SRC-000100)
- `palo-alto-knowledge-base/prisma-sd-wan/troubleshooting/paee-datapath/packet-flow-in-dpdk-release.md` (SRC-000103)
- `palo-alto-knowledge-base/prisma-sd-wan/troubleshooting/paee-datapath/data-collection-mbuf-exhaustion.md` (SRC-000099), `palo-alto-knowledge-base/prisma-sd-wan/troubleshooting/paee-datapath/mrl-troubleshooting.md` (SRC-000102)
- `palo-alto-knowledge-base/prisma-sd-wan/playbooks/official/prisma-sd-wan-playbook-ion-fc-dpdk-stats-life-of-packet.md`
- `palo-alto-knowledge-base/prisma-sd-wan/playbooks/support/prisma-sd-wan-fc-crash-checks.md`, `palo-alto-knowledge-base/prisma-sd-wan/playbooks/support/prisma-sd-wan-capture-packet-on-kernel-on-ion.md`

## Routing (static, BGP, OSPF, VRF, route manager)

Related: path selection, DC/hub routing, Prisma Access BGP, HA.

- `palo-alto-knowledge-base/prisma-sd-wan/playbooks/official/prisma-sd-wan-playbook-bgp-troubleshooting.md`, `palo-alto-knowledge-base/prisma-sd-wan/playbooks/official/prisma-sd-wan-playbooks-ospf-troubleshooting.md`
- `palo-alto-knowledge-base/prisma-sd-wan/playbooks/official/prisma-sd-wan-playbooks-vrf-troubleshooting.md`, `palo-alto-knowledge-base/prisma-sd-wan/playbooks/official/prisma-sd-wan-playbook-l3-loopback-vrf-support-6-8-1.md`
- `palo-alto-knowledge-base/prisma-sd-wan/troubleshooting/paee-datapath/route-manager.md` (SRC-000105), `palo-alto-knowledge-base/prisma-sd-wan/playbooks/legacy/route-manager-debugging.md`
- `confluence/sd_wan/78890438_*` (hub: redistribute static routes into BGP)
- Official: `SRC-000029 grep "BGP|OSPF|static route"`, `SRC-000036 grep "routing|BGP"`

## Controller connectivity and element health

Related: claim/assign lifecycle, ports and timers, element processes and logs, TSF, LENS, Garuda logs.

- `palo-alto-knowledge-base/prisma-sd-wan/playbooks/official/prisma-sd-wan-playbook-element-connectivity-to-controller.md`
- `palo-alto-knowledge-base/prisma-sd-wan/playbooks/official/prisma-sd-wan-playbook-element-troubleshooting.md`, `palo-alto-knowledge-base/prisma-sd-wan/playbooks/official/prisma-sd-wan-playbook-general-isolation.md`
- `palo-alto-knowledge-base/prisma-sd-wan/playbooks/legacy/services-ports-and-timers.md`, `palo-alto-knowledge-base/prisma-sd-wan/playbooks/legacy/element-processes-and-logs.md`
- `palo-alto-knowledge-base/prisma-sd-wan/playbooks/official/prisma-sd-wan-playbook-technical-support-file-tsf-download.md`
- `palo-alto-knowledge-base/prisma-sd-wan/playbooks/support/prisma-sd-wan-lens.md`, `palo-alto-knowledge-base/prisma-sd-wan/playbooks/support/prisma-sd-wan-using-garuda-for-element-logs.md`

## High availability

Related: branch HA topologies, interface/HA pins, failover timing, routing convergence.

- `confluence/sd_wan/346228528_*` (ION HA failover time improvements)
- `palo-alto-knowledge-base/prisma-sd-wan/research/16_HA_TOPOLOGY_DEPENDENCIES.md`
- Official: `SRC-000036 grep "high availability|HA topolog"`, `SRC-000029 grep "high availability"`

## Branch security (ZBFW, threat prevention, URL filtering, DNS security, User-ID)

Related: security policy stacks, CIE / User-ID, CloudBlades, Prisma Access offload.

- `palo-alto-knowledge-base/prisma-sd-wan/playbooks/official/prisma-sd-wan-playbook-threat-prevention.md`, `palo-alto-knowledge-base/prisma-sd-wan/playbooks/official/prisma-sd-wan-playbook-url-filtering.md`
- `palo-alto-knowledge-base/prisma-sd-wan/playbooks/official/prisma-sd-wan-playbook-dns-security.md`, `palo-alto-knowledge-base/prisma-sd-wan/playbooks/official/prisma-sd-wan-playbook-user-id.md`
- `palo-alto-knowledge-base/prisma-sd-wan/playbooks/official/prisma-sd-wan-playbook-intra-vlan-segmentation-ivs.md`
- Official: `SRC-000036 grep "ZBFW|security policy"`, `SRC-000029 grep "zone-based|ZBFW"`

## Prisma Access integration, CloudBlades, converged SD-WAN

Related: hub association, IPsec/BGP to Prisma Access, CloudBlades (FIC, PIC, ZEN, AWS TGW), CSDWAN. Crosses into the Prisma Access product tree (dependency edge Prisma SD-WAN -> Prisma Access).

- `palo-alto-knowledge-base/prisma-sd-wan/playbooks/official/prisma-sd-wan-playbook-prisma-sd-wan-and-prisma-access-hub-association.md`
- `palo-alto-knowledge-base/prisma-sd-wan/playbooks/official/prisma-sd-wan-playbook-converged-sd-wan-csdwan.md`, `confluence/sd_wan/717738125_*` (CSDWAN documentation hub)
- `palo-alto-knowledge-base/prisma-sd-wan/playbooks/official/prisma-sd-wan-playbook-prisma-access-fic-cloudblade.md`, `palo-alto-knowledge-base/prisma-sd-wan/playbooks/official/prisma-sd-wan-playbook-prisma-access-pic-cloudblade.md`
- Official: SRC-000030 (CloudBlades), SRC-000009 / SRC-000010 (extending SD-WAN into AWS / Azure)

## Branch gateway, VPN mesh and hubs

- `palo-alto-knowledge-base/prisma-sd-wan/playbooks/official/prisma-sd-wan-playbook-branch-gateway.md`, `palo-alto-knowledge-base/prisma-sd-wan/playbooks/official/prisma-sd-wan-playbook-branch-gateway-full-mesh.md`
- `palo-alto-knowledge-base/prisma-sd-wan/playbooks/legacy/hub-to-hub-3rd-party-tunnels.md`, `confluence/sd_wan/78890422_*` (hub multi-cluster management)
- Official: `SRC-000036 grep "standard VPN|branch gateway"`

## Cellular

- `palo-alto-knowledge-base/prisma-sd-wan/playbooks/official/prisma-sd-wan-playbook-cellular-connectivity.md`, `palo-alto-knowledge-base/prisma-sd-wan/playbooks/official/prisma-sd-wan-playbook-blackhawk-cellular-dual-modem.md`

## Applications and app detection

Related: custom applications, app definitions, L4 unreachability, path and QoS policy matching.

- `palo-alto-knowledge-base/prisma-sd-wan/playbooks/official/prisma-sd-wan-playbooks-debugging-app-detection.md`, `palo-alto-knowledge-base/prisma-sd-wan/playbooks/support/prisma-sd-wan-debugging-app-detection-on-ion.md`
- `confluence/sd_wan/74187076_*` (app definition and detection), `confluence/sd_wan/78890333_*` (L4 app unreachability detection)
- Official: `SRC-000036 grep "custom application"`

## Device services (DHCP, SNMP, syslog, NTP)

- `palo-alto-knowledge-base/prisma-sd-wan/playbooks/official/prisma-sd-wan-playbooks-dhcp-snmp-and-syslog.md`, `palo-alto-knowledge-base/prisma-sd-wan/playbooks/legacy/snmp-troubleshooting.md`
- `palo-alto-knowledge-base/prisma-sd-wan/research/14_PROBE_SNMP_DEPENDENCIES.md`

## Software lifecycle, upgrades, RMA, licensing

- `palo-alto-knowledge-base/prisma-sd-wan/operations/ion-lifecycle-state-machine.md`, `palo-alto-knowledge-base/prisma-sd-wan/playbooks/official/prisma-sd-wan-playbook-rma.md`
- `palo-alto-knowledge-base/prisma-sd-wan/research/2026-09-30-release-selection-lifecycle-evidence.md`, `palo-alto-knowledge-base/prisma-sd-wan/research/2026-09-30-software-recommendation-implementation.md`
- `confluence/sd_wan/78889819_*` (software lifecycle and mandatory upgrades), `confluence/sd_wan/704430042_*` (upgrade guardrails)
- `palo-alto-knowledge-base/prisma-sd-wan/playbooks/support/prisma-sd-wan-license-activation-verification-guide.md`
- Official: SRC-000033..SRC-000035 (release notes), `SRC-000036 grep "software upgrade"`

## Monitoring, visibility, reporting

Related: SCM dashboards, LQM widgets, bandwidth reporting, availability reporting, alerts.

- `palo-alto-knowledge-base/prisma-sd-wan/monitoring/scm-navigation-links.md`
- `confluence/sd_wan/78890063_*` (SD-WAN health and dashboard updates), `confluence/sd_wan/78890264_*` (operational manageability)
- `confluence/sd_wan/78890311_*` (availability reporting), `confluence/sd_wan/78890241_*` (on-demand bandwidth monitoring)
- `palo-alto-knowledge-base/prisma-sd-wan/playbooks/legacy/alert-for-100k-concurrent-flows.md`, `palo-alto-knowledge-base/prisma-sd-wan/playbooks/legacy/media-a-v-call-troubleshooting.md`
- API monitor semantics are a known gap (GAP-000015)

## APIs, automation, configuration object dependencies

Related: unified SASE API vs legacy CloudGenix API (negative routing), SDK, create/delete order, async jobs, error codes.

- `palo-alto-knowledge-base/prisma-sd-wan/reference/configuration-dependency-model.md`, `palo-alto-knowledge-base/prisma-sd-wan/reference/dependency-errors-and-async.md`
- `palo-alto-knowledge-base/prisma-sd-wan/operations/cleanup-delete-order.md`, `palo-alto-knowledge-base/prisma-sd-wan/automation/cleanup-engine-handoff.md`
- `palo-alto-knowledge-base/prisma-sd-wan/research/02_API_INVENTORY.md`, `palo-alto-knowledge-base/source-material/api-inventory.json`
- OpenAPI: SRC-000046 (unified, preferred) vs SRC-000047 (legacy controller only). SDK: SRC-000052..SRC-000055
- Logical-export field shapes: `ai_prisma_sdwan.md` (SRC-000004, internal QA contract)
- Rate limits and error envelopes are a known gap (GAP-000008)

## Hardware, sizing, virtual form factors

- Official: SRC-000022..SRC-000026 (ION hardware references), SRC-000031 (device specifications)
- `palo-alto-knowledge-base/prisma-sd-wan/licensing-and-requirements/` (vION, internal)
- Official: `SRC-000036 grep "hardware selection|form factor"`

## Architecture and design

- Official: SRC-000038 / SRC-000037 (Secure and Resilient Enterprise Connectivity, Oct25), SRC-000036
- `palo-alto-knowledge-base/reference-architecture/README.md`
- Negative routing: SRC-000027 and SRC-000028 (Oct22 "On Premises Network Security and SD-WAN for the Branch") describe **PAN-OS SD-WAN**, not Prisma SD-WAN.

## Health assessment and maturity assessment

There is no curated health-assessment or maturity framework in this KB. Derive the domains from evidence:
the best-practices sources (SRC-000036 and the May 2026 guide), monitoring material above, and the playbooks
for each domain. Ask the user before fixing thresholds that no source states.

User convention (from the user's separate assessment project, not product documentation): a Maturity Assessment
covers configuration-plane best-practice conformance; a Tenant Health Check covers live state (tunnels, counters,
incidents, experience scores). That work lives in `E:\PC3_Shared\Palo\COE\PRISMA_SDWAN_SnO`; read it only if the
user asks to align with it.
