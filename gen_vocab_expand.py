import asyncio, json, os, re, hashlib
from pathlib import Path
import edge_tts

VOICE = "en-US-AnaNeural"
RATE = "+8%"
PITCH = "+15Hz"
base = Path('/workspace/proto-page')
outdir = base / 'audio'

# IPA + phonics + zh for command vocab (US English, kid-friendly)
META = {
  "a": ("/ə/", "A", "一个"),
  "afternoon": ("/ˌæftərˈnuːn/", "af-ter-NOON", "下午"),
  "again": ("/əˈɡen/", "a-GAIN", "再次"),
  "age": ("/eɪdʒ/", "AGE", "年龄"),
  "am": ("/æm/", "AM", "是（我）"),
  "and": ("/ænd/", "AND", "和"),
  "apple": ("/ˈæpl/", "AP-ple", "苹果"),
  "apples": ("/ˈæplz/", "AP-ples", "苹果（复数）"),
  "are": ("/ɑːr/", "ARE", "是"),
  "ball": ("/bɔːl/", "BALL", "球"),
  "bamboo": ("/ˌbæmˈbuː/", "bam-BOO", "竹子"),
  "banana": ("/bəˈnænə/", "ba-NA-na", "香蕉"),
  "basketball": ("/ˈbæskɪtbɔːl/", "BAS-ket-ball", "篮球"),
  "bed": ("/bed/", "BED", "床"),
  "bicycle": ("/ˈbaɪsɪkl/", "BI-cy-cle", "自行车"),
  "bike": ("/baɪk/", "BIKE", "自行车"),
  "bone": ("/boʊn/", "BONE", "骨头"),
  "bread": ("/bred/", "BREAD", "面包"),
  "buddy": ("/ˈbʌdi/", "BUD-dy", "伙伴"),
  "bunny": ("/ˈbʌni/", "BUN-ny", "兔子"),
  "bye": ("/baɪ/", "BYE", "再见"),
  "cake": ("/keɪk/", "CAKE", "蛋糕"),
  "can": ("/kæn/", "CAN", "可以"),
  "carrot": ("/ˈkærət/", "CAR-rot", "胡萝卜"),
  "carrots": ("/ˈkærəts/", "CAR-rots", "胡萝卜（复数）"),
  "cat": ("/kæt/", "CAT", "猫"),
  "chicken": ("/ˈtʃɪkɪn/", "CHICK-en", "鸡肉/鸡"),
  "china": ("/ˈtʃaɪnə/", "CHI-na", "中国"),
  "come": ("/kʌm/", "COME", "来"),
  "cookie": ("/ˈkʊki/", "COOK-ie", "饼干"),
  "cookies": ("/ˈkʊkiz/", "COOK-ies", "饼干（复数）"),
  "course": ("/kɔːrs/", "COURSE", "当然（of course）"),
  "cycling": ("/ˈsaɪklɪŋ/", "CY-cling", "骑车"),
  "dance": ("/dæns/", "DANCE", "跳舞"),
  "dancing": ("/ˈdænsɪŋ/", "DAN-cing", "跳舞"),
  "day": ("/deɪ/", "DAY", "天/白天"),
  "delicious": ("/dɪˈlɪʃəs/", "de-LI-cious", "美味的"),
  "disc": ("/dɪsk/", "DISC", "圆盘"),
  "do": ("/duː/", "DO", "做"),
  "dog": ("/dɔːɡ/", "DOG", "狗"),
  "doing": ("/ˈduːɪŋ/", "DO-ing", "正在做"),
  "don't": ("/doʊnt/", "DON'T", "不要"),
  "dreams": ("/driːmz/", "DREAMS", "梦"),
  "egg": ("/eɡ/", "EGG", "鸡蛋"),
  "english": ("/ˈɪŋɡlɪʃ/", "ENG-lish", "英语"),
  "evening": ("/ˈiːvnɪŋ/", "EVE-ning", "晚上"),
  "excuse": ("/ɪkˈskjuːz/", "ex-CUSE", "打扰/原谅"),
  "feed": ("/fiːd/", "FEED", "喂"),
  "feels": ("/fiːlz/", "FEELS", "感觉"),
  "fine": ("/faɪn/", "FINE", "很好"),
  "fish": ("/fɪʃ/", "FISH", "鱼"),
  "five": ("/faɪv/", "FIVE", "五"),
  "food": ("/fuːd/", "FOOD", "食物"),
  "football": ("/ˈfʊtbɔːl/", "FOOT-ball", "足球"),
  "for": ("/fɔːr/", "FOR", "为了"),
  "fox": ("/fɑːks/", "FOX", "狐狸"),
  "frisbee": ("/ˈfrɪzbi/", "FRIS-bee", "飞盘"),
  "from": ("/frʌm/", "FROM", "来自"),
  "fun": ("/fʌn/", "FUN", "有趣"),
  "glad": ("/ɡlæd/", "GLAD", "高兴的"),
  "go": ("/ɡoʊ/", "GO", "去"),
  "going": ("/ˈɡoʊɪŋ/", "GO-ing", "正在去"),
  "good": ("/ɡʊd/", "GOOD", "好的"),
  "goodbye": ("/ˌɡʊdˈbaɪ/", "good-BYE", "再见"),
  "goodnight": ("/ˌɡʊdˈnaɪt/", "good-NIGHT", "晚安"),
  "grape": ("/ɡreɪp/", "GRAPE", "葡萄"),
  "grapes": ("/ɡreɪps/", "GRAPES", "葡萄（复数）"),
  "great": ("/ɡreɪt/", "GREAT", "太棒了"),
  "happy": ("/ˈhæpi/", "HAP-py", "开心的"),
  "have": ("/hæv/", "HAVE", "有"),
  "hello": ("/həˈloʊ/", "he-LLO", "你好"),
  "help": ("/help/", "HELP", "帮助"),
  "hey": ("/heɪ/", "HEY", "嘿"),
  "hi": ("/haɪ/", "HI", "嗨"),
  "hoops": ("/huːps/", "HOOPS", "篮筐"),
  "hop": ("/hɑːp/", "HOP", "跳"),
  "how": ("/haʊ/", "HOW", "怎样"),
  "how's": ("/haʊz/", "HOW'S", "怎样（how's）"),
  "hungry": ("/ˈhʌŋɡri/", "HUN-gry", "饿的"),
  "i": ("/aɪ/", "I", "我"),
  "i'm": ("/aɪm/", "I'M", "我是"),
  "im": ("/aɪm/", "I'M", "我是"),
  "is": ("/ɪz/", "IS", "是"),
  "it": ("/ɪt/", "IT", "它"),
  "it's": ("/ɪts/", "IT'S", "它是"),
  "jump": ("/dʒʌmp/", "JUMP", "跳"),
  "jumping": ("/ˈdʒʌmpɪŋ/", "JUMP-ing", "跳跃"),
  "kick": ("/kɪk/", "KICK", "踢"),
  "kitten": ("/ˈkɪtn/", "KIT-ten", "小猫"),
  "kitty": ("/ˈkɪti/", "KIT-ty", "猫咪"),
  "later": ("/ˈleɪtər/", "LA-ter", "稍后"),
  "learn": ("/lɜːrn/", "LEARN", "学习"),
  "let's": ("/lets/", "LET'S", "让我们"),
  "lets": ("/lets/", "LET'S", "让我们"),
  "like": ("/laɪk/", "LIKE", "喜欢"),
  "live": ("/lɪv/", "LIVE", "居住"),
  "lot": ("/lɑːt/", "LOT", "很多"),
  "love": ("/lʌv/", "LOVE", "爱"),
  "me": ("/miː/", "ME", "我"),
  "meat": ("/miːt/", "MEAT", "肉"),
  "meet": ("/miːt/", "MEET", "见面"),
  "milk": ("/mɪlk/", "MILK", "牛奶"),
  "more": ("/mɔːr/", "MORE", "更多"),
  "morning": ("/ˈmɔːrnɪŋ/", "MOR-ning", "早上"),
  "much": ("/mʌtʃ/", "MUCH", "很多"),
  "music": ("/ˈmjuːzɪk/", "MU-sic", "音乐"),
  "my": ("/maɪ/", "MY", "我的"),
  "name": ("/neɪm/", "NAME", "名字"),
  "nice": ("/naɪs/", "NICE", "好的"),
  "night": ("/naɪt/", "NIGHT", "夜晚"),
  "no": ("/noʊ/", "NO", "不"),
  "nope": ("/noʊp/", "NOPE", "不（口语）"),
  "of": ("/ʌv/", "OF", "的"),
  "ok": ("/ˌoʊˈkeɪ/", "O-K", "好的"),
  "okay": ("/ˌoʊˈkeɪ/", "O-KAY", "好的"),
  "old": ("/oʊld/", "OLD", "年老的/岁"),
  "on": ("/ɑːn/", "ON", "在…上"),
  "orange": ("/ˈɔːrɪndʒ/", "OR-ange", "橙子"),
  "panda": ("/ˈpændə/", "PAN-da", "熊猫"),
  "play": ("/pleɪ/", "PLAY", "玩"),
  "please": ("/pliːz/", "PLEASE", "请"),
  "pleased": ("/pliːzd/", "PLEASED", "高兴的"),
  "problem": ("/ˈprɑːbləm/", "PROB-lem", "问题"),
  "puppy": ("/ˈpʌpi/", "PUP-py", "小狗"),
  "rabbit": ("/ˈræbɪt/", "RAB-bit", "兔子"),
  "race": ("/reɪs/", "RACE", "赛跑"),
  "rice": ("/raɪs/", "RICE", "米饭"),
  "ride": ("/raɪd/", "RIDE", "骑"),
  "run": ("/rʌn/", "RUN", "跑"),
  "running": ("/ˈrʌnɪŋ/", "RUN-ning", "跑步"),
  "say": ("/seɪ/", "SAY", "说"),
  "see": ("/siː/", "SEE", "看见"),
  "shoot": ("/ʃuːt/", "SHOOT", "投篮"),
  "sleep": ("/sliːp/", "SLEEP", "睡觉"),
  "sleepy": ("/ˈsliːpi/", "SLEE-py", "困的"),
  "so": ("/soʊ/", "SO", "如此"),
  "soccer": ("/ˈsɑːkər/", "SOC-cer", "足球"),
  "soon": ("/suːn/", "SOON", "很快"),
  "sorry": ("/ˈsɑːri/", "SOR-ry", "对不起"),
  "sunny": ("/ˈsʌni/", "SUN-ny", "晴朗的"),
  "sure": ("/ʃʊr/", "SURE", "当然"),
  "sweet": ("/swiːt/", "SWEET", "甜的/美好的"),
  "swim": ("/swɪm/", "SWIM", "游泳"),
  "swimming": ("/ˈswɪmɪŋ/", "SWIM-ming", "游泳"),
  "thank": ("/θæŋk/", "THANK", "感谢"),
  "thanks": ("/θæŋks/", "THANKS", "谢谢"),
  "that": ("/ðæt/", "THAT", "那"),
  "that's": ("/ðæts/", "THAT'S", "那是"),
  "the": ("/ðə/", "THE", "这/那"),
  "there": ("/ðer/", "THERE", "那里"),
  "this": ("/ðɪs/", "THIS", "这"),
  "throw": ("/θroʊ/", "THROW", "扔"),
  "time": ("/taɪm/", "TIME", "时间"),
  "to": ("/tuː/", "TO", "到"),
  "today": ("/təˈdeɪ/", "to-DAY", "今天"),
  "tomorrow": ("/təˈmɑːroʊ/", "to-MOR-row", "明天"),
  "too": ("/tuː/", "TOO", "也"),
  "very": ("/ˈveri/", "VER-y", "非常"),
  "want": ("/wɑːnt/", "WANT", "想要"),
  "weather": ("/ˈweðər/", "WEATH-er", "天气"),
  "welcome": ("/ˈwelkəm/", "WEL-come", "欢迎"),
  "what": ("/wʌt/", "WHAT", "什么"),
  "what's": ("/wʌts/", "WHAT'S", "什么（what's）"),
  "whats": ("/wʌts/", "WHAT'S", "什么（what's）"),
  "where": ("/wer/", "WHERE", "哪里"),
  "with": ("/wɪð/", "WITH", "和"),
  "worry": ("/ˈwɜːri/", "WOR-ry", "担心"),
  "yeah": ("/jeə/", "YEAH", "是啊"),
  "years": ("/jɪrz/", "YEARS", "年"),
  "yep": ("/jep/", "YEP", "是的"),
  "yes": ("/jes/", "YES", "是的"),
  "you": ("/juː/", "YOU", "你"),
  "you're": ("/jʊr/", "YOU'RE", "你是"),
  "your": ("/jʊr/", "YOUR", "你的"),
  "yummy": ("/ˈjʌmi/", "YUM-my", "好吃"),
  # extras from old phrase list
  "book": ("/bʊk/", "BOOK", "书"),
  "school": ("/skuːl/", "SCHOOL", "学校"),
  "friend": ("/frend/", "FRIEND", "朋友"),
  "water": ("/ˈwɔːtər/", "WA-ter", "水"),
  "sit": ("/sɪt/", "SIT", "坐"),
  "down": ("/daʊn/", "DOWN", "向下"),
  "stand": ("/stænd/", "STAND", "站"),
  "up": ("/ʌp/", "UP", "向上"),
  "open": ("/ˈoʊpən/", "O-pen", "打开"),
  "tom": ("/tɑːm/", "TOM", "汤姆"),
}

