"""Add Shanghai Grade 1 (沪教版 2024 新版, 1A/1B U1-U10) words missing from words.json,
generate word + phonics MP3s (same voice/settings as regen_cute_voice.py), and write units.json.
Run: /workspace/.tts-venv/bin/python gen_grade1_words.py
"""
import asyncio, csv, json, re, subprocess
from pathlib import Path
import edge_tts

VOICE = "en-US-AnaNeural"
RATE = "+8%"
PITCH = "+15Hz"
BASE = Path(__file__).resolve().parent
AUDIO = BASE / "audio"
CSV = Path("/workspace/shanghai-grade1-english-words.csv")

# word -> (ipa US, phonics)
META = {
 "pack": ("/pæk/", "PACK"),
 "schoolbag": ("/ˈskuːlbæɡ/", "SCHOOL-bag"),
 "pencil": ("/ˈpensl/", "PEN-cil"),
 "ruler": ("/ˈruːlər/", "RU-ler"),
 "eraser": ("/ɪˈreɪsər/", "e-RA-ser"),
 "book": ("/bʊk/", "BOOK"),
 "pencil case": ("/ˈpensl keɪs/", "PEN-cil CASE"),
 "clean": ("/kliːn/", "CLEAN"),
 "classroom": ("/ˈklæsruːm/", "CLASS-room"),
 "door": ("/dɔːr/", "DOOR"),
 "desk": ("/desk/", "DESK"),
 "chair": ("/tʃer/", "CHAIR"),
 "on duty": ("/ɑːn ˈduːti/", "on DU-ty"),
 "blackboard": ("/ˈblækbɔːrd/", "BLACK-board"),
 "floor": ("/flɔːr/", "FLOOR"),
 "face": ("/feɪs/", "FACE"),
 "eye": ("/aɪ/", "EYE"),
 "ear": ("/ɪr/", "EAR"),
 "nose": ("/noʊz/", "NOSE"),
 "mouth": ("/maʊθ/", "MOUTH"),
 "family": ("/ˈfæməli/", "FAM-i-ly"),
 "mum": ("/mʌm/", "MUM"),
 "dad": ("/dæd/", "DAD"),
 "brother": ("/ˈbrʌðər/", "BROTH-er"),
 "sister": ("/ˈsɪstər/", "SIS-ter"),
 "warm": ("/wɔːrm/", "WARM"),
 "helpful": ("/ˈhelpfl/", "HELP-ful"),
 "animal": ("/ˈænɪml/", "AN-i-mal"),
 "horse": ("/hɔːrs/", "HORSE"),
 "hen": ("/hen/", "HEN"),
 "bee": ("/biː/", "BEE"),
 "bird": ("/bɜːrd/", "BIRD"),
 "hill": ("/hɪl/", "HILL"),
 "fly away": ("/flaɪ əˈweɪ/", "FLY a-WAY"),
 "come back": ("/kʌm ˈbæk/", "come BACK"),
 "flap wings": ("/flæp wɪŋz/", "FLAP WINGS"),
 "wash": ("/wɑːʃ/", "WASH"),
 "tie shoelaces": ("/taɪ ˈʃuːleɪsɪz/", "TIE SHOE-la-ces"),
 "take a photo": ("/teɪk ə ˈfoʊtoʊ/", "TAKE a PHO-to"),
 "one": ("/wʌn/", "ONE"),
 "two": ("/tuː/", "TWO"),
 "three": ("/θriː/", "THREE"),
 "four": ("/fɔːr/", "FOUR"),
 "six": ("/sɪks/", "SIX"),
 "busy": ("/ˈbɪzi/", "BU-sy"),
 "tired": ("/ˈtaɪərd/", "TI-red"),
 "lunch": ("/lʌntʃ/", "LUNCH"),
 "meatball": ("/ˈmiːtbɔːl/", "MEAT-ball"),
 "vegetable": ("/ˈvedʒtəbl/", "VEG-ta-ble"),
 "soup": ("/suːp/", "SOUP"),
 "colour": ("/ˈkʌlər/", "COL-our"),
 "playground": ("/ˈpleɪɡraʊnd/", "PLAY-ground"),
 "slide": ("/slaɪd/", "SLIDE"),
 "swing": ("/swɪŋ/", "SWING"),
 "seesaw": ("/ˈsiːsɔː/", "SEE-saw"),
 "hold on tight": ("/hoʊld ɑːn taɪt/", "HOLD on TIGHT"),
 "be careful": ("/bi ˈkerfl/", "be CARE-ful"),
 "rainy": ("/ˈreɪni/", "RAI-ny"),
 "windy": ("/ˈwɪndi/", "WIN-dy"),
 "cloudy": ("/ˈklaʊdi/", "CLOU-dy"),
 "snowy": ("/ˈsnoʊi/", "SNOW-y"),
 "trousers": ("/ˈtraʊzərz/", "TROU-sers"),
 "sock": ("/sɑːk/", "SOCK"),
 "socks": ("/sɑːks/", "SOCKS"),
 "shoe": ("/ʃuː/", "SHOE"),
 "shoes": ("/ʃuːz/", "SHOES"),
 "dress": ("/dres/", "DRESS"),
 "skirt": ("/skɜːrt/", "SKIRT"),
 "game": ("/ɡeɪm/", "GAME"),
 "hide-and-seek": ("/ˌhaɪd ən ˈsiːk/", "HIDE-and-SEEK"),
 "move-and-freeze": ("/ˌmuːv ən ˈfriːz/", "MOVE-and-FREEZE"),
 "ready": ("/ˈredi/", "REA-dy"),
 "skip rope": ("/skɪp roʊp/", "SKIP ROPE"),
 "throw sandbags": ("/θroʊ ˈsændbæɡz/", "THROW SAND-bags"),
 "traffic light": ("/ˈtræfɪk laɪt/", "TRAF-fic LIGHT"),
 "stop": ("/stɑːp/", "STOP"),
 "wait": ("/weɪt/", "WAIT"),
 "zebra crossing": ("/ˈziːbrə ˈkrɔːsɪŋ/", "ZE-bra CROSS-ing"),
 "tiger": ("/ˈtaɪɡər/", "TI-ger"),
 "elephant": ("/ˈelɪfənt/", "EL-e-phant"),
 "monkey": ("/ˈmʌŋki/", "MON-key"),
 "climb a tree": ("/klaɪm ə triː/", "CLIMB a TREE"),
 "kite": ("/kaɪt/", "KITE"),
 "toy car": ("/tɔɪ kɑːr/", "TOY CAR"),
 "toy boat": ("/tɔɪ boʊt/", "TOY BOAT"),
 "toy train": ("/tɔɪ treɪn/", "TOY TRAIN"),
 "gift": ("/ɡɪft/", "GIFT"),
 "cute": ("/kjuːt/", "CUTE"),
}

