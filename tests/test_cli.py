import subprocess
from pathlib import Path

from industry_research.db import connect, store


def test_cli_smoke_and_deletion(tmp_path):
    path = tmp_path / "db"
    cli = str(Path(".venv/bin/research").absolute())
    subprocess.run([cli, "--db", str(path), "init"], check=True, capture_output=True)
    with connect(str(path)) as db:
        store(
            db, "https://example.org", "fixture", "Teszt", "Alvállalkozó adminisztráció"
        )
    subprocess.run(
        [cli, "--db", str(path), "analyze"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        [cli, "--db", str(path), "review", "1"], check=True, capture_output=True
    )
    with connect(str(path)) as db:
        assert db.execute("SELECT COUNT(*) FROM reviews").fetchone()[0] == 1
    subprocess.run(
        [cli, "--db", str(path), "delete", "1"], check=True, capture_output=True
    )
    with connect(str(path)) as db:
        for table in ("documents", "versions", "evidence", "search_index", "reviews"):
            assert db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0
