# External services on the ION: IPFIX, syslog (events and flow logs), SNMP, DNS service, NTP, DHCP

Domain: 7 | Applies to: Admin Guide May 2025 pp. 264–313 (IPFIX pp.265–294, DNS pp.295–303, syslog pp.304–311, SNMP pp.311–313); WS-001 §Network Management (May 2026); 6.6.1 release page (VRF-aware IPFIX and DNS) | Status: DOCUMENTED | Last updated: 2026-10-08

## Explanation (plain words)

Besides what the controller collects, each ION can feed the customer's own tools: **IPFIX** flow records to a collector, **syslog** for device events, authentication logs and per-flow logs, **SNMP** read-only agent plus traps, and it can act as a branch **DNS** cache/forwarder/authoritative server and **DHCP** server or relay. These exports survive a loss of controller connectivity and feed SIEM, NMS and compliance tooling.

## IPFIX (official pp.265–294)

- RFC 7011 export of flow records to third-party collectors; configured **globally through an IPFIX profile** bound to devices, with optional **device-level overrides** (collectors, filters, sampling) under `… > Configure the device > IPFIX`; profiles created at device level become global. **Branch IONs only** can be bound to profiles.
- Profile = template + up to **4 collectors** (protocol, IPv4 or FQDN host, port, optional **collector context**) + up to **8 filters** (protocol, applications, filter context, source/destination global or local prefixes, TCP/UDP port ranges) + sampling (**Export Cache Timeout 10–600 s, default 30**; time-based sampling Time Interval / Time Spacing in ms, defaults 5/5 = 50 %).
- **Collector context** = source interface for export; one context per interface per device (reusable across devices); without a context the **controller port** is used and platforms without a controller port **must** bind one, otherwise major alarm `DEVICE_SW_IPFIX_COLLECTORS_DOWN` (raised only when no configured collector is reachable). Bindable: controller, virtual ports, virtual interfaces, sub-interfaces, PPPoE, bypass pairs; not loopback, standard VPN, port channel. **Filter context** binds to many interfaces, never the controller interface.
- Templates: default flow fields TIME_STAMPS, DST/SRC_IPV4_ADDRESS, DST/SRC_PORT, PROTOCOL (IPv4 only); optional fields include APPLICATION_HOST, APP_DEF_ID, CONNECTION_BIDIR_BYTES/PACKETS, CONNECTION_INIT, CONNECTION_NTT/RTT/SRT/UDPTRT sub-templates (min/max/count/sum), CONNECTION_XACT success/failure counts, DSCP_MAP, DSCP_LAST, INTERFACES (ingress/egress ifIndex), MEDIA_CODEC, MEDIA_JITTER/LOSS/MOS, QOS_QUEUE, RTP_TRANSPORT_TYPE, TRANSPORT_TCP_WINDOWSIZE, TROUBLESHOOT_DECISION_MAP (decision bitmap, up to 4), TROUBLESHOOT_TCP (SYN/FIN/RST/ACK/retransmit/out-of-order deltas), WAN-PATH (cgnxWanPath). Options records: APP_DEF_ID_TABLE (applicationId→applicationName), WAN_PATH_ID_TABLE, LINK_QUALITY_METRICS (per path: up/down jitter, loss, MOS, RTT, link health, bad-health reason bitmap; remote site id 0 = aggregated, non-zero only for private WAN paths), DEVICE_IDENTIFICATION (element, site, tenant IDs, element name). Template Export Timeout and Option Export Timeout default **600 s** (UDP only). Enterprise PEN fields are "CGNX" numbered 1000–1104.
- HA: replicate the profile and contexts on both devices; after switchover the collector sees a new session from the new source interface.
- 6.6.1: VRF name in templates and records; contexts on VRF sub-interfaces; cross-VRF export needs route leaks (public release page).
- CLI: `inspect ipfix exporter stats|collector stats|app table|wan path info|interface info`, `dump ipfix config collector contexts|filter contexts|derived exporters|templates|ipfix overrides|profiles|prefix filters`, `debug ipfix`.

## Syslog (official pp.304–311)

