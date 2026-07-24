---
description: Route a Prisma SASE/SCM question to the right skill via the corpus index.
---

> **Component gate (amir_project):** before doing anything else, read `.amir/project.yaml` at the project root and verify that `plugins.amir_project.components` includes `"prisma"`. If the manifest is missing or `"prisma"` is not listed, STOP — do not execute this command — and tell the user to enable the `prisma` component via `/amir:configure_project`.

# /amir:prisma_ask

Answer `$ARGUMENTS` using prisma skills.

## Instructions

1. Parse the question; consult skill `references/index.json` files under
   `${CLAUDE_PLUGIN_ROOT}/skills/prisma_*/references/` to pick the best domain skill(s).
2. Prefer live corpus at `PRISMA_DOCS_PATH` (read env var `PRISMA_DOCS_PATH`; machine-specific default documented in the amir_project plugin README, section "Prisma docs corpus"); if missing, state baked-layer fallback.
3. Follow the selected skill's honesty rules (VERIFIED / INFERRED / ASSUMED).
4. Do not invent limits or UI paths.
