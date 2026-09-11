import asyncio, json, os, re
import edge_tts

VOICE = "en-US-JennyNeural"
outdir = "/workspace/proto-page/audio"
data = json.load(open("/workspace/proto-page/words.json", encoding="utf-8"))

# Spoken cue for each IPA segment (US English), for neural TTS
IPA_SAY = {
    "iː": "ee",
    "ɪ": "ih",
    "i": "ih",
    "e": "eh",
    "æ": "a",
    "ɑː": "ah",
    "ɑ": "ah",
    "ɒ": "o",
    "ɔː": "aw",
    "ʊ": "oo",
    "uː": "ooh",
    "ʌ": "uh",
    "ə": "uh",
    "ɜː": "er",
    "eɪ": "ay",
    "aɪ": "eye",
    "ɔɪ": "oy",
    "aʊ": "ow",
    "oʊ": "oh",
    "ɪə": "ear",
    "eə": "air",
    "ʊə": "ure",
    "p": "p",
    "b": "b",
    "t": "t",
    "d": "d",
    "k": "k",
    "ɡ": "g",
    "g": "g",
    "f": "f",
    "v": "v",
    "θ": "th",
    "ð": "the",
    "s": "s",
    "z": "z",
    "ʃ": "sh",
    "ʒ": "zh",
    "h": "h",
    "tʃ": "ch",
    "dʒ": "j",
    "m": "m",
    "n": "n",
    "ŋ": "ng",
    "l": "l",
    "r": "r",
    "j": "y",
    "w": "w",
}

# Longest-first match order for tokenizer
TOKENS = sorted(IPA_SAY.keys(), key=len, reverse=True)


def clean_ipa(ipa: str) -> str:
    s = ipa.strip().strip("/").strip("[]")
    s = s.replace("ˈ", "").replace("ˌ", "").replace(".", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def tokenize_ipa(ipa: str):
    s = clean_ipa(ipa)
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
            # skip unknown char
            i += 1
    return out


def spoken_for(phones):
    parts = []
    for ph in phones:
        say = IPA_SAY.get(ph, ph)
        # Pause between symbols: "sound." helps TTS isolate
        parts.append(say)
    # Then the full word separately handled by caller
    return parts


async def gen(item):
    phones = tokenize_ipa(item["ipa"])
    item["ipaSegments"] = phones
    spoken_parts = spoken_for(phones)
    # Speak each IPA sound, then the whole word
    # Use commas/periods for clear separation
    spoken = ". ".join(spoken_parts)
    if spoken:
        spoken = spoken + ". " + item["text"] + "."
    else:
        spoken = item["text"] + "."
    path = os.path.join(outdir, item["id"] + "_phonics.mp3")
    communicate = edge_tts.Communicate(spoken, VOICE, rate="-20%")
    await communicate.save(path)
    item["phonicsAudio"] = "audio/" + item["id"] + "_phonics.mp3"
    print(item["id"], phones, "=>", spoken)


async def main():
    for item in data["items"]:
        await gen(item)
    json.dump(data, open("/workspace/proto-page/words.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("done", len(data["items"]))

asyncio.run(main())
