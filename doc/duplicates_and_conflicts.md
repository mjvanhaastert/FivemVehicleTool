# Dubbel en tegenstrijdig

Wat er meer dan eens in de projectmap stond, en waar de oude notities of de tools elkaar of de echte bestanden tegenspreken.
"Nu in" zegt waar de informatie voortaan staat. De labels staan uitgelegd in [README.md](README.md#labels).

ID's: `DI` = dubbele informatie, `DC` = dubbele code, `K` = klopt niet of spreekt elkaar tegen.

---

## DI. Dubbele informatie

| # | Wat | Stond in | Nu in |
|---|-----|----------|-------|
| DI1 | Lijst met stream-extensies (`.ydr` … `.yvr`) | `docs/meta_reference_and_load_order.md` §12, `docs/vehicle_intake_procedure.md` §8, `VehicleTool/docs/Naamloos.canvas`, en in de code van VehicleTool (`checks.py` én `ui.py`) | [folder_structure.md](folder_structure.md) §4 |
| DI2 | Wat elk meta-bestand doet | `docs/plan.md` §4, `docs/meta_reference_and_load_order.md` §2, canvas | [meta_files.md](meta_files.md) §1 |
| DI3 | `txdRelationships` uitgelegd | `docs/meta_reference_and_load_order.md` §4.5, `docs/vehicle_intake_procedure.md` §9 | [textures.md](textures.md) |
| DI4 | "Eén voertuig per meta" en splitsen | `docs/meta_reference_and_load_order.md` §4.3, `VehicleTool/docs/META_SPLIT_POLICY.md`, `VehicleTool/docs/PACK_VALIDATION.md` | [folder_structure.md](folder_structure.md) §3, [decisions.md](decisions.md) B2 |
| DI5 | Kit-id-regels | `docs/plan.md` §4, `META_SPLIT_POLICY.md` regel 5, `CARCOLS_CARVARIATIONS_REFERENCE.md` §3–4, `modkit_registry.py` | [meta_files.md](meta_files.md) §6 |
| DI6 | Minimale meta-set per type | `docs/plan.md` §5, `docs/meta_reference_and_load_order.md` §3, canvas, VehicleTool, converter | [meta_files.md](meta_files.md) §5 (met de tegenspraak) |
| DI7 | Handling-grenzen | `docs/plan.md` §9 (Eddlm), `docs/handling_template_principles.md` §4, `VehicleTool/templates/handling/*.json`, `old/oldversion/src/globals/VehicleAttributes.lua` | [handling.md](handling.md) |
| DI8 | Audio-regels | `docs/vehicle_intake_procedure.md` §4, `docs/meta_reference_and_load_order.md` §10 | [audio.md](audio.md) |
| DI9 | Botsende namen in een gedeelde `stream/` | `docs/meta_reference_and_load_order.md` §9, `docs/vehicle_intake_procedure.md` §7 | [validation_rules.md](validation_rules.md) X1 |
| DI10 | Pack-structuur `data/<handlingId>/` + gedeelde `stream/` | `docs/vehicle_intake_procedure.md` §5, `VehicleTool/README.md` | [folder_structure.md](folder_structure.md) variant D/I |
| DI11 | Manifest-dekking (`UNDECLARED_FILE_IN_RESOURCE`) | `docs/meta_reference_and_load_order.md` §11, `docs/vehicle_intake_procedure.md` §3 | [validation_rules.md](validation_rules.md) R7 |
| DI12 | Koppeling meta → `data_file`-type | `docs/plan.md` §3, `docs/meta_reference_and_load_order.md` §1, en in vier tools | [meta_files.md](meta_files.md) §1 |
| DI13 | Lijst van voertuigklassen | `docs/plan.md` §6, `VehicleTool/ui.py`, de repo (getallen in `constants.py`, namen in `scanner.py`) | [meta_files.md](meta_files.md) §3 en Q-M5 |
| DI14 | Handling-templates per type | `old/oldversion/src/templates/*_handling.meta` (6), `VehicleTool/templates/meta/handling.template.meta` (ongebruikt), de generator in `VehicleTool/ui.py`, `VehicleTool/templates/handling/*.json` (12), `VehicleOptimizer/data/handling.meta` | [meta_files.md](meta_files.md) §9, [handling.md](handling.md) |
| DI15 | Lijst van handling-velden met uitleg | `docs/plan.md` §9 (31 velden, Eddlm), `old/oldversion/src/globals/VehicleAttributes.lua` (119 velden), `VehicleTool/templates/handling/bike_default.json` en `heli_default.json` (sub-klassen) | [handling.md](handling.md) |

## Dubbele code (zelfde functie, meer dan één tool)

| # | Functie | Tools | Meest compleet |
|---|---------|-------|----------------|
| DC1 | Resource-mappen vinden | VehicleOptimizer, repo (twee versies), VehicleTool | VehicleTool en de repo |
| DC2 | `vehicleClass` vertalen naar een categorie | VehicleOptimizer, repo (twee keer dezelfde fout), VehicleTool | VehicleTool (de enige met de echte `VC_*`-namen) |
| DC3 | Sorteren per categorie | VehicleOptimizer, repo (twee versies) | repo |
| DC4 | Stream en meta kopiëren | VehicleOptimizer, converter, repo, VehicleTool | VehicleTool (recursief, met register) |
| DC5 | Botsende namen afhandelen | VehicleOptimizer en de oude repo overschrijven, de converter hernoemt (`_1`), de repo zet de resourcenaam ervoor, VehicleTool blokkeert | VehicleTool (de enige die het asset heel laat) |
| DC6 | Meta-templates | VehicleOptimizer, VehicleTool, `old/oldversion` | VehicleTool (met fouten) |
| DC7 | Manifest maken | VehicleOptimizer (ongebruikt), repo, oude repo, VehicleTool | geen enkele is foutloos |
| DC8 | Verplichte meta's controleren | converter, repo, VehicleTool | VehicleTool |
| DC9 | Texture-grootte | VehicleOptimizer (MB op schijf), `trp_dds_inspector` (px), CodeWalker-poging (MB), `ytd_mvp` (px) | geen; alleen `trp_dds_inspector` meet echt iets (op handmatig geëxporteerde `.dds`) |
| DC10 | `.rpf` uitpakken | converter, `ytd_mvp` (gebruikte rpf-cli verkeerd) | converter |
| DC11 | Packs met meerdere voertuigen herkennen | `check_resource_meta.py` (alleen `data/`), `split_multi_vehicle.py` (root, `common/`, `data/*`) | `split_multi_vehicle.py` |

## Dubbele bestanden (zelfde inhoud, md5, 20 okt 2026)

- `rpf-cli.exe` twee keer: `noneWorking/trp_vehicle_toolkit/` en `trp_rpf_to_fivem_converter/`.
- Rapporten van VehicleTool die bij elke run opnieuw werden geschreven: 13 identieke `.txt` en 12 identieke `.json` van `scout2020`, 5 van `bell505`, 4 van `dc_mdheli`, en meer. In `VehicleTool/output/` staan de oude rapporten (de README zegt: mag weg).
- In de research-packs zelf: dezelfde texture onder twee namen (`brickadeb.ytd` = `brickadebr.ytd`, `halfback2.ytd` = `ussssuv2.ytd` = `watchtower2.ytd`). Geen fout van ons, wel een idee voor de tool (X6 in [validation_rules.md](validation_rules.md)).
- `dlctext.meta` is in vijf research-packs byte-gelijk (de standaard-uitvoer van de converter).
- De repo-`main.py` bevat de oude versie van de hele tool nog een keer (regel 8–1382, nooit uitgevoerd).
- Samen ongeveer 19 MB; niet de moeite om nu op te ruimen, behalve de rapporten.

---

## K. Tegenstrijdig of fout

### In de notities

| # | Wat | Wie zegt wat | Wat klopt | Status |
|---|-----|--------------|-----------|--------|
| K1 | `vehicleClass` in `vehicles.meta` | `docs/plan.md` §4: een getal (`6`), en "alleen voor auto's" | Tekst (`VC_SUPER`), en ook bij helikopters en motoren | `fout` in plan (`tested`, gelezen) |
| K2 | Wat in `dlctext.meta` staat | `docs/plan.md` §4: weergavenamen | Alleen drie vlaggen; de naam komt uit een tekstlabel (`gameName`) | `fout` in plan (`tested`, gelezen) |
| K3 | Namen van de hoge-kwaliteit-bestanden | `docs/plan.md` §5: `[naam]+hi.yft` en `[naam]_hi.ytd` | Omgekeerd: `<naam>_hi.yft` en `<naam>+hi.ytd` | `fout` in plan (`tested`, gelezen) |
| K4 | Doel-mapstructuur | vijf versies (plan, meta_ref, intake, split-beleid, repo) | gekozen: één resource per voertuig (B1, 21 okt); de indeling binnen de resource is B24 | [folder_structure.md](folder_structure.md) §3 |
| K5 | Bereik van kit-id's | GTAMods: 0–1023 | Kit-id's in de testdata: `1101`–`1105`, `3995`, `64378` (en `10000` en `135` in de templates). (`941` is een licht-id, `6001`–`6013` zijn sirene-id's: geen kits) | open (Q-M4) |
| K6 | `data_file`-type van `shop_vehicle.meta` | convert.cfx.rs-uitvoer (`kriegerty2`) en `docs/plan.md` §3: `VEHICLE_SHOP_FILE`; meta_ref en onze pack: `VEHICLE_SHOP_DLC_FILE` | eerste blik in de FiveM-docs: alleen `VEHICLE_SHOP_DLC_FILE` | open (Q-M1) |
| K7 | Nut van `shop_vehicle.meta` en `dlctext.meta` | plan §4: "voor FiveM vrijwel altijd nodig"; canvas: "wordt nooit gebruikt in FiveM"; VehicleTool: FAIL als ze ontbreken | open; vijf van acht resources van de oude server hadden geen `shop_vehicle` | Q-M2, Q-M3, B13 |
| K8 | Minimale meta-set | vijf lijsten (zie [meta_files.md](meta_files.md) §5) | open | Q-S8 |
| K9 | Bereik van `fInitialDriveMaxFlatVel` | Eddlm: 0–200; onze class-baselines: 150–340 | Waarschijnlijk twee eenheden (meta tegenover geheugen) | Q-H9, Q-H13 |
| K10 | Waar de texture-grens over gaat | plan: bestand > 16 MB en > 2048 px; VehicleOptimizer: > 16 MB op schijf; `trp_dds_inspector`: > 1024 px | Gemeten: geheugen uit de header; 1,9 MB op schijf kan 76 MiB zijn | [textures.md](textures.md), Q-T1 |
| K11 | "Bestanden lezen of schrijven kan niet in FiveM" (reden voor twee tools) | plan §2 | Server-side kan het binnen de sandbox; de oude editor schreef zelf meta's op de server; `LoadResourceFile` leest andere resources | herzien (B3, Q-A1) |
| K12 | Betekenis van `.yfd`, `.yld`, `.ypdb`, `.ywr` | oude lijst: fragment dictionary, lights, particle database, water | Waarschijnlijk: frame filter dictionary, cloth dictionary, pose matcher database, waypoint recording | `aanname`, na te kijken in CodeWalker |
| K13 | Ontbrekende `common/` | plan: FAIL; VehicleTool: WARN als `data/` er is | keuze | hangt af van B24 (voorstel: `data/`) |
| K14 | `handlingName` in hoofdletters | plan §4: "conventie: UPPERCASE" | Pack: `scout2020` en `bell505` in kleine letters, mappen in hoofdletters; `checks.py` vergelijkt zonder hoofdletters, de split met | Q-M8 |
| K15 | Namen van tools en scripts | oud: `trp_vehicle_toolkit`, `trp_handling_editor`, `trp_dds_inspector`, … | Standaard: `dev_<naam>` (gekozen); de naam zelf kiest Mark | B17 |
| K16 | UI van de externe tool | plan: `rich` CLI, later tkinter; VehicleTool: Tk; repo: PyQt6 | open | B4 |

### In de tools

| # | Wat | Waar | Gevolg |
|---|-----|------|--------|
| K17 | Root-element van `dlctext.meta` en `shop_vehicle.meta` verzonnen (`CVehicleModelInfoNameData`, `CShopVehicleData`; echt: `CExtraTextMetaFile`, `ShopVehicleDataArray`) | VehicleTool-templates | de pack levert ongeldige bestanden |
| K18 | Kit-id vast op `10000`; `carvariations` verwijst naar `0_default_modkit` | VehicleTool-templates | alle vier pack-voertuigen hetzelfde id; de eigen kit wordt nergens gebruikt |
| K19 | De controle op dubbele kit-id's kijkt naar de `carcols` van de bron, de pack krijgt de template | `VehicleTool/ui.py` | de blokkade beschermt niet |
| K20 | Pack-sync vanuit templates in plaats van de bron | VehicleTool | handling, layout, kits, `txdRelationships`, vlaggen en `audioNameHash` gaan verloren; voorstel: bron overnemen, template alleen voor wat ontbreekt |
| K21 | Pack-manifest zonder komma's in `files {}` | VehicleTool (`ui.py`) | ongeldige Lua; FiveM laadt de pack niet |
| K22 | Stream-bestanden melden als "niet in het manifest" | VehicleTool (R7) | 171 van de 210 waarschuwingen waren "niet in het manifest"; 164 daarvan stream-bestanden (vals alarm), 7 meta's in `data/` van `batic` |
| K23 | Type/klasse-tabel keurt `VEHICLE_TYPE_BIKE` + `VC_EMERGENCY` af | VehicleTool (`checks.py`) | vanilla heeft het zelf (`policeb`); controle uit de data halen |
| K24 | Klasse-tabel met `sports`, `offroad`, … in plaats van `VC_SPORT`, `VC_OFF_ROAD`, … | repo (`scanner.py` en de oude `main.py`) | zes klassen komen in `_unknown` |
| K25 | Botsende stream-namen oplossen door te **hernoemen** | converter (`naam_1`), repo (`<resource>_naam`) | het bestand past niet meer bij `modelName`/`txdName`: het voertuig breekt |
| K26 | Meta's met dezelfde naam uit submappen overschrijven elkaar | repo | stil dataverlies |
| K27 | `data_file 'TYPE' { … }` met een tabel | repo | niet gedocumenteerd; onbekend of FiveM het leest (Q-S12) |
| K28 | Templates van een vliegtuig en een `xc90` voor elk voertuig | VehicleOptimizer | niet herbruikbaar |
| K29 | "Verkleinen" schrijft ongecomprimeerd en zonder mipmaps | `trp_dds_inspector` | bestanden worden groter |
| K30 | De docstring zegt `--dry-run`; die optie bestaat niet (dry-run is de standaard) | `split_multi_vehicle.py` | foutmelding bij het volgen van de docstring |
| K31 | README: `verify_modkit_ids.py` leest alleen | VehicleTool | hij schrijft `pack/modkit_ids.json` |
| K32 | Handling-templates met klassen die niet bestaan (`CHeliHandlingData`, `CPlaneHandlingData`); motor-template met `CCarHandlingData` en verzonnen velden, en nooit gekozen (`bike` ≠ `motorcycle`) | `old/oldversion/src/templates/` | een export is ongeldig |
| K33 | Grenzen die niet kloppen met echte waarden: `fInitialDragCoeff` 10–120 (echt 4–15), `fPercentSubmerged` 0–1 (echt 75–200, procent), `fYawMult` 0–10 (echt negatief), motor-velden | `old/oldversion/src/globals/VehicleAttributes.lua` | goede waarden worden "buiten bereik" |
| K34 | `fDownForceModifier` in plaats van `fDownforceModifier`; veldnamen zijn hoofdlettergevoelig | `old/oldversion/src/globals/VehicleAttributes.lua` | het veld werd nooit gevonden |
| K35 | De NUI stuurt Apply naar `vehicleHandling:applyHandling`, de client luistert op `applyHandling`; Copy heeft geen handler | `old/oldversion` | Apply en Copy deden niets |

### Buiten het project

| # | Wat | Wie zegt wat | Wat de broncode zegt | Status |
|---|-----|--------------|----------------------|--------|
| K36 | `io.*` in FiveM | kennisbasis `info/runtime/sandbox.md` en de standaard §2: "Niet: `io.*`" | Server-side bestaan `io` en `os` wél, binnen de sandbox (`LuaScriptRuntime.cpp`, `LuaIO.cpp`) | testen, daarna de kennisbasis bijwerken (zie [open_questions.md](open_questions.md)) |
| K37 | Sub-klassen in de handling-natives | native-docs: "only CHandlingData is supported" | De code zoekt ook in `SubHandlingData` (`HandlingLoader.cpp`) | testen (Q-H6) |
| K38 | README van de oude editor: "the server sends the detected vehicleType", "robust error handling", kopiëren "logt naar de server" | `old/oldversion/README.md` | De client stuurt het type; de speler krijgt geen foutmelding; loggen bij kopiëren is niet gebouwd | `fout` in de README |
| K39 | Welk `data_file`-type bij `.dat10.rel` hoort | `docs/meta_reference_and_load_order.md` §10, `docs/vehicle_intake_procedure.md` §4 en `VehicleTool/checks.py`: onder `AUDIO_GAMEDATA` | Werkende resource (Custom Engine Sounds): `AUDIO_SYNTHDATA` | `fout` in de notities en VehicleTool (`tested`, gelezen) |
| K40 | Welke meta's de manifests van `strman` en `zaccflatlit` noemen | `strman`: ook `carcols.meta`; `zaccflatlit`: ook `carcols.meta` en `vehiclelayouts.meta` | Die bestanden staan niet in de map | testgeval voor R3/R4 |
