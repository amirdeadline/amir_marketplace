# S08 — ZBFW drops an inbound destination-NAT service

Domains: 4 | Evidence type: SCENARIO | Written 2026-10-08

## 1. Situation

Branch ION 3200 (6.5.x) publishes an on-site camera server: a NAT rule maps public IP :443 to 10.130.5.20:443. It worked until the team bound the corporate ZBFW stack (PRIVATE/PUBLIC/VPN zones, explicit allows PRIVATE→PUBLIC and PRIVATE↔VPN). Since then external users cannot connect; `dump nat counters` still increments.

## 2. Question

Why did binding the stack break the published service, and what exactly fixes it?

## 3. Reasoning chain

1. **Default posture before/after binding.** With no stack bound nothing is filtered except unsolicited inbound to a public WAN port, which is always dropped **unless NAT translates it**; once a stack is bound, the built-in Default rule denies all inter-zone traffic not explicitly allowed. [VERIFIED — 04-security/01 (SRC-000029 pp.563–564); UNVERIFIED (internal) for the "nothing filtered without a stack" wording — WS-001]
2. **NAT and ZBFW are separate layers.** NAT zones are distinct from security zones; the DNAT rule (source-zone Internet rule, local prefix with the public /32, port 443, pool = server) translates the packet, after which the ZBFW evaluates **PUBLIC → PRIVATE** for that session; there is no such allow rule, so Default denies silently. Security policy supersedes path/NAT decisions. [VERIFIED — 02-network/11 (SRC-000029 pp.594–598), 04-security/01 (pp.565, 568)]
3. **Rule to add.** Allow rule: source zone PUBLIC, destination zone PRIVATE, destination prefix = the server (local or global security prefix), service TCP/443 or the application (keep app-based and port-based rules in separate rules), action Allow, order above the defaults. Deny is silent (no RST), so clients just time out — consistent with the symptom. [VERIFIED for rule fields/actions — SRC-000029 pp.494–495; UNVERIFIED (internal) for the "DNAT needs a ZBFW rule" best-practice wording and the app/port separation — WS-001]
4. **Return path and policy.** Inbound DNAT also needs a path policy that permits the Direct Internet path for that traffic (internal); the default rules allow Direct on public so this is usually satisfied. [UNVERIFIED (internal, strong) — 02-network/11 WS-001]
5. **Verification.** `dump nat counters`/`dump nat summary` (translation happening), `inspect security policy lookup`, `inspect flow detail` (SEC-ACTION), Monitor Rules hit counts per site, Flow Browser showing the deny. FC trace (support) would show the security lookup per candidate path and the rule hit. [VERIFIED for command names and monitoring — 04-security/01 (pp.488–489, 503–504); UNVERIFIED (internal) for the FC trace — 09-datapath/02]
6. **Common traps.** Zone not bound on the LAN interface (drops everything); site-level and device-level bindings mixed; rule with empty zones (OOM risk on small platforms); SYN EXCEPTION per zone is for asymmetric/long-lived sessions, not for this. [VERIFIED — SRC-000029 pp.496–499; UNVERIFIED (internal) for OOM — WS-001]

## 4. Answer

Binding the stack turned the ZBFW to deny-by-default; the translated inbound session is PUBLIC→PRIVATE and nothing allows it, so the Default rule drops it silently while NAT counters keep rising. Add an Allow rule PUBLIC→PRIVATE for the server prefix on TCP/443 (or the application) above the default set, confirm the zones are bound on the public circuit and the LAN interface, and re-test; Monitor Rules should show hits on the new rule and the flow's SEC-ACTION becomes allow.

## 5. What to check / collect next

Zone bindings per device, the stack's set order, rule hit counters, `inspect flow detail` for an inbound attempt, NAT rule placement (No-NAT rules above the default SNAT). [sources above]

## 6. Gaps exposed

KG-082 (NAT branch-only official text), KG-090 (ZBFW scale limits), KG-132 (official source for the DNAT-needs-ZBFW guidance).

## 7. Validation status

**SCENARIO VALIDATED** — the mechanism follows from VERIFIED default-rule and NAT documentation; the explicit "DNAT needs an allow" sentence is internal but is an inference from VERIFIED behaviour.
