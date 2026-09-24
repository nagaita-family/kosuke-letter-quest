# Kosuke Letter Quest — v12.6

## Canonical state
- Repository: `nagaita-family/kosuke-letter-quest`, `main`.
- Production: https://family.nagaita.jp/kosuke-letter-quest/
- v12.6 adds the GREEN FOREST first-person vertical slice on top of the v12.5 manual-movement system.
- Check the release's Actions result for actual deployment and production verification status.

## Build (do not migrate sources incidentally)
Keep the original v12.3 b64 chunks and `enhance_v124.py.xz.b64` unchanged.
The Pages workflow restores v12.3, validates and applies v12.4, then validates
and applies `enhance_v125.py`, then `enhance_v126.py`. Output hashes are checked at each version.
The new script is an incremental upgrade, not a replacement source tree.
When changing the script, update its SHA and the generated output hashes in Pages.
Generated `game.js`, `style.css`, and expanded v12.4 script are NOT committed.

## Road controls and combat
- Hold Up to walk; release to stop. Left/Right changes lane; A swings once per keypress.
- Keys clear on scene transitions, blur and hidden-tab changes. Release/repress Up after an interruption.
- In-range target has a green ground ring + A badge. Nearby adjacent-lane assistance is intentional.
- Sword locks its visible target on press, strikes after 145ms, grants 8 XP once.
- Target recoils/fades for 760ms; no global camera shake. The player lunges locally.
- Contact stops forward travel 42 units before a living enemy, costs 6 HP but never awards XP
  or defeats/despawns it. A or sidestepping resolves the encounter. No repeated stationary damage.
- Sidestepping and passing an enemy removes it behind the player without a defeat reward.
- Road HP=0 uses `roadrecover`: 900ms pause, restore 50 HP, require new forward input.
- Road level-ups display after swing/defeat effects, then return to manual walking.
- Tuning lives in `ROAD_COMBAT` in the v12.5 upgrade script.

## GREEN FOREST prototype (stageIndex 0 only)
- Left/Right changes lane while the road and forward view stay fixed. The
  foreground body, weapon, and ground shadow follow the player's lane. Gun
  reticle starts at the current position and world target coordinates stay fixed.
  Browser regression checks left/center movement and passing a center rock
  safely from the side lane. This replaces the camera pan from the first fix.
- The road renderer omits Kosuke's whole body/back and shows only a foreground hand and held sword.
  Existing world geometry, scenery, pickups, branch and collision projection remain intact.
- A sword attack uses the existing target/hit/XP mechanics, with a large foreground swing.
- Down draws the blaster into `forestgun` state; the road pauses and the four arrows move
  the visible reticle. Space fires, Escape or A holsters. The next Up press resumes walking.
- Four shots in each magazine. After shot 4 the gun tilts, magazine moves, and a visible
  850ms automatic reload restores ammo. Reload is not another key to learn.
- Gun hits a living small monster only when the aimed reticle is near its projected position;
  generous hit radius, one hit/8 XP. MISS consumes ammo only. The shot draws a local tracer
  and muzzle flash; the enemy shares the established recoil/defeat animation.
- A stage transition resets the gun state; later worlds retain the v12.5 runner and controls.
- The existing large-enemy letter choices, three-shot battle aiming and shield remain intact.
  Do not confuse GREEN FOREST's roaming gun magazine with the large-enemy battle ammo.
- All gun tuning is in `FOREST_GUN` and `forestGunTarget` in `enhance_v126.py`.

## Preserved
Ten worlds, routes, rocks, heals, cores, English audio / three choices / R repeat,
three-shot aiming, positional four-direction shield (success=0 damage), growth,
specials and three rescued companions. Battle Up still opens SPECIAL.

## Validation
- `node --check game.js` and `node tests/logic-regression.cjs game.js`.
- Logic test uses DOM/canvas stubs; it is NOT a browser/visual test.
- `tests/road-regression.cjs` uses Playwright and a test-only intercepted source probe.
  The probe is never included in deployed game.js. Tests cover road interactions,
  both routes, battle loops, 30 encounter victory transitions, ten stages and restart.
- Pages runs browser regression before deploying. Then `tests/production-smoke.cjs`
  checks published asset hashes and real (uninstrumented) keyboard sword/gun controls on the custom domain.
- Browser screenshots are retained as the `road-qa` Actions artifact.
- Local use: serve the reconstructed output on port 8765; install Playwright + Chromium;
  `NODE_PATH=<node_modules path> node tests/road-regression.cjs`.

## Still requires family-device feedback
Chromebook key feel, subjective difficulty, English audio, volume, sword/gun recoil,
aim assist, reload timing and whether Kosuke understands the weapon/holster cues.
Do not claim the automated simulation proves the full unassisted play experience.
