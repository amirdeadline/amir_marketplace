---
name: amir-aws-aws-cli-safety
description: >-
  Safe aws CLI usage: preflight identity, confirm mutations, never store keys in files.
---

# aws-cli-safety

1. Always run `aws sts get-caller-identity` first.
2. Reads (describe/list/get) free.
3. Mutations: print exact CLI and confirm.
4. Prefer least-privilege profile. Never write keys to files.
