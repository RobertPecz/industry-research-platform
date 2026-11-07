import json

from .taxonomy import load_taxonomy


def classify(db, taxonomy_path="config/taxonomy.yaml") -> None:
    config = load_taxonomy(taxonomy_path)
    reviewed = set()
    for r in db.execute(
        "SELECT e.version_id,e.topic,r.old_values FROM reviews r JOIN evidence e ON e.id=r.evidence_id"
    ):
        reviewed.add((r["version_id"], r["topic"]))
        if r["old_values"]:
            reviewed.add((r["version_id"], json.loads(r["old_values"])["topic"]))
    with db:
        db.execute(
            "INSERT OR IGNORE INTO taxonomies(hash,config_json) VALUES(?,?)",
            (config["hash"], config["serialized"]),
        )
        for row in db.execute(
            "SELECT v.* FROM versions v JOIN documents d ON d.id=v.document_id WHERE d.industry=?",
            (config["industry"],),
        ).fetchall():
            protected = {
                r[0]
                for r in db.execute(
                    """SELECT topic FROM evidence e WHERE version_id=? AND
                (status!='suggested' OR EXISTS(SELECT 1 FROM reviews r WHERE r.evidence_id=e.id)
                 OR EXISTS(SELECT 1 FROM hypotheses h WHERE h.evidence_id=e.id))""",
                    (row["id"],),
                )
            }
            matches = {}
            for topic, words in config["topics"].items():
                if (row["id"], topic) in reviewed or topic in protected:
                    continue
                for word in words:
                    start = row["text"].lower().find(word.lower())
                    if start >= 0:
                        matches[topic] = row["text"][max(0, start - 50) : start + 150]
                        break
            # Replace only unreviewed suggestions. Stable IDs survive unchanged topics.
            for old in db.execute(
                "SELECT id,topic FROM evidence WHERE version_id=? AND method='rules-v2'",
                (row["id"],),
            ).fetchall():
                if old["topic"] not in matches and old["topic"] not in protected:
                    db.execute("DELETE FROM evidence WHERE id=?", (old["id"],))
            for topic, excerpt in matches.items():
                db.execute(
                    """INSERT INTO evidence(version_id,topic,excerpt,method,taxonomy_hash)
                    VALUES(?,?,?,'rules-v2',?) ON CONFLICT(version_id,topic,method)
                    DO UPDATE SET excerpt=excluded.excerpt,taxonomy_hash=excluded.taxonomy_hash""",
                    (row["id"], topic, excerpt, config["hash"]),
                )


