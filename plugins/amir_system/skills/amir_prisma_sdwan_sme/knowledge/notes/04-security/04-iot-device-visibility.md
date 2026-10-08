# IoT device visibility: DHCP/ARP logging and SNMP crawling for IoT Security

Domain: 4 / 1 | Applies to: Admin Guide May 2025 pp. 111–121; DHCP/ARP visibility from 6.2.1 (deck), SNMP discovery from 6.3.1 (official) | Status: DOCUMENTED | Last updated: 2026-10-08

## Explanation (plain words)

IoT Security needs to see traffic that ties an IP to a MAC address (DHCP, ARP), which never reaches Prisma Access. Branch IONs can log that traffic to Strata Logging Service, and from 6.3.1 can also **crawl** the branch with SNMP and LLDP to discover devices behind switches the ION does not see directly. IoT Security then identifies devices and Prisma Access (or the ION with Device-ID) enforces policy.

## Documented facts (official pp. 111–121)

- Licenses in the same TSG: Prisma Access for Remote Networks with Strata Logging Service, plus IoT Security. When both add-ons are enabled on the Prisma Access account the controller **automatically** enables IoT device visibility on all branch IONs in the TSG, obtains the SLS certificate and instructs IONs to log DHCP and ARP. ARP logs are sent by default; **DHCP logs require the ION to be the DHCP relay or DHCP server**. Per-site toggle at `Workflows > Sites > site > IoT Device Visibility`.
- SNMP/LLDP discovery (6.3.1+): the ION queries LLDP neighbors' MIBs for IP/MAC bindings and recursively "crawls"; **CDP is not supported** (the deck says LLDP/CDP; official text wins). Discovered bindings (with VLAN, subnet) go in Enhanced Application Logs (EAL) to SLS.
- IoT Discovery Profile (`Manage > Resources > Configuration Profiles > IoT Discovery`): Automated SNMP Discovery (default on), Use local neighbors (branch only), Network Discovery Schedule 6/12/24 h (default 24 h), Device Discovery Schedule at or below the network schedule (deck: default hourly), SNMPv2 community (default `public`) or SNMPv3 (noauth / auth with MD5 or SHA128 default / priv with AES or DES). Bind per site or in bulk.
- Security rule for SNMP: custom protocol 161 plus apps `snmp-base` and `snmp-trap`, in a stack bound to the site.
- **IoT SNMP Start Nodes** per site: up to **128** start IPs, each with up to **8** scope subnets; must be reachable from the site's IONs. Source interface defaults to the controller port or management interface; configurable for devices without one. CLI `dump log agent iot snmp config`.
- Device Enforcement: Device-ID in security policy (source and destination device profiles); see note 02.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Licenses, auto-enable, ARP default / DHCP relay-or-server requirement, per-site toggle | VERIFIED | DOC | SRC-000029 pp.111–113 |
| SNMP+LLDP crawling from 6.3.1; CDP unsupported | VERIFIED | DOC | SRC-000029 p.112; ION RN 6.3 |
| Discovery profile fields, schedules, SNMP versions | VERIFIED | DOC | SRC-000029 pp.118–119 |
| 128 start nodes, 8 subnets each | VERIFIED | DOC | SRC-000029 p.121 |
| DHCP/ARP visibility introduced 6.2.1 | UNVERIFIED (deck notes) | DOC | WS-033 slide 124 |
