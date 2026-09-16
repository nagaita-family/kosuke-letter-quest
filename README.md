# Kosuke Letter Quest

Kosuke Letter Quest v12.2.

## Repository / Hosting

- Repository: `nagaita-family/kosuke-letter-quest`
- Main branch: `main`
- Hosting: GitHub Pages
- Publish source: GitHub Actions
- Deployment workflow: `.github/workflows/pages.yml`
- Public URL: `https://family.nagaita.jp/kosuke-letter-quest/`
- Family TOP: `https://family.nagaita.jp/`

This repository is independent from Miori Kanji Quest and other Family apps.

## Development rules

- Treat `nagaita-family/kosuke-letter-quest` as the canonical repository.
- Do not use the old `nagaitashouten-star/kosuke-letter-quest` repository as the development target.
- The app must work correctly under the `/kosuke-letter-quest/` path.
- Use relative paths for HTML, CSS, JavaScript, images, and other static assets whenever possible.
- Avoid root-absolute paths such as `/assets/...` because the app is hosted under a subpath.
- If PWA support is added, use `start_url: "./"` and `scope: "./"` by default.
- Verify production behavior at `https://family.nagaita.jp/kosuke-letter-quest/`.

## Deployment

The browser game is packaged as static files and deployed automatically by `.github/workflows/pages.yml` whenever changes are pushed to `main`.
