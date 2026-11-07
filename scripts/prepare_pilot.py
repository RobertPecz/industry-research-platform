from pathlib import Path

import yaml

sources = yaml.safe_load(Path("config/sources.yaml").read_text())
for source in sources:
    source["checked_at"] = "2026-11-07"
    source["industry"] = "construction_hu"
    source["decision"] = (
        "Nyilvános oldal megnyitva; újrafelhasználási és gépi gyűjtési engedély nem tisztázott."
    )
    source["status"] = "metadata_only"
    if source["name"] == "MMK":
        source["status"] = "blocked"
        source["decision"] = "Webes megnyitás HTTP 403; nincs megkerülés."
    if source["name"] == "KSH":
        source.update(
            status="allowed",
            max_chars=20000,
            license="CC BY 4.0",
            terms_url="https://www.ksh.hu/copyright",
            decision="Feltételek letöltve és elolvasva; robots.txt csak /apps/ tiltás. Forrásmegjelölés kötelező.",
        )
        source["urls"] = [
            f"https://www.ksh.hu/gyorstajekoztatok/epi/epi{year}{month:02}.html"
            for year in (24, 25)
            for month in range(1, 13)
        ]
Path("config/sources.yaml").write_text(
    yaml.safe_dump(sources, allow_unicode=True, sort_keys=False)
)
lines = [
    "# Forrásaudit – 2026-11-07",
    "",
    "A nyilvános elérhetőség nem jelent gyűjtési engedélyt. A metadata_only forrásokról a pipeline nem tölt le cikkeket.",
    "",
    "| Forrás | Döntés | Indok |",
    "|---|---|---|",
]
for s in sources:
    lines.append(
        f"| [{s['name']}]({s.get('terms_url', s['urls'][0])}) | {s['status']} | {s['decision']} |"
    )
lines += [
    "",
    "A KSH havi URL-ek kurált mintából képzett jelöltek. Csak sikeres HTTP-lekérés és tartalomellenőrzés után számítanak dokumentumnak. A 24 havi közlés egy intézménytől származik, nem 24 független panaszforrás.",
]
Path("docs/source_audit.md").write_text("\n".join(lines))
