#!/usr/bin/env python3
"""Synthesize a neural TTS WAV and optionally set it as Cursor Completion Sound."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

EDGE_TTS_SPEC = "edge-tts==7.2.8"
DEFAULT_VOICE = "en-US-AriaNeural"
UNSAFE_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def filename_from_phrase(phrase: str) -> str:
    cleaned = phrase.strip().strip("'\"")
    cleaned = re.sub(r"\s+", "", cleaned)
    cleaned = UNSAFE_CHARS.sub("", cleaned)
    if not cleaned:
        raise ValueError("phrase produced an empty filename")
    return f"{cleaned}.wav"


def find_project_root(explicit: str | None) -> Path:
    if explicit:
        root = Path(explicit).expanduser().resolve()
        if not root.is_dir():
            raise FileNotFoundError(f"project root is not a directory: {root}")
        return root
    start = Path.cwd().resolve()
    for candidate in [start, *start.parents]:
        if any((candidate / marker).exists() for marker in (".ai", ".amir", ".git")):
            return candidate
    return start


def ensure_edge_tts() -> None:
    try:
        import edge_tts  # noqa: F401
        return
    except ImportError:
        pass
    cmd = [sys.executable, "-m", "pip", "install", "--user", EDGE_TTS_SPEC]
    subprocess.check_call(cmd)
    import edge_tts  # noqa: F401


def find_ffmpeg() -> str:
    found = shutil.which("ffmpeg")
    if not found:
        raise FileNotFoundError("ffmpeg is not on PATH; required to write PCM WAV")
    return found


def synthesize_mp3(phrase: str, mp3_path: Path, voice: str) -> None:
    import asyncio

    import edge_tts

    async def _run() -> None:
        communicate = edge_tts.Communicate(phrase, voice, rate="-8%")
        await communicate.save(str(mp3_path))

    asyncio.run(_run())
    if not mp3_path.is_file() or mp3_path.stat().st_size < 64:
        raise RuntimeError("TTS produced an empty or missing MP3")


def mp3_to_wav(ffmpeg: str, mp3_path: Path, wav_path: Path) -> None:
    cmd = [
        ffmpeg,
        "-y",
        "-i",
        str(mp3_path),
        "-acodec",
        "pcm_s16le",
        "-ar",
        "44100",
        "-ac",
        "1",
        str(wav_path),
    ]
    subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not wav_path.is_file() or wav_path.stat().st_size < 128:
        raise RuntimeError("ffmpeg did not write a WAV file")


def load_json_object(path: Path) -> dict:
    text = path.read_text(encoding="utf-8-sig")
    return json.loads(text)


def dump_json_object(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=4) + "\n", encoding="utf-8")


def cursor_settings_path() -> Path:
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise RuntimeError("APPDATA is not set")
    return Path(appdata) / "Cursor" / "User" / "settings.json"


def cursor_custom_sound_cache(suffix: str) -> Path:
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise RuntimeError("APPDATA is not set")
    folder = Path(appdata) / "Cursor" / "User" / "globalStorage" / "customSounds"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / f"custom-chime.{suffix.lstrip('.')}"


def apply_cursor_completion_sound(wav_path: Path) -> dict:
    settings_file = cursor_settings_path()
    settings: dict = {}
    created = False
    if settings_file.is_file():
        settings = load_json_object(settings_file)
        if not isinstance(settings, dict):
            raise RuntimeError(f"Cursor settings.json is not an object: {settings_file}")
    else:
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        created = True
    settings["cursor.composer.shouldChimeAfterChatFinishes"] = True
    settings["cursor.composer.customChimeSoundPath"] = str(wav_path)
    dump_json_object(settings_file, settings)
    cache = cursor_custom_sound_cache("wav")
    shutil.copy2(wav_path, cache)
    return {
        "settings_path": str(settings_file),
        "settings_created": created,
        "customChimeSoundPath": str(wav_path),
        "cache_copy": str(cache),
        "shouldChimeAfterChatFinishes": True,
    }


def update_index(index_path: Path, phrase: str, filename: str, wav_path: Path) -> None:
    index: dict
    if index_path.is_file():
        try:
            loaded = json.loads(index_path.read_text(encoding="utf-8"))
            index = loaded if isinstance(loaded, dict) else {}
        except json.JSONDecodeError:
            index = {}
    else:
        index = {}
    sounds = index.get("sounds")
    if not isinstance(sounds, dict):
        sounds = {}
    stem = Path(filename).stem
    sounds[stem] = {
        "phrase": phrase,
        "file": f".ai/agents/notifications/{filename}",
        "absolute": str(wav_path),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    index["sounds"] = sounds
    index["active"] = stem
    dump_json_object(index_path, index)


def preview_wav(wav_path: Path) -> str:
    if os.name == "nt":
        ps = (
            f"$p = New-Object System.Media.SoundPlayer -ArgumentList @('{str(wav_path).replace(chr(39), chr(39)+chr(39))}'); "
            "$p.PlaySync()"
        )
        subprocess.check_call(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps]
        )
        return "windows-soundplayer"
    player = shutil.which("ffplay") or shutil.which("afplay") or shutil.which("aplay")
    if not player:
        return "skipped-no-player"
    if Path(player).name.lower().startswith("ffplay"):
        subprocess.check_call(
            [player, "-nodisp", "-autoexit", "-loglevel", "quiet", str(wav_path)]
        )
    else:
        subprocess.check_call([player, str(wav_path)])
    return player


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phrase", required=True, help="Spoken text for the notification")
    parser.add_argument("--project-root", default=None, help="Project root that contains .ai/")
    parser.add_argument("--voice", default=DEFAULT_VOICE)
    parser.add_argument("--no-apply", action="store_true", help="Do not change Cursor settings")
    parser.add_argument("--no-preview", action="store_true", help="Do not play the WAV")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    phrase = args.phrase.strip().strip("'\"")
    if not phrase:
        print("error: empty phrase", file=sys.stderr)
        return 2
    filename = filename_from_phrase(phrase)
    root = find_project_root(args.project_root)
    out_dir = root / ".ai" / "agents" / "notifications"
    out_dir.mkdir(parents=True, exist_ok=True)
    wav_path = out_dir / filename
    ensure_edge_tts()
    ffmpeg = find_ffmpeg()
    with tempfile.TemporaryDirectory(prefix="amir-agent-notification-") as tmp:
        mp3_path = Path(tmp) / "speech.mp3"
        synthesize_mp3(phrase, mp3_path, args.voice)
        mp3_to_wav(ffmpeg, mp3_path, wav_path)
    index_path = out_dir / "index.json"
    update_index(index_path, phrase, filename, wav_path)
    cursor = None
    if not args.no_apply:
        cursor = apply_cursor_completion_sound(wav_path)
    preview = None
    if not args.no_preview:
        try:
            preview = preview_wav(wav_path)
        except Exception as exc:  # noqa: BLE001 — report, do not hide success
            preview = f"failed: {exc}"
    result = {
        "ok": True,
        "phrase": phrase,
        "filename": filename,
        "wav": str(wav_path),
        "voice": args.voice,
        "tts": EDGE_TTS_SPEC,
        "index": str(index_path),
        "cursor": cursor,
        "preview": preview,
        "note": (
            "Cursor Completion Sound is a single global file. "
            "This run set it to this agent's WAV."
        ),
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(json.dumps({"ok": False, "error": f"command failed: {exc}"}), file=sys.stderr)
        raise SystemExit(1)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        raise SystemExit(1)
