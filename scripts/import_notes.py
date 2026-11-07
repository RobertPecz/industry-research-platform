"""Ellenőrzött, rövid kutatói jegyzetek; nem forrásszövegként importálva."""

import json
from pathlib import Path

from industry_research.db import connect, store

with connect("data/research.sqlite") as db:
    for note in json.loads(Path("config/research_notes.json").read_text()):
        store(db, note["url"], note["source"], note["title"], note["text"])
        doc = db.execute(
            "SELECT id FROM documents WHERE url=?", (note["url"],)
        ).fetchone()[0]
        db.execute(
            "UPDATE documents SET storage_mode='research_note',published=?,evidence_kind=?,accessed=? WHERE id=?",
            (note["published"], note["kind"], note["accessed"], doc),
        )
        version = db.execute(
            "SELECT MAX(id) FROM versions WHERE document_id=?", (doc,)
        ).fetchone()[0]
        for finding in note["findings"]:
            assert finding["excerpt"] in note["text"]
            db.execute(
                "INSERT OR IGNORE INTO evidence(version_id,topic,excerpt,method,status,kind,actor) VALUES(?,?,?,'curated-paraphrase-v1','source_checked','survey','contractor')",
                (version, finding["topic"], finding["excerpt"]),
            )
            evidence = db.execute(
                "SELECT id FROM evidence WHERE version_id=? AND topic=? AND method='curated-paraphrase-v1'",
                (version, finding["topic"]),
            ).fetchone()[0]
            if not db.execute(
                "SELECT 1 FROM hypotheses WHERE evidence_id=?", (evidence,)
            ).fetchone():
                db.execute(
                    "INSERT INTO hypotheses(evidence_id,description,inputs,risks,validation) VALUES(?,?,?,?,?)",
                    (
                        evidence,
                        finding["hypothesis"],
                        finding["inputs"],
                        finding["risks"],
                        finding["validation"],
                    ),
                )
