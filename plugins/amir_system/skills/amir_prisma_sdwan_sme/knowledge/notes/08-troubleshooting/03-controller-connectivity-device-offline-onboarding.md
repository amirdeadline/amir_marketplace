# Device offline, controller connectivity and onboarding failures

Domain: 8 / 1 | Applies to: TSE playbooks Element Connectivity to Controller 175768105 (2024-08), Element Troubleshooting 700294090 (2026-01), TPM check 237599551 (2024-06); Incidents guide troubleshooting steps for `DEVICESW_DISCONNECTED_FROM_CONTROLLER`; Admin Guide onboarding chapter (notes 01-fundamentals/01, 08) | Status: INTERNAL METHOD + official incident steps | Last updated: 2026-10-08

## Explanation (plain words)

An ION talks to the cloud controller over **TCP 443** using its manufacturer (MIC) and claim (CIC) certificates stored in the TPM. "Offline" means that control connection is down; traffic may still flow (the data plane does not depend on the controller) but configuration, statistics and flows stop. The usual causes are Internet or DNS problems on the controller path, a firewall or proxy that breaks TLS, an MTU problem, a stuck management agent, a full or failed TPM, or (for new devices) the wrong port or no DHCP.

## Official steps (`DEVICESW_DISCONNECTED_FROM_CONTROLLER`, WS-041 p.14)

1. Site connectivity: invalid interface configuration, interface or network incidents → clear them. 2. Process incidents (stopped processes) → act on them. 3. Firewall rules on the ION or outside it that block device-to-controller traffic → fix (controller destinations are listed in the Administrator's Guide "Allow IP Addresses in Firewall Configuration", KG-060). 4. Controller maintenance notification → wait. 5. Otherwise open a Support case. The controller raises this incident after the device has been unreachable for **10 minutes** (Day 2 draft; official hold time not quoted in the PDF text read).

## Internal method (TSE playbooks)

- **Reach the device**: remote toolkit is unavailable when offline; use console (AUX, 115200/8/N/1), a jump host, or a peer ION / DC hub with a VPN to the site. New devices without a controller port use **port 1 or 2** on a DHCP Internet network.
- **Internet and DNS from the device**: `ping <src-port> 8.8.8.8` (a backup HA device may only have controller-port connectivity), `nslookup controller.<region>.cgnx.net` (region from the browser URL, e.g. `controller.elcapitan.cgnx.net`, `controller.hood.cgnx.net`), then `tcpping <src-port> controller.<region>.cgnx.net:443`.
- **Is it trying?** `inspect flow brief dstv4=<controller-ip>` (not visible if the device uses a public/private port directly); `tcpdump <port> args="host <controller-ip> and port 443" show` (free-form args not available in 6.4.2/6.5.1).
- **TPM**: legacy models `tpm_selftest` (shell) or mrl_agent log "ENGINE load_private_key:failed loading private key"; x200 models `cgtpmtool -l` (no output = TPM not responding; restart `tcsd` from the support shell, re-check after 10 s); TPM key store is limited (about 8–10 slots), a device moved between tenants stores a new MIC per allocation and a **full TPM blocks claiming**; delete middle keys with `cgtpmtool -d -k <handle>`, never `0x81010005`, `0x81fffffe`, `0x81ffffff`; kernel `tpm_transmit: tpm_recv: error -5` = hardware failure → reboot, RMA if repeated; `debug controller reachability 1` shows "TPM command not responding".
- **Agent health**: more than one `mrl_agent` instance (`ps -aef | grep mrl_agent | grep -v wrap | grep -v grep | wc -l` > 1) → stop the service, kill stale instances, start again; `file tailf log mrl_agent` for errors.
- **MTU**: "ssl timeout" patterns in mrl_agent logs → lower the controller/Internet interface MTU from 1500 to 1460 or less until connected.
- **Proxy / TLS interception**: "invalid certificate" SSL errors in mrl_agent → a proxy between device and controller; the customer must exempt the controller destinations.
- **Forged DNS by a modem** (corner case): `config static host add ip <controller-ip> names controller.<region>.cgnx.net` then `debug process restart name=mrl_agent`; remove with `config static host remove ip <ip>`; not a permanent fix.
- **Verify**: `dump controller status` shows MRL / stats / logs connections up; `dump overview` shows the controller connection and valid MIC and Claim certificates; the Site Summary Devices widget shows all three connections (Config and Events, Analytics, Flows).
- Device connection states (Admin Guide p.40): Online = all three up; Partially online = Config and Events up but Analytics and/or Flows down (traffic unaffected, charts empty); Offline = all three down. `DEVICESW_ANALYTICS_DISCONNECTED_FROM_CONTROLLER` and `DEVICESW_FLOWS_DISCONNECTED_FROM_CONTROLLER` are the Informational incidents for the telemetry channels.

## The four controller connections (legacy KB 74187092, 2019; consistent with current connection states)

| Connection | Process | Purpose |
|---|---|---|
| MRL | `mrl_agent` | online status, configuration push, alerts/alarms to the controller |
| Cloud Infra: stats | stats | network, media and link-quality analytics |
| Cloud Infra: flows | flow | Flow Browser data |
| Cloud Infra: logs | logs | backend device logs for Palo Alto Networks |

`dump controller status` reports **Connected** (all sessions ESTABLISHED to the controller IP on 443), **Partially Connected** or **Not Connected**; `dump interface status interface=<n>` shows state, duplex/speed, address, default route and DNS server per interface. Destinations named: `cgnx.net` (service locator) and the regional controller hostnames.

## Onboarding and claim failures (Admin Guide RMA chapter p.324; notes 01-fundamentals/08–09)

Device stuck in a non-assigned state → "Put back in Inventory" (moves Claimed → Unclaimed and reboots); recovery from Claiming / Claim_Failed → "Recover the device" (Unclaimed and Claimed tabs); element shell flow for pre-staged configuration (10–15 minutes to push). Software must be on the tenant's available list (`DEVICESW_IMAGE_INCOMPATIBLE`: upgrade/downgrade then "Recheck SW Version").

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Official troubleshooting steps for disconnected device | VERIFIED | DOC | WS-041 p.14 |
| Device connection states | VERIFIED | DOC | SRC-000029 p.40 |
| Claim recovery actions | VERIFIED | DOC | SRC-000029 p.324 |
| Console settings, port 1/2 for first connectivity, controller FQDN pattern, tcpping/nslookup flow, MTU and proxy symptoms, static host workaround | UNVERIFIED (internal playbooks) | DOC | Confluence 175768105, 700294090 |
| TPM diagnostics and key-slot behaviour | UNVERIFIED (internal) | DOC | Confluence 237599551, 175768105 |
| 10-minute hold time for the disconnect incident | UNVERIFIED (Day 2 draft; event-code table text garbled) | DOC | WS-030 §3.3.3 |

## Open questions

- KG-060 / KG-118: read the official allow-list chapter and record destinations and ports per service (controller, stats, flows, software download, locator, App Acceleration, SLS, Branch Security content).
