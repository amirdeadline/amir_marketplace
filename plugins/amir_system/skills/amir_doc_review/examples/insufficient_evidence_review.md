# Example: Insufficient evidence

Illustrative outcome when required sources cannot be obtained.

# 1. Executive Assessment

| Field | Value |
| ----- | ----- |
| Technical disposition | Insufficient evidence to assess |
| Confirmed defects | 0 |
| Evidence limitations | Referenced requirements doc REQ-PA-2024 not provided; product version of Prisma Access not stated; internet research disabled |

# 5. Validated Technical Findings

*(empty — do not invent defects due to missing sources)*

# 8. Unverified Risks and Required Questions

| ID | Question or Risk | Why It Matters | Evidence Needed | Responsible Party |
| -- | ---------------- | -------------- | --------------- | ----------------- |
| Q-001 | Target management platform unknown (Panorama-managed vs SCM) | Policy and object models differ; design guidance cannot be validated | Explicit management platform + product release | Document author |
| Q-002 | Missing approved requirements baseline | Cannot judge requirement satisfaction | REQ-PA-2024 or approved substitute | Project |

# 12. Final Decision

No confirmed technical defects asserted. Full technical disposition deferred until Q-001
and Q-002 evidence is supplied. Re-run `amir_doc_review` after materials arrive.
