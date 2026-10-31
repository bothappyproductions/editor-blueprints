"""Write status.json (the homepage's urgency data) from a raw Monday items query.

usage:
  python3 tools/queue_status.py <monday_raw.json> [repo_dir]

<monday_raw.json> is the JSON returned by a Monday GraphQL read such as
  { a: items(ids:[...first 100 ids from index.json...], limit:100) { id state board{id name} group{id title}
       column_values(ids:["status","color_mkx64zpv","date_mkx6gvqa","status_1","text_mm8cf658"]){id text} }
    b: items(ids:[...next 100...], limit:100) { ...same fields... } }
Any shape works as long as the item objects (with "id" and "column_values") are somewhere inside it.
Every id in index.json that Monday did not return is written as {"st": "missing"}.

Stages the homepage understands:
  revise  Needs Revisions on Post Production   -> To do (top)
  edit    Incoming / Editing / blank            -> To do
  hold    On Hold                               -> To do (bottom)
  review  Ready for Review / Creative Review    -> In review
  done    Edits Done / Send to Client           -> Done
  client  moved to a client board               -> Done
  closed  Scrap, Closed group, Archive, deleted -> Done
"""
import datetime, json, os, sys

POST_PROD = "2135456123"
EDITORS = {"Qendrim", "Bleron", "Ardit", "Almi", "Theresa", "Jerome", "Holly", "Claire"}


def walk(o, out):
    if isinstance(o, dict):
        if "id" in o and "column_values" in o:
            out.append(o)
            return
        for v in o.values():
            walk(v, out)
    elif isinstance(o, list):
        for v in o:
            walk(v, out)


def stage(it):
    cv = {c.get("id"): (c.get("text") or "").strip() for c in it.get("column_values") or []}
    board = (it.get("board") or {})
    group = ((it.get("group") or {}).get("title") or "").strip()
    st = cv.get("status", "")
    low, glow = st.lower(), group.lower()
    if (it.get("state") or "active") != "active":
        return "closed", "Removed from Monday", cv
    if str(board.get("id")) != POST_PROD:
        if (board.get("name") or "").lower() == "archive" or "failed" in glow:
            return "closed", "Archived", cv
        return "client", "With client", cv
    if low == "scrap" or glow.startswith("closed"):
        return "closed", "Closed", cv
    if low in ("edits done", "send to client") or glow == "edits done":
        return "done", "Send to client" if low == "send to client" else "Edits done", cv
    if low == "needs revisions" or (not low and glow == "needs revisions"):
        return "revise", "Needs revisions", cv
    if low.startswith("ready for review") or (not low and glow == "creative review"):
        return "review", "In review", cv
    if low == "on hold":
        return "hold", "On hold", cv
    if low.startswith("editing"):
        return "edit", "Editing", cv
    return "edit", "To edit", cv


def main():
    raw_path = sys.argv[1]
    repo = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw = json.load(open(raw_path))
    found = []
    walk(raw, found)
    by_id = {str(i["id"]): i for i in found}
    index = json.load(open(os.path.join(repo, "index.json")))
    items = {}
    for x in index:
        iid = str(x["id"])
        it = by_id.get(iid)
        if not it:
            items[iid] = {"st": "missing"}
            continue
        st, label, cv = stage(it)
        e = {"st": st, "label": label}
        due = cv.get("date_mkx6gvqa", "")
        if due:
            e["due"] = due[:10]
        ver = cv.get("status_1", "")
        if ver:
            e["v"] = ver if ver.upper().startswith("V") else "V" + ver
        ed = cv.get("color_mkx64zpv", "")
        if ed in EDITORS and ed != x.get("editor"):
            e["ed"] = ed
        note = cv.get("text_mm8cf658", "")
        if note and st in ("hold", "revise", "edit"):
            first = note.split(". ")[0].strip()
            e["note"] = (first[:157] + "...") if len(first) > 160 else first
        items[iid] = e
    out = {
        "synced": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "Monday Post Production board 2135456123 (written by tools/queue_status.py)",
        "items": items,
    }
    with open(os.path.join(repo, "status.json"), "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=0, sort_keys=False)
        f.write("\n")
    counts = {}
    for v in items.values():
        counts[v["st"]] = counts.get(v["st"], 0) + 1
    print("status.json:", len(items), "items", json.dumps(counts, sort_keys=True))


if __name__ == "__main__":
    main()
