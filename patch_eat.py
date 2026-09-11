from pathlib import Path
p = Path('/workspace/proto-page/index.html')
html = p.read_text(encoding='utf-8')

# CSS for reject shake
css = '''
    .fx-prop.reject { animation: foodReject 1.3s ease-out forwards; }
    #pet.reject-shake .figure { animation: rejectShake 0.55s ease-in-out; }
    @keyframes foodReject {
      0% { transform: translate(-50%, -40%) scale(0.6) rotate(0deg); opacity: 0; }
      25% { opacity: 1; transform: translate(-50%, 0) scale(1.05) rotate(-8deg); }
      55% { transform: translate(40px, -20%) scale(1) rotate(12deg); }
      100% { transform: translate(90px, -80%) scale(0.7) rotate(25deg); opacity: 0; }
    }
    @keyframes rejectShake {
      0%,100% { transform: scaleX(var(--face,1)) translateX(0); }
      20% { transform: scaleX(var(--face,1)) translateX(-8px); }
      40% { transform: scaleX(var(--face,1)) translateX(8px); }
      60% { transform: scaleX(var(--face,1)) translateX(-6px); }
      80% { transform: scaleX(var(--face,1)) translateX(6px); }
    }
'''
if 'foodReject' not in html:
    html = html.replace('    .fx-prop.food {', css + '    .fx-prop.food {')

# Load foods + eat helpers after loadDialogs area
eat_js = r'''
    let FOODS = null;
    async function loadFoods() {
      const res = await fetch('foods.json');
      FOODS = await res.json();
    }
    loadFoods();

    function findFood(text) {
      if (!FOODS || !FOODS.foods) return null;
      const t = (text || '').toLowerCase();
      // prefer longer trigger matches
      let best = null, bestLen = 0;
      for (const f of FOODS.foods) {
        for (const trig of f.triggers) {
          const g = trig.toLowerCase();
          if (t.includes(g) && g.length >= bestLen) {
            best = f; bestLen = g.length;
          }
        }
      }
      return best;
    }

    function petLikesFood(food) {
      if (!FOODS || !food) return true;
      const taste = FOODS.petTaste[state.form] || { like: [], dislike: [] };
      if (taste.dislike && taste.dislike.includes(food.id)) return false;
      if (taste.like && taste.like.length && !taste.like.includes(food.id)) {
        // not explicitly liked and not disliked -> mild like for fruits etc.
        // if it's in another pet specialty only, still allow unless disliked
        return true;
      }
      return true;
    }

    function playLine(line) {
      if (!line) return;
      if (currentAudio) { currentAudio.pause(); currentAudio = null; }
      const audio = new Audio(line.audio);
      currentAudio = audio;
      audio.play().catch(() => {});
      say(line.text, 2400);
    }

    function eatFood(food) {
      if (!food) {
        holdStill(1400);
        playLine(FOODS && FOODS.askFood);
        return;
      }
      const likes = petLikesFood(food);
      holdStill(likes ? 2000 : 1800);
      const x = state.x, y = state.y - 70;
      if (likes) {
        spawnProp(food.emoji, 'food', x, y - 10, 1500);
        setTimeout(() => burst(['😋', '✨', '💖'], x, y), 500);
        setHappy(1200);
        playLine(food.accept || (FOODS && FOODS.genericAccept));
      } else {
        spawnProp(food.emoji, 'reject', x, y - 10, 1400);
        pet.classList.add('reject-shake');
        setTimeout(() => pet.classList.remove('reject-shake'), 600);
        burst(['🙅', '💨', '✖️'], x, y);
        playLine(food.reject || (FOODS && FOODS.genericReject));
      }
    }

    function maybeHandleEatCommand(text) {
      const t = (text || '').toLowerCase().trim();
      if (!t) return false;
      // eat / have / feed + food
      const isEat = /\b(eat|have|feed)\b/.test(t) || t.startsWith('eat ') || t.includes(' eat ');
      if (!isEat) {
        // bare food name only if preceded by eat intent words already required
        return false;
      }
      const food = findFood(t);
      eatFood(food);
      return true;
    }

'''

if 'function eatFood' not in html:
    html = html.replace('    let DIALOGS = null;', eat_js + '\n    let DIALOGS = null;')

# In recognition.onresult, try eat before dialog match
old_result = '''      recognition.onresult = (ev) => {
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
'''

