from pathlib import Path
p = Path('/workspace/proto-page/index.html')
html = p.read_text(encoding='utf-8')

css = '''
    /* Pet body play motions */
    #pet.acting { z-index: 6; }
    #pet.acting .figure { transform-origin: 50% 100%; }
    #pet.play-swim .figure { animation: petSwim 0.7s ease-in-out infinite; }
    #pet.play-swim .arm-l { animation: petSwimArmL 0.55s ease-in-out infinite; }
    #pet.play-swim .arm-r { animation: petSwimArmR 0.55s ease-in-out infinite; }
    #pet.play-swim .leg-l, #pet.play-swim .leg-r { animation: petSwimKick 0.55s ease-in-out infinite; }
    #pet.play-basketball .figure { animation: petBallJump 0.85s ease-in-out infinite; }
    #pet.play-basketball .arm-l, #pet.play-basketball .arm-r { animation: petArmsUp 0.85s ease-in-out infinite; }
    #pet.play-soccer .leg-r { animation: petKick 0.7s ease-in-out infinite; }
    #pet.play-soccer .arm-l, #pet.play-soccer .arm-r { animation: petBalanceArm 0.7s ease-in-out infinite; }
    #pet.play-soccer .figure { animation: petSoccerLean 0.7s ease-in-out infinite; }
    #pet.play-dance .figure { animation: petDance 0.55s ease-in-out infinite; }
    #pet.play-dance .arm-l { animation: petDanceArmL 0.55s ease-in-out infinite; }
    #pet.play-dance .arm-r { animation: petDanceArmR 0.55s ease-in-out infinite; }
    #pet.play-dance .leg-l { animation: legL 0.45s ease-in-out infinite; }
    #pet.play-dance .leg-r { animation: legR 0.45s ease-in-out infinite; }
    #pet.play-run .figure { animation: petRunBob 0.28s ease-in-out infinite; }
    #pet.play-run .leg-l { animation: legL 0.28s ease-in-out infinite; }
    #pet.play-run .leg-r { animation: legR 0.28s ease-in-out infinite; }
    #pet.play-run .arm-l { animation: armL 0.28s ease-in-out infinite; }
    #pet.play-run .arm-r { animation: armR 0.28s ease-in-out infinite; }
    #pet.play-jump .figure { animation: petBigJump 0.9s ease-in-out infinite; }
    #pet.play-jump .arm-l, #pet.play-jump .arm-r { animation: petArmsUp 0.9s ease-in-out infinite; }
    #pet.play-frisbee .arm-r { animation: petThrow 0.8s ease-in-out infinite; }
    #pet.play-frisbee .figure { animation: petThrowLean 0.8s ease-in-out infinite; }
    #pet.play-bike .figure { animation: petBikeSit 0.45s ease-in-out infinite; }
    #pet.play-bike .leg-l { animation: petPedalL 0.45s linear infinite; }
    #pet.play-bike .leg-r { animation: petPedalR 0.45s linear infinite; }
    #pet.play-bike .arm-l, #pet.play-bike .arm-r { transform: rotate(-40deg); }

    .fx-prop.mini {
      font-size: 28px !important; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.25));
    }
    .fx-prop.ball-follow { animation: ballFollowKick 3.2s ease-in-out forwards; }
    .fx-prop.bball-follow { animation: bballFollow 3.2s ease-in-out forwards; }
    .fx-prop.frisbee-follow { animation: frisbeeFly 3.2s ease-in-out forwards; font-size: 26px !important; }

    @keyframes petSwim {
      0%,100% { transform: scaleX(var(--face,1)) translate(0, 8px) rotate(-6deg); }
      50% { transform: scaleX(var(--face,1)) translate(10px, -2px) rotate(6deg); }
    }
    @keyframes petSwimArmL {
      0%,100% { transform: rotate(70deg); }
      50% { transform: rotate(120deg); }
    }
    @keyframes petSwimArmR {
      0%,100% { transform: rotate(-70deg); }
      50% { transform: rotate(-120deg); }
    }
    @keyframes petSwimKick {
      0%,100% { transform: rotate(25deg); }
      50% { transform: rotate(-30deg); }
    }
    @keyframes petBallJump {
      0%,100% { transform: scaleX(var(--face,1)) translateY(0); }
      45% { transform: scaleX(var(--face,1)) translateY(-42px); }
    }
    @keyframes petArmsUp {
      0%,100% { transform: rotate(-150deg); }
      45% { transform: rotate(-170deg); }
    }
    @keyframes petKick {
      0%,100% { transform: rotate(10deg); }
      40% { transform: rotate(-55deg); }
      55% { transform: rotate(35deg); }
    }
    @keyframes petBalanceArm {
      0%,100% { transform: rotate(18deg); }
      50% { transform: rotate(-25deg); }
    }
    @keyframes petSoccerLean {
      0%,100% { transform: scaleX(var(--face,1)) rotate(0deg); }
      40% { transform: scaleX(var(--face,1)) rotate(-8deg) translateX(4px); }
      55% { transform: scaleX(var(--face,1)) rotate(6deg); }
    }
    @keyframes petDance {
      0%,100% { transform: scaleX(var(--face,1)) translateY(0) rotate(-8deg); }
      50% { transform: scaleX(var(--face,1)) translateY(-18px) rotate(8deg); }
    }
    @keyframes petDanceArmL {
      0%,100% { transform: rotate(40deg); }
      50% { transform: rotate(-130deg); }
    }
    @keyframes petDanceArmR {
      0%,100% { transform: rotate(-130deg); }
      50% { transform: rotate(40deg); }
    }
    @keyframes petRunBob {
      0%,100% { transform: scaleX(var(--face,1)) translateY(0); }
      50% { transform: scaleX(var(--face,1)) translateY(-6px); }
    }
    @keyframes petBigJump {
      0%,100% { transform: scaleX(var(--face,1)) translateY(0) scale(1,1); }
      30% { transform: scaleX(var(--face,1)) translateY(6px) scale(1.05,0.9); }
      55% { transform: scaleX(var(--face,1)) translateY(-56px) scale(0.95,1.08); }
    }
    @keyframes petThrow {
      0% { transform: rotate(20deg); }
      45% { transform: rotate(-160deg); }
      100% { transform: rotate(20deg); }
    }
    @keyframes petThrowLean {
      0%,100% { transform: scaleX(var(--face,1)) rotate(0); }
      45% { transform: scaleX(var(--face,1)) rotate(-12deg) translateX(6px); }
    }
    @keyframes petBikeSit {
      0%,100% { transform: scaleX(var(--face,1)) translateY(4px) rotate(-4deg); }
      50% { transform: scaleX(var(--face,1)) translateY(2px) rotate(2deg); }
    }
    @keyframes petPedalL {
      0% { transform: rotate(30deg); }
      50% { transform: rotate(-40deg); }
      100% { transform: rotate(30deg); }
    }
    @keyframes petPedalR {
      0% { transform: rotate(-40deg); }
      50% { transform: rotate(30deg); }
      100% { transform: rotate(-40deg); }
    }
    @keyframes ballFollowKick {
      0% { transform: translate(-10px, 30px) scale(0.7); opacity: 0; }
      20% { opacity: 1; transform: translate(8px, 34px) scale(0.9); }
      45% { transform: translate(70px, 10px) scale(1); }
      100% { transform: translate(160px, 40px) scale(0.85); opacity: 0; }
    }
    @keyframes bballFollow {
      0% { transform: translate(0, 20px) scale(0.7); opacity: 0; }
      25% { opacity: 1; transform: translate(6px, -35px) scale(0.95); }
      50% { transform: translate(10px, 25px) scale(1); }
      75% { transform: translate(14px, -40px) scale(0.95); }
      100% { transform: translate(18px, 30px) scale(0.8); opacity: 0; }
    }

'''

