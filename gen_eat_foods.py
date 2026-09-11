import asyncio, json, os
import edge_tts

VOICE = "en-US-AnaNeural"
RATE = "+8%"
PITCH = "+15Hz"
outdir = "/workspace/proto-page/audio"

# Elementary common foods
FOODS = [
  {"id":"apple","name":"apple","emoji":"🍎","triggers":["apple"]},
  {"id":"banana","name":"banana","emoji":"🍌","triggers":["banana"]},
  {"id":"orange","name":"orange","emoji":"🍊","triggers":["orange"]},
  {"id":"grape","name":"grape","emoji":"🍇","triggers":["grape","grapes"]},
  {"id":"carrot","name":"carrot","emoji":"🥕","triggers":["carrot","carrots"]},
  {"id":"fish","name":"fish","emoji":"🐟","triggers":["fish"]},
  {"id":"meat","name":"meat","emoji":"🥩","triggers":["meat"]},
  {"id":"chicken","name":"chicken","emoji":"🍗","triggers":["chicken"]},
  {"id":"bone","name":"bone","emoji":"🦴","triggers":["bone"]},
  {"id":"egg","name":"egg","emoji":"🥚","triggers":["egg"]},
  {"id":"bread","name":"bread","emoji":"🍞","triggers":["bread"]},
  {"id":"milk","name":"milk","emoji":"🥛","triggers":["milk"]},
  {"id":"rice","name":"rice","emoji":"🍚","triggers":["rice"]},
  {"id":"cake","name":"cake","emoji":"🍰","triggers":["cake"]},
  {"id":"cookie","name":"cookie","emoji":"🍪","triggers":["cookie","cookies"]},
  {"id":"bamboo","name":"bamboo","emoji":"🎋","triggers":["bamboo"]},
]

# likes: if food not in likes and likes is non-empty specials... 
# Better: each pet has likes set and dislikes set; default like unless disliked
PET_TASTE = {
  "cat": {
    "like": ["fish","milk","meat","chicken","egg","fish"],
    "dislike": ["bone","carrot","bamboo"]
  },
  "dog": {
    "like": ["bone","meat","chicken","cookie","bread","egg"],
    "dislike": ["fish","bamboo"]
  },
  "bunny": {
    "like": ["carrot","apple","banana","grape","orange","lettuce"],
    "dislike": ["meat","fish","bone","chicken"]
  },
  "fox": {
    "like": ["meat","chicken","fish","egg","apple"],
    "dislike": ["bamboo","bone"]
  },
  "panda": {
    "like": ["bamboo","apple","banana","carrot","rice","cake"],
    "dislike": ["meat","bone","fish","chicken"]
  },
}

async def save(text, path):
    await edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH).save(path)

async def main():
    # Generate accept/reject lines per food
    for f in FOODS:
        f["accept"] = {
            "text": f"Yummy! I love {f['name']}.",
            "audio": f"audio/eat_ok_{f['id']}.mp3"
        }
        f["reject"] = {
            "text": f"No thanks. I don't like {f['name']}.",
            "audio": f"audio/eat_no_{f['id']}.mp3"
        }
        await save(f["accept"]["text"], os.path.join(outdir, f"eat_ok_{f['id']}.mp3"))
        await save(f["reject"]["text"], os.path.join(outdir, f"eat_no_{f['id']}.mp3"))
        print("food", f["id"])

    # Generic fallbacks
    await save("Yummy! Thank you.", os.path.join(outdir, "eat_ok_generic.mp3"))
    await save("No thanks. I don't want that.", os.path.join(outdir, "eat_no_generic.mp3"))
    await save("What should I eat?", os.path.join(outdir, "eat_ask.mp3"))

    data = {
        "voice": VOICE,
        "foods": FOODS,
        "petTaste": PET_TASTE,
        "genericAccept": {"text": "Yummy! Thank you.", "audio": "audio/eat_ok_generic.mp3"},
        "genericReject": {"text": "No thanks. I don't want that.", "audio": "audio/eat_no_generic.mp3"},
        "askFood": {"text": "What should I eat?", "audio": "audio/eat_ask.mp3"},
    }
    json.dump(data, open("/workspace/proto-page/foods.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("done", len(FOODS))

asyncio.run(main())
