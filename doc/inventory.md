# Inventaris

Wat er in de projectmap `resources\[wip]\VehicleEditor` en in de GitHub-repo `mjvanhaastert/FivemVehicleTool` staat, gecontroleerd op 20 okt 2026.
Per onderdeel: wat het is, uit welke tijd, de staat, wat er waardevol aan is, en een advies. De code is regel voor regel gelezen en waar mogelijk getest op kopieën (niets aan de originelen veranderd).

**Sinds 21 okt 2026 staat al het oude werk in `archive/`** (Mark: "zet alle oude docs, informatie, scripts, etc in een archief folder"). De projectmap bevat nu alleen `doc/` en `archive/`. Alles is verplaatst, niets weggegooid; de paden hieronder zijn die van vóór de verhuizing, dus `docs/plan.md` staat nu in `archive/docs/plan.md`. Uitleg per map: `archive/README.md`. In de repo `FivemVehicleTool` staat de oude code nu in `archive/` van de repo (B16).

---

## Overzicht

De map is 1,2 GB met 1.577 bestanden. Bijna alles is testdata.

| Map | Wat | Uit | Grootte | Staat | Advies |
|-----|-----|-----|---------|-------|--------|
| `docs/` | Notities: plan van aanpak, meta-referentie, handling-principes, intake | maart 2026 | 68 KB, 4 bestanden | inhoud verwerkt in `doc/` | archief na review |
| `VehicleTool/` | Python-tool: controleert voertuig-resources en bouwt een pack (Tk-UI en CLI) | maart 2026 | 91 MB, 306 bestanden | controles werken (met veel ruis); pack-uitvoer werkt niet | code bewaren als bron; `pack/`, `report/`, `output/`, `__pycache__/` mogen weg |
| `old/oldversion/` | In-game handling-editor (Lua + NUI), versie 1 | juli 2025 | 112 KB | werkte half: Apply kwam nooit aan, opslaan wel | bewaren als bron voor de editor |
| `VehicleOptimizer/` | Voertuigen sorteren per klasse en meta's maken uit templates; eigen git-repo (`mjvanhaastert/VehicleOptimizer`, één commit) | juli 2025 | 12 MB | concept, werkt niet | archief |
| `trp_dds_inspector/` | Tk-tool: resolutie en grootte van `.dds`-bestanden die met OpenIV zijn geëxporteerd | maart 2026 | 8 KB | tonen werkt; verkleinen maakt bestanden slechter | houden als tijdelijk hulpmiddel, verkleinen niet gebruiken |
| `trp_rpf_to_fivem_converter/` | `dlc.rpf` uitpakken (met `rpf-cli.exe`) en sorteren in `stream/` en `data/` | maart 2026 | 1,9 MB | werkt half, met risico's | bron voor intake (E1) |
| `noneWorking/` | Twee mislukte pogingen om een `.ytd` automatisch uit te pakken | maart 2026 | 2 MB | werkt niet | archief; de lessen staan in [textures.md](textures.md) |
| `vehiclehandler/` | Schade- en reparatiescript van een derde (QuantumMalice, GPL-3.0, vereist ox_lib) | – | 244 KB | niet van ons | uit de map halen of naar `research/` |
| `TestVehicleFolder/` | Vier testvoertuigen | maart 2026 | 363 MB | bruikbaar | houden; zie [test_data.md](test_data.md) |
| `research/` | Negen packs als referentie | maart 2026 | 699 MB | bruikbaar | houden (staat in `.gitignore`); zie [test_data.md](test_data.md) |
| GitHub `FivemVehicleTool` | PyQt6-tool: een map met voertuigen ordenen tot één resource per categorie | 23 feb 2026 (één commit "init") | ±90 KB | werkt, met inhoudelijke fouten | het idee bewaren, de code niet; de repo is het nieuwe thuis (B16), de oude code staat daar in `archive/` |

### Tijdlijn

