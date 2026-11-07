# Iparági kutatóplatform

Python 3.12+, SQLite és CLI alapú, bizonyítékcentrikus kutatási pilot.
A témacímke javaslat; üzleti következtetéshez külön validáció szükséges.

Telepítés: `uv sync --locked`. Inicializálás: `uv run research init`.
Más adatbázis: `uv run research --db /tmp/proba.sqlite init`.

## Egykattintásos indítás VS Code-ból

Nyisd meg a gyökérkönyvtárban a `start_app.py` fájlt, majd kattints a jobb felső
**Run Python File** háromszögre. Ehhez a VS Code Python bővítménye szükséges.
A script kiválasztja a projekt `.venv` környezetét, elindítja a webappot és
megnyitja az alapértelmezett böngészőt. Más munkakönyvtárból indítva is működik.

Alternatívák: a **Run and Debug → Kutatóműhely indítása → ▶** beállítás/F5
(Python Debugger bővítménnyel), vagy **Ctrl+Shift+B** a mellékelt VS Code taskkal.
Leállítás: a terminálban `Ctrl+C`, debug futásnál Stop. Párhuzamos második
indítás foglalt port esetén érthető hibával leáll, nem állít le más folyamatot.

```bash
.venv/bin/python start_app.py
.venv/bin/python start_app.py --port 8766
.venv/bin/python start_app.py --no-browser
```

Első telepítéskor továbbra is `uv sync --locked` szükséges. Az indító nem telepít
függőséget, nem gyűjt adatot, nem indít AI-hívást.

## Webes megjelenítő

**[Részletes webes használati útmutató – minden nézet és funkció](docs/webapp_user_guide.md)**

```bash
uv run research serve
```

Nyisd meg: **http://127.0.0.1:8765**. Leállítás: `Ctrl+C`.
Más port vagy adatbázis: `uv run research --db data/research.sqlite serve --port 8766`.

A magyar nyelvű Kutatóműhely felület tartalmazza:

- Áttekintés: dokumentumok, bizonyítékok, hipotézisek és forráslefedettség.
- Dokumentumtár: keresés címben, forrásban, dátumban és URL-ben; forrásszűrés;
  a mentett szöveg, dátum és verzióhash külön részletablakban.
- Bizonyítékok: keresés témában és részletben, állapotszűrés, forráshivatkozások.
- Forrásjegyzék: gyűjtési döntések és felhasználási feltételek.
- Markdown-riport és forráskövető JSON-export letöltése.

Az **Adatok frissítése** gomb újraolvassa az adatbázist; nem indít gyűjtést.
A felület csak olvas, a címkézés továbbra is a CLI-n érhető el. Kizárólag a saját
számítógépen figyelő szerver indul, külső betűtípus és új futásidejű függőség nélkül.
A mobilnézet és a billentyűzetes navigáció is támogatott.

## Használat

```bash
uv run research collect --limit 30
uv run research classify
uv run research analyze
uv run research search 'alvállalkoz*'
uv run research sources
uv run research problems
uv run research review 1 --status verified --topic 'Adminisztráció' --kind survey --actor contractor --note 'Forrás alapján ellenőrizve'
uv run research review 1 --status rejected --note 'Nem igazolja az állítást'
uv run research export --format json
uv run research export --format csv
uv run research summary
uv run research report reports/pilot_report.md
uv run research retention --days 365
uv run research retention --days 365 --apply
uv run research delete 1
```

A `review` bizonyítékazonosítót, a `delete` dokumentumazonosítót vár.
A kézi módosítás előző és új értékei megmaradnak; az újraosztályozás tiszteletben tartja őket.
Az export URL-t, forrást és verzióhash-t is tartalmaz. Az összesítés a legfrissebb
verziók nem elutasított bizonyítékait számolja; az azonos tartalom nem növeli a mintát.

A retenció alapból csak előnézet. A `--apply` törli azokat a dokumentumokat,
amelyek hozzáférési dátuma és minden verziója régebbi a megadott időnél, valamint
a régi gyűjtési naplókat. A dokumentumtörlés a kapcsolódó bizonyítékot, kézi
előzményt, hipotézist és keresési indexet is törli. Automatikus ütemezés nincs.

## Források és reprodukció

A `config/sources.yaml` auditált gyűjtési döntéseket tartalmaz. Csak `allowed`
forrásból történhet automatikus letöltés, robots.txt-ellenőrzéssel és legalább
két másodperces várakozással. Nincs automatikus átirányítás.
A tartalomhash jelzi a változatlan és más URL-en ismétlődő szöveget.
Az FTS5 kezeli az ékezeteket, magyar szótövezést nem végez.

A meglévő pilot reprodukciója a jóváhagyott források elérhetőségétől függ:

```bash
uv run python scripts/run_pilot.py
uv run python scripts/import_notes.py
uv run python scripts/enrich_pilot.py
uv run research import-experiences
uv run research classify
uv run research report reports/pilot_report.md
uv run research summary > reports/database_summary.json
```

A jelenlegi adatbázisban 24 forrásszöveg és 3 elkülönített kutatói jegyzet van,
4 forrásból. Tíz forrás auditja szerepel a konfigurációban. Két saját tapasztalatot leíró beszámoló forrásszinten ellenőrzött, de függetlenül
validált vállalkozói eset nincs; a minta nem reprezentatív.
A `collection_summary.json` a korábbi gyűjtési futás eredménye;
a `database_summary.json` az adatbázis teljes, több futást tartalmazó állapota.

## Ellenőrzés és fennmaradó feladatok

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```

A GitHub Actions ugyanezeket futtatja, külső adatforrás nélkül.
A 4. sémamigráció automatikus; megőrzi a forrásdokumentumokat és a kézi adatokat.

## Taxonómia, kutatási jegyzetek és Gemini

```bash
uv run research taxonomy-check
uv run research classify --taxonomy config/taxonomy.yaml
uv run research import-experiences
uv run research ai-status
```

A [taxonómia útmutatója](docs/taxonomy.md) leírja a témák módosítását és a kézi címkék védelmét.
A [kutatási napló](docs/research_followup.md) tartalmazza a hat új jelölt ellenőrzési eredményét.
A [Gemini útmutatója](docs/gemini_usage.md) ismerteti az opcionális telepítést, az explicit
bekapcsolást, dokumentumkiválasztást és a költség-/adatellenőrzési feltételeket.
A modellhívás alapértelmezésben kikapcsolt, a webapp használatához nem szükséges.

Az [AI-eszközök felmérésében](docs/ai_tools_research.md) külön kiemelt további feladat
a saját kutatási skill elkészítése. A felsorolt új eszközök nincsenek integrálva.
A most elkészült fejlesztések [részletes átadási riportja](reports/implementation_report_2026-11-07.md)
külön összefoglalja a változásokat, használatot és ellenőrzéseket.

A `tests/test_web.py` offline ellenőrzi a webes adatszerződést, a részletnézetet,
a letöltéseket és az olvasási kapcsolatot. A meglévő pilothoz a
`scripts/check_web.cjs` böngészős ellenőrzés is használható futó 8765-ös szerverrel;
Playwright telepítést igényel, a modul útvonala `PLAYWRIGHT_MODULE`-lal adható meg.
