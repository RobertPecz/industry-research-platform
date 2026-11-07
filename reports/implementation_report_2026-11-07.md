# Fejlesztési és használati riport – 2026-11-07

## Elkészült eredmény

A meglévő webapphoz VS Code-ból indítható belépő készült. A szabályalapú témák konfigurációba kerültek. Hat új kutatási jelölt ellenőrzését dokumentáltuk, közülük két rövid, forrásszinten ellenőrzött kutatói jegyzet bekerült az adatbázisba. Elkészült az opcionális Gemini-feldolgozás, offline tesztekkel; élő generálást nem indítottunk.

Az eszközfelmérés külön fájlban: [AI-eszközök és saját kutatási skill feladata](../docs/ai_tools_research.md). A saját skill még nincs elkészítve, ahogy a felmérésben szereplő külső csomagok integrációja sem történt meg.

## 1. Indítás VS Code-ból

Fájlok: `start_app.py`, `.vscode/launch.json`, `.vscode/tasks.json`.

**Használat:** nyisd meg a `start_app.py` fájlt, és kattints a Run Python File háromszögre. A VS Code Python bővítménye kell hozzá. A Run and Debug nézetben a „Kutatóműhely indítása” konfiguráció is választható; ehhez Python Debugger szükséges. Bővítményfüggetlen alternatíva a mellékelt alapértelmezett build task, `Ctrl+Shift+B`.

A script a projekt saját `.venv` Pythonját használja, a repository gyökerét állítja munkakönyvtárnak, elindítja a szervert és megnyitja az alapértelmezett böngészőt. Leállítás: `Ctrl+C` vagy debug futásnál Stop. A böngészőlap bezárása önmagában nem állítja le a szervert.

```bash
.venv/bin/python start_app.py
.venv/bin/python start_app.py --port 8766
.venv/bin/python start_app.py --no-browser
```

Alap URL: `http://127.0.0.1:8765`. Foglalt vagy nem megnyitható portnál érthető üzenet jelenik meg. Nincs háttérben telepítés, gyűjtés vagy modellhívás. Ha a böngésző automatikus indítását az asztali környezet blokkolja, a terminálban kiírt URL kézzel megnyitható.

**Ellenőrzés:** az indítóval ténylegesen elindult a szerver `--no-browser` módban; a böngészős teszt ezen a szerveren futott. A VS Code grafikus gombját ebben a környezetben nem nyomtuk meg; a launch/task fájlokat és a más munkakönyvtárból történő indítást teszt ellenőrzi.

## 2. Konfigurálható taxonómia

Fájlok: `config/taxonomy.yaml`, `src/industry_research/taxonomy.py`, a módosított `analysis.py` és CLI.

Kilenc alap téma: adminisztráció, koordináció, pénzügy, e-napló, ajánlatadás, anyagbeszerzés, változáskezelés, átadás és munkaszervezés. A konfiguráció szöveges verziót és iparágat is megad.

```bash
uv run research taxonomy-check
uv run research classify
uv run research classify --taxonomy config/taxonomy.yaml
```

**Miért:** új kulcsszóhoz vagy témához már nem kell Python-kódot módosítani. A teljes konfiguráció és hash-e eltárolódik, így a gépi találat eredete visszakövethető. A kézzel ellenőrzött/átnevezett és hipotézishez kapcsolt rekordokat az újrafuttatás megőrzi; az ellenőrizetlen szabálytalálatokat az aktuális konfigurációhoz igazítja.

Ez determinisztikus, részszöveges keresés, nem magyar szótövezés vagy automatikus üzleti validáció. A paraméterek és korlátok részletesen: [taxonómia útmutató](../docs/taxonomy.md).

## 3. Saját tapasztalatok ellenőrzése

Fájlok: `config/validated_experiences.json`, `experiences.py`, kiegészített kutatási napló, riport és webes megjelenítés.

| Eredmény | Darab |
|---|---:|
| Célzottan vizsgált új jelölt | 6 |
| Tartalmában ellenőrzött, saját tapasztalatot leíró beszámoló | 2 |
| Megnyitott, de nem közvetlen beszámolóként elfogadott oldal | 1 |
| Sikertelen teljes megnyitás | 3 |
| Függetlenül validált vállalkozói eset | 0 |

