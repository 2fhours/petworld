import asyncio, json, os
import edge_tts

VOICE = "en-US-JennyNeural"
outdir = "/workspace/proto-page/audio"

# Elementary English conversation: English triggers + English replies
DIALOG = [
  {
    "id": "hello",
    "triggers": ["hello", "hi", "hey", "hello there"],
    "reply": "Hello! Nice to meet you.",
    "zh": "你好！很高兴见到你。"
  },
  {
    "id": "good_morning",
    "triggers": ["good morning", "morning"],
    "reply": "Good morning! Have a nice day.",
    "zh": "早上好！祝你今天愉快。"
  },
  {
    "id": "good_afternoon",
    "triggers": ["good afternoon", "afternoon"],
    "reply": "Good afternoon!",
    "zh": "下午好！"
  },
  {
    "id": "good_evening",
    "triggers": ["good evening", "evening"],
    "reply": "Good evening!",
    "zh": "晚上好！"
  },
  {
    "id": "good_night",
    "triggers": ["good night", "goodnight", "night night"],
    "reply": "Good night. Sweet dreams.",
    "zh": "晚安，做个好梦。"
  },
  {
    "id": "how_are_you",
    "triggers": ["how are you", "how do you do", "how's it going", "how are you doing"],
    "reply": "I'm fine, thank you. And you?",
    "zh": "我很好，谢谢。你呢？"
  },
  {
    "id": "im_fine",
    "triggers": ["i'm fine", "im fine", "i am fine", "i'm good", "im good"],
    "reply": "Great! I'm happy for you.",
    "zh": "太好了！我为你高兴。"
  },
  {
    "id": "whats_your_name",
    "triggers": ["what's your name", "whats your name", "what is your name", "your name"],
    "reply": "My name is Buddy.",
    "zh": "我叫 Buddy。"
  },
  {
    "id": "nice_to_meet_you",
    "triggers": ["nice to meet you", "glad to meet you", "pleased to meet you"],
    "reply": "Nice to meet you too.",
    "zh": "我也很高兴认识你。"
  },
  {
    "id": "how_old_are_you",
    "triggers": ["how old are you", "what's your age", "whats your age"],
    "reply": "I am five years old.",
    "zh": "我五岁了。"
  },
  {
    "id": "where_are_you_from",
    "triggers": ["where are you from", "where do you live"],
    "reply": "I am from China.",
    "zh": "我来自中国。"
  },
  {
    "id": "thank_you",
    "triggers": ["thank you", "thanks", "thank you very much", "thanks a lot"],
    "reply": "You're welcome.",
    "zh": "不客气。"
  },
  {
    "id": "please",
    "triggers": ["please", "excuse me"],
    "reply": "Sure. No problem.",
    "zh": "当然，没问题。"
  },
  {
    "id": "sorry",
    "triggers": ["sorry", "i'm sorry", "im sorry", "excuse me sorry"],
    "reply": "That's okay. Don't worry.",
    "zh": "没关系，别担心。"
  },
  {
    "id": "yes",
    "triggers": ["yes", "yeah", "yep", "okay", "ok"],
    "reply": "Okay!",
    "zh": "好的！"
  },
  {
    "id": "no",
    "triggers": ["no", "nope", "no thank you", "no thanks"],
    "reply": "Okay. No problem.",
    "zh": "好的，没问题。"
  },
  {
    "id": "lets_play",
    "triggers": ["let's play", "lets play", "play with me", "come and play"],
    "reply": "Let's play! This is fun.",
    "zh": "我们一起玩吧！真好玩。"
  },
  {
    "id": "i_am_hungry",
    "triggers": ["i'm hungry", "im hungry", "i am hungry", "i want food", "feed me"],
    "reply": "Yummy! I like apples.",
    "zh": "好好吃！我喜欢苹果。"
  },
  {
    "id": "i_am_sleepy",
    "triggers": ["i'm sleepy", "im sleepy", "i am sleepy", "i want to sleep", "go to bed"],
    "reply": "Good night. Sweet dreams.",
    "zh": "晚安，做个好梦。"
  },
  {
    "id": "i_love_you",
    "triggers": ["i love you", "love you"],
    "reply": "I love you too.",
    "zh": "我也爱你。"
  },
  {
    "id": "how_is_the_weather",
    "triggers": ["how's the weather", "how is the weather", "what's the weather", "whats the weather"],
    "reply": "It's sunny today.",
    "zh": "今天是晴天。"
  },
  {
    "id": "what_time_is_it",
    "triggers": ["what time is it", "what's the time", "whats the time"],
    "reply": "It's time to learn English.",
    "zh": "现在是学英语的时间。"
  },
  {
    "id": "can_you_help_me",
    "triggers": ["can you help me", "help me", "help"],
    "reply": "Of course. I can help you.",
    "zh": "当然，我可以帮你。"
  },
  {
    "id": "see_you",
    "triggers": ["see you", "see you later", "see you soon"],
    "reply": "See you later!",
    "zh": "回头见！"
  },
  {
    "id": "bye",
    "triggers": ["bye", "bye bye", "goodbye", "good bye"],
    "reply": "Bye bye. Have a good day.",
    "zh": "拜拜，祝你今天愉快。"
  },
  {
    "id": "fallback",
    "triggers": [],
    "reply": "Sorry, please say it again.",
    "zh": "抱歉，请再说一次。"
  },
]

async def main():
    for item in DIALOG:
        path = os.path.join(outdir, f"dlg_{item['id']}.mp3")
        await edge_tts.Communicate(item["reply"], VOICE, rate="-8%").save(path)
        item["audio"] = f"audio/dlg_{item['id']}.mp3"
        print("ok", item["id"])
    json.dump({"voice": VOICE, "dialogs": DIALOG}, open("/workspace/proto-page/dialogs.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("done", len(DIALOG))

asyncio.run(main())
