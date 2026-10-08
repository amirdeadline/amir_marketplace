# Device onboarding: connect, claim, assign, shells, offline access

Domain: 1 / 7 (batch B3 start) | Applies to: Admin Guide May 2025 (navigation of that date), ION 6.x | Status: DOCUMENTED | Last updated: 2026-10-08

## Explanation (plain words)

A new ION arrives knowing only how to call home. You plug its controller port (or any port marked for controller use on newer models) into a network with DHCP and Internet, power it on, and it appears in your tenant as **Unclaimed**. **Claiming** it tells the controller "this box is mine"; the controller installs your tenant's certificates on it. **Assigning** it attaches it to a site. Then you configure its ports. If a device is not there yet, you can create a **device shell** (a placeholder) and configure it in advance; when the real device arrives you attach it to the shell. If you ever lose all passwords on an offline device, a **one-time password** flow through the console and SCM lets you back in.

## Device states (official)

| State | Meaning |
|---|---|
| Unclaimed, Offline | physical device allocated to the tenant, not yet talking to the controller |
| Unclaimed, Online-Restricted | virtual device added and licensed, talking to the controller but not claimed |
| Claimed, Online | claim completed; certificates installed (device goes offline briefly during claim) |
| Assigned | associated with a site (assignment runs in the background; green = up, red = down) |

Internal deck adds the ZTP sequence: controller port on DHCP with Internet → device calls home over SSL → appears in Unclaimed → claimed → switches to tenant credentials → can be upgraded, assigned, configured → pulls configuration. MSP or customer must provide DHCP for ZTP.

## Procedures (official, May 2025 navigation)

**Connect** (p. 140–141): connect the controller port to a LAN with Internet (DHCP by default; static possible through the AUX port); devices without a dedicated controller port use port 1 or 2 on a DHCP network with Internet; power on; the device registers and goes Online. Power troubleshooting steps are listed; if the device never powers on, submit an RMA.

**Claim** (p. 141–143): `Workflows > Devices > Unclaimed` → filter by serial, model, connected → State icon → Claim the device → OK. Certificates download; device reconnects as Claimed/Online. Related CLI: `inspect connection`, `clear connection`.

**Assign** (p. 143): `Workflows > Devices > Claimed` → State icon → Assign to a site → pick site → Done. Steps are identical for physical and virtual devices except for ports. Related CLI: `inspect connection`, `dump device status`, `clear connection`.

**Device shell** (p. 144): pre-stage configuration; with site templates, enter the serial number at deployment; if the device is unavailable, a shell (element shell) is created and the configuration is transferred when the physical device is attached; the shell is then deleted. Up to two shells per site at creation (p. 59).

**Device Access One-Time Password** (pp. 144–146): for a claimed or assigned device that is offline. Console login with username `menu` (the guide prints a fixed password for this menu account; it is not reproduced here), Status → Device offline Access → note the Challenge phrase → in SCM as Super user `Workflows > Devices` → device ellipsis → Generate one-time password → enter the challenge → one-time password → enter on the console. Challenge requests and wrong entries are logged; valid for the configured number of attempts; exiting invalidates the challenge; limits set under `Manage > System > Access Management > Device Access > Device Offline Access Policy`. (The internal best-practices guide gives the newer path `Configuration > Prisma SD-WAN > ION Devices` for the same action.)

**Configure the branch ION** (p. 148): `Workflows > Devices > Claimed` → ellipsis → Configure the device; Basic Info shows model, redundancy mode, serial, software version; toggles for L3 Direct Private WAN Forwarding, L3 LAN Forwarding, Application Reachability Probe; "Create an HA group".

## Access and accounts (internal best-practices guide)

- Default device user `elem-admin`; its password is replaced by a random string at claim. Three device roles: Monitor (dump/inspect/file), Read-Only (adds debug and search), Super (configure). SSHv2 only; prefer remote access from the portal (SSH over the TLS channel, audited); direct SSH on public circuit IPs is blocked by default. TACACS+ profiles (up to four servers) from ION 6.5 under `Configuration > Prisma SD-WAN > Profiles and Templates > AAA`; TACACS+ must return the role attribute or read-only is assigned; local user takes priority over TACACS+ if both exist; CHAP and PAP.

## Expected behavior

- After claim the device briefly goes offline, then returns Claimed/Online (official).
- Controller overwrites local configuration after claim (official).

## Verification

- Device list states; `dump device status`, `inspect connection` on the device (names from the admin guide; syntax to verify in B18).

## Limitations and gotchas

- Navigation paths differ between the admin guide (Workflows > Devices …) and the internal 2026 guide (Configuration > Prisma SD-WAN > ION Devices). Both are recorded with dates; see KG-046.
- The OTP console account password is printed in the official guide; treat as sensitive operational detail and do not spread it.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Device states and meanings | VERIFIED | DOC | SRC-000029 p.140 |
| Connect, claim, assign steps and menu paths | VERIFIED (May 2025 navigation) | DOC | SRC-000029 pp.140–143 |
| Device shell behavior | VERIFIED | DOC | SRC-000029 p.144; p.59 (max two shells) |
| OTP flow, logging, policy location | VERIFIED | DOC | SRC-000029 pp.144–146 |
| ZTP sequence and DHCP requirement | CORROBORATED (official connect steps + internal deck) | DOC | SRC-000029 p.140; WS-033 slide 37 |
| elem-admin default, randomized at claim; device roles; SSHv2 only; TACACS+ from 6.5 | UNVERIFIED (internal, strong); TACACS+ chapter exists in admin guide pp.363–368 to confirm in B13 | DOC | WS-001 §Accessing ION Devices via the CLI |
| Branch ION Basic Info toggles | VERIFIED | DOC | SRC-000029 p.148 |

## Open questions

- KG-066: official statement of controller-side device roles (Monitor/Read-Only/Super) and the 6.5 TACACS+ floor; check SRC-000029 pp.333–368 and SRC-000035.
