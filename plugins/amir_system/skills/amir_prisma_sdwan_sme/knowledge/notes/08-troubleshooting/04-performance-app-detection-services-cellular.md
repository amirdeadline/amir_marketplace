# Troubleshooting performance, application detection, element services (DHCP/SNMP/syslog) and cellular

Domain: 8 | Applies to: TSE playbooks Performance Troubleshooting 795149129 (2026-03), Debugging App-Detection 719443384 (2026-01), DHCP/SNMP/Syslog 700294438 (2026-01), Cellular Connectivity 294805872 (2026-07), Blackhawk dual modem 891623273 (2026-07); Admin Guide circuit/cellular chapters (notes 02-network/01, 03) | Status: INTERNAL METHOD | Last updated: 2026-10-08

## Performance (throughput, loss, resources)

- **Isolate first**: bypass the customer LAN; test from the ION with the **WAN interface as source**; speed tests are estimates (older builds less accurate). Legacy `debug bw-test src-interface controller1 destination=pcm.cgnx.net`; enhanced **`debug speedtest interface <wan-if> [verbose|bytes]`** from 6.3.6 / 6.4.3 / 6.5.3 (speedtest.net servers; output: ping, download, upload). Root-shell alternative: `curl --interface eth2 <large-file-url> -o test.iso`.
- **Loss over time**: a shell loop with `ping -q -c 1 -I <eth> 8.8.8.8` every second logged to `/log/ping.txt` with `nohup` (Confluence 184330298 "Create Ping script" is the how-to).
- **Overlay throughput between two IONs**: create test files with `dd` (10 MB / 100 MB / 1 GB), then `scp -oBindAddress=<local controller-port IP> elem-admin@<remote controller-port IP>:<file>` so the transfer rides the fabric VPN (push = upload, pull = download); use directories the account can access (`/log/home/elem-admin/work`); **delete the files afterwards**; run several SCP sessions in parallel on large platforms to load the crypto engines; test with QoS enabled and disabled; account for circuit capacity at both ends and model limits.
- **Memory / CPU / FC crashes**: `top` (shift+m / shift+c), `ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%mem | head`, `free -m`; flow-controller memory `fpcmd dpdk-debug-memory | grep Zone` (FC crashes when a zone reaches its limit); probe table size `redis-cli -n 10 -p 6380 keys '*' | grep probe | wc -l` (also `sla`, `app_path_sla`, `probed_app_path_prefix`); OOM kills appear in `user` and `local0` logs ("Out of memory: Killed process … (adem)"). Network-scanning traffic that is not declared as a scan application can flood probe entries and crash the app engine and FC (declare it as a Network Scan Application; Admin Guide app chapter, note 03-app/01). Related 6.8 advisory: ION 1000/1200/2000 above 80 % memory risk reboots after upgrade (note 07-ops/03).

## Application detection (how a flow gets its App-ID)

- **First SYN**: app chosen in-path by FC from standard ports (443/80 → `ssl`/`enterprise-ssl` depending on enterprise prefixes); the path decision is made then. **Custom L4 apps** match on the first packet (IP/port defined). **Custom L7 apps** are **domain-based only**: the ION must see the LAN host's DNS query and response, stores the answer in the `app-engine dns-cache` and creates **app-map** entries (destination IP + port 80 and 443 → app) so the next SYN matches on the first packet; `dump app-engine dns-cache all`, `inspect app-map summary` (columns PROTOCOL, DIRECTION, IP, PORT, APP_NAME, DETECTED_APPS, EXP_TYPE Dynamic, XFER_TYPE, EXPIRY). **App-map entries expire 10 hours after creation and the timer is not refreshed by traffic**, so long-running destinations silently fall back to the port-based app until the next DNS answer.
- If the TCP handshake never completes on the chosen path (e.g. the SSL policy path is broken), SNI-based L7 detection cannot happen and the flow stays on the generic app and its policy. Pages pull content from IPs not seen in the first DNS answer; browsers open many connections within milliseconds, so some flows precede the app-map (compare flow start times). Custom apps beat system apps. System L7 apps (SIP, FTP, SSH) use payload signatures; SaaS apps use server prefixes from the app definition. **No domain-based detection over QUIC (UDP 443)**. The ION CLI app-definition version may lag the tenant; the UI Applications page is authoritative.
- Commands: `dump appdef config application=<name>` (Unified Application ID/Name, Legacy ID, FC Application ID, Type custom/ndpi, Transfer Type, Timeout, Path Affinity, Ingress load %, Domains, App Unreachability detection, Network Scan Application); app-engine debug `debug logging facility=ngpcap module=cgnx level=debug` (revert to info afterwards): look for "Received DNS Response: domain … <-> ip …" and "Match found for CGNX domain"; FC debug shows "Starting app/policy lookup", `app_id lookup for <ip>.<port>`, "custom app hit first", "Static app map lookup app-id" (secondary app). Official equivalents: `inspect app map`, `dump app def version`, `inspect app l4 prefix lookup`.

