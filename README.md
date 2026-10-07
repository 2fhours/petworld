# Pet World

An interactive English-learning pet web prototype for kids.

## Run locally

```bash
python3 -m http.server 8765 --directory .
```

Open `http://127.0.0.1:8765`.

## Features

- Q-version pets (cat / dog / bunny / fox / panda)
- English voice commands and replies (neural TTS audio)
- Phonics by IPA, eat-food likes/dislikes, scenic backgrounds

## Note

Generated audio files are included under `audio/`.

## Version bumps

Before every code commit, run `node scripts/bump-version.js` from the repository root.
This increments the numeric `APP_VERSION` shown in the bottom-right corner.

## GitHub Pages

https://2fhours.github.io/petworld/

## Alphabet / 字母播放

English panel **字母 / ABC** (or ops **字母**) opens a fullscreen letter practice: one letter at a time as `A a` with IPA tip and en-US `speechSynthesis` pronunciation (unlocked on tap; waits for voices on mobile Chrome). **上一个** / **下一个** cycle Z↔A; **随机** picks another letter. Legacy `cast.html` may still exist but has no in-app entry.

