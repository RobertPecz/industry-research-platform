"""Loopback-only, read-only research viewer."""

import json
import sqlite3
from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import cast
from urllib.parse import urlsplit

from .analysis import report, summary
from .db import connect
from .maintenance import export_records

STATIC = Path(__file__).with_name("static")


def read_database(path: str) -> sqlite3.Connection:
    db = sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA query_only=ON")
    return db


def snapshot(db: sqlite3.Connection) -> dict:
    documents = [
        dict(row)
        for row in db.execute("""
        SELECT d.*, v.id AS version_id, length(v.text) AS characters,
        (SELECT COUNT(*) FROM evidence e WHERE e.version_id=v.id) AS evidence_count
        FROM documents d LEFT JOIN versions v ON v.id=(
            SELECT MAX(v2.id) FROM versions v2 WHERE v2.document_id=d.id)
        ORDER BY d.published DESC,d.id DESC
    """)
    ]
    return {
        "summary": summary(db),
        "documents": documents,
        "evidence": [
            dict(row)
            for row in db.execute("""
            SELECT e.*,d.url,d.title,d.source,d.storage_mode,d.id AS document_id,sv.limitations,sv.locator
            FROM evidence e JOIN versions v ON v.id=e.version_id
            JOIN documents d ON d.id=v.document_id
            LEFT JOIN source_validations sv ON sv.url=d.url
            WHERE v.id=(SELECT MAX(v2.id) FROM versions v2 WHERE v2.document_id=d.id)
            ORDER BY e.id
        """)
        ],
        "validations": [
            dict(row)
            for row in db.execute("SELECT * FROM source_validations ORDER BY url")
        ],
        "sources": [
            dict(row)
            for row in db.execute(
                "SELECT name,status,terms_url,checked_at,decision FROM source_audits ORDER BY name"
            )
        ],
        "hypotheses": [
            dict(row)
            for row in db.execute("""
            SELECT h.*,e.topic,e.status,d.url FROM hypotheses h
            JOIN evidence e ON e.id=h.evidence_id JOIN versions v ON v.id=e.version_id
            JOIN documents d ON d.id=v.document_id
            WHERE e.status!='rejected' AND v.id=(SELECT MAX(v2.id) FROM versions v2 WHERE v2.document_id=d.id)
        """)
        ],
    }


def response_for(path: str, database: str) -> tuple[int, str, bytes]:
    assets = {
        "/": ("index.html", "text/html"),
        "/app.css": ("app.css", "text/css"),
        "/app.js": ("app.js", "text/javascript"),
    }
    if path in assets:
        filename, content_type = assets[path]
        return 200, content_type + "; charset=utf-8", (STATIC / filename).read_bytes()
    result: dict | list
    with closing(read_database(database)) as db:
        if path == "/api/data":
            result = snapshot(db)
        elif path == "/api/export":
            result = export_records(db)
        elif path == "/api/report":
            return 200, "text/markdown; charset=utf-8", report(db).encode()
        elif (
            path.startswith("/api/documents/")
            and path.removeprefix("/api/documents/").isdigit()
        ):
            row = db.execute(
                """SELECT d.*,v.text,v.hash,v.created AS version_created,sv.limitations,sv.locator
                FROM documents d JOIN versions v ON v.document_id=d.id
                LEFT JOIN source_validations sv ON sv.url=d.url
                WHERE d.id=? ORDER BY v.id DESC LIMIT 1""",
                (int(path.rsplit("/", 1)[1]),),
            ).fetchone()
            if row is None:
                return 404, "application/json", b'{"error":"Not found"}'
            result = dict(row)
        else:
            return 404, "application/json", b'{"error":"Not found"}'
    return (
        200,
        "application/json; charset=utf-8",
        json.dumps(result, ensure_ascii=False).encode(),
    )


def make_server(database: str, port: int) -> ThreadingHTTPServer:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if self.headers.get("Host") not in {
                f"127.0.0.1:{cast(ThreadingHTTPServer, self.server).server_port}",
                f"localhost:{cast(ThreadingHTTPServer, self.server).server_port}",
            }:
                self.send_error(403)
                return
            try:
                status, content_type, body = response_for(
                    urlsplit(self.path).path, database
                )
            except (sqlite3.Error, OSError):
                status, content_type, body = (
                    500,
                    "application/json",
                    b'{"error":"Database unavailable"}',
                )
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'",
            )
            if urlsplit(self.path).path in {"/api/export", "/api/report"}:
                filename = (
                    "evidence.json"
                    if self.path.startswith("/api/export")
                    else "pilot_report.md"
                )
                self.send_header(
                    "Content-Disposition", f'attachment; filename="{filename}"'
                )
            self.end_headers()
            self.wfile.write(body)

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def serve(database: str, port: int = 8765) -> None:
    with closing(connect(database)):
        pass
    with make_server(database, port) as server:
        print(f"Kutatóműhely: http://127.0.0.1:{server.server_port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
