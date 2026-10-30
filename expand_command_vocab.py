#!/usr/bin/env python3
"""Expand words.json with all teachable command/dialog vocabulary + audio."""
import asyncio
import json
import re
from pathlib import Path

import edge_tts

VOICE = "en-US-AnaNeural"
RATE = "+8%"
PITCH = "+15Hz"
BASE = Path("/workspace/proto-page")
OUTDIR = BASE / "audio"

REMOVE = {
    "no hat", "no clothes", "no glasses", "no outfit", "take off", "naked",
    "no cap", "no shirt", "no sunglasses",
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
TOKENS = sorted(IPA_SAY.keys(), key=len, reverse=True)


def sid(word: str) -> str:
    w = word.lower().replace("'", "")
    return re.sub(r"[^a-z0-9]+", "_", w).strip("_") or "word"


def norm(s: str) -> str:
    s = (s or "").lower().strip()
    s = re.sub(r"[?!.,]+", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = s.replace("'", "")
    return s


def tokenize_ipa(ipa: str):
    s = (ipa or "").strip().strip("/").strip("[]")
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


# Building-block IPA / phonics / zh for composing phrases
W = {
    "a": ("/ə/", "A", "一个"),
    "am": ("/æm/", "AM", "是（我）"),
    "and": ("/ænd/", "AND", "和"),
    "apple": ("/ˈæpl/", "AP-ple", "苹果"),
    "ball": ("/bɔːl/", "BALL", "球"),
    "bamboo": ("/ˌbæmˈbuː/", "bam-BOO", "竹子"),
    "banana": ("/bəˈnænə/", "ba-NA-na", "香蕉"),
    "basketball": ("/ˈbæskɪtbɔːl/", "BAS-ket-ball", "篮球"),
    "bed": ("/bed/", "BED", "床"),
    "bike": ("/baɪk/", "BIKE", "自行车"),
    "black": ("/blæk/", "BLACK", "黑色"),
    "blue": ("/bluː/", "BLUE", "蓝色"),
    "bone": ("/boʊn/", "BONE", "骨头"),
    "bread": ("/bred/", "BREAD", "面包"),
    "bye": ("/baɪ/", "BYE", "再见"),
    "cake": ("/keɪk/", "CAKE", "蛋糕"),
    "cap": ("/kæp/", "CAP", "便帽"),
    "carrot": ("/ˈkærət/", "CAR-rot", "胡萝卜"),
    "cat": ("/kæt/", "CAT", "猫"),
    "chicken": ("/ˈtʃɪkɪn/", "CHICK-en", "鸡肉"),
    "clothes": ("/kloʊðz/", "CLOTHES", "衣服"),
    "cookie": ("/ˈkʊki/", "COOK-ie", "饼干"),
    "dance": ("/dæns/", "DANCE", "跳舞"),
    "disc": ("/dɪsk/", "DISC", "圆盘"),
    "dog": ("/dɔːɡ/", "DOG", "狗"),
    "eat": ("/iːt/", "EAT", "吃"),
    "egg": ("/eɡ/", "EGG", "鸡蛋"),
    "feed": ("/fiːd/", "FEED", "喂"),
    "fish": ("/fɪʃ/", "FISH", "鱼"),
    "football": ("/ˈfʊtbɔːl/", "FOOT-ball", "足球"),
    "fox": ("/fɑːks/", "FOX", "狐狸"),
    "frisbee": ("/ˈfrɪzbi/", "FRIS-bee", "飞盘"),
    "glasses": ("/ˈɡlæsɪz/", "GLASS-es", "眼镜"),
    "go": ("/ɡoʊ/", "GO", "去"),
    "grape": ("/ɡreɪp/", "GRAPE", "葡萄"),
    "green": ("/ɡriːn/", "GREEN", "绿色"),
    "hat": ("/hæt/", "HAT", "帽子"),
    "hoops": ("/huːps/", "HOOPS", "篮筐"),
    "i": ("/aɪ/", "I", "我"),
    "jump": ("/dʒʌmp/", "JUMP", "跳"),
    "kick": ("/kɪk/", "KICK", "踢"),
    "me": ("/miː/", "ME", "我"),
    "meat": ("/miːt/", "MEAT", "肉"),
    "milk": ("/mɪlk/", "MILK", "牛奶"),
    "orange": ("/ˈɔːrɪndʒ/", "OR-ange", "橙色/橙子"),
    "panda": ("/ˈpændə/", "PAN-da", "熊猫"),
    "pet": ("/pet/", "PET", "抚摸"),
    "pink": ("/pɪŋk/", "PINK", "粉色"),
    "play": ("/pleɪ/", "PLAY", "玩"),
    "please": ("/pliːz/", "PLEASE", "请"),
    "purple": ("/ˈpɜːrpl/", "PUR-ple", "紫色"),
    "rabbit": ("/ˈræbɪt/", "RAB-bit", "兔子"),
    "red": ("/red/", "RED", "红色"),
    "rice": ("/raɪs/", "RICE", "米饭"),
    "ride": ("/raɪd/", "RIDE", "骑"),
    "run": ("/rʌn/", "RUN", "跑"),
    "shirt": ("/ʃɜːrt/", "SHIRT", "衬衫"),
    "shoot": ("/ʃuːt/", "SHOOT", "投篮"),
    "soccer": ("/ˈsɑːkər/", "SOC-cer", "足球"),
    "sunglasses": ("/ˈsʌnˌɡlæsɪz/", "SUN-glass-es", "太阳镜"),
    "swim": ("/swɪm/", "SWIM", "游泳"),
    "swimming": ("/ˈswɪmɪŋ/", "SWIM-ming", "游泳"),
    "the": ("/ðə/", "THE", "这/那"),
    "throw": ("/θroʊ/", "THROW", "扔"),
    "white": ("/waɪt/", "WHITE", "白色"),
    "yellow": ("/ˈjeloʊ/", "YEL-low", "黄色"),
}

COLOR_ZH_SHORT = {
    "red": "红", "yellow": "黄", "blue": "蓝", "green": "绿",
    "pink": "粉", "purple": "紫", "orange": "橙", "white": "白", "black": "黑",
}
SLOT_ZH = {"hat": "帽子", "clothes": "衣服", "glasses": "眼镜"}


def join_ipa(parts):
    inner = " ".join(p.strip("/") for p in parts)
    return f"/{inner}/"


def join_phonics(parts):
    return " ".join(parts)


PHRASES = [
    # dialogs.json triggers (short phrases; apostrophe-less dupes skipped later)
    ("Hello there", "/həˈloʊ ðer/", "he-LLO there", "你好呀"),
    ("Good afternoon", "/ɡʊd ˌæftərˈnuːn/", "good af-ter-NOON", "下午好"),
    ("Good evening", "/ɡʊd ˈiːvnɪŋ/", "good EVE-ning", "晚上好"),
    ("Night night", "/naɪt naɪt/", "NIGHT night", "晚安"),
    ("How do you do?", "/haʊ duː juː duː/", "HOW do you DO", "你好（正式）"),
    ("How's it going?", "/haʊz ɪt ˈɡoʊɪŋ/", "HOW'S it GO-ing", "最近怎么样？"),
    ("How are you doing?", "/haʊ ɑːr juː ˈduːɪŋ/", "HOW are you DO-ing", "你过得怎么样？"),
    ("I am fine", "/aɪ æm faɪn/", "I am FINE", "我很好"),
    ("I'm good", "/aɪm ɡʊd/", "I'M GOOD", "我很好"),
    ("What is your name?", "/wʌt ɪz jʊr neɪm/", "WHAT is your NAME", "你叫什么名字？"),
    ("Your name", "/jʊr neɪm/", "YOUR name", "你的名字"),
    ("Glad to meet you", "/ɡlæd tə miːt juː/", "GLAD to MEET you", "很高兴见到你"),
    ("Pleased to meet you", "/pliːzd tə miːt juː/", "PLEASED to MEET you", "很高兴认识你"),
    ("How old are you?", "/haʊ oʊld ɑːr juː/", "HOW old are you", "你几岁了？"),
    ("What's your age?", "/wʌts jʊr eɪdʒ/", "WHAT'S your AGE", "你多大了？"),
    ("Where are you from?", "/wer ɑːr juː frʌm/", "WHERE are you FROM", "你来自哪里？"),
    ("Where do you live?", "/wer duː juː lɪv/", "WHERE do you LIVE", "你住在哪里？"),
    ("Thank you very much", "/ˈθæŋk juː ˈveri mʌtʃ/", "THANK you VER-y MUCH", "非常感谢"),
    ("Thanks a lot", "/θæŋks ə lɑːt/", "THANKS a LOT", "非常感谢"),
    ("Excuse me", "/ɪkˈskjuːz miː/", "ex-CUSE me", "打扰一下"),
    ("I'm sorry", "/aɪm ˈsɑːri/", "I'M SOR-ry", "对不起"),
    ("No thank you", "/noʊ ˈθæŋk juː/", "NO THANK you", "不用了，谢谢"),
    ("No thanks", "/noʊ θæŋks/", "NO thanks", "不用了，谢谢"),
    ("Play with me", "/pleɪ wɪð miː/", "PLAY with me", "和我一起玩"),
    ("Come and play", "/kʌm ænd pleɪ/", "COME and PLAY", "来玩吧"),
    ("I'm hungry", "/aɪm ˈhʌŋɡri/", "I'M HUN-gry", "我饿了"),
    ("I am hungry", "/aɪ æm ˈhʌŋɡri/", "I am HUN-gry", "我饿了"),
    ("I want food", "/aɪ wɑːnt fuːd/", "I WANT food", "我想吃东西"),
    ("Feed me", "/fiːd miː/", "FEED me", "喂我"),
    ("I'm sleepy", "/aɪm ˈsliːpi/", "I'M SLEE-py", "我困了"),
    ("I am sleepy", "/aɪ æm ˈsliːpi/", "I am SLEE-py", "我困了"),
    ("I want to sleep", "/aɪ wɑːnt tə sliːp/", "I WANT to SLEEP", "我想睡觉"),
    ("Go to bed", "/ɡoʊ tə bed/", "GO to BED", "去睡觉"),
    ("Love you", "/lʌv juː/", "LOVE you", "爱你"),
    ("How's the weather?", "/haʊz ðə ˈweðər/", "HOW'S the WEATH-er", "天气怎么样？"),
    ("How is the weather?", "/haʊ ɪz ðə ˈweðər/", "HOW is the WEATH-er", "天气怎么样？"),
    ("What's the weather?", "/wʌts ðə ˈweðər/", "WHAT'S the WEATH-er", "天气怎么样？"),
    ("What time is it?", "/wʌt taɪm ɪz ɪt/", "WHAT TIME is it", "现在几点了？"),
    ("What's the time?", "/wʌts ðə taɪm/", "WHAT'S the TIME", "现在几点了？"),
    ("Can you help me?", "/kæn juː help miː/", "CAN you HELP me", "你能帮我吗？"),
    ("Help me", "/help miː/", "HELP me", "帮帮我"),
    ("See you", "/siː juː/", "SEE you", "再见"),
    ("See you later", "/siː juː ˈleɪtər/", "SEE you LA-ter", "回头见"),
    ("See you soon", "/siː juː suːn/", "SEE you SOON", "很快见"),
    ("Bye bye", "/baɪ baɪ/", "BYE bye", "拜拜"),
    ("Good bye", "/ɡʊd baɪ/", "good BYE", "再见"),
    # plays.json useful phrases
    ("Play soccer", "/pleɪ ˈsɑːkər/", "PLAY SOC-cer", "踢足球"),
    ("Play football", "/pleɪ ˈfʊtbɔːl/", "PLAY FOOT-ball", "踢足球"),
    ("Kick the ball", "/kɪk ðə bɔːl/", "KICK the BALL", "踢球"),
    ("Play basketball", "/pleɪ ˈbæskɪtbɔːl/", "PLAY BAS-ket-ball", "打篮球"),
    ("Shoot hoops", "/ʃuːt huːps/", "SHOOT HOOPS", "投篮"),
    ("Let's swim", "/lets swɪm/", "LET'S SWIM", "我们游泳吧"),
    ("Go swimming", "/ɡoʊ ˈswɪmɪŋ/", "GO SWIM-ming", "去游泳"),
    ("Swim please", "/swɪm pliːz/", "SWIM please", "请游泳"),
    ("Let's dance", "/lets dæns/", "LET'S DANCE", "我们跳舞吧"),
    ("Let's run", "/lets rʌn/", "LET'S RUN", "我们跑步吧"),
    ("Go for a run", "/ɡoʊ fɔːr ə rʌn/", "GO for a RUN", "去跑步"),
    ("Let's jump", "/lets dʒʌmp/", "LET'S JUMP", "我们跳跃吧"),
    ("Play frisbee", "/pleɪ ˈfrɪzbi/", "PLAY FRIS-bee", "玩飞盘"),
    ("Throw the disc", "/θroʊ ðə dɪsk/", "THROW the DISC", "扔飞盘"),
    ("Ride a bike", "/raɪd ə baɪk/", "RIDE a BIKE", "骑自行车"),
    # animals.json "I am a …"
    ("I am a cat", "/aɪ æm ə kæt/", "I am a CAT", "我是一只猫"),
    ("I am a dog", "/aɪ æm ə dɔːɡ/", "I am a DOG", "我是一只狗"),
    ("I am a rabbit", "/aɪ æm ə ˈræbɪt/", "I am a RAB-bit", "我是一只兔子"),
    ("I am a fox", "/aɪ æm ə fɑːks/", "I am a FOX", "我是一只狐狸"),
    ("I am a panda", "/aɪ æm ə ˈpændə/", "I am a PAN-da", "我是一只熊猫"),
]


def display_single(word: str) -> str:
    special = {
        "i": "I", "i'm": "I'm", "ok": "OK", "okay": "Okay",
    }
    return special.get(word.lower(), word[:1].upper() + word[1:].lower())


def make_item(text, ipa, phonics, zh):
    _id = sid(text)
    segs = tokenize_ipa(ipa)
    return {
        "id": _id,
        "text": text,
        "ipa": ipa,
        "zh": zh,
        "phonics": phonics,
        "audio": f"audio/{_id}.mp3",
        "phonicsAudio": f"audio/{_id}_phonics.mp3",
        "ipaSegments": segs,
    }


def collect_candidates(existing_norm):
    """Also walk source JSON so we don't miss a short trigger."""
    extra = []
    dialogs = json.loads((BASE / "dialogs.json").read_text(encoding="utf-8"))
    for d in dialogs["dialogs"]:
        for t in d.get("triggers") or []:
            t = (t or "").strip()
            if not t or len(t) > 40:
                continue
            extra.append(t)
    plays = json.loads((BASE / "plays.json").read_text(encoding="utf-8"))
    for p in plays["plays"]:
        for t in p.get("triggers") or []:
            t = (t or "").strip()
            if not t or len(t) > 40:
                continue
            extra.append(t)
    animals = json.loads((BASE / "animals.json").read_text(encoding="utf-8"))
    for a in animals["animals"]:
        for t in a.get("triggers") or []:
            extra.append(t)
        name = a.get("name") or a.get("id")
        article = a.get("article") or "a"
        extra.append(f"I am {article} {name}")
    foods = json.loads((BASE / "foods.json").read_text(encoding="utf-8"))
    for f in foods["foods"]:
        extra.append(f["name"])
        extra.append(f"eat {f['name']}")
        for t in f.get("triggers") or []:
            extra.append(t)
    # report uncovered English triggers (not already known / not in PHRASES / not singles we'll add)
    return extra


async def tts_save(text, path, rate=RATE, pitch=PITCH):
    last = None
    for attempt in range(4):
        try:
            await edge_tts.Communicate(text, VOICE, rate=rate, pitch=pitch).save(str(path))
            if path.exists() and path.stat().st_size > 200:
                return
            last = RuntimeError(f"tiny file {path} size={path.stat().st_size if path.exists() else 0}")
        except Exception as e:
            last = e
            await asyncio.sleep(0.6 * (attempt + 1))
    raise last


async def gen_pair(item, sem):
    audio_path = BASE / item["audio"]
    phonics_path = BASE / item["phonicsAudio"]
    chunks = [c for c in re.split(r"[-\s]+", item["phonics"]) if c]
    spoken = ". ".join(chunks) + ". " + item["text"] + "."
    async with sem:
        if not audio_path.exists() or audio_path.stat().st_size < 200:
            await tts_save(item["text"], audio_path)
            print("audio", item["text"])
        else:
            print("skip-audio", item["text"])
        if not phonics_path.exists() or phonics_path.stat().st_size < 200:
            await tts_save(spoken, phonics_path, rate="-8%", pitch=PITCH)
            print("phonics", item["text"])
        else:
            print("skip-phonics", item["text"])


async def main():
    data = json.loads((BASE / "words.json").read_text(encoding="utf-8"))
    items = data["items"]
    before = len(items)
    existing_ids = {it["id"] for it in items}
    existing_norm = {norm(it["text"]) for it in items}

    # Drop forbidden phrases if present
    kept = []
    removed = []
    for it in items:
        if norm(it["text"]) in {norm(x) for x in REMOVE}:
            removed.append(it["text"])
            continue
        kept.append(it)
    items = kept

    new_items = []
    seen_new = set(existing_norm)

    def consider(text, ipa, phonics, zh):
        key = norm(text)
        if not key or key in REMOVE or key in {norm(x) for x in REMOVE}:
            return
        if key in seen_new:
            return
        if len(text) > 40:
            return
        if re.fullmatch(r"[^\w\s]+", text):
            return
        it = make_item(text, ipa, phonics, zh)
        # unique id
        base_id = it["id"]
        n = 2
        while it["id"] in existing_ids or any(x["id"] == it["id"] for x in new_items):
            it["id"] = f"{base_id}_{n}"
            it["audio"] = f"audio/{it['id']}.mp3"
            it["phonicsAudio"] = f"audio/{it['id']}_phonics.mp3"
            n += 1
        seen_new.add(key)
        new_items.append(it)

    # explicit phrases
    for text, ipa, phonics, zh in PHRASES:
        consider(text, ipa, phonics, zh)

    # care singles
    consider("Pet", "/pet/", "PET", "抚摸/宠物")
    consider("Eat", "/iːt/", "EAT", "吃")

    # outfit colors + pieces
    colors = ["red", "yellow", "blue", "green", "pink", "purple", "orange", "white", "black"]
    pieces = ["hat", "cap", "clothes", "shirt", "glasses", "sunglasses"]
    combo_slots = ["hat", "clothes", "glasses"]
    for c in colors:
        ipa, ph, zh = W[c]
        consider(display_single(c), ipa, ph, zh)
    for p in pieces:
        ipa, ph, zh = W[p]
        consider(display_single(p), ipa, ph, zh)
    for c in colors:
        for sl in combo_slots:
            ipa = join_ipa([W[c][0], W[sl][0]])
            ph = join_phonics([W[c][1], W[sl][1]])
            zh = COLOR_ZH_SHORT[c] + SLOT_ZH[sl]
            text = f"{display_single(c)} {sl}"
            consider(text, ipa, ph, zh)

    # foods eat X
    foods = json.loads((BASE / "foods.json").read_text(encoding="utf-8"))
    for f in foods["foods"]:
        name = f["name"]
        ipa_n, ph_n, zh_n = W.get(name, (f"/ /", name.upper(), name))
        if name not in W:
            # fallback shouldn't happen
            print("MISSING FOOD META", name)
            continue
        consider(
            f"Eat {name}",
            join_ipa([W["eat"][0], ipa_n]),
            join_phonics([W["eat"][1], ph_n]),
            "吃" + zh_n,
        )

    # Walk sources: warn about leftover short English triggers not covered
    extras = collect_candidates(existing_norm)
    leftover = []
    for t in extras:
        if norm(t) not in seen_new and norm(t) not in {norm(x) for x in REMOVE}:
            leftover.append(t)
    leftover = sorted(set(leftover), key=str.lower)
    print("LEFTOVER TRIGGERS (apostrophe-stripped already in list expected):", leftover)

    new_items.sort(key=lambda it: it["text"].lower())
    data["items"] = items + new_items
    data["voice"] = VOICE

    OUTDIR.mkdir(exist_ok=True)
    sem = asyncio.Semaphore(5)
    await asyncio.gather(*(gen_pair(it, sem) for it in new_items))

    (BASE / "words.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("BEFORE", before)
    print("REMOVED", removed)
    print("ADDED", len(new_items))
    print("AFTER", len(data["items"]))
    print("ADDED TEXTS:")
    for it in new_items:
        print(" -", it["text"])


if __name__ == "__main__":
    asyncio.run(main())
