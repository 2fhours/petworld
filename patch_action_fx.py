from pathlib import Path
p = Path('/workspace/proto-page/index.html')
html = p.read_text(encoding='utf-8')

css = '''
    .fx-prop {
      position: fixed; z-index: 7; pointer-events: none;
      font-size: 42px; line-height: 1;
      filter: drop-shadow(0 8px 16px rgba(0,0,0,0.35));
    }
    .fx-prop.ball { animation: ballBounce 1.6s ease-in-out forwards; }
    .fx-prop.food { animation: foodDrop 1.4s ease-out forwards; font-size: 46px; }
    .fx-prop.zzz { animation: zzzFloat 2.2s ease-out forwards; font-size: 28px; color: #c4b5fd; }
    .fx-prop.pethand { animation: petHand 1.1s ease-out forwards; font-size: 36px; }
    .fx-burst {
      position: fixed; z-index: 7; pointer-events: none; font-size: 22px;
      animation: burstOut 0.9s ease-out forwards;
    }
    @keyframes ballBounce {
      0% { transform: translate(-50%, -50%) scale(0.6); opacity: 0; }
      15% { opacity: 1; transform: translate(-50%, -50%) scale(1.05); }
      35% { transform: translate(40px, -90px) scale(1); }
      55% { transform: translate(90px, 10px) scale(1); }
      75% { transform: translate(140px, -70px) scale(1); }
      100% { transform: translate(190px, 30px) scale(0.85); opacity: 0; }
    }
    @keyframes foodDrop {
      0% { transform: translate(-50%, -120%) scale(0.4) rotate(-20deg); opacity: 0; }
      25% { opacity: 1; transform: translate(-50%, -40%) scale(1.1) rotate(8deg); }
      55% { transform: translate(-50%, 0) scale(1) rotate(0deg); }
      75% { transform: translate(-50%, -18%) scale(0.95); }
      100% { transform: translate(-30%, -80%) scale(0.4); opacity: 0; }
    }
    @keyframes zzzFloat {
      0% { transform: translate(-50%, 0) scale(0.7); opacity: 0; }
      20% { opacity: 1; }
      100% { transform: translate(30px, -90px) scale(1.2); opacity: 0; }
    }
    @keyframes petHand {
      0% { transform: translate(-50%, -20%) rotate(-25deg) scale(0.8); opacity: 0; }
      25% { opacity: 1; transform: translate(-10%, 10%) rotate(10deg) scale(1); }
      50% { transform: translate(10%, -5%) rotate(-8deg) scale(1); }
      100% { transform: translate(20%, -40%) rotate(0deg) scale(0.9); opacity: 0; }
    }
    @keyframes burstOut {
      0% { transform: translate(-50%, -50%) scale(0.5); opacity: 1; }
      100% { transform: translate(calc(-50% + var(--dx)), calc(-50% + var(--dy))) scale(1.2); opacity: 0; }
    }

'''

if '.fx-prop' not in html:
    html = html.replace('    .heart {', css + '    .heart {')

fx_js = r'''
    function spawnProp(emoji, cls, x, y, ms = 1600) {
      const el = document.createElement('div');
      el.className = 'fx-prop ' + cls;
      el.textContent = emoji;
      el.style.left = x + 'px';
      el.style.top = y + 'px';
      document.body.appendChild(el);
      setTimeout(() => el.remove(), ms);
      return el;
    }

    function burst(emojis, x, y) {
      emojis.forEach((e, i) => {
        const el = document.createElement('div');
        el.className = 'fx-burst';
        el.textContent = e;
        const ang = (Math.PI * 2 * i) / emojis.length;
        el.style.left = x + 'px';
        el.style.top = y + 'px';
        el.style.setProperty('--dx', Math.cos(ang) * 56 + 'px');
        el.style.setProperty('--dy', Math.sin(ang) * 40 - 20 + 'px');
        document.body.appendChild(el);
        setTimeout(() => el.remove(), 900);
      });
    }

    function actionVisual(kind) {
      const x = state.x;
      const y = state.y - 70;
      if (kind === 'play' || kind === 'lets_play') {
        spawnProp('⚽', 'ball', x + 30, y + 20, 1700);
        burst(['✨', '⭐', '💫'], x, y);
        setHappy(1200);
      } else if (kind === 'feed' || kind === 'hungry' || kind === 'i_am_hungry') {
        const foods = { cat: '🐟', dog: '🦴', bunny: '🥕', fox: '🍗', panda: '🎋' };
        const food = foods[state.form] || '🍎';
        spawnProp(food, 'food', x, y - 10, 1500);
        setTimeout(() => burst(['😋', '✨', '💖'], x, y), 500);
        setHappy(1200);
      } else if (kind === 'sleep' || kind === 'good_night' || kind === 'i_am_sleepy') {
        spawnProp('Z', 'zzz', x + 24, y - 10, 2200);
        setTimeout(() => spawnProp('z', 'zzz', x + 40, y - 24, 2000), 280);
        setTimeout(() => spawnProp('💤', 'zzz', x + 18, y - 36, 2000), 560);
      } else if (kind === 'pet' || kind === 'love' || kind === 'i_love_you') {
        spawnProp('🤚', 'pethand', x - 10, y - 8, 1200);
        hearts(5);
        burst(['💗', '✨', '💞'], x, y);
      }
    }

'''

