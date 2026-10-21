# Editor Blueprints — GitHub Pages copy

Static copy of the Editor Blueprints site. Motion-graphics downloads (PNG sequence .zip and MP4) are built in the viewer's browser and saved as normal Blob downloads, so they work for anyone who can open the page.

## Publish
1. Create a new GitHub repository (e.g. `editor-blueprints`).
2. Upload everything in this folder to the repo root, including the hidden `.nojekyll` file.
3. Repo → Settings → Pages → Source: "Deploy from a branch" → `main` / `(root)` → Save.
4. After a minute the site is at `https://<your-username>.github.io/editor-blueprints/`. Open a blueprint with `#i<item id>`, e.g. `#i12489938131`.

## Notes
- Downloads need Chrome (or Edge) on a computer; MP4 export uses the browser's VideoEncoder.
- The "ask a question" helper and team-wide checklist sync rely on claude.ai and are off here; checklists save on each person's device.
