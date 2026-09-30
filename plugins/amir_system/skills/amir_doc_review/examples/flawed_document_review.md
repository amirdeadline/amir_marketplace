# Example: Flawed document — single material routing defect

Illustrative partial report when one material inconsistency is validated.

# 1. Executive Assessment

| Field | Value |
| ----- | ----- |
| Technical disposition | Revision required |
| Confirmed defects | 1 |
| Material omissions | 0 |

# 5. Validated Technical Findings

| ID | Severity | Confidence | Classification | Domain | Document Location | Finding | Evidence | Impact | Required Correction |
| -- | -------- | ---------- | -------------- | ------ | ----------------- | ------- | -------- | ------ | ------------------- |
| F-001 | High | High | confirmed_defect | routing | §6.4 vs Table 22 | Section 6.4 states branch advertises `10.40.0.0/16` over both service connections; Table 22 assigns that prefix only to East DC with no route preference or summarization defined. | Internal contradiction: §6.4 narrative vs Table 22 columns Prefix/Site | Ambiguous active-path design may yield asymmetric routing on failure | State single intended origin, preference/MED/local-pref behavior, and summarization rules; align table and narrative |

# 9. Optional Improvements

*(none — do not pad)*

# 12. Final Decision

Required: correct F-001 before implementation. Re-review recommended for routing / HA
sections only after correction.
