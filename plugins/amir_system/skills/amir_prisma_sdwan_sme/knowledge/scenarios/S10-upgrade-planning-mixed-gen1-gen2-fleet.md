# S10 — Upgrade planning for a mixed Gen-1 / Gen-2 fleet to 6.5.x

Domains: 7 | Evidence type: SCENARIO | Written 2026-10-08

## 1. Situation

Fleet: 30 × ION 2000 and 10 × ION 3000 (Gen-1) on 5.6.15, 80 × ION 1200-S and 3200 on 6.3.5, two DC pairs of ION 9000 on 6.1.11, 12 HA pairs, one FIPS virtual DC in Azure (3108v on 6.1.x), two inter-DC standard VPNs. Target: a supported 6.5.x line; some customers ask for 6.8.

## 2. Question

Plan the paths, order, pre-checks and what will change after the upgrade.

## 3. Reasoning chain

1. **Paths.** To 6.5.x: `5.6.x → 6.1.x → 6.3.x → 6.4.x → 6.5.x`; `6.2.x → 6.3.x|6.4.x → 6.5.x`; `6.4.x → 6.5.x`. DCs must be ≥ 5.4.x before branches go to 6.1.x. To 6.8.x: `… 6.3.x → 6.5.x → 6.8.x`, `6.5.x → 6.8.x`. Rollback is the reverse. [VERIFIED — 07-operations/03 (RN 6.5 p.11; public 6.8 page)]
2. **Platform floors.** Gen-1 (1000, 2000, 3000) ends at 6.5.x; 6.6.1+ only on Gen-2 and ION 9000; so the 6.8 request is impossible for the ION 2000/3000 — they stay on 6.5.x (supported to 2028-02-15 with hardware exceptions) or are replaced. ION 1000/2000/1200 above 80 % memory risk reboots after upgrade, especially 5.x → 6.x: check memory first. Stacked policies only from 6.0.1: any site still on Original policy sets blocks the 6.0.1+ step until migrated. [VERIFIED — 07-operations/03 (6.6/6.8 pages), 03-application-traffic/02 (SRC-000029 pp.439–441), 04-security/01]
3. **Order.** DCs first (prerequisite), one DC ION at a time so branches re-home to the peer (capacity rule), then branches in rings (lab → low-impact → batches ≤ 50 per bulk operation); HA pairs: backup first, then active (internal practice). [VERIFIED for the DC prerequisite and bulk limit — RN 6.5, SRC-000029 pp.326–331; UNVERIFIED (internal) for backup-first — WS-001]
4. **Considerations per hop.** 6.3.1: performance policy replaces Advanced-menu LQM/APT thresholds (review sites without a policy; defaults apply). 6.4.1: performance probes/MOS/UDP-TRT, branch gateway prerequisites, SVI Auto Operational State, HA-over-SVI downgrade gate, **all policies must use App-IDs ≥ 6.0.1** before 6.4.1. 6.5.1: inter-DC fabric tunnels (**all existing BGP peers set to Local scope after upgrade** → set Global where learned prefixes must propagate), GCM ciphers (keep a CBC option if downgrade is possible); the two inter-DC standard VPNs: do not mix with fabric inter-DC tunnels, or add the prefix-list deny. FIPS vION from <6.2.1: disable FIPS, upgrade, re-enable (up to 20 min; 6.2.3/6.3.1–6.3.3 blocked); FIPS-certified 6.1.2 and 6.4.2+. [VERIFIED — 07-operations/03 (RN 6.3/6.4/6.5), 02-network/06 (SRC-000029 pp.89–90)]
5. **Scheduling mechanics.** Scheduling needs ≥ 5.1.1; download first (up to 4 interfaces, controller/Internet fallback), max download/upgrade time 5–59 min (default 30), 3 retries, bulk 50; rollback action available; `dump software status` to verify. Incompatible targets cannot be selected in bulk (intermediate hop first). [VERIFIED — SRC-000029 pp.326–331]
6. **Pre-checks and post-checks (Day 2 draft, cross-checked).** Controller connectivity, disk, memory, HA state, policy compatibility per hop, suppression rules for Device and Spoke HA incident categories during the window; afterwards: version, three controller connections, no second `DEVICESW_SYSTEM_BOOT`, circuits/overlays up, BGP prefix counts, HA roles, flows, 24-hour incident review; `DEVICESW_IMAGE_UNSUPPORTED`/`DEVICEHW_DISKENC_SYSTEM` → TAC. [CORROBORATED — 07-operations/03 (WS-030 §13), 07-operations/01 (WS-041)]
7. **Branch Security tenants** need an "-I" image; CDSS supported models exclude ION 2000/3000. [UNVERIFIED (internal) — 04-security/03; WS-021]

## 4. Answer

Upgrade both DC pairs first (6.1.11 → 6.3.x → 6.4.x → 6.5.x, one ION at a time), then the 6.3.5 Gen-2 branches (→ 6.4.x → 6.5.x), then the Gen-1 2000/3000 (5.6.15 → 6.1.x → 6.3.x → 6.4.x → 6.5.x) after confirming memory headroom and stacked policies; the FIPS vION goes through the FIPS disable/enable procedure. After 6.5.1 set the inter-DC BGP peers back to Global where needed and decide between standard-VPN and fabric inter-DC tunnels. The Gen-1 devices cannot go to 6.8; present 6.8 as a Gen-2-only step from 6.5.x with its own PQC/BGW-filter downgrade considerations.

## 5. What to check / collect next

Per-device version and model inventory, memory utilisation (Device Activity), Original vs stacked policy state, App-ID versions in policies, FIPS state, HA roles, BGP peer scopes before/after 6.5.1, incident suppression windows. [sources above]

## 6. Gaps exposed

KG-065 (release guidelines / recommended release), KG-115 (EOL and compatibility tables as text), KG-116 (6.6.x considerations), KG-113 (retired codes after 6.3.2).

## 7. Validation status

**SCENARIO VALIDATED** — paths, floors, considerations and mechanics are VERIFIED; sequencing details (backup-first, rings) are internal and labelled.
