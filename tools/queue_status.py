"""Mirror Monday into status.json, the data behind the homepage's per-editor to-do lists.

usage:
  python3 tools/queue_status.py --query               print the Monday GraphQL read to run (built from index.json)
  python3 tools/queue_status.py <monday_result.json>  write status.json from that read's result

The read covers (1) every open item in Post Production's Incoming Edits, Needs Revisions and
Creative Review groups, and (2) every blueprint id in index.json wherever it now lives.
Any JSON shape works as long as the item objects (with "id" and "column_values") are inside it.

status.json:
  items  one entry per index.json id: {"st", "label", "due", "v", "ed", "note"}; ids Monday did
         not return are {"st": "missing"} (shown as "Not on Monday" under Done).
  extra  open Post Production items for a named editor that have no blueprint yet:
         {"st", "label", "due", "v", "ed", "title", "client", "link"}

Stages: revise (Needs Revisions), edit (Incoming / Editing / blank), hold (On Hold) -> To do;
review (Ready for Review) -> In review; done / client / closed -> Done.

The file is rewritten only when something changed, or when the last write is over 3 hours old
(the page warns when it is over 6 hours old). Exit code 0 either way; output says which.
"""
import datetime, json, os, re, sys

POST_PROD = "2135456123"
OPEN_GROUPS = ["group_mkx6r7at", "new_group36605", "topics"]  # Incoming Edits, Needs Revisions, Creative Review
COLS = ["status", "color_mkx64zpv", "date_mkx6gvqa", "status_1", "text_mm8cf658", "dropdown6", "link_mkx6ay1e"]
EDITORS = {"Qendrim", "Bleron", "Ardit", "Almi", "Theresa", "Jerome", "Holly", "Claire", "Atdhe"}
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIELDS = 'id name state board{id name} group{id title} column_values(ids:[%s]){id text}' % ",".join('"%s"' % c for c in COLS)


