---
description: Aside question via Cursor native Side Chat — redirects to /btw or /side; does not answer in this thread
argument-hint: [question]
disable-model-invocation: true
---

# /amir:btw

Aside question without interrupting the current agent. **Do not answer `$ARGUMENTS` in this thread.**

## Cursor (required path)

Cursor 3.11+ has native **Side Chat**. Use that — amir cannot open it via API.

1. Run one of:
   - `/btw <question>`
   - `/side <question>`
2. Or UI: Plus → Side Chat, or selection → **Ask in Side Chat**.
3. Keep working in this parent chat; the aside stays in the Side Chat transcript.
4. Bring findings back only by **@-mentioning** that Side Chat in this thread (optional).

If the user already pasted a question as `$ARGUMENTS`, repeat it once so they can copy it into `/btw …`, then stop. Do **not** solve the question here.

Honest limit: this command only redirects. It does not spawn a Side Chat and does not guarantee zero host history beyond what Cursor Side Chat provides.

## Claude Code

Refuse. Amir does not register a working `/btw` aside for Claude Code (no true zero-pollution ephemeral session). Tell the user to ask in a normal chat or use Cursor’s native `/btw` / `/side`.

## Codex / other hosts

Refuse in-session answering. Prefer a separate session for isolation. On Cursor, use native `/btw` / `/side` instead.
