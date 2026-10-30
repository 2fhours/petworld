from pathlib import Path
import re
p = Path('/workspace/proto-page/index.html')
html = p.read_text(encoding='utf-8')

css = '''
    .fx-prop.bball { animation: ballBounce 3.2s ease-in-out forwards; }
    .fx-prop.swim { animation: swimBob 3.2s ease-in-out forwards; font-size: 48px; }
    .fx-prop.dance { animation: danceSpin 3.2s ease-in-out forwards; font-size: 48px; }
    .fx-prop.run { animation: runDash 3.2s linear forwards; font-size: 46px; }
    .fx-prop.jump { animation: jumpUp 3.2s ease-in-out forwards; font-size: 46px; }
    .fx-prop.frisbee { animation: frisbeeFly 3.2s ease-in-out forwards; font-size: 44px; }
    .fx-prop.bike { animation: bikeRide 3.2s linear forwards; font-size: 46px; }
    .fx-splash {
      position: fixed; z-index: 6; pointer-events: none; left: 0; right: 0; bottom: 18%;
      height: 18%; background: linear-gradient(180deg, rgba(100,180,255,0), rgba(80,170,255,0.35));
      opacity: 0; animation: splashIn 3.2s ease-out forwards;
    }
    @keyframes swimBob {
      0% { transform: translate(-50%, 20%) scale(0.7); opacity: 0; }
      20% { opacity: 1; transform: translate(-20%, -10%) scale(1); }
      50% { transform: translate(40px, 10%) scale(1.05) rotate(-8deg); }
      80% { transform: translate(100px, -5%) scale(1) rotate(6deg); }
      100% { transform: translate(150px, 15%) scale(0.9); opacity: 0; }
    }
    @keyframes danceSpin {
      0% { transform: translate(-50%, -50%) scale(0.6) rotate(0); opacity: 0; }
      20% { opacity: 1; transform: translate(-50%, -60%) scale(1.1) rotate(-20deg); }
      50% { transform: translate(-50%, -40%) scale(1) rotate(20deg); }
      80% { transform: translate(-50%, -70%) scale(1.15) rotate(-15deg); }
      100% { transform: translate(-50%, -30%) scale(0.8); opacity: 0; }
    }
    @keyframes runDash {
      0% { transform: translate(-80px, 0) scale(0.8); opacity: 0; }
      15% { opacity: 1; }
      100% { transform: translate(180px, 0) scale(1); opacity: 0; }
    }
    @keyframes jumpUp {
      0% { transform: translate(-50%, 0) scale(0.8); opacity: 0; }
      25% { opacity: 1; transform: translate(-50%, -90px) scale(1.1); }
      50% { transform: translate(-50%, -10px) scale(1); }
      75% { transform: translate(-50%, -70px) scale(1.05); }
      100% { transform: translate(-50%, 10px) scale(0.85); opacity: 0; }
    }
    @keyframes frisbeeFly {
      0% { transform: translate(-60px, 20px) rotate(0); opacity: 0; }
      20% { opacity: 1; }
      100% { transform: translate(170px, -80px) rotate(540deg); opacity: 0; }
    }
    @keyframes bikeRide {
      0% { transform: translate(-90px, 10px); opacity: 0; }
      15% { opacity: 1; }
      100% { transform: translate(190px, -5px); opacity: 0; }
    }
    @keyframes splashIn {
      0% { opacity: 0; }
      20% { opacity: 1; }
      100% { opacity: 0; }
    }
'''
if '.fx-prop.swim' not in html:
    if '.fx-prop.ball {' not in html:
        raise SystemExit('ball css missing')
    html = html.replace('    .fx-prop.ball {', css + '    .fx-prop.ball {')

