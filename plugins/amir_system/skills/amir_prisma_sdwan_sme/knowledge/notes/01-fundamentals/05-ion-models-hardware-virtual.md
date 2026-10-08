# ION models: hardware and virtual

Domain: 1 | Applies to: datasheet dated 2025-11-17 (throughput measured on ION 6.5.1 as of 2025-02-01); Admin Guide May 2025 | Status: EVIDENCE REVIEWED (datasheet pages 7–8 verified from rendered PDF images, `inventory/figures/SRC-000031/`) | Last updated: 2026-10-08

## Explanation (plain words)

ION devices are the boxes (or virtual machines) that forward traffic. Small branches use the ION 1200 family (some with built-in 4G/5G), medium branches the ION 3200 (and the ruggedized 3200H), large branches and data centers the ION 5200 and ION 9200. Virtual IONs run on hypervisors or in public clouds. Older models (1000, 2000, 3000, 7000, 9000) are still supported by the software and appear in the Administrator's Guide, but the current datasheet no longer lists them; the ION 3000 and 9000 are marked end-of-sale in a datasheet footnote.

## Current hardware (datasheet Table 1, verified from image)

| | ION 1200 | ION 1200-S | ION 3200 | ION 3200H | ION 5200 | ION 9200 | PA-5440 (listed as high-throughput DC) |
|---|---|---|---|---|---|---|---|
| Use case | small branch | small branch | small branch, DC | small branch, DC, temperature hardened (IP40) | large branch, DC | multigigabit remote-office DC and large campus | high-throughput DC |
| Controller ports | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| Ports | 4× 10/100/1000 RJ45 | 6× 1 GE RJ45, 2× 1 GE RJ45/SFP combo, 2× 1 GE bypass, 4× PoE++ | same as 1200-S | 5× 1 GE RJ45, 2× combo, 2× bypass | 4× 10 GE SFP+, 11× 1 GE RJ45, 4× MGIG (1G/2.5G), 4× 1 GE bypass, 4× 802.3bt PoE++ | 10× 10 GE SFP+, 11× 1 GE RJ45, 4× MGIG (1/2.5/5G), 8× bypass, 4× PoE++ | 8× multi-gig RJ45, 12× 1/10 GE SFP/SFP+, 4× 40/100G QSFP, 2× 10G HA, 1× 1G MGMT |
| Cellular | 4G LTE/5G variants | 4G LTE/5G variants | none | 5G variant | none | none | none |
| Bypass pairs | N/A | 1 (ports 3/4) | 1 (ports 3/4) | 1 (ports 3/4) | 2 (1–2, 3–4) | 4 (1–2, 3–4, 5–6, 7–8) | N/A |
| Encrypted throughput, 1,400-byte packets | 800 Mbps | 800 Mbps | 1 Gbps branch / 1.4 Gbps DC | 1.3 Gbps branch / 1.7 Gbps DC | 3.2 Gbps branch / 4 Gbps DC | 7.5 Gbps branch (2 VPN tunnels) / 15 Gbps DC | 54 Gbps DC |
| Threat prevention throughput (appmix) | N/A | 350 Mbps | 520 Mbps | 710 Mbps | 1.3 Gbps | 4.5 Gbps | 70 Gbps DC |
| Flows per second | 1K | 2K | 6K DC / 3.1K branch | 15K DC / 4.7K branch | 16K DC / 8.5K branch | 65K DC / 20K branch | 390K DC |
| Concurrent flows | 20K branch | 40K branch | 100K | 100K | 100K | 1M | 20M DC |
| DC VPN scale (tunnels) | N/A | N/A | 500 | 2,000 | 2,000 | 5,000 | 3,000 |
| Power | 25 W adapter (40 W cellular), fanless | 2× 150 W PSU, fanless | 2× 150 W PSU, fanless | 2× 270 W PSU, redundant DC, fanless | 1+1 450 W, 4 fixed fans | 1+1 450 W, 4 fixed fans | 2× 1200 W hot-swap, AC or DC |
| Operating temperature | 0–40 °C | 0–40 °C (C5G-WW with PoE disabled 0–60 °C) | 0–40 °C | −40–70 °C on DC power; 0–60 °C on AC | 0–40 °C | 0–40 °C | 0–55 °C |

Footnotes on the datasheet: ION 3000 (end-of-sale) DC VPN scale 500; ION 9000 (end-of-sale) 5,000. All IONs have an AUX port at 115,200 baud for out-of-band management. Throughput numbers "subject to change".

## Cellular variants (datasheet Table 2)

