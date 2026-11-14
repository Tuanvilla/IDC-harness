"""Ghim cam ket cua dream job (1.4.0): job dem chi rut ra DE XUAT, khong bao gio
ghi thang vao brain; de xuat chi vao brain khi chu bam Ap dung tren dashboard,
voi hash guard tren file dich.

    python tests/python/test_dream.py

Khong can API key, khong cham mang: text_call va sessions_reader deu la gia lap.
"""
from _paths import ROOT, SERVER  # noqa: E402,F401  - nap server/ vao sys.path
import json
import os
import tempfile
import time
from pathlib import Path

import dream  # noqa: E402

dream.RETRY_PAUSE = 0  # test khong doi 20s moi lan thu lai

_fails = []


def check(name, cond, them=""):
    print(("ok   " if cond else "FAIL ") + name + ((f"  [{them!r}]") if them and not cond else ""))
    if not cond:
        _fails.append(name)


def _mk(tmp):
    """Mot Dreamer chay tren thu muc tam, voi text_call gia lap tra ve JSON co dinh."""
    brain = Path(tmp) / "brains" / "IDC"
    (brain / "memory").mkdir(parents=True)
    (brain / "wiki").mkdir(parents=True)
    state = Path(tmp) / "state"
    state.mkdir(parents=True)
    return brain, state


def _host(brain, state, sessions, script):
    calls = {"i": 0}

    def text_call(system, prompt):
        idx = calls["i"]
        calls["i"] += 1
        entry = script[min(idx, len(script) - 1)]
        if isinstance(entry, Exception):
            raise entry
        return entry

    return dream.Host(
        text_call=text_call,
        sessions_reader=lambda b: sessions,
        brain_root=lambda b: brain,
        policy_on=lambda b: True,
        state_dir=state,
        backups=state / "dream-backups")


SESSIONS = [{
    "session_id": "s1",
    "messages": [
        {"role": "user", "content": "UPS Liebert NX300 300 kVA o phong 2A dang chay the nao?", "ts": 1793000000.0},
        {"role": "assistant", "content": "UPS Liebert NX300 300 kVA o phong 2A dang chay binh thuong, tai 62%.", "ts": 1793000060.0},
    ],
}]

ANALYZER_OK = json.dumps({"proposals": [{
    "kind": "fact",
    "target": "memory/facts/ups-2a.md",
    "title": "UPS phong 2A chay 62% tai",
    "body": "UPS Liebert NX300 300 kVA phong 2A chay binh thuong o muc 62% tai.",
    "evidence": ["UPS Liebert NX300 300 kVA o phong 2A dang chay binh thuong, tai 62%."],
}]}, ensure_ascii=False)

VERIFIER_KEEP = json.dumps({"keep": [1], "drop": {}}, ensure_ascii=False)

CLOCK_0230 = 1794598200.0  # 2026-11-14 02:30 gio dia phuong cua may test (UTC+7)


# ---- 1. Che do mac dinh la suggest; "auto" bi ha xuong suggest ----
tmp = tempfile.mkdtemp(prefix="idc-dream-1-")
cfg = dream.read_config(Path(tmp))
check("cau hinh mac dinh: enabled True, mode suggest",
      cfg["enabled"] is True and cfg["mode"] == "suggest", cfg)
saved = dream.save_config(Path(tmp), {"mode": "auto"})
check("ghi mode 'auto' vao cau hinh -> doc lai chi con 'suggest'",
      dream.read_config(Path(tmp))["mode"] == "suggest", saved)
check("normalize_mode('auto') == 'suggest'", dream.normalize_mode("auto") == "suggest")
check("normalize_mode('dry-run') giu nguyen", dream.normalize_mode("dry-run") == "dry-run")

