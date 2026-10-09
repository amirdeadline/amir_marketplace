# Curriculum templates and rules for amir_prisma_sdwan_training

## 1. Module record (every module, Basic or Advanced)

| Field | Rule |
|---|---|
| ID | `B<n>` Basic, `A<n>` Advanced |
| Target level | Basic (guided deployment, operations, foundational troubleshooting) or Advanced (independent architecture, automation, deep troubleshooting) |
| Prerequisites | Module IDs that must precede it; general networking knowledge is assumed, never taught |
| Learning objectives | Measurable, verb-first ("configure", "verify with", "diagnose", "justify"); each objective maps to at least one assessment item |
| Topics / subtopics | Product-specific; each topic names the knowledge note(s) it rests on (`knowledge/notes/...`) |
| Hours | Theory / Demo / Lab / Assessment, summing to the module total; breaks are not module time |
| Lab mapping | Blueprint IDs (`L-xx`) and their status (READY / PARTIAL / MISSING / UNVERIFIED) |
| Learner artifacts | What the learner produces (configuration, verification output, design memo, script) |
| Verification | How success is observed (SCM screen, CLI output, API response, flow record) with the source that documents that observation |
| Assessment | Quiz, practical check, rubric reference |
| Version applicability | Release floor and the sources behind it; CONFLICTED floors shown as such |
| References | Note paths and SRC/WS/PUB IDs from the SME knowledge layer |

## 2. Lab exercise blueprint (every `L-xx`)

Objective · Prerequisites · Topology / devices used (names from the lab inventory only) · Existing scenario mapping (Day0 state, scenario id) · **Supported status** · Setup effort (instructor minutes) · Steps outline (not a manual) · Verification · Reset / rollback · Evidence (documents that prove the lab can do this; "UNVERIFIED — not observed live" when only documentation exists) · Duration.

Status enum:

| Status | Meaning |
|---|---|
| READY | Documented as built and as-built configuration exists (Day0 configs, lab guide); no new infrastructure needed |
| PARTIAL | Devices exist but the exercise needs configuration the learner or instructor must build first, or depends on a feature documented as incomplete |
| MISSING | The lab has no device, licence or service for it; recommend an addition only if the value is clear |
| UNVERIFIED | Documentation suggests support but nothing observed; must be checked live before the course runs |

## 3. Time accounting

- Basic: exactly the agreed number of days and scheduled hours (default 5 days, 8 scheduled hours per day = 40 h). Each day shows a contiguous session table `| Start | End | Type | Session | Module | Notes |`; `Type` is one of Theory, Demo, Lab, Assessment, Break, Lunch, Capstone, Review. Contact time = scheduled minus Break/Lunch rows. Run `scripts/check_schedule.py basic <file>`.
- Advanced: hours are estimated per module from depth and lab complexity, never forced to a round number; the module table ends with a `Total` row; run `scripts/check_schedule.py advanced <file>`. Convert to days at the agreed contact hours per day (state the assumption).
- Breaks: 15 min mid-morning, 30–45 min lunch, 15 min mid-afternoon, shown explicitly.

## 4. Evidence and labels

Product claims inside the curriculum carry the SME labels (VERIFIED / CORROBORATED / INFERRED / UNVERIFIED / CONFLICTED / OBSOLETE) and point to notes or sources. Lab claims are either documented (cite the lab file and date) or marked UNVERIFIED. Never state that a lab action worked unless it was observed and the evidence path is given. Credentials, tokens and tenant identifiers from lab documents are never copied into curriculum files.

## 5. Deliverable set (curriculum structure phase)

`00_CURRICULUM_OVERVIEW.md`, `01_BASIC_5_DAY_PLAN.md`, `02_ADVANCED_TRAINING_PATH.md`, `03_LEARNING_OBJECTIVES_MATRIX.md`, `04_LAB_CAPABILITY_MATRIX.md`, `05_LAB_EXERCISE_BLUEPRINTS.md`, `06_ASSESSMENT_AND_CAPSTONES.md`, `07_SOURCES_ASSUMPTIONS_AND_GAPS.md`, `08_IMPLEMENTATION_ROADMAP.md`, `09_REVIEW_QUESTIONS.md`. Cross-link them; use tables; add Mermaid diagrams for sequencing and topology where they help. Stop after this set and ask for approval; full lessons, slides, lab manuals and tests come only after approval.

## 6. Quality gates (run before handing over)

1. Basic schedule validated by the script (days, hours, contiguous sessions, breaks shown).
2. Advanced module hours validated by the script; total and day conversion stated.
3. Every objective appears in the objectives matrix with an assessment.
4. Prerequisite modules precede dependent modules in both sequences.
5. Every blueprint has a status and evidence; no READY without as-built documentation.
6. Advanced adds depth, not repetition: each Advanced module names what Basic already covered and what it adds.
7. Product claims that rest on internal-only or conflicted sources are flagged in `07_SOURCES_ASSUMPTIONS_AND_GAPS.md`.
8. No live environment was changed; no credentials appear in any file.

## 7. Review-question format (`09_REVIEW_QUESTIONS.md`)

One table: `| # | Decision needed | Why it matters | Options (recommended first) | Default if no answer |`. Group by audience, schedule, lab, scope, assessment. These are the only questions the user should receive; do not interrupt during drafting.
