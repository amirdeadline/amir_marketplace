# Dashboards and monitoring screens: what each shows, licences, scope, time ranges, freshness

Domain: 5 / 7 | Applies to: Admin Guide May 2025 pp. 30–56 (dashboards), 633–640 (WAN Clarity Reports); WS-041 Incidents and Alerts guide (structure); WS-030 Day 2 draft §3.1.3 (scope, time ranges, freshness; documented behaviour cross-checked); WS-033 deck slides 406–434, 466–478 | Status: DOCUMENTED | Last updated: 2026-10-08

## Explanation (plain words)

The SD-WAN screens answer four questions: is everything connected (dashboard, device list), is the network good (link quality, site and circuit health), are applications good (Applications, Site Summary App Health and App Response Time) and what went wrong (Incidents, Flows, audit logs). Health scores, insights and predictions need the **WAN Clarity or AIOps** licences, long time ranges need **Network DVR**, and weekly PDF-style reports need **WAN Clarity Reports**.

## Tenant-level screens (official)

- **Prisma SD-WAN Dashboard** (p.30–33): default screen (Command Center for SASE customers); refreshed every **5 minutes**; widgets Device To Controller Connectivity (online/offline IONs, branch and DC), Application Utilization (top 10 apps, ingress/egress), Network Insights from Past Week (AIOps for richer insights), Top Sites By Alarms, Link Quality Details (active links table, worst value on top, 90th percentile distribution), Bandwidth Utilization (1H view per-minute, 1D view 5-minute averages; dashed line = configured bandwidth), Transactional Stats (Init/TXN success and failure), Predictive Analysis link.
- **Applications / Application Insights** (p.34–35): health distribution Good/Fair/Poor, time series (durations 1 h, 3 h, 1 d, 7 d, 30 d, 90 d with intervals 1 min, 5 min, 1 h, 1 d), application table (name, profile, health score, impacted sites, volume, init/transaction failures), New Flows (TCP first SYN, UDP first packet), TCP Connection Stats; TCP health distribution charts need the **WCR** licence; health score per path driven mainly by RTT, then loss; Path Detail page.
- **Device Activity** (p.37): CPU, free memory, free disk, interface bandwidth, dropped packets, errors; Top-10 interface filters by bytes/errors/packets/drops.
- **Predictive Analytics** (p.45–48; WAN Clarity licence; preview for tenants migrated to the new data lake): Sites/Links/Applications rated **Good ≥70, Fair 30–69, Poor <30**; a site is Poor when ≥10% of its 5-minute health samples are <30 (36 samples in 3 h); Network Insights (excessive loss, excessive latency, bandwidth upgrade recommended, configured-vs-consumed mismatch, low throughput); top 10 sites by 30-day utilisation growth; Site Capacity Prediction (28-day, fallback 7-day) and anomaly; default range 3 h; >7 days needs Network DVR.
- **Link Quality** (p.49): aggregate MOS, loss, jitter, latency for branch and DC links; last 5 minutes or last hour; by default link quality moves real-time voice/video flows (existing and new) when a link degrades; CLI `inspect lqm stats`.
- **Subscription Usage** (p.51–56): rolling yearly maximum Mbps consumed per month across branch sites, top 5 sites per month, CSV export, top application usage during peak utilisation.
- **WAN Clarity Reports** (p.633–640; separate licence): weekly auto-generated Branch, Data Center and Aggregate Bandwidth reports: Traffic Distribution by path type, Utilization Quadrant (**90th percentile > 50%** of provisioned capacity flags a circuit), Utilization Over Threshold (**minutes above 70%** per day), Heatmap (site local hours), Hotspots (periods above 70%; top 10 applications, destination IPs, source IPs, IP pairs, undefined domains; CSV companions; charts for the top 10 sites by volume), Top N, Application Volume per Circuit.

## Site Summary (official pp.38–44; from release 5.6.1)

Default range 3 h; >7 days needs Network DVR; health scores need WAN Clarity or AIOps (trial preview in 5.6.1). Widgets: Site Health Overview (Current Best Health Score = healthiest Secure Fabric link; Overall Consumed Bandwidth), Circuit Connectivity and Health (physical, tunnel, health time series, consumed bandwidth; per circuit: Circuit Metrics, Insights, Secure Fabric Connectivity and Health with loss/jitter/latency/MOS per link), Circuit Health (per-path score weighted by load vs baseline: "1% loss unloaded scores differently from 2% loss at 100% load"), Consumed Bandwidth anomaly, **Devices** (status, software, admin interface, routing peers, HA, CPU, memory; connection states **Online** = Config and Events + Analytics + Flows all up, **Partially online** = Config and Events up but Analytics and/or Flows down, **Offline** = all three down), Top Events by Priority (all events in range regardless of status; View All Site Alarms and Alerts for standing alarms), Application Utilization, Recent Site Audit Logs, TCP Connection Stats (Init/Transaction success/failure), Top Media Audio Performance (MOS box plot ingress/egress), **App Health** (per app/path; records stop after **10 minutes** of inactivity and a refresh record every **50 minutes** carries the last state without metrics; states Good / Partially Good / Unreachable / No Data; multi-origin apps such as Office 365 may show Partially Good and still work), **App Response Time** (NTTn network transfer time, RTT measured throughout the flow life so TCP proxies are accounted for, SRT server response time, UDP-TRT for DNS only). ADEM for Remote Networks agent runs natively on the ION when enabled.