plays_js = r'''
    let PLAYS = null;
    async function loadPlays() {
      const res = await fetch('plays.json');
      PLAYS = await res.json();
    }
    loadPlays();

    function findPlay(text) {
      if (!PLAYS || !PLAYS.plays) return null;
      const t = (text || '').toLowerCase().trim();
      if (!t) return null;
      let best = null, bestLen = 0;
      for (const p of PLAYS.plays) {
        for (const trig of p.triggers) {
          const g = trig.toLowerCase();
          if (t.includes(g) && g.length >= bestLen) {
            best = p; bestLen = g.length;
          }
        }
      }
      return best;
    }

    function playVisual(play) {
      const x = state.x, y = state.y - 70;
      const id = play && play.id;
      document.querySelectorAll('.fx-splash').forEach((el) => el.remove());
      if (id === 'swim') {
        const splash = document.createElement('div');
        splash.className = 'fx-splash';
        document.body.appendChild(splash);
        setTimeout(() => splash.remove(), 3200);
        spawnProp('🏊', 'swim', x, y + 10, 3400);
        burst(['💧', '🌊', '✨'], x, y);
      } else if (id === 'basketball') {
        spawnProp('🏀', 'bball', x + 30, y + 20, 3400);
        burst(['✨', '⭐', '💥'], x, y);
      } else if (id === 'soccer') {
        spawnProp('⚽', 'ball', x + 30, y + 20, 3400);
        burst(['✨', '⭐', '💫'], x, y);
      } else if (id === 'dance') {
        spawnProp('💃', 'dance', x, y, 3400);
        setTimeout(() => spawnProp('🎵', 'dance', x + 40, y - 20, 3000), 200);
        burst(['🎶', '✨', '💜'], x, y);
      } else if (id === 'run') {
        spawnProp('🏃', 'run', x, y + 10, 3400);
        burst(['💨', '✨', '⭐'], x, y);
      } else if (id === 'jump') {
        spawnProp('🤸', 'jump', x, y, 3400);
        burst(['✨', '⭐', '💫'], x, y);
      } else if (id === 'frisbee') {
        spawnProp('🥏', 'frisbee', x, y, 3400);
        burst(['✨', '💨'], x, y);
      } else if (id === 'bike') {
        spawnProp('🚲', 'bike', x, y + 10, 3400);
        burst(['✨', '💨', '⭐'], x, y);
      } else {
        spawnProp('⚽', 'ball', x + 30, y + 20, 3400);
        burst(['✨', '⭐', '💫'], x, y);
      }
      setHappy(2400);
    }

    function startPlay(play) {
      if (state.mode === 'sleep') pet.classList.remove('sleep');
      holdStill(4000);
      if (!play && PLAYS && PLAYS.plays && PLAYS.plays.length) {
        play = PLAYS.plays[Math.floor(Math.random() * PLAYS.plays.length)];
      }
      playVisual(play);
      if (play && play.audio) {
        playCachedAudio(play.audio);
        say(play.reply || "Let's play!", 4400);
      } else if (PLAYS && PLAYS.generic) {
        playCachedAudio(PLAYS.generic.audio);
        say(PLAYS.generic.reply, 4400);
      }
    }

    function maybeHandlePlayCommand(text) {
      const t = (text || '').toLowerCase().trim();
      if (!t) return false;
      const play = findPlay(t);
      if (play) {
        startPlay(play);
        return true;
      }
      if (/\b(let's play|lets play|play with me|come and play)\b/.test(t) || /玩耍|一起玩|玩游戏/.test(text || '')) {
        startPlay(null);
        return true;
      }
      return false;
    }

'''

if 'function startPlay' not in html:
    if 'let ANIMALS = null;' not in html:
        raise SystemExit('ANIMALS anchor missing')
    html = html.replace('    let ANIMALS = null;', plays_js + '\n    let ANIMALS = null;')

# actionVisual play branch -> startPlay
html2, n = re.subn(
    r"if \(kind === 'play' \|\| kind === 'lets_play'\) \{\n        spawnProp\('⚽', 'ball', x \+ 30, y \+ 20, 3400\);\n        burst\(\['✨', '⭐', '💫'\], x, y\);\n        setHappy\(2400\);\n      \}",
    "if (kind === 'play' || kind === 'lets_play') {\n        startPlay(null);\n        return;\n      }",
    html,
    count=1,
)
print('actionVisual repl', n)
html = html2

