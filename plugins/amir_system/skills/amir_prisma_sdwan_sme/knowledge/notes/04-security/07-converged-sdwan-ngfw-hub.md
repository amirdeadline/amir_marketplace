# Converged SD-WAN: PAN-OS NGFW as a Prisma SD-WAN data-center device (Phase 1)

Domain: 4 / 9 | Applies to: TSE playbook 867864901 (v44, 2026-07-16); no official KB document found | Status: INTERNAL ONLY | Last updated: 2026-10-08

## Explanation (plain words)

Converged SD-WAN lets a **PAN-OS firewall act as the data-center hub** of a Prisma SD-WAN fabric for throughput beyond what ION appliances reach (the playbook quotes ION DC throughput topping out around 15 Gbps and the NGFW target at 50–100 Gbps). The firewall is onboarded in SCM, moved into its own folder, switched into "dc-mode", claimed and assigned to a DC site like an ION, and the controller then orchestrates logical routers (one per VRF), IKE-based IPsec tunnels and BGP toward the branch IONs. Phase 1 covers hubs only; branch convergence is roadmap.

## Internal facts (playbook; all UNVERIFIED against official docs)

- Requirements: PAN-OS **12.1.2**, ION **6.5.2**; supported platform **PA-5440** (PA-5410/5420/5430/5445 and PA-VM lab/POC only); NGFW needs an SD-WAN or Advanced SD-WAN license; SCM-managed only (no Panorama).
- Supported: NGFW as DC device, NGFW HA (active/passive), multi-VRF, direct Internet access. Not supported: fabric auto-VPN (uses IKE IPsec + BGP instead of the native fabric), policy-based routing, DHCP WAN interfaces (static only), sub-interfaces or port channels for circuits, VRF leaks, brownfield PAN-OS SD-WAN coexistence, mixing NGFW and ION in one DC site.
- Workflow: move device to Cloud Managed, new folder, enable Device Scope Configuration, enable the Prisma SD-WAN Integration widget (device reboots, commits `sdwan dc-mode enable yes`), configure LAN/WAN interfaces and zones, push. On the SD-WAN side the firewall appears **Claimed**; create a DC site, assign, set site to Enable; a Global VRF profile orchestrates logical router `prisma-sdwan-global`; custom VRF profiles orchestrate routers named after the VRFs; attach circuits with static IP in the widget and push; tunnels and BGP come up automatically.
- Processes added on PAN-OS: `sdwan_mrl_agent`, `scm`, `cgnxinfra`, `csdwan`, `evg`, `evd`; controller-to-Cloud-Management messaging over GCP Pub/Sub; explicit (UI) vs implicit (controller-triggered, shown as admin `csdwan-controller`) pushes.
- HA: strict active/passive; both nodes identical config; one tunnel per circuit to the active node; pairing needs both Claimed or one Claimed and one Assigned; circuits must match exactly or the secondary must have none; unpair by unassigning one device.
- CLI: `show csdwan site-config`, `show csdwan device-reachability`, `show csdwan standingalarms`, `show cloud-management-status`, `show device-certificate status`, `show system software status | match mrl_agent`, `show vpn flow|ike-sa|ipsec-sa`, `show advanced-routing bgp peer status`, `show advanced-routing route`; ION side `dump vpn summary`, `dump vpn status VpnID=…` (cipher aes-256-cbc shown, encap geneve), `dump routing peer status all`, `dump routing summary`, `dump standingalarms`. Logs `/var/log/pan/sdwan_agents_mrl_agent.log`, `/var/log/pan/ikemgr.log`.
- Alarm codes listed: `SITE_CONNECTIVITY_DOWN`, `SITE_CONNECTIVITY_DEGRADED`, `DEVICESW_ANALYTICS_DISCONNECTED_FROM_CONTROLLER`, `NETWORK_SECUREFABRICLINK_DEGRADED|DOWN`, `NETWORK_DIRECTINTERNET_DOWN`, `NETWORK_VPNLINK_DOWN`, `DEVICEHW_INTERFACE_DOWN`, `PEERING_BGP_DOWN`, `DEVICESW_SYSTEM_BOOT`.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Everything above | UNVERIFIED (internal TSE playbook, 2026-07) | DOC | Confluence 867864901 |
| Converged SD-WAN exists as a shipped capability | INFERRED from a mature v44 support playbook with CLI output; no official document in the KB | DOC | KG-045 |

## Open questions

- KG-045 (existing): shipped status and public documentation of Converged SD-WAN; search docs.paloaltonetworks.com under D2 for "Prisma SD-WAN integration" in the PAN-OS 12.1 / SCM NGFW guides.
