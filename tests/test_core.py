from industry_research.analysis import classify, report
from industry_research.collect import extract
from industry_research.db import connect, store


def test_versions_and_evidence(tmp_path):
    db = connect(str(tmp_path / "test.sqlite"))
    assert (
        store(
            db,
            "https://example.org/a",
            "teszt",
            "Teszt",
            "építőipar alvállalkozó adminisztráció",
        )
        == "stored"
    )
    assert (
        store(
            db,
            "https://example.org/a",
            "teszt",
            "Teszt",
            "építőipar alvállalkozó adminisztráció",
        )
        == "unchanged"
    )
    assert (
        store(
            db,
            "https://example.org/b",
            "teszt",
            "Teszt",
            "építőipar alvállalkozó adminisztráció",
        )
        == "duplicate"
    )
    assert (
        store(db, "https://example.org/a", "teszt", "Teszt", "kintlévőség") == "stored"
    )
    classify(db)
    classify(db)
    assert db.execute("SELECT count(*) FROM evidence").fetchone()[0] == 5
    assert (
        db.execute(
            "SELECT count(*) FROM search_index WHERE search_index MATCH 'alvállalkozó'"
        ).fetchone()[0]
        == 2
    )
    assert "https://example.org/a" in report(db)
    assert "ismeretlen" in report(db)


def test_extraction():
    assert extract(
        b"<html><title>T</title><main>adat</main><script>bad</script></html>",
        "text/html",
    ) == ("T", "adat")
