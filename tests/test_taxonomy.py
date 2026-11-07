import json

import pytest
import yaml

from industry_research.analysis import classify
from industry_research.db import connect, store
from industry_research.maintenance import review
from industry_research.taxonomy import load_taxonomy


def config(tmp_path, topics, industry="construction_hu"):
    path = tmp_path / "taxonomy.yaml"
    path.write_text(
        yaml.safe_dump(
            {"version": "1", "industry": industry, "topics": topics}, allow_unicode=True
        )
    )
    return path


def test_taxonomy_changes_keep_manual_labels(tmp_path):
    path = config(tmp_path, {"régi": ["munka"], "kézi": ["adat"]})
    with connect(str(tmp_path / "db")) as db:
        store(db, "https://example.org", "teszt", "Teszt", "Munka és adat")
        classify(db, path)
        evidence = db.execute("SELECT id FROM evidence WHERE topic='kézi'").fetchone()[
            0
        ]
        review(db, evidence, "verified", "Kézzel ellenőrzött", "javított")
        old_hash = load_taxonomy(path)["hash"]
        config(tmp_path, {"új": ["munka"], "kézi": ["adat"]})
        classify(db, path)
        classify(db, path)
        rows = db.execute("SELECT * FROM evidence ORDER BY topic").fetchall()
        assert {r["topic"] for r in rows} == {"javított", "új"}
        assert db.execute("SELECT COUNT(*) FROM reviews").fetchone()[0] == 1
        assert db.execute("SELECT COUNT(*) FROM taxonomies").fetchone()[0] == 2
        assert old_hash != load_taxonomy(path)["hash"]
        assert (
            json.loads(
                db.execute("SELECT config_json FROM taxonomies LIMIT 1").fetchone()[0]
            )["version"]
            == "1"
        )


def test_industry_scope(tmp_path):
    path = config(tmp_path, {"téma": ["munka"]}, "other")
    with connect(str(tmp_path / "db")) as db:
        store(db, "https://example.org", "teszt", "Teszt", "munka")
        classify(db, path)
        assert db.execute("SELECT COUNT(*) FROM evidence").fetchone()[0] == 0


@pytest.mark.parametrize(
    "topics", [{}, [], {"téma": []}, {"téma": [""]}, {"téma": [1]}, {"téma": "szó"}]
)
def test_invalid_taxonomy(tmp_path, topics):
    with pytest.raises(ValueError):
        load_taxonomy(config(tmp_path, topics))
