# Term index (Phase 5, 2026-10-08)

Term → note(s) that define or constrain it (paths relative to `notes/`). Expansions use the official spelling where the sources give one.

| Term | Notes |
|---|---|
| Active / Backup / L3 Failure paths | 03-application-traffic/02; 10-design/01 |
| Aggregate Bandwidth (Prisma Access) | 04-security/06; 10-design/01, 02 |
| Analytics / Control / Disabled mode | 01-fundamentals/02 |
| Anynet link, anynetlinks (API) | 02-network/06; 06-api-automation/02 |
| App-ID (unified, 6.0.1), custom application (L3/L4, L7), app-map, DNS cache | 03-application-traffic/01; 08-troubleshooting/04 |
| App Acceleration | 03-application-traffic/07 |
| Application reachability probe | 03-application-traffic/06; 02-network/05 |
| Audit logs | 04-security/05; 05-scm/01 |
| Best Available Bandwidth | 03-application-traffic/02 |
| Best Path policy (6.4.2) | 03-application-traffic/02, 05 |
| BFD mode (aggressive / non-aggressive) | 02-network/01, 05 |
| BGP peer types (classic / core / edge), prefix splitting, route maps | 02-network/08; 10-design/01 |
| Branch gateway (6.4.1), full mesh (6.8.1) | 02-network/06; 01-fundamentals/06 |
| Branch Security / CDSS, Security Profile Groups, "-I" image | 04-security/03; 08-troubleshooting/05 |
| Bypass pair (hardware / virtual), fail-to-wire | 02-network/02; 02-network/07; 10-design/01 |
| Cellular (SIM, APN, PIN/PUK, firmware, Blackhawk) | 02-network/03; 08-troubleshooting/04 |
| Circuit, circuit category (32/32), circuit label, WAN network, cost | 02-network/01 |
| Claim / assign / unassign / declaim / RMA | 01-fundamentals/08, 09; 06-api-automation/02 |
| CloudBlade (AWS TGW, Azure vWAN, GCP NCC, Zscaler, legacy Prisma Access FIC/PIC) | 02-network/12; 04-security/06 |
| Cloud Identity Engine (CIE), User-ID, Cloud User-ID, Device-ID | 04-security/02 |
| Controller connections (MRL, stats, flows, logs), online / partially online / offline | 08-troubleshooting/03; 01-fundamentals/01 |
| Controller port, ZTP-capable port, "use for controller connection" | 02-network/02; 01-fundamentals/01; 10-design/01 |
| Converged SD-WAN (PAN-OS NGFW hub) | 04-security/07 |
| Datapath (OVS vs DPDK, 6WIND, flow controller, intercore queue, punt/inject) | 09-datapath/01, 02 |
| DC cluster, default cluster, soft limit, intra-cluster tunnel | 02-network/06; 02-network/08; 10-design/01 |
| Dependency error codes (`DELETE_FORBIDDEN_*`, `*_IN_USE`) | 06-api-automation/02 |
| Deployment mode (SASE Connectivity: Private-App-Access, Internet-Only, Internet-Only-With-Mobile-User-Access) | 04-security/06; 10-design/01, 02 |
| Device shell | 01-fundamentals/08 |
| DHCP server / relay, DNS service, NTP | 07-operations/02; 08-troubleshooting/04 |
| Domain, service group, DC group, service endpoint, "Prisma Access: All Regions" | 03-application-traffic/03; 10-design/02 |
| Easy Onboarding (SASE), IPSec termination node, tunnel inner pool (/31) | 04-security/06; 10-design/01, 02 |
| Enterprise prefixes, enterprise vs non-enterprise traffic | 02-network/01; 10-design/01, 02 |
| Event codes, incidents vs alerts, correlation, suppression, dampening, incident policies | 07-operations/01 |
| FEC, packet duplication | 03-application-traffic/05 |
| FIPS, FIPS-CC, On-Premises Controller | 01-fundamentals/01; 10-design/04; 07-operations/03 |
| Flow Browser, Flow Decision Data | 03-application-traffic/06; 05-scm/02 |
| Gen-1 / Gen-2 hardware, lifecycle (6.5.x end for Gen-1) | 01-fundamentals/05; 07-operations/03; 09-datapath/01 |
| Guest access (network context + GUEST zone + Local scope) | 10-design/03; 03-application-traffic/03 |
| HA group, HA control interface, priority, preempt, tracking, advertisement interval | 02-network/07; 10-design/01, 02 |
| Host tracking (DC) | 02-network/08 |
| IoT device visibility (SNMP/LLDP discovery) | 04-security/04 |
| IPFIX, syslog, flow logs, SNMP traps | 07-operations/02 |
| IPv6 (IPv4 first; fabric prefers IPv4) | 10-design/01; 02-network/08 |
| L3 Direct Private WAN Forwarding, L3 LAN Forwarding | 01-fundamentals/06; 02-network/08; 10-design/02 |
| L3 reachability probes, service health probes (6.4.1) | 03-application-traffic/06 |
| Licensing (bandwidth vs data-center subscription, tiers, DVR, WCR, site licence) | 01-fundamentals/04; 10-design/01 |
| LQM (Link Quality Monitoring), "Use LQM for Non Hub Paths" | 02-network/01, 05; 03-application-traffic/06 |
| Loopback, port channel, SVI/VLAN, sub-interface | 02-network/02; 10-design/01, 03 |
| Minimize metered LTE usage | 03-application-traffic/02; 02-network/03 |
| Move Flows (graceful / forced) | 03-application-traffic/05; 10-design/01 |
| Multicast (RP, WAN multicast profile, SPT) | 02-network/10 |
| Multitenant Cloud Manager, MSP roles, device allocation, vION licences | 10-design/04; 01-fundamentals/09 |
| NAT policy (zones, pools, DNAT, static NAT, ALG disable), default source NAT | 02-network/11 |
| Navigation generations (Manage/Workflows/Monitor; Configuration/Insights; Nav 3.0) | 05-scm/01 |
| Network context | 03-application-traffic/03; 10-design/01, 03 |
| OAuth client credentials, service account, TSG scope, `GET /sdwan/v2.1/api/profile` | 06-api-automation/01; 04-security/09 |
| Overlay prefix filter (inter-DC) | 02-network/06 |
| Path affinity | 03-application-traffic/01, 02 |
| Path policy stack / set / rule, default and enterprise-default rules | 03-application-traffic/02; 10-design/02 |
| Performance policy, SLA (All Apps 500/5/100; Media 150/2/40) | 03-application-traffic/05; 10-design/01 |
| Post-quantum cryptography (6.8.1) | 04-security/08 |
| Predictive Analytics, Site Summary, dashboards | 05-scm/02 |
| Prisma Access remote network, RN-SPN, ECMP, IKEv2 liveness | 10-design/01; 04-security/06 |
| QoS classes (Platinum/Gold/Silver/Bronze), transfer types, DSCP | 03-application-traffic/04; 10-design/01 |
| RBAC roles, TACACS+, RADIUS, 802.1X | 04-security/05 |
| Route manager, Redis config DB, wanpaths, Rhea/Elapi | 09-datapath/02; 02-network/08 |
| SAML SSO, `accessPolicies` | 04-security/09 |
| Secure fabric link (Prisma SD-WAN VPN), ciphers (GCM 6.5.1) | 02-network/06; 10-design/01 |
| Security zone, ZBFW, stacked security policy, self-zone / intra-zone / default rules, SYN exception | 04-security/01; 10-design/02, 03 |
| Site prefixes, Global vs Local scope | 02-network/06, 08; 10-design/02 |
| Site templates | 01-fundamentals/09 |
| Software upgrade (paths, considerations, bulk 50, rollback) | 07-operations/03 |
| Standard VPN (IPsec/GRE), service link, liveliness probes, passive mode | 02-network/04; 03-application-traffic/03 |
| Static route (next-hop probe, admin distance) | 02-network/08 |
| TPM (`cgtpmtool`), MIC/CIC certificates | 08-troubleshooting/03; 04-security/09 |
| VPN keep-alive (interval / failure count, precedence) | 02-network/05; 03-application-traffic/06 |
| VRF, VRF profile, route leak, simplified DIA | 02-network/09; 10-design/01 |
| WAN Clarity Reports, DVR | 05-scm/02; 01-fundamentals/04 |
| Zero-touch provisioning (ZTP), unclaimed / online-restricted | 01-fundamentals/08; 10-design/01 |
