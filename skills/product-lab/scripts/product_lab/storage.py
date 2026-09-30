"""Keep local experiment records and snapshots separate from working source."""

import hashlib
import json
import os
import shutil
import sqlite3
import stat
from datetime import datetime, timezone
from pathlib import Path

from .model import LabError, canonical, digest, identifier, validate_contract

IGNORED = {".git", "__pycache__", ".venv", "node_modules", ".product-lab"}


def now():
    return datetime.now(timezone.utc).isoformat()


def tree_digest(root):
    root = Path(root)
    if not root.is_dir() or root.is_symlink():
        raise LabError(f"Expected a real directory: {root}")
    files = {}
    total = 0
    for directory, directories, filenames in os.walk(root, followlinks=False):
        directories[:] = sorted(name for name in directories if name not in IGNORED)
        for name in sorted(directories + [name for name in filenames if name not in IGNORED]):
            path = Path(directory) / name
            relative = path.relative_to(root)
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode) or not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
                raise LabError(f"Unsupported snapshot entry: {relative}")
            if path.is_dir():
                files[str(relative)] = {"kind": "directory"}
            if path.is_file():
                total += path.stat().st_size
                if total > 50_000_000:
                    raise LabError("Snapshot exceeds the 50 MB prototype limit")
                files[str(relative)] = {
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "executable": bool(mode & 0o111),
                }
    if not files:
        raise LabError("Snapshot is empty")
    return digest(files)


def snapshot(source, target):
    if Path(source).is_symlink():
        raise LabError("Snapshot source must not be a symlink")
    source, target = Path(source).resolve(), Path(target).resolve()
    if target.is_relative_to(source):
        raise LabError("Store snapshots outside the candidate or evaluator directory")
    before = tree_digest(source)
    shutil.copytree(source, target, ignore=shutil.ignore_patterns(*IGNORED))
    if tree_digest(target) != before or tree_digest(source) != before:
        raise LabError("Source changed during snapshot creation")
    return before


