import asyncio, json, os
import edge_tts

VOICE = "en-US-JennyNeural"
outdir = "/workspace/proto-page/audio"

ACTIONS = {
  "pet": [
    {"id":"act_pet_1","text":"That feels good","ipa":"/ðæt fiːlz ɡʊd/","zh":"好舒服"},
    {"id":"act_pet_2","text":"I like that","ipa":"/aɪ laɪk ðæt/","zh":"我喜欢"},
    {"id":"act_pet_3","text":"Thank you","ipa":"/ˈθæŋk juː/","zh":"谢谢你"},
  ],
  "feed": [
    {"id":"act_feed_1","text":"Yummy","ipa":"/ˈjʌmi/","zh":"好吃"},
    {"id":"act_feed_2","text":"So delicious","ipa":"/soʊ dɪˈlɪʃəs/","zh":"太美味了"},
    {"id":"act_feed_3","text":"More please","ipa":"/mɔːr pliːz/","zh":"再来一点"},
  ],
  "play": [
    {"id":"act_play_1","text":"Let's play","ipa":"/lets pleɪ/","zh":"我们一起玩吧"},
    {"id":"act_play_2","text":"This is fun","ipa":"/ðɪs ɪz fʌn/","zh":"真好玩"},
    {"id":"act_play_3","text":"Come on","ipa":"/kʌm ɑːn/","zh":"来呀"},
  ],
  "sleep": [
    {"id":"act_sleep_1","text":"Good night","ipa":"/ɡʊd ˈnaɪt/","zh":"晚安"},
    {"id":"act_sleep_2","text":"I'm sleepy","ipa":"/aɪm ˈsliːpi/","zh":"我困了"},
    {"id":"act_sleep_3","text":"See you tomorrow","ipa":"/siː juː təˈmɑːroʊ/","zh":"明天见"},
  ],
}

async def one(item):
    path = os.path.join(outdir, item["id"] + ".mp3")
    await edge_tts.Communicate(item["text"], VOICE, rate="-8%").save(path)
    item["audio"] = "audio/" + item["id"] + ".mp3"
    print("ok", item["id"])

async def main():
    flat = []
    for kind, items in ACTIONS.items():
        for it in items:
            it["action"] = kind
            await one(it)
            flat.append(it)
    out = {"voice": VOICE, "actions": ACTIONS}
    # also flat list for convenience
    json.dump(out, open("/workspace/proto-page/actions.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("done", len(flat))

asyncio.run(main())
