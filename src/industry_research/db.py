import hashlib
import sqlite3
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

SCHEMA = """
CREATE TABLE IF NOT EXISTS documents(id INTEGER PRIMARY KEY, url TEXT UNIQUE NOT NULL,
 source TEXT NOT NULL, title TEXT NOT NULL, published TEXT, accessed TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS versions(id INTEGER PRIMARY KEY, document_id INTEGER REFERENCES documents ON DELETE CASCADE,
 hash TEXT NOT NULL, text TEXT NOT NULL, created TEXT DEFAULT CURRENT_TIMESTAMP, UNIQUE(document_id,hash));
CREATE TABLE IF NOT EXISTS evidence(id INTEGER PRIMARY KEY, version_id INTEGER REFERENCES versions ON DELETE CASCADE,
 topic TEXT NOT NULL, excerpt TEXT NOT NULL, method TEXT NOT NULL, status TEXT DEFAULT 'suggested',
 kind TEXT DEFAULT 'unknown', actor TEXT DEFAULT 'unknown', UNIQUE(version_id,topic,method));
CREATE TABLE IF NOT EXISTS attempts(id INTEGER PRIMARY KEY,url TEXT,status TEXT,error TEXT,created TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE VIRTUAL TABLE IF NOT EXISTS search_index USING fts5(text,version_id UNINDEXED,tokenize='unicode61 remove_diacritics 2');
PRAGMA user_version=1;
"""


def connect(path: str) -> sqlite3.Connection:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    if db.execute("PRAGMA user_version").fetchone()[0] == 0:
        db.executescript(SCHEMA)
    if db.execute("PRAGMA user_version").fetchone()[0] < 2:
        db.executescript(MIGRATION_2)
    if db.execute("PRAGMA user_version").fetchone()[0] < 3:
        db.executescript(MIGRATION_3)
    if db.execute("PRAGMA user_version").fetchone()[0] < 4:
        db.executescript(MIGRATION_4)
    return db


def store(db: sqlite3.Connection, url: str, source: str, title: str, text: str) -> str:
    parts = urlsplit(url)
    url = urlunsplit(
        (parts.scheme.lower(), parts.netloc.lower(), parts.path, parts.query, "")
    )
    text = " ".join(text.split())
    if not text:
        raise ValueError("Üres tartalom")
    digest = hashlib.sha256(text.encode()).hexdigest()
    with db:
        db.execute(
            "INSERT OR IGNORE INTO documents(url,source,title) VALUES(?,?,?)",
            (url, source, title),
        )
        doc = db.execute("SELECT id FROM documents WHERE url=?", (url,)).fetchone()[0]
        if db.execute(
            "SELECT 1 FROM versions WHERE document_id=? AND hash=?", (doc, digest)
        ).fetchone():
            return "unchanged"
        duplicate = db.execute(
            "SELECT 1 FROM versions WHERE hash=?", (digest,)
        ).fetchone()
        cursor = db.execute(
            "INSERT INTO versions(document_id,hash,text) VALUES(?,?,?)",
            (doc, digest, text),
        )
        db.execute(
            "INSERT INTO search_index(text,version_id) VALUES(?,?)",
            (text, cursor.lastrowid),
        )
    return "duplicate" if duplicate else "stored"


MIGRATION_2 = """
BEGIN;
ALTER TABLE documents ADD COLUMN storage_mode TEXT NOT NULL DEFAULT 'source_text';
ALTER TABLE documents ADD COLUMN industry TEXT NOT NULL DEFAULT 'construction_hu';
ALTER TABLE documents ADD COLUMN evidence_kind TEXT NOT NULL DEFAULT 'unknown';
CREATE TABLE reviews(id INTEGER PRIMARY KEY, evidence_id INTEGER REFERENCES evidence ON DELETE CASCADE,
 old_status TEXT, new_status TEXT, note TEXT, created TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE source_audits(name TEXT PRIMARY KEY, industry TEXT, status TEXT, terms_url TEXT,
 checked_at TEXT, decision TEXT, config_json TEXT);
CREATE TABLE hypotheses(id INTEGER PRIMARY KEY, evidence_id INTEGER REFERENCES evidence ON DELETE CASCADE,
 description TEXT, inputs TEXT, risks TEXT, validation TEXT, impact TEXT DEFAULT 'unknown');
CREATE INDEX version_hash ON versions(hash);
PRAGMA user_version=2;
COMMIT;
"""


MIGRATION_3 = """
BEGIN;
DROP TABLE IF EXISTS processing;
ALTER TABLE reviews ADD COLUMN old_values TEXT;
ALTER TABLE reviews ADD COLUMN new_values TEXT;
CREATE TRIGGER delete_version_search AFTER DELETE ON versions BEGIN
 DELETE FROM search_index WHERE version_id=OLD.id;
END;
PRAGMA user_version=3;
COMMIT;
"""


MIGRATION_4 = """
BEGIN;
CREATE TABLE taxonomies(hash TEXT PRIMARY KEY, config_json TEXT NOT NULL, created TEXT DEFAULT CURRENT_TIMESTAMP);
ALTER TABLE evidence ADD COLUMN taxonomy_hash TEXT REFERENCES taxonomies(hash);
UPDATE evidence SET method='rules-v2' WHERE method='rules-v1';
CREATE TABLE source_validations(url TEXT PRIMARY KEY, document_id INTEGER REFERENCES documents ON DELETE CASCADE,
 checked_at TEXT NOT NULL, status TEXT NOT NULL, locator TEXT, limitations TEXT, next_step TEXT);
CREATE TABLE ai_chunks(id INTEGER PRIMARY KEY, version_id INTEGER NOT NULL REFERENCES versions ON DELETE CASCADE,
 content_hash TEXT NOT NULL, model TEXT NOT NULL, prompt_version TEXT NOT NULL, schema_version TEXT NOT NULL,
 chunk_start INTEGER NOT NULL, chunk_end INTEGER NOT NULL, status TEXT NOT NULL, result TEXT,
 updated TEXT DEFAULT CURRENT_TIMESTAMP,
 UNIQUE(version_id,model,prompt_version,schema_version,chunk_start));
CREATE TABLE ai_attempts(id INTEGER PRIMARY KEY, chunk_id INTEGER REFERENCES ai_chunks ON DELETE CASCADE,
 model TEXT NOT NULL, operation TEXT NOT NULL, status TEXT NOT NULL, error_code TEXT,
 input_tokens INTEGER, output_tokens INTEGER, total_tokens INTEGER, elapsed REAL,
 created TEXT DEFAULT CURRENT_TIMESTAMP);
PRAGMA user_version=4;
COMMIT;
"""
