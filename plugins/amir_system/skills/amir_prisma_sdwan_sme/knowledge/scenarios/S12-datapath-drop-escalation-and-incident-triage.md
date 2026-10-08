# S12 — Datapath drop escalation: what to collect, how incidents map

Domains: 7, 8, 9 (datapath) | Evidence type: SCENARIO | Written 2026-10-08

## 1. Situation

Branch ION 2000 (6.3.6) intermittently drops a subset of flows to the DC for 30–60 s several times a day; incidents show `DEVICESW_GENERAL_PROCESSRESTART` and occasional `NETWORK_SECUREFABRICLINK_DEGRADED`; the customer runs a vulnerability scanner nightly. Support asked for "datapath evidence".

## 2. Question

Triage with the incident model, decide whether the ION drops, and assemble the escalation package.

## 3. Reasoning chain

1. **Incident reading.** `DEVICESW_GENERAL_PROCESSRESTART` = a process (likely the flow controller) restarted; `NETWORK_SECUREFABRICLINK_DEGRADED` (Informational) = some VPN links of a secure fabric link down, correlated from individual VPN codes; check Correlation IDs and whether `APPLICATION_PERFORMANCE_DEGRADED` or `CIRCUIT_PERFORMANCE_DEGRADED` co-occur. Device standing incidents re-sync every 24 h. [VERIFIED — 07-operations/01 (WS-041 pp.5–10, 25–28)]
2. **Isolation order.** System → site → device → path → VPN → routing → application; and device→controller connectivity → circuits → fabric → routing. Rule out WAN/underlay (LQM, interface errors, keep-alive drops) before blaming the datapath. [UNVERIFIED (internal TSE method) — 08-troubleshooting/01; incident semantics VERIFIED]
3. **Why an ION 2000 on 6.3.6 matters.** 6.x datapath is DPDK user-space with per-core flow controllers; a few heavy flows pinned to one core, probe-table floods (undeclared scanners) or trace logging can starve a core → FC crash/restart → flows dropped and VPN keep-alives missed (link degraded). 6.3.6 shrank queues and protects control packets (VPN keep-alives, LQM) when the Rx FIFO is half full, which is why links show degraded rather than down. Small platforms are also the OOM/80 %-memory risk group. [UNVERIFIED (internal PAEE) — 09-datapath/01; 80 % memory advisory VERIFIED — 07-operations/03]
4. **Scanner hypothesis.** Undeclared network scanning floods probe entries and can crash the app engine and FC; the official remedy is to define scanners as **Network Scan App** (disable unreachability detection, affinity None). Check the probe table size and OOM logs. [VERIFIED for the Network Scan App recommendation — 03-application-traffic/01 (SRC-000029 pp.464, 467); UNVERIFIED (internal) for the probe-table/FC-crash mechanism — 08-troubleshooting/04]
5. **Prove or disprove the ION drop.** Capture at ingress and egress ports (`tcpdump <port> args=… show`), check `inspect flow brief|detail` (right PATH, SEC-ACTION allow); if the flow entry is correct, read stage counters: `dump dpdk port stats` (ierrors/imissed/inombuf/oerrors), `dump dpdk stats`, 6.3.6 counters `fpn.rx_cp_passthrough|rx_cp_kept|rx_cp_overrun|rx_dp_drop`; punt/inject accounting on the fpvi ports (support shell). [UNVERIFIED (internal playbook 700294454) — 09-datapath/02]
6. **Collect for escalation.** `dump-support all file=<name>` after the event (cores under `/log/cgnx_infra/core_dir/`), syslog around the restarts, alarms/incidents with timestamps, `dump dpdk port stats` before/after, flow samples, policy and app-map state (`inspect app-map summary`), memory snapshot (`top`, `free -m`, `fpcmd dpdk-debug-memory | grep Zone`), probe-table count, scanner schedule; FC debug (`debug flow create …`, `debug logging facility=flow-ctrl … level=trace`) only for a bounded window and **revert to info**. Engineering scripts (`cont_dpdk_record.sh`, `ts_and_port_data.sh`, `cdump.sh`) only when TAC provides them. [UNVERIFIED (internal) — 09-datapath/02, 08-troubleshooting/02; `dump-support` syntax from the CLI reference VERIFIED]
7. **Operational hygiene.** Incident policy: dampening or suppression for the scan window is wrong here (hides the symptom); instead fix the scanner definition and consider a memory-driven platform refresh (Gen-1 ends at 6.5.x). [VERIFIED for policy mechanics and lifecycle — 07-operations/01, 07-operations/03]

## 4. Answer

The pattern (process restarts, links degraded not down, nightly scanner, small Gen-1 platform) points to flow-controller restarts under probe/flow pressure rather than a WAN fault. Declare the scanner as a Network Scan App, verify memory and probe-table growth, and build the escalation package: support dump with cores, incident timeline with correlation IDs, DPDK port/stage counters around an event, flow samples and policy state, plus a short bounded FC trace reverted to info. Say plainly that stage-counter and FC-trace analysis is TAC/engineering territory.

## 5. What to check / collect next

As listed in step 6; plus `dump vpn summary`, `dump vpn ka summary`, LQM for the degraded link, interface error counters. [sources above]

## 6. Gaps exposed

KG-123 (official datapath statements), KG-125 (safety of debug/trace logging), KG-121 (app-map/QUIC), KG-090 (ZBFW/platform limits). New: **KG-141** — official description of `DEVICESW_GENERAL_PROCESSRESTART` sub-reasons and which process names appear in the incident text.

## 7. Validation status

**SCENARIO PARTIAL** — incident semantics and the scanner remedy are VERIFIED; the datapath mechanism and evidence commands are internal-only.
