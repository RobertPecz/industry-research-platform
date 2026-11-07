"""KSH dátumok visszakeresése az eltárolt szövegből; audit metaadatok mentése."""

import json
import re
from pathlib import Path

import yaml

from industry_research.db import connect

months = "január február március április május június július augusztus szeptember október november december".split()
with connect("data/research.sqlite") as db:
    for row in db.execute(
        "SELECT d.id,v.text FROM documents d JOIN versions v ON v.document_id=d.id WHERE d.source=?",
        ("KSH",),
    ).fetchall():
        match = re.search(r"Közzététel: (\d{4})\. (\w+) (\d{1,2})\.", row["text"])
        if match and match[2] in months:
            published = f"{match[1]}-{months.index(match[2]) + 1:02}-{int(match[3]):02}"
            db.execute(
                "UPDATE documents SET published=?, evidence_kind='official_statistics' WHERE id=?",
                (published, row["id"]),
            )
    for s in yaml.safe_load(Path("config/sources.yaml").read_text()):
        db.execute(
            "INSERT OR REPLACE INTO source_audits VALUES(?,?,?,?,?,?,?)",
            (
                s["name"],
                s["industry"],
                s["status"],
                s.get("terms_url"),
                s["checked_at"],
                s["decision"],
                json.dumps(s, ensure_ascii=False),
            ),
        )
