# Licensing and subscriptions

Domain: 1 | Applies to: cloud-managed Prisma SD-WAN; licensing documents dated 2024–2025 | Status: DOCUMENTED | Last updated: 2026-10-08

## Explanation (plain words)

Every ION device needs a subscription to be used. Data center devices need a **data center subscription** each. Branch devices use one of three **branch models** per tenant: per device, per branch site, or a shared pool of bandwidth (aggregate). The models differ in what is included (zone-based firewall, reporting, longer data retention) and in how you count bandwidth. Palo Alto Networks measures usage but, as of the documents read, does not cut traffic when you exceed or when the term expires; it reserves the right to enforce or charge later.

## Documented model

| Model | Unit | Tiers | Included | Notes |
|---|---|---|---|---|
| Data center subscription | per ION (physical or virtual) assigned to a DC site | bandwidth up to device throughput per datasheet | essential DC feature set | only for DC-capable models |
| Branch per device | per ION at a branch; HA pair needs two | Small ≤25 Mbps, Medium ≤250 Mbps, Large ≤2,500 Mbps (also legacy tiers 25/50/150/250/500/1000/2500 Mbps) | ZBFW always included | optional add-ons per device: WAN Clarity Reporting (WCR), Clarity Network DVR |
| Branch per site | shared by all IONs in a branch site | Small/Medium/Large with the same ceilings, counted across all devices in the site | ZBFW, DVR and WCR included | recommended for HA sites or multi-device sites |
| Branch on demand (aggregate bandwidth) | pool in Mbps shared by all branch sites | — | ZBFW, WCR, DVR included | minimum average 10 Mbps per device; needs an accurate consumption estimate |

- Bandwidth = ingress + egress through the ION (LAN to WAN plus WAN to LAN).
- Terms: minimum one year, maximum five years, also for add-ons.
- Only one branch model per tenant.
- DVR and WCR are tenant-level features: if bought, they must be bought for every branch device; no partial coverage.
- DVR: retain and access up to 90 days of statistics, policy, configuration, alarms and alerts (datasheet) versus the default seven days (activation guide). Licensed per ION device.
- WCR: automatically generated downloadable reports plus advanced AIOps insights.

## Monitoring and enforcement

- All sites report ingress and egress bytes on all WAN circuits; per-site utilization is computed over five-minute intervals; monthly site utilization = maximum five-minute value in the month; monthly tenant utilization = sum of the site values.
- Not enforced today; Palo Alto Networks reserves the right to enforce on new purchases and renewals and to charge for excess on a "true forward" basis.
- Expired subscription: traffic is not halted, but operating is non-compliant.
- SCM shows usage under **Prisma SD-WAN Subscription Usage** (admin guide pp. 51–56; to be read in B17).

## Internal context (TME deck, Feb 2026; sales motion, not product behavior)

- Per-device and per-site Small/Medium/Large offerings became available January 2024; legacy device tiers "will not change in FY'24, may be discontinued for net-new quotes from FY'25 (under consideration)". Aggregate model best for many low-throughput sites; per-site model best for HA and higher-throughput sites.

## Verification

- `Insights`/dashboard: Prisma SD-WAN Subscription Usage (admin guide TOC p. 51).
- Customer Support Portal: view licenses (activation guide p. 29).

## Limitations and gotchas

- Numbers above come from the Activation and Onboarding 6.4 guide (April 2024) and the datasheet (Nov 2025). Pricing, SKU names and FY roadmap statements are internal and may change; label them accordingly.
- vION licenses: an internal TAC runbook (SRC-000090) describes how support allocates vION licenses per tenant through a Jira process; customer-facing statement is only "virtual devices appear Unclaimed and Online-Restricted when added and licensed" (admin guide p. 140). Covered further in B2/B3.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Every ION needs a subscription; DC subscription per DC device; three branch models; one model per tenant | VERIFIED | DOC | WS-040 pp.5–6 (rev 2024-04-12); SRC-000031 p.6 |
| Tier ceilings S/M/L = 25/250/2,500 Mbps; legacy device tiers list | VERIFIED | DOC | WS-040 pp.5–6 |
| HA pair needs two per-device licenses; per-site license shared | VERIFIED | DOC | WS-040 p.6 |
| ZBFW included in all models; WCR and DVR add-ons per device, included per site and aggregate | VERIFIED | DOC | WS-040 p.6 |
| Aggregate model minimum average 10 Mbps per device | VERIFIED | DOC | WS-040 p.6 |
| Five-minute interval measurement, monthly max per site, sum per tenant; not enforced; true-forward right | VERIFIED | DOC | WS-040 p.7 |
| Expired subscription does not halt traffic | VERIFIED | DOC | WS-040 p.7 |
| DVR retains up to 90 days; licensed per device | VERIFIED | DOC | SRC-000031 p.4 |
| Default retention seven days | VERIFIED | DOC | WS-040 p.6 |
| Terms 1–5 years | VERIFIED | DOC | WS-040 p.5 |
| Jan 2024 availability of S/M/L; FY'25 discontinuation under consideration | UNVERIFIED (internal, forward-looking) | DOC | WS-033 slides 495–497 |

## Open questions

- KG-005: official SKU list and how licenses map to the Subscription Usage dashboard values; read SRC-000029 pp.51–56 in B17.

## Addendum 2026-10-08 (B20: Design Guide view, KG-126)

Design Guide Oct 2025 (SRC-000038 pp.55–56, VERIFIED): two Prisma SD-WAN subscriptions — **data center** (ION 7000, 7100V, 9000; unlimited bandwidth) and **bandwidth** (any branch device). Table 13 tiers by model: 1200-S 25/50/250 Mbps; 3200 250/1000 Mbps; 5200 250 Mbps, 1 Gbps, 2.5 Gbps; 9200 1/2.5 Gbps; 3102V and 3104V 25/50/250 Mbps; 3108V 250/1000 Mbps; 7108V and 7116V 1/2.5 Gbps. Optional per-branch-device licences: ZBFW, Prisma SD-WAN DVR (Clarity Network DVR, 90 days of statistics), Prisma SD-WAN Report (WAN Clarity Reports); DVR and Report are enabled at customer level but must be purchased for every branch device. Prisma Access **site licence** (Very Small ≤25 Mbps, Small ≤50, Medium ≤250, Large ≤1000, X-Large ≤2500; minimum two sites; includes Interconnect and SD-WAN add-ons; new tenants only; cannot mix with remote-network units) — reconcile tier naming with the subscription guide (KG-126).