# ---- 2. Mot lan chay day du: chi ghi de xuat, khong ghi brain ----
tmp = tempfile.mkdtemp(prefix="idc-dream-2-")
brain, state = _mk(tmp)
host = _host(brain, state, SESSIONS, [ANALYZER_OK, VERIFIER_KEEP])
dm = dream.Dreamer(dream.Store(state / "dream.sqlite3"), host, clock=lambda: CLOCK_0230)
result = dm.run("IDC", force=True)
check("run force -> done, 1 de xuat", result["state"] == "done" and result["proposals_created"] == 1, result)
props = dm.list_proposals("IDC")
check("1 de xuat pending, target dung, verified",
      len(props) == 1 and props[0]["status"] == "pending"
      and props[0]["target_path"] == "memory/facts/ups-2a.md" and props[0]["verified"] == 1, props)
check("brain KHONG co file moi nao sau khi dream chay",
      list(brain.rglob("*.md")) == [], sorted(str(p) for p in brain.rglob("*.md")))

# ---- 3. De xuat khong bang chung bi loai o buoc xac minh ----
tmp = tempfile.mkdtemp(prefix="idc-dream-3-")
brain, state = _mk(tmp)
bad = json.dumps({"proposals": [{
    "kind": "fact", "target": "memory/facts/x.md", "title": "Phong doan",
    "body": "Chac la UPS sap hong.",
    "evidence": ["cau nay khong he co trong nhat ky"],
}]}, ensure_ascii=False)
host = _host(brain, state, SESSIONS, [bad, VERIFIER_KEEP])
dm = dream.Dreamer(dream.Store(state / "dream.sqlite3"), host, clock=lambda: CLOCK_0230)
result = dm.run("IDC", force=True)
check("de xuat khong trich dan dung -> 0 de xuat",
      result["proposals_created"] == 0 and dm.list_proposals("IDC") == [], result)

# ---- 4. De xuat nham vao sources/ bi loai ----
tmp = tempfile.mkdtemp(prefix="idc-dream-4-")
brain, state = _mk(tmp)
src = json.dumps({"proposals": [{
    "kind": "correction", "target": "sources/01 - He thong dien/x.md", "title": "Sua nguon",
    "body": "Sua tai lieu goc.", "evidence": ["UPS Liebert NX300 300 kVA o phong 2A dang chay binh thuong, tai 62%."],
}]}, ensure_ascii=False)
host = _host(brain, state, SESSIONS, [src, VERIFIER_KEEP])
dm = dream.Dreamer(dream.Store(state / "dream.sqlite3"), host, clock=lambda: CLOCK_0230)
result = dm.run("IDC", force=True)
check("de xuat vao sources/ -> 0 de xuat",
      result["proposals_created"] == 0 and dm.list_proposals("IDC") == [], result)
check("valid_target tu choi sources/", dream.valid_target("sources/01/x.md") == "")
check("valid_target chap nhan memory/ va wiki/",
      dream.valid_target("memory/facts/a.md") == "memory/facts/a.md"
      and dream.valid_target("wiki/13 - Su co/a.md") == "wiki/13 - Su co/a.md")
check("valid_target tu choi duong dan thoat ra ngoai",
      dream.valid_target("../ngoai.md") == "" and dream.valid_target("/tmp/x.md") == "")

# ---- 5. dry-run: phan tich xong nhung khong luu de xuat ----
tmp = tempfile.mkdtemp(prefix="idc-dream-5-")
brain, state = _mk(tmp)
dream.save_config(state, {"mode": "dry-run"})
host = _host(brain, state, SESSIONS, [ANALYZER_OK, VERIFIER_KEEP])
dm = dream.Dreamer(dream.Store(state / "dream.sqlite3"), host, clock=lambda: CLOCK_0230)
result = dm.run("IDC", force=True)
check("dry-run -> state dry_run, 0 de xuat",
      result["state"] == "dry_run" and dm.list_proposals("IDC") == [], result)