## Element services: DHCP, SNMP, syslog

- Status: `dump dhcp-server status` (interfaces where the server runs), `dump snmpagent status` ("SNMP agent is running"), `dump syslog status` ("Syslog service is running"); from the shell `ps -ax | grep snmpd` / `grep dhcpd`.
- DHCP server: `dump dhcp-server config` (subnet, broadcast, gateway, ranges, lease times 43200/86400 in the example, static mappings, custom options); shell: Redis DB 13 keys `dhcpserver/subnet/<id>`, logs `tail -f /log/syslog/daemon` (ISC dhcpd) and `elem-mgr*`, config `/config/dhcpd/intf/dhcpd.conf` (vendor class `CGNXCLIENT`), capture `tcpdump <port> save file=<name>.pcap`.
- DHCP relay: `dump dhcp-relay config` (server IPs, source interface, option 82, reforwarding policy), `dump dhcp-relay stat interface=<n>` (Request/Relayed/Response/Drop/NACK/ACK counters); Redis `interface/config/<eth>`.
- Syslog/SNMP failure incidents: `DEVICESW_SYSLOGSERVERS_DOWN` (Informational), `DEVICESW_SNMP_AGENT_RESTART|FAILED_TO_START`, `DEVICESW_DHCPSERVER_ERRORS|RESTART`, `DEVICESW_DHCPRELAY_RESTART` (note 07-ops/01).

## Cellular (ION 1200 4G/5G family; Blackhawk ION 3545R-D-C5G-WW dual modem)

- Checklist: SIM inserted and activated; interface **Admin Up** (no data session otherwise); correct **APN** (Auto APN default for dynamic-IP SIMs from AT&T/T-Mobile/Verizon; else an APN profile with PAP/CHAP credentials from the carrier); all antennas connected, placement away from interference.
- `dump cellular status cwan1`: Card State present / not present (reseat, check orientation), IMSI, ICCID, **PIN State** (`disabled`, `enabledAndVerified` good, `enabledAndNotVerified` = configured PIN mismatch → Enter PIN, `blocked` = wrong PIN three times → PUK from the carrier → Unblock SIM, `permanentlyBlocked` = wrong PUK ten times → replace SIM, `unknown` → reseat), PIN/PUK retries, Active SIM. Alarms `DEVICE_CELLULAR_SIM_PIN` / `_SIM_PUK_NEEDED` (Critical). Carrier firmware (AT&T, T-Mobile, Verizon, Generic PTCRB/GCF) is pre-loaded and selected by the SIM; automatic SIM switchover on failure.
- Blackhawk (internal, 2026): ruggedised −40…+70 °C (Rev A max 60 °C), AMD 8-core CPU, Marvell switch, Intel Max 10 CPLD (eSPI), NVMe, 12×RJ45 (ports 1–4 and 15 L3, 5–12 L2) + 2 SFP (13–14), 18 thermal sensors (CPU high 3 consecutive 5-minute readings → shutdown; non-CPU 5 consecutive), dual DC PSUs; **two independent 5G modems (EM9293), one SIM each**, carrier diversity, per-application carrier selection, GPS per modem, independent firmware (QDL flashing); modem states BOOTMODE / OPERATIONAL / DISCONNECTED / UNKNOWN; RF metrics RSSI, RSRP, RSRQ, SINR; unsupported: combo port, HW bypass, PoE in software (at FCS), MSTP, IPv6 on cellular, L2/L3 mode change. Treat all Blackhawk facts as internal until the hardware reference is in the KB.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Speed-test commands and release availability; SCP overlay test; memory/FC diagnostics | UNVERIFIED (internal playbook, 2026) | DOC | Confluence 795149129 |
| App-detection mechanics incl. 10-hour app-map expiry, QUIC limitation, DNS-based custom L7 | UNVERIFIED (internal playbook) but consistent with official app chapter (domains, probes) | DOC | Confluence 719443384; SRC-000029 app chapter |
| Service status commands and log/Redis locations | UNVERIFIED (internal; shell-level) | DOC | Confluence 700294438 |
| Cellular SIM/PIN states and actions | CORROBORATED (official cellular chapter read in B4 documents SIM operations; playbook adds state table) | DOC | Confluence 294805872; SRC-000029 cellular pages |
| Blackhawk platform details | UNVERIFIED (internal, 2026-07); no datasheet in KB | DOC | Confluence 891623273 |

## Open questions

- KG-120: official documentation for the ION 3545R-D-C5G-WW (Blackhawk) and dual-modem cellular (hardware reference, release notes) under D2.
- KG-121: official statement of app-map expiry (10 h) and the QUIC limitation.
