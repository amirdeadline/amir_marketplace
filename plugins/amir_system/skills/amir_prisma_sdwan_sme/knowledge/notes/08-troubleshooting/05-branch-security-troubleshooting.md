# Troubleshooting Branch Security (Threat Prevention, DNS Security, URL Filtering) and Intra-VLAN Segmentation

Domain: 8 / 4 | Applies to: TSE playbooks Threat Prevention 645404167 (2026-07), DNS Security 646388120 (2025-12), URL Filtering 645960986 (2025-12), IVS 891621909 (2026-07); Admin Guide pp.570–577 (note 04-security/03) | Status: INTERNAL METHOD; version floor 6.5.3-I per all three playbooks | Last updated: 2026-10-08

## Explanation (plain words)

Branch Security runs the **ML7** inspection engine on the ION. Profiles are built in SCM, pushed to the SD-WAN controller, **compiled** into content ("blob") that the ION downloads, grouped into a Security Profile Group and attached to a ZBFW **allow** rule. Most field problems are one of: unsupported model or image, missing licence, profile group not attached, content not compiled or downloaded, cloud service unreachable (PAN-DB, DNS Security cloud, SLS), or an expected limitation (no SSL decryption, cache not synced across HA, DNS Security not applied when the ION is the DNS server).

## Prerequisites (all three playbooks agree)

- Supported models: **ION 1200-H-S, 1200-S, 3108v and above, 3200, 3200H, 5200, 9200**. Not supported: 1000, 1200 (non-S), 2000, 3000, 3104v and below, 7000, 9000.
- Software **6.5.3-I or above** ("-I" image); below that the device ignores security profile groups and does not download threat content. (Admin Guide p.570 says 6.5.1-I: KG-094 stays CONFLICTED; the playbooks and the 6.8 release page favour 6.5.3-I.)
- Branch Security licence (UI elements greyed out without it); SLS licence for cloud logging; the ZBFW rule carrying the profile group must be **Allow** (a Deny wins before inspection).

## Content pipeline and push failures

SCM push → SD-WAN controller → compilation by the **Metis** service in the mL7c pod → blob in S3 → **Eirene** tells the element → element downloads app content and blob → installed into the ML7D library; threat logs to SLS. Push failures show as `TIMEOUT` in SCM Push Status (acknowledged but job timed out) and "Out of Sync" on the Configuration Scope overview; controller-side the Garuda/eirene and metis logs ("UCF" messages) are internal-only evidence. The Branch Security maintenance release PRD (note 04-security/03) tracks compilation stuck in Pending and Thermite certificate issues.

## Threat Prevention (Anti-Spyware, Vulnerability)

- Verify the rule has the profile group and the group has both profiles. On the device `inspect flow detail` shows `SEC-RULE-IDS`, `SEC-PROFILE-GROUP-ID`, `ML7-SESSION-ID`, `ML7-SESSION-STATE` and **`SESS-END-REASON: THREAT`** for a blocked flow.
- Logging: `dump mlog-mgr config` (Cloud Server Enabled, SLS endpoint, tenant), `dump mlog-mgr status` (SLS Connection Established, Thermite Certificate Present, Service Status Running, source interface), `dump mlog-mgr stats` (Logs Rx/Tx/Dropped); Flow Browser shows threat details and Session End Reason; SLS Log Viewer → Network → Threat. Syslog needs the Threat/DNS/URL checkboxes.

## DNS Security

- The `dnssec-agent` process exists only when at least one security rule carries a DNS Security profile; `dump dns-security agent status` (`service_status Running`, `connection_state Connected`; otherwise "Inactive (DNS-Security Profile does not exist in security policy)"); `debug process status name=dnssec-agent`.
- Flow: local lookup (Global Allow List refreshed every **24 h**, user allow list, local cache) → otherwise the DNS query is forwarded **and** a cloud verdict is requested asynchronously → action Allow / Drop / Sinkhole. If the DNS answer arrives after the **100 ms** verdict window the client receives it with **TTL overridden to 30 s**; later queries hit the cache with normal TTL (expected behaviour, explains "slow first lookup").
- Debug: `debug logging facility=dns-sec level=debug`, `… module=messages …`, `debug logging facility=flow-ctrl module=dnssec|dnssec_dp level=debug`. Limitation: **DNS Security is not applied when the ION itself is the DNS server for clients**. Log correlation gap for threat subtype 44 in the SLS viewer noted (Dec 2025).

## URL Filtering (URL Access Management)

- Precedence: custom URL categories beat predefined; multiple matches resolve **BLOCK > ALERT > ALLOW**. HTTPS blocks show as connection errors (no SSL decryption, no block page); plain HTTP shows a standard block page.
- Commands: `dump url-filtering profiles <best-practice|all>`, `inspect url-filtering cloud-category-response <url>`, `dump url-filtering server-status`, `inspect url-filtering server-election`, `inspect url-filtering server-fqdn <fqdn>`, `dump url-cache table` (exports to `/log/syslog/url_cache_table.txt`), `dump url-cache url-name <url>`, `clear url-cache url-name <url>`. "not-resolved" category = cloud connection down (cache misses) or device resource exhaustion dropping requests. Cloud reachability: interface chosen in order controller port → LAN → WAN; the traffic is application **`pan-db-cloud`** and must be allowed by path and security policy (WS-001 also asks for explicit path rules for `pan-db-cloud` and `paloalto-dns-security`). Thermite certificate must be installed. **URL cache is not synchronised across HA peers** (empty cache after failover).

## Intra-VLAN Segmentation (IVS; internal, controller 6.7.1+)

Micro-segmentation inside one VLAN on switch-port IONs: each switch port joins an **L2 Security Zone** (one port per zone), unidirectional ALLOW/DENY rules per zone pair in a security stack bound to the site; `Site > Configuration > MICROSEGMENTATION` toggle selects the VLAN. Verify: `dump microsegments config`, `dump security-policy config zones all` (shows `L2 Zone : true` and interface bindings), `dump security-policy config policy-rules all`. Requirements: SVI switch ports (example platform ION 3545R-D-C5G-WW), existing SVI VLAN, controller 6.7.1+.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Model list and 6.5.3-I floor | UNVERIFIED (three internal playbooks agree; conflicts with guide p.570) | DOC | Confluence 645404167, 646388120, 645960986 |
| Content pipeline (Metis, Eirene, S3, ML7D) | UNVERIFIED (internal architecture) | DOC | same |
| Flow-detail fields for threats; mlog-mgr commands | UNVERIFIED (internal) | DOC | Confluence 645404167 |
| DNS Security 100 ms / 30 s TTL behaviour, 24 h allow list, local-DNS-server limitation | UNVERIFIED (internal) | DOC | Confluence 646388120 |
| URL precedence, HTTPS block-page limitation, cache not synced in HA, pan-db-cloud app | UNVERIFIED (internal; WS-001 corroborates pan-db-cloud rule) | DOC | Confluence 645960986; WS-001 |
| IVS feature and commands | UNVERIFIED (internal 2026; no official doc in KB) | DOC | Confluence 891621909 |

## Open questions

- KG-094 (existing): Branch Security first release.
- KG-122: official documentation of Intra-VLAN Segmentation (release, platforms) under D2.
