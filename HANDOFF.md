# Kosuke Letter Quest — v12.5

## Canonical state
- Repository: `nagaita-family/kosuke-letter-quest`, `main`.
- Production: https://family.nagaita.jp/kosuke-letter-quest/
- v12.5 implements the approved manual-movement / road-combat instruction.
- Check the release's Actions result for actual deployment and production verification status.

## Build (do not migrate sources incidentally)
Keep the original v12.3 b64 chunks and `enhance_v124.py.xz.b64` unchanged.
The Pages workflow restores v12.3, validates and applies v12.4, then validates
and applies `enhance_v125.py`. Output hashes are checked at both versions.
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
  checks published asset hashes and real (uninstrumented) keyboard controls on the custom domain.
- Browser screenshots are retained as the `road-qa` Actions artifact.
- Local use: serve the reconstructed output on port 8765; install Playwright + Chromium;
  `NODE_PATH=<node_modules path> node tests/road-regression.cjs`.

## Still requires family-device feedback
Chromebook key feel, subjective difficulty, English audio, volume, perceived lunge/recoil,
attack-reach/assist tuning and whether Kosuke understands the visual cues.
Do not claim the automated simulation proves the full unassisted play experience.
