# Controller releases, maintenance windows, and who upgrades what

Domain: 1 / 7 | Applies to: cloud-managed controller; Admin Guide May 2025 | Status: DOCUMENTED | Last updated: 2026-10-08

## Explanation (plain words)

Palo Alto Networks upgrades the cloud controller and tells you in advance. You upgrade the ION device software yourself, when you choose, from the releases that Palo Alto Networks has allocated to your tenant. The two are independent: a new controller release is never a prerequisite for an ION software release (this separation is also the main finding of the KB's 2026-09-30 feature review).

## Documented release types and notice periods

| Release type | What it is | Notice |
|---|---|---|
| Major release (controller) | significant features and optimizations; pushed in a planned maintenance window | at least 21 days before (production) |
| Maintenance release (controller) | bug fixes, sometimes features; planned window | at least 21 days |
| Infrastructure maintenance | incremental features/optimizations; may include a hot fix | 10 days |
| Urgent scheduled upgrades | hot fixes, emergency fixes (zero-day, critical UI) | best effort 48 hours, may be shorter |
| UI/infra-only updates | UI patches outside the formal process when no API or backend change | CI/CD windows every Friday and Sunday, 8 PM–2 AM PT |
| ION software device releases | made available to tenants by allocation; appear under Software Upgrade in SCM; customer decides when to upgrade | not applicable; see Live Community "ION Software Release Guidelines" |

Notifications: email and the SD-WAN portal (via SCM); subscribe at `https://sase.status.paloaltonetworks.com`.

## Related procedures (to read in B17)

Upgrade ION Device Software (p. 326), Schedule Software Upgrade (p. 327), View Upgrade Status (p. 328), Bulk Upgrade (p. 329). On-Premises Controller has its own upgrade chapters (WS-044 pp. 35–39).

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Release types and notice periods (21 / 10 days, 48 h, Fri/Sun windows) | VERIFIED | DOC | SRC-000029 pp.14–15 |
| ION upgrades are customer-controlled, via allocation | VERIFIED | DOC | SRC-000029 p.14 |
| Controller releases are not ION prerequisites | CORROBORATED | DOC | SRC-000029 p.14; WS-021 feature review (2026-09-30) |

## Open questions

- KG-065: the Live Community "ION Software Release Guidelines" page (recommended release policy) is referenced but not in the KB; fetch under D2 in B17.