def sid(word):
    w = word.lower().replace("'", "")
    return re.sub(r'[^a-z0-9]+', '_', w).strip('_') or 'word'

async def save(text, path):
    await edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH).save(str(path))

# collect command vocab same as before
def words_from_text(s):
    return re.findall(r"[a-z]+(?:'[a-z]+)?", (s or '').lower())

vocab = set(META.keys())
for name in ['dialogs.json','animals.json','plays.json','foods.json','actions.json']:
    data = json.loads((base/name).read_text(encoding='utf-8'))
    blob = json.dumps(data, ensure_ascii=False).lower()
    # only english tokens from known files via structured walk
# rebuild precisely
vocab = set()

def add_many(s):
    for w in words_from_text(s):
        vocab.add(w)

data_d = json.loads((base/'dialogs.json').read_text(encoding='utf-8'))
for d in data_d['dialogs']:
    for t in d.get('triggers', []): add_many(t)
    add_many(d.get('reply',''))
data_a = json.loads((base/'animals.json').read_text(encoding='utf-8'))
for a in data_a['animals']:
    for t in a.get('triggers', []): add_many(t)
    add_many(a.get('reply','')); add_many(a.get('name',''))
data_p = json.loads((base/'plays.json').read_text(encoding='utf-8'))
for pitem in data_p['plays']:
    for t in pitem.get('triggers', []): add_many(t)
    add_many(pitem.get('reply',''))
