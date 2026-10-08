# Writing style

The reader is an engineer, sometimes junior, often busy. Write so they understand why a section exists
before they meet the details, and so they can act on it without rereading.

## 1. Voice

- Professional, plain, direct. Short sentences when the idea is simple; longer ones only when the logic needs them.
- Present tense and active voice: "The ION measures loss on each path", not "Loss is being measured".
- Address the reader in procedures with imperatives: "Open", "Check", "Select", "Run", "Compare", "Confirm".
- No marketing, no enthusiasm, no first-person commentary, no rhetorical questions, no jokes.

## 2. Remove AI-style writing

Rewrite the sentence rather than deleting a phrase mechanically.

| Avoid | Write instead |
|---|---|
| "It is important to note that the ION drops..." | "The ION drops..." |
| "In this section, we will explore circuit health." | Start with the content. The heading already says it. |
| "This robust, comprehensive solution seamlessly..." | Say what it does, with the specific behavior. |
| "In order to verify..." | "To verify..." |
| "Not only does X do A, but it also does B." | "X does A and B." |
| Em dash used to join two thoughts | A period, a comma, parentheses, or two sentences. |
| A closing paragraph that repeats the section | End when the content ends. |
| "Note:" on every other paragraph | Keep notes for things a reader must not miss. |

`mddoc.py check` flags em dashes and common filler phrases (W101, W102). It cannot judge tone; you must.

## 3. Explain context

For each major topic, give the reader what they need from this list, in this order, and nothing more:

1. What it is.
2. Why it matters operationally.
3. What is being evaluated or configured.
4. How it affects the system (Prisma SD-WAN behavior, with evidence).
5. What to check, and how.
6. How to read the result, and what to do next.

Usually two or three short paragraphs and one table or procedure cover it. Do not create six subsections
per topic.

Example of the order (health check item, Prisma SD-WAN facts come from the evidence register):

> Packet loss on a WAN path reduces application quality and can cause the ION to steer traffic to another
> path. This check compares measured loss on each circuit with the threshold your performance policy uses.
> [procedure] A circuit that stays above the threshold during business hours needs follow-up with the
> carrier; short spikes usually do not. [interpretation sourced or marked as advice]

## 4. Progressive depth

Concept, purpose, operational relevance, technical behavior, validation, interpretation, then
troubleshooting or recommendation. A junior engineer should understand the first paragraph of every
section. Deep detail (internals, packet flow, counters) comes after, never instead. Do not simplify facts
until they become wrong.

## 5. Procedures

- Numbered steps, one action per step, in the order performed.
- State where the action happens (portal page, ION CLI, API) and any prerequisite before step 1.
- Show the expected result after a step when the reader needs to decide what to do next.
- GUI labels in **bold** exactly as shown in the product; commands, paths, fields and values in `code`.
- Commands and API calls in fenced blocks with a language (`text`, `bash`, `json`). Never invent output.

## 6. Recommendations

Separate what Palo Alto Networks documents ("The best practices guide recommends...") from engineering
judgment ("Consider..."). Judgment is INFERENCE in the evidence register and must read as advice.

## 7. Terminology, acronyms, numbers

- Pick one term per concept and keep it (for example "circuit", not "link" in one place and "uplink" in another,
  unless the product UI distinguishes them).
- Use product names exactly: Prisma SD-WAN, Strata Cloud Manager, ION, Prisma Access.
- Define each acronym at first use in body text, spelled out exactly as the official sources spell it. Look
  it up in the evidence; do not expand product acronyms from memory. A glossary appendix helps long
  documents but does not replace first-use definitions. `mddoc.py check` reports undefined acronyms (W105).
- Units with every number (ms, %, Mbps). Thresholds and defaults only with a source.

## 8. Lists, tables, notes

- Explanations are prose. Bullets are for genuinely parallel items. Avoid three-item lists added for rhythm.
- Tables for comparisons, check matrices, parameters and document control. Keep cells short; move long
  explanations into prose under the table.
- Callouts (`> [!NOTE]`, `> [!WARNING]`, `> [!IMPORTANT]`) sparingly: data loss, outage risk, irreversible
  actions, licensing traps.