| Wanneer | Wat |
|---------|-----|
| 1–21 juli 2025 | In-game editor in `TrueRP/VehicleEditor` (26 commits), nu `old/oldversion/` |
| 22–23 juli 2025 | `VehicleOptimizer` |
| 23 feb 2026 | GitHub-repo `FivemVehicleTool` |
| 19–20 maart 2026 | `.ytd`-pogingen (`noneWorking/`), daarna `docs/plan.md` v0.3 met het besluit om voorlopig met OpenIV te werken |
| 20 maart 2026 | Commit die de editor uit git haalt; `trp_dds_inspector` en `trp_rpf_to_fivem_converter` erbij |
| 20 maart – 1 april 2026 | `VehicleTool` en de documenten in `VehicleTool/docs/`; rapporten van 20–25 maart |

---

## Git

- De map is een clone van **`TrueRP/VehicleEditor`** (niet openbaar te lezen). 27 commits: 26 van 1–21 juli 2025 (de in-game editor), en één op 20 maart 2026 die de editor weghaalde en `trp_dds_inspector` en `trp_rpf_to_fivem_converter` toevoegde.
- **Git volgt maar 7 bestanden**: `.gitignore`, `trp_dds_inspector/` (3) en `trp_rpf_to_fivem_converter/` (3). De wijzigingen daarin zijn alleen regeleinden (CRLF), plus één regel in `.gitignore` (`research/`).
- **Niet in git, dus zonder back-up:** `VehicleTool/`, `VehicleOptimizer/` (heeft wel een eigen repo), `vehiclehandler/`, en via `.gitignore` ook `docs/`, `old/`, `noneWorking/`, `TestVehicleFolder/` en `research/`. Het patroon `docs/` in `.gitignore` sluit ook `VehicleTool/docs/` uit. De nieuwe map `doc/` valt er niet onder.
- Het project woont voortaan in de repo `mjvanhaastert/FivemVehicleTool` (B16, gekozen op 21 okt 2026). De oude lokale repo staat met `.git` en `.gitignore` in `archive/`; de zeven bestanden die hij volgt zijn mee verhuisd, dus daar klopt hij nog.

---

## VehicleTool (maart 2026)

**Wat:** controleert een al omgezette voertuig-resource en schrijft een rapport; zet voertuigen in één gedeelde pack (`pack/`) met een register van stream-bestanden en kit-id's. Losse scripts voor packs met meerdere voertuigen. Alleen de Python-standaardbibliotheek, met tkinter (het testplan zegt Python 3.10+; de code zelf vraagt minimaal 3.9). Start vanuit de map zelf: `python main.py "<resource>" [--json]` of `python ui.py`.

| Bestand | Rol |
|---------|-----|
| `checks.py` | Alle controles, als vaste foutcodes; `run_all_checks()` voor CLI en UI |
| `reporting.py` | Totaaloordeel en tekstrapport |
| `main.py` | CLI (geen handling-profiel) |
| `ui.py` (1.600 regels) | Tk-UI, pack-sync, handling-generator, register, manifest aanpassen |
| `check_resource_meta.py` | Packs met meerdere voertuigen en dubbele `carcols` vinden (alleen onder `data/`) |
| `split_multi_vehicle.py` | Een pack splitsen naar `<out>/<modelName>/` |
| `modkit_registry.py`, `verify_modkit_ids.py` | Kit-id-index, vrij id voorstellen (vanaf 700, tot 1023) |
| `verify_pack_assets.py` | Register tegenover `pack/stream/` |
| `templates/` | Meta-templates, 12 handling-profielen (JSON), profielenlijst |

**Wat werkt:** de controles en rapporten (tekst en JSON), meta zoeken door de hele resource, beide manifest-schrijfwijzen lezen, audio-controles, stream-bestanden kopiëren met botsingscontrole, de kit-index, de basis van het splitsen. Alle controles staan in [validation_rules.md](validation_rules.md).

**Wat niet werkt** (de belangrijkste; met bewijs uit de code en tests op kopieën):

