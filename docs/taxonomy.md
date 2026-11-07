# Konfigurálható taxonómia

A szabályalapú címkézés a `config/taxonomy.yaml` fájlt használja, nem a Python-kódba írt szótárat.

```yaml
version: '2'
industry: construction_hu
topics:
  ajánlatadás: [árajánlat, költségvetés]
  pénzügy: [kintlévőség, késedelmes]
```

```bash
uv run research taxonomy-check
uv run research classify
uv run research analyze --backend none
uv run research classify --taxonomy config/taxonomy.yaml
```

A `taxonomy-check` adatbázismódosítás nélkül ellenőrzi és kiírja a konfigurációt. A verzió szöveg legyen, ezért az idézőjelet tartsd meg. A témákhoz nem üres szöveglisták tartoznak. A keresés kis- és nagybetűtől független részszövegegyezés; nem reguláris kifejezés és nem nyelvi elemzés. Az ékezetek számítanak.

A `taxonomies` táblában a teljes konfiguráció és SHA-256 azonosítója megmarad; a gépi bizonyíték hivatkozik erre. A hash akkor is változik, ha elfelejted növelni a kézi verziószámot. A szabályok csak az `industry` mezővel egyező dokumentumokat címkézik.

Újrafuttatáskor az ellenőrizetlen szabálytalálatok frissülnek, a már nem megfelelő javaslatok eltűnnek. A kézi ellenőrzést vagy hipotézist kapott rekordok megmaradnak. A régi és az átnevezett kézi témákat is védjük az újragenerálástól. A változatlan témák rekordazonosítója megmarad.

A taxonómia nem bizonyít üzleti problémát: minden automatikus találat `suggested`. Nem reprezentatív mintából nem számítunk ágazati gyakoriságot.
