import json
from contextlib import closing

import pytest

from industry_research.analysis import classify
from industry_research.db import connect, store
from industry_research.web import read_database, response_for


def test_viewer_reads_real_data_and_details(tmp_path):
    path = str(tmp_path / "test.sqlite")
    with closing(connect(path)) as db:
        store(
            db,
            "https://example.org/a",
            "Teszt",
            "Árvíztűrő <script>",
            "Építőipari adminisztráció és alvállalkozó.",
        )
        classify(db)
    status, content_type, body = response_for("/api/data", path)
    data = json.loads(body)
    assert status == 200
    assert "application/json" in content_type
    assert data["summary"]["documents"] == 1
    assert len(data["evidence"]) == 2
    assert data["documents"][0]["title"] == "Árvíztűrő <script>"
    assert "text" not in data["documents"][0]
    status, _, body = response_for("/api/documents/1", path)
    assert status == 200
    assert json.loads(body)["text"].startswith("Építőipari")
    assert response_for("/api/documents/999", path)[0] == 404
    assert response_for("/api/documents/1 OR 1=1", path)[0] == 404
    assert response_for("/../pyproject.toml", path)[0] == 404
    assert "https://example.org/a" in response_for("/api/report", path)[2].decode()
    assert (
        json.loads(response_for("/api/export", path)[2])[0]["url"]
        == "https://example.org/a"
    )


def test_empty_database_and_read_only_connection(tmp_path):
    path = str(tmp_path / "empty.sqlite")
    with closing(connect(path)):
        pass
    data = json.loads(response_for("/api/data", path)[2])
    assert data["documents"] == []
    assert data["summary"]["documents"] == 0
    with closing(read_database(path)) as db:
        import sqlite3

        with pytest.raises(sqlite3.OperationalError):
            db.execute("DELETE FROM documents")


@pytest.mark.parametrize(
    "path,content_type",
    [("/", "text/html"), ("/app.js", "text/javascript"), ("/app.css", "text/css")],
)
def test_packaged_assets(path, content_type):
    status, kind, body = response_for(path, "/does/not/exist")
    assert status == 200
    assert kind.startswith(content_type)
    assert len(body) > 100
