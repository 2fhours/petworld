# Rewarded ads — double hearts

Pet World shows an **optional** “双倍爱心 / Double hearts” offer after some lesson moments
(phonics finish, atlas milestone, or every 3 word listens in a session). Ads never auto-play.

## Current behavior (GitHub Pages / demo)

`showRewardedAd()` runs in **DEMO** mode:

1. User taps **看视频 Watch**
2. Overlay: “Ad preview (demo)” with a 3-second countdown
3. Resolves `true` → `awardXp` again with reason `ad-double`

Rate limit: at most one offer every few minutes.

## Wire a real SDK later

Replace the DEMO body inside `showRewardedAd()` in `index.html`:

### Native wrapper (Capacitor / Cordova / custom WebView)

Use **Google AdMob Rewarded**:

1. Create a Rewarded ad unit in AdMob
2. Load the ad on app start / before offer
3. On Watch: show the rewarded ad
4. On reward callback → `resolve(true)`
5. On close / fail → `resolve(false)`

### Pure web (GitHub Pages)

Keep the demo stub, or plug a web rewarded network if you have one.
Do **not** force interstitial ads on kids’ flows; keep the Watch / Later choice.

## Safety

- Always optional (Watch / Later)
- Child-friendly copy only
- Never print or embed publisher secrets in this static repo
