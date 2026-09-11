from pathlib import Path
p = Path('/workspace/proto-page/index.html')
html = p.read_text(encoding='utf-8')

css = '''
    .mic-wrap {
      position: fixed; left: 16px; bottom: 22px; z-index: 8;
      display: flex; flex-direction: column; gap: 8px; align-items: flex-start;
    }
    body.hide-actions .mic-wrap { bottom: 64px; }
    .mic-btn {
      appearance: none; border: 1px solid rgba(255,255,255,0.14);
      border-radius: 999px; padding: 12px 16px; font: inherit; font-size: 14px;
      color: #e2e8f0; background: rgba(15,23,42,0.72); backdrop-filter: blur(10px);
      cursor: pointer; display: inline-flex; align-items: center; gap: 8px;
    }
    .mic-btn.listening {
      background: rgba(239,68,68,0.28); border-color: rgba(248,113,113,0.7);
      box-shadow: 0 0 0 4px rgba(239,68,68,0.15);
      animation: pulse 1.2s ease-in-out infinite;
    }
    .mic-status {
      max-width: min(280px, 70vw); font-size: 12px; color: rgba(226,232,240,0.7);
      background: rgba(15,23,42,0.55); border: 1px solid rgba(255,255,255,0.08);
      border-radius: 12px; padding: 8px 10px; line-height: 1.45;
    }
'''
if '.mic-wrap' not in html:
    html = html.replace('    .dock-toggle {', css + '    .dock-toggle {')

mic_html = '''
  <div class="mic-wrap" id="micWrap">
    <button type="button" class="mic-btn" id="micBtn">🎤 说话</button>
    <div class="mic-status" id="micStatus">点一下，用中文或英语说预设指令（如「你好」「Let's play」）</div>
  </div>

'''
if 'id="micBtn"' not in html:
    html = html.replace('  <div class="panel">', mic_html + '  <div class="panel">')

js = r'''
    // Voice dialog: mic -> match preset -> English reply (neural audio)
    let DIALOGS = null;
    async function loadDialogs() {
      const res = await fetch('dialogs.json');
      DIALOGS = await res.json();
    }
    loadDialogs();

    function matchDialog(text) {
      if (!DIALOGS || !DIALOGS.dialogs) return null;
      const t = (text || '').toLowerCase().trim();
      if (!t) return null;
      let best = null;
      let bestLen = 0;
      for (const d of DIALOGS.dialogs) {
        if (d.id === 'fallback') continue;
        for (const trig of d.triggers) {
          const g = trig.toLowerCase();
          if (t.includes(g) && g.length >= bestLen) {
            best = d;
            bestLen = g.length;
          }
        }
      }
      return best || DIALOGS.dialogs.find((d) => d.id === 'fallback');
    }

    function speakDialog(d) {
      if (!d) return;
      if (currentAudio) { currentAudio.pause(); currentAudio = null; }
      const audio = new Audio(d.audio);
      currentAudio = audio;
      audio.play().catch(() => {});
      say(d.reply, 2600);
      setHappy(900);
      if (d.id === 'play') {
        state.vx += (Math.random() - 0.5) * 8;
        if (state.mode === 'sleep') {
          pet.classList.remove('sleep');
          state.mode = 'wander';
        }
      } else if (d.id === 'sleep') {
        state.mode = 'sleep';
        pet.classList.add('sleep');
        pet.classList.remove('walk', 'happy');
        state.vx = 0; state.vy = 0;
      } else if (d.id === 'hungry') {
        hearts(2);
      } else if (d.id === 'love' || d.id === 'greet') {
        hearts(3);
      }
      const st = document.getElementById('micStatus');
      if (st) st.textContent = `你说：${lastHeard || '…'} → 回复：${d.reply}`;
    }

    let lastHeard = '';
    let recognizing = false;
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition = null;
    if (SpeechRec) {
      recognition = new SpeechRec();
      recognition.lang = 'zh-CN';
      recognition.interimResults = false;
      recognition.maxAlternatives = 3;
      recognition.continuous = false;
      recognition.onstart = () => {
        recognizing = true;
        document.getElementById('micBtn').classList.add('listening');
        document.getElementById('micBtn').textContent = '🎤 正在听…';
        document.getElementById('micStatus').textContent = '请说话（中文或英语预设指令）';
      };
      recognition.onend = () => {
        recognizing = false;
        document.getElementById('micBtn').classList.remove('listening');
        document.getElementById('micBtn').textContent = '🎤 说话';
      };
      recognition.onerror = (e) => {
        recognizing = false;
        document.getElementById('micBtn').classList.remove('listening');
        document.getElementById('micBtn').textContent = '🎤 说话';
        const msg = {
          'not-allowed': '麦克风权限被拒绝，请在浏览器允许麦克风后重试',
          'no-speech': '没有听到声音，请再试一次',
          'audio-capture': '找不到麦克风设备',
          'network': '语音识别需要网络，请检查网络后重试'
        }[e.error] || ('识别出错：' + e.error);
        document.getElementById('micStatus').textContent = msg;
      };
      recognition.onresult = (ev) => {
        const alts = [];
        for (let i = 0; i < ev.results[0].length; i++) alts.push(ev.results[0][i].transcript);
        lastHeard = alts[0] || '';
        let matched = null;
        for (const a of alts) {
          matched = matchDialog(a);
          if (matched && matched.id !== 'fallback') break;
        }
        if (!matched) matched = matchDialog(lastHeard);
        speakDialog(matched);
      };
    }

    document.getElementById('micBtn').addEventListener('click', () => {
      if (!recognition) {
        document.getElementById('micStatus').textContent = '当前浏览器不支持语音识别，请用 Chrome / Edge';
        return;
      }
      if (recognizing) {
        recognition.stop();
        return;
      }
      try {
        // Prefer Chinese; English triggers still match via lowercase includes
        recognition.lang = 'zh-CN';
        recognition.start();
      } catch (err) {
        document.getElementById('micStatus').textContent = '无法启动麦克风，请重试';
      }
    });

'''

if 'matchDialog' not in html:
    # insert before loadActions or after currentAudio
    anchor = '    let ACTION_LINES = null;'
    if anchor not in html:
        raise SystemExit('anchor missing')
    html = html.replace(anchor, js + '\n' + anchor)

p.write_text(html, encoding='utf-8')
print('ok', 'matchDialog' in html, 'micBtn' in html)