new_result = '''      recognition.onresult = (ev) => {
        const alts = [];
        for (let i = 0; i < ev.results[0].length; i++) alts.push(ev.results[0][i].transcript);
        lastHeard = alts[0] || '';
        // Eat commands first: "eat apple"
        let ate = false;
        for (const a of alts) {
          if (maybeHandleEatCommand(a)) { ate = true; break; }
        }
        if (ate) return;
        let matched = null;
        for (const a of alts) {
          matched = matchDialog(a);
          if (matched && matched.id !== 'fallback') break;
        }
        if (!matched) matched = matchDialog(lastHeard);
        speakDialog(matched);
      };
'''

if old_result not in html:
    raise SystemExit('onresult missing')
html = html.replace(old_result, new_result)

# Extend dialog list to include eat foods section
old_render = '''    function renderDialogList() {
      const box = document.getElementById('dlgList');
      if (!box || !DIALOGS || !DIALOGS.dialogs) return;
      box.innerHTML = DIALOGS.dialogs
        .filter((d) => d.id !== 'fallback')
        .map((d) => {
          const say = (d.triggers && d.triggers[0]) ? d.triggers[0] : d.id;
          const more = (d.triggers && d.triggers.length > 1)
            ? ` · also: ${d.triggers.slice(1, 3).join(', ')}`
            : '';
          return `<button type="button" class="dlg-item" data-dlg="${d.id}">
            <span class="say">Say: ${say}${more}</span>
            <span class="reply">Reply: ${d.reply}${d.zh ? '（' + d.zh + '）' : ''}</span>
          </button>`;
        }).join('');
    }
'''

new_render = '''    function renderDialogList() {
      const box = document.getElementById('dlgList');
      if (!box || !DIALOGS || !DIALOGS.dialogs) return;
      const dialogHtml = DIALOGS.dialogs
        .filter((d) => d.id !== 'fallback')
        .map((d) => {
          const say = (d.triggers && d.triggers[0]) ? d.triggers[0] : d.id;
          const more = (d.triggers && d.triggers.length > 1)
            ? ` · also: ${d.triggers.slice(1, 3).join(', ')}`
            : '';
          return `<button type="button" class="dlg-item" data-dlg="${d.id}">
            <span class="say">Say: ${say}${more}</span>
            <span class="reply">Reply: ${d.reply}${d.zh ? '（' + d.zh + '）' : ''}</span>
          </button>`;
        }).join('');
      let foodHtml = '';
      if (FOODS && FOODS.foods) {
        foodHtml = `<div class="dlg-tip" style="margin-top:10px">Eat foods (try: eat apple)</div>` + FOODS.foods.map((f) => {
          return `<button type="button" class="dlg-item" data-eat="${f.id}">
            <span class="say">Say: eat ${f.name} ${f.emoji}</span>
            <span class="reply">Like / dislike depends on pet</span>
          </button>`;
        }).join('');
      }
      box.innerHTML = dialogHtml + foodHtml;
    }
'''

if old_render not in html:
    raise SystemExit('renderDialogList missing')
html = html.replace(old_render, new_render)

# Click handler for eat items in list
old_click = '''    document.getElementById('dlgList').addEventListener('click', (e) => {
      const btn = e.target.closest('button[data-dlg]');
      if (!btn || !DIALOGS) return;
      const d = DIALOGS.dialogs.find((x) => x.id === btn.dataset.dlg);
      if (d) speakDialog(d);
    });
'''

new_click = '''    document.getElementById('dlgList').addEventListener('click', (e) => {
      const eatBtn = e.target.closest('button[data-eat]');
      if (eatBtn && FOODS) {
        const f = FOODS.foods.find((x) => x.id === eatBtn.dataset.eat);
        if (f) eatFood(f);
        return;
      }
      const btn = e.target.closest('button[data-dlg]');
      if (!btn || !DIALOGS) return;
      const d = DIALOGS.dialogs.find((x) => x.id === btn.dataset.dlg);
      if (d) speakDialog(d);
    });
'''

if old_click not in html:
    raise SystemExit('dlg click missing')
html = html.replace(old_click, new_click)

# Reload dialog list after foods loaded too
html = html.replace('    loadFoods();', '    loadFoods().then(() => { if (document.getElementById("dlgPanel").classList.contains("open")) renderDialogList(); });')

p.write_text(html, encoding='utf-8')
print('patched', 'eatFood' in html, 'maybeHandleEatCommand' in html)
