# Evidence policy for Prisma SD-WAN answers

Read this when you label claims, resolve conflicting sources, or decide whether to stop and ask.

## 1. Evidence labels

| Label | Use when | Example |
|---|---|---|
| CONFIRMED | An official source (registry rank 1-4: official docs, OpenAPI, release notes, official SDK code) states it. | "Path policy rules are evaluated per application session" with the admin-guide line (SRC-000029). |
| INTERNAL | Only internal material states it (rank 9: Confluence, TSE/SHUB playbooks, PAEE pages, research notes, QA contracts). | A CLI collection step from the PAEE LQM page (SRC-000101). |
| INFERENCE | You reasoned it from evidence, but no source says it directly. Name the evidence it rests on. | "Both circuits probably fail the performance threshold, so the backup path is used" based on the policy definition plus user-supplied loss figures. |
| UNKNOWN | The KB does not answer it, or the answer needs data the user has not given. | Default LQM probe interval when no source states it. |

Rules:
- Label every important technical claim: behavior, defaults, thresholds, limits, commands, API endpoints and fields, GUI paths, licensing, version support, performance numbers, recommendations.
- Background that any network engineer knows (what a BGP session is) needs no label. Prisma SD-WAN behavior always does.
- A Palo Alto recommendation needs a source. Your own engineering advice is INFERENCE and must be worded as advice ("consider", "one option is"), never as a Palo Alto requirement.
- Tenant facts (this branch's policy, circuits, software version) are UNKNOWN until the user supplies them or a supplied export shows them.

## 2. Authority and citation

`kbq.py src <ID>` prints the rank and the label it supports.

- Lower rank is more authoritative for product behavior: 1 official docs, 2 OpenAPI, 3 release notes, 4 official code/SDK, 9 internal, 10 expert inference.
- A rank the registry's `authority_scale` does not define (for example 8): treat as INTERNAL and say the rank is undefined.
- Official PDFs live inside container files (`prisma_sdwan.md`, `prisma_access.md`, `prisma_sase_architecure.md`). Cite the **embedded PDF's own SRC ID** (for example SRC-000029 for the admin guide), not the container's ID (SRC-000002 is rank 9).
- Cite a Confluence page by pageId, title and local path. Cite an unregistered file by its path.
- Some KB documents reference IDs that are not in the registry (for example SRC-000120 to SRC-000151 in the research package, SRC-000153 on the playbooks index). `kbq.py src` reports them as NOT IN REGISTRY. Cite those files by path and mention the registry gap if it matters.
- Confluence `sd_wan` pages are mostly product requirement and design notes. They describe intended behavior that may differ from what shipped. Treat them as INTERNAL and look for official corroboration before stating behavior.
- Internal material is not for customers. Say so when an answer or a customer document relies on it. Never copy credentials, tokens or hostnames from internal playbooks; refer to a credential by name only.

## 3. Freshness

- Check `publication_date`, `last_updated_date`, `retrieved_date`, `document_version` and `superseded_by` with `kbq.py src`.
- The ION CLI reference (SRC-000032) is dated June 2021 (GAP-000012). Before presenting a CLI command for a newer release, look for it in the release notes (SRC-000033..035), the playbooks or PAEE pages.
- Version-specific behavior: state the release it applies to. If the user's release is unknown and behavior differs by release, ask.
- The corpus mirror is a copy. It is not newer than the repo-root original unless `COPY_MANIFEST.jsonl` says so.

## 4. Conflicts

When two sources disagree:
1. Show both, with source, rank and date.
2. Prefer the higher-authority, newer, version-matching source, and say why.
3. If the conflict changes the answer and you cannot resolve it, it is a missing-evidence case (section 5).

Never merge conflicting statements into one smooth sentence.

## 5. Missing evidence: stop and ask

Stop before writing the affected part when information that the task needs:
- is not in the KB,
- is ambiguous or contradicted in the KB,
- depends on an assumption you would have to make,
- needs a value only the user has (version, model, topology, policy, symptom data),
- or cannot be verified well enough for the claim you would make.

Use this format, then wait for the user:

```text
Missing information
1. What is missing: <the exact fact or value>
2. Why it matters: <which conclusion, step or section depends on it>
3. What the KB has: <sources found, with SRC IDs or paths, and what they do say>
4. What is still uncertain: <the specific open point>
5. What I need from you: <the question or decision, with options if useful>
```

You may still deliver the parts that are fully supported, clearly separated from the open item. Do not
fill the gap with plausible text, typical values, or "usually" statements.
