# ION software upgrades, release naming, upgrade paths, considerations, lifecycle and recommendation policy

Domain: 7 | Applies to: Admin Guide May 2025 pp.326–332; ION release notes 6.3/6.4/6.5 (upgrade chapters), 6.8 (cached public page), 6.6 (cached public page); WS-001 §ION Software Upgrade; WS-021 lifecycle evidence (EOL summary, compatibility matrix, 2026-09-30); WS-030 Day 2 §13 | Status: DOCUMENTED | Last updated: 2026-10-08

## Explanation (plain words)

An ION version reads **primary.release.main-build** (6.5.1-b1). Upgrades are scheduled from the controller: download first, upgrade later or immediately, with retry limits and chosen download interfaces; bulk upgrades handle up to 50 devices. Each release note lists an **upgrade path** (multi-hop) that is also the rollback path in reverse, plus per-feature **upgrade/downgrade considerations** (configuration that must be removed before a downgrade, or that changes on upgrade). Hardware generations end at specific trains: Gen-1 models stop at 6.5.x, ION 7000 at 6.3.x. A "recommended release" is customer policy, not a vendor statement, unless the vendor's release guidelines say so.

## Scheduling mechanics (official pp.326–331)

- Scheduling needs device software ≥ **5.1.1**; download and upgrade can be scheduled separately; if only a download time is given the upgrade must be scheduled afterwards; with no times both run immediately.
- **Interfaces**: up to **4** interfaces for the download; blank = controller interface or any interface marked use-for-Internet; if a chosen interface is unusable the device falls back to those.
- **Max Download Time / Max Upgrade Time** 5–59 minutes (default **30**); the device retries **three times** before declaring failure; a failed download means no upgrade; a download in progress when the max time elapses still completes; after failure, reschedule. Actions: cancel/abort download, abort upgrade, upgrade already-downloaded software, retry download, **rollback** to an older version.
- Status screen (Device Options → Device Software Upgrade): Download Scheduled, Download Complete, Upgrade Scheduled, Other (in progress); History shows the last five operations; Retry Upgrade / Edit / Abort. Verify with `dump software status`.
- **Bulk Software Upgrades**: up to **50 devices** per operation, incompatible devices cannot be selected (upgrade to an intermediate version first), schedule with download/upgrade dates and max times.

## Upgrade paths and considerations (release notes)

