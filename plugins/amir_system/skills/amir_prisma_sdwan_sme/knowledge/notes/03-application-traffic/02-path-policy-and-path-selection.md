# Path policy, stacked policies, and dynamic path selection

Domain: 3 | Applies to: Admin Guide May 2025; stacked policies mandatory from 6.0.1; SLA-compliant / best-path options; IPv6 default rule from 6.2.1 | Status: EVIDENCE REVIEWED | Last updated: 2026-10-08

## Explanation (plain words)

A **path policy** says, per application (and optionally per LAN segment, prefix, user), which WAN paths may carry the flow: **active** paths are used first and load-shared, **backup** paths are used when no active path is healthy, and **L3 failure** paths are used only when everything else is truly down. A path is a combination of an **overlay type** (direct on the circuit, the Prisma SD-WAN fabric VPN, or a standard VPN) and a **circuit category**. Rules live in **policy sets**, sets in a **stack**, and one stack per policy type is bound to each site. When a flow starts, or when a path fails or degrades, the ION picks a path by checking policy, link status, link quality, application reachability and performance, affinity, and finally the available bandwidth.

## Stacked policies (official pp. 439–447, 462)

- From **6.0.1 only stacked policies** are supported; devices with original (legacy) policies cannot be upgraded to 6.0.1+ until migrated (clone original sets into stacked Path and QoS sets; a Default Rule policy set is created with default-deny, intra-zone-allow, self-zone-allow for security).
- Stack = up to **four policy sets plus one default-rule set**, evaluated left to right; one Path stack and one QoS stack per site; Path and QoS stacks always contain **Default Rule** and **Enterprise Default Rule**; simple stacks hold one set. Bindings: `Manage > Policies > Bindings` (Path, Performance, QoS, Security stacks per site; bulk assignment).
- Rule ordering: explicit **order 1–65535 (default 1024)**, ties resolved by implicit specificity (more specific attributes win).
- QoS precedence among attributes: network context > source prefix > application > destination prefix (p. 444). Rules may match up to **256 applications**.

## Path policy rule (official pp. 448–452)

- Match: network context, source/destination prefixes (path prefixes), users/groups (User-ID; TSG tenants), applications (≤256), order, disable flag.
- **Paths tab**: Active / Backup / L3 Failure lists; each entry = overlay (Direct, Prisma SD-WAN VPN, Standard VPN; underlay) + circuit category; a combination cannot repeat within a rule; at least one active path; backup optional; L3 failure can exist without backup. From **5.2.1** flows move back to the active path as soon as it is available again (default).
- Two selection modes:
  - **SLA Compliant Path**: active paths used first and load-shared while SLA-compliant; if none, backup paths; if all active and backup are completely down, L3 failure paths. Metrics usable together: link quality (latency, loss, jitter, MOS), probes (ICMP latency/loss/jitter, DNS transaction time/failure rate, HTTP/S transaction time/failure rate), app metrics (TCP init failure and RTT, UDP TRT).
  - **Best Path Policy**: picks the path with the absolute lowest single metric (LQM latency/loss/jitter, or a probe metric), active paths first, L3 failure only if all active are down; **one metric per rule; no load sharing**; bandwidth disregarded.
- **Service & DC Groups** tab: active/backup groups; **Required** forces transit through the group and cannot be combined with any direct path in the rule.
- **L3 failure path conditions** (p. 455–456): used when all active/backup paths are up but L3-unreachable and an L3 failure path is reachable; when all active/backup are down or have no route; or on network asymmetry.
- **IPv6 default rule** (6.2.1+): global IPv6 prefix in a rule; in 6.2.1 only Direct on Any Private or Prisma SD-WAN VPN on Any Public/Private as active paths.
- **Minimize metered LTE** (pp. 456–459): on the LTE circuit clear BW and LQ monitoring, BFD non-aggressive (≤5.3.x) or keep-alive 600,000 ms (5.4.1+), cost 129, Controller Connections No, App Reachability Probes No; on the Metered 3G/4G/LTE category clear controller and probe use and set keep-alive 600,000 ms (only when the category is used strictly as an L3 failure path); put the category under **L3 Failure Paths** (5.2.1+; older releases used Backup with VPN overlay).

## Path selection inputs (official p. 467–468; deck 152–153; WS-001)

