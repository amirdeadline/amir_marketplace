---
description: SASE Lab Expert — troubleshoot any lab, get data on any pod/VM/device/SCM tenant, redo a lab's gold snapshot.
argument-hint: "<task, e.g. 'why is lab7 unreachable' or 'redo gold for lab4'>"
---

> **Component gate (amir_project):** before doing anything else, read `.amir/project.yaml` at the project root and verify that `plugins.amir_project.components` includes `"saselab"`. If the manifest is missing or `"saselab"` is not listed, STOP — do not execute this command — and tell the user to enable the `saselab` component via `/amir:configure_project`.

# /amir:lab_expert

Task: `$ARGUMENTS`

## Instructions

1. Locate the `lab_expert` skill folder (`$LE`), first match wins:
   - `.amir/generated/claude/marketplace/plugins/amir_project/skills/lab_expert/` (rendered into this project)
   - `E:\PC3_Shared\Plugins\amir_marketplace\plugins\amir_project\skills\lab_expert\` (marketplace source)
2. Read `$LE/SKILL.md` completely and follow it as your operating instructions for this task:
   load only the references it routes you to, use its tools, obey its rules.
3. If no task was given, say in two lines what you can do (troubleshoot a lab, answer any
   question about a pod / VM / device / SCM tenant, redo a lab's gold snapshot) and ask for
   the lab and the problem.
