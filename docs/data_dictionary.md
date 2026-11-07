# Adatszótár

- `documents`: egyedi URL, intézményi forrás, cím, publikálás (ismeretlen esetben NULL), hozzáférés, iparág, tárolási mód (`source_text`/`research_note`), bizonyítékjellege.
- `versions`: dokumentumhoz kötött normalizált szöveg, SHA-256, létrehozás; egyedi dokumentum–hash pár.
- `evidence`: verzió, téma, pontos részlet vagy jelölt parafrázis, módszer, státusz (`suggested`, `source_checked`, `verified`, `rejected`), szereplő és bizonyítéktípus. A source_checked gépi kutatás során visszaellenőrzött forrást, nem felhasználói validációt jelent.
- `attempts`: minden megkísérelt URL státusza, hibája és ideje. `blocked` szabályzat miatti kihagyást is jelent, nem feltétlenül HTTP-tiltást.
- `source_audits`: megnyitott források döntése és konfigurációja.
- `reviews`: kézi állapot- és címkeváltozás előzménye, indoklás, időpont; `old_values` és `new_values` JSON-pillanatkép a témáról, státuszról, szereplőről és bizonyítéktípusról.
- `hypotheses`: bizonyítékhoz kötött automatizálási irány, adatigény, kockázat, validáció; az üzleti hatás alapértéke unknown.
- `search_index`: FTS5, magyar ékezetek kezelése; szótövezés nincs.

A `PRAGMA user_version` szerinti 1–4. migráció a csomag db.py moduljában van. A dokumentumtörlés kaszkádolja a verziót, bizonyítékot, előzményt és hipotézist; adatbázis-trigger törli az FTS-indexet is.

- `taxonomies`: a szabálykonfiguráció SHA-256 kulcsa, teljes JSON-ja és mentési ideje; az `evidence.taxonomy_hash` kapcsolja a találatot a konfigurációhoz.
- `source_validations`: URL, dokumentumkapcsolat (sikertelen ellenőrzésnél NULL), dátum, státusz, forráshely, korlátok és következő ellenőrzés. Állapot: `source_checked`, `unavailable`, `not_first_hand`.
- `ai_chunks`: dokumentumverzió, tartalomhash, modell, prompt- és sémaverzió, szövegkezdő és -végpozíció, állapot, validált JSON. A JSON modellelőrejelzéseket tartalmaz, nem kézi bizonyítékminősítést.
- `ai_attempts`: minden API-próba művelete, modellje, állapota, biztonságos hibakódja, ismert tokenhasználata és időtartama. A szöveges hívás a darabhoz kapcsolódik; a `models.get` ellenőrzésnél `chunk_id` NULL.

Dokumentumtörléskor a darabok, kapcsolt API-próbák és dokumentumhoz kötött validációs jegyzetek is törlődnek. A forrásszöveget nem tartalmazó modell-ellenőrzési naplók és a taxonómiakonfigurációk megmaradnak. Az előnézetes retenció továbbra is dokumentumokra és gyűjtési próbákra vonatkozik; a külön modell-ellenőrzési naplókhoz nincs automatikus retenció.