- 6.5 path (RN 6.5 p.11): `… -> 5.6.x -> 6.1.x -> 6.3.x -> 6.4.x -> 6.5.x`; `6.2.x -> 6.3.x|6.4.x -> 6.5.x`; `6.4.x -> 6.5.x`; reverse for rollback. Prerequisite: before upgrading branches to 6.1.x, DCs must run ≥ 5.4.x. Example (RN 6.3): to reach 6.3.5-b9 from 5.6.15 go `5.6.15 > 6.1.11-b2 > 6.3.5-b9`.
- 6.8 path (public page): `5.6.x|6.0.x -> 6.1.x -> 6.3.x -> 6.5.x -> 6.8.x`; `6.2.x -> 6.3.x|6.4.x -> 6.5.x -> 6.8.x`; `6.3.x|6.4.x -> 6.5.x -> 6.8.x`; `6.5.x -> 6.8.x`. **Upgrade advisory**: ION 1000/2000/1200 consistently above **80 % memory** risk unexpected reboots after upgrade, especially 5.x→6.x; assess memory first.
- Considerations: **6.3.1** performance policy (default LQM thresholds applied when no policy is attached; Advanced-menu LQM/APT thresholds become read-only and are ignored; review before upgrading), IPv6 BGP (remove IPv6 config before downgrade). **6.4.1** performance policy (probes, MOS, UDP-TRT, System Rules; on downgrade to 6.3.x rules with new SLA parameters are not sent and System Rules cannot be created), Branch Gateway (enable L3 Direct Private WAN Forwarding and L3 LAN Forwarding; remove BGW-related Service & DC Groups and WAN default route distribution before downgrade), SVI Auto Operational State (on for new SVIs, off for existing; disable before downgrade), HA over SVI access port (downgrade blocked unless a trunk member port exists for the HA control SVI), App IDs (all policies must use application versions ≥ 6.0.1 to upgrade to 6.4.1; no 6.4.1+ applications in policies before downgrading); **FIPS virtual form factor**: disable FIPS, upgrade, re-enable (up to 20 minutes) when moving from <6.2.1 to ≥6.2.1 (6.2.3/6.3.1–6.3.3 blocked); FIPS-certified versions 6.1.2 and 6.4.2+. **6.5.1** DC-to-DC fabric tunnels (hybrid topologies need a prefix list denying the second DC's prefixes on the standard VPN; **all existing BGP peers become Local scope after upgrade**, change to Global to distribute learned prefixes), GCM encryption (select at least one CBC algorithm before downgrading). **6.8.1** PQC (remove PPK/ML-KEM from IPsec profiles before downgrade), BGW overlay prefix filters (remove before downgrade).
- Platform floors: **6.6.1 and higher only on Gen-2 (3200, 5200, 9200) and ION 9000; Gen-1 (1000, 2000, 3000) end at 6.5.x** (6.6 release page). Compatibility matrix (WS-021 summary): **ION 7000 ends at 6.3.x**. EOL summary (WS-021 summary): 6.5 supported through **15 Feb 2028**, with hardware exceptions extending 6.5 to hardware EOL for ION 1000/2000/3000. End-of-sale ≠ end-of-support.

## Internal practice (WS-001 §ION Software Upgrade; WS-030 §13)

Download ahead of the window; bulk upgrades for scale; **HA pairs: upgrade the backup first**, then the active (failover and, with pre-emption, failback cause brief interruptions); alternative: raise the upgraded backup's priority to make it active, verify tunnels, then upgrade the former active; monitor and use Retry; verify with `dump software status`. Day 2 draft adds rings (lab → low-impact branches → batches → DCs per prerequisite), pre-checks (path, ordering, model/FIPS, controller connectivity, disk, health, HA state, policy feature compatibility at every hop, suppression rules for Device and Spoke HA categories), post-upgrade validation (version, three controller connections, no second `DEVICESW_SYSTEM_BOOT`, circuits, overlays, BGP prefix counts, HA roles, flows, 24-hour incident check) and failure handling (`DEVICESW_IMAGE_UNSUPPORTED`, `DEVICEHW_DISKENC_SYSTEM` → TAC). The project's own release-recommendation engine (WS-021) uses 6.5.3-b16 as a **user-selected fallback**, explicitly "not a vendor preferred-release claim"; CDSS requires an "-I" image.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Scheduling rules, 4 interfaces, 5–59 min max times (default 30), 3 retries, status states, bulk 50 | VERIFIED | DOC | SRC-000029 pp.326–331 |
| Version naming; 6.5 and 6.8 upgrade paths; DC ≥5.4.x prerequisite | VERIFIED | DOC | RN 6.5 p.11 (WS-047); public 6.8 page (WS-022 b2c53f0703ff) |
| Per-feature upgrade/downgrade considerations 6.3.1, 6.4.1, 6.5.1, 6.8.1 | VERIFIED | DOC | RN 6.3 p.11; RN 6.4 pp.12–13; RN 6.5 pp.11–12; public 6.8 page |
| 80 % memory advisory for ION 1000/2000/1200 | VERIFIED | DOC | public 6.8 page |
| Gen-1 end at 6.5.x; 6.6.1+ Gen-2 and ION 9000 only | VERIFIED | DOC | public 6.6 page (WS-022 9b9fd3acba30) |
| ION 7000 ends at 6.3.x; 6.5 supported to 2028-02-15 | CORROBORATED (WS-021 summary of EOL summary and compatibility matrix; pages not stored as text) | DOC | WS-021 lifecycle evidence |
| HA backup-first sequencing | UNVERIFIED (internal, strong) | DOC | WS-001 §ION Software Upgrade |
| "Recommended release" guidance | UNKNOWN officially; Live Community release guidelines not in KB (KG-065) | — | — |

## Open questions

- KG-065 (existing): Live Community "ION Software Release Guidelines" (recommended/preferred release policy) not in KB.
- KG-115: full EOL and compatibility matrix tables (per model, per train) as first-hand text (cached HTML exists, no text extraction).
- KG-116: 6.6.x upgrade/downgrade considerations page (not among cached pages).