Up to **16 syslog servers per ION**; forwards device events (alerts/alarms), authentication logs and **flow logs**. Severity filter critical/major/minor (default minor; selected level and higher). Flow logging (RFC 5424, `cgxFlowLogV1`, minimum 5.1.17/5.2.3) emits on initial flow-rule classification, update and end-of-flow with CSV body: time, src/dst IP and port, protocol, packets/bytes sent/received, src/dst interface, path id, app name, flow event (New Flow / Flow Update / Delete Flow), ZBFW classification `Rule:SourceZone:DestZone:Action:Code` with codes 1 ALLOW, 2 DENY, 3 REJECT, 4–6 unknown-zone denies. Configuration per device under Syslog Export (from 5.6.1 via **Syslog Profiles**, `Manage > Resources > Configuration Profiles > Syslog`): enable, name, source interface (VRF-aware, bypass pair not allowed, controller port default), profile or custom config, Enable Flow Logging, severity, protocol **UDP (default) / TCP / TLS** (TLS: import certificate; self-signed fails; FQDN must match SAN; **TLS 1.2 only**; OpenSSL 1.1.1 from 6.2.1), server IP or FQDN, port **514 (TCP/UDP) / 6514 (TLS)**. Branch Security threat/DNS/URL logs need the Threat/DNS/URL checkboxes in the profile (note 04-security/03). CLI `dump syslog config|status`, `dump syslog rtr stats`.

## SNMP (official pp.311–313)

Agents and traps **disabled by default**; agent read-only; v2 (community, default `public`) and/or v3 (user, engine ID, NOAUTH/AUTH/PRIV; auth MD5/SHA with 8–25-char phrase; encryption AES/DES); traps: manager IP, **source interface (VRF-aware)**, v2 or v3, **max 16 servers per version**. In 6.x the **ifIndex is not persistent** across datapath restarts; reference statistics by ifName. CLI `dump snmp agent configuration|status`. Incidents correlate with cgx traps (note 01).

## DNS service (official pp.295–303)

Roles (group interfaces that listen and/or forward) and profiles (servers with domain or IP-prefix steering, domain-to-address mapping, query metadata/EDNS client data, cache and DNSSEC proxy/server, authoritative records); one DNS service instance per ION, enabled at device level with role-to-interface bindings; IPv6 servers from 6.2.1; default cache **150** domains, up to **10,000** (0 disables). Use cases: caching, augmenting enterprise DNS, authoritative for small sites, Internet-local resolution for SaaS, DNSSEC proxy or server (trust anchors), IoT DNS (per source address, combine with ZBFW), DNS accounting (client MAC, element name/ID), **DNS survivability** (internal domains to private servers, everything else to Internet DNS, "Listen and Forward" role on LAN interfaces). 6.6.1 adds cross-VRF listen/forward roles. CLI `dig dns`, `dump dns service config`.

## NTP and DHCP (WS-001 §Network Management; Admin Guide elsewhere)

NTP: UDP 123 must be allowed; use UTC for global deployments; NTP authentication MD5/SHA-1 under the device NTP Client (internal recommendation). DHCP server: branch-only, up to **256 subnets per device**, leases persist across reboots, DHCPv6 from 6.2.1, not on secondary IPs; DHCP relay up to **16 server IPs per interface** (internal, WS-001; official DHCP chapter pp.252–258 read in B4).

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| IPFIX profile structure, limits (4 collectors, 8 filters), timeouts, sampling defaults, context rules, alarm name, bindable interfaces | VERIFIED | DOC | SRC-000029 pp.265–277 |
| IPFIX field catalog and options templates | VERIFIED | DOC | SRC-000029 pp.279–294 |
| Syslog limits (16 servers), flow log format and codes, TLS rules, ports | VERIFIED | DOC | SRC-000029 pp.304–311 |
| SNMP defaults, v2/v3 options, 16 trap servers per version, ifIndex non-persistence | VERIFIED | DOC | SRC-000029 pp.311–313 |
| DNS service roles/profiles, cache 150–10,000, use cases | VERIFIED | DOC | SRC-000029 pp.295–303 |
| 6.6.1 VRF-aware IPFIX and DNS | VERIFIED (public release page, cached 2026-09-30) | DOC | WS-022 id 9b9fd3acba30 |
| NTP authentication, DHCP 256 subnets / 16 relay servers | UNVERIFIED (internal, strong) | DOC | WS-001 §Network Management |

## Open questions

- KG-114: official DHCP server scale (256 subnets) and relay server count (16) in the Administrator's Guide DHCP chapter (verify pp.252–258 wording).