# act play
html2, n = re.subn(
    r"\} else if \(kind === 'play'\) \{\n        if \(state\.mode === 'sleep'\) pet\.classList\.remove\('sleep'\);\n        holdStill\(4000\);\n        setHappy\(2000\);\n        actionVisual\('play'\);\n        // no knockback while showing play effect\n        speakAction\('play'\);\n",
    "} else if (kind === 'play') {\n        startPlay(null);\n",
    html,
    count=1,
)
print('act play repl', n)
html = html2

# speakDialog
html2, n = re.subn(
    r"if \(d\.id === 'lets_play' \|\| d\.id === 'play'\) \{\n        if \(state\.mode === 'sleep'\) pet\.classList\.remove\('sleep'\);\n        holdStill\(4000\);\n        actionVisual\('play'\);\n",
    "if (d.id === 'lets_play' || d.id === 'play') {\n        startPlay(null);\n        return;\n",
    html,
    count=1,
)
print('speakDialog repl', n)
html = html2

# recognition
if 'maybeHandlePlayCommand' not in html.split('if (switched) return;')[1][:500]:
    if 'if (switched) return;' not in html:
        raise SystemExit('switched marker missing')
    html = html.replace(
        '        if (switched) return;\n        let matched = null;',
        '        if (switched) return;\n        let played = false;\n        for (const a of alts) {\n          if (maybeHandlePlayCommand(a)) { played = true; break; }\n        }\n        if (played) return;\n        let matched = null;',
        1,
    )
    print('recognition ok')

# preload
if 'PLAYS.plays.forEach' not in html:
    html = html.replace(
        '''        if (ANIMALS && ANIMALS.animals) {
          ANIMALS.animals.forEach((a) => add(a.audio));
        }
''',
        '''        if (ANIMALS && ANIMALS.animals) {
          ANIMALS.animals.forEach((a) => add(a.audio));
        }
        if (PLAYS && PLAYS.plays) {
          PLAYS.plays.forEach((p) => add(p.audio));
          if (PLAYS.generic) add(PLAYS.generic.audio);
        }
'''
    )
    print('preload ok')

# dialog list
if 'data-play' not in html:
    html = html.replace(
        '''      let animalHtml = '';
      if (ANIMALS && ANIMALS.animals) {
''',
        '''      let playHtml = '';
      if (PLAYS && PLAYS.plays) {
        playHtml = `<div class="dlg-tip" style="margin-top:10px">Play (say: swim / basketball)</div>` + PLAYS.plays.map((p) => {
          return `<button type="button" class="dlg-item" data-play="${p.id}">
            <span class="say">Say: ${p.triggers[0]} ${p.emoji}</span>
            <span class="reply">Reply: ${p.reply}</span>
          </button>`;
        }).join('');
      }
      let animalHtml = '';
      if (ANIMALS && ANIMALS.animals) {
'''
    )
    html = html.replace(
        'box.innerHTML = dialogHtml + animalHtml + foodHtml;',
        'box.innerHTML = dialogHtml + playHtml + animalHtml + foodHtml;',
    )
    html = html.replace(
        '''      const animalBtn = e.target.closest('button[data-animal]');
''',
        '''      const playBtn = e.target.closest('button[data-play]');
      if (playBtn && PLAYS) {
        const pl = PLAYS.plays.find((x) => x.id === playBtn.dataset.play);
        if (pl) startPlay(pl);
        return;
      }
      const animalBtn = e.target.closest('button[data-animal]');
'''
    )
    print('dialog list ok')

p.write_text(html, encoding='utf-8')
assert 'function startPlay' in html
assert 'maybeHandlePlayCommand' in html
assert '.fx-prop.swim' in html
assert 'data-play' in html
print('ALL OK')
