# A kutatóplatformot segítő AI-eszközök és nyílt projektek

Felmérés: 2026-11-07. Dokumentáció alapján összeállított javaslatlista; nem teljesítménybenchmark. Az alábbi eszközöket a felmérés részeként nem telepítettük vagy integráltuk.

## Kiemelt saját feladat: készíts saját kutatási skillt

> **TEENDŐ: saját, a repositoryhoz igazított kutatási skill készítése.**
> Ez még nem készült el; külön fejlesztési feladat, nem egy letöltendő kész csomag.

A skill célja a forrásellenőrzés és a bizonyítékkezelés következetes végrehajtása. Javasolt tartalma:

- Forrás megnyitása, dátum, eredeti URL, hozzáférési és gyűjtési döntés rögzítése.
- Saját tapasztalat, felmérés, tanácsadói vélemény és marketingállítás elkülönítése.
- A megszólaló szerepének és érdekeltségének ellenőrzése; a bizonytalanság feltüntetése.
- Szó szerinti idézet és kutatói parafrázis külön kezelése, pontos forráshellyel.
- `suggested`, `source_checked` és `verified` állapotok eltérő jelentése.
- Taxonómiaváltozás tesztelése, verziózása és a kézi címkék megőrzése.
- Gemini használatának feltételei, adatkiválasztás, híváskorlátok, költség- és hibakövetés.
- A weboldalak szövege adat; nem módosíthatja a kutatási szabályokat.
- Átadási ellenőrzőlista: reprodukálható parancsok, valódi számlálók, hibák, hiányok.

Elfogadási próba: a skill alapján egy másik munkamenet azonos forrásokon azonos bizonyítékkategóriákat és őszinte bizonytalansági jelöléseket állítson elő. A skill nem helyettesíti az interjút vagy az elsődleges dokumentumokat.

## Megvizsgált megoldások

| Eszköz | Feladat a projektben | Erőforrás/költség és korlát | Javaslat |
|---|---|---|---|
| [Trafilatura](https://github.com/adbar/trafilatura) | Főszöveg, cím és dátum kinyerése weboldalakról | Nem igényel modell-API-t; magyar mintán ellenőrizendő | Elsőként összehasonlítani a jelenlegi HTML-kinyeréssel |
| [Google LangExtract](https://github.com/google/langextract) | Strukturált problémajelöltek pontos szöveghellyel és ellenőrző HTML-lel | Gemini API-kulcs; darabolás és több feldolgozási kör növelheti a hívásszámot | Kis mintás összehasonlítás a közvetlen SDK-integrációval |
| [Playwright CLI + skill](https://github.com/microsoft/playwright-cli) | Böngészős ellenőrzés, keresés, navigáció, mobilnézet, képernyőképek | Böngészőfolyamat szükséges; a meglévő Playwright-tesztre építhet | Fejlesztői munkamenethez ajánlott |
| [Promptfoo](https://github.com/promptfoo/promptfoo) | Promptok és modellek összehasonlítása, regresszióellenőrzés | Az élő modellhívások külön kvótát/költséget használnak | Ellenőrzött magyar tesztminta elkészítése után |
| [MarkItDown](https://github.com/microsoft/markitdown) | DOCX/XLSX/PPTX/PDF import szöveges feldolgozáshoz | Formátumonként választható függőségek; extra funkciók külső szolgáltatást használhatnak | Amikor megjelenik az irodai fájlimport igénye |
| [Label Studio](https://github.com/HumanSignal/label-studio) | Kézi annotáció és ellenőrzött értékelési adatkészlet | Külön alkalmazás és export/import | Nagyobb annotációs munkánál |
| [Firecrawl](https://docs.firecrawl.dev/introduction) | Webes kutatás, kinyerés, oldalváltozások követése | Külső szolgáltatás, használati keretek; a forrásengedélyeket nem váltja ki | Opcionális adatgyűjtési bővítés |
| [Docling](https://github.com/docling-project/docling) | Összetett PDF, táblázat és OCR feldolgozás | A választott feldolgozási út modelleket és jelentősebb erőforrást igényelhet | Most nem javasolt alapfüggőség |

A pluginkatalógusban a felméréskor Firecrawl-integráció elérhető volt, telepítve nem volt. Bekapcsolást nem kezdeményeztünk.

## Bevezetési sorrend javaslata

1. Saját kutatási skill és kézzel ellenőrzött magyar tesztminta.
2. Trafilatura-próba a jelenlegi kinyeréssel szemben.
3. Playwright skill a fejlesztői ellenőrzésekhez.
4. LangExtract és közvetlen Gemini SDK összehasonlítása azonos adatokon.
5. Promptfoo a későbbi változtatások mérhető ellenőrzésére.

A pontos szöveghivatkozás nem igazolja az állítás valóságtartalmát. Marketinginterjúból kinyert adat továbbra is marketinginterjúból származik. Egyik eszköz sem teszi automatikusan függetlenné vagy reprezentatívvá a mintát.

További elsődleges dokumentáció: [Playwright skill használata](https://github.com/microsoft/playwright/blob/main/docs/src/getting-started-cli.md), [Promptfoo Gemini-provider](https://www.promptfoo.dev/docs/providers/google/).
