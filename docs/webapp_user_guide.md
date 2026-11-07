# Kutatóműhely – részletes webes használati útmutató

A dokumentum a repository 2026-11-07-i megvalósítását írja le. A funkciókat a felület és a kiszolgáló kódjával összevetve dokumentáltuk. A példákban szereplő elemszámok és azonosítók az adatbázis bővülésével változhatnak.

A Kutatóműhely az építőipari kutatás mentett dokumentumainak, bizonyítékainak, hipotéziseinek és forrásellenőrzéseinek áttekintésére szolgál. A weboldal **olvasási felület**: böngészni, keresni, szűrni, forrást megnyitni és exportálni lehet. A gyűjtés, címkézés, törlés és Gemini-feldolgozás külön parancssori művelet.

## Tartalomjegyzék

1. [Gyors kezdés](#1-gyors-kezdés)
2. [Indítás, cím és leállítás](#2-indítás-cím-és-leállítás)
3. [Navigáció és közös kezelőszervek](#3-navigáció-és-közös-kezelőszervek)
4. [Áttekintés](#4-áttekintés)
5. [Dokumentumtár](#5-dokumentumtár)
6. [Dokumentumrészletek](#6-dokumentumrészletek)
7. [Bizonyítékok](#7-bizonyítékok)
8. [Forrásjegyzék](#8-forrásjegyzék)
9. [Riport és export](#9-riport-és-export)
10. [Frissítés és az adatok aktualitása](#10-frissítés-és-az-adatok-aktualitása)
11. [Javasolt munkamenetek](#11-javasolt-munkamenetek)
12. [Billentyűzet és keskeny képernyő](#12-billentyűzet-és-keskeny-képernyő)
13. [A weboldalon kívüli műveletek](#13-a-weboldalon-kívüli-műveletek)
14. [Hibakeresés](#14-hibakeresés)
15. [Fogalmak és értelmezési korlátok](#15-fogalmak-és-értelmezési-korlátok)
16. [Teljes funkciólista](#16-teljes-funkciólista)

## 1. Gyors kezdés

1. Nyisd meg a repository mappáját VS Code-ban.
2. Nyisd meg a gyökérkönyvtárban a [`start_app.py`](../start_app.py) fájlt.
3. Kattints a **Run Python File ▶** gombra. A VS Code Python bővítménye szükséges hozzá.
4. A böngészőben megnyílik a `http://127.0.0.1:8765` cím. Ha nem nyílik meg automatikusan, másold a címet a böngésző címsorába.
5. Az **Áttekintés** oldalon nézd meg a minta méretét és korlátait.
6. A **Dokumentumtárban** kattints egy dokumentum címére a mentett szöveg megtekintéséhez.
7. A **Bizonyítékok** oldalon keresd meg a téged érdeklő témát, és ellenőrizd a részletet, állapotot és eredeti forrást.
8. A **Riport letöltése** gombbal mentsd le az összefoglalót.

A webapp használatához nincs szükség Gemini-kulcsra. A megnyitás és böngészés nem indít adatgyűjtést vagy modellhívást.

## 2. Indítás, cím és leállítás

### 2.1. Első telepítés

Ha a projekt már működik, ezt nem kell minden indításkor megismételni. Új környezetben Python 3.12 vagy újabb és `uv` szükséges. A projekt gyökerében:

```bash
uv sync --locked
```

Ez létrehozza/frissíti a projekt Python-környezetét. A webapp indítása inicializálja a szükséges adatbázissémát, de **nem tölti fel automatikusan kutatási adatokkal**. Üres adatbázissal üres nézeteket kapsz.

### 2.2. VS Code-indítási lehetőségek

| Módszer | Lépések | Feltétel |
|---|---|---|
| Python-fájl futtatása | `start_app.py` megnyitása → **Run Python File ▶** | VS Code Python bővítmény |
| Run and Debug | **Run and Debug** → **Kutatóműhely indítása** → **▶**, vagy F5 | Python Debugger bővítmény |
| Projektfeladat | **Ctrl+Shift+B** | A mellékelt `.vscode/tasks.json`; elkészült `.venv` |
| Terminál | Az alábbi indítóparancs | Elkészült `.venv` |

```bash
.venv/bin/python start_app.py
```

Az indító a projekt mappájára vált, és a projekt `.venv` Python-környezetét használja. A böngészőt is megpróbálja megnyitni. A terminált hagyd nyitva, mert ott fut a kiszolgáló.

### 2.3. Másik port vagy böngészőnyitás nélküli indítás

```bash
.venv/bin/python start_app.py --port 8766
.venv/bin/python start_app.py --no-browser
```

Az első parancshoz a `http://127.0.0.1:8766` cím tartozik. A másodiknál kézzel nyisd meg az alapértelmezett címet.

A CLI is elindíthatja a webappot, automatikus böngészőnyitás nélkül:

```bash
uv run research serve
```

Másik adatbázis és port kiválasztása:

```bash
uv run research --db data/masik-kutatas.sqlite serve --port 8766
```

Ez valóban másik adatbázist nyit meg. Ha az adott fájl még nem létezik, új, üres adatbázis készül. A `start_app.py` ezzel szemben a projekt `data/research.sqlite` fájlját használja.

### 2.4. Leállítás

- A kiszolgáló termináljában nyomj **Ctrl+C**-t.
- Debug futásnál használd a VS Code **Stop** gombját.
- A böngészőlap bezárása önmagában nem állítja le a kiszolgálót.
- Újraindítás után az adatbázis megmarad; a keresőmezők pillanatnyi tartalma nem.

A `127.0.0.1` a saját számítógépedet jelenti. A jelenlegi szerver kizárólag erről a gépről érhető el. A cím továbbküldésével másik ember vagy a telefonod nem kap hozzáférést a számítógépeden futó apphoz.

## 3. Navigáció és közös kezelőszervek

### 3.1. A négy fő nézet

| Menü | Feladat | Közvetlen cím az alapporton |
|---|---|---|
| **Áttekintés** | Számlálók, legfrissebb dokumentumok, hipotézisek, mintakorlátok | `http://127.0.0.1:8765/#overview` |
| **Dokumentumtár** | Mentett dokumentumok és jegyzetek keresése | `http://127.0.0.1:8765/#documents` |
| **Bizonyítékok** | Problémajelöltek, részletek és ellenőrzési állapotok | `http://127.0.0.1:8765/#evidence` |
| **Forrásjegyzék** | Tapasztalatellenőrzési napló és gyűjtési döntések | `http://127.0.0.1:8765/#sources` |

A kiválasztott menüpont kiemelést kap. A felső sávban is megjelenik az aktuális nézet neve. A **Kutatóműhely** logóra kattintva az Áttekintéshez térsz vissza.

A böngésző Vissza/Előre gombja a nézetváltások között használható. A keresés és szűrés nem kerül a címbe: a nézet könyvjelzőzhető, az aktuális szűrt találati lista nem.

### 3.2. Közös gombok

- **↻ Adatok frissítése:** újraolvassa a mentett adatokat. Részletek a [10. fejezetben](#10-frissítés-és-az-adatok-aktualitása).
- **↓ Riport letöltése:** az egész kutatás aktuális Markdown-riportját tölti le, bármelyik nézetből.
- **Forrás megnyitása ↗:** az eredeti külső oldalra vezet, új böngészőlapon. Ehhez az oldalnak elérhetőnek kell lennie, és általában internetkapcsolat szükséges.

A bal oldali **Saját adatbázis** felirat tájékoztató jelzés, nem kattintható adatbázisválasztó és nem folyamatos állapotellenőrző. Az adatbázis kiválasztása indításkor történik.

## 4. Áttekintés

Az Áttekintés célja, hogy lásd, mekkora és milyen minőségű mintából dolgozol, és hová érdemes továbblépni.

### 4.1. A négy felső számláló

| Számláló | Mit számol? | Hogyan értelmezd? |
|---|---|---|
| **Dokumentumok** | Az adatbázis dokumentumrekordjait, beleértve a kutatói jegyzeteket | Nem kizárólag eredeti cikkek száma; azonos tartalom külön URL-en külön dokumentum lehet |
| **Felhasznált források** | A mentett dokumentumok különböző forrásneveit | Nem az összes megvizsgált weboldal vagy az auditált források száma; a rendszer forrásnév szerint számol |
| **Bizonyítékjelöltek** | A legfrissebb dokumentumverziókhoz tartozó, nem elutasított bizonyítékrekordokat | Egy dokumentum több bizonyítékot is adhat; a kézzel validált rekordok is beleszámítanak |
| **Első kézből validált** | A `first_hand` típusú és `verified` állapotú bizonyítékokhoz tartozó egyedi tartalmakat | Tartalomhash szerint deduplikált érték; a `source_checked` állapot önmagában nem növeli |

A „Kézzel validált” állapotot emberi döntés állítja be. A rendszer nem végez külön külső személyazonosság- vagy tényellenőrzést, ezért a számláló megbízhatósága a felülvizsgálat minőségétől függ.

### 4.2. Legfrissebb dokumentumok

Legfeljebb öt dokumentumot mutat, publikálási dátum szerint csökkenő sorrendben. Az ismeretlen publikálási dátumú rekordok a dátummal rendelkezők után szerepelnek. Azonos dátumnál a nagyobb dokumentumazonosító kerül előre.

- Kattints a **címre** a dokumentumrészletekhez.
- Kattints az **Összes megtekintése →** linkre a teljes Dokumentumtárhoz.
- A „legfrissebb” itt a publikálás szerinti sorrendet jelenti, nem a legutóbb importált öt rekordot.

### 4.3. Vizsgálandó hipotézisek

Egy hipotéziskártya tartalma:

- **H-azonosító**, például `H1`;
- a vizsgálandó automatizálási lehetőség;
- a javasolt validálási lépés;
- az üzleti hatás ismert értéke vagy **Ismeretlen** jelölése;
- hivatkozás a kiinduló bizonyíték eredeti forrására.

Az **E… – kiinduló bizonyíték ↗** link a külső forrást nyitja meg, nem a Bizonyítékok nézetet szűri. A hipotézis vizsgálandó lehetőség, nem igazolt megtakarítás vagy kész ajánlás. Csak aktuális, nem elutasított bizonyítékhoz kapcsolt hipotézis látható.

### 4.4. „A minta még nem a teljes kép.”

Ez a panel a kutatás korlátaira figyelmeztet. Külön mutatja a tartalmukban ellenőrzött saját beszámolókat és a kézzel validált esetektől való eltérésüket.

Ha egyszerre látsz nulla validált esetet és két ellenőrzött beszámolót, az nem számlálási hiba: az utóbbiaknál az eredeti közlést ellenőriztük, de nem történt független esemény- vagy eredményigazolás.

### 4.5. Témák a mintában

A sorok a témákhoz és szereplőtípusokhoz tartozó egyedi dokumentumtartalmak számát mutatják. Azonos szöveg több URL-en ebben az összesítésben nem növeli ugyanannak a csoportnak a darabszámát.

- Egy dokumentum több témában is megjelenhet, ezért a számokat ne add össze dokumentumszámként.
- A sávhossz az aktuális legnagyobb csoporthoz viszonyít; nem ágazati százalék.
- A jelenlegi felület csak a témanevet írja ki, a szereplőt nem. Emiatt ugyanaz a témanév több sorban is szerepelhet. A szereplő szerinti bontást a letöltött riport táblázata mutatja meg.
- Elutasított bizonyíték nem vesz részt ebben az összesítésben.

### 4.6. Források hozzáférése

A gyűjtési auditban szereplő források számát összesíti állapotonként. A **Részletek →** link a Forrásjegyzékhez vezet. A panel alján az ismeretlen publikálási dátumú dokumentumok száma látható.

## 5. Dokumentumtár

### 5.1. Keresés

1. Válaszd a **Dokumentumtár** menüpontot.
2. Gépelj a **Keresés** mezőbe.
3. A lista azonnal frissül; nem kell Entert nyomni.
4. A találatszám a kereső és a táblázat között jelenik meg.

A kereső ezekben keres:

| Mező | Példa |
|---|---|
| Dokumentum címe | `ajánlat` |
| Forrás neve | `KSH` |
| Tárolt publikálási dátum | `2025-` |
| Eredeti forrás URL-je | `ksh.hu` |

**A teljes dokumentumszövegben ez a kereső nem keres.** Egy kizárólag a szövegben szereplő mondatra itt nem feltétlenül kapsz találatot.

A keresés kis- és nagybetűtől, valamint ékezetektől független: például az `epitoipar` és az `építőipar` ugyanúgy kereshető. Egyszerű, egybefüggő részszövegegyezést használ. Nincs külön `AND`/`OR`, idézőjeles kifejezéskezelés, csillagos helyettesítés vagy szótövezés. Ne írj `*`-ot a keresés végére; a szó elejének beírása önmagában elegendő részszövegkereséshez.

A szóközök a beírt szöveg részei. Ha váratlanul nincs találat, töröld a kezdő/végi szóközt, vagy keress rövidebb kifejezésre.

### 5.2. Forrásszűrő

A **Forrás** legördülőben válassz egy forrásnevet. A listában a ténylegesen mentett dokumentumok forrásai szerepelnek, nem az összes auditált jelölt.

A keresés és a forrásszűrő együtt érvényesül. Például `KSH` forrás és `2025-` keresés esetén a KSH 2025-ös publikálási dátumot tartalmazó rekordjait látod.

A teljes listához töröld a keresőmezőt és válaszd az **Összes** lehetőséget. Nézetváltás vagy sikeres adatfrissítés után a keresés és szűrés alaphelyzetbe áll.

### 5.3. A táblázat mezői

| Mező | Jelentés |
|---|---|
| **Dokumentum** | Kattintható cím; a mentett részletablakot nyitja |
| `D…` | Dokumentumazonosító; nem bizonyítékazonosító |
| `… karakter` | A legfrissebb mentett szövegváltozat hossza |
| `… bizonyíték` | A legfrissebb verzióhoz tartozó bizonyítékok száma, az elutasítottakat is beleértve |
| **Forrás** | A dokumentum tárolt forrásneve |
| **Publikálás** | Publikálási dátum, vagy **Ismeretlen** |
| **Típus** | **Forrásszöveg** vagy **Kutatói jegyzet** |

A nulla bizonyíték nem feltétlenül hibát jelent. Lehet, hogy a dokumentumban nincs a kutatás szempontjából releváns probléma, vagy még nem történt osztályozás.

A lista publikálási dátum szerint rendezett. A fejlécekre kattintva jelenleg nem lehet sorrendet váltani. Nincs lapozás; a szűrés az egész betöltött dokumentumlistán működik.

## 6. Dokumentumrészletek

A részletablak két helyről nyitható meg:

- az Áttekintés vagy Dokumentumtár dokumentumcímére kattintva;
- egy bizonyítékkártyán a **… · dokumentum →** gombbal.

Az ablakban a következők szerepelnek:

1. Cím.
2. Forrás, publikálási dátum és tárolási típus.
3. **Forrás megnyitása ↗** hivatkozás az élő külső oldalra.
4. Tájékoztató arról, hogy tárolt forrásszöveg vagy kutatói jegyzet következik.
5. Ha rögzítve van: **Ellenőrzési korlát** és **Forráshely**.
6. A teljes **eltárolt** szöveg.
7. **Verzió:** a szöveg tartalomhash-e.
8. **Mentve:** az adott szövegváltozat mentési ideje.

Az eltárolt szöveg nem feltétlenül az eredeti weboldal teljes tartalma: a gyűjtés vagy a kutatási módszer kivonatot is tárolhat. A kutatói jegyzet saját összefoglaló, nem az eredeti cikk másolata.

A verzióazonosító a szövegváltozat azonosítására való; nem minőségi pontszám. A „Mentve” nem a cikk publikálási dátuma.

**Bezárás:** kattints a jobb felső **✕** gombra, vagy nyomj **Esc**-et. Az ablakon kívüli kattintásra ne számíts bezárási módként. Hosszú dokumentumnál az ablak tartalma görgethető. A szöveg kijelölhető és a szokásos módon másolható; külön másolásgomb nincs.

Mindig a dokumentum legfrissebb mentett változatát mutatja. Korábbi változatok között ezen az ablakon belül nem lehet váltani.

## 7. Bizonyítékok

### 7.1. A bizonyítékkártya olvasása

| Elem | Mire szolgál? |
|---|---|
| **E-azonosító**, például `E2` | A bizonyíték egyedi azonosítása |
| Állapotcímke | Az ellenőrzés aktuális szintje |
| Téma | A kapcsolódó problémakategória |
| Bizonyítéktípus és szereplő | Milyen jellegű forrás, illetve kinek a nézőpontja szerepel |
| Szövegrészlet | Az állításhoz kapcsolt tárolt részlet |
| Parafrázis-/idézetjelölés | Segít elkülöníteni a kutatói összefoglalót az eredeti szövegtől |
| **Forrásellenőrzés** | Rögzített korlátok, például marketingérdekeltség vagy hiányzó mérés |
| **… · dokumentum →** | A saját adatbázisban lévő dokumentum megnyitása |
| **Forrás megnyitása ↗** | Az eredeti külső oldal megnyitása |

A részlet vizuális idézetformázása önmagában nem jelenti, hogy szó szerinti idézet. Mindig olvasd el az alatta lévő jelölést: **„Kutatói parafrázis, nem szó szerinti forrásidézet.”** esetén kutatói összefoglalót látsz.

### 7.2. Ellenőrzési állapotok

| Felirat | Belső azonosító | Jelentés |
|---|---|---|
| **Ellenőrzésre vár** | `suggested` | Automatikus vagy még nem validált javaslat |
| **Forrás ellenőrizve** | `source_checked` | A közlés tartalmát visszaellenőriztük; az esemény vagy eredmény ettől még nem függetlenül igazolt |
| **Kézzel validált** | `verified` | Emberi felülvizsgálat után így minősített rekord |
| **Elutasítva** | `rejected` | A bizonyítékot elutasították; megmarad visszakereshető rekordként |

Az **Összes** nézet az aktuális verziók elutasított bizonyítékait is mutatja. Emiatt több kártyát láthatsz, mint amennyit az Áttekintés **Bizonyítékjelöltek** számlálója jelez.

### 7.3. Bizonyítéktípusok

| Felirat | Mit jelent? |
|---|---|
| **Első kézből** | Saját tapasztalatként közölt beszámoló; nem automatikus hitelességi garancia |
| **Felmérés** | Több szereplő válaszait összegző kutatás |
| **Hivatalos folyamat** | Hivatalos eljárás vagy folyamat leírása |
| **Hivatalos statisztika** | Ágazati háttéradat; önmagában nem vállalkozói panasz |
| **Másodlagos forrás** | Mások tapasztalatáról vagy eredményéről szóló közlés |
| **Hipotézis** | Ellenőrizendő feltevés |
| **Ismeretlen** | Nincs elég adat a besoroláshoz |

Szereplőként **Kivitelező**, **Alvállalkozó**, **Tervező**, **Megrendelő** vagy **Ismeretlen** jelenhet meg.

Gemini-feldolgozás után a témában angol kategóriaazonosítók is megjelenhetnek, például `finance` vagy `coordination`. A felület ezeket jelenleg nem fordítja automatikusan magyar taxonómiacímkére. A modell javasolt szereplője és bizonyítéktípusa nem válik automatikusan ellenőrzött besorolássá.

### 7.4. Keresés és szűrés

A **Keresés** mező a téma, a bizonyítékrészlet, a forrásnév és a kapcsolódó dokumentum címe alapján szűr. Nem keres a teljes dokumentumszövegben, a validációs korlát leírásában, az E-azonosítóban vagy a forrás URL-jében.

Az ékezet- és kis-/nagybetű-kezelés ugyanaz, mint a Dokumentumtárban. A találatok gépelés közben frissülnek.

Az **Ellenőrzési állapot** legördülővel választhatsz állapotot. Csak azok az állapotok szerepelnek a listában, amelyekhez az aktuálisan betöltött bizonyítékok között van rekord. Ha nincs „Kézzel validált” opció, az nem feltétlenül hiba: lehet, hogy még nincs ilyen bizonyíték.

A keresés és az állapotszűrő együtt érvényesül. Alaphelyzet: üres kereső és **Összes** állapot. Téma-, szereplő- vagy bizonyítéktípus szerinti külön legördülő nincs.

### 7.5. Teljes export

A **↓ Teljes export** gomb az `evidence.json` fájlt tölti le. **Nem az éppen szűrt kártyákat exportálja**, hanem az adatbázis összes bizonyítékrekordját. További részletek a [9. fejezetben](#9-riport-és-export).

## 8. Forrásjegyzék

A nézet két eltérő célú részből áll. Egy forrás közlésének ellenőrzése nem ugyanaz, mint az automatikus gyűjtésének engedélyezése.

### 8.1. Tapasztalatok ellenőrzési naplója

Minden bejegyzés megmutatja az ellenőrzés állapotát, dátumát, korlátait, a következő javasolt lépést és az eredeti forrás linkjét.

| Állapot | Jelentés |
|---|---|
| **Forrás ellenőrizve** | A közlés hozzáférhető volt és a rögzített beszámolót ellenőriztük |
| **Nem elérhető** | Az ellenőrzéskor a teljes oldal megnyitása sikertelen volt |
| **Nem közvetlen beszámoló** | A vizsgált oldal nem került elfogadásra közvetlen saját tapasztalatként |

A sikertelen vagy elutasított jelöltnek nem feltétlenül van dokumentumrekordja. Ezért a napló elemszáma eltérhet az importált új dokumentumok számától.

A „Következő lépés” javaslat, nem elindítható feladatgomb. A forráslink megnyitása sem írja át automatikusan az ellenőrzés dátumát vagy állapotát.

### 8.2. Auditált források

| Oszlop | Tartalom |
|---|---|
| **Forrás** | A vizsgált forrás neve |
| **Gyűjtés** | Az automatizált adatgyűjtés rögzített státusza |
| **Ellenőrizve** | A forrásaudit időpontja |
| **Döntés és feltételek** | A státusz indoklása és – ha van – a felhasználási feltételek linkje |

A gyűjtési állapotok:

- **Gyűjthető (`allowed`):** a rögzített feltételekkel engedélyezett forrás. A tényleges gyűjtéskor további technikai ellenőrzések is történnek.
- **Csak metaadat (`metadata_only`):** a forrásról metaadat rögzíthető; a státusz nem ad automatikus tartalomgyűjtési engedélyt.
- **Tiltott (`blocked`):** a gyűjtés blokkolt. A pontos indok a döntésben olvasható; lehet hozzáférési akadály is.
- **Kézi vizsgálat (`manual_review`):** a döntéshez még kézi ellenőrzés szükséges.

A táblázat forrásnév szerint rendezett. Jelenleg nincs hozzá saját kereső vagy állapotszűrő. Hosszabb listánál a böngésző **Ctrl+F** keresése használható a látható oldalon.

Az audit dátuma nem azonos egy most végzett élő rendelkezésreállási teszttel. Az oldal megnyitása nem ellenőrzi újra automatikusan a forrásokat.

## 9. Riport és export

### 9.1. Markdown-riport

Bármely nézetben kattints a **↓ Riport letöltése** gombra. A böngésző `pilot_report.md` néven kínálja fel a fájlt; ismételt letöltéskor a böngésző sorszámot is fűzhet a nevéhez.

A riport tartalmazza:

- a minta és a módszer összefoglalását;
- a forráslefedettséget;
- a témák és szereplők szerinti táblázatot;
- az aktuális, nem elutasított bizonyítékokat;
- az azokhoz kapcsolt hipotéziseket;
- a saját beszámolók ellenőrzési naplóját;
- a kutatási korlátokat és a dokumentumjegyzéket.

A riport **az egész adatbázisról szól**, nem az aktuális keresésről. A kattintáskor az adatbázisból készül; nem a repository `reports/pilot_report.md` fájljának változatlan másolata. A böngészős letöltés nem írja felül ezt a repositoryban lévő fájlt.

Megnyitás VS Code-ban: nyisd meg a letöltött `.md` fájlt, és használd a Markdown előnézetet, például **Ctrl+Shift+V**-vel. A forráslinkek a riportban is megmaradnak. Nincs külön webes PDF-, Word- vagy Excel-riportgomb.

A módszertani bevezető a magyar építőipari pilothoz írt szöveget is tartalmaz; nem minden mondata automatikusan levezetett adat. Új kutatási területre használva ezt külön át kell nézni.

### 9.2. JSON-export

A **Bizonyítékok → ↓ Teljes export** gomb `evidence.json` fájlt készít.

| Adatcsoport | Jellemző mezők |
|---|---|
| Azonosítás | `id`, `version_id` |
| Bizonyíték | `topic`, `excerpt`, `method`, `status`, `kind`, `actor` |
| Forrás | `url`, `source`, `title`, `published`, `storage_mode` |
| Verzió | `version_hash`, `version_created`, szükség szerint `taxonomy_hash` |

Az export a régebbi dokumentumverziók és az elutasított bizonyítékok rekordjait is tartalmazhatja. Emiatt az elemszáma nagyobb lehet a webes aktuális kártyalistánál. Az exportmezők többnyire belső angol azonosítók, nem a felület magyar feliratai.

Ez **bizonyítékexport, nem teljes adatbázismentés**. Nem tartalmazza a teljes dokumentumtár minden szövegét, az összes ellenőrzési előzményt és API-naplót. JSON-ból visszatöltő gomb sincs a weboldalon.

### 9.3. Internetkapcsolat és letöltések

A saját gépeden futó kiszolgálóból történő riport- és JSON-letöltéshez nincs külső API-hívás. Az eredeti forrásoldalak megnyitása ettől eltérő művelet: külső weboldalra navigál.

## 10. Frissítés és az adatok aktualitása

Az oldal megnyitáskor beolvassa az adatokat. Nem frissít automatikusan időzítővel.

Ha a háttérben új jegyzetet importáltál, osztályoztál vagy kézzel felülvizsgáltál egy bizonyítékot:

1. Térj vissza a böngészőhöz.
2. Kattints az **↻ Adatok frissítése** gombra.
3. Várd meg, amíg eltűnik az **Adatok betöltése…** jelzés.
4. Szükség esetén add meg újra a keresést és a szűrőt.

A gomb betöltés közben átmenetileg letiltott. A sikeres frissítés az aktuális nézetet megtartja, a kereső- és szűrőmezőket alaphelyzetbe állítja.

A frissítés **nem** tölti le újra a forráscikkeket, nem indít osztályozást, nem auditál forrást, és nem hívja meg a Geminit.

A dokumentumrészletek megnyitáskor külön kéréssel töltődnek be. Egy már nyitott részletablak nem frissül automatikusan; zárd be és nyisd meg újra. Ha közben változott az adatbázis, a részlet újabb adatot is mutathat, mint az előzőleg betöltött lista.

Sikertelen adatfrissítéskor a korábban betöltött tartalom a képernyőn maradhat. Az új hibaüzenet mellett ezt korábbi állapotként kezeld, ne sikeresen frissített adatként.

## 11. Javasolt munkamenetek

### 11.1. Egy téma áttekintése

1. Nyisd meg az **Áttekintés** nézetet és olvasd el a mintakorlátokat.
2. Lépj a **Bizonyítékok** nézetre.
3. Keress például `ajánlat` részszövegre.
4. Olvasd el a találat státuszát, típusát és részletét.
5. Nyisd meg a **dokumentum →** gombbal a tárolt szöveget.
6. Ellenőrizd a forrásellenőrzési korlátokat.
7. A **Forrás megnyitása ↗** hivatkozással hasonlítsd össze az eredeti közléssel.
8. Nézd meg a Forrásjegyzékben az ellenőrzési döntést és a következő lépést.

### 11.2. Egy forrás dokumentumainak áttekintése

1. Nyisd meg a **Dokumentumtárat**.
2. Válaszd ki a forrást, például `KSH`.
3. Ha egy év érdekel, írj be egy dátumrészletet, például `2025-`.
4. Nyisd meg a releváns címeket.
5. Figyelj arra, hogy a hivatalos statisztika háttéradat, nem közvetlen vállalkozói panasz.

### 11.3. Ellenőrzött és validált beszámolók megkülönböztetése

1. A Bizonyítékok állapotszűrőjében válaszd a **Forrás ellenőrizve** értéket.
2. A kártyákon nézd meg, melyek **Első kézből** típusúak.
3. Olvasd el az érdekeltségre és hiányzó igazolásra vonatkozó megjegyzéseket.
4. Ne sorold őket automatikusan a kézzel validált esetek közé.
5. Az ellenőrzési napló „Következő lépés” sorai alapján tervezd meg a további kutatást.

### 11.4. Eredmények átadása

1. Frissítsd az adatokat.
2. Töltsd le a Markdown-riportot.
3. Ha további adatfeldolgozás kell, töltsd le a teljes JSON-exportot is.
4. Az átadáskor jelöld a letöltés dátumát és a minta korlátait.
5. A riportban szereplő H-azonosítós hipotéziseket vizsgálandó irányként, ne már bizonyított eredményként add tovább.

## 12. Billentyűzet és keskeny képernyő

### 12.1. Billentyűzetes használat

- **Tab / Shift+Tab:** léptetés a linkek, gombok és mezők között.
- **Enter:** a kijelölt link vagy gomb aktiválása.
- **Szóköz:** gomb aktiválása a böngésző szokásos működése szerint.
- **Esc:** a dokumentumrészlet-ablak bezárása.
- A keresőben gépeléskor azonnal frissül a lista.
- Az oldal elején billentyűzetes fókusznál megjelenik az **Ugrás a tartalomra** link; ezzel átugorható a navigáció.

A fókusz színes kerettel látszik. A böngésző **Ctrl+F** keresése a megjelenített oldalszövegben keres; ez nem helyettesíti az adatbázis teljes szövegű keresését.

### 12.2. Keskeny képernyő

Keskeny ablakban a navigáció felülre kerül, a kártyák és panelek kevesebb oszlopba rendeződnek. A menüikonok és a dokumentumtár melletti kis számláló elrejtődhetnek, a menüpontok megmaradnak.

A széles táblázatot saját területén vízszintesen is görgetheted a jobb oldali oszlopokhoz. A részletablak továbbra is görgethető és az ✕ gombbal bezárható.

A reszponzív megjelenés nem jelent hálózati telefonos hozzáférést: a számítógép loopback címét a telefon nem éri el. A telefonon beírt `127.0.0.1` a telefont jelenti, nem a számítógépet.

## 13. A weboldalon kívüli műveletek

Az alábbiak a platform részei, de nincs hozzájuk webes gomb. A parancsokat a repository gyökerében kell futtatni, majd a böngészőben az **Adatok frissítése** gombot használni.

| Művelet | Elérési mód | Kapcsolódó útmutató |
|---|---|---|
| Új forrásadat gyűjtése | `uv run research collect --limit 30` – külső webes kéréseket indít a konfiguráció szerint | [README](../README.md) |
| Kurált kutatói jegyzetek importja | `uv run research import-experiences` – a meglévő jegyzetfájlt importálja | [Kutatási napló](research_followup.md) |
| Szabályalapú besorolás | `uv run research classify` | [Taxonómia](taxonomy.md) |
| Témák és keresőkifejezések módosítása | `config/taxonomy.yaml` szerkesztése, `taxonomy-check`, majd `classify` | [Taxonómia](taxonomy.md) |
| Bizonyíték kézi minősítése | `research review` E-azonosító alapján; az E betű nélküli számot kell megadni | [README](../README.md) |
| Teljes tárolt szöveg keresése | `uv run research search 'alvállalkoz*'` – FTS-keresés, a korábbi verziókat is megtalálhatja | [README](../README.md) |
| CSV-export | `uv run research export --format csv` – a terminálra ír, fájlhoz átirányítás szükséges | [README](../README.md) |
| Gemini-feldolgozás | Külön telepítés, dokumentumkiválasztás és explicit kapcsolók | [Gemini használata](gemini_usage.md) |
| Gemini-hívások összesítése | `uv run research ai-status` | [Gemini használata](gemini_usage.md) |
| Dokumentumtörlés | `research delete` D-azonosító alapján; kapcsolt adatokat is töröl | [README](../README.md) |
| Megőrzési szabályok alkalmazása | `research retention`, először előnézettel | [README](../README.md) |
| Másik adatbázis megnyitása | Indításkor `--db` paraméterrel | E dokumentum 2. fejezete |

A weboldalon nincs fájlfeltöltés, új rekord létrehozása, címkeszerkesztő, jóváhagyásgomb, törlésgomb, Gemini-beállító, verziótörténet-választó vagy felhasználói fiókkezelés. A kártyák megnyitása nem változtat státuszt.

A parancssori keresésben használható `*` eltér a webes kereső működésétől: a webes keresőbe ne másold át automatikusan az FTS-kifejezéseket.

## 14. Hibakeresés

| Jelenség | Lehetséges ok | Teendő |
|---|---|---|
| Nincs Run Python File gomb | Hiányzó Python bővítmény vagy nem a Python-fájl van megnyitva | Nyisd meg a `start_app.py`-t; használd a taskot vagy a terminálos indítást |
| „Hiányzik a .venv” | Még nem települt a projekt környezete | A gyökérkönyvtárban futtasd: `uv sync --locked` |
| A port nem nyitható meg | Már fut egy kiszolgáló, más alkalmazás foglalja a portot vagy a környezet tiltja a megnyitását | Nézd meg a korábbi terminált; szükség esetén állítsd le a saját korábbi futást, vagy válassz másik portot |
| A böngésző nem nyílik meg magától | Az asztali környezet nem indította el | Nyisd meg kézzel a terminálban kiírt címet |
| „A webhely nem érhető el” | Nem fut a szerver, hibás port vagy másik gépen nyitod meg | Ellenőrizd az indító terminálját és a pontos URL-t |
| „Az adatbázis nem érhető el…” | Nem sikerült az adatlekérés; lehet kiszolgáló-, fájl- vagy adatbázishiba | Ellenőrizd a szervert, majd kattints az Adatok frissítése gombra; ne töröld az adatbázist hibajavításként |
| „A dokumentum nem tölthető be…” | Közben törlődött a rekord vagy nem sikerült a kérés | Zárd be az ablakot, frissítsd a listát, majd nyisd meg újra |
| Minden számláló nulla | Üres vagy másik adatbázis indult | Ellenőrizd az indítási parancsot és a `--db` útvonalat; az indító önmagában nem gyűjt adatot |
| „Nincs a feltételeknek megfelelő…” | A keresés és a szűrő együtt nem ad találatot | Töröld a keresést, válaszd az Összes lehetőséget, majd keress rövidebb részszövegre |
| Egy szó biztosan szerepel a cikkben, mégsem található | A webes kereső nem vizsgálja a teljes cikket | Nyisd meg a dokumentumot, vagy használd a parancssori teljes szövegű keresést |
| Nincs egy adott státusz a legördülőben | Nincs ilyen állapotú aktuális bizonyíték | Ellenőrizd az Összes listát; ez önmagában nem hiba |
| Frissítés után eltűnik a keresés | A nézet újrarajzolásakor a mezők alaphelyzetbe kerülnek | Add meg újra a szűrést |
| A külső forrás nem nyílik meg | Nincs internet, az oldal változott vagy hozzáférési hibát ad | A mentett szöveget továbbra is megtekintheted; az élő elérhetőség hiányát külön kezeld |
| Nem találod a letöltött fájlt | A böngésző letöltési beállítása határozza meg a mentés helyét | Nyisd meg a böngésző Letöltések nézetét; a fájl neve `pilot_report.md` vagy `evidence.json` |
| A JSON több rekordot tartalmaz, mint a kártyalista | Teljes export: korábbi verziók és elutasított rekordok is szerepelhetnek | A `version_id` és `status` mezők szerint vizsgáld az adatot |
| Ismétlődik egy témanév az Áttekintésben | Az összesítés szereplő szerint is csoportosít, de a panel nem írja ki a szereplőt | A riport témák–szereplők táblázatában nézd meg a bontást |

Az általános adatbázishiba-üzenet nem bizonyítja önmagában, hogy sérült az adatbázis. Hibakereséshez az indító termináljának kimenete is hasznos.

## 15. Fogalmak és értelmezési korlátok

| Fogalom | Jelentés |
|---|---|
| **Dokumentum, D…** | Egy mentett forrásrekord vagy kutatói jegyzet |
| **Verzió** | Egy dokumentum adott mentett szövegváltozata |
| **Bizonyíték, E…** | Dokumentumverzióhoz kapcsolt téma és részlet, ellenőrzési állapottal |
| **Hipotézis, H…** | Bizonyítékból kiinduló, további vizsgálatra váró lehetőség |
| **Forrásszöveg** | Az eredeti forrásból eltárolt szöveg vagy engedélyezett kivonat |
| **Kutatói jegyzet** | A kutató saját parafrázisa vagy összefoglalója |
| **Publikálás** | A forrás megjelenésének ismert dátuma |
| **Mentve** | A szövegváltozat adatbázisba kerülésének ideje |
| **Ismeretlen** | Hiányzó vagy nem igazolt adat; nem nulla érték |

A számlálók a saját gyűjtött mintát írják le. A gyakoribb tématalálat nem bizonyítja, hogy az adott probléma a teljes magyar építőiparban is gyakoribb. Ugyanarról a felmérésről szóló több közlés nem feltétlenül több független bizonyíték.

A felület a legfrissebb dokumentumverziókra összpontosít. A teljes export és a parancssori keresés ennél tágabb adatot adhat. Az eltérő darabszámokat mindig az adott funkció szűrési szabályával együtt értelmezd.

A webapp meglévő adatok megjelenítésére szolgál. Az AI-eszközök korábbi felmérése és a saját kutatási skill tervezett elkészítése nem jelent további, rejtett webes funkciókat. Ezekről külön dokumentum szól: [AI-eszközök és saját kutatási skill](ai_tools_research.md).

## 16. Teljes funkciólista

Az alábbi lista a jelenleg megvalósított webes műveletek gyors ellenőrzésére használható.

| Funkció | Hol találod? | Eredmény |
|---|---|---|
| Nézetváltás | Négy menüpont | Másik kutatási nézet |
| Visszatérés a kezdőnézethez | Kutatóműhely logó | Áttekintés |
| Aktuális nézet azonosítása | Menükiemelés és felső sáv | Látható navigációs állapot |
| Adatok újraolvasása | Adatok frissítése | Friss adatbázis-pillanatkép |
| Kutatási számlálók | Áttekintés felső kártyái | Minta, források és bizonyítékok számai |
| Legfrissebb öt dokumentum | Áttekintés | Publikálás szerint rendezett rövid lista |
| Teljes dokumentumlista elérése | Összes megtekintése | Dokumentumtár |
| Hipotézisek áttekintése | Áttekintés | Lehetőség, validációs lépés, üzleti hatás és forrás |
| Minta korlátainak megjelenítése | Áttekintés | Forrásellenőrzött és validált esetek elkülönítése |
| Témák összehasonlítása | Témák a mintában | Csoportonkénti tartalomszám és viszonyított sáv |
| Forrásstátuszok összesítése | Források hozzáférése | Auditstátuszok darabszámai |
| Hiányzó publikációs dátumok száma | Áttekintés | Adatminőségi jelzés |
| Dokumentumkeresés | Dokumentumtár | Szűrés cím/forrás/dátum/URL alapján |
| Forrásszűrés | Dokumentumtár | Kiválasztott forrás rekordjai |
| Találatszám | Dokumentumtár és Bizonyítékok | Az aktuális szűrés eredményének mérete |
| Mentett szöveg megnyitása | Dokumentumcím vagy dokumentum gomb | Részletablak |
| Verzió és mentési idő | Részletablak alja | A megjelenített szöveg azonosítása |
| Validációs korlát és forráshely | Részletablak, ha van ilyen adat | Az ellenőrzés kontextusa |
| Részletablak bezárása | ✕ vagy Esc | Visszatérés a listához |
| Bizonyítékkeresés | Bizonyítékok | Szűrés téma/részlet/forrás/dokumentumcím alapján |
| Bizonyítékállapot-szűrés | Bizonyítékok | Kiválasztott ellenőrzési állapot |
| Bizonyítéktípus, szereplő és parafrázis jelölése | Bizonyítékkártyák | A részlet helyes értelmezése |
| Ellenőrzési napló | Forrásjegyzék | Dátum, döntés, korlát, következő lépés |
| Gyűjtési audit és feltételek | Forrásjegyzék | Rögzített hozzáférési döntések |
| Külső forrás megnyitása | ↗ linkek | Eredeti oldal új lapon |
| Teljes Markdown-riport letöltése | Riport letöltése | `pilot_report.md` |
| Teljes bizonyítékexport | Bizonyítékok → Teljes export | `evidence.json` |
| Billentyűzetes navigáció | Tab, Enter, Esc, Ugrás a tartalomra | Egér nélküli kezelés |
| Keskeny képernyős elrendezés | Automatikus | Átrendezett menü, panelek, görgethető táblázat |
| Betöltési, üres és hibaállapotok | Az érintett nézetben | Visszajelzés és újrapróbálási lehetőség |

Kapcsolódó dokumentumok: [README](../README.md), [taxonómia](taxonomy.md), [Gemini](gemini_usage.md), [adatszótár](data_dictionary.md), [kutatási napló](research_followup.md), [fejlesztési riport](../reports/implementation_report_2026-11-07.md).
