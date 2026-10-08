# S09 — Branch HA pair never fails over

Domains: 2, 8 | Evidence type: SCENARIO | Written 2026-10-08

## 1. Situation

Two ION 1200-S in an HA group at a dual-Internet branch, release 6.5.2. During a test the active device is powered off; the site goes down and the second device stays "Backup" (in another test it shows "Init"). HA control interfaces are connected with a direct Ethernet cable between the two devices.

## 2. Question

Why does the backup not take over, and what else must be checked?

## 3. Reasoning chain

1. The HA control interface must be reachable through an external switch (or two switches with a common VLAN). **A direct cable is explicitly forbidden**: when the active device is powered off, the backup's control link goes down, and the backup never transitions to active. [VERIFIED — 10-design/01 (SRC-000038 p.38); 02-network/07 (SRC-000029 pp.611–613: embedded-switch platforms allow back-to-back only when no southbound switch exists, with a documented split-brain caveat)]
2. On 1200-S the recommended HA control interface is an SVI ("virtual-controller", Use this port for HA, static /30, each gateway = peer IP) carried on a trunk port to the LAN switch together with the LAN VLAN; **SVI Auto Operational State** (6.4.1+) puts the device in backup if all member ports are down — so a trunk port that is down also blocks activation. [VERIFIED — 10-design/02 (SRC-000037 pp.102–105), 02-network/07 (SRC-000029 pp.622–624)]
3. "Init" means the devices never completed negotiation: the site must be in **Control mode** before HA devices become active, both control interfaces must share one IPv4 subnet with unique static IPs, and the HA group must exist with both devices assigned (priority, control interface). [VERIFIED — SRC-000037 p.99; SRC-000038 p.38]
4. Election rules: priority 1–254 with a recommended gap of ≥40; **preempt** off means no re-election unless the active fails catastrophically (priority 0: power loss, critical process, control link loss, tracking to 0). Power-off is catastrophic, so preempt is not the reason here. Detection = advertisement interval × 3 missed (1 s → 3 s). [VERIFIED — 02-network/07 (SRC-000029 pp.604, 620, 629–630)]
5. Interface tracking: control-interface failure ⇒ immediate failed state; up to four tracked interfaces with priority decrements; WAN L3 tracking is not supported with bypass pairs. A tracking misconfiguration cannot prevent takeover after power loss but can cause unwanted switchovers. [VERIFIED — SRC-000029 p.630]
6. Hardware bypass behaviour: on the backup the bypass WAN port is bridged to its LAN port so both circuits reach the active device; after takeover both circuits must terminate on the new active device — requires the cross-connect cabling (port 3 WAN input, port 4 pass-through to the partner's port 1). Wrong cabling makes a "successful" failover look like an outage. [VERIFIED — 10-design/01 (SRC-000038 pp.38–40), 10-design/02 (SRC-000037 pp.113–114)]
7. Verification: SCM lags minutes; use the toolkit `dump spoke-ha status` (deployment guide spelling) / `dump spoke ha status` (admin guide spelling) for live state and last switchover reason. [VERIFIED — SRC-000037 p.114; SRC-000029 p.605; spelling CONFLICT recorded]

## 4. Answer

The direct cable is the fault: with the active powered off, the backup sees its HA control link down and therefore cannot become active. Move the HA control interfaces to the LAN switch (trunk carrying the HA VLAN and the LAN VLAN; MSTP/RSTP, not PVST), confirm the site is in Control mode, both devices are in the HA group with distinct priorities (e.g. 50/45) and a 1,000 ms advertisement interval, then re-test and watch `dump spoke-ha status`. Check the bypass cross-connect so both WAN circuits land on the surviving device.

## 5. What to check / collect next

HA group config and status (`dump spoke ha config|status`), SVI membership and trunk state, site mode, LAN switch STP mode, cabling against Table 28 of the deployment guide; device-level settings (zone bindings, NAT) replicated on both devices. [VERIFIED — 02-network/07, 10-design/02]

## 6. Gaps exposed

KG-011 (process-crash decrements, "<4 s" claim). New: **KG-137** — the official CLI spelling `dump spoke ha status` vs `dump spoke-ha status` (admin guide vs deployment guide); confirm on a device or in the CLI reference.

## 7. Validation status

**SCENARIO VALIDATED** — every step rests on VERIFIED claims; only the CLI spelling is CONFLICTED.
