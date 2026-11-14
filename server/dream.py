"""Dream job: nightly consolidation of session transcripts into reviewable proposals.

Anthropic's dreaming (Claude Managed Agents, research preview, blog 19/05/2026;
research "The components of agent memory", 06/11/2026) is an offline pass that
reads past session transcripts and an existing memory store, then produces a NEW
reorganized store: duplicates merged, stale entries replaced, new insights
surfaced. The input store is never modified. Anthropic's own cookbook ("Dreaming
with a dynamic workflow", 11/2026) builds the same thing with a nightly cron:
one analyzer agent per transcript, an organizer pass, and a read-only mount of
the result until it is reviewed.

This module is the IDC Harness equivalent, adapted to this project's governance:

- The job runs once a night (02:00-04:00 local) in a worker thread, text-only,
  on the background model. It cannot send, buy or post anything by construction.
- It NEVER writes to the brain. It only writes proposals into its own SQLite
  store. A proposal reaches the brain only when the owner presses Apply on the
  dashboard (page "Tu hoc"), with a hash guard on the target file.
- Modes: "suggest" (default) and "dry-run". There is NO "auto" mode: a config
  value of "auto" is downgraded to "suggest" and logged. The brain's wiki is
  the live knowledge base; dream output must never reach it unreviewed.
- Proposals may only target memory/ and wiki/. They NEVER target sources/:
  source documents are ground truth, not something a dream rewrites.

Passes (mirroring Anthropic's cookbook):
1. Analyzer: one call over the day's digest extracts candidate facts, lessons
   and corrections, each with verbatim evidence quotes from the transcript.
2. Verification: candidates whose quotes cannot be found in the digest are
   dropped in code; a second call then judges whether each surviving candidate
   is actually supported by the transcript. Only supported candidates become
   proposals. A note is a prediction and can be wrong, so nothing is promoted
   without evidence.
3. Organizer: candidates are grouped by target file and deduplicated against
   each other and against proposals still pending review.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import sqlite3
import threading
import time
from contextlib import closing
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

DREAM_HOUR = 2               # nightly window starts at 02:00 local
MAX_SESSIONS = 5             # sessions read per run (learn.py digest uses 3; dream reads a little more)
MAX_MSGS = 12                # last messages per session
MSG_LIMIT = 3000             # chars per message in the digest
DIGEST_LIMIT = 16000         # chars of digest per run (learn.py uses 24000; dream
                             # trims to 16000 so the free-tier API answers faster)
MAX_PROPOSALS = 10           # proposals stored per run
RETRY_PAUSE = 20             # seconds between the two text_call attempts
ALLOWED_PREFIXES = ("memory/", "wiki/")
MODES = ("suggest", "dry-run")
CONFIG_NAME = "dream_config.json"
STATE_NAME = "dream-state.json"


class DreamError(Exception):
    """A dream run failed: the work stays queued for the next night."""


class ConflictError(Exception):
    """The target file changed since the proposal was written: never overwrite it."""


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _cut(text, limit: int = MSG_LIMIT) -> str:
    text = str(text or "")
    return text if len(text) <= limit else text[:limit] + "\n[...]"


def _norm_ws(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def parse_json(text: str):
    """The first JSON object in a model answer (fenced or bare)."""
    text = str(text or "")
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("no_json")
    return json.loads(text[start:end + 1])


def normalize_mode(mode) -> str:
    """Only suggest and dry-run exist. "auto" is downgraded to "suggest": dream
    output must never reach the brain without the owner pressing Apply."""
    mode = str(mode or "suggest").strip().lower()
    if mode == "auto":
        print("[dream] che do 'auto' khong ton tai cho dream job: ha xuong 'suggest'", flush=True)
        return "suggest"
    return mode if mode in MODES else "suggest"


def default_config() -> dict:
    return {"enabled": True, "mode": "suggest", "hour": DREAM_HOUR}


def read_config(state_dir) -> dict:
    cfg = default_config()
    try:
        raw = json.loads((Path(state_dir) / CONFIG_NAME).read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            cfg.update({k: v for k, v in raw.items() if k in cfg})
    except Exception:
        pass
    cfg["mode"] = normalize_mode(cfg.get("mode"))
    cfg["enabled"] = bool(cfg.get("enabled", True))
    try:
        cfg["hour"] = max(0, min(23, int(cfg.get("hour", DREAM_HOUR))))
    except Exception:
        cfg["hour"] = DREAM_HOUR
    return cfg


def save_config(state_dir, cfg: dict) -> dict:
    merged = read_config(state_dir)
    for key in ("enabled", "mode", "hour"):
        if key in cfg:
            merged[key] = cfg[key]
    merged["mode"] = normalize_mode(merged.get("mode"))
    merged["enabled"] = bool(merged.get("enabled", True))
    try:
        merged["hour"] = max(0, min(23, int(merged.get("hour", DREAM_HOUR))))
    except Exception:
        merged["hour"] = DREAM_HOUR
    (Path(state_dir) / CONFIG_NAME).write_text(
        json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    return merged


def valid_target(target: str) -> str:
    """A proposal target, normalized, or "": only memory/ and wiki/ files, never
    sources/ (ground truth) and never outside the brain."""
    target = str(target or "").strip().replace("\\", "/")
    if target.startswith("/") or ".." in Path(target).parts:
        return ""
    if not target.endswith(".md"):
        return ""
    if not target.startswith(ALLOWED_PREFIXES):
        return ""
    return target


# -- storage -----------------------------------------------------------------------------------------

_SCHEMA = """
CREATE TABLE IF NOT EXISTS proposals(id TEXT PRIMARY KEY, brain TEXT, kind TEXT, target_path TEXT,
    title TEXT, body TEXT, evidence TEXT, verified INTEGER DEFAULT 0, status TEXT,
    created_at REAL, reviewed_at REAL, base_sha TEXT, applied_sha TEXT, run_id TEXT, backup TEXT);
