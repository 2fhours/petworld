from pathlib import Path
p = Path('/workspace/proto-page/index.html')
html = p.read_text(encoding='utf-8')

# CSS for collapse toggles
extra_css = '''
    .dock-toggle {
      position: fixed; z-index: 10; appearance: none; border: 1px solid rgba(255,255,255,0.14);
      border-radius: 999px; padding: 8px 12px; font: inherit; font-size: 12px;
      color: #e2e8f0; background: rgba(15,23,42,0.72); backdrop-filter: blur(10px);
      cursor: pointer;
    }
    .dock-toggle.top { top: 14px; right: 14px; }
    .dock-toggle.learn-btn { right: 14px; top: 54px; }
    .dock-toggle.bottom { left: 50%; bottom: 14px; transform: translateX(-50%); }
    body.hide-picker .picker, body.hide-picker .hint { display: none; }
    body.hide-learn .learn { display: none; }
    body.hide-actions .panel { display: none; }
    body.hide-picker .dock-toggle.top { opacity: 0.85; }
    .learn.collapsed-inner .list { display: none; }

'''
if '.dock-toggle {' not in html:
    html = html.replace('    .panel {', extra_css + '    .panel {')

# Add toggle buttons near body start content
toggles = '''
  <button type="button" class="dock-toggle top" id="togglePicker" title="形象菜单">形象</button>
  <button type="button" class="dock-toggle learn-btn" id="toggleLearn" title="英语菜单">英语</button>
  <button type="button" class="dock-toggle bottom" id="toggleActions" title="操作菜单">操作</button>

'''
if 'id="togglePicker"' not in html:
    html = html.replace('<div class="picker" id="picker"></div>', toggles + '<div class="picker" id="picker"></div>')

# Add 拼读 button
if 'id="btnPhonics"' not in html:
    html = html.replace(
        '<button type="button" class="primary" id="btnPlay">▶ 标准发音</button>\n      <button type="button" id="btnSlow">慢速再听</button>',
        '<button type="button" class="primary" id="btnPlay">▶ 标准发音</button>\n      <button type="button" id="btnPhonics">拼读</button>\n      <button type="button" id="btnSlow">慢速再听</button>'
    )

# Replace playWord and related JS more carefully
old_play = '''    function playWord({ slow = false } = {}) {
      const it = WORDS.items[wordIndex];
      if (!it) return;
      if (currentAudio) {
        currentAudio.pause();
        currentAudio = null;
      }
      const audio = new Audio(it.audio);
      audio.playbackRate = slow ? 0.78 : 1;
      currentAudio = audio;
      audio.play().catch(() => {});
      say(it.text);
      setHappy(700);
    }

    document.getElementById('btnPlay').addEventListener('click', () => playWord());
    document.getElementById('btnSlow').addEventListener('click', () => playWord({ slow: true }));
    document.getElementById('btnNext').addEventListener('click', () => { showWord(wordIndex + 1); playWord(); });
'''

new_play = '''    function stopAudio() {
      if (currentAudio) {
        currentAudio.pause();
        currentAudio = null;
      }
    }

    function playWord({ slow = false, phonics = false } = {}) {
      const it = WORDS.items[wordIndex];
      if (!it) return;
      stopAudio();
      const src = phonics && it.phonicsAudio ? it.phonicsAudio : it.audio;
      const audio = new Audio(src);
      audio.playbackRate = slow ? 0.78 : 1;
      currentAudio = audio;
      audio.play().catch(() => {});
      say(phonics ? ('拼读：' + it.phonics) : it.text);
      setHappy(700);
    }

    function playRandomWord() {
      if (!WORDS.items.length) return;
      const i = Math.floor(Math.random() * WORDS.items.length);
      showWord(i);
      playWord();
    }

    document.getElementById('btnPlay').addEventListener('click', () => playWord());
    document.getElementById('btnPhonics').addEventListener('click', () => playWord({ phonics: true }));
    document.getElementById('btnSlow').addEventListener('click', () => playWord({ slow: true }));
    document.getElementById('btnNext').addEventListener('click', () => { showWord(wordIndex + 1); playWord(); });

    function applyDock(key, hidden) {
      document.body.classList.toggle('hide-' + key, hidden);
      localStorage.setItem('proto-hide-' + key, hidden ? '1' : '0');
      const map = { picker: 'togglePicker', learn: 'toggleLearn', actions: 'toggleActions' };
      const labels = { picker: '形象', learn: '英语', actions: '操作' };
      const btn = document.getElementById(map[key]);
      if (btn) btn.textContent = (hidden ? '展开' : '收起') + labels[key];
    }
    ['picker','learn','actions'].forEach((key) => {
      applyDock(key, localStorage.getItem('proto-hide-' + key) === '1');
    });
    document.getElementById('togglePicker').addEventListener('click', () => {
      applyDock('picker', !document.body.classList.contains('hide-picker'));
    });
    document.getElementById('toggleLearn').addEventListener('click', () => {
      applyDock('learn', !document.body.classList.contains('hide-learn'));
    });
    document.getElementById('toggleActions').addEventListener('click', () => {
      applyDock('actions', !document.body.classList.contains('hide-actions'));
    });
'''

if old_play not in html:
    raise SystemExit('playWord block not found')
html = html.replace(old_play, new_play)

# Change short-press endPress to random read instead of act('pet')
old_end = '''    function endPress() {
      if (!state.pressing) return;
      const wasFollow = state.mode === 'follow';
      state.pressing = false;
      clearTimeout(state.longPressTimer);
      if (wasFollow) {
        state.mode = 'wander';
        pickWanderTarget();
        say('我自己逛逛');
      } else {
        act('pet');
      }
    }
'''

new_end = '''    function endPress() {
      if (!state.pressing) return;
      const wasFollow = state.mode === 'follow';
      state.pressing = false;
      clearTimeout(state.longPressTimer);
      if (wasFollow) {
        state.mode = 'wander';
        pickWanderTarget();
        say('我自己逛逛');
      } else {
        // short click: randomly pick and read an English item
        playRandomWord();
      }
    }
'''

if old_end not in html:
    raise SystemExit('endPress block not found')
html = html.replace(old_end, new_end)

p.write_text(html, encoding='utf-8')
print('ok')
for s in ['btnPhonics', 'playRandomWord', 'togglePicker', 'hide-learn', 'phonicsAudio']:
    print(s, s in html)