add_many(data_p.get('generic',{}).get('reply',''))
data_f = json.loads((base/'foods.json').read_text(encoding='utf-8'))
for f in data_f['foods']:
    for t in f.get('triggers', []): add_many(t)
    add_many(f['name']); add_many(f.get('accept',{}).get('text','')); add_many(f.get('reject',{}).get('text',''))
data_act = json.loads((base/'actions.json').read_text(encoding='utf-8'))
for arr in data_act['actions'].values():
    for it in arr: add_many(it.get('text',''))

# keep useful phrase entries from old words.json
old = json.loads((base/'words.json').read_text(encoding='utf-8'))
phrase_keep = []
for it in old['items']:
    # keep multi-word phrases
    if ' ' in it['text'] or '?' in it['text']:
        phrase_keep.append(it)

missing_meta = sorted(w for w in vocab if w not in META)
if missing_meta:
    print('MISSING META', missing_meta)
    raise SystemExit(1)

async def main():
    items = []
    # phrases first
    for it in phrase_keep:
        items.append(it)
        # ensure audio exists
        # keep existing paths
    # single words
    for w in sorted(vocab):
        ipa, phonics, zh = META[w]
        special = {
            "i":"I","i'm":"I'm","im":"I'm","let's":"Let's","lets":"Let's",
            "what's":"What's","whats":"What's","that's":"That's","you're":"You're",
            "how's":"How's","it's":"It's","don't":"Don't","ok":"OK","okay":"Okay",
        }
        display = special.get(w, w.capitalize())
        _id = 'w_' + sid(w)
        audio = f'audio/{_id}.mp3'
        phonics_audio = f'audio/{_id}_phonics.mp3'
        # skip duplicate if phrase already covers exact same single? always add word entry
        # generate audio
        await save(display if display != "I'm" else "I'm", outdir / f'{_id}.mp3')
        # phonics: say phonics chunks then word
        chunks = [c for c in re.split(r'[-\s]+', phonics) if c]
        spoken = '. '.join(chunks) + '. ' + display + '.'
        await save(spoken, outdir / f'{_id}_phonics.mp3')
        # rough ipa segments: strip and split by spaces only; keep whole for chips via simple letters later
        segs = re.findall(r"[^\s/ˈˌ]+", ipa.strip('/'))
        items.append({
            "id": _id,
            "text": display,
            "ipa": ipa,
            "zh": zh,
            "phonics": phonics,
            "audio": audio,
            "phonicsAudio": phonics_audio,
            "ipaSegments": segs,
            "tags": ["command-vocab"],
        })
        print('word', display)

    # dedupe by lowercase text keeping first
    seen = set()
    uniq = []
    for it in items:
        key = it['text'].lower()
        if key in seen:
            continue
        seen.add(key)
        uniq.append(it)

    out = {"voice": VOICE, "items": uniq}
    (base/'words.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print('done items', len(uniq), 'vocab', len(vocab), 'phrases', len(phrase_keep))

asyncio.run(main())
