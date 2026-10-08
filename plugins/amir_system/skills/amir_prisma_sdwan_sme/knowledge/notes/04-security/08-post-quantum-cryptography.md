# Post-quantum cryptography (PQC) for Prisma SD-WAN: status and design intent

Domain: 4 | Applies to: internal PRDs 344267341 (draft 2024-09), 607981953 (target 6.7.1, 2025-08), 609207049 (target 6.8.1, reviewed 2025-11-25); no official KB document | Status: ROADMAP / INTERNAL ONLY | Last updated: 2026-10-08

## Explanation (plain words)

Nothing in the official May 2025 documentation or the 6.3–6.5 release notes describes post-quantum features for Prisma SD-WAN. The KB holds three internal requirement documents. Their consistent picture: fabric VPN data traffic already uses AES-256 (considered quantum-resistant), so the exposure is the **key material**: the TLS channel from ION to controller that carries shared secrets, the **IKEv2** standard VPNs to Prisma Access and to PAN-OS firewalls, certificates, and SSH. The plan is a hybrid approach: first **RFC 8784 post-quantum pre-shared keys** mixed into IKEv2, then **RFC 9370/9242 hybrid key exchange** with ML-KEM, TLS 1.3 with hybrid KEM for the control channel, and PQC certificates (ML-DSA / SLH-DSA) issued by the SCM-hosted CA.

## Internal design points (PRDs; UNVERIFIED, forward-looking)

- Existing fabric: controller distributes encrypted shared secrets over TLS; IONs derive session keys with HMAC-SHA-512; data plane AES-256; proposed upgrade of the shared-secret payload encryption from AES-128-CBC to AES-256-GCM, interim RSA 2048 to 4096 for MIC/CIC certificates.
- IKEv2: Phase 1 RFC 8784 PPK managed in IPsec profiles by the controller (standard VPNs and Prisma Access tunnels; Prisma Access NPN and PAN-OS must match); Phase 2 RFC 9370 hybrid KEM with fallback to classical when the peer lacks PQC.
- Control plane: TLS 1.2 to TLS 1.3 with hybrid KEM (draft-ietf-tls-hybrid-design); crypto-agility by remote library updates; PQC CIC via SCEP for IONs on 6.8.1+ ("Thermite" certificates).
- Operations: UI state per tunnel (Active-PPK / Active-Hybrid KEM / Inactive / Legacy), alerts on PQC negotiation failure, logging of algorithms, ≤10% performance impact target, no extra license.
- Target releases moved from TBC (2024) to 6.7.1 (Aug 2025) to 6.8.1 (Nov 2025 review).

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Current fabric uses AES-256 data plane and controller-distributed secrets over TLS 1.2 | CORROBORATED (PRD statements agree with note 01-fundamentals/01 official MIC/CIC chain and 02-network/05 ciphers) | DOC | Confluence 607981953, 609207049 |
| All PQC features (PPK, hybrid KEM, TLS 1.3, PQC certs) | UNVERIFIED roadmap; must never be presented as shipped | DOC | Confluence 344267341, 607981953, 609207049 |

## Open questions

- KG-101: shipped PQC capability in ION 6.7/6.8 (public release notes under D2); until confirmed the skill must answer "not documented as available".

## Addendum 2026-10-08 (B17 finding, supersedes "roadmap" wording above)

Post-quantum cryptography **shipped in ION 6.8.1** (official 6.8 features page, cached `c269c51d0b2c`; note 07-operations/04): RFC 8784 post-quantum pre-shared keys (PPK) for IKEv2, RFC 9370/9242 hybrid key exchange with ML-KEM, and TLS 1.3 hybrid groups for controller connections. Treat earlier statements in this note that describe PQC as planned as OBSOLETE. KG-101 CLOSED. Label: VERIFIED (official feature page); configuration details and limits still to be read (D2).
