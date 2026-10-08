# ION CLI: command families, roles, key commands with syntax, release deltas, capture and export

Domain: 8 | Applies to: ION Device CLI Reference (WS-048, 2025 edition, 21,936 text lines; 179 dump, 62 inspect, 20 debug, 16 clear, 7 config, 5 file commands plus dump-support, dig, ssh, tcpdump); release notes 6.3/6.4/6.5 CLI chapters; WS-001 §CLI access; WS-030 Day 2 ch.10 | Status: DOCUMENTED | Last updated: 2026-10-08

## Explanation (plain words)

The ION command line is read-mostly. `dump` shows configuration and status tables, `inspect` shows live state, `file` handles logs, cores and captures, `debug` runs tests and a few disruptive actions, `clear` resets counters and tables (destroys evidence), `config` covers the small set of local settings (controller reachability, banner, static hosts). Access is through the SCM Device Toolkit (SSH over the TLS control channel, audited) or a console; the device role (Monitor / Read Only / Super) decides which families are allowed. Commands and options change by release, so the running release's help output wins over any list, including this one.

## Roles and families (CLI reference "Role" lines; WS-001)

Monitor: `dump`, `inspect`, `file` (display). Read Only: adds `debug` and `search` for display. Super: everything including `config` and state-changing `debug`/`clear`. Each command entry in the reference lists Role, Related Commands and **Introduced in Release**; e.g. `dump vpn status` 5.0.1, `debug bounce interface` 4.5.1, `dump servicelink` 4.7.1.

## Key commands (syntax from the CLI reference)

