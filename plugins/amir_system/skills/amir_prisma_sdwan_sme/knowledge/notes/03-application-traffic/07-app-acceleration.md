# App Acceleration (network/L4 optimization and SaaS/L7 acceleration)

Domain: 3 | Applies to: network optimization from ION 6.4.2; SaaS app acceleration from 6.5.2; App Acceleration license required | Status: DOCUMENTED | Last updated: 2026-10-08

## Explanation (plain words)

App Acceleration sends selected Internet-bound TCP traffic from a branch into Palo Alto Networks cloud **acceleration nodes** over automatically built tunnels. Two things happen there: **network optimization** (a smarter TCP stack that starts faster and recovers faster from loss) for all TCP apps, and, for a list of supported SaaS applications, **L7 acceleration** that pre-fetches the dynamic content a user is likely to ask for next. It only applies to traffic whose path policy sends it **direct to the Internet**, and SaaS acceleration requires installing a certificate on clients because the node terminates TLS.

## Documented facts (official pp. 526–535)

- Scenarios: standalone Prisma SD-WAN (SaaS over direct Internet) and Prisma SASE (public and private apps through Prisma Access, real-user metrics). Network optimization: congestion control enhancements, selective acknowledgment, window scaling; aware of device, network and app context; per-session packet shaper with an optimal burst rate; starts at higher throughput and recovers faster than standard TCP. L7: predictive caching and programmed API prefetching, no manual configuration.
- Configuration: `Workflows > App Acceleration > Configuration` → Enabled for Prisma SD-WAN (enables acceleration for all branch sites; network optimization automatically for all TCP apps); for SaaS acceleration upload a trusted certificate (PEM or PKCS12) that is distributed to all clients (the service creates domain-specific certificates per app; do not enable per-app acceleration until certificates exist or clients see TLS errors; exclude segments whose certificate store you do not control, such as guests, using network contexts in performance policy); toggle Accelerated per application; per-site toggle on Branch Sites > Configuration (on by default once tenant-enabled); performance policy rule with action **App Acceleration** and path filter **Direct-Internet**, bound through a performance stack; the path policy for the app must be **Direct on Any Public**.
- Monitoring: Site Summary > Applications > View All Flows > flow > **App Acceleration Info**: cloud availability zone, connect time, RTT variance, end RTT, connection duration, bytes in/out, throughput in/out, begin/end congestion window. CLI: `dump app accel keys`, `dump app accel status`, `dump flow`, `inspect flow details`.

## Internal (deck slides 173–184; WS-001)

Architecture: the controller derives the branch location from site latitude/longitude, picks the closest GCP compute region, spins up (or reuses, multi-tenant) an acceleration node behind an elastic load balancer, sends the ELB public IP to the branch ION, which provisions **Geneve** tunnels. L7-accelerated applications as of Dec 2024: Azure Storage, Box, Google Drive, OneDrive, Microsoft 365, Amazon S3, Salesforce, SAP Ariba, SAP Concur, SAP S/4HANA, Slack, ServiceNow, Zoom. SASE acceleration GA 15 May 2024 (deck notes). WS-001: consider for SaaS over direct Internet; requires the App Acceleration license.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Version floors 6.4.2 / 6.5.2 and license requirement | VERIFIED | DOC | SRC-000029 pp.526–527 |
| Direct-Internet only; configuration steps; certificate requirements; guest exclusion advice | VERIFIED | DOC | SRC-000029 pp.530–531 |
| Flow-level acceleration statistics | VERIFIED | DOC | SRC-000029 pp.533–535 |
| Node placement by geolocation, Geneve tunnels, multi-tenant nodes, supported L7 app list | UNVERIFIED (internal deck, Dec 2024 list) | DOC | WS-033 slides 179–182 |

## Open questions

- KG-089: current list of L7-accelerated applications and whether private-app acceleration through Prisma Access is covered by the SD-WAN license or the Prisma Access license (public docs under D2).
