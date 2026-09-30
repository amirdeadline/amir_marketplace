# amir_humanized — full rules

These rules are binding. The skill uses a **minimum-change** approach.
Technical meaning has higher priority than humanization.

## Core editing principle

Before changing any sentence, ask:

`Does this already sound like something an experienced human engineer would naturally write?`

If yes:

**Leave it unchanged.**

Change text only when there is a meaningful improvement in:

* Naturalness
* Readability
* Clarity
* Conciseness
* Technical-documentation quality

Do not rewrite sentences merely to create differences from the source.

Do not optimize for the maximum number of edits.

Optimize for the **smallest number of justified edits**.

## Remove em dashes from normal prose

Do not use this character in normal prose:

`—`

Rewrite the sentence naturally.

Possible alternatives include:

* Periods
* Commas
* Parentheses
* Colons when appropriate
* Splitting the sentence

Do not mechanically perform:

`—` -> `,`

Instead, understand the sentence and rewrite it naturally.

Example:

Avoid:

`The controller provides this information — including site status, alarms, and path health — through the monitoring interface.`

Prefer a natural construction such as:

`The controller provides this information through the monitoring interface, including site status, alarms, and path health.`

However, do not alter an em dash when it is part of immutable technical content such as:

* Code
* CLI output
* Literal strings
* API responses
* Configuration
* URLs
* Product-generated output

After editing, search the final document for `—`.

There should be **zero em dashes in normal prose**.

If any remain in normal prose, rewrite those sentences.

Do not modify occurrences inside immutable technical content.

The report must state the final count of em dashes remaining in normal prose.

Expected result:

`Em dashes remaining in normal prose: 0`

## Remove common AI writing patterns

Actively detect wording that commonly makes technical documentation sound AI-generated.

Examples include:

`It is important to note that...`

`It is worth noting that...`

`It should be noted that...`

`This ensures that...`

`This allows you to...`

`In this section, we will explore...`

`In this section, we will discuss...`

`The following section provides...`

`This comprehensive approach...`

`This robust solution...`

`This seamless process...`

`By leveraging...`

`In order to...`

`When it comes to...`

Do not blindly delete these phrases.

Rewrite the sentence naturally while preserving its meaning.

Example:

Avoid:

`It is important to note that the device must be online before proceeding.`

Prefer:

`The device must be online before proceeding.`

## Avoid artificial contrast patterns

Reduce AI-style constructions such as:

`This is not just X, but Y.`

`Rather than simply doing X, this enables Y.`

`Not only does this provide X, but it also provides Y.`

`While X is important, Y is equally important.`

Use these structures only when the contrast itself is meaningful.

Otherwise, state the information directly.

## Reduce unnecessary filler

Remove adjectives and adverbs that add no technical value.

Examples include:

* robust
* comprehensive
* seamless
* powerful
* sophisticated
* critical
* crucial
* essential
* streamlined
* holistic
* effectively
* efficiently
* significantly
* extremely

These words are not completely prohibited.

Keep them when they communicate meaningful technical information.

Avoid:

`This provides a robust and comprehensive approach to efficiently troubleshooting connectivity issues.`

Prefer:

`Use this workflow to troubleshoot connectivity issues.`

## Avoid excessive colon usage

Do not structure every explanation using colons.

Avoid repetitive constructions such as:

`The goal is simple: identify the issue and resolve it.`

When more natural:

`The goal is to identify the issue and resolve it.`

Colons remain appropriate for:

* Headings
* Labels
* Definitions
* Tables
* Technical syntax
* Commands
* Lists where a colon is grammatically appropriate

Do not remove valid colons simply to satisfy this rule.

## Use direct engineering language

Write like an experienced engineer explaining a procedure to another engineer.

Prefer:

`Check the site status before troubleshooting.`

Instead of:

`Before proceeding with the troubleshooting workflow, administrators should first verify the operational status of the affected site.`

Prefer direct verbs such as:

* Check
* Verify
* Open
* Select
* Review
* Confirm
* Run
* Compare
* Configure
* Validate
* Troubleshoot
* Monitor
* Identify
* Test