| Area | Command | Notes |
|---|---|---|
| Device / controller | `dump overview` | software, model, hardware ID, controller connection and address, MIC and Claim certificate validity, operational interfaces, controller port address |
| | `dump device status`, `dump device info`, `dump software status`, `dump controller status` | state/role/HA; version; control-plane connections |
| | `debug controller reachability <interface>` | prints "Mic cert check passed / Cic cert check passed / Mic cert verify passed / Cic cert verify passed / CIC cert connection test …"; a curl exit code on failure (7 = connection failed) |
| | `ping <src-port> <ip>`, `ping6`, `tcpping <src-port> host:port`, `nslookup`, `dig dns`, `trace route`, `ssh interface`, `curl` (toolkit utilities named in playbooks) | reachability tests from a chosen interface |
| Resources | `inspect memory summary`, `inspect process status`, `debug process status all|name=`, `dump sensor type summary`, `dump device conntrack count` | memory, processes, temperature/fans, conntrack vs limit |
| Interfaces | `dump interface config`, `dump interface status [interface details|module]`, `inspect interface stats <if>`, `inspect system arp`, `dump lldp *`, `dump switch port status`, `dump poe system status`, `dump bypass-pair`, `dump static-arp`, `dump vlan` | link/speed/duplex, counters, ARP, LLDP, switch and PoE |
| Secure Fabric | `dump vpn summary (all | RemoteSite=<site-id> | Active=(true|false) | VpnType=(public|private) | Status=(Up|Down) | vrf-name= | vni=)` | find failing paths of one circuit |
| | `dump vpn status (VpnID= | VpnLinkID=)` (5.0.1) | one link: local/remote IPs, shim IPs, peer VEP, role, encap geneve, cipher, usable, health |
| | `dump bfd status [all | localv4= | remotev4= | localv6= | remotev6= | state=(up|down)]`, `dump vpn ka summary`, `inspect lqm stats (all | path-id=<id> | <path type>)` | BFD sessions; keep-alives; link quality per path |
| Standard VPN | `dump servicelink summary all`, `dump servicelink status`, `inspect servicelink connection`, `inspect servicelink SA` (6.5.1) | SlDev, status, ExtState (e.g. `gre_keepalive_configured`, `tunnel_up`), parent, local/peer IP, type, IPsec profile; IKE/DPD details |
| Routing | `dump routing summary`, `dump routing running configuration`, `dump routing peer status (all | peer-ip= | vrf-name= | address-family=(ipv4|ipv6))` (VRF/AF options 6.3.1), `dump routing peer neighbor|config|received-routes|advertised routes|routes|route-json|route-via`, `dump routing static-route config|reachability-status`, `dump routing prefix-list|route-map`, `dump routing ospf …` (6.4.1), `dump routing vpn host tracker status` (6.5.1), `dump routing prefix-reachability` (6.4.2), `clear routing peer-ip <ip> soft` (6.3.1 `clear routing`), `clear routing ospf` (6.4.1) | BGP/OSPF state and tables; soft reset is the only safe clear |
| Flows / apps | `inspect flow brief (all | [prot-nm=(udp|tcp|icmp) | prot-no=0-255] | srcv4= | srcv6= | srcport= | dstv4= | dstv6= | dstport=)` (IPv6 from 6.2.1), `inspect flow detail …` (columns VRF, SRC, DST, ports, protocol, START-TIME, APP-ID, NET-POLICY, PRI-POLICY, SEC-POLICY, SEC-ACTION, WANPATH-ID, PATH; then TRAFFIC, PRIORITY, DSCP, STATE, IDLE, IFACE, RX_VRF/FWD_VRF, UG-INFO, APP_ACCEL, SEC-RULE-IDS, SEC-PROFILE-GROUP-ID, ML7-SESSION-*, SESS-END-REASON), `dump flow count summary`, `dump flow stats`, `inspect wanpaths` (6.4.1) | live flow table and path decisions |
| | `dump appdef config application=<name>`, `dump app def version`, `inspect app map` / `inspect app-map summary`, `dump app-engine dns-cache all`, `inspect app l4 prefix lookup`, `dump app probe config|status|flow|prefix`, `clear app probe prefix`, `clear app map dynamic`, `clear app engine` | application definitions, maps, probes (clears are disruptive) |
| Policies | `inspect network-policy lookup application=`, `inspect priority policy lookup|hits|conflicts|dropped`, `inspect security-policy lookup|size`, `dump network-policy|priority-policy|security-policy|performance-policy config …`, `inspect performance-policy lookup|incidents|fec status|hits analytics`, `dump nat summary|counters`, `dump nat6 counters` (6.4.2), `dump qos-bwc config`, `inspect qos bwc …` | which rule matched and why |
| Services | `dump dhcp-server config|status`, `dump dhcpstat`, `dump dhcp-relay config|stat interface=`, `inspect dhcplease [all]`, `dump dnsservice config all`, `dump syslog config|status`, `dump syslog-rtr stats`, `dump snmpagent config|status`, `inspect ipfix exporter stats|collector stats|app table|wan path info|interface info`, `dump ipfix config …`, `dump time status|config|log`, `dump radius config|status|statistics`, `dump auth config|status` | element services |
| HA / clusters | `dump spoke-ha status|config`, `dump intra-cluster-tunnel` (6.5.1), `dump standingalarms` | branch HA state and priorities; hub intra-cluster tunnel; standing alarms |
| Cellular | `dump cellular status cwan1`, `dump cellular stats`, `dump cellular config`, `dump cellular module images` | SIM state (Card State, PIN State, PIN/PUK retries, Active SIM), signal, firmware |
| Security services | `dump url-filtering profiles <best-practice|all>`, `inspect url-filtering cloud-category-response <url>`, `dump url-filtering server-status`, `inspect url-filtering server-election|server-fqdn`, `dump url-cache table|url-name <url>`, `clear url-cache url-name <url>`, `dump dns-security agent status`, `dump mlog-mgr config|stats|status`, `dump ml7 mctd counters|session|version` (6.4.1), `dump microsegments config`, `debug process status name=dnssec-agent` | Branch Security (note 05) |
| User-ID | `dump user-id status|summary|agent config|agent status|agent statistics|ip-user-mapping|group-mapping|useridx|groupidx`, `clear user-id agent statistics` | note 04-security/02 |
| App acceleration | `dump appaccel status|keys` (6.5.2) | |
| Capture / files | `tcpdump <interface> [srcv4= dstv4= port= protocol= host= srcport= dstport= …] (show | save <file>)`; `args="<tcpdump filter>"` free-form (**not available in 6.4.2 and 6.5.1; reintroduced 6.4.3 / 6.5.2**); no capture on sub-interfaces or SVIs in 6.1.x–6.3.x (capture on the parent and filter) | automatically included tcpdump options listed in the reference (-v/-vv/-x/-X/-c/-s …) |
| | `file view log <name>`, `file tailf log <name>`, `file list`, `file remove`, `file space available`, `file export <interface> [log|core|capturefile] <destination-URL>` (Role Super, Read Only) | log and capture handling |
| | `dump-support (all | cores | syslog | outputs) file=<tar>` (cores/syslog options 6.4.1) | tech-support bundle; export with `file export` |
| Speed test | `debug bw-test src-interface <if> destination=pcm.cgnx.net` (legacy); `debug speedtest interface <wan-if> [verbose|bytes]` (6.3.6, 6.4.3, 6.5.3) | estimates only; use the WAN interface as source |
| Local config | `config static host add|remove ip <ip> names <fqdn>`, `config banner`, `config interface` (initial), `debug process restart name=<p>` | corner-case controller reachability (forged DNS); banner |
| Disruptive | `debug bounce interface = <n>` (5-second disable, 4.5.1), `debug reboot`, `debug shutdown`, `debug poe interface <id> restart`, `debug process stop|start|restart name=`, `clear flow(s)`, `clear connection`, `clear routing …` (non-soft), `clear dhcplease`, `clear switch mac address entries` | never first; evidence-destroying or service-affecting |