if 'function actionVisual' not in html:
    html = html.replace('    function hearts(n = 3) {', fx_js + '    function hearts(n = 3) {')

# Update act() to call actionVisual
old_act = '''    function act(kind) {
      if (kind === 'pet') {
        setHappy(900);
        hearts(4);
        speakAction('pet');
      } else if (kind === 'feed') {
        setHappy(1000);
        hearts(2);
        speakAction('feed');
      } else if (kind === 'play') {
        setHappy(1000);
        state.vx += (Math.random() - 0.5) * 10;
        state.vy -= 2 + Math.random() * 2;
        speakAction('play');
        if (state.mode !== 'follow') {
          pickWanderTarget();
          state.mode = 'wander';
          pet.classList.remove('sleep');
        }
      } else if (kind === 'sleep') {
        state.mode = 'sleep';
        pet.classList.add('sleep');
        pet.classList.remove('walk', 'happy');
        state.vx = 0; state.vy = 0;
        speakAction('sleep');
'''

new_act = '''    function act(kind) {
      if (kind === 'pet') {
        setHappy(900);
        actionVisual('pet');
        speakAction('pet');
      } else if (kind === 'feed') {
        setHappy(1000);
        actionVisual('feed');
        speakAction('feed');
      } else if (kind === 'play') {
        setHappy(1000);
        actionVisual('play');
        state.vx += (Math.random() - 0.5) * 10;
        state.vy -= 2 + Math.random() * 2;
        speakAction('play');
        if (state.mode !== 'follow') {
          pickWanderTarget();
          state.mode = 'wander';
          pet.classList.remove('sleep');
        }
      } else if (kind === 'sleep') {
        state.mode = 'sleep';
        pet.classList.add('sleep');
        pet.classList.remove('walk', 'happy');
        state.vx = 0; state.vy = 0;
        actionVisual('sleep');
        speakAction('sleep');
'''

if old_act not in html:
    raise SystemExit('act block missing')
html = html.replace(old_act, new_act)

# Update speakDialog visuals
old_sd = '''      if (d.id === 'play') {
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
'''

new_sd = '''      if (d.id === 'lets_play' || d.id === 'play') {
        actionVisual('play');
        state.vx += (Math.random() - 0.5) * 8;
        if (state.mode === 'sleep') {
          pet.classList.remove('sleep');
          state.mode = 'wander';
        }
      } else if (d.id === 'good_night' || d.id === 'i_am_sleepy' || d.id === 'sleep') {
        actionVisual('sleep');
        state.mode = 'sleep';
        pet.classList.add('sleep');
        pet.classList.remove('walk', 'happy');
        state.vx = 0; state.vy = 0;
      } else if (d.id === 'i_am_hungry' || d.id === 'hungry') {
        actionVisual('feed');
      } else if (d.id === 'i_love_you' || d.id === 'love') {
        actionVisual('pet');
      } else if (d.id === 'hello' || d.id === 'greet' || d.id === 'good_morning') {
        hearts(3);
        burst(['👋', '✨', '💖'], state.x, state.y - 70);
      }
'''

if old_sd not in html:
    raise SystemExit('speakDialog visuals missing')
html = html.replace(old_sd, new_sd)

p.write_text(html, encoding='utf-8')
print('ok', 'actionVisual' in html, 'ballBounce' in html)
