---
name: create-project-doc
description: >-
  Creates a complete, accurate, navigable documentation hub by inspecting all
  Markdown files and repository structure, then writing root-level project.md
  as the main entry point for humans and AI agents. Use when the user invokes
  /create_ai_doc, asks to create project.md, or requests an AI documentation
  navigation hub for the current project.
disable-model-invocation: true
---

# Skill: create_ai_doc

## Purpose

Create a complete, accurate, navigable documentation system for the current project.

The skill must inspect all Markdown files in the repository, understand the project from the available documentation and source structure, and create a root-level file named:

`project.md`

`project.md` must become the main documentation entry point for both humans and AI agents.

---

## Invocation

```text
/create_ai_doc
```

Optional goal or additional instruction:

```text
/create_ai_doc {additional_instructions}
```

Example:

```text
/create_ai_doc Create a concise project documentation hub optimized for AI coding agents.
```

---

## Primary Goal

Review all Markdown files in the repository and create:

```text
<project-root>/project.md
```

The generated `project.md` must:

1. Explain what the project is.
2. Explain the project architecture and major components.
3. Explain how the project works.
4. Explain how to install, configure, run, test, and maintain it.
5. Link to every relevant Markdown file using correct relative paths.
6. Organize the documentation into logical categories.
7. Identify the authoritative source for each topic.
8. Help AI agents determine which documents to read for a specific task.
9. Avoid duplicating entire documents unnecessarily.
10. Clearly identify missing, conflicting, outdated, or incomplete documentation.

---

## Mandatory Behavior

### 1. Locate the Project Root

Determine the project root using repository indicators such as:

```text
.git/
package.json
pyproject.toml
Cargo.toml
go.mod
pom.xml
build.gradle
Makefile
docker-compose.yml
README.md
```

Create `project.md` only in the resolved project root.

Do not create duplicate `project.md` files in subdirectories.

---

### 2. Discover All Markdown Files

Recursively find all files matching:

```text
*.md
*.markdown
```

Include Markdown files in directories such as:

```text
docs/
documentation/
.ai/
.github/
architecture/
design/
tests/
deploy/
operations/
security/
```

Exclude files that are clearly generated, third-party, temporary, or dependency-owned unless they contain project-specific information.

Common exclusions include:

```text
node_modules/
vendor/
dist/
build/
coverage/
.venv/
venv/
.git/
.cache/
tmp/
temp/
generated/
```

Do not exclude a directory only because of its name. Confirm that its contents are generated or external before ignoring it.

---

### 3. Read and Classify Every Relevant Markdown File

For every relevant Markdown file, determine:

* Purpose
* Scope
* Main topics
* Whether it is current
* Whether it is authoritative
* Whether it duplicates another file
* Whether it conflicts with another file
* Whether it contains decisions, requirements, instructions, status, risks, or historical information
* Which other documents it relates to
* Whether humans, developers, operators, QA agents, security agents, or AI agents should read it

Classify files into categories such as:

```text
Overview
Requirements
Architecture
Design
Development
Configuration
API
Deployment
Operations
Testing
Security
AI Agent Instructions
Tasks and Status
Decisions
Risks
Troubleshooting
Historical or Archived Documentation
```

Create additional categories when necessary.

---

### 4. Inspect the Repository Structure

Do not rely only on Markdown files.

Inspect the repository structure and important project files to verify documentation claims.

Review relevant files such as:

```text
package manifests
dependency files
build files
entry points
configuration files
container files
CI/CD files
test directories
source directories
infrastructure files
database schemas
API definitions
```

Use this inspection to understand:

* Project language and framework
* Main applications and services
* Entry points
* Runtime dependencies
* Build process
* Test process
* Deployment method
* Configuration model
* Major components
* Important integrations

Do not perform a full source-code audit unless required to accurately explain the project.

---

### 5. Create `project.md`

Create or replace:

```text
<project-root>/project.md
```

The file must use this general structure, adapted to the actual project:

