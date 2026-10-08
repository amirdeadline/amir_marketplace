# Deployment blueprint: greenfield Prisma SD-WAN with Prisma Access DIA (Deployment Guide Oct 2025)

Domain: 9 (design/deployment) | Applies to: SRC-000037 Deployment Guide Oct 2025 (122 pp), validated with SCM 2025.r3.0, Prisma Access 6.0.0 Preferred, ION 6.5.2; SCM navigation as printed in the guide (pre-Nav-3.0 labels, see note 05-scm/01) | Status: VERIFIED (official) | Last updated: 2026-10-08

## Explanation (plain words)

This is the order of operations Palo Alto Networks validated for a new deployment: licences → global preparation → onboarding workflows for data centers and branches → device configuration → path policy → zone-based firewall → HA branch. Each step below keeps the parameters and warnings the guide attaches to it, because those are the details a design reviewer checks (the address pool to remove, the alarm a default policy raises, the state that blocks site assignment). Example values (10.130.x, 65401) are the guide's, not requirements.

## 1. Licences and SCM access (pp.16–22)

Activation emails launch guided activation in Common Services (Multi-Tenant Cloud Management; claim subscription under the Customer Support Account and parent tenant; Add Licensed Product; SASE region; unique hostname). Verify tenant status "Complete". SCM: Configuration pane, pin the Configuration Scope; Prisma Access settings live under `Configuration > NGFW and Prisma Access` with folder scopes.

## 2. Preparation (pp.22–29)

1. **Allocate remote-network bandwidth** per Prisma Access compute location (`NGFW and Prisma Access > Remote Networks > Setup > Bandwidth Management`): **minimum 50 Mbps per compute location**; enable Autonomous DEM there; Push Config → Remote Networks; deployment takes about 15–30 minutes.
2. **Enterprise prefixes** (`Configuration > System > Enterprise Prefixes`): the onboarding workflow sets the Prisma Access infrastructure subnet to **192.168.255.0/24**, so **remove the 192.168.0.0/16 summary** unless in use; add any non-RFC-1918 internal prefixes; remove unused ones.
3. **Circuit categories** (`Configuration > Resources > Circuit Categories`): rename unused categories for a second provider of the same type (MPLS-1/MPLS-2); clear **Use For Controller Connections** on private categories (Table 3: MPLS No; internet categories Yes).
4. **Security zones** (`Configuration > Policies > Security > Security Zones`): PRIVATE, PUBLIC, PRIVATEWAN, VPN created before onboarding so the workflow can bind the zone to the auto-created Prisma Access tunnels.
5. **SASE Connectivity** (`Configuration > Resources > SASE Connectivity`): Deployment Mode **Internet-Only**, Security Zone **PUBLIC**; optionally override default local AS and tunnel inner pool.
6. **Claim devices** (`Configuration > ION Devices > Unclaimed Devices`): only online devices can be claimed; if Software shows **"Software Unknown"** run **Recheck SW version**, otherwise site assignment fails; upgrade anything below 6.5.2 before onboarding.

## 3. Onboarding workflows (pp.30–48)

- Data centers: `Configuration > Onboarding > Onboard Connectivity to Private Apps > Configure > Prisma SD-WAN Data Center > Create`: site name, address search, internet circuits (Manage Networks to create ISP names; circuit category, WAN network, circuit name, Link Down/Up Mbps), private WAN circuits (MPLS network), select devices. Example DCs: 1000/1000 and 500/500 Mbps internet, 500/500 and 200/200 MPLS.
- **Domains and DC service groups** (`Configuration > Resources > Service and DC Groups`): domains East US / West US; groups Primary-DC and Secondary-DC (type Prisma SD-WAN) with per-domain membership (Table 6; preset domain includes all DCs). Licence activation **auto-creates two standard VPN endpoints (active and backup) per Prisma Access region** in service groups **"Prisma Access: All Regions"** and **"Prisma Access: Backup Regions"**.
- Branches: `Configuration > Onboarding > Onboard Branch Sites > Configure > Add`: site info, Domain (and optional path policy stack), circuits, device, then **Prisma Access Location page**: primary and secondary location with IPsec termination node (e.g. us-southwest-edelweiss, us-east-violet). Example circuits: cable 75/12, DSL 24/3, MPLS 50/50.
- MPLS direct communication DC↔branch is out of scope of the guide; branch↔branch over MPLS is covered.