ION 1200-C-NA / 1200-S-C-NA (North America LTE bands, carrier-certified AT&T, PTCRB, T-Mobile, Verizon, Bell Canada for 1200-C-NA); 1200-C-ROW / 1200-S-C-ROW (rest of world, GCF); 1200-C5G-WW / 1200-S-C5G-WW (5G NR sub-6 plus LTE, worldwide; AT&T, GCF, PTCRB, T-Mobile, Verizon, Telstra); ION 3200H-C5G-WW (5G; AT&T, PTCRB, Verizon, T-Mobile, GCF; Telstra in progress). Two nano-SIM slots on the 1200 cellular models (internal deck).

## Virtual IONs (datasheet Table 3)

| | ION 3102V | ION 3104V | ION 3108V | ION 7108V | ION 7116V |
|---|---|---|---|---|---|
| Role | remote office | remote office | remote office | data center | data center |
| Platforms | ESXi, Hyper-V, KVM | same | same | ESXi, Hyper-V, KVM, Azure, AWS, Google Cloud | same |
| Throughput | up to 100 Mbps | up to 200 Mbps | up to 350 Mbps | up to 3 Gbps | up to 10 Gbps |
| vCPU / RAM / disk | 2 / 8 GB / 40 GB | 4 / 8 / 40 | 8 / 8 / 40 | 8 / 32 GB / 100 GB | 16 / 64 / 100 |

Internal best-practices guide (May 2026) gives much higher vION numbers: 3102V up to 700 Mbps, 3104V up to 1.1 Gbps, 3108V up to 1.8 Gbps (ESXi 8.0, 1,400-byte packets); 7108V 3.2 Gbps branch / 4.2 Gbps DC; 7116V 10 Gbps DC, 11 Gbps on AWS; and mentions an ION 7132V. The deck (Feb 2026) also lists OCI as a supported cloud and ION 7108v only. **CONFLICTED**: the datasheet (official, Nov 2025) and the internal guide (May 2026) disagree on vION throughput by 3–7×; the internal numbers may reflect newer software or a different test, but no official source confirms them.

## Older models (Administrator's Guide, still documented)

- Branch-only: ION 1000, 1200, 2000 (and 3000, 3200 which can be branch or DC).
- Branch or DC: ION 3000, 3200, 5200, 7000, 9000, 9200.
- Gen-1 (2000, 3000, 7000, 9000): dedicated controller port. Gen-2 (1200-S, 3200, 5200, 9200, and 1200): any L3 interface can be Used-for-Controller from 6.3.1.
- Hardware bypass defaults (admin guide p. 148): ports 4/5 on ION 2000; all LAN/WAN ports on ION 3000; 5/6 and 7/8 on ION 7000; 1/2, 3/4, 5/6, 7/8 on ION 9000.
- Internal deck table for Gen-1: ION 1000 up to 100 Mbps, 10K concurrent connections; ION 2000 up to 250 Mbps, 40K; ION 3000 up to 500 Mbps, 100K, 1 controller port, 1 bypass pair; ION 9000 up to 3 Gbps branch / 10 Gbps DC, 500K/1M, 2 controller ports, 4 bypass pairs, dual hot-swap PSUs.

## Branch gateway support (admin guide p. 60)

ION 3200, 5200, 9200, 3000, 7000, 9000 and all virtual models; software 6.4.1 or higher.

## Internal best-practices table vs datasheet (conflicts to carry)

| Item | Datasheet (SRC-000031, Nov 2025) | Internal guide (WS-001, May 2026) | Summary doc (WS-002) |
|---|---|---|---|
| ION 5200 throughput | 3.2 Gbps branch / 4 Gbps DC | 2 Gbps / 4 Gbps | 2 Gbps / 4 Gbps |
| ION 1200 throughput | 800 Mbps | 800 Mbps | 250 / 700 Mbps |
| ION 9200 throughput | 7.5 / 15 Gbps | 7.5 / 15 Gbps | 5 / 15 Gbps |
| ION 3200H temperature | −40–70 °C DC power; 0–60 °C AC | same | — |
| vION throughput | 100/200/350 Mbps; 3/10 Gbps | 700/1,100/1,800 Mbps; 3.2–4.2 / 10–11 Gbps | — |