def build_query(ids):
    parts = ['pp: boards(ids:[%s]) { groups(ids:[%s]) { id title items_page(limit:500) { cursor items { %s } } } }'
             % (POST_PROD, ",".join('"%s"' % g for g in OPEN_GROUPS), FIELDS)]
    for n in range(0, len(ids), 100):
        alias = "i%d" % (n // 100)
        parts.append('%s: items(ids:[%s], limit:100) { %s }' % (alias, ",".join(ids[n:n + 100]), FIELDS))
    return "query { " + " ".join(parts) + " }"


def walk(o, out, cursors):
    if isinstance(o, dict):
        if "id" in o and "column_values" in o:
            out.append(o)
            return
        if o.get("cursor"):
            cursors.append(o["cursor"])
        for v in o.values():
            walk(v, out, cursors)
    elif isinstance(o, list):
        for v in o:
            walk(v, out, cursors)


def stage(it, cv):
    board = it.get("board") or {}
    group = ((it.get("group") or {}).get("title") or "").strip()
    low, glow = cv.get("status", "").lower(), group.lower()
    if (it.get("state") or "active") != "active":
        return "closed", "Removed from Monday"
    if str(board.get("id")) != POST_PROD:
        if (board.get("name") or "").lower() == "archive" or "failed" in glow:
            return "closed", "Archived"
        return "client", "With client"
    if low == "scrap" or glow.startswith("closed"):
        return "closed", "Closed"
    if low in ("edits done", "send to client") or glow == "edits done":
        return "done", "Send to client" if low == "send to client" else "Edits done"
    if low == "needs revisions" or (not low and glow == "needs revisions"):
        return "revise", "Needs revisions"
    if low.startswith("ready for review") or (not low and glow == "creative review"):
        return "review", "In review"
    if low == "on hold":
        return "hold", "On hold"
    if low.startswith("editing"):
        return "edit", "Editing"
    return "edit", "To edit"


def common(st, label, cv):
    e = {"st": st, "label": label}
    due = cv.get("date_mkx6gvqa", "")
    if due:
        e["due"] = due[:10]
    ver = cv.get("status_1", "")
    if ver:
        e["v"] = ver if ver.upper().startswith("V") else "V" + ver
    note = cv.get("text_mm8cf658", "")
    if note and st in ("hold", "revise", "edit"):
        first = note.split(". ")[0].strip()
        e["note"] = (first[:157] + "...") if len(first) > 160 else first
    return e


def split_name(name, client):
    """'MHA — Story of Hope: X — "Y" (Sept shoot)' -> ('MHA', 'Story of Hope: X — "Y"')."""
    name = re.sub(r"\s*\[[^\]]*\]\s*$", "", name.strip())
    m = re.match(r"^(.{2,28}?)\s+[—–-]\s+(.+)$", name)
    short_client = (client.split(" - ")[0].strip() if client else "")
    if m:
        pre, rest = m.group(1).strip(), m.group(2).strip()
        if len(pre) <= 14 or not short_client:
            short_client = pre
        name = rest
    return short_client or "—", name


def main():
    index = json.load(open(os.path.join(REPO, "index.json")))
    ids = [str(x["id"]) for x in index]
    if sys.argv[1:2] == ["--query"]:
        print(build_query(ids))
        return
    raw = json.load(open(sys.argv[1]))
    found, cursors = [], []
    walk(raw, found, cursors)
    if not found:
        print("No items in the Monday result; status.json left as it was.")
        sys.exit(2)
    if cursors:
        print("Note: a Post Production group has more than 500 open items; only the first 500 were read.")
    by_id = {}
    for it in found:
        by_id.setdefault(str(it["id"]), it)
    in_index = set(ids)
    items, extra = {}, {}
    for x in index:
        iid = str(x["id"])
        it = by_id.get(iid)
        if not it:
            items[iid] = {"st": "missing"}
            continue
        cv = {c.get("id"): (c.get("text") or "").strip() for c in it.get("column_values") or []}
        st, label = stage(it, cv)
        e = common(st, label, cv)
        ed = cv.get("color_mkx64zpv", "")
        if ed in EDITORS and ed != x.get("editor"):
            e["ed"] = ed
        items[iid] = e
    for iid, it in by_id.items():
        if iid in in_index or str((it.get("board") or {}).get("id")) != POST_PROD:
            continue
        cv = {c.get("id"): (c.get("text") or "").strip() for c in it.get("column_values") or []}
        ed = cv.get("color_mkx64zpv", "")
        st, label = stage(it, cv)
        if ed not in EDITORS or st not in ("revise", "edit", "hold", "review"):
            continue
        e = common(st, label, cv)
        e["ed"] = ed
        e["client"], e["title"] = split_name(it.get("name", ""), cv.get("dropdown6", ""))
        m = re.search(r"https?://\S+", cv.get("link_mkx6ay1e", ""))
        e["link"] = m.group(0) if m else "https://happyproductions.monday.com/boards/%s/pulses/%s" % (POST_PROD, iid)
        extra[iid] = e
    path = os.path.join(REPO, "status.json")
    now = datetime.datetime.now(datetime.timezone.utc)
    try:
        old = json.load(open(path))
        age = now - datetime.datetime.strptime(old.get("synced", ""), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
        if old.get("items") == items and old.get("extra", {}) == extra and age < datetime.timedelta(hours=3):
            print("unchanged: status.json already mirrors Monday (last written %d min ago)" % (age.total_seconds() // 60))
            return
    except Exception:
        pass
    out = {"synced": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
           "source": "Monday Post Production board %s (tools/queue_status.py)" % POST_PROD,
           "items": items, "extra": extra}
    with open(path, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=0)
        f.write("\n")
    counts = {}
    for v in list(items.values()) + list(extra.values()):
        counts[v["st"]] = counts.get(v["st"], 0) + 1
    print("written: status.json with %d blueprint items + %d Monday-only items %s"
          % (len(items), len(extra), json.dumps(counts, sort_keys=True)))


if __name__ == "__main__":
    main()