# ---- 6. Ap dung: ghi file + hash guard + undo ----
tmp = tempfile.mkdtemp(prefix="idc-dream-6-")
brain, state = _mk(tmp)
host = _host(brain, state, SESSIONS, [ANALYZER_OK, VERIFIER_KEEP])
dm = dream.Dreamer(dream.Store(state / "dream.sqlite3"), host, clock=lambda: CLOCK_0230)
dm.run("IDC", force=True)
pid = dm.list_proposals("IDC")[0]["id"]
out = dm.apply_proposal("IDC", pid)
target = brain / "memory" / "facts" / "ups-2a.md"
check("apply -> file duoc tao, noi dung co trong file",
      out["applied"] is True and target.is_file() and "62% tai" in target.read_text(encoding="utf-8"), out)
check("apply lan 2 -> idempotent, van applied",
      dm.apply_proposal("IDC", pid)["applied"] is True)
check("undo sau khi tao file moi -> file bi go",
      dm.undo_apply("IDC", pid)["undone"] is True and not target.exists())

# hash guard: file dich da doi tu khi de xuat duoc viet thi tu choi ap dung
tmp = tempfile.mkdtemp(prefix="idc-dream-6b-")
brain, state = _mk(tmp)
old_file = brain / "memory" / "facts" / "cu.md"
old_file.parent.mkdir(parents=True, exist_ok=True)
old_file.write_text("Noi dung cu.\n", encoding="utf-8")
host = _host(brain, state, SESSIONS, [ANALYZER_OK, VERIFIER_KEEP])
dm = dream.Dreamer(dream.Store(state / "dream.sqlite3"), host, clock=lambda: CLOCK_0230)
import hashlib
base = hashlib.sha256(old_file.read_bytes()).hexdigest()
dm.store.write(lambda c: c.execute(
    "INSERT INTO proposals(id, brain, kind, target_path, title, body, evidence, verified, status,"
    " created_at, reviewed_at, base_sha, applied_sha, run_id, backup) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
    ("drm_" + "a" * 16, "IDC", "fact", "memory/facts/cu.md", "T", "B moi.", "[]", 1,
     "pending", CLOCK_0230, None, base, "", "drm_" + "b" * 16, "")))
old_file.write_text("Ai do da sua file nay sau do.\n", encoding="utf-8")
try:
    dm.apply_proposal("IDC", "drm_" + "a" * 16)
    check("hash guard: file doi -> apply phai tu choi", False, "khong raise")
except dream.ConflictError:
    check("hash guard: file doi -> apply phai tu choi", True)
check("sau khi tu choi, file dich van nguyen (khong bi ghi de)",
      old_file.read_text(encoding="utf-8") == "Ai do da sua file nay sau do.\n")

# ---- 7. Tu choi: khong ghi gi vao brain ----
tmp = tempfile.mkdtemp(prefix="idc-dream-7-")
brain, state = _mk(tmp)
host = _host(brain, state, SESSIONS, [ANALYZER_OK, VERIFIER_KEEP])
dm = dream.Dreamer(dream.Store(state / "dream.sqlite3"), host, clock=lambda: CLOCK_0230)
dm.run("IDC", force=True)
pid = dm.list_proposals("IDC")[0]["id"]
check("reject -> marked rejected", dm.reject_proposal("IDC", pid)["rejected"] is True)
check("sau reject, brain van khong co file de xuat",
      not (brain / "memory" / "facts" / "ups-2a.md").exists())

# ---- 8. Cong dem: chay 1 lan/dem, lan 2 cung dem la no-op ----
tmp = tempfile.mkdtemp(prefix="idc-dream-8-")
brain, state = _mk(tmp)
host = _host(brain, state, SESSIONS, [ANALYZER_OK, VERIFIER_KEEP])
dm = dream.Dreamer(dream.Store(state / "dream.sqlite3"), host, clock=lambda: CLOCK_0230)
first = dm.run("IDC", force=True)
second = dm.run("IDC", force=False)
check("lan 2 cung dem (khong force) -> skipped not_due",
      first["state"] == "done" and second["state"] == "skipped"
      and second.get("reason") == "not_due", second)

