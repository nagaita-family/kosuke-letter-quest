# Kosuke Letter Quest

Version **12.4** — mini-monster sword encounters and three-shot aiming battles.

## Repository & hosting

- Canonical repo: `nagaita-family/kosuke-letter-quest` (`main`)
- Game: https://family.nagaita.jp/kosuke-letter-quest/
- Family TOP: https://family.nagaita.jp/
- Publisher: `.github/workflows/pages.yml` (GitHub Actions / GitHub Pages)
- This game is independent of other Family apps. Never update the old personal repo.

## Controls

- Road: Left/Right changes one of three lanes. **A** swings the sword at approaching small monsters in your lane; a successful hit awards 8 XP. A mini monster you pass in the same lane without defeating costs 6 HP.
- Main monster: select an English letter with Left/Right; Space confirms. A correct answer opens the aiming round.
- Aiming: all four arrow keys move the crosshair; **Space** fires. You have **three shots per correct answer**. Misses use ammunition without damage; hits reduce monster HP. A defeated monster ends the battle; otherwise the enemy attacks after the third shot.
- Enemy turn: all four arrow keys position the shield; intercept the incoming projectile to take zero damage. Space does not auto-block.
- Special attack: Up during the letter question opens the special menu; Left/Right chooses, Space activates, Up cancels. R repeats the spoken letter.
- Route fork: Left/Right chooses, Space confirms.

The camera does not shake during attacks, guards, victories or sword swings.

## Build and deployment

The original v12.3 `game-*.b64` and `style-*.b64` chunks are retained as immutable base sources. GitHub Actions reconstructs ordinary `game.js` and `style.css`, then applies the checked `enhance_v124.py.xz.b64` upgrade script to build v12.4. The workflow validates SHA-256 hashes and JavaScript syntax before publishing `index.html` and the generated assets. Do not remove the base chunks or upgrade script until the files have been migrated to ordinary repository source files.

Use relative asset paths (not root-absolute `/assets/...`) to support the `/kosuke-letter-quest/` subpath. If adding PWA, default to `start_url: "./"` and `scope: "./"`. Verify the live result on the custom-domain game URL above.
