---
description: Disable Langfuse tracing for this project (trace data preserved by default)
---

# /amir:langfuse_disable

## Gate

Read `.amir/project.yaml`. If the manifest is missing, stop and point to `/amir:configure_project`. May run when already disabled, for cleanup.

## Steps — project integration only

1. Remove or comment out the project's tracing instrumentation only if the user wants code changes; the lighter default is configuration-level disable (unset/ignore the Langfuse env in this project's run configs). Show any code diff before applying and run tests after.
2. Set `project_tools.langfuse.enabled: false` and `mode: disabled` in `.amir/project.yaml` with a dated note ("disabled by langfuse_disable").
3. Data preservation (default):
   - Self-hosted: leave containers and volumes intact; optionally `docker compose down` (without `-v`) to stop them. Volume deletion (`docker compose down -v`) ONLY on explicit user request with a second confirmation — it destroys all trace history.
   - Hosted: data stays in Langfuse Cloud; deletion happens in their UI by the user, not by this command.
   - Local records in `.amir/state/langfuse/` are preserved unless the user opts to delete.
4. Credentials: preserve `%USERPROFILE%\.amir\secrets\langfuse.env` by default (other projects may use it); delete only on explicit yes, and remind the user to revoke/rotate keys in the Langfuse UI if the project is being decommissioned.
5. Report exactly what was stopped, removed, preserved, and the new manifest state.