# ---- 9. Verifier hong -> van giu de xuat qua cua code, danh dau chua kiem chung ----
tmp = tempfile.mkdtemp(prefix="idc-dream-9a-")
brain, state = _mk(tmp)
host = _host(brain, state, SESSIONS, [ANALYZER_OK, RuntimeError("model loi")])
dm = dream.Dreamer(dream.Store(state / "dream.sqlite3"), host, clock=lambda: CLOCK_0230)
result = dm.run("IDC", force=True)
props = dm.list_proposals("IDC")
check("verifier goi model hong -> van 1 de xuat, verified=0",
      result["state"] == "done" and len(props) == 1 and props[0]["verified"] == 0, result)

tmp = tempfile.mkdtemp(prefix="idc-dream-9b-")
brain, state = _mk(tmp)
host = _host(brain, state, SESSIONS, [ANALYZER_OK, json.dumps({"keep": "all"}, ensure_ascii=False)])
dm = dream.Dreamer(dream.Store(state / "dream.sqlite3"), host, clock=lambda: CLOCK_0230)
result = dm.run("IDC", force=True)
props = dm.list_proposals("IDC")
check("verifier tra keep khong dung duoc -> van 1 de xuat, verified=0",
      result["state"] == "done" and len(props) == 1 and props[0]["verified"] == 0, result)

# ---- 10. Loi analyzer giu nguyen van + so phien da thay (14/11/2026: 7 lan chay failed chi de lai ten lop) ----
tmp = tempfile.mkdtemp(prefix="idc-dream-10-")
brain, state = _mk(tmp)
host = _host(brain, state, SESSIONS, [RuntimeError("final_error: 404 model khong ton tai")])
dm = dream.Dreamer(dream.Store(state / "dream.sqlite3"), host, clock=lambda: CLOCK_0230)
result = dm.run("IDC", force=True)
check("analyzer loi -> failed, error giu nguyen van 'final_error: 404', sessions_seen=1",
      result["state"] == "failed" and "final_error: 404" in result["error"] and result["sessions_seen"] == 1,
      result)

# ---- 12. Analyzer timeout lan 1 -> thu lai lan 2 thanh cong (14/11/2026: Gemini ReadTimeout) ----
tmp = tempfile.mkdtemp(prefix="idc-dream-12-")
brain, state = _mk(tmp)
host = _host(brain, state, SESSIONS, [RuntimeError("ReadTimeout"), ANALYZER_OK, VERIFIER_KEEP])
dm = dream.Dreamer(dream.Store(state / "dream.sqlite3"), host, clock=lambda: CLOCK_0230)
result = dm.run("IDC", force=True)
check("analyzer timeout lan 1, thu lai thanh cong -> done, 1 de xuat",
      result["state"] == "done" and result["proposals_created"] == 1, result)

# ---- 13. Analyzer hong ca 2 lan -> failed, giu nguyen van loi cuoi ----
tmp = tempfile.mkdtemp(prefix="idc-dream-13-")
brain, state = _mk(tmp)
host = _host(brain, state, SESSIONS, [RuntimeError("ReadTimeout")])
dm = dream.Dreamer(dream.Store(state / "dream.sqlite3"), host, clock=lambda: CLOCK_0230)
result = dm.run("IDC", force=True)
check("analyzer hong ca 2 lan -> failed, error giu 'ReadTimeout'",
      result["state"] == "failed" and "ReadTimeout" in result["error"], result)

# ---- 11. Khong co phien moi -> khong chay vo ich ----
tmp = tempfile.mkdtemp(prefix="idc-dream-9-")
brain, state = _mk(tmp)
host = _host(brain, state, [], [ANALYZER_OK, VERIFIER_KEEP])
dm = dream.Dreamer(dream.Store(state / "dream.sqlite3"), host, clock=lambda: CLOCK_0230)
result = dm.run("IDC", force=True)
check("khong co phien moi -> no_new_sessions, 0 de xuat",
      result["state"] == "no_new_sessions" and result["proposals_created"] == 0, result)

print()
if _fails:
    print(f"FAIL: {len(_fails)} kiem tra hong: {_fails}")
    raise SystemExit(1)
print("Tat ca kiem tra dream job deu pass.")
