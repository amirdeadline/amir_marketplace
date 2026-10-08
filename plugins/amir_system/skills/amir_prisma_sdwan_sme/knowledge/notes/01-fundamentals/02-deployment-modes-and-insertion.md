# Deployment modes (Analytics, Control, Disabled) and branch insertion models

Domain: 1 | Applies to: ION 6.x, SCM | Status: DOCUMENTED | Last updated: 2026-10-08

## Explanation (plain words)

An ION at a branch can run in one of three modes. **Analytics** only watches traffic and reports on applications; it makes no decisions and builds no VPNs. **Control** is the real SD-WAN mode: the ION forwards traffic, picks the best path for each application, applies security and QoS policies, and builds VPN tunnels to data centers. **Disabled** means the ION is just a wire between the router and the switch; it does nothing. Analytics mode is the usual first step in a migration because it lets you learn the application mix before you change anything.

## Documented definitions

| Mode | Behavior (official) | Needs a DC site? |
|---|---|---|
| Analytics | ION sits in-path between branch router and LAN switch; monitors traffic; no policy, no path selection; no VPN to the data center | No |
| Control | ION sits in-path or replaces the router; forwards traffic, selects best path, applies security and QoS policies; for a native SD-WAN VPN branch-to-DC an ION 3000/7000/9000 class device is required in the data center (admin guide wording, May 2025; the DC-capable list elsewhere also includes 3200, 5200, 9200) | Yes, for fabric VPN |
| Disabled | In-path link only; no monitoring, no policy, no path selection; for staging or troubleshooting; not for production (best-practices wording) | No |

Switching: `Workflows > Prisma SD-WAN Setup > Branch Sites`, site ellipsis menu, **Switch to Control Mode**; same for Data Centers (admin guide p. 154, May 2025 navigation). Data centers only need to be activated when deploying in Control mode; when both branch and DC are activated, VPN tunnels form automatically (admin guide p. 59).

## Branch insertion models (internal deck, Feb 2026; consistent with official modes)

1. **Analytics only**: transparent inline insertion between the branch L2 switch and L3 router; integrated fail-to-wire preserves connectivity on power loss. Use cases: learn traffic profile, migrate from IP/port rules to application rules, baseline performance.
2. **Control mode with router interop**: same inline position, now with app SLAs, QoS and path selection; the router can stay as a media converter for TDM circuits; allows gradual router retirement. Deck note: if the branch will use the direct private-WAN underlay path, have at least one Prisma SD-WAN DC site reachable on the underlay so underlay reachability can be detected.
3. **Router replacement (Control mode)**: suitable for Ethernet-only sites; smallest footprint.
4. **High availability pair**: active/backup devices; "maintain 100% circuit capacity upon device failure"; Ethernet-only WAN interfaces; does not replace voice gateway services such as SRST.

## Expected behavior

- In Analytics mode there are no VPN tunnels to the DC (official).
- Moving a site to Control mode pushes network and security policies and starts path selection and application prioritization (official p. 154).

## Verification

- Site Summary and the Prisma SD-WAN Dashboard show device-to-controller status and application utilization regardless of mode (p. 30).
- In Control mode, VPN status appears under site/device status (details in batch B5).

## Limitations and gotchas

- The admin guide text for Control mode still lists only ION 3000/7000/9000 as DC devices in the Get Started chapter while the Set Up Devices chapter (p. 140) lists 3000, 3200, 5200, 7000, 9000, 9200 for DC insertion. Treat the longer list as current.
- Disabled mode guidance ("not recommended for production") comes from the internal best-practices guide, not the admin guide.

## Version notes

- No version dependency found for the three modes.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Analytics, Control, Disabled definitions | VERIFIED | DOC | SRC-000029 p.11 |
| DC ION required for native VPN in Control mode | VERIFIED | DOC | SRC-000029 p.11, p.59 |
| DC-capable models: 3000, 3200, 5200, 7000, 9000, 9200; branch-only: 1000, 1200, 2000 (3000, 3200 either) | VERIFIED | DOC | SRC-000029 p.12, p.140 |
| Switch to Control Mode menu path | VERIFIED (navigation as of May 2025; re-check against Sep 2026 SCM navigation in B14) | DOC | SRC-000029 p.154 |
| Disabled mode is for staging/troubleshooting only | UNVERIFIED (internal, strong) | DOC | WS-001 §Deployment and Operational Modes |
| Four insertion models and their use cases; fail-to-wire | UNVERIFIED (internal) | DOC | WS-033 slides 44–47 |
| Underlay reachability needs at least one DC reachable on the underlay | UNVERIFIED (internal); mechanism to be confirmed in routing batch | DOC | WS-033 slide 46 |
| HA preserves 100% WAN capacity on device failure | VERIFIED (marketing-level statement) | DOC | SRC-000031 p.5 |

## Open questions

- KG-062: official description of fail-to-wire behavior per model (bypass pairs are documented per model in SRC-000031 and admin guide p.148; the behavior statement "fail open or closed" needs the bypass-pair section p.233).
