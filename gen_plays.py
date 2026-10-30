import asyncio, json, os
import edge_tts

VOICE = "en-US-AnaNeural"
RATE = "+8%"
PITCH = "+15Hz"
outdir = "/workspace/proto-page/audio"

PLAYS = [
  {
    "id": "soccer",
    "emoji": "⚽",
    "label": "Soccer",
    "triggers": ["soccer", "football", "play soccer", "play football", "kick the ball"],
    "reply": "Let's play soccer!",
  },
  {
    "id": "basketball",
    "emoji": "🏀",
    "label": "Basketball",
    "triggers": ["basketball", "play basketball", "shoot hoops", "hoops"],
    "reply": "Let's play basketball!",
  },
  {
    "id": "swim",
    "emoji": "🏊",
    "label": "Swim",
    "triggers": ["swim", "swimming", "let's swim", "go swimming", "swim please"],
    "reply": "Let's go swimming!",
  },
  {
    "id": "dance",
    "emoji": "💃",
    "label": "Dance",
    "triggers": ["dance", "dancing", "let's dance", "music"],
    "reply": "Let's dance!",
  },
  {
    "id": "run",
    "emoji": "🏃",
    "label": "Run",
    "triggers": ["run", "running", "let's run", "go for a run", "race"],
    "reply": "Let's run!",
  },
  {
    "id": "jump",
    "emoji": "🤸",
    "label": "Jump",
    "triggers": ["jump", "jumping", "let's jump", "hop"],
    "reply": "Let's jump!",
  },
  {
    "id": "frisbee",
    "emoji": "🥏",
    "label": "Frisbee",
    "triggers": ["frisbee", "play frisbee", "throw the disc"],
    "reply": "Let's play frisbee!",
  },
  {
    "id": "bike",
    "emoji": "🚲",
    "label": "Bike",
    "triggers": ["bike", "bicycle", "ride a bike", "cycling"],
    "reply": "Let's ride a bike!",
  },
]

async def save(text, path):
    await edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH).save(path)

async def main():
    for p in PLAYS:
        audio = f"audio/play_{p['id']}.mp3"
        await save(p["reply"], os.path.join(outdir, f"play_{p['id']}.mp3"))
        p["audio"] = audio
        print("ok", p["id"])
    # generic fallback for plain "let's play"
    await save("Let's play!", os.path.join(outdir, "play_generic.mp3"))
    data = {
        "voice": VOICE,
        "plays": PLAYS,
        "generic": {"reply": "Let's play!", "audio": "audio/play_generic.mp3"},
    }
    json.dump(data, open("/workspace/proto-page/plays.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("done", len(PLAYS))

asyncio.run(main())
