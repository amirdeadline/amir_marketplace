# S06 — Branch offline after cut-over (controller connectivity)

Domains: 1, 8 | Evidence type: SCENARIO | Written 2026-10-08

## 1. Situation

During a router-replacement cut-over the branch ION 3200 (6.5.x) was moved from the staging LAN to the production Internet handoff behind the customer's firewall/proxy. SCM shows the device Offline for 25 minutes and the incident `DEVICESW_DISCONNECTED_FROM_CONTROLLER`; users can still browse the Internet through the ION.

## 2. Question

Explain what "offline" means here, isolate the cause, and restore management.

## 3. Reasoning chain

1. **What is down.** The device opens three controller connections (Config and Events = MRL, Analytics, Flows); Offline = all three down; Partially online = only telemetry down. The data plane does not depend on the controller, which is why Internet still works. The controller raises `DEVICESW_DISCONNECTED_FROM_CONTROLLER` after ~10 minutes unreachable; at a branch `SITE_CONNECTIVITY_DOWN` needs all fabric links down **and** all devices disconnected > 10 minutes. [VERIFIED for connection states and site-connectivity rule — 08-troubleshooting/03 (SRC-000029 p.40), 07-operations/01 (WS-041 pp.26–28); UNVERIFIED for the 10-minute hold on the device incident]
2. **Official steps for the incident.** Clear interface/network incidents → act on process incidents → check firewall rules on the ION or in front of it against the controller allow-list → check for controller maintenance → Support. [VERIFIED — WS-041 p.14; allow-list chapter still unread, KG-060/118]
3. **Which interface carries management.** The ION uses the controller port, or any interface marked "use for controller connection" (Gen-2 from 6.3.1), choosing by cost; private categories often have controller use disabled. After the move, the port with Internet may be one whose circuit category has "Use for Controller Connections" cleared, or the controller port may still point at the old staging LAN. The `DEVICESW_INITIATED_CONNECTION_ON_EXCLUDED_PATH` alarm appears if an excluded path had to be used. [VERIFIED — 02-network/01 (SRC-000029 pp.72–74), 01-fundamentals/01; UNVERIFIED (internal) for the MRL interface order — 09-datapath/02]
4. **Path tests from the device** (console 115200/8/N/1 or SSH from the LAN): `ping <port> 8.8.8.8`, `nslookup controller.<region>.cgnx.net`, `tcpping <port> controller.<region>.cgnx.net:443`, `dump controller status`, `dump overview` (certificates valid), `dump interface status <port>` (DNS server and default route present). [VERIFIED for `dump controller status` meaning and command names in the CLI reference; UNVERIFIED (internal) for the sequence — 08-troubleshooting/03]
5. **Typical post-cut-over causes.** (a) Firewall blocks TCP 443 to the controller destinations or DNS; (b) **TLS-intercepting proxy** → "invalid certificate" in the mrl_agent log; the controller FQDNs must be exempted from decryption; (c) **MTU**: "ssl timeout" patterns → lower the interface MTU (1460 or less) on the controller path; (d) no DHCP/DNS on the new segment; (e) stale `mrl_agent` instances. [UNVERIFIED (internal TSE playbooks) — 08-troubleshooting/03; proxy/decryption exclusion also appears in WS-001's control-app guidance — 03-application-traffic/02]
6. **What not to do.** Do not re-claim or "Put back in Inventory" for a connectivity problem (that is for claim-state recovery); do not disable the firewall globally — allow the documented controller destinations instead. [VERIFIED for the claim-recovery semantics — SRC-000029 p.324]

## 4. Answer

The ION is forwarding but cannot reach the controller over TCP 443 from its new position. Check from the device (ping, DNS, tcpping to the regional controller FQDN on 443), then look at the mrl_agent log for certificate errors (proxy) or SSL timeouts (MTU). The usual fix is a firewall/proxy exemption for the controller destinations and DNS, or an MTU reduction on the controller-facing interface; make sure the interface used for management is on a circuit category with controller connections enabled. Once `dump controller status` shows all sessions Connected, SCM clears the incident.

## 5. What to check / collect next

`dump controller status`, `dump overview`, `dump interface status`, `file tailf log mrl_agent`, `tcpdump <port> args="host <controller-ip> and port 443" show` (free-form args not on 6.4.2/6.5.1), customer firewall logs for 443 to the controller IPs; `dump-support all file=<name>` if escalating. [sources above; 08-troubleshooting/02]

## 6. Gaps exposed

KG-060/KG-118 (official allow-list of controller destinations and ports), KG-124 (official controller-interface selection), KG-125 (safety of debug logging).

## 7. Validation status

**SCENARIO PARTIAL** — the state model and official incident steps are VERIFIED; the diagnostic recipe is internal.
