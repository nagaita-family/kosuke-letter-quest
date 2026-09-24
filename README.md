# Kosuke Letter Quest

Version **12.6** — first-person GREEN FOREST prototype with sword and blaster.

## Repository & hosting

- Canonical repo: `nagaita-family/kosuke-letter-quest` (`main`)
- Game: https://family.nagaita.jp/kosuke-letter-quest/
- Family TOP: https://family.nagaita.jp/
- Publisher: `.github/workflows/pages.yml` (GitHub Actions / GitHub Pages)
- This game is independent of other Family apps. Never update the old personal repo.

## Controls

- Road: hold **Up** to walk, release to stop. Left/Right changes one of three lanes. **A** swings at the enemy marked by a green ring and A badge; nearby adjacent targets get gentle assistance. A hit knocks the enemy away and awards 8 XP. Contact costs 6 HP and stops you, but the enemy stays alive: attack or sidestep. Passing is not defeating and gives no XP. Release/repress Up after a scene transition or focus loss.
- GREEN FOREST prototype: the road is shown entirely through Kosuke's eyes, with the held sword in front. Press **Down** to draw the blaster; walking pauses. Use all four arrow keys to move the reticle, **Space** to fire, **Escape** or **A** to holster. Four shots; a visible short automatic reload follows an empty magazine. Aim generously near a visible small monster. On other worlds, the v12.5 third-person road remains unchanged.
- Main monster: select an English letter with Left/Right; Space confirms. A correct answer opens the aiming round.
- Aiming: all four arrow keys move the crosshair; **Space** fires. You have **three shots per correct answer**. Misses use ammunition without damage; hits reduce monster HP. A defeated monster ends the battle; otherwise the enemy attacks after the third shot.
- Enemy turn: all four arrow keys position the shield; intercept the incoming projectile to take zero damage. Space does not auto-block.
- Special attack: Up during the letter question opens the special menu; Left/Right chooses, Space activates, Up cancels. R repeats the spoken letter.
- Route fork: Left/Right chooses, Space confirms.

The camera does not shake during attacks, guards, victories or sword swings.

## Build and deployment

The original v12.3 `game-*.b64` and `style-*.b64` chunks are retained as immutable base sources. GitHub Actions reconstructs ordinary `game.js` and `style.css`, applies the checked `enhance_v124.py.xz.b64` upgrade, then `enhance_v125.py`, then `enhance_v126.py` for the Green Forest slice. The workflow validates SHA-256 hashes, JavaScript syntax, deterministic logic checks and browser regressions before publishing. It then verifies production asset hashes and real keyboard controls. Do not remove the base chunks or upgrade scripts until an explicitly approved source migration. See `HANDOFF.md` for test commands and tuning details.

Use relative asset paths (not root-absolute `/assets/...`) to support the `/kosuke-letter-quest/` subpath. If adding PWA, default to `start_url: "./"` and `scope: "./"`. Verify the live result on the custom-domain game URL above.