Az [ELBA-interjú](https://elba.hu/blog/interju-egy-aktiv-elba-felhasznalo-kivitelezovel-emecz-viktorral/) ajánlatból kimaradó tételek tapasztalatát írja le. Az [iKont-interjú](https://ikont.hu/interju-juhasz-sandor-peterrel-az-ikont-ugyvezetojevel-es-tarsalapitojaval/) a feladategyeztetés és helyszíni végrehajtás közötti eltérésről számol be. Mindkettő terméket népszerűsítő közegben jelent meg, ezért az értékesítési érdeket és a független mérés hiányát feltüntettük.

Rövid parafrázisokat mentettünk, nem teljes cikkeket. Tárolás: `research_note`; bizonyítéktípus: `first_hand`; állapot: `source_checked`. A `verified` állapotot nem osztottuk ki. A publikálás ismeretlen maradt, nem helyettesítettük a hozzáférés dátumával.

```bash
uv run research import-experiences
uv run research report reports/pilot_report.md
uv run research summary
```

A jegyzetimport offline, megismételhető. A webappban az **Adatok frissítése** után a két dokumentum és a bizonyítékok láthatók. A forrásnézetben megjelent az ellenőrzési napló; a bizonyítékkártyák és dokumentumrészletek mutatják a korlátokat.

**A hiány továbbra is valós:** az öt függetlenül ellenőrzött tapasztalat célja nem teljesült. Ehhez eredeti dokumentumminták, folyamatmegfigyelés vagy közvetlen interjú kellene. Külső személynek nem küldtünk üzenetet.

## 4. Opcionális Gemini-integráció

Fájlok: `gemini.py`, `config/gemini.yaml`, CLI, opcionális `google-genai` függőség és lockfájl, `tests/test_gemini.py`.

**Miért:** külön, újraindítható feldolgozási lépésben készüljenek strukturált problémajelöltek, miközben a gyűjtés, a kézi munka és a webapp API nélkül is használható.

Telepítés: `uv sync --locked --extra gemini`. A jelen környezetben a hivatalos SDK 1.75.0 verziója került telepítésre. A modell a konfigurációban cserélhető; automatikus modell- vagy szolgáltatóváltás nincs.

A bekapcsoláshoz kulcs, konkrét dokumentumazonosító és három explicit kapcsoló kell. A Free Tier státuszt az API-projektben ellenőrizned kell; a program nem tudja azt a kulcsból bizonyítani. A dokumentum továbbíthatóságát is ellenőrizni kell.

```bash
uv run --extra gemini research analyze --backend gemini_free \
  --document 1 --allow-external-llm --confirm-free-tier --confirm-public-data
```

A kulcs biztonságos megadása és a teljes használati sorrend: [Gemini útmutató](../docs/gemini_usage.md). Az alap `research analyze` továbbra is csak szabályalapú.

A megvalósítás tartalmazza:

- Modell-elérhetőség ellenőrzése, soros kéréskezelés és futásonkénti kéréskeret.
- Darabolás, forráshelyek és sikeres darabok tartós cache-e.
- 503/egyéb átmeneti szerverhiba korlátozott retryja; 429 és hálózati hiba halasztása.
- JSON-mezők, kategóriák és a pontos bizonyító idézet ellenőrzése.
- Modell/metaadat, kérésstátusz, ismert tokenszám és idő naplózása, titkok nélkül.
- Több problémajelölt egy dokumentumból; kézi címkék megőrzése.

**Élő Gemini-hívás nem történt.** Az `ai-status` jelenleg üres. A fejlesztés nem indított fizetős vagy ingyenes generálási kérést; tényleges AI-pontosságot, válaszidőt vagy API-projektkvótát ezért nem állítunk mért eredménynek.

## 5. Adatbázis és kutatási állapot

A 4. migráció hozzáadja a taxonómiakonfigurációkat, a validációs naplót, a feldolgozási darabokat és API-próbákat. Migráció előtt mentés készült: `data/before-extension-v4.sqlite`. Ez helyi, gitignore alatti biztonsági másolat; érzékeny dokumentum későbbi törlésekor a mentéseket is külön kezelni kell.

Aktuális adatállapot:

- 27 dokumentum/jegyzet: 24 eredeti forrásszöveg és 3 kutatói jegyzet.
- 4 felhasznált forrás; a korábbi gyűjtési auditban 10 forrás szerepel.
- 2 forrásszinten ellenőrzött saját tapasztalat, 0 függetlenül validált eset.
- 2 ismeretlen publikációs dátum.
- Korábbi gyűjtési próbák összesen: 24 `stored`, 28 `blocked`, 24 `error`. Ezek több korábbi futás naplói, nem ennyi egyedi dokumentum és nem a mostani hat webes ellenőrzés számai.

A gépi összesítés: [database_summary.json](database_summary.json). A friss kutatási riport: [pilot_report.md](pilot_report.md).

## 6. Tényleges ellenőrzések

- **53 pytest teszt sikeres.** Adatbázis, migráció, gyűjtés, kézi előzmények, retenció, webes API, taxonómia, jegyzetimport, launcher és Gemini.
- Ruff lint és formázás ellenőrzése sikeres; mypy 10 forrásmodult hiba nélkül ellenőriz.
- JavaScript szintaxisellenőrzés sikeres.
- Böngészős ellenőrzés sikeres: navigáció, keresés, szűrés, részletablak, letöltés, csak olvasó HTTP-viselkedés, mobilnézet, hibajelzés és újratöltés.
- Gemini: mock szolgáltatóval és a valódi SDK mock HTTP-transportjával ellenőrzött; a tesztek nem hívnak külső modellt.
- A CI az opcionális SDK-t is telepíti, hogy a transportteszt se maradjon ki. Alaptelepítésben ez az egy SDK-specifikus teszt kihagyható, a többi offline marad.

## Következő prioritások

1. A saját kutatási skill elkészítése és az ellenőrzési munkamenet kipróbálása.
2. További független vállalkozói tapasztalatok, elsődleges dokumentumminták és kézzel annotált magyar értékelési minta.
3. Kifejezetten engedélyezett, kis elemszámú Gemini-próba megfelelő projekttel; csak utána pontosság- és költség-összehasonlítás a később kiválasztott eszközökkel.
