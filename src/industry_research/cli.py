import argparse
import csv
import json
import sys
from pathlib import Path

import yaml

from .analysis import classify, report
from .collect import collect
from .db import connect
from .maintenance import ACTORS, KINDS, STATUSES, export_records, retention, review


def main() -> None:
    parser = argparse.ArgumentParser(description="Iparági kutatási pilot")
    parser.add_argument("--db", default="data/research.sqlite")
    parser.add_argument(
        "command",
        choices=[
            "init",
            "collect",
            "classify",
            "search",
            "report",
            "review",
            "delete",
            "export",
            "analyze",
            "sources",
            "problems",
            "retention",
            "summary",
            "serve",
            "taxonomy-check",
            "import-experiences",
            "ai-status",
        ],
    )
    parser.add_argument("value", nargs="?", default="")
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--status", choices=STATUSES, default="verified")
    parser.add_argument("--note", default="CLI kézi ellenőrzés")
    parser.add_argument("--topic")
    parser.add_argument("--kind", choices=KINDS)
    parser.add_argument("--actor", choices=ACTORS)
    parser.add_argument("--format", choices=["json", "csv"], default="json")
    parser.add_argument("--days", type=int, default=365)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--taxonomy", default="config/taxonomy.yaml")
    parser.add_argument("--backend", choices=["none", "gemini_free"], default="none")
    parser.add_argument("--gemini-config", default="config/gemini.yaml")
    parser.add_argument("--document", type=int, action="append", default=[])
    parser.add_argument("--allow-external-llm", action="store_true")
    parser.add_argument("--confirm-free-tier", action="store_true")
    parser.add_argument("--confirm-public-data", action="store_true")
    args = parser.parse_args()
    if args.backend != "none" and args.command != "analyze":
        parser.error("A Gemini-backend csak az analyze paranccsal használható")
    if args.command == "taxonomy-check":
        from .taxonomy import load_taxonomy

        try:
            config = load_taxonomy(args.taxonomy)
        except ValueError as exc:
            parser.error(str(exc))
        print(
            json.dumps(
                {k: config[k] for k in ("version", "industry", "hash", "topics")},
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    if not 1 <= args.port <= 65535:
        parser.error("A port 1 és 65535 közötti legyen")
    if args.command == "serve":
        from .web import serve

        serve(args.db, args.port)
        return
    if args.command in {"review", "delete"} and (
        not args.value.isdigit() or int(args.value) < 1
    ):
        parser.error("Pozitív rekordazonosító szükséges")
    if args.days < 1 or args.limit < 1:
        parser.error("A napok és a limit értéke pozitív legyen")
    with connect(args.db) as db:
        if args.command in {"analyze", "classify"}:
            try:
                if args.backend == "none":
                    classify(db, args.taxonomy)
                    print("Szabályalapú feldolgozás kész.")
                else:
                    from .gemini import analyze, load_config

                    if len(args.document) > args.limit:
                        parser.error(
                            "A kiválasztott dokumentumok száma nagyobb a limitnél"
                        )
                    result = analyze(
                        db,
                        load_config(args.gemini_config),
                        args.document,
                        allow_external=args.allow_external_llm,
                        confirm_free_tier=args.confirm_free_tier,
                        confirm_public_data=args.confirm_public_data,
                    )
                    print(json.dumps(result, ensure_ascii=False))
                    if result["status"] != "success":
                        raise SystemExit(1)
            except ValueError as exc:
                parser.error(str(exc))
        elif args.command == "import-experiences":
            from .experiences import import_experiences

            try:
                print(
                    json.dumps(
                        import_experiences(
                            db, args.value or "config/validated_experiences.json"
                        ),
                        ensure_ascii=False,
                    )
                )
            except (ValueError, OSError) as exc:
                parser.error(str(exc))
        elif args.command == "ai-status":
            print(
                json.dumps(
                    [
                        dict(r)
                        for r in db.execute(
                            "SELECT model,operation,status,COUNT(*) requests,SUM(input_tokens) input_tokens,SUM(output_tokens) output_tokens,SUM(total_tokens) total_tokens FROM ai_attempts GROUP BY model,operation,status"
                        )
                    ],
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.command == "sources":
            print(
                json.dumps(
                    [dict(row) for row in db.execute("SELECT * FROM source_audits")],
                    ensure_ascii=False,
                )
            )
        elif args.command == "problems":
            print(
                json.dumps(
                    [dict(row) for row in db.execute("SELECT * FROM evidence")],
                    ensure_ascii=False,
                )
            )
        elif args.command == "collect":
            print(
                json.dumps(
                    collect(
                        db,
                        yaml.safe_load(Path("config/sources.yaml").read_text()),
                        args.limit,
                    )
                )
            )
        elif args.command == "search":
            print(
                [
                    dict(row)
                    for row in db.execute(
                        "SELECT * FROM search_index WHERE search_index MATCH ?",
                        (args.value,),
                    )
                ]
            )
        elif args.command == "report":
            Path(args.value or "reports/pilot_report.md").write_text(report(db))
        elif args.command == "review":
            try:
                review(
                    db,
                    int(args.value),
                    args.status,
                    args.note,
                    args.topic,
                    args.kind,
                    args.actor,
                )
            except ValueError as exc:
                parser.error(str(exc))
        elif args.command == "retention":
            print(json.dumps(retention(db, args.days, args.apply), ensure_ascii=False))
        elif args.command == "summary":
            from .analysis import summary

            print(json.dumps(summary(db), ensure_ascii=False, indent=2))
        elif args.command == "delete":
            db.execute(
                "DELETE FROM search_index WHERE version_id IN (SELECT id FROM versions WHERE document_id=?)",
                (int(args.value),),
            )
            db.execute("DELETE FROM documents WHERE id=?", (int(args.value),))
        elif args.command == "export":
            rows = export_records(db)
            if args.format == "json":
                print(json.dumps(rows, ensure_ascii=False))
            elif rows:
                writer = csv.DictWriter(sys.stdout, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