CREATE INDEX IF NOT EXISTS proposals_status ON proposals(brain, status, created_at);
CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY, brain TEXT, started_at REAL, finished_at REAL,
    state TEXT, sessions_seen INTEGER DEFAULT 0, proposals_created INTEGER DEFAULT 0, error TEXT);
CREATE INDEX IF NOT EXISTS runs_brain ON runs(brain, started_at);
"""


class Store:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        with self._conn() as c:
            c.executescript(_SCHEMA)

    def _conn(self):
        conn = sqlite3.connect(self.path, timeout=15)
        conn.row_factory = sqlite3.Row
        return conn

    def write(self, fn):
        with self._lock, closing(self._conn()) as c:
            with c:
                return fn(c)

    def read(self, sql: str, args=()) -> list:
        with closing(self._conn()) as c:
            return [dict(r) for r in c.execute(sql, args).fetchall()]


# -- host --------------------------------------------------------------------------------------------

@dataclass
class Host:
    """Everything the dreamer needs from the server. All callables are synchronous;
    the dreamer runs in a worker thread with no event loop."""
    text_call: Callable[[str, str], str]                 # (system, prompt) -> text, background model, text only
    sessions_reader: Callable[[str], list]               # brain -> [{"session_id", "messages": [{role, content, ts}]}]
    brain_root: Callable[[str], Path]                    # brain -> folder of the brain on disk
    policy_on: Callable[[str], bool] = lambda brain: True  # brain -> learning allowed (improvement policy not "off")
    state_dir: Path = Path(".")
    backups: Path = None                                 # folder for pre-apply backups of target files


# -- prompts -----------------------------------------------------------------------------------------

ANALYZER_SYSTEM = ("Ban doc nhat ky hoi thoai cua mot ky su van hanh trung tam du lieu (IDC) "
                   "voi tro ly AI cua anh ay, va rut ra nhung dieu dang ghi nho lau dai. "
                   "Tra loi CHI BANG JSON.")


def analyzer_prompt(digest: str) -> str:
    return (
        "Duoi day la nhat ky cac phien tro chuyen gan day (tin nhan cua nguoi dung va cau tra loi cua tro ly).\n"
        "Hay rut ra cac de xuat ghi nho, moi de xuat la mot ghi chu nho, tap trung, co bang chung.\n\n"
        "CHI de xuat nhung dieu co trong nhat ky, va phan loai:\n"
        "- \"fact\": su kien/thong so/quy tac da KIEM CHUNG trong phien (vi du: thong so thiet bi vua xac nhan, "
        "cach xu ly su co da lam xong va co ket qua).\n"
        "- \"lesson\": bai hoc rut ra tu mot sai lam hoac su co (chi khi nhat ky cho thay ro cai gi sai va cai gi dung).\n"
        "- \"correction\": thong tin trong kho tri thuc hien tai co ve SAI hoac LOI THOI theo nhat ky (ghi ro cai cu va cai moi).\n\n"
        "KHONG de xuat: trang thai tam thoi doc duoc tu man hinh (so lieu hien tai, vi tri, so du), cau hoi chua co cau tra loi, "
        "phong doan khong co bang chung. It ma chat thang nhieu ma rac: toi da 10 de xuat, moi de xuat phai co it nhat "
        "MOT trich dan nguyen van tu nhat ky lam bang chung.\n\n"
        "Moi de xuat can mot file dich: chi duoc chon trong hai thu muc:\n"
        "- \"memory/facts/<slug>.md\" cho su kien/bai hoc rieng le (slug ngan, chu thuong, gach noi);\n"
        "- \"wiki/<duong-dan>.md\" cho kien thuc thuoc mot mang cua trung tam (vi du \"wiki/13 - Su co & Bai hoc/<ten>.md\").\n"
        "TUYET DOI KHONG de xuat file trong sources/ (do la tai lieu goc, khong phai cho dream viet lai).\n\n"
        "Tra loi CHI BANG JSON: {\"proposals\": [{\"kind\": \"fact|lesson|correction\", "
        "\"target\": \"memory/facts/<slug>.md\", \"title\": \"...\", \"body\": \"...noi dung ghi chu dang Markdown...\", "
        "\"evidence\": [\"...trich dan nguyen van...\", \"...\"]}]}\n\n"
        f"## Nhat ky\n{_cut(digest, DIGEST_LIMIT)}\n")


VERIFIER_SYSTEM = ("Ban kiem tra tung de xuat ghi nho xem no co that su duoc nhat ky ho tro hay khong. "
                   "Nghiem khac: chi giu lai de xuat co bang chung ro rang. Tra loi CHI BANG JSON.")


def verifier_prompt(digest: str, candidates: list) -> str:
    listing = "\n\n".join(
        f"### De xuat {i + 1}\nLoai: {c.get('kind')}\nTieu de: {c.get('title')}\n"
        f"Noi dung:\n{c.get('body')}\nBang chung dua ra:\n"
        + "\n".join(f"- {q}" for q in (c.get("evidence") or []))
        for i, c in enumerate(candidates))
    return (
        "Duoi day la nhat ky va danh sach de xuat rut ra tu no. Voi MOI de xuat, quyet dinh:\n"
        "- \"keep\": nhat ky HO TRO RO RANG cho noi dung de xuat (bang chung trich dan dung voi nhat ky).\n"
        "- \"drop\": khong du bang chung, suy dien qua xa, hoac noi dung mo ho/khong kiem chung duoc.\n\n"
        "Tra loi CHI BANG JSON: {\"keep\": [1, 3], \"drop\": {\"2\": \"ly do ngan\"}}\n\n"
        f"## Nhat ky\n{_cut(digest, DIGEST_LIMIT)}\n\n## De xuat\n{listing}\n")


# -- the dreamer -------------------------------------------------------------------------------------

class Dreamer:
    def __init__(self, store: Store, host: Host, *, clock: Callable[[], float] = time.time):
        self.store, self.host, self.clock = store, host, clock

    # config + nightly state

    def config(self) -> dict:
        return read_config(self.host.state_dir)

    def set_config(self, cfg: dict) -> dict:
        return save_config(self.host.state_dir, cfg or {})

    def _state_path(self) -> Path:
        return Path(self.host.state_dir) / STATE_NAME

    def _state(self) -> dict:
        try:
            raw = json.loads(self._state_path().read_text(encoding="utf-8"))
            return raw if isinstance(raw, dict) else {}
        except Exception:
            return {}

    def _save_state(self, state: dict) -> None:
        self._state_path().write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")

    def _paused(self) -> bool:
        return os.environ.get("JAVIS_DREAM_PAUSED") == "1"

    def due(self, brain: str, now: Optional[float] = None) -> bool:
        """One run per night, inside the configured hour window, only when there
        are new session messages since the last run."""
        cfg = self.config()
        if not cfg.get("enabled") or self._paused():
            return False
        try:
            if not self.host.policy_on(brain):
                return False
        except Exception:
            return False
        now = now if now is not None else self.clock()
        local = time.localtime(now)
        if local.tm_hour != int(cfg.get("hour", DREAM_HOUR)):
            return False
        state = self._state().get(brain) or {}
        if state.get("last_run_date") == time.strftime("%Y-%m-%d", local):
            return False
        return True

    # input: recent sessions, digest like learn.py

    def _collect(self, brain: str, since_ts: float):
        """Recent sessions with new messages since `since_ts`: digest + the newest
        message timestamp seen. Mirrors learn.py digest caps."""
        try:
            sessions = self.host.sessions_reader(brain) or []
        except Exception:
            sessions = []
        parts, seen_ts, seen_sessions = [], float(since_ts or 0), 0
        total = 0
        for session in sessions[:MAX_SESSIONS]:
            msgs = [m for m in (session.get("messages") or [])
                    if m.get("role") in ("user", "assistant") and m.get("content")]
            new = [m for m in msgs if float(m.get("ts") or 0) > float(since_ts or 0)]
            if not new:
                continue
            seen_sessions += 1
            tail = msgs[-MAX_MSGS:]
            for m in tail:
                who = "NGUOI DUNG" if m["role"] == "user" else "IDC HARNESS(assistant)"
                txt = str(m["content"])[:MSG_LIMIT]
                parts.append(f"[{who}] {txt}")
                total += len(txt)
                try:
                    seen_ts = max(seen_ts, float(m.get("ts") or 0))
                except Exception:
                    pass
                if total > DIGEST_LIMIT:
                    break
            if total > DIGEST_LIMIT:
                break
        return "\n\n".join(parts), seen_ts, seen_sessions

    # passes

    def _call_with_retry(self, fn, what: str):
        """Call a model text_call once, retrying once after a 20s pause on
        failure. The free-tier Gemini API sometimes stalls a request past
        httpx's 120s read timeout (ReadTimeout, 14/11/2026: the analyzer
        died on the first attempt); a retry 20s later often gets through
        once the provider queue drains. Two attempts fit the host's 300s
        text_call cap (120s + 20s + 120s)."""
        last = None
        for attempt in (1, 2):
            try:
                return fn()
            except Exception as error:
                last = error
                print(f"[dream] {what} lan {attempt} loi: "
                      f"{type(error).__name__}: {str(error)[:120]}", flush=True)
                if attempt == 1:
                    time.sleep(RETRY_PAUSE)
        raise last

    def _analyze(self, digest: str) -> list:
        try:
            data = parse_json(self._call_with_retry(
                lambda: self.host.text_call(ANALYZER_SYSTEM, analyzer_prompt(digest)),
                "analyzer"))
        except Exception as error:
            # Giu NGUYEN VAN loi cua engine (vd. "final_error: 404 model khong ton tai"):
            # chi ghi ten lop (EngineOutcomeError) thi chu khong the biet no hong o dau,
            # dung nhu 7 lan chay failed ngay 14/11/2026 chi de lai cai ten chung chung.
            raise DreamError(f"analyzer_failed: {type(error).__name__}: {str(error)[:200]}") from error
        items = data.get("proposals") if isinstance(data, dict) else None
        if not isinstance(items, list):
            raise DreamError("analyzer_no_proposals")
        out = []
        for row in items[:MAX_PROPOSALS]:
            if not isinstance(row, dict):
                continue
            target = valid_target(row.get("target"))
            title = str(row.get("title") or "").strip()[:200]
            body = str(row.get("body") or "").strip()
            evidence = [str(q).strip() for q in (row.get("evidence") or []) if str(q).strip()][:5]
            kind = str(row.get("kind") or "").strip()
            if not target or not title or not body or not evidence or kind not in ("fact", "lesson", "correction"):
                continue
            out.append({"kind": kind, "target": target, "title": title, "body": body[:6000],
                        "evidence": evidence})
        return out

    def _verify(self, digest: str, candidates: list) -> tuple:
        """Two gates: (1) in code, every candidate needs at least one evidence
        quote that literally appears in the digest; (2) a model call judges
        whether the digest really supports each surviving candidate.

        Returns (kept, model_checked). If the model verifier fails or returns
        an unusable answer, the code-gate survivors are kept anyway but marked
        unverified (verified=0): a broken verifier must not silently eat the
        whole night's work, and the owner can see the missing tick in review."""
        flat = _norm_ws(digest)
        kept = []
        for c in candidates:
            if any(_norm_ws(q) and _norm_ws(q) in flat for q in c["evidence"]):
                kept.append(c)
        if not kept:
            return [], True
        try:
            data = parse_json(self._call_with_retry(
                lambda: self.host.text_call(VERIFIER_SYSTEM, verifier_prompt(digest, kept)),
                "verifier"))
        except Exception as error:
            print(f"[dream] verifier goi model hong ({type(error).__name__}), "
                  f"giu {len(kept)} de xuat qua cua code, danh dau chua kiem chung", flush=True)
            return kept, False
        keep_idx = set()
        usable = False
        if isinstance(data, dict) and isinstance(data.get("keep"), list):
            for i in data.get("keep"):
                try:
                    keep_idx.add(int(i) - 1)
                    usable = True
                except Exception:
                    pass
        if not usable:
            print("[dream] verifier tra ve danh sach keep khong dung duoc, "
                  f"giu {len(kept)} de xuat qua cua code, danh dau chua kiem chung", flush=True)
            return kept, False
        return [c for i, c in enumerate(kept) if i in keep_idx], True

    def _organize(self, brain: str, candidates: list, run_id: str) -> list:
        """Group by target file, drop duplicates inside this run and duplicates
        of proposals still pending review."""
        pending = {(r["target_path"], _norm_ws(r["title"]).lower())
                   for r in self.store.read(
                       "SELECT target_path, title FROM proposals WHERE brain=? AND status='pending'", (brain,))}
        seen, out = set(), []
        for c in candidates:
            key = (c["target"], _norm_ws(c["title"]).lower())
            if key in seen or key in pending:
                continue
            seen.add(key)
            out.append(c)
        return out

    # one run

    def run(self, brain: str, force: bool = False) -> dict:
        run_id, now = "drm_" + secrets.token_hex(8), self.clock()
        cfg = self.config()
        if not cfg.get("enabled") or self._paused():
            return {"run_id": run_id, "state": "skipped", "reason": "disabled_or_paused"}
        try:
            if not self.host.policy_on(brain):
                return {"run_id": run_id, "state": "skipped", "reason": "policy_off"}
        except Exception:
            return {"run_id": run_id, "state": "skipped", "reason": "policy_off"}
        if not force and not self.due(brain, now):
            return {"run_id": run_id, "state": "skipped", "reason": "not_due"}
        state = self._state()
        brain_state = state.get(brain) or {}
        since_ts = float(brain_state.get("last_seen_ts") or 0)
        self.store.write(lambda c: c.execute(
            "INSERT INTO runs(id, brain, started_at, state) VALUES(?,?,?,?)",
            (run_id, brain, now, "running")))

        def finish(state_name, sessions_seen=0, proposals_created=0, error=""):
            self.store.write(lambda c: c.execute(
                "UPDATE runs SET finished_at=?, state=?, sessions_seen=?, proposals_created=?, error=? WHERE id=?",
                (self.clock(), state_name, sessions_seen, proposals_created, error[:300], run_id)))
            print(f"[dream] run {run_id} brain={brain} state={state_name} "
                  f"sessions={sessions_seen} proposals={proposals_created} error={error[:200]}", flush=True)
            return {"run_id": run_id, "state": state_name, "sessions_seen": sessions_seen,
                    "proposals_created": proposals_created, "error": error}

        sessions_seen = 0
        try:
            digest, seen_ts, sessions_seen = self._collect(brain, since_ts)
            if not digest.strip():
                return finish("no_new_sessions", sessions_seen)
            candidates = self._analyze(digest)
            verified, model_checked = self._verify(digest, candidates)
            final = self._organize(brain, verified, run_id)
            created = 0
            if cfg.get("mode") == "dry-run":
                return finish("dry_run", sessions_seen, 0)
            for c in final:
                target_path = Path(self.host.brain_root(brain)) / c["target"]
                base_sha = _sha_bytes(target_path.read_bytes()) if target_path.is_file() else ""
                self.store.write(lambda cc: cc.execute(
                    "INSERT INTO proposals(id, brain, kind, target_path, title, body, evidence, verified, "
                    "status, created_at, reviewed_at, base_sha, applied_sha, run_id, backup) "
                    "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    ("drm_" + secrets.token_hex(8), brain, c["kind"], c["target"], c["title"], c["body"],
                     json.dumps(c["evidence"], ensure_ascii=False), 1 if model_checked else 0,
                     "pending", now, None, base_sha, "", run_id, "")))
                created += 1
            brain_state["last_run_date"] = time.strftime("%Y-%m-%d", time.localtime(now))
            brain_state["last_seen_ts"] = seen_ts
            state[brain] = brain_state
            self._save_state(state)
            return finish("done", sessions_seen, created)
        except DreamError as error:
            return finish("failed", sessions_seen, error=str(error))
        except Exception as error:  # noqa: BLE001 - a run never stays "running"
            return finish("failed", sessions_seen, error=f"{type(error).__name__}: {error}")

    # owner view: list / apply / reject / undo

    def list_proposals(self, brain: str, status: Optional[str] = None, limit: int = 50) -> list:
        sql = ("SELECT id, brain, kind, target_path, title, body, evidence, verified, status, "
               "created_at, reviewed_at, base_sha, run_id FROM proposals WHERE brain=?")
        args: list = [brain]
        if status:
            sql += " AND status=?"
            args.append(status)
        sql += " ORDER BY created_at DESC LIMIT ?"
        args.append(limit)
        rows = self.store.read(sql, tuple(args))
        for row in rows:
            try:
                row["evidence"] = json.loads(row.get("evidence") or "[]")
            except Exception:
                row["evidence"] = []
        return rows

    def history(self, brain: str, limit: int = 20) -> list:
        return self.store.read(
            "SELECT id, brain, started_at, finished_at, state, sessions_seen, proposals_created, error "
            "FROM runs WHERE brain=? ORDER BY started_at DESC LIMIT ?", (brain, limit))

    def stats(self, brain: str) -> dict:
        pending = self.store.read(
            "SELECT COUNT(*) AS n FROM proposals WHERE brain=? AND status='pending'", (brain,))[0]["n"]
        applied = self.store.read(
            "SELECT COUNT(*) AS n FROM proposals WHERE brain=? AND status='applied'", (brain,))[0]["n"]
        return {"pending": pending, "applied": applied}

    def _get(self, brain: str, proposal_id: str) -> dict:
        rows = self.store.read("SELECT * FROM proposals WHERE id=? AND brain=?", (proposal_id, brain))
        if not rows:
            raise ValueError("proposal_not_found")
        return rows[0]

    def apply_proposal(self, brain: str, proposal_id: str) -> dict:
        """Dashboard-only: write the proposal into the brain with a hash guard.
        The file must be exactly as it was when the proposal was written, or the
        apply is refused. The previous content is backed up for undo."""
        row = self._get(brain, proposal_id)
        if row["status"] == "applied":
            return {"proposal_id": proposal_id, "applied": True}
        if row["status"] != "pending":
            raise ConflictError("not_pending")
        if not self.host.policy_on(brain):
            raise PermissionError("improvement_disabled")
        target = valid_target(row["target_path"])
        if not target:
            raise ValueError("invalid_target")
        path = Path(self.host.brain_root(brain)) / target
        if ".." in path.parts:
            raise ValueError("invalid_target")
        old = path.read_bytes() if path.is_file() else None
        if old is not None and _sha_bytes(old) != row["base_sha"]:
            raise ConflictError("changed_since")
        backups = Path(self.host.backups) if self.host.backups else Path(self.host.state_dir) / "dream-backups"
        backups.mkdir(parents=True, exist_ok=True)
        backup = backups / f"{proposal_id}.bak"
        if old is not None:
            backup.write_bytes(old)
        stamp = time.strftime("%Y-%m-%d", time.localtime(self.clock()))
        header = (f"---\ntitle: {row['title']}\nsource: dream {row['run_id']} ({stamp})\n"
                  f"status: de xuat da duyet\n---\n\n")
        if old is None:
            path.parent.mkdir(parents=True, exist_ok=True)
            new = (header + f"# {row['title']}\n\n" + row["body"].rstrip() + "\n").encode("utf-8")
        else:
            new = old + (f"\n\n## Cap nhat {stamp} (dream {row['run_id']})\n\n"
                         + row["body"].rstrip() + "\n").encode("utf-8")
        temp = path.with_name(path.name + f".dream-{proposal_id}.tmp")
        temp.write_bytes(new)
        os.replace(temp, path)
        self.store.write(lambda c: c.execute(
            "UPDATE proposals SET status='applied', reviewed_at=?, applied_sha=?, backup=? WHERE id=?",
            (self.clock(), _sha_bytes(new), str(backup) if old is not None else "", proposal_id)))
        return {"proposal_id": proposal_id, "applied": True, "target": target}

    def reject_proposal(self, brain: str, proposal_id: str) -> dict:
        row = self._get(brain, proposal_id)
        if row["status"] != "pending":
            raise ConflictError("not_pending")
        self.store.write(lambda c: c.execute(
            "UPDATE proposals SET status='rejected', reviewed_at=? WHERE id=?", (self.clock(), proposal_id)))
        return {"proposal_id": proposal_id, "rejected": True}

    def undo_apply(self, brain: str, proposal_id: str) -> dict:
        row = self._get(brain, proposal_id)
        if row["status"] != "applied":
            raise ConflictError("nothing_to_undo")
        path = Path(self.host.brain_root(brain)) / valid_target(row["target_path"])
        current = path.read_bytes() if path.is_file() else None
        if current is None or _sha_bytes(current) != row["applied_sha"]:
            raise ConflictError("changed_since")
        backup = Path(row["backup"]) if row["backup"] else None
        if backup is None or not backup.is_file():
            # The proposal created the file: removing it restores the old state.
            path.unlink()
        else:
            temp = path.with_name(path.name + f".dream-undo-{proposal_id}.tmp")
            temp.write_bytes(backup.read_bytes())
            os.replace(temp, path)
        self.store.write(lambda c: c.execute(
            "UPDATE proposals SET status='rejected', reviewed_at=? WHERE id=?", (self.clock(), proposal_id)))
        return {"proposal_id": proposal_id, "undone": True}