1. **De pack-manifest is ongeldige Lua**: in `files {}` ontbreken de komma's (`ui.py` voegt regels zonder komma in). FiveM kan hem niet laden. Gecontroleerd met Lua 5.4.
2. **De pack gebruikt templates in plaats van de meta's uit de bron.** Weg zijn: de echte handling, kits, liveries, `txdRelationships`, layout, vlaggen en `audioNameHash`. De motor (BATIC) en de heli (BELL505) kregen auto-handling en `LAYOUT_LOW`. Alle vier `handling.meta`'s zijn gelijk.
3. **Alle vier pack-voertuigen hebben kit-id 10000** (vast in de template). De controle vooraf kijkt naar de `carcols` van de bron, maar in de pack komt de template. En `carvariations` verwijst naar `0_default_modkit`, niet naar die kit.
4. **`dlctext.meta` en `shop_vehicle.meta` hebben een verzonnen root-element** (zie [meta_files.md](meta_files.md)).
5. **Het register verliest wijzigingen** bij het bijwerken van een pack-voertuig (twee kopieën van het register, de oude wordt het laatst opgeslagen).
6. **XML-commentaar verdwijnt** bij elke opslag, ook de commentaarsecties waar de UI op leunt.
7. **164 van de 210 waarschuwingen zijn vals alarm**: stream-bestanden "niet in het manifest" (FiveM streamt `stream/` vanzelf). Nog 7 meldingen gingen over meta's in `data/` van `batic`, waarschijnlijk door de beperking met globs (`AUDIT.md`).
8. **Alleen het eerste voertuig** in een `vehicles.meta` wordt gecontroleerd.
9. In het splitsen: de check op ontbrekende mod-onderdelen geeft altijd niets; `Lights` en `Sirens` vallen weg; `--dry-run` uit de docstring bestaat niet (het is de standaard).
10. `verify_modkit_ids.py` schrijft een bestand terwijl de README zegt dat het alleen leest; "Reset pack + registry" wist de **gekozen** map, niet per se `VehicleTool/pack`.

**Waardevol:** de keten vehicles → carvariations → kitName → carcols → `.yft`; het register-idee (wie is eigenaar van welk stream-bestand, plus een kit-index); de audio-afspraken; de foutcodes als basis voor [validation_rules.md](validation_rules.md); de lessen uit 40 rapporten.

**Advies:** de code bewaren als bron, niet verder uitbouwen. De pack-functie niet gebruiken. `pack/` (91 MB kopieën), `report/`, `output/` en `__pycache__/` kunnen weg.

**Tip uit `PACK_VALIDATION.md`:** in PowerShell zijn `[` en `]` in een pad jokertekens. Bij mappen als `[wip]` of `[dev]` dus `-LiteralPath` of enkele aanhalingstekens gebruiken.

---

## VehicleOptimizer (juli 2025)

**Wat:** voertuig-mappen sorteren naar `<klasse|onbekend|oversized>/<naam>/` en er meta's bij maken uit templates. Alleen de standaardbibliotheek.

**Staat: concept, werkt niet.**

- `main.py` print alleen resource-mappen onder een vast pad (`C:/test`); in `vehicle.py` staat het startblok in commentaar.
- "Oversized" = bestand groter dan 16 MB **op schijf**. Dat meet het verkeerde (zie [textures.md](textures.md)). Het logbestand is leeg: er is nooit iets gemeld.
- Een gewone resource (`<res>/stream/`) gaat mis: de map `stream` wordt als voertuig gezien. Alleen `<naam>.yft` en `<naam>.ytd` worden gekopieerd; `_hi`, `+hi`, liveries en onderdelen niet.
- **De templates zijn niet algemeen:** `vehicles.meta` en `handling.meta` zijn van een vliegtuig (Alkonost), `carcols` en `carvariations` van een `xc90`, en die twee verwijzen niet eens naar dezelfde kit. Elk voertuig krijgt die inhoud.
- Geen manifest; de manifest-template wordt niet gebruikt en is niet in te vullen.

**Advies:** archief. Het idee "sorteren op klasse en apart zetten wat te groot is" staat in [tool_functions.md](tool_functions.md).

---

## trp_dds_inspector (maart 2026)

**Wat:** Tk-tool (Pillow) die meerdere `.dds`-bestanden toont met resolutie en grootte, en ze kan verkleinen tot maximaal 1024 px. Hoort bij de handmatige werkwijze: eerst textures exporteren met OpenIV.