def report(db) -> str:
    docs = db.execute("SELECT * FROM documents ORDER BY id").fetchall()
    lines = [
        "# Magyar építőipari kutatási pilot",
        "",
        "## Minta és módszer",
        f"Nyilvántartott dokumentumok/jegyzetek: {len(docs)}.",
        "A forrásszöveg és a kutatói parafrázis külön tárolási mód. A havi KSH közlések ágazati háttéradatok, nem panaszok. Az ÉVOSZ jegyzete egy felmérésből származik. A minta nem reprezentatív; az általánosítás és az ROI nem igazolt.",
        "",
        "## Forráslefedettség",
    ]
    for row in db.execute(
        "SELECT source,storage_mode,COUNT(*) n FROM documents GROUP BY source,storage_mode"
    ):
        lines.append(f"- {row['source']}: {row['n']} ({row['storage_mode']}).")
    lines.append(
        f"Első kézből származó, ellenőrzött dokumentumverziók: {summary(db)['verified_first_hand_versions']}."
    )
    lines += [
        "",
        "## A minta témái és szereplői",
        "",
        "| Téma | Szereplő | Egyedi tartalmak | Ellenőrzött |",
        "|---|---|---:|---:|",
    ]
    for row in summary(db)["matrix"]:
        lines.append(
            f"| {row['topic']} | {row['actor']} | {row['contents']} | {row['verified']} |"
        )
    lines += [
        "",
        "A darabszámok kizárólag a gyűjtött mintára vonatkoznak; azonos tartalom több URL-en egyszer számít.",
        "",
        "## Problémák és bizonyítékjelöltek",
    ]
    for row in db.execute(
        "SELECT e.*,d.url,d.source,d.published,d.storage_mode FROM evidence e JOIN versions v ON v.id=e.version_id JOIN documents d ON d.id=v.document_id WHERE e.status!='rejected' AND v.id=(SELECT MAX(v2.id) FROM versions v2 WHERE v2.document_id=d.id)"
    ):
        lines.append(
            f"- E{row['id']} – **{row['topic']}**; {row['kind']}, {row['status']}, {row['method']}. Publikálás: {row['published'] or 'ismeretlen'}. [Forrás: {row['source']}]({row['url']})."
        )
        if row["storage_mode"] == "research_note":
            lines.append(f"  Kutatói parafrázis: {row['excerpt']}")
        else:
            lines.append(
                "  Automatikus tématalálat; önmagában nem igazol üzleti problémát. Az idézet az adatbázisban ellenőrizhető."
            )
    lines += ["", "## Interjúval validálandó automatizálási hipotézisek"]
    for row in db.execute(
        "SELECT h.*,d.url FROM hypotheses h JOIN evidence e ON e.id=h.evidence_id JOIN versions v ON v.id=e.version_id JOIN documents d ON d.id=v.document_id WHERE e.status!='rejected' AND v.id=(SELECT MAX(v2.id) FROM versions v2 WHERE v2.document_id=d.id)"
    ):
        lines += [
            f"- **H{row['id']}**: {row['description']} [Kiinduló bizonyíték E{row['evidence_id']}]({row['url']}).",
            f"  Adatigény: {row['inputs']} Kockázat: {row['risks']} Validáció: {row['validation']} Üzleti hatás: {row['impact']}.",
        ]
    lines += ["", "## Első kézből származó beszámolók ellenőrzése"]
    for row in db.execute("SELECT * FROM source_validations ORDER BY url"):
        lines.append(
            f"- [{row['status']}]({row['url']}); ellenőrzés: {row['checked_at']}. {row['limitations']} Következő lépés: {row['next_step']}"
        )
    lines += [
        "",
        "## Konkurencia és korlátok",
        "Az e-építési napló létező hivatalos dokumentációs rendszer, nem igazoltan azonos funkcionalitású versenytárs. [Hivatalos alkalmazásjegyzék](https://www.e-epites.hu/alkalmazasok). Kereskedelmi versenytársak összehasonlítása még nem készült.",
        "A KSH anyagai CC BY 4.0 licencűek; a kinyerés szöveges átalakítás. [Felhasználási feltételek](https://www.ksh.hu/copyright). A többi forrás automatikus gyűjtése nincs engedélyezve. A minta nem fedi le megfelelően a családiház-építőket és a szakipari alvállalkozókat.",
        "",
        "## Dokumentumjegyzék",
    ]
    for doc in docs:
        lines.append(
            f"- D{doc['id']}: [{doc['title']}]({doc['url']}); forrás: {doc['source']}; publikálás: {doc['published'] or 'ismeretlen'}; tárolás: {doc['storage_mode']}."
        )
    return "\n".join(lines)


def summary(db) -> dict:
    latest = """FROM evidence e JOIN versions v ON v.id=e.version_id
        JOIN documents d ON d.id=v.document_id
        WHERE e.status!='rejected' AND v.id=(SELECT MAX(v2.id) FROM versions v2 WHERE v2.document_id=d.id)"""
    return {
        "documents": db.execute("SELECT COUNT(*) FROM documents").fetchone()[0],
        "sources": db.execute(
            "SELECT COUNT(DISTINCT source) FROM documents"
        ).fetchone()[0],
        "missing_publication_dates": db.execute(
            "SELECT COUNT(*) FROM documents WHERE published IS NULL"
        ).fetchone()[0],
        "attempts": {
            r[0]: r[1]
            for r in db.execute("SELECT status,COUNT(*) FROM attempts GROUP BY status")
        },
        "source_audits": {
            r[0]: r[1]
            for r in db.execute(
                "SELECT status,COUNT(*) FROM source_audits GROUP BY status"
            )
        },
        "verified_first_hand_versions": db.execute(
            "SELECT COUNT(DISTINCT v.hash) "
            + latest
            + " AND e.kind='first_hand' AND e.status='verified'"
        ).fetchone()[0],
        "source_checked_first_hand_versions": db.execute(
            "SELECT COUNT(DISTINCT v.hash) "
            + latest
            + " AND e.kind='first_hand' AND e.status='source_checked'"
        ).fetchone()[0],
        "matrix": [
            dict(r)
            for r in db.execute(
                "SELECT e.topic,e.actor,COUNT(DISTINCT v.hash) contents,COUNT(DISTINCT CASE WHEN e.status='verified' THEN v.hash END) verified "
                + latest
                + " GROUP BY e.topic,e.actor ORDER BY e.topic,e.actor"
            )
        ],
    }