class Lab:
    def __init__(self, root):
        self.root = Path(root).resolve()
        path = self.root / "lab.sqlite3"
        if not path.is_file():
            raise LabError(f"No lab at {self.root}. Run init first")
        self.db = sqlite3.connect(path, timeout=5)
        self.db.row_factory = sqlite3.Row

    def close(self):
        self.db.close()

    def get(self, kind, key):
        row = self.db.execute(
            "SELECT payload, hash FROM records WHERE kind=? AND id=?", (kind, key)
        ).fetchone()
        if row is None:
            raise LabError(f"Unknown {kind}: {key}")
        value = json.loads(row["payload"])
        if digest(value) != row["hash"]:
            raise LabError(f"Changed record: {kind}/{key}")
        return value

    def all(self, kind):
        keys = self.db.execute("SELECT id FROM records WHERE kind=? ORDER BY rowid", (kind,))
        return [self.get(kind, row["id"]) for row in keys.fetchall()]

    def put(self, kind, key, value, *, replace=False):
        statement = "INSERT OR REPLACE" if replace else "INSERT"
        try:
            self.db.execute(
                f"{statement} INTO records VALUES (?, ?, ?, ?)",
                (kind, key, canonical(value), digest(value)),
            )
        except sqlite3.IntegrityError as exc:
            raise LabError(f"Already registered: {kind}/{key}") from exc
        self.db.execute(
            "INSERT INTO events (at, kind, id, payload) VALUES (?, ?, ?, ?)",
            (now(), kind, key, canonical(value)),
        )

    @classmethod
    def create(cls, root, contract, evaluator):
        validate_contract(contract)
        if Path(evaluator).is_symlink():
            raise LabError("Evaluator source must not be a symlink")
        evaluator = Path(evaluator).resolve()
        if not (evaluator / "evaluate.py").is_file():
            raise LabError("Evaluator directory must contain evaluate.py")
        root = Path(root).resolve()
        if root.exists():
            raise LabError("Choose a new lab directory. Existing evidence is preserved")
        # Validate the input tree before creating any state.
        tree_digest(evaluator)
        if root.is_relative_to(evaluator):
            raise LabError("Lab must be outside the evaluator directory")
        root.mkdir(parents=True, mode=0o700)
        fingerprint = snapshot(evaluator, root / "evaluator")
        db = sqlite3.connect(root / "lab.sqlite3")
        with db:
            db.executescript("""
                CREATE TABLE records (
                    kind TEXT, id TEXT, payload TEXT, hash TEXT, PRIMARY KEY (kind, id)
                );
                CREATE TABLE events (
                    seq INTEGER PRIMARY KEY, at TEXT, kind TEXT, id TEXT, payload TEXT
                );
            """)
        db.close()
        lab = cls(root)
        with lab.db:
            lab.put(
                "contract",
                "main",
                {
                    "contract": contract,
                    "digest": digest(contract),
                    "evaluator_digest": fingerprint,
                    "created_at": now(),
                },
            )
            lab.put(
                "state",
                "main",
                {"original": None, "current": None, "busy": None, "validation_used": False},
            )
        return lab

    @property
    def contract(self):
        record = self.get("contract", "main")
        if digest(record["contract"]) != record["digest"]:
            raise LabError("Contract digest changed")
        return record["contract"]

    def verify(self, candidate_id):
        contract = self.get("contract", "main")
        if tree_digest(self.root / "evaluator") != contract["evaluator_digest"]:
            raise LabError("Evaluator snapshot changed")
        candidate = self.get("candidate", candidate_id)
        if tree_digest(self.root / candidate["path"]) != candidate["digest"]:
            raise LabError(f"Candidate snapshot changed: {candidate_id}")
        return candidate

    def register(self, candidate_id, source, hypothesis):
        identifier(candidate_id)
        if not isinstance(hypothesis, str) or not hypothesis.strip():
            raise LabError("State the candidate hypothesis before running it")
        if self.get("state", "main")["busy"]:
            raise LabError("A run is already active")
        target = self.root / "candidates" / candidate_id
        if target.exists():
            raise LabError(f"Candidate path already exists: {candidate_id}")
        target.parent.mkdir(exist_ok=True)
        fingerprint = snapshot(source, target)
        candidate = {
            "id": candidate_id,
            "hypothesis": hypothesis,
            "digest": fingerprint,
            "path": str(target.relative_to(self.root)),
            "registered_at": now(),
        }
        with self.db:
            self.put("candidate", candidate_id, candidate)
        return candidate

    def lesson(self, lesson_id, candidate_id, statement, evidence_runs):
        identifier(lesson_id)
        self.verify(candidate_id)
        if not statement.strip() or not evidence_runs:
            raise LabError("A lesson needs a statement and development evidence")
        state = self.get("state", "main")
        if state["validation_used"] or state["busy"]:
            raise LabError("Freeze lessons before validation and outside active runs")
        for run_id in evidence_runs:
            run = self.get("run", run_id)
            if run["phase"] != "development" or run["status"] != "complete":
                raise LabError("Lessons require completed development runs")
            self.verify_evidence(run)
        if state["current"] is None:
            raise LabError("Establish a development baseline first")
        value = {
            "id": lesson_id,
            "candidate": candidate_id,
            "statement": statement,
            "evidence_runs": sorted(set(evidence_runs)),
            "created_at": now(),
            "scope": self.contract["question"],
            "status": "proposed",
        }
        with self.db:
            self.put("lesson", lesson_id, value)
        return value

    def reserve(self, run_id, phase, payload):
        identifier(run_id)
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            state = self.get("state", "main")
            if state["busy"]:
                raise LabError(f"Run {state['busy']} is active. Recover only after it has stopped")
            if state["validation_used"]:
                raise LabError("Validation was consumed. Start a new study with fresh tasks")
            run = {
                "id": run_id,
                "phase": phase,
                "status": "running",
                "started_at": now(),
                "original": state["original"],
                "current": state["current"],
                **payload,
            }
            self.put("run", run_id, run)
            state["busy"] = run_id
            if phase == "validation":
                state["validation_used"] = True
            self.put("state", "main", state, replace=True)
        return run

    def finish(self, run, *, promote=False):
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            state = self.get("state", "main")
            if state["busy"] != run["id"]:
                raise LabError("Run ownership changed. This result cannot change accepted state")
            run["finished_at"] = now()
            self.put("run", run["id"], run, replace=True)
            if promote:
                state["original"] = state["original"] or run["id"]
                state["current"] = run["id"]
            if run.get("lesson_verdict"):
                lesson = self.get("lesson", run["lesson"])
                self.put(
                    "lesson",
                    lesson["id"],
                    {**lesson, "status": run["lesson_verdict"], "validation_run": run["id"]},
                    replace=True,
                )
            state["busy"] = None
            self.put("state", "main", state, replace=True)

    def recover(self, run_id):
        run = self.get("run", run_id)
        if run["status"] != "running":
            raise LabError("Only an interrupted active run can be recovered")
        run.update(status="failed", error="Marked interrupted by the operator")
        self.finish(run)
        return run

    def verify_evidence(self, run):
        for samples in run.get("samples", {}).values():
            for sample in samples:
                folder = (self.root / sample["artifact"]).resolve()
                if not folder.is_relative_to(self.root):
                    raise LabError("Evidence path is outside the lab")
                for filename, expected in sample["digests"].items():
                    path = folder / filename
                    if (
                        not path.is_file()
                        or path.is_symlink()
                        or hashlib.sha256(path.read_bytes()).hexdigest() != expected
                    ):
                        raise LabError(f"Recorded evidence changed: {path}")

    def report(self):
        for candidate in self.all("candidate"):
            self.verify(candidate["id"])
        for run in self.all("run"):
            self.verify_evidence(run)
        return {
            "contract": self.get("contract", "main"),
            "state": self.get("state", "main"),
            "candidates": self.all("candidate"),
            "runs": self.all("run"),
            "lessons": self.all("lesson"),
        }
