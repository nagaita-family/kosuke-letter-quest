# Kosuke Letter Quest

Kosuke Letter Quest v12.3.

## Repository / Hosting

- Repository: `nagaita-family/kosuke-letter-quest`
- Main branch: `main`
- Hosting: GitHub Pages
- Publish source: GitHub Actions
- Deployment workflow: `.github/workflows/pages.yml`
- Public URL: `https://family.nagaita.jp/kosuke-letter-quest/`
- Family TOP: `https://family.nagaita.jp/`

This repository is independent from Miori Kanji Quest and other Family apps.

## Controls

- AUTO RUN: Left / Right arrows to switch between three lanes.
- Battle (Kosuke turn): Left / Right arrows to choose a letter, Space to attack, R to repeat the letter, Up to open SPECIAL.
- Battle (enemy turn): Move the shield with all four arrow keys (Left / Right / Up / Down). Watch the incoming orb and put the shield over its landing point. Space does not automatically guard.
- Route fork: Left / Right to choose, Space to confirm.

## v12.3 guard and motion changes

- Removed whole-screen camera shake, including after normal and special attacks, hits, successful guards, and victories.
- Incoming enemy attack shows a target marker and an orb approaching the shield plane.
- Shield position, not a Space press, determines the outcome: intercept the orb for zero HP loss; miss it to take damage.
- Successful guard has a brief clean, positive glint instead of fireworks-like sparks.

## Development rules

- Treat `nagaita-family/kosuke-letter-quest` as the canonical repository.
- Do not use the old `nagaitashouten-star/kosuke-letter-quest` repository as the development target.
- The app must work correctly under the `/kosuke-letter-quest/` path.
- Use relative paths for HTML, CSS, JavaScript, images, and other static assets whenever possible.
- Avoid root-absolute paths such as `/assets/...` because the app is hosted under a subpath.
- If PWA support is added, use `start_url: "./"` and `scope: "./"` by default.
- Verify production behavior at `https://family.nagaita.jp/kosuke-letter-quest/`.

## Deployment

The browser game is packaged as static files and deployed automatically by `.github/workflows/pages.yml` whenever changes are pushed to `main`. The `game-*.b64` and `style-*.b64` chunks are compressed game assets loaded via relative paths by `index.html`. Update all chunks together when publishing a new build.
