# amir_doc_review — test cases

Structural and behavioral acceptance tests. Execute by following SKILL.md against the
fixtures described (or synthetic mini-documents). Record **completed / failed / skipped**
separately with evidence.

## Structural tests

| ID | Check | Expected |
| -- | ----- | -------- |
| S1 | Skill directory contains SKILL.md, prompts/, schemas/, templates/, examples/, tests/, config/, README.md | All present |
| S2 | Command `commands/amir_doc_review.md` exists | Present |
| S3 | Catalog core component lists `amir_doc_review` in skills and commands | Present |
| S4 | User junctions (when installed): `~/.cursor/skills/amir_doc_review`, `~/.claude/skills/amir_doc_review` | Resolve to plugin skill dir |
| S5 | SKILL frontmatter name equals `amir_doc_review` | Pass |

## Behavioral tests

### Test 1: Excellent HLD

**Input:** Complete consistent HLD at HLD-level detail; correct architecture; clear requirements.  
**Expected:** Approved as written or with optional improvements only; zero fabricated defects;
no demand for LLD-level config; specific strengths listed.

### Test 2: HLD with one material routing defect

**Input:** Same as Test 1 plus intentional prefix vs table contradiction.  
**Expected:** Routing defect identified; reasonable severity; no pad of low-value findings;
evidence-based correction.

### Test 3: LLD with cross-section IP inconsistency

**Input:** Same IP assigned to two sites in different sections/tables.  
**Expected:** One consolidated finding listing all affected locations.

### Test 4: Missing evidence

**Input:** Document without requirements, version, or reachable sources; internet disabled.  
**Expected:** Insufficient evidence disposition; no invented conclusion; evidence needed listed.

### Test 5: Outdated product guidance

**Input:** Design mixing superseded Panorama-managed behavior with SCM features without distinction.  
**Expected:** Conflict explained; current official docs preferred; generations not silently mixed.

### Test 6: Large document

**Input:** Multi-part / multi-chapter document.  
**Expected:** Logical decomposition; separate review units; coverage tracking; synthesis;
no “whole document to every agent” pattern in plan.

### Test 7: Editorial-only defects

**Input:** Technically sound doc with typos.  
**Expected:** Technical disposition approved; typos only in editorial table.

### Test 8: Optional enhancement

**Input:** Technically sound doc where a diagram legend would help but is not required.  
**Expected:** Optional label only; does not affect approval; omit if no real benefit.

## Anti-hallucination spot checks

- [ ] No soft “best practice” required findings without source  
- [ ] Empty technical findings table accepted  
- [ ] Optional and editorial never mixed into section 5 as defects  
- [ ] Incomplete coverage is reported when a unit fails validation retry  

## Results log (fill when run)

| Test | Result | Evidence |
| ---- | ------ | -------- |
| S1–S5 | | |
| T1 | | |
| T2 | | |
| T3 | | |
| T4 | | |
| T5 | | |
| T6 | | |
| T7 | | |
| T8 | | |
