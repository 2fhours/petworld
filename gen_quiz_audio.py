"""Generate primary-school textbook-style quiz/read-aloud MP3s for 抽读.
Voice: en-GB-SoniaNeural (clear British classroom), rate -18%.
Writes audio/quiz/<id>.mp3 and sets quizAudio on each words.json item.
Run: /workspace/.tts-venv/bin/python gen_quiz_audio.py
"""
import asyncio
import json
from pathlib import Path
import edge_tts

VOICE = "en-GB-SoniaNeural"
RATE = "-18%"
PITCH = "+0Hz"
CONCURRENCY = 5
RETRIES = 4
BASE = Path(__file__).resolve().parent
AUDIO_DIR = BASE / "audio" / "quiz"
WORDS_PATH = BASE / "words.json"

SPEAK = {
    "w_mum": "mum",
    "w_colour": "colour",
    "w_trousers": "trousers",
}


def speak_text(it: dict) -> str:
    tid = it.get("id") or ""
    text = (it.get("text") or "").strip()
    if tid in SPEAK:
        return SPEAK[tid]
    t = text.rstrip("?!.,")
    if text.lower() in ("hide-and-seek", "move-and-freeze"):
        return text.replace("-", " ")
    if t.lower() in ("hide-and-seek", "move-and-freeze"):
        return t.replace("-", " ")
    return t or text


async def synth_one(sem, it, force=False):
    wid = it["id"]
    out = AUDIO_DIR / f"{wid}.mp3"
    rel = f"audio/quiz/{wid}.mp3"
    if out.exists() and out.stat().st_size > 500 and not force:
        it["quizAudio"] = rel
        return "skip", wid
    text = speak_text(it)
    last_err = None
    async with sem:
        for attempt in range(RETRIES):
            try:
                communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH)
                await communicate.save(str(out))
                if not out.exists() or out.stat().st_size < 200:
                    raise RuntimeError("empty audio")
                it["quizAudio"] = rel
                return "ok", wid
            except Exception as e:
                last_err = e
                if out.exists():
                    try:
                        out.unlink()
                    except OSError:
                        pass
                await asyncio.sleep(0.6 * (attempt + 1))
        it.pop("quizAudio", None)
        return "fail", f"{wid}: {last_err}"


async def main():
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    data = json.loads(WORDS_PATH.read_text(encoding="utf-8"))
    items = data.get("items") or []
    sem = asyncio.Semaphore(CONCURRENCY)
    results = await asyncio.gather(*[synth_one(sem, it) for it in items])
    ok = sum(1 for s, _ in results if s == "ok")
    skip = sum(1 for s, _ in results if s == "skip")
    fail = [m for s, m in results if s == "fail"]
    WORDS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"voice={VOICE} rate={RATE} total={len(items)} ok={ok} skip={skip} fail={len(fail)}")
    for m in fail[:30]:
        print(" FAIL", m)
    with_q = sum(1 for it in items if it.get("quizAudio"))
    print(f"quizAudio set on {with_q}/{len(items)}")


if __name__ == "__main__":
    asyncio.run(main())
