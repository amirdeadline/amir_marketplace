# S07 — Poor voice quality on an MPLS + Internet branch

Domains: 3, 8 | Evidence type: SCENARIO | Written 2026-10-08

## 1. Situation

Branch ION 1200-S (6.5.x), MPLS 20/20 Mbps and cable 100/20 Mbps. Teams/SIP calls to the DC-hosted PBX are choppy in the afternoon. Path policy for voice: active = Prisma SD-WAN VPN on MPLS; backup = VPN on Any Public. QoS stack is the default. Circuit speeds were left at system defaults when the site was built.

## 2. Question

Find the cause and fix it; say what evidence proves each step.

## 3. Reasoning chain

1. **Identify the flows and their path.** Flow Browser → voice flows → path (VPN over MPLS expected), Flow Decision Data (SLA violations, moves); `inspect flow detail` for a call (PATH, QoS class, app). [VERIFIED — 03-application-traffic/06 (SRC-000029 pp.547–549); 08-troubleshooting/02]
2. **Measure the path.** LQM on the MPLS VPN towards the DC gives latency/loss/jitter/MOS; built-in Media SLA 150 ms / 2 % / 40 ms jitter. Compare with the Link Quality dashboard and `inspect lqm stats path-id=<vpnlink_id>` (internal). Afternoon degradation on a 20 Mbps MPLS points to congestion rather than carrier fault. [VERIFIED for LQM scope and SLA values — SRC-000029 p.548, SRC-000038 p.46; UNVERIFIED (internal) for the LQM CLI and sampling — SRC-000101]
3. **QoS shaping depends on circuit speed.** Link Down/Up speeds drive the QoS shaper; defaults left in place mean the ION shapes to the wrong rate and congestion happens upstream in the carrier queue, where ION QoS cannot protect voice. Set carrier values (internal guidance: 1–2 % below rated). Default class budgets: Platinum 50 %, Gold 25 %, Silver 15 %, Bronze 10 %; within a class real-time audio queue 20 % of the allocation; the default QoS rule maps unmatched apps to Bronze — voice needs an explicit QoS rule (Platinum) or the correct transfer type (real-time audio). [VERIFIED for speeds→shaping, class defaults — 02-network/01 (SRC-000029 pp.68–69), 10-design/01 (SRC-000038 p.45); UNVERIFIED (internal) for the 1–2 % rule and the default-rule-to-Bronze statement — WS-001]
4. **Does the performance policy move voice?** Only if a rule with Move Flows (graceful/forced) covers the voice app; with Create Incident only, calls stay on degraded MPLS and `APPLICATION_PERFORMANCE_DEGRADED` is raised. Backup paths are used on SLA breach, so after fixing the rule voice shifts to the Internet VPN when MPLS breaches the SLA. Advanced actions: FEC for lossy paths, packet duplication across up to three VPN paths for critical calls. [VERIFIED — SRC-000038 pp.45–47, 03-application-traffic/05]
5. **Application identification.** SIP/RTP recognised by signature; Teams as a SaaS app by prefixes; if calls are mis-identified (e.g. generic `ssl`/UDP) they fall to the default rules and Bronze; check `dump appdef config application=<name>`, app-map behaviour (custom L7 apps need DNS visibility; 10-hour app-map expiry; no QUIC detection). [VERIFIED for identification techniques — 03-application-traffic/01; UNVERIFIED (internal) for app-map expiry/QUIC — 08-troubleshooting/04]
6. **Underlay checks.** Carrier-side loss shows as LQM loss with low ION egress; MPLS WAN network must match at both ends for the overlay (else no private overlay and voice silently rides Internet); interface errors `DEVICEHW_INTERFACE_ERRORS`/half-duplex incidents. [VERIFIED for incidents; CORROBORATED for WAN-network match — 02-network/01, 07-operations/01]
7. **Measurement caveat.** Branch samples LQM every minute, hub every 10 s (internal), so branch and hub values differ; use the branch view for the user experience. [UNVERIFIED (internal) — SRC-000101]

## 4. Answer

Most likely the MPLS circuit saturates in the afternoon and, because the circuit speed was left at defaults and voice is not in a Platinum QoS rule, the ION neither prioritises voice nor shapes at the real rate; LQM shows jitter/loss on the MPLS VPN while the Internet VPN is clean, and no performance rule moves the flows. Fix: set real circuit speeds (slightly below rated), add a QoS rule placing voice in Platinum/real-time audio, add a performance rule with the Media SLA and Move Flows (graceful) so voice uses the Internet VPN when MPLS breaches, optionally FEC or packet duplication for the PBX traffic. Verify with Flow Decision Data and MOS trending.

## 5. What to check / collect next

Circuit speeds vs contract; QoS stack rules and the app's transfer type; performance policy actions; LQM/MOS per path; `dump wan interface summary`, `inspect flow detail`; interface error counters. [sources above]

## 6. Gaps exposed

KG-070 (DC bandwidth informational only), KG-088/KG-127 (jitter default), KG-134 (built-in performance rule actions). New: **KG-140** — official statement of the default QoS rule's class (Bronze/best-effort) and whether real-time audio transfer type alone changes class assignment.

## 7. Validation status

**SCENARIO PARTIAL** — causes and fixes rest on VERIFIED policy facts; the shaping-at-default-speed consequence and LQM internals are internal.
