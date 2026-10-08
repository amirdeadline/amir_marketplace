# QoS policy, circuit capacities (bandwidth allocation), DSCP mapping

Domain: 3 | Applies to: Admin Guide May 2025 | Status: DOCUMENTED (official structure); internal tuning guidance pending B10 | Last updated: 2026-10-08

## Explanation (plain words)

QoS in Prisma SD-WAN is about **priority and shaping on the WAN interface**. Each application is placed in one of four priorities (Platinum, Gold, Silver, Bronze) and, within a priority, one of four queues by transfer type (real-time audio, real-time video, transactional, bulk), giving 16 queues. The **circuit capacity** scheme decides what share of a circuit each priority/queue gets, and can change by circuit size using breakpoints. **DSCP** values can be honored on the first packet of unknown flows, mapped to priorities, or written onto packets leaving the LAN toward the WAN.

## Documented facts (official pp. 442–446, 477–479)

- QoS stacks/sets mirror path stacks (≤4 sets + default set; one stack per site; Default and Enterprise Default rules; sets can be created blank, from a Palo Alto template, cloned from stacked or original sets).
- QoS rule: name, order (default 1024), network context, source/destination prefix, applications (≤256), **priority**, **DSCP action** (No Action, or Mark/Remark 0–63 applied to all packets of the flow in the LAN-to-WAN direction). Bulk edit available. Attribute precedence: network context > source prefix > application > destination prefix. When rules with DSCP are applied, the branch ION honors the DSCP bits of the first packet of an unknown application flow and queues it in that priority class.
- **Circuit capacities** (`QoS Sets > Edit Circuit Capacity`): percentage per priority and traffic type; up to **four bandwidth allocation schemes and three breakpoints** (Mbps) per QoS set; the scheme matching the link capacity is used; adding a breakpoint copies the existing scheme's values; deleting one merges ranges; allocations must sum to 100%.
- **DSCP mapping** (`QoS Set > DSCP Configuration`): up to **16 DSCP values** mapped to priority and transfer type; first match wins in policy-set order; default mapping EF→Platinum Audio, AF41/AF31→Gold Video, CS6→Platinum Transactional, AF21→Silver Transactional, AF11→Bronze Bulk.
- Circuit speeds (Link Up/Down) are the shaping rates; QoS is enabled per circuit (note 02-network/01). CLI names: `inspect qos bwc debug state|queue history|queue snapshot`, `dump qos bwc config`, `clear qos bwc queue snapshot`.

## Internal (deck slide 157; WS-001 §Policies and §QoS Policy)

Four buckets with four queues each; bandwidth allocation per bucket and queue; DSCP-based rules; mark/remark; traffic engineering and priority rules can be coupled or decoupled.

WS-001 §QoS Policy (May 2026, internal, strong): the scheduler is **Hierarchical Fair Service Curve (HFSC)** (hierarchical link sharing; decouples bandwidth from delay); QoS is enforced **only on branch WAN interfaces**, not at DC sites (DC circuits carry no shaping speeds); the circuit Upload/Download speeds are the thresholds that make QoS engage, so **QoS does not engage if circuit speed is missing**; the sub-queue comes strictly from the application's **Transfer Type**, never from its category (a voice app in Platinum lands in Platinum-Audio only if its transfer type is Real-time Audio); a new custom application inherits the default rule (**Bronze/best effort**) until an explicit QoS rule places it; flows are **re-classified and re-queued** when identification changes (for example SSL → a specific SaaS app); Flow Browser shows QoS set, rule, traffic type, priority class and DSCP in both directions; by default the ION classifies by App-ID, not incoming DSCP, unless DSCP mapping is configured; QoS acts when utilization approaches the configured speeds, primarily **egress (LAN-to-WAN) shaping with ingress (WAN-to-LAN) policing on the download speed**, aggregated across direct, fabric VPN and standard VPN traffic on that interface.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| QoS rule attributes, precedence, DSCP action semantics, 256 apps | VERIFIED | DOC | SRC-000029 pp.444–446 |
| Circuit capacity schemes: 4 schemes, 3 breakpoints, copy/merge behavior, 100% sum | VERIFIED | DOC | SRC-000029 pp.477–478 |
| DSCP mapping: 16 values, first match, default table | VERIFIED | DOC | SRC-000029 p.479 |
| 16 queues (4 priorities × 4 transfer types) | CORROBORATED (official transfer-type queue order + deck + WS-001) | DOC | SRC-000029 p.466; WS-033 slide 157; WS-001 §Policies |