Do not make simple actions sound academic or corporate.

## Avoid unnecessary formality

Do not use complicated language when a simpler technical sentence communicates the same information.

Avoid:

`Administrators are advised to utilize the monitoring functionality to facilitate identification of potential connectivity-related conditions.`

Prefer:

`Use the monitoring tools to identify connectivity issues.`

Simple does not mean casual.

Keep the documentation professional.

## Do not make the document conversational

Do not add:

* Jokes
* Casual commentary
* Personal opinions
* Marketing language
* Sales language
* Fake quotations
* Unnecessary analogies
* First-person commentary
* AI disclaimers
* Emotional language

Do not write things such as:

`Let's take a look at...`

`Now let's dive into...`

`As you can see...`

`You might be wondering...`

`Luckily...`

`The good news is...`

Use direct technical language.

## Avoid repetitive section introductions

Do not automatically begin sections with:

`In this section...`

`This section will...`

`The following section...`

`This chapter provides...`

If the heading already explains the topic, start with useful information.

Keep an introductory sentence when it provides context that the heading alone does not provide.

## Avoid repetitive conclusions

Do not end every section with a summary that simply repeats the section.

Keep summaries when they provide operational value or help connect one workflow to another.

Remove unnecessary AI-generated wrap-up paragraphs.

## Avoid excessive bullet lists

Do not convert normal explanatory prose into bullets merely to make the document look organized.

Use bullets when the information naturally represents:

* Requirements
* Options
* Checks
* Procedures
* Troubleshooting items
* Prerequisites
* Multiple distinct concepts

Use normal paragraphs for explanatory material.

Preserve existing lists when they already make sense.

## Avoid repetitive sentence structures

AI-generated content often contains several consecutive sentences or bullets using nearly identical grammatical structures.

Example:

`The dashboard provides...`

`The dashboard allows...`

`The dashboard enables...`

`The dashboard helps...`

Rewrite only when this repetition makes the document sound unnatural.

Do not introduce artificial sentence variation when the existing structure is useful.

## Preserve technical meaning

This requirement has higher priority than humanization.

Never change technical meaning simply to improve writing style.

Do not modify technical content unless the user explicitly requests technical corrections.

Preserve:

* CLI commands
* Code
* API endpoints
* API requests
* API responses
* JSON
* YAML
* XML
* Terraform
* Python
* PowerShell
* Bash
* PAN-OS commands
* Prisma SD-WAN commands
* Configuration snippets
* IP addresses
* IPv6 addresses
* Prefix lengths
* Subnet masks
* Ports
* Protocol names
* URLs
* Filenames
* Paths
* Object names
* Variable names
* Environment variables
* Configuration values
* Error messages
* Log messages
* UI labels
* Product names
* Feature names
* Version numbers
* IDs
* UUIDs
* Examples containing literal values

## Do not humanize code

Treat the following as immutable unless explicitly instructed otherwise:

* Fenced code blocks
* Preformatted text
* CLI commands
* Configuration blocks
* Scripts
* API payloads
* JSON
* YAML
* XML
* Terraform
* Command output
* Log output
* Error output

Do not fix spelling, capitalization, punctuation, spacing, or grammar inside technical content merely because it appears unusual.

It may be syntactically significant.

## Potential technical errors

Humanization and technical correction are separate tasks.

If you encounter something that appears technically incorrect:

**Do not silently fix it.**

Preserve the original technical content.

Record it in the report as:

`Potential technical issue detected but not modified.`

Include enough context to identify the location.

Do not claim something is technically incorrect unless there is sufficient evidence.

## DOCX formatting preservation

For `.docx` files, preserve the original document structure and formatting as much as technically possible.

Preserve:

* Heading hierarchy
* Heading styles
* Paragraph styles
* Font formatting
* Bold
* Italics
* Underlining
* Numbered lists
* Bullet lists
* Tables
* Table formatting
* Hyperlinks
* Page breaks
* Section breaks
* Headers
* Footers
* Captions
* Cross-references where possible
* Images
* Screenshots
* Diagrams
* Embedded objects where possible

