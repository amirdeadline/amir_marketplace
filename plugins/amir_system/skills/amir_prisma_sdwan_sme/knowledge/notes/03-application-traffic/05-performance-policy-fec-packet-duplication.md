# Performance policy: SLAs, Move Flows, FEC, packet duplication, incidents, system health

Domain: 3 | Applies to: Performance Policy from ION 6.3.1 (6.3.2 recommended); packet duplication, service health probes, system metrics, UDP-TRT and MOS SLAs from 6.4.1 | Status: DOCUMENTED (official chapter read in full) | Last updated: 2026-10-08

## Explanation (plain words)

Path policy says which paths are *allowed*; **performance policy** says what "good enough" means and what to do when a path is not good enough. A rule matches applications (or transfer types), paths and DC groups, carries an **SLA** (thresholds on link quality, real-traffic application metrics, or synthetic probes), and takes **actions**: raise an incident, show the threshold on graphs (visibility), **move flows** off the bad path, add **forward error correction** (repair packets) or **packet duplication** (send copies on up to three fabric VPNs), or send traffic to **App Acceleration**. A second rule type watches device health (CPU, memory, disk, flows, circuit utilization) and raises incidents.

## Defaults (official pp. 505–512)

- A default performance stack is bound to every site; default set, default rules and default threshold profile cannot be removed; thresholds and actions of default rules can be edited. Three rules after upgrade to 6.3.1+: **Visibility** (media SLA latency 150 ms, loss 2%, jitter 75 ms; draws threshold lines on the Secure Fabric link quality graph), **All Media Apps** (Move Flows; audio and video transfer types; same SLA), **All Apps** (Move Flows; transactional and bulk; latency 500 ms, loss 5%, jitter 100 ms). The chapter intro states the media jitter default as 40 ms while the rule listing says 75 ms (**internal inconsistency in the guide**; the detailed rule text says 75 and WS-001 agrees).
- Function-to-version matrix: Move Flows / Visibility / Incident and FEC from 6.3.1; Packet Duplication, Service Health Probes, system-metric incidents, UDP-TRT and MOS SLAs from 6.4.1. A rule containing a function unsupported by the device's version is **ignored in its entirety** by that device.
- Action compatibility: FEC and packet duplication **require Move Flows** and are **mutually exclusive**; visibility uses only link quality metrics; FEC uses only loss and latency link quality metrics; FEC and duplication only on Prisma SD-WAN VPNs.
- Default service health probes (6.4.1+): CloudFlare DNS ICMP (1.1.1.1), MS Teams ICMP (teams.microsoft.com), Google G-Suite ICMP (apps.google.com); 10-second cycle, probe count 2, paths Direct / Prisma SD-WAN VPN / Standard VPN; attached to default probe profiles bound to non-metered circuit categories; **disabled for tenants existing at the April 2024 controller upgrade**, enabled for newer tenants.

## Rules (official pp. 513–526)

- Stacks (simple/advanced, ≤4 sets + default set, left-most highest), sets (defaults immutable), rules with explicit order (default order lands just above the default rules; "an empty match field = match any").
- **App/Network SLA** rule: actions Create Incident, Move Flows (Graceful / Forced), FEC, Packet Duplication, Visibility, App Acceleration; match: ≤256 apps, transfer type, path category (overlay + circuit category, no repeats), path type (Direct / Prisma SD-WAN VPN / Standard VPN), DC group (blank = all groups plus branch-to-branch VPNs; naming any group excludes branch-to-branch VPNs); Performance SLA (existing or new); advanced: **Raise Above 10–100%** and **Clear Below 1–80%** of LQM samples across the circuit's paths; **monitoring approach** Conservative / Moderate (default) / Aggressive (time-based weighting of recent vs historical samples; affects incident generation).
- **System Health** rule: Create Incident on CPU, memory, disk (1–100%), concurrent flow utilization (1–100%), circuit utilization (1–100%, per circuit or all).
- **Move Flows Graceful**: excludes violating paths for new flows; with application-metric SLAs only new flows are redirected and existing flows stay up to 10 minutes; with LQM SLAs both new and existing flows move; keeps application path affinity; detects within one minute (probes sharpen it). Empty Move Flows ⇒ link quality metrics are ignored for that rule.
- **Move Flows Forced**: moves existing flows even across a NAT boundary (best available path if nothing better); triggers: L3 unreachability, LQM SLA violation, app unreachable, synthetic probe SLA violation, service link up/down, flow revalidation, DC core reachability with host tracking; supported on Private L2, Direct, SD-WAN VPNs, standard VPNs; Flow Decision Data shows forced moves.
- **FEC**: effective for 1–10% loss; repair increases with loss; branch ION measures both directions and sends an in-band instruction so the DC ION applies FEC for inbound loss. Deck: parity ratio 10% for 0–5% loss, 20% for 5–10%, none above 10%.
- **Packet Duplication** (6.4.1+): replicates a session on up to **three** VPN paths; requires explicit selection of the primary and the duplicate paths; needs Move Flows.
- **Always ON vs Adaptive** (p. 545): Always ON regardless of link state for mission-critical apps; Adaptive engages when a fabric VPN exceeds the SLA loss threshold (WS-001 recommends Adaptive).
- Platform limits (p. 545–546): VPNs actively encoding FEC/duplication: ION 1000/1200/1200-S/2000 = 8 (branch); 3000/3200 = 16 branch / 32 DC; 5200/7000 = 32 / 128; 9000/9200 = 64 / 256; FEC and duplication on the same VPN count once. Rule limits (count / rules×apps): 1000 = 30/150; 1200 = 50/250; 1200-S = 200/1275; 2000 = 50/1275; 3000, 3200, 5200, 9000, 9200 = 255/1275.
- Prerequisite: **Use LQM on non-hub paths** on each circuit category in use (circuit overrides allowed).

