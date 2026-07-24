---
description: DEPRECATED alias
---

# /amir:project_doctor (DEPRECATED)

This command is a deprecated alias. Do the following, in order:

1. Print this warning to the user verbatim:

   > WARNING: `/amir:project_doctor` is deprecated and will be removed in amir_project 1.0.
   > Use `/amir:validate_project` instead (provided by the amir_system plugin).

2. Then invoke the replacement: run `/amir:validate_project` with the same arguments
   (`$ARGUMENTS`) and continue there. Do not perform any other work under the
   old name.