Do not flatten the DOCX into plain text and rebuild the entire document unless there is no safe alternative.

Prefer editing existing paragraph/run content while retaining the original document structure.

## Images and embedded content

Do not modify:

* Images
* Screenshots
* Diagrams
* Charts
* Embedded files
* Embedded objects

unless modification is required simply to preserve them during document processing.

Humanization applies to human-readable document prose, not graphical assets.

## Tables

Review normal explanatory prose inside table cells.

Humanize it when appropriate.

Do not modify literal technical values such as:

* Commands
* Configuration values
* IP addresses
* API fields
* Object names
* UI labels
* Product names
* Error messages
* Structured data

Preserve:

* Rows
* Columns
* Cell relationships
* Table order
* Table formatting as much as possible

## Headings

Headings may be humanized when they are clearly:

* AI-generated sounding
* Unnecessarily verbose
* Awkward
* Difficult to understand

Do not change headings merely to create stylistic consistency.

Preserve:

* Section numbers
* Heading hierarchy
* Technical terminology
* Product terminology

## Grammar

Correct genuine grammar problems when doing so does not alter technical meaning.

Do not overcorrect technical writing into academic English.

The target is clear professional engineering documentation.

## Preserve author intent

Do not change:

* Conclusions
* Recommendations
* Requirements
* Warnings
* Severity
* Technical intent
* Operational sequence
* Procedure order
* Scope
* Meaning

Humanization is a language-quality operation, not a content-redesign operation.

## No hallucination

Never add technical facts that were not present in the source merely because they would make a paragraph sound more complete.

Do not invent:

* Product capabilities
* Requirements
* Limitations
* Commands
* API behavior
* Best practices
* Prerequisites
* Troubleshooting procedures
* Explanations

If something appears incomplete, preserve it unless correcting completeness is explicitly part of the user's request.

## First-pass workflow

For each document:

1. Validate the input.
2. Detect the project root.
3. Determine the output document path.
4. Determine the report path.
5. Load the document while preserving structure.
6. Identify editable human-readable prose.
7. Identify immutable technical content.
8. Review each editable paragraph or text block.
9. Leave good human-written content unchanged.
10. Rewrite only text that materially benefits from humanization.
11. Save the humanized document as a new file.
12. Perform a validation pass.
13. Compare source and output.
14. Generate the report.

## Mandatory second-pass validation

After humanization, perform a separate quality-control pass.

Check for:

* Changed technical meaning
* Modified commands
* Modified configuration
* Modified code
* Corrupted URLs
* Changed IP addresses
* Changed ports
* Changed filenames
* Changed object names
* Changed product terminology
* Changed UI labels
* Broken numbering
* Broken bullets
* Missing sections
* Missing paragraphs
* Duplicated paragraphs
* Missing tables
* Damaged tables
* Missing images
* Formatting damage
* Accidental removal of technical details
* New unsupported technical statements
* Unnatural sentences introduced during humanization

If a humanization change introduces a problem, correct or revert that change before producing the final output.

## Source-to-output integrity comparison

Before finalizing, compare the original and humanized versions logically.

Confirm that:

* No sections disappeared.
* No paragraphs were accidentally removed.
* No technical procedures disappeared.
* No procedure order changed.
* No commands changed.
* No code changed.
* No API examples changed.
* No technical values changed.
* No URLs changed.
* No images disappeared.
* No tables disappeared.
* Heading hierarchy remains valid.
* Numbering remains valid.
* Technical meaning remains unchanged.

Human-readable prose is expected to differ where humanization was justified.

## Mandatory report

Every invocation must generate a Markdown report.

Location:

`<PROJECT_ROOT>/.ai/reports/<filename>_humanized_report.md`

Create `.ai/reports/` automatically if necessary.

The report should be concise and useful.

Do not generate a huge sentence-by-sentence diff unless specifically requested.

Use `report_template.md`.

Only list changes that were actually made.

If no potential technical issues were found:

`None observed during the humanization pass.`

If there are no warnings:

`No technical-integrity issues detected.`