```markdown
# Project Name

> Main documentation and navigation hub for this repository.

## Project Summary

A concise explanation of:

- What the project does
- Why it exists
- Who or what uses it
- Its major capabilities
- Its current state

## Project Goals

- Business goals
- Technical goals
- Explicit non-goals
- Important constraints

## System Overview

Explain the system at a high level.

Include links to detailed architecture and design documents.

## Architecture

Summarize:

- Main components
- Service boundaries
- Data flow
- External dependencies
- Deployment topology
- Important technical decisions

Related documentation:

- [Architecture document](./docs/architecture.md)
- [Design decisions](./docs/decisions.md)

## Repository Structure

Explain important directories and files.

```text
src/
tests/
docs/
config/
deploy/
```

## Getting Started

Summarize:

* Prerequisites
* Installation
* Configuration
* Local execution
* Common commands

Link to detailed setup documents.

## Configuration

Explain the configuration model and link to relevant files.

## Development Workflow

Explain:

* Branch or contribution process
* Build commands
* Coding standards
* Local development workflow

## Testing and Quality Assurance

Explain:

* Test types
* Test commands
* Acceptance criteria
* QA workflow
* Known limitations

## Deployment and Operations

Explain:

* Deployment process
* Environments
* Monitoring
* Logging
* Recovery
* Operational procedures

## Security

Explain:

* Authentication and authorization
* Secrets handling
* Security assumptions
* Threat model
* Security-related documents

## AI Agent Documentation

Explain which files AI agents must read.

### Always Read

* [Project documentation hub](./project.md)
* [Current project status](./.ai/status.md)
* [Task registry](./.ai/tasks.md)
* [Agent rules](./.ai/rules.md)

### Read for Architecture Work

* Relevant architecture and design links

### Read for Development Work

* Relevant implementation, standards, and task links

### Read for QA Work

* Relevant testing and acceptance-criteria links

### Read for Security Work

* Relevant security and threat-model links

## Documentation Index

### Overview

* [README](./README.md) — description

### Architecture and Design

* [Architecture](./docs/architecture.md) — description

### Development

* [Development Guide](./docs/development.md) — description

### Testing

* [Testing Guide](./docs/testing.md) — description

### Operations

* [Deployment Guide](./docs/deployment.md) — description

### AI Agent Files

* [Current Status](./.ai/status.md) — description
* [Task Registry](./.ai/tasks.md) — description

Continue until every relevant Markdown file is included.

## Documentation Authority Map

| Topic            | Authoritative File     | Supporting Files        |
| ---------------- | ---------------------- | ----------------------- |
| Project overview | `project.md`           | `README.md`             |
| Architecture     | `docs/architecture.md` | Related design files    |
| Current status   | `.ai/status.md`         | `.ai/tasks.md`           |
| Testing          | `docs/testing.md`      | Test-specific documents |

## Known Documentation Gaps

List missing or incomplete documentation.

## Documentation Conflicts

List contradictions or ambiguous instructions.

## Maintenance Rules

Explain how future contributors and AI agents must maintain documentation.

## Last Documentation Review

* Date:
* Reviewed scope:
* Files reviewed:
* Main findings:

````

The exact headings may change when necessary, but the resulting file must remain structured and easy to navigate.

---

### 6. Link Every Relevant Markdown File

Every relevant Markdown file must appear in the documentation index.

Use relative Markdown links.

Examples:

```markdown
[Architecture](./docs/architecture.md)
[QA Process](./.ai/qa/process.md)
[API Reference](./docs/api/reference.md)
```

For filenames containing spaces or special characters, use valid URL encoding when required.

Example:

```markdown
[System Design](./docs/System%20Design.md)
```

Verify that every link resolves from the root-level `project.md`.

Do not invent links to files that do not exist.

---

### 7. Add Useful Descriptions

Do not create a bare list of filenames.

Each link must include a short explanation.

Bad:

```markdown
- [architecture.md](./docs/architecture.md)
```

Good:

```markdown
- [System Architecture](./docs/architecture.md) — Describes service boundaries, major components, network flow, and external integrations.
```

Descriptions must reflect the actual file contents.

---

### 8. Detect Documentation Problems

Identify:

* Broken Markdown links
* Missing linked files
* Duplicate documents
* Conflicting instructions
* Multiple files claiming to be authoritative
* Outdated references
* Empty documents
* Placeholder documents
* Documents that no longer match the repository structure
* Missing setup instructions
* Missing test instructions
* Missing deployment instructions
* Missing architecture documentation
* Missing ownership information
* Missing AI-agent context-routing instructions

Record problems in `project.md` under:

```markdown
## Known Documentation Gaps
```

and:

```markdown
## Documentation Conflicts
```

Do not silently invent missing facts.

---

### 9. Preserve Existing Documentation

This skill primarily creates the documentation hub.

Do not rewrite all existing Markdown files unless a minimal correction is required to create valid navigation.

Allowed minimal changes include:

* Fixing an obviously broken relative link
* Adding a link back to `project.md`
* Correcting a filename reference
* Adding missing navigation metadata

Do not remove substantial content.

Do not archive documents.

Do not change technical decisions.

Use `/improve_ai_doc` for broad documentation cleanup and rewriting.

---

### 10. Add Navigation Back to `project.md`

Where safe and useful, add a small navigation line near the top of project-owned Markdown files:

```markdown
[← Project Documentation](../project.md)
```

Calculate the correct relative path for each file.

Examples:

```markdown
[← Project Documentation](../project.md)
```


```markdown
[← Project Documentation](../../project.md)
```

Do not add navigation to:

* Third-party documentation
* Generated files
* Vendored files
* Changelogs where modification is inappropriate
* Files whose required format would be broken

---

### 11. Create an Agent Context Map

Inside `project.md`, include a context-routing section that tells agents what to read.

At minimum:

```markdown
## AI Agent Context Routing

