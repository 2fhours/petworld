"""Generate letter-name MP3s (A-Z) for the Alphabet player.

Same neural voice/pitch as word audio (regen_cute_voice.py), slightly slower for clarity.
Run: /workspace/.tts-venv/bin/python gen_letters.py
"""
import asyncio
import subprocess
from pathlib import Path
import edge_tts

VOICE = "en-US-AnaNeural"
RATE = "-5%"
PITCH = "+15Hz"
OUT = Path(__file__).resolve().parent / "audio" / "letters"
OUT.mkdir(parents=True, exist_ok=True)

SAY = {c: c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
SAY.update({"W": "double U", "Z": "zee"})


async def main():
    for letter, text in SAY.items():
        path = OUT / f"{letter.lower()}.mp3"
        raw = path.with_suffix(".raw.mp3")
        await edge_tts.Communicate(text + ".", VOICE, rate=RATE, pitch=PITCH).save(str(raw))
        # Trim trailing silence (keep ~0.12s) and keep small: mono 24kHz 48kbps.
        subprocess.run([
            "ffmpeg", "-v", "error", "-y", "-i", str(raw),
            "-af", "areverse,silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.12,areverse",
            "-ac", "1", "-ar", "24000", "-c:a", "libmp3lame", "-b:a", "48k", str(path),
        ], check=True)
        raw.unlink()
        print(letter, path.stat().st_size)


asyncio.run(main())
