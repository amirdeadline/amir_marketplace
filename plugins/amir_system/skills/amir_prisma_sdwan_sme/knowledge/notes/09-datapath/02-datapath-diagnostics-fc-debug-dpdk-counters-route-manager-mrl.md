# Datapath diagnostics: FC debug, DPDK port and stage counters, process restarts and cores, route manager, MRL interface selection, data collection scripts

Domain: 9 / 8 | Applies to: TSE playbooks SD-WAN Datapath 5.6.x 175768166 (2026-01), FC/DPDK Life of Packet 700294454 (2026-01); CGXKB "FC Debug" 184330031 (2025-07), Flow Debugging 74187066, Route Manager Debugging 74187077 (2016); PAEE Route Manager SRC-000105 (Dec 2024, "in progress"), MRL Troubleshooting SRC-000102 (2024), mbuf exhaustion SRC-000099, 6WIND data collection SRC-000098 | Status: INTERNAL ONLY; shell-level commands are support-only | Last updated: 2026-10-08

## Explanation (plain words)

When SCM and the toolkit `dump`/`inspect` commands have localised a drop or a wrong path to the ION itself, support engineers use three deeper layers: **FC debug** (per-flow trace of app and policy decisions), **DPDK stage counters** (where in the pipeline packets are lost: port Rx, 6WIND, FC, 6WIND egress, port Tx, punt/inject), and the **control-plane databases** (Redis config/state DBs, route manager and FRR tables, MRL logs). None of these are customer procedures; the skill should describe them as what TAC will do and what to collect.

## FC debug (CGXKB 184330031; playbooks)

- Toolkit: `debug flow create id=1 host1=<ip> host2=<ip>` (filter), `debug flow view all`, then `debug logging facility=flow-ctrl module=flow_ext|flow|policy|wan_path level=trace` (`debug logging facility=flow-ctrl` alone shows current settings); read with `debug logs follow flow-ctrl` or `file tailf log flow-ctrl`; **always revert every module to `info`** and `debug flow delete id=`. Shell equivalent `/usr/lib/lion/fc_log.py set-filter -F 1 --host1 … --host2 … --protocol tcp|udp` and `delete-all`.
- Use for flow drops, app detection, security and path policy questions; take a PCAP at the same time for drop cases. **Trace logging left enabled makes datapath threads busy and the monitor declares them unresponsive** ("monitor files"), a frequent self-inflicted cause of FC restarts.
- What the trace shows (notes 04-security/01, 08-troubleshooting/04): app lookups by tuple combinations, custom app precedence, static app-map (port) lookup, network policy lookup with the most specific app then app 0, WAN path candidates pruned by active/backup and by security per destination zone, path selection, re-evaluation on continuous detection.
- **Requeue drops**: when the terminal app changes (http → custom app) QoS and security policy are re-evaluated, path policy is not; a drop after requeue is investigated with FC debug, ZBFW state, before/after policies and app-map (`inspect app-map summary`).
- Flow Decision Bitmap (UI Advanced Info / Flow Decision Data) explains exclusions; "Asymmetry path change"/"Asymmetry bridge" and "secondary flow"/"Strict affinity" markers explain backup-path selection despite an active path (DC routing asymmetry; session or path affinity after a recent policy change).

## DPDK stage counters (playbook 700294454; use only after the ION is proven to drop)

1. Map the front-panel port to the Ethernet name: `dump interface status <port>` (Device `ethrN`, "DPDK Controlled: true"). Shell: `fp-shmem-ports -d | grep ethrN` gives the physical **DPDK port** and its **fpvi** port (used for punt/inject accounting).
2. Ingress: toolkit `dump dpdk port stats` → `ierrors` (L1/L2 errors), `inombuf` (mbuf leak), `imissed` (Rx queue full/backpressure); shell `fp-cli dpdk-port-stats <port>` or `fpcmd dpdk-port-stats <port>` → `rx_good_packets`, `rx_mbuf_allocation_errors`, per-queue `rx_q<n>`.
3. 6WIND processing before FC and on egress: `fp-cli stats` / `fpcmd stats` (toolkit `dump dpdk stats`) global stats; 6.3.6 control-protection counters `fpn.rx_cp_passthrough|rx_cp_kept|rx_cp_overrun|rx_dp_drop`.
4. FC stage: `inspect flow brief|detail` must show the flow with the right PATH (not `unknown_flow_path`) and SEC-ACTION allow; otherwise it is a policy/routing/app problem, not a datapath drop; routing (ip tables, ip rules, prefix reachability) must be ruled out first.
5. Egress: `dump dpdk port stats` → `oerrors`; `fp-cli dpdk-port-stats <egress port>`.
6. Punt/for-us packets: stats on the ingress port's **fpvi** port (rx counters); inject packets: egress port's fpvi (tx counters). Kernel-side capture only with a copied tcpdump binary (`cpdump -s0 -c20 -nei ethrN <filter>`) on the pseudo interface, tightly filtered, never left running, binary removed afterwards ("only when you know what you're doing").
7. Decision tree in the playbook: packet not seen on the ingress capture → external; seen on ingress but not egress and no flow entry → check decrypted packet on the VPN/service-link veth pair, then routing; flow entry present with correct path and allow → stage counters 5–8.
- Supporting captures: `tcpdump <port> args="host A and host B" show`; on VPN interfaces (shell) `tcpdump -eni vpnNN` shows the VXLAN/Geneve-encapsulated inner packets; `ovs-dpctl dump-flows | grep <ip>` on 5.6.x; `inspect flow internal …` for the internal flow record.

## Process restarts, cores and memory (playbooks 175768166, 795149129)