## 4. Device configuration (pp.48–68)

- **DC devices** (`Configuration > Data Centers > device`): Port 1 Connect to Internet, static IP + default gateway, **Advanced: External NAT Address and Port 4500** (NAT traversal, RFC 3947/3948); Port 2 **Peer with a Network**, circuit label MPLS, static IP, no gateway. Site: **Add IP Prefixes** (10.5.0.0/16 per DC) and **Mode Control**. Routing (`ION Devices > device > Routing > BGP Global Config`): local AS, **MD5 secret**, router ID, Advanced **Keep Alive 1 / Hold 3**; Create Peer type **Core** towards the core router (remote AS). Default gateway on the internet port is enough for public fabric links; BGP towards the MPLS edge is needed for private fabric links.
- **Branch devices** (`Configuration > Branch Sites > device`): Basic Info enable **L3 Direct Private WAN Forwarding** and **L3 LAN Forwarding**; Port 1 Internet DHCP (accept "Update NAT Zone to Internet"); Port 2 LAN static, **Application Reachability Probe Source Interface** enabled, **Scope Global** ("only global prefixes are included in BGP route advertisements"); Port 3 Internet DHCP or Private WAN static **with default gateway** (removes the need for static/BGP towards MPLS). DHCP server per site (`Branch Sites > site > Configure DHCP Scopes`: subnet, gateway, domain, DNS, range). Switch each branch to **Control**. Static routes for non-attached LAN networks with **Scope Global** ("Prisma SD-WAN routes traffic to only global prefixes"). Direct branch-to-branch over MPLS requires the provider network to carry the branch prefixes (BGP advertisement or static routes handed to the provider).

## 5. Path policies and inter-site links (pp.69–85)

- Controller programs routes per fabric link: DC side = all global prefixes of the branch; branch side = DC site prefixes **plus a default route**; branch-to-branch links carry the peer branch's global prefixes.
- Default path set (Table 16): **enterprise-default** = Prisma SD-WAN VPN on any public and any private, Direct on any private; **default** = Direct on any private and any public, VPN on any public and private; no service groups. Default behaviour: DCs↔branches over VPN; MPLS branches talk directly; internet-only branches cannot reach each other; DIA direct with the default NAT rule. **Warning: a site bound to the default set without both a public and a private circuit raises a major alarm** → clone and trim the set.
- **Advanced stacks**: selecting Advanced for one policy type switches all four (path, QoS, security, NAT); switching modes later is time-consuming, keep one mode. Procedure: clone the default set per site type (Dual-INET PathSet, MPLS+INET PathSet), create stacks with the clone as the default-rule set, bind on **Stacked Bindings**.
- Dual-internet sites (Table 18): default rule active **Direct on any public**, backup **Prisma SD-WAN VPN on any public** with active group Primary-DC / backup Secondary-DC (DC security stack as fallback for DIA); enterprise-default = VPN on any public. MPLS+internet (Table 19): same plus VPN on any private as backup; enterprise-default VPN on public and private.
- **Transit between branches** (5.4): set Primary-DC/Secondary-DC on the enterprise-default rule; **each DC ION needs a default or WAN summary route (e.g. 10.130.0.0/16) to the core** so branches homed on different DC IONs can reach each other.
- **Branch-to-branch fabric links** (5.5, `Branch Sites > site > Overlay Connections > Connected Sites: Branch-Branch > Add Link`): source/destination circuits; behind NAT the interface needs **External NAT Address and Port** with inbound UDP 4500 statically mapped.
- **MPLS Direct override** (5.6): global path prefix of MPLS branch prefixes; new set with Direct on MPLS active, VPN public/private backup, DC groups; placed as Policy Set 1 in the MPLS+INET stack.
- **DIA via Prisma Access** (5.7): default rule active **Standard VPN on any public**, backup **Direct on any public**, (MPLS sites) L3 failure path VPN on any private; service groups active **Prisma Access: All Regions**, backup **Prisma Access: Backup Regions**. Prisma Access security policy must permit the DIA applications.

