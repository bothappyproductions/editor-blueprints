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

## Homepage queue (each editor's to-do list, mirrored from Monday)
- The homepage lists each editor's edits in urgency order: **To do** (numbered: Needs Revisions and To edit by Monday deadline, late first; On Hold last), then **In review** and **Done and closed** folded away.
- It mirrors Monday's Post Production board. `status.json` carries each blueprint's Monday stage and deadline, plus open Post Production edits for a named editor that have no blueprint yet (shown with a "No blueprint yet" / "Brief in Google Docs" tag). Blueprints Monday no longer has show under Done as "Not on Monday".
- Refresh: `python3 tools/queue_status.py --query` prints the Monday read to run; `python3 tools/queue_status.py <result.json>` rewrites `status.json` (only when something changed, or every 3 hours). The scheduled task `editor-queue-status-sync` does this hourly.
- Lanes that publish blueprints never touch `status.json`.