IPA_SAY = {
    "iː": "ee", "ɪ": "ih", "i": "ih", "e": "eh", "æ": "a", "ɑː": "ah", "ɑ": "ah",
    "ɒ": "o", "ɔː": "aw", "ʊ": "oo", "uː": "ooh", "ʌ": "uh", "ə": "uh", "ɜː": "er",
    "eɪ": "ay", "aɪ": "eye", "ɔɪ": "oy", "aʊ": "ow", "oʊ": "oh", "ɪə": "ear",
    "eə": "air", "ʊə": "ure", "p": "p", "b": "b", "t": "t", "d": "d", "k": "k",
    "ɡ": "g", "g": "g", "f": "f", "v": "v", "θ": "th", "ð": "the", "s": "s",
    "z": "z", "ʃ": "sh", "ʒ": "zh", "h": "h", "tʃ": "ch", "dʒ": "j", "m": "m",
    "n": "n", "ŋ": "ng", "l": "l", "r": "r", "j": "y", "w": "w",
}
TOKENS = sorted(IPA_SAY, key=len, reverse=True)

def tokenize_ipa(ipa):
    s = ipa.strip().strip("/").replace("ˈ", "").replace("ˌ", "")
    out, i = [], 0
    while i < len(s):
        m = next((t for t in TOKENS if s.startswith(t, i)), None)
        if m: out.append(m); i += len(m)
        else: i += 1
    return out

def sid(w):
    return "w_" + re.sub(r"[^a-z0-9]+", "_", w.lower().replace("'", "")).strip("_")

def display(w):
    return w[0].upper() + w[1:]

async def tts(text, path):
    raw = path.with_suffix(".raw.mp3")
    await edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH).save(str(raw))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw),
                    "-ac", "1", "-ar", "24000", "-c:a", "libmp3lame", "-b:a", "48k", str(path)], check=True)
    raw.unlink()

async def main():
    rows = [r for r in csv.DictReader(open(CSV, encoding="utf-8-sig")) if r["edition"].startswith("新版")]
    data = json.loads((BASE / "words.json").read_text(encoding="utf-8"))
    items = data["items"]
    by_text = {}
    for it in items:
        by_text.setdefault(it["text"].lower(), it)
    ids = {it["id"] for it in items}
    added = []
    for r in rows:
        w = r["word"].strip()
        k = w.lower()
        if k in by_text:
            continue
        ipa, phon = META[k]
        _id = sid(w)
        assert _id not in ids, _id
        segs = tokenize_ipa(ipa)
        text = display(w)
        await tts(text + ".", AUDIO / f"{_id}.mp3")
        spoken = ". ".join(IPA_SAY.get(p, p) for p in segs) + ". " + text + "."
        await tts(spoken, AUDIO / f"{_id}_phonics.mp3")
        it = {"id": _id, "text": text, "ipa": ipa, "zh": r["zh"], "phonics": phon,
              "audio": f"audio/{_id}.mp3", "phonicsAudio": f"audio/{_id}_phonics.mp3",
              "ipaSegments": segs, "tags": ["grade1"]}
        items.append(it); by_text[k] = it; ids.add(_id); added.append(text)
        print("added", text, (AUDIO / f"{_id}.mp3").stat().st_size)
    (BASE / "words.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    units, order = {}, []
    for r in rows:
        sem = r["semester"][:2]
        num = int(re.search(r"\d+", r["unit"]).group())
        uid = f"{sem}-U{num}"
        if uid not in units:
            units[uid] = {"id": uid, "book": sem, "bookTitle": "上册" if sem == "1A" else "下册",
                          "unit": num, "title": f"{sem} U{num} {r['unit_title']}", "words": []}
            order.append(uid)
        wid = by_text[r["word"].strip().lower()]["id"]
        if wid not in units[uid]["words"]:
            units[uid]["words"].append(wid)
    out = {"source": "沪教版(五四制) 2024 新版 一年级英语 1A/1B",
           "units": sorted((units[u] for u in order), key=lambda u: (u["book"], u["unit"]))}
    (BASE / "units.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("added", len(added), "units", len(units))

asyncio.run(main())
