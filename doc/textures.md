# Textures en "oversized assets"

FiveM waarschuwt voor te grote bestanden in `stream/`. Mark wil dat de tool dat vooraf ziet, en het liefst ook oplost.
Dit document zet bij elkaar wat we weten, wat we dachten te weten, en wat we al probeerden.
De labels staan uitgelegd in [README.md](README.md#labels).

---

## Voorbeeld: de geheugengrootte uit de header lezen

Elk gestreamd GTA-bestand (`.ytd`, `.yft`, `.ydr`, …) begint met een RSC7-header van 16 bytes. Daarin staat hoeveel geheugen het bestand in de game nodig heeft. Dit script draaide op 20 okt 2026 over al onze testdata (`tested`). De formule komt uit CodeWalker (`community`).

```python
import struct

def size_from_flags(flags: int) -> int:
    # Formule uit CodeWalker (RpfFile.GetSizeFromFlags)
    s = (((flags >> 27) & 0x1) << 0) + (((flags >> 26) & 0x1) << 1) \
      + (((flags >> 25) & 0x1) << 2) + (((flags >> 24) & 0x1) << 3) \
      + (((flags >> 17) & 0x7F) << 4) + (((flags >> 11) & 0x3F) << 5) \
      + (((flags >> 7) & 0xF) << 6) + (((flags >> 5) & 0x3) << 7) \
      + (((flags >> 4) & 0x1) << 8)
    return (0x200 << (flags & 0xF)) * s

def read_header(path: str) -> dict:
    with open(path, 'rb') as fh:
        head = fh.read(16)
    if head[:4] == b'FXAP':
        return {'kind': 'escrow'}          # versleuteld door Cfx-escrow
    if head[:4] != b'RSC7':
        return {'kind': 'unknown', 'magic': head[:4]}
    version, sys_flags, gfx_flags = struct.unpack('<III', head[4:16])
    return {
        'kind': 'rsc7',
        'version': version,                       # .ytd 13, .yft 162, .ycd 46
        'virtual_mib': size_from_flags(sys_flags) / 1048576,   # model, physics
        'physical_mib': size_from_flags(gfx_flags) / 1048576,  # textures
    }
```

---

## Wat we gemeten hebben (`tested`, 20 okt 2026)

| Bestand | Op schijf | In geheugen | Opmerking |
|---------|-----------|-------------|-----------|
| `strman.ytd` | 1,9 MB | **76 MiB phys** | Marks bekende "oversized"-geval |
| `brickadeb.ytd` (0x63E74A4A) | 4,9 MB | **224 MiB phys** | grootste in de testdata |
| `lsfd3.ytd` | 2,2 MB | 64 MiB phys | |
| `socharger.ytd` | 4,3 MB | 52 MiB phys | |
| `zaccflatlit.ytd` | 7,6 MB | 32 MiB phys | |
| `lssdbuffalosx.ytd` | 2,3 MB | 28 MiB phys | |
| `kriegerty2.ytd` | 0,2 MB | 0,5 MiB phys | referentie zonder probleem |
| `bell505.yft` | 10,0 MB | 20,1 MiB virt | grootste model |

Alle cijfers per bestand staan in [test_data.md](test_data.md).

**Wat dit laat zien:**

1. **De grootte op schijf zegt niets.** Een `.ytd` van 1,9 MB vraagt 76 MiB geheugen. Het bestand is gecomprimeerd; grote, egale textures comprimeren extreem goed. Een check op bestandsgrootte (zoals "`.ytd` > 16 MB" in `docs/plan.md`) mist dus juist de probleemgevallen.
2. **Het probleem zit per bestand.** Elk bestand heeft zijn eigen header en zijn eigen grootte, en FiveM meet ook per bestand (`official`, zie hieronder).
3. **Textures (phys) zijn het probleem, modellen (virt) minder.** In onze testdata zit geen `.yft` boven de 24 MiB virt, wel veel `.ytd`'s boven de 16 MiB phys. Let op: ook een `.yft` kan veel phys hebben, als de textures ín het model zitten. In de downloads van 21 okt is dat zelfs het vaakst: 1.197 van de 1.352 bestanden boven 16 MiB zijn `.yft`'s, 1.029 daarvan door phys en 168 door virt ([test_data.md](test_data.md#downloads-in-vehicles-21-okt-2026)).

## De melding van FiveM

Mark zag de melding bij `strman`. Hoe hij werkt, staat in de FiveM-broncode (`official`, `code/components/citizen-server-impl/src/ResourceStreamComponent.cpp`, functies `ValidateSize` en `ConvertRSC7Size`, master 20 okt 2026; Q-T1):

- De **server** controleert bij het starten van een resource elk bestand in `stream/` met een RSC7-, RSC8- of RSC5-header. Alleen voor GTA V. Het aantal meldingen staat daarna in "Started resource x (n warnings)" (`ServerResources.cpp`).
- Per bestand twee getallen: physical en virtual, elk apart. Ze worden berekend met precies dezelfde formule als ons script (`ConvertRSC7Size`).
- De grenzen zijn hard "groter dan":

| Grootte (per getal) | Kleur in de console | Extra zin |
|---------------------|---------------------|-----------|
| tot en met 16 MiB | geen melding | |
| meer dan 16 MiB | blauw (`^4`) | |
| meer dan 32 MiB | geel (`^3`) | |
| meer dan 48 MiB | geel (`^3`) | "Oversized assets can and WILL lead to streaming issues (such as models not loading/rendering)." |
| meer dan 64 MiB | rood (`^1`) | idem |

- De tekst is: `Asset <resource>/<bestand> uses <X.X> MiB of <physical|virtual> memory.` Een bestand dat op beide boven de grens zit, geeft twee regels.
- Het gevolg (`community`): textures of modellen laden niet of laat ("streaming issues"), vooral bij spelers met weinig videogeheugen (Q-T2).

Op het Cfx-forum gaan de draden [Oversized assets can and WILL lead to streaming issues](https://forum.cfx.re/t/oversized-assets-can-and-will-lead-to-streaming-issues/1761205) en [Virtual/physical memory for assets](https://forum.cfx.re/t/virtual-physical-memory-for-assets/1689728/4) hierover (`community`, nog niet gelezen). Nog te doen: de melding in de serverlog van de dev-server terugzien.

---

## Wat de oude notities zeiden (nog niet bewezen)

Uit `docs/plan.md` §7 en §8. Allemaal `aanname`; sommige meten het verkeerde.

| Bewering | Probleem |
|----------|----------|
| Een texture groter dan 2048×2048 = fout, "crash op sommige clients" | Niet nagekeken. Een grote texture telt mee in phys, maar de grens van FiveM gaat waarschijnlijk over het hele bestand |
| Geen macht van 2 (bijv. 1500×1000) = "rendering artifacts" | Niet nagekeken |
| `.ytd` groter dan 16–20 MB = streaming errors | **Meet het verkeerde**: bestandsgrootte in plaats van geheugen (zie hierboven) |
| Meer dan 50–60 textures per `.ytd` = geheugenproblemen | Niet nagekeken |
| Een groot basisformaat geeft een grote mipmap-keten | Klopt in principe (een volledige mip-keten is ±1/3 extra) |
| VehicleOptimizer: `.ytd`/`.yft` groter dan 16 MB op schijf = oversized | Zelfde fout: bestandsgrootte; het logbestand bleef leeg |
| `trp_dds_inspector`: alles boven 1024 px verkleinen | Andere grens dan het plan (2048), en zonder bron |

Voor de tool betekent dit: meet eerst de header (snel, geen extra software), en kijk pas daarna per texture (resolutie, formaat, mips) om te zien wát het bestand zo groot maakt.

---

## Bestandsformaten (kort)

| Formaat | Herkennen | Wat | Status |
|---------|-----------|-----|--------|
| RSC7 | eerste 4 bytes `RSC7` | één resource (`.ytd`, `.yft`, `.ydr`, …); data gecomprimeerd (deflate) | `tested` (header), indeling `community` |
| RPF7 | eerste 4 bytes `RPF7` (`7FPR` als je ze omgekeerd leest), daarna het type versleuteling | archief, bijv. `dlc.rpf` van een GTA-mod; `cle53amg/dlc.rpf` heeft `OPEN` (niet versleuteld) | `tested` (header) |
| FXAP | eerste 4 bytes `FXAP` | door Cfx-escrow versleuteld; niet te lezen of aan te passen | `tested` (`strman.yft`, `strman_hi.yft`) |

**Escrow:** bij `strman` zijn de `.yft`'s versleuteld, de `.ytd`'s niet. Een escrow-resource herken je aan `.fxap` in de root en `dependency '/assetpacks'` in het manifest. Zo'n resource mag de tool alleen lezen en melden, nooit aanpassen (Q-T7).

### `+hi` en `_hi`

- `<model>_hi.yft`: het model in hoge kwaliteit, voor dichtbij. `community`
- `<txd>+hi.ytd`: textures in hoge kwaliteit; `HDTextureDist` in `vehicles.meta` bepaalt vanaf welke afstand. `community`
- In `0x63E74A4A` zijn `brickadeb.ytd` en `brickadeb+hi.ytd` precies even groot (224 MiB). Of de game dan beide laadt, weten we niet (Q-T5).
- `docs/plan.md` §5 had het omgekeerd (`[naam]+hi.yft`, `[naam]_hi.ytd`): `fout`. In alle testdata is het `_hi.yft` en `+hi.ytd`.

---

## txdRelationships

Een voertuig kan textures erven van een andere `.ytd`: staat een texture niet in de `child`, dan zoekt de game in de `parent`. Uit `docs/meta_reference_and_load_order.md` §4.5 en `docs/vehicle_intake_procedure.md` §9 (`community`):

```xml
<txdRelationships>
  <Item>
    <parent>vehicles_jet_interior</parent>
    <child>bell505a</child>
  </Item>
  <Item>
    <parent>bell505a</parent>
    <child>bell505</child>
  </Item>
</txdRelationships>
```

Zoekvolgorde: `bell505` → `bell505a` → `vehicles_jet_interior` (vanilla).

- Een extra `.ytd` naast het model (`bell505a.ytd`) is dus meestal geen tweede voertuig, maar een laag in deze keten. Niet blind weghalen. (`PACK_VALIDATION.md` dacht dat er livery-varianten in zitten; dat kan allebei, in-game nakijken.)
- Een vanilla-parent (`vehicles_fmj_interior` bij `kriegerty2`) scheelt textures en geheugen.
- **Nieuw gevonden:** `strman` herhaalt in zijn `vehicles.meta` relaties van vanilla-voertuigen (`vehshare` → `vehicles_biker_shared`, …). De tool moet relaties melden waarvan de `child` niet bij de resource zelf hoort (`tested`, gelezen).
- **Nieuw gevonden:** in de VehicleTool-pack is `txdRelationships` bij BELL505 leeg; de template nam de keten uit de bron niet over (`tested`, gelezen).

**Idee om te testen (Q-T8):** als FiveM per bestand meet, kan een te grote `.ytd` misschien gesplitst worden in twee `.ytd`'s met een `txdRelationships`-keten. Het totale geheugen blijft gelijk, maar elk bestand komt onder de grens.

---

## Wat we al probeerden (maart 2026)

Uit `docs/plan.md` §8b en de code. De tools zelf staan in [inventory.md](inventory.md).

**Geen van onze tools leest de inhoud of de geheugengrootte van een `.ytd`.** `ytd_mvp.py` leest alleen de eerste 4 bytes (zo bleek dat een `.ytd` RSC7 is). De rest meet de grootte op schijf (VehicleOptimizer, de CodeWalker-poging), kijkt alleen naar de extensie (converter, repo), of leest `.dds`-bestanden die met de hand uit OpenIV komen (`trp_dds_inspector`).

| Route | Uitkomst |
|-------|----------|
| `rpf-cli` (via `noneWorking/trp_vehicle_toolkit/ytd_mvp.py`) | Werkt niet voor een losse `.ytd`: `rpf-cli extract` verwacht een RPF7-archief, een `.ytd` is RSC7. Terugpakken naar een `.ytd` kan rpf-cli niet. Volgens een hint in de code is de schrijfwijze `rpf-cli extract -o <uit> <archief>` (geen `-i`); niet bewezen |
| CodeWalker.API (via `noneWorking/trp_codewalker_ytd_toolkit`) | Endpoints: `GET /api/service-status`, `GET /api/search-file?filename=…`, `GET /api/download-files?fullPaths=…` (optioneel `xml`, `textures`). `download-files` geeft HTTP 200 met een fout per item: kijk altijd naar de inhoud, niet naar de status. `fullPaths` moet een pad zijn dat CodeWalker zelf kent; een lokaal pad naar een `.rpf` werkte niet. Het enige bewaarde rapport laat zien dat de API toen niet draaide. Importeren of vervangen is nooit gebouwd |
| **Handmatig met OpenIV** (tijdelijke werkwijze) | Werkt: `.ytd` openen, alle textures exporteren naar een map met dezelfde naam (`strman.ytd` → `strman/`), daarna kijken met `trp_dds_inspector` |
| Verkleinen met Pillow (`trp_dds_inspector`, "Auto-resize > 1024") | **Maakt het erger**: ongecomprimeerd RGBA zonder mipmaps. Getest: DXT1 2048² van 2,0 MB werd 1024² van 4,0 MB. Pillow kan DXT1 en DXT5 schrijven, geen BC7, en geen mipmaps (`tested` op een kopie, 20 okt 2026) |

Het **terugschrijven** van een `.ytd` is dus nooit geprobeerd. Dat blijft de echte onbekende (Q-T4).

**Nieuw om te bekijken:** volgens een eerste blik op de projectpagina heeft een nieuwere `rpf-cli` een opdracht om textures uit een `.ytd` te exporteren (`textures`, met `--dds`) en een opdracht die de RSC7-header met de geheugengroottes toont (`resource info`). Welke versie onze `rpf-cli.exe` is, weten we niet. `aanname` (Q-A3, Q-A5).

**Toolkeuze uit maart** (`aanname`, niet uitgewerkt):

| Rol | Tool |
|-----|------|
| automatisch uitpakken en vervangen | CodeWalker.API |
| `.rpf` naar werkmap | RPF-Extractor + rpf-cli |
| controle in Blender | Sollumz |
| handmatige terugval | OpenIV |
| na-bewerking | Texture Magic |
| resizen en comprimeren | Pillow / ImageMagick (DXT1 zonder, DXT5 met transparantie) |

De verklein-route uit het plan (§7, na bevestiging door de gebruiker): textures uitpakken; elke te grote texture naar de dichtstbijzijnde macht van 2 die niet groter is dan 2048; verkleinen met ImageMagick (lanczos-filter); opnieuw comprimeren (DXT1 zonder, DXT5 met transparantie); terug in de `.ytd`. `aanname`, nooit gebouwd.

De eisen die het plan stelde aan een eerste proef (§8b): minstens één `.ytd` uitgepakt, minstens één resolutie in het rapport, minstens één poging tot terugpakken, en in het rapport `extract_ok` en `repack_ok` apart, met het gebruikte commando en de foutmelding als terugpakken mislukt. Bruikbaar als maatstaf voor Q-T4.

---

## Hoe zou de tool een te grote `.ytd` kunnen verkleinen?

Allemaal ideeën; niets getest. Uitzoeken in Q-T4.

1. **Bovenste mip-levels weglaten.** Een texture met een mip-keten heeft de halve resolutie al aan boord. Het bovenste level weghalen halveert breedte en hoogte en scheelt ±75% geheugen, zonder opnieuw te comprimeren (dus geen kwaliteitsverlies buiten de resolutie). Vereist wel dat we een `.ytd` kunnen herschrijven.
2. **Uitpakken, verkleinen, opnieuw comprimeren** met een DDS-tool (bijv. texconv), daarna terug in de `.ytd`. Nodig als er geen mips zijn.
3. **Splitsen** over twee `.ytd`'s met `txdRelationships` (zie hierboven, Q-T8).
4. **Handmatig** (OpenIV of CodeWalker): de tool meldt alleen en geeft per texture advies.

Wat een texture "groot" maakt (resolutie, formaat, aantal mips) kunnen we pas zien als we de inhoud van een `.ytd` kunnen lezen. Dat kan zonder extra software als we het RSC7-formaat zelf parsen, of met CodeWalker als bibliotheek (Q-A5).

---

## Open vragen

Q-T1 t/m Q-T8 in [open_questions.md](open_questions.md).

## Links

- CodeWalker: https://github.com/dexyfex/CodeWalker
- CodeWalker.API: https://github.com/flobros/CodeWalker.API
- rpf-cli: https://github.com/VIRUXE/rpf-cli
- Sollumz: https://github.com/Sollumz/Sollumz
- Meer in [sources.md](sources.md).
