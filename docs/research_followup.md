# További forrásellenőrzés – 2026-11-07

## Versenytársak

- [PlanDoc](https://www.plandoc.hu/hu/): a gyártó nyilvános termékoldalát megnyitottuk. Dokumentum- és tervkezelést, helyszíni munkafolyamatokat és BIM-modult ismertet. A funkcionalitás gyártói állítás, nem független teszt. Árazás és API-hozzáférés nincs ellenőrizve.
- [PlanRadar](https://www.planradar.com/hu/termekunk/epitesi-tervdokumentacio-kezeles/): keresőben elérhető gyártói oldal tervkezelésről; a nyitóoldal közvetlen webes megnyitása időtúllépéssel járt. Egyelőre kutatási jelölt, nem tesztelt megoldás.

## Első kézből származó tapasztalat keresése

[Nyilvános építőipari Reddit-beszélgetés](https://www.reddit.com/r/epitoipar_hun/comments/1v48dyd/): webes megnyitás sikerült. A szerző saját kivitelezői működéséről számol be: elkülönült táblázatok, későn látható projekteredmény, gépnyilvántartás. Saját szoftvert is népszerűsít, ezért erős értékesítési torzítás lehetséges; a foglalkozási önazonosítás nem ellenőrzött. A kommentekben mások meglévő eszközösszeállításról és CRM-bevezetési szándékról írnak. Ezek nem külön, validált panaszok. Automatizált gyűjtést nem végeztünk; platformengedély nincs igazolva. Csak bibliográfiai kutatási jegyzet marad, személynevek nélkül.

Eredmény: egy ígéretes, önbevallásos első kézből származó jelölt, nulla ellenőrzött vállalkozói tapasztalat. Az öt tapasztalatra vonatkozó cél nem teljesült. A hiányt nem pótoljuk statisztikai közlésekkel vagy szoftveres reklámállításokkal.

## Kiegészítő ellenőrzés – 2026-11-07

Hat jelölt célzott vizsgálatának eredménye a `config/validated_experiences.json` fájlban található. A korábbi nulla értékhez képest **2 forrásszinten ellenőrzött, saját tapasztalatot leíró beszámoló** került elő. **Függetlenül validált eset továbbra is 0; az öt ilyen tapasztalatot célzó kutatási feltétel nem teljesült.**

- [ELBA kivitelezői interjú](https://elba.hu/blog/interju-egy-aktiv-elba-felhasznalo-kivitelezovel-emecz-viktorral/): korábbi ajánlatadási problémákra vonatkozó kérdés–válasz ellenőrizve. Rövid kutatói parafrázis készült. Szállítói ügyfélinterjú, így az állítás nem független teljesítménymérés.
- [iKont alapítói interjú](https://ikont.hu/interju-juhasz-sandor-peterrel-az-ikont-ugyvezetojevel-es-tarsalapitojaval/): 2. és 4. kérdés ellenőrizve; saját kivitelezői múltra utaló beszámoló. Értékesítési érdekeltség fennáll, független munkanapló nincs.
- [Bonsite iparági oldal](https://bonsite.hu/hu/iparag/epitoipar): megnyitva, de a termékoldal nem közvetlen kivitelezői beszámoló; marketingeredményt nem emeltünk át validált bizonyítékként.
- A korábbi Reddit-jelölt és az [MKIK esettanulmány-jelölt](https://vallalkozzdigitalisan.mkik.hu/tudastar/adatlap?category=tanulmanyok&id=5084) megnyitása Cache miss hibával sikertelen.
- A [Dynago ERP-interjú](https://dynago.hu/van-amit-csak-evekkel-tapasztalattal-es-futo-rendszerekkel-lehet-kivaltani-hol-csuszhat-el-az-epitoipari-erp-rendszerek-bevezetese/) megnyitása időtúllépéssel sikertelen; keresési kivonat nem elég validáláshoz.

A két jegyzet `research_note`, bizonyítékaik `first_hand` és `source_checked` jelölést kapnak. A `first_hand` a beszámoló jellegét jelzi, nem külső személyazonosság-ellenőrzést. Publikálási dátumuk ismeretlen maradt. Automatikus gyűjtési engedélyt nem adtunk ezeknek az oldalaknak.

Reprodukció: `uv run research import-experiences`. Az import nem tesz webes kérést: a már ellenőrzött, kurált jegyzeteket tölti be. Újrafuttatáskor nem duplikálja őket és nem írja felül a kézi bizonyítékstátuszt. A felületen a bizonyítékkártyák és a forrásnézet ellenőrzési naplója mutatja a korlátokat.
