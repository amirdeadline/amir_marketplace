# Labels, evidence types and answer format for amir_prisma_sdwan_sme

Read this the first time you label claims in a session.

## 1. Claim labels (from the research corpus; use them exactly)

| Label | Meaning | How to present |
|---|---|---|
| VERIFIED | Stated by an official Palo Alto Networks source of rank 1–4 (admin guide, release notes, OpenAPI, official SDK or code, reference-architecture guides). | State as product behaviour, with source and date. |
| CORROBORATED | Two independent sources agree, at least one of them official, but no single official line says it outright; or an authored analysis built on official data. | State as product behaviour, say it is corroborated rather than directly documented. |
| INFERRED | Reasoning from labelled evidence; no source says it directly. | Word as advice or expectation ("consider", "expect"), name the evidence it rests on. Never "Palo Alto Networks requires". |
| UNVERIFIED | Only internal material says it (TSE/PAEE playbooks, best-practices guide WS-001, decks, PRDs). | Present as field guidance; say it is internal; never for customer-facing documents without that caveat. |
| CONFLICTED | Sources disagree. | List every value with source and date; never average or pick silently; point to `05_UNRESOLVED_QUESTIONS.md` §E. |
| OBSOLETE | Superseded by a newer source or release. | Mention only to explain older behaviour; name what replaced it. |

Evidence type: **DOC** (documented), **SCENARIO** (worked through on paper in `knowledge/scenarios/`), **LAB** (observed on a tenant or device). Nothing in the corpus is LAB (no lab access); say "unverified on a live tenant" where a note says so.

Mapping to the sibling skill `amir_prisma_sdwan`: VERIFIED ≈ CONFIRMED; UNVERIFIED (internal) ≈ INTERNAL; INFERRED ≈ INFERENCE; an OPEN gap (KG-…) ≈ UNKNOWN. When both skills are loaded, use this skill's six labels and add the sibling's label in brackets only if the user asks for it.

## 2. Standing rules

1. Every Prisma SD-WAN behaviour, default, limit, timer, command, API endpoint or field, menu path, licence statement, release floor and recommendation carries a label and a pointer (note path and/or SRC/WS ID, with page or line where the note gives it).
2. **Numbers** (throughput, timers, limits) always with source and context; CONFLICTED numbers are listed, never averaged (05 §E lists the known ones: vION/5200/9200 throughput, media jitter 40 vs 75 ms, loopback 4 vs 12, path affinity options, Branch Security floor, TACACS+ precedence, `dump spoke ha status` spelling).
3. **SCM navigation** is quoted with its generation and date (knowledge/notes/05-scm/01): "`Configuration > Prisma SD-WAN > ION Devices` (Aug 2025 navigation; the May 2025 Administrator's Guide writes `Workflows > Prisma SD-WAN Setup > Devices`)". Deep links are inferred unless the note says verified.
4. **Negative routing**: PAN-OS SD-WAN material (Oct 2022 branch guides, Panorama SD-WAN plugin), AWS/Azure vendor docs, legacy CloudGenix API for current authentication, Confluence PRDs as shipped behaviour — never used as Prisma SD-WAN evidence.
5. **Tenant facts** (their release, model, policy, circuits, symptoms) come from the user or their data; never assume defaults for them.
6. Internal material may contain hostnames, credentials or customer names: never repeat them; refer to a credential by name only.
7. When a step depends on an OPEN gap, say so with the KG ID and the group in `05_UNRESOLVED_QUESTIONS.md` (A user decision, B lab-only, C public documentation, D local read).

## 3. Missing evidence: stop and ask

Use this format and wait when the task needs something the corpus and the KB do not have, or a value only the user has:

```text
Missing information
1. What is missing: <fact or value>
2. Why it matters: <which conclusion or step depends on it>
3. What the corpus has: <note(s), labels, SRC IDs, and what they do say>
4. What is still uncertain: <the open point; KG ID if registered>
5. What I need from you: <question or decision, with options>
```

Deliver the fully supported parts, clearly separated from the open item. Do not fill the gap with "usually" statements.

## 4. Answer format

1. **Scope** — product (Prisma SD-WAN, cloud-managed unless stated), release and platform if known, management generation if navigation is involved. One line.
2. **Answer** — the reasoning or recommendation, labels inline on important claims: `[VERIFIED — 02-network/08; SRC-000029 pp.370–371]`, `[UNVERIFIED (internal) — 09-datapath/02]`, `[INFERRED]`. Plain words; expand an acronym the first time using the official spelling found in the notes.
3. **What to check or collect next** — only steps a source supports (CLI names from 08-troubleshooting/02, UI paths dated).
4. **Sources** — notes used (path) and the primary sources behind them (SRC/WS IDs with title and rank).
5. **Gaps and questions** — OPEN/PARTIAL/CONFLICTED items touched (KG IDs), anything needed from the user.
6. For design reviews, use the checklist in `knowledge/notes/10-design/05-design-anti-patterns-and-review-checklist.md` and name each anti-pattern row hit, with its label.

Keep simple questions short (Scope + Answer + Sources). Close every message with the user's standard footer when the user profile asks for one (Section / Status / Blockers-Issues / Summary).

## 5. Worked examples

`knowledge/scenarios/S01…S14` show the full chain (situation → question → labelled reasoning → answer → checks → gaps → validation status). Reuse the closest scenario's structure for a new question of the same type; do not copy its conclusions to a different situation.