## Release deltas (release notes CLI chapters)

- **6.3.1 new**: `clear routing` (BGP peer sessions), `debug performance-policy`, `debug log-agent eal-file-log`, `dump log-agent iot-snmp config|device-discovery-stats|neighbor-discovery-stats`, `dump log-agent ip-mac-bindings`, `dump performance-policy config policy-rules|policy-sets|policy-set-stacks|threshold-profile`, `dump routing peer neighbor|route-via`, `dump vrf`, `inspect performance-policy fec status`; updated: dhcp-server config/status, dhcpstat, interface config/status, routing peer advertised/config/neighbor/received/route-json/routes/status/route-via, static-route config/reachability-status, prefix-list, route-map.
- **6.4.1 new**: `clear routing ospf`, `dump ml7-mctd counters`, `dump ml7 mctd session|version`, `dump routing ospf`, `dump probe profile|config`; updated: `dump flow count summary`, interface config, overview, performance-policy config, `dump service link summary`, `dump support`, `dump vpn status`, `inspect performance-policy lookup|incidents`, `inspect wanpaths`. **6.4.2 updated**: `dump nat6 counters`, `dump routing prefix-reachability`, `inspect connection`, `inspect flow brief|detail`.
- **6.5.1 new**: `dump intra-cluster-tunnel`, `dump routing vpn host tracker status`, `inspect servicelink connection|SA`, `inspect vpn status`; **6.5.2 new**: `dump appaccel status|keys`; updated `dump flow stats`, `dump interface config`, `inspect flow detail`.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Command syntax and options quoted in the table | VERIFIED | DOC | WS-048 (CLI reference 2025) entries read: dump vpn status/summary, inspect flow brief/detail, debug controller reachability, tcpdump, dump routing peer status, file export, dump-support, dump overview, debug bounce interface, inspect lqm stats, dump servicelink, dump spoke-ha status, dump bfd status |
| Role scopes per family | VERIFIED (Role lines) + WS-001 | DOC | WS-048; WS-001 §CLI access |
| tcpdump limitations by release | VERIFIED | DOC | WS-048 tcpdump entry |
| Release deltas | VERIFIED | DOC | RN 6.3 pp.12–14; RN 6.4 pp.14–16; RN 6.5 pp.13–14 |
| Security-service, User-ID and performance-policy commands | VERIFIED names in RN/CLI reference; option details from playbooks UNVERIFIED | DOC | WS-048; TSE playbooks |
| `debug speedtest` availability 6.3.6/6.4.3/6.5.3 | UNVERIFIED (playbook) / CORROBORATED by WS-021 FEATURE-016 "CLI speed testing 6.3.6" | DOC | Confluence 795149129; WS-021 |

## Open questions

- KG-119: a verified per-release command availability matrix (the reference lists "Introduced in" per command; a generated table would need a full pass over all 290 entries).