## Incidents and alerts screens

Official Incidents and Alerts guide (WS-041, Nov 2023): chapters Monitor Incidents, Troubleshoot Incidents (troubleshooting steps per code), Correlate Incidents with SNMP Traps, Device High Temperature Incident, Incident and Alert Event Categories and Codes, API changes for Network Secure Fabric Link event codes, Setup Incident Policies (`Incidents & Alerts > Settings`). Deck (internal): dashboard shows open incidents by category and priority and a chronological top list; filters include suppressed and acknowledged; ML-based correlation aggregates related incidents without configuration; incident policy rules **Suppress, Escalate (priority change or standing-time escalation), Dampen (hold for N minutes before raising)** and **flap rules** (N flaps in M minutes raise a new incident); priorities P1–P5. Detailed codes and policies belong to B17.

## Scope, time ranges and freshness (WS-030 §3.1.3, cross-checked with the guide)

- Tenant-wide: Dashboard, Applications, Branch Sites (Map/List/Activity), Data Centers, Predictive Analytics, Incidents, Subscription Usage, Audit Logs. Per site: Site Summary, Flows (site must be selected), site audit logs, Secure Fabric links. Per device/interface: Device Activity, Routing.
- Durations 1 h / 3 h / 24 h / 7 d / 30 d / 90 d with 1 min / 5 min / 1 h / 1 d samples (matches guide pp.34, 46); default **Past 3 Hours** on Dashboard, Branch Sites, Applications, Site Summary, Predictive Analytics; >7 days needs Network DVR (guide pp.38, 45).
- Flows: last **1000 flows per page**, range up to **one hour**; flows appear roughly **10 s to 3 min** after they start (ION exports periodically) — internal observation, not in the guide.
- Dashboard "Last Update" stamp; 5-minute refresh (guide p.30 agrees). Health samples every 5 minutes (guide p.45 agrees). Site Connectivity Health needs device software 5.6.1+ (guide p.38: Site Summary from 5.6.1).
- Analytics SKUs (deck slide 434, internal): Base 7 days of data (1 h at 1-min, 1 d at 5-min granularity), audit/config history and events 30 days; DVR 90 days of data (adds 1 week/1 month at 1 h, 3 months at 1 d), audit/config history and events 1 year. Official licensing note 01-fundamentals/04 says DVR 90 days.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Dashboard widgets, 5-minute refresh, 1H/1D chart granularity | VERIFIED | DOC | SRC-000029 pp.30–33 |
| Applications screen durations/intervals, WCR gate on TCP health charts, RTT-dominant health score | VERIFIED | DOC | SRC-000029 pp.34–35 |
| Predictive Analytics thresholds (70/30), 10% poor-sample rule, licences, 28/7-day prediction | VERIFIED | DOC | SRC-000029 pp.45–48 |
| Site Summary widgets, device connection states, App Health 10/50-minute behaviour, response-time metrics | VERIFIED | DOC | SRC-000029 pp.38–44 |
| WAN Clarity report set and 50%/70% thresholds | VERIFIED | DOC | SRC-000029 pp.633–640 |
| Subscription Usage content | VERIFIED | DOC | SRC-000029 pp.51–56 |
| Incident policy actions (suppress, escalate, dampen, flap) | CORROBORATED (official guide chapter "Setup Incident Policies" exists; details from deck) | DOC | WS-041; WS-033 slides 411–421 |
| Flows page size 1000 and 10 s–3 min appearance delay | UNVERIFIED (internal Day 2 draft) | DOC | WS-030 §3.1.3 |
| Analytics SKU retention table | UNVERIFIED (deck) | DOC | WS-033 slide 434 |

## Open questions

- KG-105: official statement of Flow Browser limits (flows per page, maximum range) and flow export latency.
- KG-106: official retention table per analytics licence (Base vs DVR) beyond "90 days" (deck gives 7 days / 90 days and 30 days / 1 year for audit and events).