New selection happens when a flow is created, a path flaps, link quality or application thresholds are exceeded, an application becomes unreachable on a path, or asymmetry is detected (return path differs). Evaluation (deck): network and security policy → link status → DC transit → path preference → per-app link thresholds (latency, loss, jitter) → L3 reachability on direct and VPN paths → application reachability (TCP init and transaction failures) → application performance (RTT, network transit time, failure percentages, media MOS) → path affinity → performance policy → **path with the most available bandwidth**. WS-001 condenses it to four steps (policy candidates → link quality → app performance → most available bandwidth). Deck slide 158: LQM default thresholds RTT 150 ms, jitter 50 ms, loss 3%; by default only real-time media applications use link quality for path selection (others can be enabled) — to be confirmed against the performance policy defaults in B10.

## Behavioral notes (internal, strong)

- **Active/Backup is not legacy active/standby**: flows move to backup while the active is still up when the app is unreachable, LQM thresholds are breached, or BFD/L3 reachability fails; for strict last-resort behavior use **L3 Failure** instead of Backup (especially for metered LTE).
- With several Internet circuits, prefer "Any Public" active paths so the **Best Available Bandwidth** algorithm (flow-level, symmetry-preserving) spreads flows; active/backup wastes the backup during congestion because the ION does not shift traffic for utilization alone.
- Use the two built-in rules (default = Internet-bound, enterprise default = RFC 1918); do not duplicate them; never put metered cellular into them. Baseline model: generic Internet (DIA or inspection via DC/Prisma Access; exclude LTE), enterprise traffic (any overlay; LTE last resort), voice (private underlay/overlay, Internet overlay on degradation, LTE last resort), SaaS (DIA primary, MPLS overlay backup), video conferencing (DIA primary, MPLS backup, no LTE).
- If no rule matches, the default rules apply; if their paths are all down and no backup exists the flow is dropped but **tracked and re-evaluated** when a path returns (not silently black-holed).
- **Control apps**: add a rule above the defaults for `paloalto-prisma-sdwan-base` (plus `pan-db-cloud` and `paloalto-dns-security` when branch security is used) allowing all paths; exclude paths with SSL-decrypting appliances or add controller FQDNs/IPs to their decryption exclusions.
- **Network context** rules always beat rules without context; a LAN network belongs to one context only.
- **Path affinity**: see note 01 (official Strict/None; internal three modes). Avoid Required Strict broadly.

## Historical path-selection internals (Confluence 78890282, 2019; OBSOLETE in detail, useful for concepts)

Distinguishes **soft failures** (L3 unreachability, app unreachability, LQM, BFD on private WAN) from **hard failures** (prefix reachability, link down, port down); tables of which path-type pairs switch on which failure in 5.1.3+ and the path re-evaluation matrix in 5.2.1+. Historical bug IDs listed. Treat as OBSOLETE except for the vocabulary.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Stacked-only from 6.0.1; upgrade blocked with original policies; migration by cloning | VERIFIED | DOC | SRC-000029 pp.439–441 |
| Stack limits (4 sets + default), one stack per site per type, default and enterprise default rules | VERIFIED | DOC | SRC-000029 pp.442–443, 462 |
| Rule order 1–65535 default 1024; implicit specificity; 256 apps per rule | VERIFIED | DOC | SRC-000029 pp.445, 449 |
| QoS attribute precedence (context > source prefix > app > destination prefix) | VERIFIED | DOC | SRC-000029 p.444 |
| Active/Backup/L3 failure semantics; SLA-compliant vs best-path modes; metrics; no load sharing in best path; 5.2.1 fail-back default | VERIFIED | DOC | SRC-000029 pp.449–452 |
| Required DC group incompatible with direct paths | VERIFIED | DOC | SRC-000029 p.452 |
| L3 failure path conditions | VERIFIED | DOC | SRC-000029 pp.455–456 |
| Minimize metered LTE recipe (cost 129, 600,000 ms keep-alive, exclusions) | VERIFIED | DOC | SRC-000029 pp.456–459 |
| IPv6 default rule 6.2.1 restrictions | VERIFIED | DOC | SRC-000029 pp.459–460 |
| Path selection triggers and evaluation order | CORROBORATED (official unreachability text + deck + WS-001) | DOC | SRC-000029 p.467; WS-033 slides 152–153; WS-001 §Path Policy |
| LQM defaults 150 ms / 50 ms / 3%; media-only by default | UNVERIFIED (deck) pending B10 | DOC | WS-033 slide 158 |
| Backup used on degradation; L3 failure for strict last resort; best available bandwidth; control-app rule; drop-and-track | UNVERIFIED (internal, strong) | DOC | WS-001 §Path Policy, §Control Apps |
| Soft/hard failure vocabulary | OBSOLETE (2019 internal notes) | DOC | SRC-000091 pageId 78890282 |

## Open questions

- KG-085: official statement of "drop but track and re-evaluate" and of the Best Available Bandwidth algorithm name.
- KG-086: official text on which failures move existing flows vs only new flows (soft vs hard) in current releases.
