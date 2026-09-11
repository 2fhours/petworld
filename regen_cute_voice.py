import asyncio, json, os, re
from pathlib import Path
import edge_tts

VOICE = "en-US-AnaNeural"  # US child voice, cuter for pet/kids
RATE = "+8%"
PITCH = "+15Hz"
outdir = Path("/workspace/proto-page/audio")
outdir.mkdir(exist_ok=True)

IPA_SAY = {
    "iː": "ee", "ɪ": "ih", "i": "ih", "e": "eh", "æ": "a", "ɑː": "ah", "ɑ": "ah",
    "ɒ": "o", "ɔː": "aw", "ʊ": "oo", "uː": "ooh", "ʌ": "uh", "ə": "uh", "ɜː": "er",
    "eɪ": "ay", "aɪ": "eye", "ɔɪ": "oy", "aʊ": "ow", "oʊ": "oh", "ɪə": "ear",
    "eə": "air", "ʊə": "ure", "p": "p", "b": "b", "t": "t", "d": "d", "k": "k",
    "ɡ": "g", "g": "g", "f": "f", "v": "v", "θ": "th", "ð": "the", "s": "s",
    "z": "z", "ʃ": "sh", "ʒ": "zh", "h": "h", "tʃ": "ch", "dʒ": "j", "m": "m",
    "n": "n", "ŋ": "ng", "l": "l", "r": "r", "j": "y", "w": "w",
}
TOKENS = sorted(IPA_SAY.keys(), key=len, reverse=True)

def tokenize_ipa(ipa: str):
    s = ipa.strip().strip("/").strip("[]")
    s = s.replace("ˈ", "").replace("ˌ", "").replace(".", " ")
    s = re.sub(r"\s+", " ", s).strip()
    out = []
    i = 0
    while i < len(s):
        if s[i] == " ":
            i += 1
            continue
        matched = None
        for tok in TOKENS:
            if s.startswith(tok, i):
                matched = tok
                break
        if matched:
            out.append(matched)
            i += len(matched)
        else:
            i += 1
    return out

async def save(text, path):
    await edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH).save(str(path))

async def main():
    # words
    words = json.load(open("/workspace/proto-page/words.json", encoding="utf-8"))
    words["voice"] = VOICE
    for item in words["items"]:
        await save(item["text"], outdir / f"{item['id']}.mp3")
        item["audio"] = f"audio/{item['id']}.mp3"
        phones = tokenize_ipa(item["ipa"])
        item["ipaSegments"] = phones
        spoken = ". ".join(IPA_SAY.get(ph, ph) for ph in phones)
        spoken = (spoken + ". " + item["text"] + ".") if spoken else (item["text"] + ".")
        await save(spoken, outdir / f"{item['id']}_phonics.mp3")
        item["phonicsAudio"] = f"audio/{item['id']}_phonics.mp3"
        print("word", item["id"])
    json.dump(words, open("/workspace/proto-page/words.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    # actions
    actions = json.load(open("/workspace/proto-page/actions.json", encoding="utf-8"))
    actions["voice"] = VOICE
    for kind, items in actions["actions"].items():
        for item in items:
            await save(item["text"], outdir / f"{item['id']}.mp3")
            item["audio"] = f"audio/{item['id']}.mp3"
            print("act", item["id"])
    json.dump(actions, open("/workspace/proto-page/actions.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    # dialogs
    dialogs = json.load(open("/workspace/proto-page/dialogs.json", encoding="utf-8"))
    dialogs["voice"] = VOICE
    for item in dialogs["dialogs"]:
        await save(item["reply"], outdir / f"dlg_{item['id']}.mp3")
        item["audio"] = f"audio/dlg_{item['id']}.mp3"
        print("dlg", item["id"])
    json.dump(dialogs, open("/workspace/proto-page/dialogs.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print("DONE", VOICE)

asyncio.run(main())
