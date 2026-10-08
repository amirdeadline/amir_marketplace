# S04 — Brownfield migration from a legacy MPLS WAN with regional server rooms (branch-gateway topology)

Domains: 1, 2, 9 | Evidence type: SCENARIO | Written 2026-10-08

## 1. Situation

120 sites on a single-carrier MPLS WAN with Cisco CE routers; two DCs; three regional offices host file/print/AD servers used by nearby branches. Internet already exists at every site but is unused for business traffic. The customer wants to migrate in waves without a flag day and keep MPLS for a year.

## 2. Question

Sequence the migration, decide the topology (DC hubs vs branch gateways), and name the constraints.

## 3. Reasoning chain

1. **Wave 0 — DCs first.** Insert DC IONs off-path with core peers (eBGP, MD5, 1 s/3 s) and, because MPLS must carry fabric tunnels too, an edge peer to the MPLS CE (listen-only). No topology change in the DC. [VERIFIED — 10-design/01 (SRC-000038 pp.51–53), 02-network/08]
2. **Wave 1 — Analytics mode at pilot branches.** ION inline between CE router and LAN switch (fail-to-wire); monitors applications, no policy, no VPN; lets the team replace port-based assumptions with application knowledge before control mode. [VERIFIED — 01-fundamentals/02 (SRC-000029 p.11); UNVERIFIED (internal) for the insertion-model detail — deck]
3. **Wave 2 — Control mode with router interop.** Site switched to Control: fabric VPNs form to both DCs over Internet and over MPLS (same category and WAN network); the CE stays as MPLS handoff; L3 Direct Private WAN Forwarding and L3 LAN Forwarding on; default gateway on the private WAN port or BGP classic peer to the CE. Legacy (not yet migrated) MPLS sites remain reachable over the direct MPLS underlay because the default path set keeps Direct on Any Private and the ZBFW needs PRIVATE↔PRIVATEWAN rules for that transition traffic. [VERIFIED — 10-design/02 (SRC-000037 pp.64, 70, 85–88); 02-network/08]
4. **Regional offices → Branch Gateways.** A branch gateway is a branch that also offers hub services (policy transit, LQM server) to branches in its **domain**; tunnels auto-form within the domain; prerequisites: control mode, both L3 forwarding toggles, no existing branch-to-branch VPNs (deleted), and the conversion reboots the ION; supported models 3200/5200/9200/3000/7000/9000 and virtual (6.4.1+). Create one domain per region and bind the regional branches to it; DCs are reached regardless of domain. [VERIFIED — 02-network/06 (SRC-000029 pp.60–62), 01-fundamentals/06; UNVERIFIED (internal) for "DC targets ignore domains" and classic-peering-only at gateways — TSE playbooks]
5. **Gateway count caution.** With three regional gateways plus two DCs, WS-001 warns of asymmetry/one-way traffic from implicit prefix reflection until the native fix; 6.8.1 adds hop-aware routing, metric 0/30 symmetry and Anynet prefix filters (internal, QA-qualified). On 6.5.x keep gateways to regional hub-and-spoke (branches in a region talk to their own gateway and to the DCs) and use prefix-based path rules if branch↔gateway↔DC chains appear. [UNVERIFIED (internal) — 02-network/06 and addendum; official 6.8.1 release considerations mention branch-gateway prefix filters — 07-operations/04 VERIFIED]
6. **Wave 3 — Router replacement** at Ethernet-only sites once MPLS contracts allow: ION terminates MPLS and Internet directly; classic BGP peer to the PE or default gateway. [VERIFIED — 02-network/08 (SRC-000029 pp.370–371)]
7. **Policy evolution.** Start with the default path set (clone per site type), add DC groups on enterprise-default for transit, then move DIA to Prisma Access or DC backhaul per the security model; advanced stacks chosen once (toggle affects all four policy types). [VERIFIED — 10-design/02 §5]
8. **Constraints to state up front.** Stacked policies are mandatory from 6.0.1 (legacy policy sets block upgrades); Gen-1 hardware ends with 6.5.x, so buy Gen-2 for new sites; each DC ION must be able to carry all branches of its cluster alone; a branch is in exactly one domain and changing it tears down its VPNs (internal). [VERIFIED for stacked policies, Gen-1 lifecycle, capacity — 03-application-traffic/02, 01-fundamentals/05 addendum, 10-design/01; UNVERIFIED (internal) for the domain-change teardown]

## 4. Answer

Order: DC IONs off-path → pilot branches in Analytics → Control mode with the CE kept as MPLS handoff (legacy sites reachable over the MPLS underlay with explicit ZBFW rules) → convert the three regional offices to branch gateways inside regional domains → router replacement at Ethernet-only sites. Keep the gateway topology regional on 6.5.x; revisit full mesh after 6.8.1 is adopted. Buy Gen-2 only.

## 5. What to check / collect next

Current CE routing (BGP vs static), whether the MPLS carrier can carry the branch prefixes needed for direct underlay reach, server-room platforms vs the branch-gateway model list, target release and the Gen-1 inventory, per-site circuit inventory for category planning. [sources as above]

## 6. Gaps exposed

KG-064 (domain semantics, official), KG-077 (6.8.1 full-mesh documentation), KG-072 (switching chapter, if L2 insertion is needed). New: **KG-136** — official guidance on the maximum branch gateways per domain and gateway↔gateway behaviour on 6.5.x.

## 7. Validation status

**SCENARIO PARTIAL** — migration mechanics and prerequisites are VERIFIED; the multi-gateway topology limits depend on internal material.
