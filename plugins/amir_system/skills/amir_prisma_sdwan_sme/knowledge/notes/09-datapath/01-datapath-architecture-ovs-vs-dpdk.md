# ION datapath architecture: 5.6.x Open vSwitch kernel path vs 6.x DPDK user-space path, Gen-1 vs Gen-2 platforms, 6.3.6 queue changes

Domain: 9 (internals) | Applies to: PAEE "Life of Packet – Datapath on Prisma SDWAN ION" SRC-000100 (page 645857374, retrieved 2026-10-04), "Packet flow in dpdk release" SRC-000103, TSE playbook ION FC/DPDK Stats – Life of Packet 700294454 (2026-01) | Status: INTERNAL ONLY (engineering documents); no official equivalent | Last updated: 2026-10-08

## Explanation (plain words)

Up to release 5.6.x the ION forwarded packets inside the Linux kernel with **Open vSwitch**: a hash lookup in a shared flow table forwarded known flows, and the first packet of a new flow went to the **flow controller** (`fc`, process `fp_appgw`) for policy and to the **app-engine** for application identification. From 6.x the datapath runs in **user space on DPDK** with dedicated cores: the NIC is owned by DPDK, **6WIND (`6wnd`, process `fp-rte`)** does receive-side scaling, first-stage processing and IPsec, hands packets through an **intercore queue** to the destination core where the flow controller (`libfc`) creates the flow, detects the application and applies path, QoS and security policy, then back to 6WIND for encryption and transmit. Control and "for-us" packets are **punted** to the kernel over `fpvi` ports. Why it matters: a few heavy flows pinned to one core, debug logging left at trace level, or probe-table floods can starve a DPDK core and crash or reboot the device while average CPU looks fine.

## 5.6.x (OVS) characteristics (SRC-000100)

Kernel-context forwarding; QoS, ARP, VLAN and IPsec as kernel modules; IPsec decryption off-pipeline in software crypto; no clear control-plane/data-plane separation; soft-IRQ round-robin core distribution with one shared, locked flow table; ION 2000 used all four cores for everything; kernel "natural throttling" and tap-interface mirroring drops protect `fc` and the app-engine but drop data and control packets aggressively when the FIFO fills; lower throughput and connections per second.

## 6.x (DPDK) characteristics (SRC-000100; playbook 700294454)

- Cores: on ION 2000, 2 cores for DPDK, 2 for kernel and user-space processes; each DPDK thread carries its own 6WIND drivers and `libfc`.
- Pipeline: (1) ingress + **RSS** hash to Rx queues (same tuple → same core); (2) first-stage 6WIND processing on the Rx core (for-us vs transit, IPsec decryption with hardware acceleration where available, software on vIONs); (3) **intercore queue**, processed in **bulks of 32 packets**; (4) destination core: `flow-ctrl` flow creation, app detection, path/security/QoS policy; egress via 6WIND, encryption for fabric or standard VPN, Tx queue.
- **Punt path**: TCP SYN, new UDP flows needing a flow record, L3 lookups and control packets go to the kernel through an `fpN`/`fpvi` port; this can cause head-of-line blocking within a bulk. Inject packets (locally generated) take the reverse path.
- Kernel still owns ARP, route tables, NAT, IPsec SAs, conntrack and interface state; 6WIND control-plane components subscribe to **netlink** events (IP changes, routes, SAs, conntrack, interface state/creation) to keep the fast path synchronised. Interfaces appear as `v-eXX-p`/`v-eXX` tap pairs and as `fpvi` pseudo-interfaces (what `ifconfig` shows in the shell).
- Queues before 6.3.6: Rx up to 4K packets, intercore 8K (256 bulks) → about 12K packets buffered, adding latency. **6.3.6 changes**: Rx queue 1,024 packets (50 % of available buffers; 2K on ION 9000 with 4K buffers), intercore **16 bulks = 512 packets**; **control-packet protection**: when the Rx FIFO is 50 % full, data packets drop while control packets (ARP, ESMC, VRRP, ICMP, OSPF, NETFPC, TCP/UDP control, **VPN keep-alives, LQM**) are still queued until the FIFO is full, via ingress classification and DSCP marking; new counters `fpn.rx_cp_passthrough`, `fpn.rx_cp_kept`, `fpn.rx_cp_overrun`, `fpn.rx_dp_drop`.
- Trade-offs vs 5.6.x: about 20 % more throughput with well-distributed flows, better minimum latency, but worse average/maximum latency under new-flow bursts and sensitivity to a few high-volume flows (e.g. one VPN pinned to one core → backpressure, intercore drops, FC crash or reboot).
- Fragmentation (SRC-000103): LAN→fabric-VPN packets are ESP-encapsulated by 6WIND first (internal packet up to 65,535 bytes) and **fragmented after encryption** when the ESP packet exceeds the 1,500-byte IP MTU; only the first fragment carries the ESP/SPI header, so Wireshark decrypts only that fragment and shows the rest as IP fragments (match by IP ID/offset).

## Platforms (SRC-000100)

Gen-1: ION 1000, 2000, 3000, 7000, 9000 (NIC directly on the PF). Gen-2: ION 1200-S, 3200, 3200H, 5200, 9200: front-panel ports sit behind a switch (Marvell on 1200-S) connected to a backplane using **SR-IOV PF/VF**; a few WAN ports (e.g. 1200-S ports 1–2) go straight to the NIC PF; LAN0 VFs carry L3 sub-interface traffic, LAN1 VFs carry L2 VLAN traffic for SVIs (**one VF per VLAN, maximum 32 VLANs in SVI mode**); switch control packets (ARP, BPDU, STP) go to the PF; traffic is segregated with EDSA VLAN tags decoded by a DPDK EDSA plugin. 6.6.1+ software runs only on Gen-2 and ION 9000 (note 07-ops/03).

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| All architecture statements, queue sizes, 6.3.6 changes, platform mapping | UNVERIFIED (internal PAEE engineering documents; consistent with the 6.3.6 "datapath memory-management enhancement" release-note entry, WS-021 FEATURE-017) | DOC | SRC-000100; Confluence 700294454 |
| ESP-then-fragment behaviour | UNVERIFIED (internal) | DOC | SRC-000103 |
| 32 VLAN SVI limit on Gen-2 | UNVERIFIED (internal); cross-check with the official switching chapter (KG-072) | DOC | SRC-000100 |

## Open questions

- KG-123: any official statement on DPDK core allocation, queue sizes or the 32-VLAN SVI limit (switching chapter pp.163–180 pending, KG-072).
