---
description: Neural-TTS spoken label saved as a project WAV and applied as this Cursor agent's Completion Sound
argument-hint: "'<spoken label>'"
disable-model-invocation: true
---

# /amir:amir_agent_notification

Follow the skill at `skills/amir_agent_notification/SKILL.md` in this plugin (also
installed at user scope as `/amir_agent_notification` for Cursor and Claude Code).

Apply that skill now. Treat `$ARGUMENTS` as the spoken phrase (strip wrapping quotes).
Synthesize a natural-voice WAV, save it at `.ai/agents/notifications/<nospaces>.wav`,
and set Cursor Completion Sound (`cursor.composer.customChimeSoundPath`) to that file
for this agent. Report the absolute WAV path.
