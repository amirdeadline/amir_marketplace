# bin/

Optional executable stubs for Claude Code plugin `PATH` augmentation.

**Prefer:** invoke amir CLI directly from the package `tools/` directory:

```bash
node "${CLAUDE_PLUGIN_ROOT}/../../tools/state.js" <project-root> status
node "${CLAUDE_PLUGIN_ROOT}/../../tools/render.js" <project-root> all
node "${CLAUDE_PLUGIN_ROOT}/../../tools/secrets_scan.js" <path>
node "${CLAUDE_PLUGIN_ROOT}/../../tools/cost.js" <project-root>
node "${CLAUDE_PLUGIN_ROOT}/../../tools/doctor.js" <project-root>
node "${CLAUDE_PLUGIN_ROOT}/../../tools/activity.js" <project-root> append
```

Add thin wrapper scripts here only if your team needs shorter command names on `PATH`.
