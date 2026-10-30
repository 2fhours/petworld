import asyncio, json, os
import edge_tts

VOICE = "en-US-AnaNeural"
RATE = "+8%"
PITCH = "+15Hz"
outdir = "/workspace/proto-page/audio"

ANIMALS = [
  {"id":"cat","form":"cat","name":"cat","article":"a","triggers":["cat","kitten","kitty","猫"]},
  {"id":"dog","form":"dog","name":"dog","article":"a","triggers":["dog","puppy","狗"]},
  {"id":"bunny","form":"bunny","name":"rabbit","article":"a","triggers":["rabbit","bunny","兔子"]},
  {"id":"fox","form":"fox","name":"fox","article":"a","triggers":["fox","狐狸"]},
  {"id":"panda","form":"panda","name":"panda","article":"a","triggers":["panda","熊猫"]},
]

async def save(text, path):
    await edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH).save(path)

async def main():
    for a in ANIMALS:
        text = f"I am {a['article']} {a['name']}."
        audio = f"audio/iam_{a['id']}.mp3"
        await save(text, os.path.join(outdir, f"iam_{a['id']}.mp3"))
        a["reply"] = text
        a["audio"] = audio
        print("ok", a["id"], text)
    data = {"voice": VOICE, "animals": ANIMALS}
    json.dump(data, open("/workspace/proto-page/animals.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("done")

asyncio.run(main())
