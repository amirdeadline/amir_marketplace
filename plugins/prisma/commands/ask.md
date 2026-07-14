---
name: ask
description: Route a Prisma SASE/SCM question to the right skill via the corpus index.
---

# /prisma:ask

Answer `$ARGUMENTS` using prisma skills.

## Instructions

1. Parse the question; consult skill `references/index.json` files under
   `${CLAUDE_PLUGIN_ROOT}/skills/*/references/` to pick the best domain skill(s).
2. Prefer live corpus at `PRISMA_DOCS_PATH` (default
   `E:\PC3_Shared\Palo\Documents\Markdowns Prisma SASE`); if missing, state baked-layer fallback.
3. Follow the selected skill's honesty rules (VERIFIED / INFERRED / ASSUMED).
4. Do not invent limits or UI paths.
