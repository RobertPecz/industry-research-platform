import json

from industry_research.analysis import summary
from industry_research.db import connect
from industry_research.experiences import import_experiences
from industry_research.maintenance import review


def test_experiences_are_audited_not_human_verified(tmp_path):
    path = tmp_path / "notes.json"
    note = {
        "url": "https://example.org/interview",
        "source": "Teszt",
        "title": "Teszt",
        "checked_at": "2026-11-07",
        "status": "source_checked",
        "published": None,
        "locator": "Második kérdés",
        "text": "Parafrázis: a munka elmaradt.",
        "topic": "koordináció",
        "excerpt": "a munka elmaradt.",
        "limitations": "Önbevallás",
        "next_step": "Interjú",
    }
    path.write_text(json.dumps([note]))
    with connect(str(tmp_path / "db")) as db:
        import_experiences(db, path)
        review(db, 1, "rejected", "Nem elég bizonyíték")
        import_experiences(db, path)
        assert db.execute("SELECT COUNT(*) FROM documents").fetchone()[0] == 1
        assert db.execute("SELECT COUNT(*) FROM source_validations").fetchone()[0] == 1
        assert db.execute("SELECT status FROM evidence").fetchone()[0] == "rejected"
        assert summary(db)["verified_first_hand_versions"] == 0
        db.execute("DELETE FROM documents")
        assert db.execute("SELECT COUNT(*) FROM source_validations").fetchone()[0] == 0