## SLA metric catalog (pp. 536–538; WS-001)

Link Quality: latency 1–500 ms, jitter 1–100 ms, MOS 1–5, loss 1–20% (uses the best value between the branch and all DCs per branch circuit). Application: init failure rate 1–100% (TCP handshake failures), RTT 1–500 ms, UDP-TRT 1–500 ms (DNS only). Probe: DNS transaction time/failure rate, HTTP transaction time/init failure, ICMP latency/jitter/loss. System health, circuit utilization, flow metrics (1–100%).

## Line conditioning with Prisma Access

FEC and packet duplication between Prisma SD-WAN and Prisma Access require **Prisma Access Remote Networks – High Performance** (p. 505).

## Use cases (pp. 550–560, official)

1. SaaS app on dual direct Internet with metered 5G L3 failure: Raise Alarms + Move Flows; LQM jitter 50 ms, latency 100 ms, loss 3%; app init failure 10%, RTT 100 ms; aggressive monitoring; incidents `APPLICATION_PERFORMANCE_DEGRADED` (child) and `CIRCUIT_PERFORMANCE_DEGRADED` (parent, suppresses the child by default; changeable in Incident Settings).
2. Enterprise point-of-sale over fabric VPN on primary Internet with metered 5G L3 failure: FEC + Move Flows; jitter 50, latency 150, loss 1%; adaptive FEC takes ~5% transport loss to 0% for the sessions.
3. Physical security over LEO satellite and unmetered 5G (both active) with ADSL L3 failure: Packet Duplication + Move Flows + Create Incident; jitter 50, latency 200, loss 1%; dual-link duplication when both degrade, single-link when one is down.
4. Contact-center voice over Internet and MPLS fabric VPNs with metered 5G last resort: Packet Duplication + Move Flows; MOS 3.6, loss 1%.

## Internal guidance (WS-001 §Performance Policy)

Use simple stacks; specific rules first; migrate pre-6.3.1 Advanced-menu LQM/APT thresholds (ignored from 6.3.1); pair LQM SLAs with Move Flows; Graceful for most, Forced for real-time apps; enable LQM on non-hub paths before Internet-circuit SLAs; prefer Adaptive FEC/duplication and respect VPN encoding limits; check rule-count limits per platform; probes for backup-path health and third-party endpoints. Deck: "Forced Flow Move" was roadmap FY25 Q1 (now documented); "Best Path Selection" labelled 6.4.2 on one slide and 6.5.1 on another (CONFLICTED internally; official path policy page documents both selection modes without a release floor).

## CLI names (official)

`debug performance policy`, `inspect performance policy fec status|hits analytics|incidents|lookup`, `dump performance policy config policy rules|policy sets|policy set stacks|threshold profile`; app acceleration: `dump app accel keys|status`, `dump flow`, `inspect flow details`.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Performance policy from 6.3.1; function/version matrix; whole-rule ignore on unsupported function | VERIFIED | DOC | SRC-000029 pp.505–506 |
| Three default rules and thresholds (150/2/75; 500/5/100) | VERIFIED (jitter 40 vs 75 inconsistency noted) | DOC | SRC-000029 pp.505, 510–511; WS-001 |
| Default service health probes and enablement rule by tenant age | VERIFIED | DOC | SRC-000029 pp.511–512 |
| Action dependencies (FEC/PD need Move Flows, mutually exclusive, VPN-only) | VERIFIED | DOC | SRC-000029 pp.506, 518 |
| Graceful vs Forced semantics, triggers, 10-minute existing-flow grace, 1-minute detection | VERIFIED | DOC | SRC-000029 pp.523–526 |
| FEC 1–10% range; in-band DC instruction; PD up to 3 paths; Always ON vs Adaptive | VERIFIED | DOC | SRC-000029 pp.518, 545–546 |
| Platform VPN encoding limits and rule limits | VERIFIED | DOC | SRC-000029 pp.545–547 |
| SLA metric ranges | VERIFIED | DOC | SRC-000029 pp.537–538 |
| Prisma Access RN-HP required for FEC/PD toward Prisma Access | VERIFIED | DOC | SRC-000029 p.505 |
| Incident codes and parent/child suppression | VERIFIED | DOC | SRC-000029 pp.553–554 |
| FEC parity ratios 10%/20% | UNVERIFIED (deck) | DOC | WS-033 slide 195 |
| Best Path Selection release floor (6.4.2 vs 6.5.1) | CONFLICTED (deck slides 168 vs 192); official text gives none | DOC | WS-033 |

## Open questions

- KG-087: release that introduced Best Path Selection and Move Flows Forced (public release notes 6.4.x/6.5.x under D2).
- KG-088: media jitter default 40 ms vs 75 ms (guide inconsistency); confirm on a tenant or newer guide.

## Addendum 2026-10-08 (B17/B18 findings)

- Release chronology (note 07-operations/04): **Best Path selection confirmed in 6.4.2**; **Move Flows (forced)** introduced in 6.5.1. KG-087 PARTIAL (the 6.4.2 floor is corroborated by the release considerations; the admin-guide wording differs).
- Design Guide Oct 2025 (SRC-000038 p.46, VERIFIED): built-in SLAs "All Apps" 500 ms latency / 5 % loss / 100 ms jitter and "Media Apps" 150 ms / 2 % / 40 ms; graceful move honours link affinity, forced move ignores it; packet duplication across up to three VPN paths.
