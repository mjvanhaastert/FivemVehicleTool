# Onderzoeksscripts

Scripts die we voor het onderzoek gebruiken. Ze veranderen niets in de gescande mappen; alleen `build_testpack.py` schrijft, en dan alleen in `[vehicletests]`. Python 3.9 of nieuwer, alleen de standaardbibliotheek.

Gebruikt voor de scan van de downloads op 21 okt 2026 ([doc/test_data.md](../../doc/test_data.md)).

## `scan_vehicles.py`

```text
python3 -I scan_vehicles.py fivem-view <resources-map> <uit.json>
python3 -I scan_vehicles.py units <map> <uit.json>
```

- `fivem-view` doet na hoe de FiveM-server resources vindt: alleen mappen met haken worden doorzocht, elke andere map is een resource ([doc/folder_structure.md](../../doc/folder_structure.md) §5).
- `units` zoekt in een map elke resource (elke map met `fxmanifest.lua` of `__resource.lua`, ook diep genest) en leest per resource: het manifest (`data_file`, `files`, scripts), alle meta's, `AddTextEntry` in de `.lua`-bestanden, de namen in `.nametable`-bestanden, en de eerste 16 bytes van elk resource-bestand (RSC7-header: geheugengrootte, zie [doc/textures.md](../../doc/textures.md)).

## `analyze.py`

```text
python3 -I analyze.py <map met units_*.json en fivem_view.json> <bevindingen.json> [vehicles.json]
```

Zet de scans om in bevindingen per soort (laden, manifest, meta-inhoud, botsingen, grootte). `vehicles.json` is de lijst met vanilla-voertuigen uit de kennisbasis (`mjvanhaastert/Fivem`, `data/vehicles.json`); zonder die lijst vallen de vanilla-controles weg.

## `build_testpack.py`

```text
python3 -I build_testpack.py <resources-map> <scan-map> plan    <geval> [<geval> ...]
python3 -I build_testpack.py <resources-map> <scan-map> build   <geval> [<geval> ...]
python3 -I build_testpack.py <resources-map> <scan-map> rewrite <geval> [<geval> ...]
python3 -I build_testpack.py <resources-map> <scan-map> index
```

Bouwt het testpakket `[vehicletests]` uit de downloads in `[Vehicles]` ([doc/test_pack.md](../../doc/test_pack.md)). `<scan-map>` bevat de `units_*.json` van `scan_vehicles.py`. Een geval is een naam (`vt_00_baseline`), een begin van namen (`vt_0`), of `all`, `wild` of `made`.

- `plan` laat per geval zien wat er gekopieerd wordt (mappen, modellen, onderdelen, liveries, naam).
- `build` maakt de gevallen die nog niet bestaan. Een voertuig uit een pack krijgt de indeling van B24; bestanden blijven byte voor byte gelijk. Elk geval krijgt een `README.md` en een `sources.json` (per bestand: herkomst, grootte, md5).
- `rewrite` schrijft van een gebouwd geval alleen de eigen bestanden opnieuw (`README.md`, `sources.json`, `fxmanifest.lua`, gewijzigde meta's) en controleert dat de gekopieerde bestanden gelijk zijn aan de bron.
- `index` schrijft het overzicht `[vehicletests]/README.md`.

Het script leest alleen uit `[Vehicles]` en schrijft alleen in `[vehicletests]`. Het overschrijft geen voertuigbestanden en verwijdert niets (in de gedeelde mappen mag dat ook niet).

## Uitvoer

Zet uitvoer in `research/output/`; die map staat in `.gitignore`. De scans bevatten bestandslijsten van packs van anderen en horen niet in git.

`-I` zorgt dat Python geen modules uit de huidige map laadt; handig als je een script vanuit een map met downloads start.
