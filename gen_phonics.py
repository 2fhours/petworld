import asyncio, json, os, re
import edge_tts

VOICE = "en-US-JennyNeural"
outdir = "/workspace/proto-page/audio"
data = json.load(open("/workspace/proto-page/words.json", encoding="utf-8"))

async def gen_phonics(item):
    chunks = [c.strip() for c in re.split(r"[-\s]+", item["phonics"]) if c.strip()]
    spoken = ". ".join(chunks) + ". " + item["text"] + "."
    path = os.path.join(outdir, item["id"] + "_phonics.mp3")
    communicate = edge_tts.Communicate(spoken, VOICE, rate="-15%")
    await communicate.save(path)
    item["phonicsAudio"] = "audio/" + item["id"] + "_phonics.mp3"
    print("phonics", item["id"])

async def main():
    for item in data["items"]:
        await gen_phonics(item)
    json.dump(data, open("/workspace/proto-page/words.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("done")

asyncio.run(main())
