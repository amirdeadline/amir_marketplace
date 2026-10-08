# Standard VPN (IPsec and GRE to third parties) and DC-to-DC standard VPN

Domain: 2 / 4 | Applies to: Admin Guide May 2025 | Status: DOCUMENTED | Last updated: 2026-10-08

## Explanation (plain words)

Besides its own automatic fabric tunnels between IONs, an ION can build ordinary **IPsec or GRE tunnels** to anything else: a cloud security service, a third-party firewall, or another data center ION. These are called **Standard VPNs**. They are treated like any other path: monitored for application reachability, usable in path policy, and subject to QoS. CloudBlades can automate their creation for some cloud services.

## Documented behavior

- Types: IPsec or GRE; one endpoint on the ION, the other on the remote peer; a combination of IPsec and GRE tunnels from one interface to one endpoint is allowed, but not two tunnels of the same type to the same endpoint from the same interface.
- **IPsec profile** (`Manage > Resources > Configuration Profiles > IPsec`): IKEv1 or IKEv2; IKE lifetime default 24 h; port default 500 (must match the endpoint); IKEv1 mode Main or Aggressive (Aggressive when behind NAT or multiple tunnels to one endpoint); IKEv2 "ReAuth" renegotiates at lifetime; up to **8 proposals** (DH group, encryption, hash/PRF); **AES-GCM only with IKEv2**, GCM PRF limited to SHA-256 and SHA-512; DPD: IKEv1 delay/timeout, IKEv2 uses 5 retransmissions; ESP lifetime default 24 h; encapsulation Auto or Force UDP (must match); authentication PSK (secret, local ID type Interface IP / Hostname / Custom, optional remote ID) or certificates (cert, local CA, private key, optional remote CA). New tenants get default IPsec profiles matching cloud partner best practices; open a support case if missing.
- **GRE**: stateless; interface comes up as soon as created with parent up and admin up unless keep-alive is enabled; strongly recommended to enable GRE keep-alive (default interval 10 s, retry 3) or endpoint liveliness probes to avoid black-holing; keep-alive needs a peer that answers; NAT between endpoints may break keep-alives; checksum requires peer support (else frame errors); parent interfaces for a branch: Internet or Private WAN L3 port, virtual interface, PPPoE, bypass pair WAN ports, sub-interfaces; DC: any Connect-to-Internet or Connect-to-Peer-Network port; not a Private L2 bypass port nor a loopback; Inner Tunnel IP; VRF (two standard VPNs in different VRFs cannot share the same overlay endpoint IP; a Global-VRF standard VPN carrying custom-VRF LAN traffic needs a NO-NAT rule); endpoint (required at branch so policy can target it; Peer IP overrides endpoint addresses; DC requires Peer IP). Apply ZBFW and source NAT to GRE over the Internet (unencrypted).
- **DC-to-DC standard VPN**: IPsec only (not GRE); IKEv1 or IKEv2; **Passive Mode** (responder-only) on one end to avoid both DCs initiating; Peer IP mandatory (endpoints are not pushed to DC IONs); view under Overlays Connections for the DC site; if one DC ION is behind NAT, configure an inbound DNAT so port 4500 translates to 4501 for that IP.
- Related CLI names: `dump vpn count|ka|ka summary|ka vpn id|status|summary`, `dump service end points`, `dump service link summary|stats|status`, `dump overview`, `dump intra cluster tunnel`, `dump routing summary`, `dump routing vpn host tracker`.

## Internal guidance (WS-001 §Standard VPN, not yet read in detail; deck slide 368: standard VPN tunnels are created, monitored and maintained for CloudBlade integrations such as Zscaler)

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Standard VPN types, monitoring, QoS applicability, one-per-type-per-endpoint rule | VERIFIED | DOC | SRC-000029 p.224 |
| IPsec profile parameters and defaults (24 h, port 500, 8 proposals, GCM/IKEv2, DPD) | VERIFIED | DOC | SRC-000029 pp.225–227 |
| GRE behavior, keep-alive defaults 10 s / 3, parent interface rules, VRF rules | VERIFIED | DOC | SRC-000029 pp.228–230 |
| DC-DC IPsec only, passive mode, peer IP mandatory, 4500→4501 DNAT when behind NAT | VERIFIED | DOC | SRC-000029 pp.231–232 |

## Open questions

- KG-076: read WS-001 §Prisma SD-WAN Standard VPN (lines 917–995) and the Zscaler/ZEN CloudBlade playbook for field practice (B8/B12).