Use the datasheet values as VERIFIED; the WS-001 values as CONFLICTED where they differ; WS-002 as OBSOLETE/UNVERIFIED.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Table 1 hardware specifications (ports, bypass pairs, throughput, flows, VPN scale, power, temperature) | VERIFIED | DOC (image-verified) | SRC-000031 p.7 (datasheet 111725; throughput measured on 6.5.1, 2025-02-01) |
| Cellular variants and bands | VERIFIED | DOC | SRC-000031 p.8 |
| Virtual model sizing and throughput | VERIFIED (datasheet) / CONFLICTED with WS-001 | DOC | SRC-000031 p.8; WS-001 §Software Form Factors |
| ION 3000 and 9000 end-of-sale | VERIFIED | DOC | SRC-000031 p.8 footnote |
| Branch-only vs DC-capable model lists | VERIFIED | DOC | SRC-000029 pp.12, 140 |
| Gen-1 vs Gen-2 controller port behavior | VERIFIED | DOC | SRC-000029 p.183 |
| Hardware bypass port pairs on 2000/3000/7000/9000 | VERIFIED | DOC | SRC-000029 p.148 |
| Branch gateway supported platforms and 6.4.1 minimum | VERIFIED | DOC | SRC-000029 p.60 |
| FIPS 140-3 baseline for all IONs; customer- and device-specific keys with high-frequency rotation | VERIFIED | DOC | SRC-000031 p.6 |
| Gen-1 throughput/connection table | UNVERIFIED (internal, undated slide, superseded models) | DOC | WS-033 slide 52 |
| OCI as a supported vION cloud; ION 7132V exists | UNVERIFIED | DOC | WS-033 slide 53; WS-001 |

## Open questions

- KG-063: official sizing for ION 7132V and current vION throughput (resolve conflict; public datasheet or hardware reference needed; D2 allows a public check in B2 follow-up).
- KG-003 remains: hardware references for 1000/2000/3000/7000 are not in the KB (00ION_data may contain quick starts; check in B2 follow-up).

## Addendum 2026-10-08 (B17/B20 findings)

- Lifecycle (note 07-operations/03, VERIFIED from official release/upgrade pages): **Gen-1 hardware (ION 1000, 2000, 3000, 7000) ends with the 6.5.x line; 6.6.1 and later run only on Gen-2 (1200-S, 3200, 3200H, 5200, 9200) and ION 9000**; ION 7000 ends at 6.3.x; 6.5 end-of-life 2028-02-15.
- Throughput, third official set (Design Guide Oct 2025, SRC-000038 pp.25–27, "recommended range"): ION 1200/1200-S up to 250 Mbps; 3200/3200H 600 Mbps DC mode / 500 Mbps branch; 5200 1.5 Gbps DC / 1 Gbps branch; 9200 6 Gbps DC / 3 Gbps branch; 3102v 700 Mbps, 3104v 1.1 Gbps, 3108v 1.8 Gbps (2/4/8 vCPU, 8 GB RAM, 40 GB disk), 7108v 3 Gbps, 7116v 10 Gbps. KG-063 now a three-way CONFLICT for the ION 5200 (datasheet 3.2 Gbps, WS-001 2 Gbps, Design Guide 1 Gbps branch / 1.5 Gbps DC) — never quote a single number without the source and mode.

## Addendum 2026-10-08 (public pages cached under D2; see 03_SOURCE_CATALOG.md §J)

- **Compatibility matrix** (PUB-007, 2026-10-05, VERIFIED) model list: ION 1000, 2000, 3000, 7000, 9000, 1200, 1200-C-NA, 1200-C-ROW, 1200-C5G-EXP, 1200-S, 1200-S-C-NA, 1200-S-C-ROW, 1200-S-C5G-WW, 3200, 3200H, 3200H-C5G-WW, 5200, 9200, 3102V, 3104V, 3108V, 7108V, 7116V, 7132V. Gen-1 and the ION 1200 family end at 6.5.x; 3200H from 6.4.2; 7116V/7132V from 6.5.1; 3100v not on Azure.
- **Hardware pages carry no throughput** (PUB-012): 3200 16 GB RAM / 128 GB eMMC; 3200H 8 GB; 5200 32 GB / 240 GB NVMe, 19 ports (11 x 1G, 4 x SFP+, 4 x MGig PoE++), 2 bypass pairs; 9200 64 GB / 480 GB NVMe, 10 x SFP+, 4 bypass pairs; 1200-S 8 GB / 128 GB eMMC, fanless, 150 W adapter derated to 50 W above 45 C.
- **vION sizing** (PUB-014, Virtual ION on KVM for NFV guide 1.0.0, 2024-09, VERIFIED): 3102v 2 vCPU / 8 GB / 40 GB / 100 Mbps; 3104v 4 / 8 / 40 / 200; 3108v 8 / 8 / 40 / 350; 7108v 8 / 32 / 100 / 500 Mbps. Matches the datasheet; the Oct 2025 Design Guide "recommended range" (700 / 1,100 / 1,800 / 3,000 Mbps) is the outlier. Quote both with their source (KG-063).
