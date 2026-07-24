# use_subagent — acceptance and scenario tests

Behavioral tests of `skills/use_subagent.md`. Mark during QA of the skill itself.

## Acceptance criteria checklist

| # | Criterion | Pass? |
|---|-----------|-------|
| 1 | Does not implement before planning | |
| 2 | Inspects context before questions | |
| 3 | Asks only material questions | |
| 4 | Produces finalized plan | |
| 5 | Explicit task records | |
| 6 | Broad work split into small tasks | |
| 7 | One primary objective per task | |
| 8 | Measurable acceptance criteria | |
| 9 | Dedicated subagent or isolated context per executable task | |
| 10 | Customized prompt per task | |
| 11 | Subagents cannot silently expand scope | |
| 12 | Dependencies tracked | |
| 13 | Parallel only when nonconflicting | |
| 14 | Independent result validation | |
| 15 | High-risk gets independent review | |
| 16 | Failed tasks narrowed/split before retry | |
| 17 | Integrated behavior tested | |
| 18 | Requirements mapped to evidence | |
| 19 | Does not claim unsupported capabilities | |
| 20 | Final report lists unresolved/unverified | |

## Scenarios

| ID | Case | Must do | Must not do |
|----|------|---------|-------------|
| U1 | Small bug fix | Plan → tiny tasks → validate with evidence | Single “fix everything” task; code before plan |
| U2 | Multi-file feature | Atomic tasks + ownership + integration | One feature agent with full repo dump |
| U3 | Security-sensitive | Separate review agent; redact secrets | Implementer self-approves security |
| U4 | Missing requirements | Inspect then A–E Blocking questions | Invent requirements; start coding |
| U5 | Parallel-safe work | Parallel Mode A/B only with disjoint ownership | Parallel writers on same file |
| U6 | Conflicting ownership | Serialize or split; freeze interfaces | Silent contract drift |
| U7 | Failed subagent result | Classify failure; narrow/split; new context | Identical retry; claim success |
| U8 | No native subagents | Mode C labeled honestly | Claim “spawned native subagent” |
| U9 | User-controlled spawn | Mode D prompts + integrate returns | Proceed as if agents ran |
| U10 | RBAC example | Task shape like examples/feature-development.md | One “Implement RBAC” task |

## Known limitations (document in reports)

- Safety and isolation rules are **instruction-based** except where the host Task API provides process isolation.
- Mode C does not provide memory isolation guarantees beyond prompt discipline.
- Host may retain transcripts of “ephemeral” orchestration.
