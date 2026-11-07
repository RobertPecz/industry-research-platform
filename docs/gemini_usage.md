# Opcionális Gemini-feldolgozás

A `research analyze` alapértelmezésben szabályalapú, nem indít modellhívást.
A webapp és az indítóscript sem használja a Gemini API-t.

## Telepítés és konfiguráció

```bash
uv sync --locked --extra gemini
```

A `config/gemini.yaml` állítja a modellazonosítót és a korlátokat. A csomag opcionális: nélküle a webapp, a taxonómia, az import és a riport működik.

Az alapkonfigurációban `gemini-3.1-flash-lite` szerepel. Ezt a 2026-11-07-i dokumentációellenőrzéskor a Google árlistája Free Tier lehetőséggel mutatta. Ez **nem bizonyítja a te API-projekted díjmentességét**. Ellenőrizd a projekt billing- és kvótaállapotát az AI Studióban. A program `models.get` kéréssel ellenőrzi a modell elérhetőségét, de ez sem igazolja a billing állapotát.

Források: [Google árlista](https://ai.google.dev/gemini-api/docs/pricing?frmapp=yes), [Google SDK](https://googleapis.github.io/python-genai/), [modell API](https://ai.google.dev/api/models).

## Bekapcsolás egy kiválasztott dokumentumra

1. A webappban nézd meg a dokumentum teljes tárolt szövegét és azonosítóját.
2. Csak olyan eredeti forrásszöveget válassz, amely jogszerűen továbbítható, nem bizalmas és nem tartalmaz személyes adatot. A kód csak `source_text` tárolási módot és `allowed` forrásauditot enged át. Ez technikai előszűrés, nem automatikus adatvédelmi vagy licencellenőrzés.
3. A kulcsot környezeti változóban add meg. Bashban a következő bevitel nem jeleníti meg és nem írja a shell historyba a kulcsot:

```bash
read -rsp 'Gemini API-kulcs: ' GEMINI_API_KEY
export GEMINI_API_KEY
printf '\n'
```

4. Csak a fenti ellenőrzések után indítsd el:

```bash
uv run --extra gemini research analyze \
  --backend gemini_free \
  --document 1 \
  --allow-external-llm \
  --confirm-free-tier \
  --confirm-public-data
```

A `1` példaként szereplő dokumentumazonosító; a kiválasztott dokumentumot ellenőrizni kell. Több dokumentumhoz ismételd a `--document` kapcsolót. Nincs „összes dokumentum automatikusan” mód. Más konfiguráció: `--gemini-config config/gemini.yaml`.

A három kapcsoló azt jelenti, hogy engedélyezed a külső hívást, ellenőrizted a projekt Free Tier állapotát és a kijelölt szövegek továbbíthatóságát. A kulcs jelenléte önmagában nem elegendő. A program nem kapcsol billinget és nem vált más szolgáltatóra vagy modellre.

## Korlátok, hibák és újraindítás

- Alapból legfeljebb 10 API-kérés futásonként, beleértve a modell-ellenőrzést és az újrapróbálkozásokat.
- Egyszerre egy kérés; 30 másodperces időkorlát kérésenként.
- 4000 karakteres darabok, legfeljebb 40000 karakteres dokumentum. Túl hosszú dokumentumnál hiba történik, nem csendes csonkolás.
- A fix darabolás mondatot is szétvághat; ez csökkentheti a felismerés teljességét.
- 500/502/503/504: legfeljebb 3 próbálkozás, korlátozott exponenciális várakozással és jitterrel.
- 429: azonnali halasztás és a batch leállítása. Ez konzervatív politika, a program nem próbálja vakon elkölteni a kvótát.
- Timeout/hálózati hiba: halasztás, később kézzel újraindítható.
- 400/401/403/404: konfigurációs vagy jogosultsági hiba, nincs automatikus retry.
- Hibás JSON, hiányzó mezők, nem létező idézet: nincs bizonyítékmentés.
- A sikeres darabok újraindításkor a cache-ből maradnak meg. A feldolgozás dokumentumverzióhoz, tartalomhash-hez, modellhez, prompt-/sémaverzióhoz és darabolási mérethez kötött.
- A cache dokumentumverziónként működik; azonos szöveg más URL alatt külön verzióként új hívást igényelhet.

Ugyanazt a parancsot újrafuttatva folytatható a batch. A nem sikeres futás 1-es kilépési kódot ad és géppel olvasható státuszt ír ki.

```bash
uv run research ai-status
uv run research problems
uv run research export --format json
```

Az `ai_attempts` tábla a hívásokat, státuszokat, ismert tokenhasználatot és időt tárolja; az ismeretlen tokenadat NULL, nem kitalált nulla. Pénzbeli költséget nem becsülünk árlista és projektbilling alapján ellenőrizetlenül. A `models.get` naplója nem tartalmaz forrásszöveget. Hibaszövegek helyett biztonságos hibakódok maradnak meg; a kulcsot nem tároljuk.

## Eredmények értelmezése

A gépi bizonyíték `suggested` állapotú. A modell által javasolt szereplő, bizonyítéktípus, összefoglaló és munkafolyamat az `ai_chunks.result` JSON-ban marad. Az `evidence` rekord szereplője és bizonyítéktípusa kezdetben `unknown`: a gépi önbizalom nem jelent validált tényt.

Minden gépi bizonyíték módszere `gemini:<chunk_id>:<eredményazonosító>`, így összeköthető az `ai_chunks` táblában a modelllel, időponttal, dokumentumverzióval és szövegrész határaival. Több probléma is menthető ugyanabból a részletből. A kézi címkéket nem írjuk felül.

A szabályalapú témák a taxonómia magyar neveit, a Gemini-kimenet pedig az ellenőrzött séma angol kategóriaazonosítóit használja; automatikus összevonás nincs.

## Ellenőrzött működés és fennmaradó korlát

Az integráció mock klienssel és a valódi Google SDK mock HTTP-transportjával tesztelt. A fejlesztés során nem történt élő Gemini-generálás. Emiatt a konkrét kulccsal való hozzáférés, a tényleges kvóta, a magyar kinyerési pontosság és a valós válaszidő még nincs megmérve.
