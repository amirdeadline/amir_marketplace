# Feature chronology for ION 6.x and controller announcements (Feb 2024 – Sep 2026), with evidence classes

Domain: 7 / 1 | Applies to: WS-021 feature-release matrix (86 records, reviewed 2026-09-30 from public pages, rank-1 URLs with hashes), WS-021 conflict register, ION release notes PDFs 6.3/6.4/6.5, cached public 6.6/6.8 feature pages (WS-022) | Status: DOCUMENTED (public sources) | Last updated: 2026-10-08

## Explanation (plain words)

Prisma SD-WAN has two release streams: **ION device software** (6.3.x, 6.4.x, 6.5.x, 6.6.x, 6.8.x) and the **cloud controller / SCM** (announced monthly, not an ION prerequisite). The WS-021 review distinguishes evidence classes: a feature **listed under a release section**, an **explicit minimum** stated in a guide, a **preview/trial**, a **controller announcement** with no device floor, and a **homepage listing**. A later numeric version does not imply support on every model (Gen-1 ends at 6.5.x; "-I" images carry CDSS). The skill must quote the class with the version.

## Device software floors (explicit minimum or release section; all public rank 1)

| Release | Features (R = release section, E = explicit minimum, P = preview/trial) |
|---|---|
| 5.6.1 | ADEM agent (5.6.1-b13+), LQM non-hub selection, stacked security, TLS syslog/profiles, LAN multicast, cellular telemetry, limited-model FIPS (baseline) |
| 6.0.1 / 6.0.2 | Unified App-ID; stacked policies only (6.0.1); 802.1X/MAC on 1200-S switch ports (6.0.2) |
| 6.1.1 | Branch-source multicast, cellular IPv4/IPv6, DC multicluster (R); 6.1.3 controller/UI migration |
| 6.2.1 | DHCP/ARP IoT visibility (deck), DHCPv6, OpenSSL 1.1.1, User-ID (playbook) |
| 6.3.1 | VRF segmentation (R), performance-policy framework (R), FEC (P), IoT SNMP discovery (R), incident dampening (controller listing), ION 3200 LAN switching (R), routed main-interface HA role (R), IPv6 BGP (CONFLICT with "5.5+" announcement) |
| 6.3.2 | Site templates (ION 5.6+, controller 6.3.2+, E), device prestaging/shells (controller), UDP DNS reachability probing (E), disable Standard VPN destination reoptimisation (E), retirement of `APPLICATION_APP_UNREACHABLE` and `NETWORK_VPNBFD_DOWN` |
| 6.3.6 | Flow-acceptance incident enhancements, application-probe diagnostics, CLI speed test, datapath memory management (R) |
| 6.4.1 | Packet duplication (R), app acceleration trial (P), service health probes (R), system/site metric incidents, Branch Gateway mode (R), OSPF (R), XL710 SR-IOV vION (R), Jinja conditions in templates (controller), DC Standard VPN responder-only (R), incident navigation/bulk acknowledge, subscription usage (controller), VRF Standard VPN and management services (R), ION 3200H (R), >4,000 system apps, configurable circuit L3 probes (R), SVI Auto Operational State (R), automatic APN selection (R) |
| 6.4.2 | VRF direct Internet breakout (R), **Best Path selection (E)**, IPv6 NAT66/NAT64 and ULA (E), custom-app name collision suffix, All Incidents/All Alerts selectors, SASE onboarding enhancements (controller), peak application consumption view |
| 6.5.1 | SGT propagation (R), AES-GCM 128/256 (R), Copilot (cloud), LAN port channels (R), Panorama-managed native SASE onboarding (R), device TACACS+ (R), enhanced DC routing (prefix distribution to fabric, summarisation, asymmetry correction, host-tracking failover) (R), Secure Fabric DC-to-DC (R), graceful and forced Move Flows (R), end-to-end flow visualisation; cellular modem firmware update (ION 5.6.1+, 6.1.6+ recommended) |
| 6.5.2 | **L3 loopbacks (E; IPv4 /32, max 12, not Standard VPN endpoints)**, DC LAN LAG on 3200/5200/9200 (R), DNS liveliness through Standard VPN (R), app acceleration expanded (R), Device-ID enforcement (R, support activation) |
| 6.5.3-I | **Enhanced CDSS Branch Security (E, image)**; SLS logging needs SLS entitlement (**conflicts with the May 2025 guide's 6.5.1-I**, KG-094) |
| 6.6.1 | Branch HA optimisation (UDP app-map replication, instant route availability with BGP graceful restart, readiness-based pre-empt) (R), VRF service-link multiplexing (R), VRF-aware IPFIX (R), cross-VRF DNS (R), **WAN port channels with fabric automation on 3200/5200/9200 (E)**; **Gen-2 and ION 9000 only** |
| 6.8.1 | Coffeeshop policies for Prisma Access Mobile User / Explicit Proxy traffic (R, needs RN-HP), **post-quantum Standard VPN IPsec (E; RFC 8784 PPK, RFC 9370/9242 ML-KEM-512/768/1024 hybrids, TLS 1.3 hybrid groups X25519MLKEM768, SecP256r1MLKEM768, SecP384r1MLKEM1024)**, BGW hop-count forwarding (R), Indonesia controller (R), OSPF fabric default advertisement and metric (E), custom-VRF LAN L3 loopbacks (E; WAN loopbacks Default VRF only), BGP loopback update source (E), OSPF router-ID from loopback, BGW overlay prefix filters (downgrade dependency) |

## Controller / SCM announcements without a device floor (public)

ADEM selected-path synthetic testing (Dec 2024), SCM ION replacement workflow (Jan 2025), SASE Health dashboard (May 2025; absent on at least one tenant in Sep 2026), NGFW as SD-WAN DC integration (Aug 2025; PA-5440 + branch IONs; Advanced SD-WAN and Branch subscriptions), shared SCM security configurations (Oct 2025), ION software EOL notifications (Feb 2026), Site Protection Profiles (Feb 2026), native Site Snapshot (Feb 2026), global BGP configuration with VRF/router ID (homepage Feb 2026), enhanced device-port visualisation and interface security-zone binding workflow (homepage Oct 2025), FedRAMP Moderate (6.1.6+ for 1200-S-5G/3200/9200).

## Chronology conflicts to carry forward (WS-021 register, unchanged)

IPv6 BGP 6.3.1 vs 5.5+; L3 loopback scope (announcement vs guide); native SASE integration eligibility (Cloud Managed only vs both; Panorama explicit in 6.5.1); app acceleration trial 6.4.1 vs broader 6.5.2 (GA boundary unknown); announcement dates vs device revision history; homepage "6.6.2" label (controller vs device); port-channel scope by release (6.5.1 LAN, 6.5.2 DC, 6.6.1 WAN); Site Protection Profiles vs 6.3.6 flow-acceptance profiles; newer-train inheritance not automatic; empty monthly pages (13 of 32) are not proof of no release.

## Correlation with this project's notes

Deck/internal claims now corroborated publicly: Move Flows Forced 6.5.1 (KG-087 partially resolved: Best Path 6.4.2 confirmed by explicit minimum; Forced Move 6.5.1 by release section); hop-aware full mesh for BGW 6.8.1 and DC 6.5.1 (KG-077 partially resolved); PQC shipped in 6.8.1 for Standard VPN (KG-101 resolved: shipped, Standard VPN and controller TLS; fabric tunnels unchanged); Branch Security floor conflict persists (KG-094); Gen-1 end of software line 6.5.x (new fact for note 01-fundamentals/05).

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Release-section and explicit-minimum rows for 6.3–6.5 | VERIFIED (PDF release notes in KB + public pages with hashes) | DOC | WS-045/046/047; WS-021 matrix |
| 6.6.1 and 6.8.1 rows | VERIFIED (public pages cached 2026-09-30) | DOC | WS-022 9b9fd3acba30, c269c51d0b2c |
| Controller announcements | VERIFIED as announcements; device floors UNKNOWN | DOC | WS-021 matrix FEATURE-074..086 |
| Conflict register | VERIFIED as documented conflicts | DOC | WS-021 conflicts file |

## Open questions

- KG-117: official statement of the controller release that corresponds to each monthly announcement (controller versions are not published with the ION release notes).
- KG-087 remainder: deck's 6.4.2 vs 6.5.1 labels for "Best Path Selection" explained (6.4.2 best path; 6.5.1 forced move); mark CONFLICT resolved in note 03-app/05 at next revision.

## Addendum 2026-10-08 (public pages cached under D2; see 03_SOURCE_CATALOG.md §J)

- **6.4.1** (PUB-011, VERIFIED): packet duplication (up to 3 VPN paths), App Acceleration (SaaS/direct internet, performance-policy action; CONFLICT with the 6.4.2/6.5.2 floors in note 03-application-traffic/07, KG-142), service health probes (ICMP/DNS/HTTP/HTTPS over Direct/Fabric/Standard VPN; usable for L3 reachability), system/site health incidents, Branch Gateway, OSPF, SR-IOV XL710 on vION, Jinja conditionals in site templates, standard VPN IKE initiator/responder control (DC-to-DC behind NAT), bulk incident acknowledgement, subscription-usage visibility, VRF support for Standard VPN/NTP/Syslog/SNMP, ION 3200H, 4,000+ App-IDs, configurable L3 reachability probes, SVI Autostate, Auto-APN.
- **6.4.2** (PUB-011, VERIFIED): Direct Internet Access for VRF-based segments; SASE Easy Onboarding enhancements (site templates, automated BGP deployment modes, region redundancy, IPsec profile changes); Best Path selection (needs 6.4.2+); custom apps renamed "-custom"/"-cm" on name clash; Top Application Usage chart; IPv6 ULA on LAN and NAT66/NAT64 for DIA (6.4.2+); All Incidents / All Alerts selectors.
- **6.6.1** (PUB-010, VERIFIED): Gen-2 and ION 9000 only; Branch HA optimization (UDP app-map replication to standby, LAN dynamic routes merged on role change with BGP graceful restart, readiness-based preempt); VRF Service Link Multiplexing (custom-VRF internet via Global service links, VNI in connection marks, failover, native-VRF preference); VRF-aware IPFIX (VRF name in templates, collector/filter contexts on VRF sub-interfaces); multi-VRF DNS service (listen/forward roles per VRF, DNS profiles). No 6.6 upgrade/downgrade considerations page exists (KG-116 closed).
- **6.8.1** (PUB-008/009, VERIFIED): Coffeeshop policies (auto-learned Prisma Access Mobile User and Explicit Proxy gateway prefixes; auto-created "Default Path Coffeeshop Simple Stack Policy Set" with two protected rules for RN-HP tenants; attach to the active stack and enable); PQC for Standard VPN (RFC 8784 PPK Mandatory/Preferred; RFC 9370/9242 up to seven extra rounds with ML-KEM-512/768/1024; TLS 1.3 hybrid groups X25519MLKEM768, SecP256r1MLKEM768, SecP384r1MLKEM1024 for ION-to-controller); hop-count-based forwarding in BGW mode (DC mode since 6.5.1); Indonesia cloud controller; OSPF fabric default-route advertisement toward LAN with custom metric; custom-VRF L3 loopbacks (LAN side; WAN side Default VRF only) usable for SNMP, BGP update source, OSPF router ID; Branch Security "supported starting with the release 6.5.3-I". Upgrade paths: 5.6.x/6.0.x > 6.1.x > 6.3.x > 6.5.x > 6.8.x; 6.2.x > 6.3.x or 6.4.x > 6.5.x > 6.8.x; 6.3.x or 6.4.x > 6.5.x > 6.8.x; 6.5.x > 6.8.x. Downgrade: remove PQC settings and BGW overlay prefix filters first.
- **Compatibility matrix** (PUB-007, updated 2026-10-05, VERIFIED): release columns 5.6.1 / 6.1.1 / 6.1.3 / 6.2.1 / 6.3.1 / 6.4.2 / 6.5.1 / 6.6.1 / 6.8.1; Gen-1 (1000, 2000, 3000, 1200, 1200-C-*, 1200-C5G-EXP) end at the 6.5.1 column; ION 7000 ends at 6.3.x (keep sustained CPU at or below 50 % at branches); ION 9000 and all Gen-2 through 6.8.1; 3200H/3200H-C5G-WW from 6.4.2; vION 7116V/7132V from 6.5.1; 3100v series not on Azure; 7108V/7116V/7132V on OpenStack, ESXi, AWS, Azure, GCP, Oracle.
