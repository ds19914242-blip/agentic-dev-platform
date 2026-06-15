"""console.inbox — typed intake ("backlog inbox") persistence for the Console.

Extracted verbatim from server.py (Phase 5b). A single backlog/_inbox.json file
holds captured items ({id, product, type, text, status, created}) where type is one
of epic / task / bug. Functions take the backlog directory explicitly (no server
globals), so this is self-contained and unit-testable. server.py keeps thin
same-named wrappers (inbox_list / inbox_add / inbox_delete) that inject BACKLOG_DIR.

Behaviour is byte-for-byte identical to the originals.
"""
import json
import uuid
from datetime import datetime
from pathlib import Path


def inbox_path(backlog_dir):
    return Path(backlog_dir) / "_inbox.json"


def load(backlog_dir):
    p = inbox_path(backlog_dir)
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            return {"items": []}
    return {"items": []}


def save(backlog_dir, data):
    try:
        Path(backlog_dir).mkdir(parents=True, exist_ok=True)
        inbox_path(backlog_dir).write_text(json.dumps(data, ensure_ascii=False, indent=2))
    except Exception:
        pass


def list_items(backlog_dir, product):
    items = [i for i in load(backlog_dir).get("items", []) if not product or i.get("product") == product]
    return {"items": sorted(items, key=lambda i: i.get("created", ""), reverse=True)}


def add(backlog_dir, product, itype, text):
    itype = itype if itype in ("epic", "task", "bug") else "task"
    if not (text or "").strip():
        return {"ok": False, "error": "empty text"}
    d = load(backlog_dir)
    item = {"id": uuid.uuid4().hex[:12], "product": product, "type": itype,
            "text": text.strip(), "status": "new",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    d.setdefault("items", []).append(item)
    save(backlog_dir, d)
    return {"ok": True, "item": item}


def delete(backlog_dir, item_id):
    d = load(backlog_dir)
    before = len(d.get("items", []))
    d["items"] = [i for i in d.get("items", []) if i.get("id") != item_id]
    save(backlog_dir, d)
    return {"ok": True, "removed": before - len(d["items"])}
