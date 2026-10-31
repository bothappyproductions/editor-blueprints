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

## Homepage queue (each editor's to-do list)
- The homepage lists each editor's edits in priority order: **To do** (numbered, work top to bottom), then **In review** and **Done and closed** folded away.
- Default order is urgency: Needs Revisions and To edit sorted by Monday deadline (late first), On Hold last.
- `status.json` holds each item's Monday stage and deadline. Rebuild it with `python3 tools/queue_status.py <raw Monday items JSON>` (the script's header shows the query). Items Monday does not return show as "Not on Monday": in To do while their deadline is ahead, in Done once it has passed.
- `order.json` is written only by the page: **Arrange order** (Atdhe, with a GitHub token saved in his browser) lets him drag edits, mark them Done or Reopen them. New edits slot in by urgency and show a "New" tag. A Done/Reopen mark lapses by itself when the item's Monday stage changes.
- Lanes that publish blueprints never touch `status.json` or `order.json`.

