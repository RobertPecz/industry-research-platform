"""Kézi ellenőrzés, forráskövető export és explicit adatmegőrzés."""

import json
import sqlite3
from datetime import datetime, timedelta, timezone

STATUSES = ("suggested", "source_checked", "verified", "rejected")
KINDS = (
    "unknown",
    "first_hand",
    "survey",
    "official_process",
    "official_statistics",
    "secondary_report",
    "hypothesis",
)
ACTORS = ("unknown", "contractor", "subcontractor", "designer", "customer")


def review(
    db: sqlite3.Connection,
    evidence_id: int,
    status: str,
    note: str,
    topic: str | None = None,
    kind: str | None = None,
    actor: str | None = None,
) -> None:
    if (
        status not in STATUSES
        or (kind is not None and kind not in KINDS)
        or (actor is not None and actor not in ACTORS)
    ):
        raise ValueError("Érvénytelen címke vagy állapot")
    if topic is not None and not topic.strip():
        raise ValueError("A téma nem lehet üres")
    with db:
        row = db.execute("SELECT * FROM evidence WHERE id=?", (evidence_id,)).fetchone()
        if row is None:
            raise ValueError("Nincs ilyen bizonyíték")
        old = {key: row[key] for key in ("status", "topic", "kind", "actor")}
        new = dict(old, status=status)
        new.update(
            {
                k: v
                for k, v in {"topic": topic, "kind": kind, "actor": actor}.items()
                if v is not None
            }
        )
        db.execute(
            "INSERT INTO reviews(evidence_id,old_status,new_status,note,old_values,new_values) VALUES(?,?,?,?,?,?)",
            (
                evidence_id,
                old["status"],
                status,
                note,
                json.dumps(old, ensure_ascii=False),
                json.dumps(new, ensure_ascii=False),
            ),
        )
        db.execute(
            "UPDATE evidence SET status=?,topic=?,kind=?,actor=? WHERE id=?",
            (new["status"], new["topic"], new["kind"], new["actor"], evidence_id),
        )


def export_records(db: sqlite3.Connection) -> list[dict]:
    return [
        dict(row)
        for row in db.execute("""
        SELECT e.*, d.url, d.source, d.title, d.published, d.storage_mode,
               v.hash AS version_hash, v.created AS version_created
        FROM evidence e JOIN versions v ON v.id=e.version_id
        JOIN documents d ON d.id=v.document_id ORDER BY e.id
    """)
    ]


def retention(db: sqlite3.Connection, days: int, apply: bool = False) -> dict:
    if days < 1:
        raise ValueError("A megőrzési idő pozitív nap legyen")
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    # Keep a document if any version was created within the retention period.
    ids = [
        row[0]
        for row in db.execute(
            """SELECT d.id FROM documents d
        WHERE datetime(d.accessed)<datetime(?) AND NOT EXISTS
        (SELECT 1 FROM versions v WHERE v.document_id=d.id AND datetime(v.created)>=datetime(?))""",
            (cutoff, cutoff),
        )
    ]
    attempts = db.execute(
        "SELECT COUNT(*) FROM attempts WHERE datetime(created)<datetime(?)", (cutoff,)
    ).fetchone()[0]
    if apply:
        with db:
            db.executemany("DELETE FROM documents WHERE id=?", [(i,) for i in ids])
            db.execute(
                "DELETE FROM attempts WHERE datetime(created)<datetime(?)", (cutoff,)
            )
    return {
        "applied": apply,
        "cutoff": cutoff,
        "document_ids": ids,
        "attempts": attempts,
    }