**Staat:** tonen werkt. **Verkleinen maakt het erger**: de uitvoer is ongecomprimeerd RGBA zonder mipmaps. Getest: DXT1 2048² van 2,0 MB werd 1024² van 4,0 MB. Een DXT1 krijgt er een alfakanaal bij; een bestand dat geen macht van 2 is, blijft dat; de originelen kunnen zonder waarschuwing overschreven worden. Pillow kan DXT1 en DXT5 schrijven, geen BC7, en geen mipmaps.

**Advies:** alleen gebruiken om te kijken. De README is verouderd ("one file").

---

## noneWorking (maart 2026)

Twee mislukte pogingen. Bewust zo genoemd. De lessen staan in [textures.md](textures.md#wat-we-al-probeerden-maart-2026).

| Map | Route | Waarom het niet werkte |
|-----|-------|------------------------|
| `trp_vehicle_toolkit/ytd_mvp.py` | `rpf-cli` (uitpakken, inspecteren, terugpakken) | `rpf-cli extract` werkt op RPF7-archieven; een `.ytd` is RSC7. Terugpakken naar een `.ytd` kan rpf-cli niet. Een deel van de code is dood en geeft een fout |
| `trp_codewalker_ytd_toolkit/` | CodeWalker.API (HTTP op `localhost:5555`) | `fullPaths` moet een pad zijn dat CodeWalker zelf kent; een lokaal pad gaf HTTP 200 met een fout per item. Het enige bewaarde rapport laat zien dat de API niet draaide. Zelfs bij succes zou er niets op schijf komen; importeren/vervangen is nooit gebouwd |

Het **terugschrijven** van een `.ytd` is dus nooit geprobeerd. Dat blijft de echte onbekende (Q-T4).

**Advies:** archief. `rpf-cli.exe` staat hier en in de converter; het is hetzelfde bestand.

---

## trp_rpf_to_fivem_converter (maart 2026)

**Wat:** Tk-tool die `dlc.rpf` uitpakt met `rpf-cli extract` (ook geneste archieven) en alles plat kopieert naar `stream/` en `data/`, met een controle op zes "verplichte" meta's. Afgeleid van [Piliii/RPF-Extractor](https://github.com/Piliii/RPF-Extractor). `VehicleTool/README.md` noemt hem als stap vóór VehicleTool.

**Staat: werkt half.** Risico's (getest op een kopie van de sorteerlogica):

- Filtert op stukjes tekst in het **hele** pad: staat "update" in het pad, dan blijft er niets over. Staat "vehicles" erin, dan gaat alles (ook `.meta`) naar `stream/`.
- **Audio valt stil weg** (filter op "audio").
- `content.xml` en `setup2.xml` van de DLC komen in `data/`.
- **Dubbele namen worden hernoemd** (`cle53.ytd` → `cle53_1.ytd`). Dan werkt het bestand niet meer: de naam is de koppeling met `modelName` of `txdName`.
- Wist bij elke run eerst `stream/` en `data/` in de uitvoermap (standaard de map van het `.rpf`).
- Waarschuwt dat grote bestanden "afgekapt kunnen worden" (16 MB). Of rpf-cli dat echt doet, is niet getest (Q-A3).
- Maakt geen manifest.

**Advies:** bron voor de intake-functie (F-E1 in [tool_functions.md](tool_functions.md)), niet zo gebruiken.

---

## GitHub-repo FivemVehicleTool (feb 2026)

**Wat:** PyQt6-tool die een map met losse voertuig-resources scant en ordent tot één resource `Vehicles/` met per categorie `stream/` en `meta/`, met dry-run en een zip-back-up. Eén commit ("init", 23 feb 2026).

**Twee versies in één bestand:** `main.py` regel 1–7 start de pakketversie 1.1.0 (`fivem_vehicle_tool/`); regel 8–1382 is de oude versie 1.0.0 ("FiveM Asset Organizer") die nooit draait. De oude had meer UI (slepen, een filter op `_unknown`, een tab met problemen) maar een kapot manifest.

**Staat: werkt, met inhoudelijke fouten** (getest met een vervanger voor PyQt6):

- **Verkeerde klasse-tabel:** verwacht `sports`, `offroad`, …, terwijl `vehicles.meta` `VC_SPORT`, `VC_OFF_ROAD`, `VC_SPORT_CLASSIC`, `VC_CYCLE`, `VC_RAIL`, `VC_OPEN_WHEEL` gebruikt. Die gaan naar `_unknown` (getest met `strman`).
- Een pack wordt één voertuig, met de klasse van het eerste.
- **Bij dubbele stream-namen hernoemt hij** (`fdtruck.yft` → `lsfd_fdtruck.yft`): dat breekt het model.
- **Meta's met dezelfde naam uit submappen overschrijven elkaar** zonder melding (twee `vehicles.meta` → één).
- Mist `.ydr`, `.ybn`, `.ypt` en audio; kopieert `.xml` als meta.
- Schrijft `data_file 'TYPE' { … }` met een tabel; dat staat niet in de FiveM-documentatie (Q-S12). Geen `data_file` voor `dlctext` en `shop_vehicle`.
- "Organiseren" schrijft standaard niets: dry-run staat aan.

**Advies:** het idee (een hele map met losse voertuigen in één keer ordenen, met dry-run en back-up) hoort in de tool (F-D1, F-D3, F-D8 in [tool_functions.md](tool_functions.md)); de code niet hergebruiken. De repo is het nieuwe thuis (B16); deze code staat daar nu in `archive/`.

---

## old/oldversion: de in-game editor (juli 2025)

**Wat:** Marks eigen eerdere handling-editor: resource `VehicleHandlingEditor` 1.0.0 (auteur Man1C, voor TrueRP). Commando `/handlingeditor` (ACE), NUI met alle velden van het voertuigtype, opslaan als `handling.meta` op de server. Geen dependencies. 23 bestanden; `src/globals/VehicleAttributes.lua` (119 velden met naam, uitleg, type en min/max) is het grootste.

**Staat: werkte maar half.**

- Apply kwam nooit aan (de naam van de NUI-callback klopte niet); Copy had geen handler. Opslaan werkte wel.
- Was Apply aangekomen, dan had hij de handling globaal gezet en het voertuig opnieuw gespawnd.
- Grenzen alleen als HTML-hint; verschillende grenzen kloppen niet met echte waarden.
- De export nam vlaggen en sub-handling uit een template, niet van het voertuig; de templates gebruiken klassen die niet bestaan.
- Het save-event op de server controleerde niets.
- Wijkt op veel punten af van de standaard van nu: ±14 globals zonder `-- GLOBAL:`, eventnamen niet volgens `resource:side:action`, `while` zonder `WaitLimiter`, `io.*` op de server, geen bridge, geen `assert`'s.
- `VEHICLE_EDITOR_TESTS.md` heeft acht testgevallen, maar is nooit ingevuld.

**Waardevol:** het schema per veld, de typelijst (`VehicleTypes.lua`), de zoek- en labellogica, het idee van opslaan op de server. De details en wat er mis was, staan in [handling.md](handling.md#de-in-game-editor-die-we-al-hadden-oldoldversion-juli-2025).

**Advies:** bewaren als bron; niet verder bouwen op deze code.

---

## vehiclehandler (niet van ons)

**Wat:** [QuantumMalice/vehiclehandler](https://github.com/QuantumMalice/vehiclehandler) versie 1.4.3 (de laatste is 1.4.7, 13 okt 2026). Gaat over **schade en reparatie**, niet over handling-bestanden: motorschade verlaagt het koppel, wielen kunnen afbreken, kantelen zet de besturing uit, en er zijn reparatie-items (repairkit, tirekit, cleaningkit) en admin-commando's (`/fix`, `/wash`, `/setfuel`).

- **Licentie GPL-3.0**: code overnemen maakt ons script ook GPL.
- **Vereist ox_lib** (ox_inventory en ox_fuel optioneel): past niet bij onze regel (alleen oxmysql).
- In de kopie in onze map ontbreken `LICENSE`, de vertalingen en de plaatjes.

**Relevantie:** laag. Alleen ideeën (snelle admin-acties, een schademodule), geen code. **Niet tegelijk draaien met handling-tests**, want het verandert koppel en besturing.

**Advies:** uit de projectmap halen, of in `research/` zetten met een notitie over de licentie.
