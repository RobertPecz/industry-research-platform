# Architektúra

CLI → forráskonfiguráció → jogosultság és robots → HTTPX → HTML/PDF kinyerés → SQLite verzió → szabályok → bizonyíték → Markdown.

- `db.py`: sémaverziózott migráció, tranzakciós tárolás, SHA-256 és FTS5.
- `collect.py`: soros lekérések, forrásszabályok, robots-cache, domainenkénti leállás 403/429/503 esetén. Átirányítást nem követ automatikusan.
- `analysis.py`: témakeresés és bizonyítékcentrikus riport. A témacímke nem üzleti igazolás.
- `scripts/`: reprodukálható pilot, rövid ellenőrzött parafrázis importja. A jegyzetek külön tárolási módot kapnak.

A dokumentum több témához kapcsolódhat, egy téma több dokumentumban megjelenhet. A kézi ellenőrzés előzménye külön táblában marad. A szerzői személyazonosságot nem következtetjük ki a szövegből.

- `maintenance.py`: auditált kézi címkézés, forráskövető export, előnézetes retenció.
- A riport és a `summary` az aktuális, nem elutasított bizonyítékokat összesíti, tartalomhash szerinti deduplikációval.

## Webes megjelenítés

`research serve` → loopback HTTP → csak olvasható SQLite-kapcsolat → JSON → böngésző.

A `web.py` a csomag `static/` könyvtárából szolgálja ki a HTML/CSS/JavaScript
felületet. Az összesítés a meglévő elemzőmodult használja; a dokumentumszöveget
csak a részletablak megnyitásakor kéri le. A webes végpontok nem módosítanak adatot.
A szerver indításakor a szokásos sémamigráció lefut. Minden lekérés külön,
lezárt adatbázis-kapcsolatot kap. A szerver csak loopback címen figyel, ellenőrzi
a Host fejlécet, és saját eredetre korlátozott CSP-t ad. A felület a forrástartalmat
szövegként jeleníti meg, a külső hivatkozásokat HTTP/HTTPS-re korlátozza.
Ez személyes, helyi megjelenítő; nyilvános üzemeltetésre nincs autentikációs rétege.

## Konfiguráció és opcionális feldolgozás

- `taxonomy.py`: típus- és méretellenőrzött YAML; a taxonómia tartalomhash-e bizonyítékhoz köthető.
- `experiences.py`: kurált kutatói jegyzetek idempotens importja, külön validációs naplóval.
- `gemini.py`: késleltetetten importált opcionális SDK, explicit engedélyek, auditált forráskiválasztás, soros és korlátozott hívások, darabonkénti cache és séma-/idézetellenőrzés.
- `start_app.py`: projektkörnyezet kiválasztása, szerverindítás és böngészőnyitás. VS Code launch/task konfiguráció a gyökérkönyvtárban.

A forrásgyűjtés és a modellfeldolgozás továbbra is külön lépés. A webapp csak az adatbázist olvassa; frissítésgombja sem indít külső kutatást vagy modellhívást.
