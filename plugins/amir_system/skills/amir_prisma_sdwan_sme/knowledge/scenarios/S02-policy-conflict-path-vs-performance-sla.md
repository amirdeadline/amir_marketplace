# S02 — Policy conflict: path policy prefers Internet for SaaS while the performance SLA fails on Internet

Domains: 3 | Evidence type: SCENARIO | Written 2026-10-08

## 1. Situation

Branch with MPLS and Internet (ION 6.5.x). Path rule for Microsoft 365: active = Direct on Any Public; backup = Prisma SD-WAN VPN on Any Private (to the DC, which has Internet egress). A performance policy rule for the same application has an SLA (latency 150 ms, loss 2 %) and action **Move Flows (graceful)**. The Internet circuit shows 4 % loss for ten minutes; MPLS is clean.

## 2. Question

Which policy wins, what happens to existing and new flows, and what will the operator see?

## 3. Reasoning chain

1. Path policy defines the **candidate set**: active paths first and load-shared while SLA-compliant; backup only when no active path can be used; L3 failure only when all active and backup lost L3 reachability. [VERIFIED — 03-application-traffic/02 (SRC-000029 pp.449–452), 10-design/01 (SRC-000038 p.43)]
2. Performance policy acts **inside** that set: when an active path is out of SLA, the ION moves the application to another in-policy active path; if none remains, to an in-policy backup path. Graceful move honours link affinity, link quality and probe metrics; forced move also reacts to WAN interface changes and ignores affinity. [VERIFIED — 10-design/01 (SRC-000038 p.46), 03-application-traffic/05]
3. Here the only active path (Direct Internet) is out of SLA and the backup (VPN over MPLS) is in policy → existing flows move to the MPLS VPN and new flows avoid the violating path. This is the documented difference from legacy active/standby: backup is used while the active is still up. [VERIFIED — SRC-000038 pp.43, 46; UNVERIFIED (internal, strong) for the phrasing "not legacy active/backup" — WS-001]
4. If the performance rule had only **Create Incident** (the guide says most SLAs are used for visibility), no move would occur for a non-media application; only real-time media uses link quality for path selection by default (deck claim). [VERIFIED for Create Incident semantics — SRC-000038 p.45; UNVERIFIED for the "media only by default" statement — 03-application-traffic/02 deck]
5. If instead the path rule used **Best Path** mode, the ION would pick the path with the lowest single metric among active paths (no load sharing, bandwidth ignored); backup would not be considered unless all active paths were down. [VERIFIED — 03-application-traffic/02 (SRC-000029 pp.450–451)]
6. Fail-back: from 5.2.1 flows return to the active path once it is available and in policy. [VERIFIED — SRC-000029 p.449]
7. Observability: Flow Browser → Advanced Info → **Flow Decision Data** shows the SLA violation, the action taken and the forced-move reason; incidents `APPLICATION_PERFORMANCE_DEGRADED` / `CIRCUIT_PERFORMANCE_DEGRADED` when configured; Application Site Details shows per-path performance. [VERIFIED — 03-application-traffic/06 (SRC-000029 pp.547–549), 07-operations/01]
8. Trap: if the SaaS traffic reaches the DC over the backup and the DC has no Internet egress policy or NAT for it, the move "succeeds" in SD-WAN terms but the session fails upstream; DC sites cannot carry network or NAT policy, so DC Internet egress must be handled by DC infrastructure. [VERIFIED — 10-design/01 (SRC-000038 pp.24, 51); UNVERIFIED (internal) for NAT branch-only — 02-network/11]

## 4. Answer

Neither policy "overrides" the other: path policy sets which paths are allowed and in what order; performance policy decides when a path is unusable for that application. With Move Flows configured and the Internet path out of SLA, Microsoft 365 moves to the MPLS VPN (backup) and comes back when the Internet path is in policy again. With only Create Incident, traffic stays on the Internet and an incident is raised. The decision and reason are visible in Flow Decision Data.

## 5. What to check / collect next

Performance policy rule action for the app; SLA thresholds vs built-ins (All Apps 500/5/100, Media 150/2/40); Flow Decision Data for sample flows; `inspect flow detail` PATH field over time; circuit LQM in the Link Quality dashboard. [VERIFIED sources above]

## 6. Gaps exposed

KG-085 (drop-and-track and Best Available Bandwidth naming), KG-086 (which failures move existing vs new flows), KG-088/KG-127 (jitter default). New: **KG-134** — official list of default actions in the two built-in performance policy rules (Create Incident only vs Move Flows) in current SCM.

## 7. Validation status

**SCENARIO VALIDATED** for the mechanism (steps 1–3, 5–7 all VERIFIED); the "default behaviour without a performance rule" branch (step 4) is PARTIAL.