if '#pet.play-swim' not in html:
    html = html.replace('    /* Pet body play motions */', css) if '/* Pet body play motions */' in html else None
if '#pet.play-swim' not in html:
    # insert before .fx-prop.ball or after #pet.happy
    anchor = '    #pet.happy .figure { animation: hop 0.9s ease; }'
    if anchor not in html:
        raise SystemExit('happy anchor missing')
    html = html.replace(anchor, anchor + '\n' + css)

new_play_visual = r'''
    function clearPetPlayPose() {
      if (!pet) return;
      pet.classList.remove('acting','play-swim','play-basketball','play-soccer','play-dance','play-run','play-jump','play-frisbee','play-bike');
      clearTimeout(clearPetPlayPose._t);
    }

    function setPetPlayPose(id, ms = 3600) {
      clearPetPlayPose();
      const map = {
        swim: 'play-swim',
        basketball: 'play-basketball',
        soccer: 'play-soccer',
        dance: 'play-dance',
        run: 'play-run',
        jump: 'play-jump',
        frisbee: 'play-frisbee',
        bike: 'play-bike',
      };
      const cls = map[id] || 'play-dance';
      pet.classList.add('acting', cls);
      pet.classList.remove('walk', 'sleep');
      clearPetPlayPose._t = setTimeout(() => clearPetPlayPose(), ms);
    }

    function playVisual(play) {
      const x = state.x, y = state.y - 40;
      const id = (play && play.id) || 'soccer';
      document.querySelectorAll('.fx-splash').forEach((el) => el.remove());
      setPetPlayPose(id, 3800);

      // small props interact with the pet body (not sticker characters)
      if (id === 'swim') {
        const splash = document.createElement('div');
        splash.className = 'fx-splash';
        document.body.appendChild(splash);
        setTimeout(() => splash.remove(), 3800);
        burst(['💧', '🌊'], x, y);
      } else if (id === 'basketball') {
        spawnProp('🏀', 'bball-follow mini', x + 18, y + 10, 3800);
        burst(['✨'], x, y - 10);
      } else if (id === 'soccer') {
        spawnProp('⚽', 'ball-follow mini', x + 22, y + 20, 3800);
        burst(['✨'], x, y);
      } else if (id === 'dance') {
        burst(['🎵', '✨', '💜'], x, y - 20);
      } else if (id === 'run') {
        burst(['💨', '✨'], x - 20, y);
      } else if (id === 'jump') {
        burst(['✨', '⭐'], x, y - 30);
      } else if (id === 'frisbee') {
        spawnProp('🥏', 'frisbee-follow mini', x + 10, y - 10, 3800);
        burst(['💨'], x, y);
      } else if (id === 'bike') {
        // subtle wheel cue near feet
        spawnProp('🚲', 'mini', x, state.y - 18, 3800);
        const el = document.querySelector('.fx-prop.mini:last-of-type');
        if (el) {
          el.style.left = x + 'px';
          el.style.top = (state.y - 8) + 'px';
          el.style.animation = 'bikeRide 3.2s linear forwards';
        }
        burst(['💨'], x, y);
      } else {
        spawnProp('⚽', 'ball-follow mini', x + 22, y + 20, 3800);
      }
      setHappy(2400);
    }
'''

import re
# replace from function playVisual through end of playVisual (before startPlay)
pat = r"    function playVisual\(play\) \{.*?\n    \}\n\n    function startPlay"
if not re.search(pat, html, re.S):
    raise SystemExit('playVisual block not found')
html2, n = re.subn(pat, new_play_visual + '\n    function startPlay', html, count=1, flags=re.S)
print('replaced', n)
html = html2

# ensure tickPet doesn't force walk class over acting
# find pet.classList.toggle('walk'
if "pet.classList.toggle('walk'" in html:
    html = html.replace(
        "pet.classList.toggle('walk', moving);",
        "if (!pet.classList.contains('acting')) pet.classList.toggle('walk', moving);\n      else pet.classList.remove('walk');"
    )
    print('walk guard ok')

p.write_text(html)
assert 'setPetPlayPose' in html
assert 'petSwim' in html
print('ALL OK')
