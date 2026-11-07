import json

import pytest

from industry_research.analysis import classify, summary
from industry_research.db import connect, store
from industry_research.maintenance import export_records, retention, review


def seed(db, url="https://example.org/a", text="Alvállalkozó adminisztráció"):
    store(db, url, "fixture", "Teszt", text)
    classify(db)


def test_review_history_survives_reclassification(tmp_path):
    with connect(str(tmp_path / "db")) as db:
        seed(db)
        before = db.execute("SELECT COUNT(*) FROM evidence").fetchone()[0]
        review(
            db,
            1,
            "verified",
            "Ellenőrzött fixture",
            "Kézi téma",
            "first_hand",
            "contractor",
        )
        classify(db)
        row = db.execute("SELECT * FROM evidence WHERE id=1").fetchone()
        assert (row["topic"], row["status"], row["actor"]) == (
            "Kézi téma",
            "verified",
            "contractor",
        )
        assert db.execute("SELECT COUNT(*) FROM evidence").fetchone()[0] == before
        history = db.execute("SELECT * FROM reviews").fetchone()
        assert json.loads(history["old_values"])["topic"] == "adminisztráció"
        assert json.loads(history["new_values"])["kind"] == "first_hand"
        assert summary(db)["verified_first_hand_versions"] == 1
        record = export_records(db)[0]
        assert record["url"] == "https://example.org/a"
        assert len(record["version_hash"]) == 64
        with pytest.raises(ValueError):
            review(db, 999, "verified", "")


def test_retention_preview_and_cascade(tmp_path):
    with connect(str(tmp_path / "db")) as db:
        seed(db)
        review(db, 1, "verified", "Teszt")
        db.execute("UPDATE documents SET accessed='2000-01-01'")
        db.execute("UPDATE versions SET created='2000-01-01'")
        db.execute("INSERT INTO hypotheses(evidence_id,description) VALUES(1,'Teszt')")
        db.execute(
            "INSERT INTO attempts(url,created) VALUES('https://example.org/a','2000-01-01')"
        )
        result = retention(db, 365)
        assert result["document_ids"] == [1]
        assert not result["applied"]
        assert db.execute("SELECT COUNT(*) FROM documents").fetchone()[0] == 1
        retention(db, 365, True)
        for table in (
            "documents",
            "versions",
            "evidence",
            "reviews",
            "hypotheses",
            "search_index",
            "attempts",
        ):
            assert db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0
        with pytest.raises(ValueError):
            retention(db, 0, True)


def test_retention_keeps_recent_versions(tmp_path):
    with connect(str(tmp_path / "db")) as db:
        seed(db)
        db.execute("UPDATE documents SET accessed='2000-01-01'")
        assert retention(db, 365, True)["document_ids"] == []


def test_summary_counts_content_once_and_ignores_old_and_rejected(tmp_path):
    with connect(str(tmp_path / "db")) as db:
        seed(db)
        seed(db, "https://example.org/b")
        assert all(row["contents"] == 1 for row in summary(db)["matrix"])
        seed(db, text="Új tartalom tématalálat nélkül")
        db.execute("UPDATE evidence SET status='rejected' WHERE version_id=2")
        assert summary(db)["matrix"] == []


def test_migration_from_previous_database(tmp_path):
    path = str(tmp_path / "db")
    import sqlite3

    from industry_research.db import MIGRATION_2, SCHEMA

    with sqlite3.connect(path) as db:
        db.executescript(SCHEMA)
        db.executescript(MIGRATION_2)
        db.execute(
            "INSERT INTO documents(url,source,title) VALUES('https://example.org','fixture','Teszt')"
        )
        db.execute("CREATE TABLE processing(id INTEGER PRIMARY KEY)")
    with connect(path) as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == 4
        assert (
            db.execute(
                "SELECT name FROM sqlite_master WHERE name='processing'"
            ).fetchone()
            is None
        )
        assert db.execute("SELECT COUNT(*) FROM documents").fetchone()[0] == 1
        db.execute("DELETE FROM documents")
        assert db.execute("SELECT COUNT(*) FROM search_index").fetchone()[0] == 0