### Before Any Task

1. Read `project.md`.
2. Read the current task definition.
3. Read the current status.
4. Read the documents listed for the task type.
5. Do not assume that linked files were automatically loaded.

### Architecture Tasks

Read:
- Requirements
- Architecture
- Design decisions
- Risks

### Development Tasks

Read:
- Active task
- Architecture
- Coding standards
- Relevant component documentation
- Acceptance criteria

### QA Tasks

Read:
- Active task
- Acceptance criteria
- Testing strategy
- Known risks
- Relevant implementation documentation

### Documentation Tasks

Read:
- `project.md`
- All affected documents
- Source files needed to verify claims
```

Adapt links to files that actually exist.

---

### 12. Validate the Result

Before completing:

* Confirm `project.md` exists in the root.
* Confirm all relative links are valid.
* Confirm every relevant Markdown file is indexed.
* Confirm no excluded dependency documentation was accidentally included.
* Confirm summaries accurately reflect file contents.
* Confirm documented commands exist in the repository.
* Confirm there are no invented technologies, components, or workflows.
* Confirm the repository tree shown in `project.md` matches reality.
* Confirm the file is readable by humans and useful to AI agents.

---

## Safety and Accuracy Rules

1. Never invent missing project details.
2. Never claim a command works unless it exists or has been verified.
3. Never delete documentation.
4. Never change application behavior.
5. Never modify source code unless explicitly instructed.
6. Never hide documentation conflicts.
7. Clearly mark assumptions.
8. Clearly mark unknowns.
9. Prefer accurate incomplete documentation over complete fictional documentation.
10. If the repository cannot be understood from available evidence, state that directly.

---

## Completion Report

After creating the documentation, report:

```text
CREATE_AI_DOC RESULT

Project root:
project.md path:

Markdown files discovered:
Markdown files included:
Markdown files excluded:

Files modified:
Files created:

Broken links fixed:
Documentation gaps found:
Documentation conflicts found:

Validation:
- project.md in project root: PASS/FAIL
- All indexed links valid: PASS/FAIL
- All relevant Markdown files indexed: PASS/FAIL
- No source code changed: PASS/FAIL
- No unsupported claims added: PASS/FAIL
```

Do not mark the skill complete if `project.md` is missing or contains invalid links.