## 6. Zone-based firewall (pp.85–93)

Global security prefixes (DC Networks 10.5.0.0/16, 10.6.0.0/16; Remote-Site Networks 10.130.0.0/16; policy type NGFWSECURITY). Built-in rules in every stack: **self-zone** (traffic from the ION; to the ION on trusted L3 interfaces — controller, L3 LAN, L3 private WAN; on untrusted public L3 interfaces only ION-sourced), **intra-zone** (allow same zone), **default** (deny all). Example set (Table 23): PRIVATE→VPN (dns-base, enterprise-http, enterprise-ssl, ping), VPN→PRIVATE with DC/Remote-Site prefixes as source filters, PRIVATE→PUBLIC (dns-base, web-browsing, ssl, ping), PRIVATE→PRIVATEWAN and PRIVATEWAN→PRIVATE for legacy MPLS sites during migration. Stack = up to four sets + default-rule set (DefaultSet). **Bind zones per device before binding the stack**: PUBLIC → internet circuits **and the service_link entries described "Auto created and managed by SDWAN"**, PRIVATE → LAN port, VPN → VPN, PRIVATE-WAN → MPLS circuit. Branch-to-branch links inherit the parent VPN interface's zone. Bind the stack on Stacked Bindings.

## 7. HA branch with ION 1200-S (pp.94–120)

- Management: ZTP port 1 on each device first; both IONs managed through DHCP + DNS + outbound TCP 443. Site created with the Dual-INET stack and two devices; **devices only become active once the site is in control mode**; HA group with **Advertisement Interval 1000 ms**; DHCP server only active once a device is Active.
- Primary device: SVI **VLAN 192 "virtual-controller", Use this port for HA, static 192.168.0.1/30**, gateway .2, DNS; SVI VLAN 151 LAN (Scope Global, 10.130.96.1/24); switch port 5 trunk VLANs 151 and 192 to the LAN switch; probe source vlan-151; Redundancy: Spoke Cluster, **Priority 50**, HA Control Interface virtual-controller, **Track Availability Switch Port 5, Reduce Priority 50**. Then WAN: Port 1 circuit label; **Port 3 Interface Type Bypass Pair** (3 & 4) Internet DHCP. Secondary: same with 192.168.0.2/30, **Priority 45**; it goes Init → Backup and is managed over the virtual controller through the primary.
- Cabling (Table 28): move each ISP into the other device's port 3 (WAN input) and connect that device's port 4 (pass-through) to the partner's port 1, so both circuits terminate on whichever device is active. SCM status lags minutes; verify with toolkit `dump spoke-ha status`.
- **Prisma Access bypass path set** (7.12): because the backup's management traffic rides the primary's DIA policy, add rules **Prisma SD-WAN Control (order 1024, app paloalto-prisma-sdwan-control, Direct on Any Public)**, **DNS (1025, dns-base, destination GoogleDNS 8.8.8.8/32 and 8.8.4.4/32)**, **NTP (1025, ntp-base)**; from 6.0.1 a common App-ID set exists for Prisma Access and SD-WAN — choose the common App-IDs. Place the set as Policy Set 1 (Dual-INET) / Policy Set 2 (MPLS+INET).

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Procedure order, parameters, warnings (Software Unknown, major alarm, 50 Mbps minimum, 192.168.255.0/24, auto-created Prisma Access groups, bypass set order values) | VERIFIED (official, Oct 2025) | DOC | SRC-000037 pp.14–120 |
| Navigation paths | VERIFIED for the Oct 2025 UI; may differ after Nav 3.0 (KG-103) | DOC | SRC-000037 |
| Common App-ID set from 6.0.1 | VERIFIED | DOC | SRC-000037 p.119 |

## Open questions

- KG-128: the guide's enterprise-default rule shows "Direct on any private" as a backup path (p.70, p.74) — confirm whether the current default set still includes direct private as backup (admin guide default policy text).
- KG-129: does the Prisma Access onboarding still hard-set the infrastructure subnet to 192.168.255.0/24 in current SCM, or was that specific to the validated release.
