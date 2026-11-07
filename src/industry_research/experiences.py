"""Import reviewed research notes without upgrading them to human verification."""

import json
from pathlib import Path

from .db import store


def import_experiences(db, path="config/validated_experiences.json") -> dict:
    notes = json.loads(Path(path).read_text(encoding="utf-8"))
    # Validate the complete file before changing records.
    for note in notes:
        if not isinstance(note, dict) or not all(
            isinstance(note.get(k), str) and note[k].strip()
            for k in (
                "url",
                "checked_at",
                "status",
                "locator",
                "limitations",
                "next_step",
            )
        ):
            raise ValueError("Hiányos validációs jegyzet")
        if note["status"] not in {"source_checked", "unavailable", "not_first_hand"}:
            raise ValueError("Érvénytelen validációs állapot")
        if note["status"] == "source_checked":
            if not all(
                isinstance(note.get(k), str) and note[k].strip()
                for k in ("source", "title", "text", "topic", "excerpt")
            ):
                raise ValueError("Hiányos forrásellenőrzött jegyzet")
            if note["excerpt"] not in note["text"]:
                raise ValueError("A részlet nincs a jegyzetben")
    counts = {"source_checked": 0, "unavailable": 0, "not_first_hand": 0}
    for note in notes:
        doc = None
        if note["status"] == "source_checked":
            store(db, note["url"], note["source"], note["title"], note["text"])
            doc = db.execute(
                "SELECT id FROM documents WHERE url=?", (note["url"],)
            ).fetchone()[0]
            with db:
                db.execute(
                    "UPDATE documents SET storage_mode='research_note',evidence_kind='first_hand',published=?,accessed=? WHERE id=?",
                    (note.get("published"), note["checked_at"], doc),
                )
                version = db.execute(
                    "SELECT MAX(id) FROM versions WHERE document_id=?", (doc,)
                ).fetchone()[0]
                db.execute(
                    """INSERT OR IGNORE INTO evidence(version_id,topic,excerpt,method,status,kind,actor)
                    VALUES(?,?,?,'curated-experience-v1','source_checked','first_hand','contractor')""",
                    (version, note["topic"], note["excerpt"]),
                )
        with db:
            db.execute(
                """INSERT INTO source_validations(url,document_id,checked_at,status,locator,limitations,next_step)
                VALUES(?,?,?,?,?,?,?) ON CONFLICT(url) DO UPDATE SET
                document_id=excluded.document_id,checked_at=excluded.checked_at,status=excluded.status,
                locator=excluded.locator,limitations=excluded.limitations,next_step=excluded.next_step""",
                (
                    note["url"],
                    doc,
                    note["checked_at"],
                    note["status"],
                    note["locator"],
                    note["limitations"],
                    note["next_step"],
                ),
            )
        counts[note["status"]] += 1
    return counts