Any process restart raises an alarm; `sup status` (shell) shows `fc` restarts. With core files (`/log/cgnx_infra/core_dir/`): export them, add FC debug logs for any tuple seen in the core, attach all cores; engineering uses gdb on the matching build (`gdb /bin/fp_appgw core.<n>`, `bt full`). Without cores: tar `/log/syslog`, alarms around the time, audit log. "Monitor files" → check `debug logging facility=flow-ctrl` for anything above info. Memory: `top`, `ps … --sort=-%mem`, `free -m`; `fpcmd dpdk-debug-memory | grep Zone` (FC crashes at the zone limit); probe-table size in Redis (`redis-cli -n 10 -p 6380 keys '*' | grep probe | wc -l`); OOM kills in `user`/`local0` logs. Data-collection scripts from engineering: `cont_dpdk_record.sh <device>` for about 5 minutes (mbuf exhaustion, SRC-000099), `ts_and_port_data.sh <device>` for 90 minutes and `cdump.sh` kernel capture for about 1 minute (6WIND issues, SRC-000098), always followed by `dump-support all file=<name>` and clean-up of the scripts and outputs.

## VPN and service-link internals (playbook 175768166)

Fabric VPN causes: peer unreachable, ESP failures, MAC mismatch, both peers behind dynamic NAT, keep-alive failures; collect `dump vpn status <id>`, tcpdump of the peers, `debug logging facility=vpn module=vpn_ctun module=vpn_dtun module=vpn_sm level=debug` (log `/log/syslog/vpn`), SA and policy dumps `ip -s xfrm s` / `ip -s xfrm p` (keys allow Wireshark ESP decryption). Service links (standard VPN): peer unreachable, PSK mismatch (local auth failure), tunnel flap (peer-sent delete), config change, liveliness down, configuration mismatch; `dump servicelink summary|status <name>` (ExtState error codes), `debug logging facility=tunnelmgr level=debug`, `debug servicelink logging enabled`, logs `/log/syslog/tunnelmgr/` and strongSwan `/log/syslog/local1`, `ipsec statusall`, `ip tunnel show`. Known pattern: intermittent flaps when ION and Prisma Access rekey simultaneously; PAN-OS 10.2.4+ uses new keys immediately after rekey.

## Route manager (SRC-000105, Dec 2024; CGXKB 74187077, 2016)

- Reads config DB (Redis 11: interfaces, static routes, BGP config, **wanpaths**, `prefixset/<site-id>`, `config/enterpriseprefixset`, `config/localprefixset`, `config/core|edge/<peer-id>`, `config/wan_networks`, `config/bfdpeers`), builds the state DB (interface state, FIB for VPN/LAN/route leak; wiped on reboot), resolves routes through the FIB manager, programs the kernel (veth pairs, ip rules, route tables, neighbours) and configures **FRR** for BGP. Threads: config, backend (wanpath/static/OSPF/interface/element-state), probe/static monitor, data publisher (peer status, reachable/advertised prefixes, next-hop reachability).
- Wanpaths are produced on the controller by the **Rhea** service from UI config (Eirene) or element BGP prefixes and pushed via `elapi` (`PUT …/wanpathsbulk` in elapi logs). On the hub, duplicate prefixes from two sites show as `add_branch_prefix_route: … ex=(17, 'File exists')`; withdrawal keeps a prefix still used by another site ("Skip prefix withdraw … used by other site"). `wan_path_update` triggers: interface IP/scope change, static route change, BGP learned route change, spoke HA state change. Kernel tables: per-interface VRF tables (`mgmt` 200, `internet-ethN` 100+, hub `core-in` 10 / `core-out-vethN` 11+), `ip rule`, `ip route show table 2010` (all-peer-in). A wanpath mismatch between hub and spoke blackholes traffic (check both sides).

## MRL (controller connection) interface selection (SRC-000102, 2024)

`mrl_agent` logs `on_close_closed`, `monitor_warning_unacknowledged_messages_count` (link drops), `getsockopt_Got_ethlist`, `getsockopt_using_interface`, `on_open`. Interface order for connection attempts: **controller ports → LAN interfaces → WAN interfaces with "use for controller connection" true (sorted by cost) → excluded WAN interfaces (sorted by cost)**; the last-used interface is marked "expensive" if it is last in the WAN list or excluded, in which case the next attempt restarts from the first interface; otherwise the same interface is retried for 20 s before moving on. WAN ordering comes from the interface state DB (Redis 13 `interface/state/*`) and is not user-controllable, so two identical HA hubs can reconnect at different speeds (enhancement CGSDW-24144). Practical effect: give the controller a cheap, Internet-capable interface early in the list and avoid setting "use for controller connection" false on the only path that works.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| FC debug procedure, revert rule, requeue semantics | UNVERIFIED (internal; `debug logging` and `debug flow` exist in the CLI reference) | DOC | Confluence 184330031, 175768166 |
| DPDK stage counters and decision tree | UNVERIFIED (internal 2026 playbook) | DOC | Confluence 700294454 |
| Core/memory handling, data-collection scripts | UNVERIFIED (internal) | DOC | Confluence 175768166, 795149129; SRC-000098/099 |
| VPN/service-link internals and rekey flap pattern | UNVERIFIED (internal) | DOC | Confluence 175768166 |
| Route manager design, Redis keys, wanpath flow | UNVERIFIED (internal, document marked in progress) | DOC | SRC-000105; Confluence 74187077 |
| MRL interface order and 20-s retry | UNVERIFIED (internal 2024 analysis) | DOC | SRC-000102 |

## Open questions

- KG-124: official description of the controller-connection interface preference ("use for controller connection", cost) and the MRL retry behaviour.
- KG-125: official guidance on when FC debug / trace logging is safe (duration, impact) for customer-run diagnostics.
