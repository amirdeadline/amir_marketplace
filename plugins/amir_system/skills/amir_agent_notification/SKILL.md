---
name: amir_agent_notification
description: >-
  Synthesize a spoken agent label with neural TTS, save it as a WAV under
  .ai/agents/notifications/, and set it as this Cursor agent's Completion Sound.
  Use for /amir_agent_notification or /amir:amir_agent_notification.
argument-hint: "'<spoken label>'"
disable-model-invocation: true
---

# amir_agent_notification

Create a natural-voice completion chime from a short spoken label, save it in the
**current project**, and point Cursor Completion Sound at that file.

## Invocation

```
/amir_agent_notification 'project one agent two'
/amir:amir_agent_notification 'project one agent two'
```

`$ARGUMENTS` is the spoken phrase. Strip wrapping quotes. If it is empty, ask for the
phrase and stop.

## What this does

1. Speak the phrase with Microsoft neural TTS (`edge-tts`, voice `en-US-AriaNeural`).
2. Write WAV to `<project-root>/.ai/agents/notifications/<filename>.wav`.
3. Filename = the phrase with **all whitespace removed** (and Windows-illegal characters
   stripped). Example: `project one agent two` → `projectoneagenttwo.wav`.
4. Enable Cursor Completion Sound and set
   `cursor.composer.customChimeSoundPath` to that WAV's absolute path.
5. Copy the same file to Cursor's playback cache
   `%APPDATA%/Cursor/User/globalStorage/customSounds/custom-chime.wav` so Preview/playback
   matches the Browse-button behavior.

## Execute (do not describe — run it)

From the current project root (the folder that contains `.ai/`, `.amir/`, or `.git`):

```
python "%USERPROFILE%/.cursor/plugins/local/amir_system/skills/amir_agent_notification/scripts/synthesize.py" --phrase "<phrase>" --project-root "<absolute project root>"
```

If the user-scope junction is what loaded this skill, the same script lives at:

```
python "%USERPROFILE%/.cursor/skills/amir_agent_notification/scripts/synthesize.py" --phrase "<phrase>" --project-root "<absolute project root>"
```

Use whichever path exists. The script needs **network** (Microsoft Edge TTS). It will
install PyPI package **`edge-tts==7.2.8`** with `pip install --user` if it is missing.
Identity: name `edge-tts`, registry PyPI, version `7.2.8`. `ffmpeg` must already be on PATH
(it is, on this machine).

Do not print API keys or secrets. Do not commit the WAV unless the user asks.

## After the script exits

Report, with evidence from the script's JSON stdout:

- Spoken phrase
- WAV absolute path
- Filename
- Whether Cursor settings were updated
- Whether a preview playback was attempted

Tell the user: run this **in the agent chat whose completion should speak that label**.
Cursor Completion Sound is **one global file** for the IDE. This skill sets that file to
this agent's clip, so you hear the words when that agent finishes. A later run in another
agent replaces the global sound with that agent's clip.

## Honest limits

- Cursor has no per-chat Completion Sound API. Parallel agents share whichever WAV was
  applied last.
- Do not invent a per-agent Cursor setting that does not exist.
- TTS quality depends on Microsoft neural voices, not a local robotic SAPI voice.

## Optional flags (only if the user asks)

Pass through to the script:

- `--voice <name>` — default `en-US-AriaNeural`
- `--no-apply` — write the WAV and index only; do not change Cursor settings
- `--no-preview` — skip playing the WAV after generation
