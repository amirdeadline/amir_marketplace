# Identity in policy: User-ID (User-ID Agent and Cloud User-ID), Cloud Identity Engine groups, Device-ID

Domain: 4 | Applies to: User-ID from 6.2.1 (NGFW agent model, internal); Cloud User-ID (CUID / User Context) from 6.6.1 per TSE playbook; Device-ID enforcement in 6.5.x behind a support-enabled flag | Status: DOCUMENTED + INTERNAL PLAYBOOK | Last updated: 2026-10-08

## Explanation (plain words)

Instead of matching IP addresses, path, QoS and security rules can match a **user** or a **group**. Two mappings are needed: IP to user and user to group. IP-to-user comes either from a **User-ID Agent on a PAN-OS firewall** that a data-center ION connects to, or (newer) from **Cloud User-ID** in the Cloud Identity Engine (CIE) that the controller reads directly. User-to-group always comes from CIE. The controller merges both, filters them by each branch's known prefixes, and pushes them to branch IONs. For branch-to-branch traffic over direct tunnels the sending ION tags packets with the user so the receiving ION can apply user rules to inbound flows. **Device-ID** (IoT Security device categories) can be used the same way in security policy once Support enables it.

## Documented facts (official pp. 452–455; 6.5 release notes)

- Only for TSG-compatible tenants; requires a PAN-OS firewall license and Cloud Identity Engine activation in the **same TSG**. PAN-OS 10.1.7, 10.2.3, 11.0.x or higher.
- Nine-step workflow: DC ION learns IP-to-user from the User-ID Agent, pushes it to the controller, the controller gets user-to-group from CIE, distributes to branches after prefix filtering, pushes policies, the branch enforces, tags site-to-site traffic with the username, the remote branch enforces on the tag, and stats/logs go to the controller.
- **Supported only for branch-to-branch traffic over direct tunnels**; not for traffic that originates from or transits a data center.
- Configuration: `Workflows > Data Centers > site > Configuration > Configure User Agent` (name, Disabled flag, host IP/FQDN, port, optional Collector Name for a virtual system, optional Collector Pre-Shared Key); `Manage > System > Identity Management > Cloud Identity Engine > Configure Identity Engine`; username formats **UPN** (`user@domain.com`) or **SAM Account Name** in `netbios\user` form only (not `domain\user`). Rules: Users tab, default Any; **explicit user beats group, group beats Any/Known/Unknown**.
- CLI: `dump user-id agent config|statistics|status|summary`, `dump user-id groupidx|group-mapping|ip-user-mapping|statistics|status|summary|useridx`, `clear user-id agent statistics`.
- Device-ID enforcement (6.5 release notes): device IDs from IoT Security can be used in security policies; "contact Palo Alto Networks Support" to enable. Deck: Device-ID can also drive path/performance, QoS, NAT and local security actions, "enabled with feature flag".

## Internal playbook (Confluence 645959526, TSE, v9 2026-03-26)

- Feature introduced **6.2.1**; supported only for SD-WAN "BF/GF" tenants with CIE onboarded. **CUID / User Context model (6.6.1)**: a controller service (CUID Sync) pulls IP-to-user over a persistent gRPC connection every **5 s**; CIE group sync is partial every **15 min**; the two IP-mapping sources **cannot coexist**. UI: new User Context tab, separate Users and Groups dropdowns, Users monitoring tab.
- Constraints: the NGFW model needs a hub ION connected to a standalone PAN-OS firewall (branch-only deployments cannot use it); no hub-transit traffic; **no NAT policy, no Dynamic User Groups, no IPv6, no overlapping prefixes**.
- Usernames and group names travel as a **64-bit index in the Geneve tunnel header metadata**; policy lookup order: username, then groups (first matching rule), then Known, then Any. Unknown user: security hits the highest-priority Unknown rule (recommend drop); path/QoS use unknown/any rules; **security and QoS re-evaluate when the mapping arrives, path does not change**.
- Hub role: the controller pushes config to all hub IONs and picks the **lowest Element ID** as active User-ID client; failover to the next hub; **no preemption**.
- Triage: `dump user-id status` ("User-ID service running"), `dump user-id agent config all`, `dump user-id agent status all` (Last Disconnect Reason: Proposal Mismatch or Peer Authentication Failed means PSK or ID mismatch; TLS 1.2), hub log `file view log ip-users.log`, spoke `dump user-id ip-user-mapping all`, `dump user-id summary`, `inspect flow details` (UG-INFO). Alarms `USER_ID_DIRECTORY_SYNC_FAILED`, `USER_ID_HUB_SELECTION_FAILED`; CUID states Operational / Error (certificate, gRPC) / Initialising. A mapping only reaches a branch whose known prefix covers the user IP (global interfaces, site prefixes, global BGP/OSPF routes).

## WS-001 §CIE and User-ID (internal, strong)

Same TSG for SD-WAN, PAN-OS and CIE; User-ID Agent only on DC IONs; choose **one** source (Agent or CUID; CUID preferred when Prisma Access is the identity source; configured under `Configuration > Prisma SD-WAN > System > Cloud Identity Engine`); scope branch prefixes correctly or enforcement silently fails; explicit user beats group beats Any.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Licensing, PAN-OS floors, workflow, direct-tunnel-only scope, formats, precedence | VERIFIED | DOC | SRC-000029 pp.452–455 |
| CLI names for user-id | VERIFIED | DOC | SRC-000029 p.455; CLI reference WS-048 pp.321–331 |
| Device-ID enforcement exists in 6.5, enabled via Support | VERIFIED | DOC | ION release notes 6.5 (WS-047) |
| Introduced in 6.2.1; CUID model in 6.6.1; 5 s / 15 min sync; one source at a time | UNVERIFIED (internal playbook) | DOC | Confluence 645959526 |
| 64-bit index in Geneve metadata; lookup order; re-evaluation; hub election lowest Element ID, no preemption | UNVERIFIED (internal playbook) | DOC | Confluence 645959526 |
| No NAT/DUG/IPv6/overlapping prefixes | UNVERIFIED (internal) | DOC | Confluence 645959526 |

## Open questions

- KG-092: official public documentation of Cloud User-ID (User Context) in Prisma SD-WAN and its release floor (playbook says 6.6.1; the May 2025 guide predates it).
- KG-093: Device-ID enforcement GA status and license dependency (IoT Security plus SASE?) beyond "contact Support".
